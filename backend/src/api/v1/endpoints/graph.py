from fastapi import APIRouter

from src.models.schemas import Response

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", summary="获取知识图谱")
async def list_graph() -> Response:
    """返回知识点节点与关联边的完整图谱"""
    # TODO: 从向量库聚合知识点，构建图结构
    return Response(data={"nodes": [], "edges": []})
