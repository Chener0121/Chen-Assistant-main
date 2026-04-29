from langchain_core.tools import tool

from src.ai.vectorstores import chroma_store


@tool
def search_notes(query: str, subject: str = "") -> str:
    """从用户的学习笔记中检索与问题相关的内容。
    query: 搜索关键词或问题
    subject: 问题所属学科（如：数学、语文、英语），不确定时留空
    """
    vs = chroma_store.get_vectorstore()

    if subject:
        docs = vs.similarity_search(query, k=5, filter={"subject": subject})
    else:
        docs = vs.similarity_search(query, k=8)

    if not docs:
        return "没有找到相关笔记内容。"

    parts = []
    for doc in docs:
        s = doc.metadata.get("subject", "未知")
        parts.append(f"[学科：{s}]\n{doc.page_content}")
    return "\n\n".join(parts)
