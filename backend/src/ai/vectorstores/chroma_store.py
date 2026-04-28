from langchain_chroma import Chroma

from src.core.config import settings
from src.core.llm_client import embeddings

# 向量库单例
_vectorstore: Chroma | None = None


def get_vectorstore() -> Chroma:
    """获取 Chroma 向量库实例（懒加载单例）"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name="documents",
            embedding_function=embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR,
        )
    return _vectorstore


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
