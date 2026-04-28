from fastapi import APIRouter

from src.api.v1.endpoints import users, items, files, qa, graph

api_v1_router = APIRouter()
api_v1_router.include_router(users.router)
api_v1_router.include_router(items.router)
api_v1_router.include_router(files.router)
api_v1_router.include_router(qa.router)
api_v1_router.include_router(graph.router)
