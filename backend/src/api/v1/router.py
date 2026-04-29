from fastapi import APIRouter

from src.api.v1.endpoints import documents, qa, graph, analytics

api_v1_router = APIRouter()
# 文档上传与管理
api_v1_router.include_router(documents.router)
# 智能问答
api_v1_router.include_router(qa.router)
# 知识图谱
api_v1_router.include_router(graph.router)
# 学习分析
api_v1_router.include_router(analytics.router)
