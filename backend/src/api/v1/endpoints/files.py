from fastapi import APIRouter

from src.models.schemas import Response

router = APIRouter(prefix="/files", tags=["files"])


@router.get("")
async def list_files() -> Response:
    return Response(data=[])
