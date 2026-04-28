from fastapi import APIRouter

from src.models.schemas import Response

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def list_users() -> Response:
    return Response(data=[])
