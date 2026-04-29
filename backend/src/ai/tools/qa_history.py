from langchain_core.tools import tool

from src.ai.vectorstores import chroma_store


@tool
def query_qa_history() -> str:
    """查询用户的历史提问记录。当用户问到"我之前问过什么"、"历史问题"等时使用。"""
    records = chroma_store.get_all_qa_records()
    if not records:
        return "暂无任何提问记录。"

    lines = ["用户的历史提问记录："]
    for record in records:
        question = record.get("question", "")
        subject = record.get("subject", "")
        timestamp = record.get("timestamp", "")
        if question:
            lines.append(f"- [{subject}] {question}（{timestamp}）")
    return "\n".join(lines)
