from fastapi import APIRouter

from src.models.schemas import Response, SummarizeRequest
from src.services import qa_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/summary", summary="对话摘要压缩")
async def summarize_messages(body: SummarizeRequest) -> Response:
    """将旧消息压缩为摘要，减少 token 开销"""
    summary = qa_service.summarize(body.messages)
    return Response(data={"summary": summary})
