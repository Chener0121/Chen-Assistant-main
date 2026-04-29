from fastapi import APIRouter

from src.ai.vectorstores import chroma_store
from src.models.schemas import Response
from src.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/weak-points", summary="获取薄弱知识点")
async def list_weak_points() -> Response:
    """根据最近 30 天的问答记录分析薄弱知识点，带时间衰减"""
    points = analytics_service.list_weak_points()
    return Response(data=points)


@router.delete("/qa-records", summary="清空问答记录", status_code=204)
async def clear_qa_records() -> None:
    """清空所有问答记录（不影响文档向量数据）"""
    chroma_store.clear_qa_records()


@router.get("/daily-stats", summary="提问统计")
async def get_daily_stats(mode: str = "daily") -> Response:
    """mode=daily 近14天，mode=hourly 近14小时"""
    stats = analytics_service.daily_stats(mode)
    return Response(data=stats)
