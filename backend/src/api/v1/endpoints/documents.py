from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse

from src.models.schemas import Response
from src.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", summary="获取文档列表")
async def list_documents() -> Response:
    """返回所有已上传的文档，按 file_id 去重"""
    docs = document_service.list_documents()
    return Response(data=docs)


@router.post("", summary="上传文档", response_model=None)
async def upload_document(file: UploadFile) -> Response | JSONResponse:
    """上传 PDF/DOCX 学习笔记，自动解析、切片、增量去重、向量化入库。"""
    file_bytes = await file.read()
    result = document_service.process_upload(file_bytes, file.filename)

    if result["added"] == 0 and result["deleted"] == 0:
        return Response(msg="文件内容未变化，跳过处理", data=result)

    return JSONResponse(
        status_code=201,
        content=Response(data=result).model_dump(),
    )


@router.get("/{file_id}", summary="获取文档详情")
async def get_document(file_id: str) -> Response:
    """根据 file_id 查询文档详情（学科、chunk 数量）"""
    detail = document_service.get_document_detail(file_id)
    return Response(data=detail)


@router.delete("/{file_id}", summary="删除文档", status_code=204)
async def delete_document(file_id: str) -> None:
    """删除文档及其所有向量数据"""
    document_service.delete_document(file_id)
