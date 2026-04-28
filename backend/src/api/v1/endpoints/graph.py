from fastapi import APIRouter

from src.models.schemas import Response

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("")
async def list_graph() -> Response:
    return Response(data=[])
