from src.ai.vectorstores import chroma_store


def build_graph() -> dict:
    """构建简易知识图谱：节点（学科、文档、知识点）+ 边（关联关系）"""
    nodes = []
    edges = []
    node_ids: set[str] = set()

    # 从文档 chunk 元数据中提取学科和文档节点
    vs = chroma_store.get_vectorstore()
    doc_results = vs.get(include=["metadatas"])

    subjects: set[str] = set()
    documents: set[str] = set()
    # 知识点来源于 QA 记录，这里先收集学科和文档
    for meta in doc_results["metadatas"] or []:
        subject = meta.get("subject", "")
        file_id = meta.get("file_id", "")
        if subject:
            subjects.add(subject)
        if file_id:
            documents.add(file_id)

    # 从 QA 记录中提取知识点，建立关联
    qa_records = chroma_store.get_all_qa_records()
    # 知识点 → 出现过的学科
    kp_subjects: dict[str, set[str]] = {}
    # 知识点 → 共现的其他知识点（同一问题中出现的）
    kp_cooccur: dict[str, set[str]] = {}
    # 知识点 → 出现次数
    kp_count: dict[str, int] = {}

    for record in qa_records:
        points_str = record.get("knowledge_points", "")
        subject = record.get("subject", "")
        if not points_str:
            continue
        points = [p.strip() for p in points_str.split(",") if p.strip()]

        for kp in points:
            kp_count[kp] = kp_count.get(kp, 0) + 1
            if subject:
                kp_subjects.setdefault(kp, set()).add(subject)

        # 同一问题中的知识点建立共现关系
        for i, kp1 in enumerate(points):
            for kp2 in points[i + 1:]:
                kp_cooccur.setdefault(kp1, set()).add(kp2)
                kp_cooccur.setdefault(kp2, set()).add(kp1)

    # 构建节点
    def add_node(node_id: str, label: str, node_type: str, extra: dict | None = None):
        if node_id not in node_ids:
            node_ids.add(node_id)
            n = {"id": node_id, "label": label, "type": node_type}
            if extra:
                n.update(extra)
            nodes.append(n)

    for s in subjects:
        add_node(f"subject:{s}", s, "subject")

    for d in documents:
        add_node(f"doc:{d}", d, "document")

    for kp, count in kp_count.items():
        add_node(f"kp:{kp}", kp, "knowledge_point", {"count": count})

    # 构建边：学科 → 知识点
    for kp, subs in kp_subjects.items():
        for s in subs:
            edges.append({"source": f"subject:{s}", "target": f"kp:{kp}", "type": "contains"})

    # 构建边：学科 → 文档
    for meta in doc_results["metadatas"] or []:
        subject = meta.get("subject", "")
        file_id = meta.get("file_id", "")
        if subject and file_id:
            edge_key = f"subject:{subject}->doc:{file_id}"
            if edge_key not in node_ids:
                node_ids.add(edge_key)
                edges.append({"source": f"subject:{subject}", "target": f"doc:{file_id}", "type": "belongs_to"})

    # 构建边：知识点共现
    seen_edges: set[str] = set()
    for kp1, related in kp_cooccur.items():
        for kp2 in related:
            key = tuple(sorted([f"kp:{kp1}", f"kp:{kp2}"]))
            if key not in seen_edges:
                seen_edges.add(key)
                edges.append({"source": key[0], "target": key[1], "type": "related"})

    return {"nodes": nodes, "edges": edges}


def list_weak_points() -> list[dict]:
    """分析薄弱知识点：高频提问 + 笔记缺失 + 笔记纠错"""
    records = chroma_store.get_all_qa_records()
    if not records:
        return []

    # 按知识点聚合统计
    kp_stats: dict[str, dict] = {}
    for record in records:
        points = record.get("knowledge_points", "")
        if not points:
            continue
        for kp in points.split(","):
            kp = kp.strip()
            if not kp:
                continue
            if kp not in kp_stats:
                kp_stats[kp] = {"knowledge_point": kp, "ask_count": 0, "missing_count": 0, "correction_count": 0}
            kp_stats[kp]["ask_count"] += 1
            if not record.get("used_note", True):
                kp_stats[kp]["missing_count"] += 1
            if record.get("has_corrections", False):
                kp_stats[kp]["correction_count"] += 1

    # 按提问频率排序，取前 20
    sorted_points = sorted(kp_stats.values(), key=lambda x: x["ask_count"], reverse=True)[:20]

    # 标记薄弱等级
    for point in sorted_points:
        if point["correction_count"] > 0:
            point["level"] = "high"
        elif point["missing_count"] > 0:
            point["level"] = "medium"
        elif point["ask_count"] >= 3:
            point["level"] = "low"
        else:
            point["level"] = ""

    return [p for p in sorted_points if p["level"]]
