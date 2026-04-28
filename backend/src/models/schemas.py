from typing import Any

from pydantic import BaseModel


class Response(BaseModel):
    code: int = 200
    msg: str = "success"
    data: Any = None


class DocumentUploadResult(BaseModel):
    """文档上传处理结果"""
    filename: str
    file_md5: str
    chunk_count: int
    skipped: bool = False
