from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse

from src.models.schemas import Response
from src.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", summary="获取文档列表")
async def list_documents() -> Response:
    """从向量库中聚合已上传的去重文档列表"""
    docs = document_service.list_documents()
    return Response(data=docs)


@router.post("", summary="上传文档")
async def upload_document(file: UploadFile) -> Response:
    """上传学习笔记，chunk 级增量 diff，仅 embedding 变化的部分"""
    file_bytes = await file.read()
    result = document_service.process_upload(file_bytes, file.filename)

    # 完全无变化（added=0, deleted=0）视为已存在
    if result["added"] == 0 and result["deleted"] == 0:
        return Response(msg="文件内容未变化，跳过处理", data=result)

    # 有新增或更新
    return JSONResponse(
        status_code=201,
        content=Response(data=result).model_dump(),
    )


@router.get("/{file_id}", summary="获取文档详情")
async def get_document(file_id: str) -> Response:
    """根据 file_id 查询文档详情（学科、chunk 数量等）"""
    detail = document_service.get_document_detail(file_id)
    return Response(data=detail)


@router.delete("/{file_id}", summary="删除文档", status_code=204)
async def delete_document(file_id: str) -> None:
    """删除文档及其所有向量数据"""
    document_service.delete_document(file_id)
