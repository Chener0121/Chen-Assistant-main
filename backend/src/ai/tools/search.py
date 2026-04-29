from src.ai.vectorstores import chroma_store


def _search(query: str, subject: str = "") -> list[dict]:
    """检索笔记，返回 [{"subject": "数学", "content": "..."}] 列表"""
    vs = chroma_store.get_vectorstore()
    if subject:
        docs = vs.similarity_search(query, k=5, filter={"subject": subject})
    else:
        docs = vs.similarity_search(query, k=8)
    return [{"subject": d.metadata.get("subject", "未知"), "content": d.page_content} for d in docs]
