from fastapi import APIRouter

from src.api.v1.endpoints import users, items

api_v1_router = APIRouter()
api_v1_router.include_router(users.router)
api_v1_router.include_router(items.router)
