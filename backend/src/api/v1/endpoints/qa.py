from fastapi import APIRouter

from src.models.schemas import Response

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("", summary="智能问答")
async def ask_question(question: str) -> Response:
    """基于向量检索 + LLM 生成回答"""
    # TODO: 检索相关文档片段 → 构建 prompt → 调用 LLM
    return Response(data={"question": question, "answer": ""})
