from fastapi import APIRouter

from src.models.schemas import Response

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
async def list_items() -> Response:
    return Response(data=[])
