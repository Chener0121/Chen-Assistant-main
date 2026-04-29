from fastapi import APIRouter

from src.models.schemas import Response, QARequest
from src.services import qa_service

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("", summary="智能问答")
async def ask_question(body: QARequest) -> Response:
    """基于向量检索 + LLM 的智能问答（Chain 模式，1 次 LLM 调用）"""
    result = qa_service.ask(body.question, thread_id=body.thread_id)
    return Response(data=result)
