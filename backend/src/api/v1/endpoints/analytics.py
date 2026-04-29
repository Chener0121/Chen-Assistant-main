from fastapi import APIRouter

from src.models.schemas import Response
from src.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/weak-points", summary="获取薄弱知识点")
async def list_weak_points() -> Response:
    """根据问答记录分析薄弱知识点，带时间衰减"""
    points = analytics_service.list_weak_points()
    return Response(data=points)
