from fastapi import APIRouter

from src.models.schemas import Response
from src.services import graph_service

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", summary="获取知识图谱")
async def list_graph() -> Response:
    """返回知识点节点与关联关系，包含学科、文档、知识点三类节点"""
    graph = graph_service.build_graph()
    return Response(data=graph)
