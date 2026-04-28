from typing import Any

from pydantic import BaseModel


class Response(BaseModel):
    code: int = 200
    msg: str = "success"
    data: Any = None


class DocumentUploadResult(BaseModel):
    """文档上传增量处理结果"""
    file_id: str
    added: int       # 新增 chunk 数
    skipped: int     # 已存在跳过的 chunk 数
    deleted: int     # 被移除的旧 chunk 数
