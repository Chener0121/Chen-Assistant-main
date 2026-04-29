from langchain_core.tools import tool

from src.ai.vectorstores import chroma_store
from src.services import analytics_service
from src.services import graph_service


@tool
def query_weak_points() -> str:
    """查询用户的薄弱知识点列表，包含关联知识点和笔记复习建议。当用户问到学习情况、薄弱项、需要复习什么时使用。"""
    points = analytics_service.list_weak_points()
    if not points:
        return "暂无薄弱知识点记录，可能是还没有足够的问答数据。"

    # 获取知识图谱，用于查找关联知识点
    graph = graph_service.build_graph()
    related_map = _build_related_map(graph)

    # 获取向量库实例，用于检索相关笔记
    vs = chroma_store.get_vectorstore()

    level_map = {"high": "高", "medium": "中", "low": "低"}
    lines = ["用户的薄弱知识点："]

    for p in points:
        kp = p["knowledge_point"]
        level = level_map.get(p["level"], "")
        lines.append(f"\n【{kp}】学科：{p['subject']}，薄弱等级：{level}，提问次数：{p['ask_count']}")

        # 关联知识点
        related = related_map.get(kp, [])
        if related:
            lines.append(f"  关联知识点：{', '.join(related[:5])}")

        # 从笔记中检索该知识点的相关内容
        docs = vs.similarity_search(kp, k=2, filter={"subject": p["subject"]})
        if docs:
            lines.append("  笔记相关内容：")
            for doc in docs:
                lines.append(f"    - {doc.page_content[:100]}...")

    return "\n".join(lines)


def _build_related_map(graph: dict) -> dict[str, list[str]]:
    """从图谱的 related 边中提取知识点的关联关系"""
    related_map: dict[str, list[str]] = {}
    for edge in graph.get("edges", []):
        if edge.get("type") != "related":
            continue
        src = edge["source"].removeprefix("kp:")
        tgt = edge["target"].removeprefix("kp:")
        related_map.setdefault(src, []).append(tgt)
        related_map.setdefault(tgt, []).append(src)
    return related_map
