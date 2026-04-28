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
    """上传学习笔记，自动解析、切片、去重、向量化入库"""
    file_bytes = await file.read()
    result = document_service.process_upload(file_bytes, file.filename)

    if result["skipped"]:
        # 文件已存在，返回 200 + 提示
        return Response(msg="文件已存在，跳过处理", data=result)

    # 新文件创建成功，返回 201
    return JSONResponse(
        status_code=201,
        content=Response(data=result).model_dump(),
    )


@router.get("/{doc_id}", summary="获取文档详情")
async def get_document(doc_id: str) -> Response:
    """根据 doc_id（文件 MD5）查询文档信息"""
    return Response(data={"doc_id": doc_id})


@router.delete("/{doc_id}", summary="删除文档", status_code=204)
async def delete_document(doc_id: str) -> None:
    """删除文档及其对应的向量数据"""
    document_service.delete_document(doc_id)
