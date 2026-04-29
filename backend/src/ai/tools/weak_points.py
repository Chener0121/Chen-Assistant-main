from langchain_core.tools import tool

from src.services import analytics_service


@tool
def query_weak_points() -> str:
    """查询用户的薄弱知识点列表。当用户问到学习情况、薄弱项、需要复习什么时使用。"""
    points = analytics_service.list_weak_points()
    if not points:
        return "暂无薄弱知识点记录，可能是还没有足够的问答数据。"

    lines = ["用户的薄弱知识点："]
    level_map = {"high": "高", "medium": "中", "low": "低"}
    for p in points:
        level = level_map.get(p["level"], "")
        lines.append(f"- {p['knowledge_point']}（学科：{p['subject']}，薄弱等级：{level}，提问次数：{p['ask_count']}）")
    return "\n".join(lines)
