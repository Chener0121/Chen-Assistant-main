import hashlib
import tempfile
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.ai.vectorstores import chroma_store
from src.core.exceptions import AppException

# 支持的文件类型与对应的 Loader
LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
}

# 文本切片器（中文标点优先断句，chunk_size 放大以减少公式截断）
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=300,
    separators=["\n\n", "\n", "。", "；", "！", "？", ".", " ", ""],
)


def process_upload(file_bytes: bytes, filename: str) -> dict:
    """文件上传主流程：解析 → 切片 → 去重 → 向量化 → 入库"""
    # 校验文件类型
    ext = Path(filename).suffix.lower()
    if ext not in LOADERS:
        raise AppException(status_code=400, msg=f"不支持的文件类型: {ext}")

    # 计算文件 MD5 用于去重
    file_md5 = hashlib.md5(file_bytes).hexdigest()

    # 文件级去重：MD5 相同则跳过
    if chroma_store.exists_by_md5(file_md5):
        return {"filename": filename, "file_md5": file_md5, "chunk_count": 0, "skipped": True}

    # 写入临时文件供 Loader 解析
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # 根据扩展名选择 Loader 解析文档
        loader = LOADERS[ext](tmp_path)
        docs = loader.load()
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # 切片
    chunks = _splitter.split_documents(docs)

    # 为每个 chunk 注入 file_md5 和 filename 元数据
    for chunk in chunks:
        chunk.metadata["file_md5"] = file_md5
        chunk.metadata["filename"] = filename

    # 向量化入库
    chroma_store.add_documents(chunks)

    return {"filename": filename, "file_md5": file_md5, "chunk_count": len(chunks), "skipped": False}


def list_documents() -> list[dict]:
    """从 Chroma 元数据中聚合去重的文档列表"""
    vs = chroma_store.get_vectorstore()
    results = vs.get(include=["metadatas"])

    # 按 file_md5 去重，聚合文档信息
    seen: dict[str, dict] = {}
    for meta in results["metadatas"] or []:
        md5 = meta.get("file_md5", "")
        if md5 and md5 not in seen:
            seen[md5] = {
                "doc_id": md5,
                "filename": meta.get("filename", ""),
            }
    return list(seen.values())


def delete_document(doc_id: str) -> None:
    """根据 doc_id（即 file_md5）删除文档及向量数据"""
    chroma_store.delete_by_md5(doc_id)
