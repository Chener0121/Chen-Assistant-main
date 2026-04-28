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


def exists_by_md5(file_md5: str) -> bool:
    """根据文件 MD5 判断是否已入库"""
    vs = get_vectorstore()
    results = vs.get(where={"file_md5": file_md5})
    return len(results["ids"]) > 0


def delete_by_md5(file_md5: str) -> None:
    """删除该文件 MD5 对应的所有 chunks"""
    vs = get_vectorstore()
    results = vs.get(where={"file_md5": file_md5})
    if results["ids"]:
        vs.delete(results["ids"])


def add_documents(chunks: list) -> None:
    """将 chunks 入库（metadata 中需包含 file_md5）"""
    vs = get_vectorstore()
    vs.add_documents(chunks)
