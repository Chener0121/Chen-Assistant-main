from fastapi import APIRouter, UploadFile

from src.models.schemas import Response

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", summary="获取文档列表")
async def list_documents() -> Response:
    """查询所有已上传的文档"""
    return Response(data=[])


@router.post("", summary="上传文档", status_code=201)
async def upload_document(file: UploadFile) -> Response:
    """上传学习笔记，后台自动解析、分块、向量化存入 Chroma"""
    # TODO: 解析文档 → 分块 → embedding → 存入 Chroma
    return Response(data={"filename": file.filename})


@router.get("/{doc_id}", summary="获取文档详情")
async def get_document(doc_id: str) -> Response:
    """根据 ID 查询单个文档的解析状态与元信息"""
    return Response(data={"doc_id": doc_id})


@router.delete("/{doc_id}", summary="删除文档", status_code=204)
async def delete_document(doc_id: str) -> None:
    """删除文档及其对应的向量数据"""
    # TODO: 从 Chroma 中移除对应向量数据
    pass
