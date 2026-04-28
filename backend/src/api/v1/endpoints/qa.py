from fastapi import APIRouter

from src.models.schemas import Response

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("")
async def ask_question() -> Response:
    return Response(data=[])
