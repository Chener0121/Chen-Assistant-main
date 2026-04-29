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
        elif stat["missing_count"] > 0:
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
