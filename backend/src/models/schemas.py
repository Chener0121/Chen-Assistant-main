from typing import Any

from pydantic import BaseModel


class Response(BaseModel):
    """统一返回结果"""
    code: int = 200
    msg: str = "success"
    data: Any = None


class DocumentUploadResult(BaseModel):
    """文档上传增量处理结果"""
    file_id: str
    subject: str     # 学科
    added: int       # 新增 chunk 数
    skipped: int     # 已存在跳过的 chunk 数
    deleted: int     # 被移除的旧 chunk 数


class DocumentItem(BaseModel):
    """文档列表项"""
    file_id: str
    subject: str


class DocumentDetail(BaseModel):
    """文档详情"""
    file_id: str
    subject: str
    chunk_count: int


class QARequest(BaseModel):
    """问答请求"""
    question: str


class NoteCorrection(BaseModel):
    """笔记纠错项"""
    original: str
    corrected: str


class QAResult(BaseModel):
    """问答结构化输出"""
    subject: str
    answer: str
    knowledge_points: list[str]
    note_corrections: list[NoteCorrection]
    used_note: bool


class WeakPoint(BaseModel):
    """薄弱知识点"""
    knowledge_point: str
    subject: str
    ask_count: int
    missing_count: int
    correction_count: int
    last_active: str
    level: str       # high / medium / low
