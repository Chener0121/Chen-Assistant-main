from fastapi import APIRouter

from src.models.schemas import Response
from src.services import qa_service

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("", summary="智能问答")
async def ask_question(question: str) -> Response:
    """基于向量检索 + 单次 LLM 调用的智能问答"""
    result = qa_service.ask(question)
    return Response(data=result)
