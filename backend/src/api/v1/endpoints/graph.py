from fastapi import APIRouter

from src.models.schemas import Response

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get(
    "",
    summary="获取知识图谱",
)
async def list_graph() -> Response:
    """返回知识点节点与关联边的完整图谱（待实现）"""
    return Response(data={"nodes": [], "edges": []})
