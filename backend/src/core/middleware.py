from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.exceptions import AppException, app_exception_handler


def register_middleware(app: FastAPI) -> None:
    # 全局跨域，允许所有来源、方法、请求头
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # 全局异常处理，AppException 统一返回 Response 格式
    app.add_exception_handler(AppException, app_exception_handler)
