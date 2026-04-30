from datetime import datetime, timedelta

from src.ai.vectorstores import chroma_store

# 衰减时间窗口
_ACTIVE_DAYS = 30       # 30 天内有活动保持当前等级
_DECAY_DAYS = 60         # 30-60 天无活动降一级，60 天以上移除

# 等级降级映射
_LEVEL_DOWN = {"high": "medium", "medium": "low", "low": ""}


def list_weak_points() -> list[dict]:
    """分析薄弱知识点，带时间衰减：30天内保持等级，30-60天降一级，60天以上移除"""
    records = chroma_store.get_all_qa_records()
    if not records:
        return []

    now = datetime.now()

    # 按知识点聚合统计
    kp_stats: dict[str, dict] = {}
    for record in records:
        points = record.get("knowledge_points", "")
        if not points:
            continue
        timestamp_str = record.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            continue

        for kp in points.split(","):
            kp = kp.strip()
            if not kp:
                continue
            if kp not in kp_stats:
                kp_stats[kp] = {
                    "knowledge_point": kp,
                    "subject": record.get("subject", ""),
                    "ask_count": 0,
                    "missing_count": 0,
                    "correction_count": 0,
                    "last_active": ts,
                }
            stat = kp_stats[kp]
            # 优先保留非空的学科
            new_subject = record.get("subject", "")
            if new_subject and not stat["subject"]:
                stat["subject"] = new_subject
            stat["ask_count"] += 1
            if not record.get("used_note", True):
                stat["missing_count"] += 1
            if record.get("has_corrections", False):
                stat["correction_count"] += 1
            if ts > stat["last_active"]:
                stat["last_active"] = ts

    # 计算等级并应用时间衰减
    results = []
    for stat in kp_stats.values():
        # 计算原始等级
        if stat["correction_count"] > 0:
            level = "high"
        elif stat["missing_count"] >= 2:
            level = "medium"
        elif stat["ask_count"] >= 3:
            level = "low"
        else:
            continue

        # 应用时间衰减
        days_inactive = (now - stat["last_active"]).days
        if days_inactive > _DECAY_DAYS:
            # 超过 60 天，移除
            continue
        elif days_inactive > _ACTIVE_DAYS:
            # 30-60 天无活动，降一级
            level = _LEVEL_DOWN.get(level, "")
            if not level:
                continue

        stat["level"] = level
        # last_active 转为字符串便于 JSON 序列化
        stat["last_active"] = stat["last_active"].isoformat()
        results.append(stat)

    # 按等级排序：high > medium > low
    level_order = {"high": 0, "medium": 1, "low": 2}
    results.sort(key=lambda x: level_order.get(x["level"], 3))

    return results


def daily_stats(mode: str = "daily") -> dict:
    """统计提问次数，按学科分组。mode=daily 按14天，mode=hourly 按14小时"""
    records = chroma_store.get_all_qa_records()
    now = datetime.now()

    if mode == "hourly":
        # 近 14 小时
        slots = [(now - timedelta(hours=i)).strftime("%Y-%m-%d %H:00") for i in range(13, -1, -1)]
    else:
        # 近 14 天
        slots = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13, -1, -1)]

    slot_set = set(slots)

    # 按时间槽+学科聚合
    subject_set: set[str] = set()
    counter: dict[tuple[str, str], int] = {}
    for record in records:
        ts_str = record.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str)
        except (ValueError, TypeError):
            continue
        slot = ts.strftime("%Y-%m-%d %H:00") if mode == "hourly" else ts.strftime("%Y-%m-%d")
        if slot not in slot_set:
            continue
        subject = record.get("subject", "")
        if not subject:
            continue
        subject_set.add(subject)
        counter[(slot, subject)] = counter.get((slot, subject), 0) + 1

    # 构建 series
    subjects = sorted(subject_set)
    series = {}
    for s in subjects:
        series[s] = [counter.get((sl, s), 0) for sl in slots]

    # 缩短标签显示
    labels = [s[5:] if mode == "daily" else s[11:] for s in slots]
    return {"dates": labels, "subjects": subjects, "series": series}


def coverage_stats() -> dict:
    """知识活跃度：各学科被提问过的唯一知识点数量"""
    qa = chroma_store.get_qa_store()

    # 各学科被提问过的唯一知识点数
    qa_records = qa.get(include=["metadatas"])
    subject_kps: dict[str, set[str]] = {}
    for meta in qa_records["metadatas"] or []:
        subject = meta.get("subject", "")
        points = meta.get("knowledge_points", "")
        if subject and points:
            subject_kps.setdefault(subject, set()).update(
                p.strip() for p in points.split(",") if p.strip()
            )

    total_kps = sum(len(kps) for kps in subject_kps.values())

    return {
        "total_active_kps": total_kps,
        "subjects": {
            s: len(subject_kps.get(s, set()))
            for s in sorted(subject_kps.keys())
        },
    }


def review_suggestions() -> list[dict]:
    """返回建议复习的知识点：薄弱 + 超过 3 天未提问"""
    weak_points = list_weak_points()
    if not weak_points:
        return []

    now = datetime.now()
    suggestions = []
    for wp in weak_points:
        last_active_str = wp.get("last_active", "")
        try:
            last_active = datetime.fromisoformat(last_active_str)
            days_inactive = (now - last_active).days
        except (ValueError, TypeError):
            days_inactive = 999

        if days_inactive >= 3:
            suggestions.append({
                "knowledge_point": wp["knowledge_point"],
                "subject": wp["subject"],
                "level": wp["level"],
                "days_inactive": days_inactive,
            })

    return suggestions
