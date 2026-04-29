import uuid
from datetime import datetime

from langchain_chroma import Chroma

from src.core.config import settings
from src.core.llm_client import embeddings

# 向量库单例
_vectorstore: Chroma | None = None
# 问答记录库单例
_qa_store: Chroma | None = None


def get_vectorstore() -> Chroma:
    """获取文档向量库实例（懒加载单例）"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name="documents",
            embedding_function=embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR,
        )
    return _vectorstore


def get_qa_store() -> Chroma:
    """获取问答记录向量库实例（懒加载单例）"""
    global _qa_store
    if _qa_store is None:
        _qa_store = Chroma(
            collection_name="qa_records",
            embedding_function=embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR,
        )
    return _qa_store


def get_chunk_hashes(file_id: str) -> set[str]:
    """查询该文件已有的所有 chunk_hash"""
    vs = get_vectorstore()
    results = vs.get(where={"file_id": file_id}, include=["metadatas"])
    return {meta["chunk_hash"] for meta in results["metadatas"] or [] if "chunk_hash" in meta}


def add_chunks(chunks: list, ids: list[str]) -> None:
    """用指定 id（chunk_hash）将新 chunks 入库"""
    vs = get_vectorstore()
    vs.add_documents(chunks, ids=ids)


def delete_chunks(chunk_hashes: list[str]) -> None:
    """按 chunk_hash 删除指定 chunks"""
    if not chunk_hashes:
        return
    vs = get_vectorstore()
    vs.delete(chunk_hashes)


def delete_by_file_id(file_id: str) -> None:
    """删除该文件的所有 chunks"""
    vs = get_vectorstore()
    results = vs.get(where={"file_id": file_id})
    if results["ids"]:
        vs.delete(results["ids"])


def save_qa_record(question: str, result: dict) -> None:
    """保存一条问答记录到 qa_records 集合"""
    qa = get_qa_store()
    record_id = str(uuid.uuid4())
    # 用问题文本作为向量化的内容
    from langchain_core.documents import Document
    doc = Document(
        page_content=question,
        metadata={
            "record_id": record_id,
            "question": question,
            "subject": result.get("subject", ""),
            "knowledge_points": ",".join(result.get("knowledge_points", [])),
            "used_note": result.get("used_note", False),
            "has_corrections": len(result.get("note_corrections", [])) > 0,
            "timestamp": datetime.now().isoformat(),
        },
    )
    qa.add_documents([doc], ids=[record_id])


def get_all_qa_records() -> list[dict]:
    """获取所有问答记录"""
    qa = get_qa_store()
    results = qa.get(include=["metadatas"])
    return results["metadatas"] or []


def clear_qa_records() -> int:
    """清空所有问答记录，返回删除的记录数"""
    qa = get_qa_store()
    results = qa.get()
    if results["ids"]:
        qa.delete(results["ids"])
    return len(results["ids"])
