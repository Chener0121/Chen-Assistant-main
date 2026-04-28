from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.middleware import register_middleware
from src.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

register_middleware(app)
app.include_router(api_v1_router, prefix="/api/v1")
