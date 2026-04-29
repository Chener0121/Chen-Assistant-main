import hashlib
import tempfile
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.ai.vectorstores import chroma_store
from src.core.exceptions import AppException
from src.core.llm_client import llm

# 支持的文件类型与对应的 Loader
LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
}

# 文本切片器（中文标点优先断句，chunk_size 放大以减少公式截断）
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", "。", "；", "！", "？", ".", " ", ""],
)


def _chunk_hash(text: str) -> str:
    """计算 chunk 文本内容的 MD5"""
    return hashlib.md5(text.encode()).hexdigest()


def _detect_subject(text: str) -> str:
    """用 LLM 判断文档内容属于什么学科"""
    # 取前 800 字符作为样本
    sample = text[:800]
    response = llm.invoke(
        f"请根据以下学习笔记内容，判断它属于哪个学科。只回答学科名称（如：数学、英语、语文、物理、化学、历史、其他），不要解释。\n\n{sample}"
    )
    return response.content.strip()


def process_upload(file_bytes: bytes, filename: str) -> dict:
    """文件上传主流程：解析 → 切片 → chunk 级增量 diff → 入库"""
    # 校验文件类型
    ext = Path(filename).suffix.lower()
    if ext not in LOADERS:
        raise AppException(status_code=400, msg=f"不支持的文件类型: {ext}")

    file_id = filename

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

    # 切片，过滤掉空文本 chunk（避免 embedding API 报错）
    chunks = [c for c in _splitter.split_documents(docs) if c.page_content.strip()]

    # 用 LLM 判断学科（取所有 chunk 拼接后的前 800 字）
    full_text = "\n".join(c.page_content for c in chunks)
    subject = _detect_subject(full_text)

    # 为每个 chunk 计算 chunk_hash，注入 metadata
    for chunk in chunks:
        c_hash = _chunk_hash(chunk.page_content)
        chunk.metadata["file_id"] = file_id
        chunk.metadata["chunk_hash"] = c_hash
        chunk.metadata["subject"] = subject

    # 查询该文件已有的 chunk_hash 集合
    existing_hashes = chroma_store.get_chunk_hashes(file_id)

    # 三路 diff
    new_chunks = []       # 需要新增的 chunks
    new_ids = []          # 对应的 chunk_hash 作为 Chroma id
    skipped_count = 0

    current_hashes: set[str] = set()
    for chunk in chunks:
        c_hash = chunk.metadata["chunk_hash"]
        current_hashes.add(c_hash)
        if c_hash in existing_hashes:
            # chunk 内容未变化，跳过
            skipped_count += 1
        else:
            # 新 chunk，需要 embedding 入库
            new_chunks.append(chunk)
            new_ids.append(c_hash)

    # 已删除的旧 chunk（存在于旧集合但不在新集合中）
    deleted_hashes = list(existing_hashes - current_hashes)
    chroma_store.delete_chunks(deleted_hashes)

    # 新增 chunks 入库
    if new_chunks:
        chroma_store.add_chunks(new_chunks, new_ids)

    return {
        "file_id": file_id,
        "subject": subject,
        "added": len(new_chunks),
        "skipped": skipped_count,
        "deleted": len(deleted_hashes),
    }


def list_documents() -> list[dict]:
    """从 Chroma 元数据中聚合去重的文档列表"""
    vs = chroma_store.get_vectorstore()
    results = vs.get(include=["metadatas"])

    # 按 file_id 去重，聚合文档信息和 chunk 计数
    seen: dict[str, dict] = {}
    for meta in results["metadatas"] or []:
        file_id = meta.get("file_id", "")
        if not file_id:
            continue
        if file_id not in seen:
            seen[file_id] = {
                "file_id": file_id,
                "subject": meta.get("subject", ""),
                "chunk_count": 1,
            }
        else:
            seen[file_id]["chunk_count"] += 1
    return list(seen.values())


def delete_document(file_id: str) -> None:
    """根据 file_id 删除文档及所有向量数据，不存在则抛出 404"""
    vs = chroma_store.get_vectorstore()
    results = vs.get(where={"file_id": file_id})
    if not results["ids"]:
        raise AppException(status_code=404, msg="文档不存在")
    chroma_store.delete_by_file_id(file_id)


def get_document_detail(file_id: str) -> dict:
    """根据 file_id 查询文档详情"""
    vs = chroma_store.get_vectorstore()
    results = vs.get(where={"file_id": file_id}, include=["metadatas", "documents"])

    if not results["ids"]:
        raise AppException(status_code=404, msg="文档不存在")

    return {
        "file_id": file_id,
        "subject": results["metadatas"][0].get("subject", ""),
        "chunk_count": len(results["ids"]),
    }
