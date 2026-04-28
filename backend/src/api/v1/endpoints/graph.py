from fastapi import APIRouter

from src.models.schemas import Response

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", summary="获取知识图谱")
async def list_graph() -> Response:
    """返回知识点节点与关联边的完整图谱"""
    # TODO: 从向量库聚合知识点，构建图结构
    return Response(data={"nodes": [], "edges": []})


@router.get("/weak-points", summary="获取薄弱知识点")
async def list_weak_points() -> Response:
    """根据问答记录分析用户薄弱知识点并返回"""
    # TODO: 统计问答错误率，标记薄弱知识点
    return Response(data=[])
