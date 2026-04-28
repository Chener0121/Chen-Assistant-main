from fastapi import Request
from fastapi.responses import JSONResponse

from src.models.schemas import Response


class AppException(Exception):
    def __init__(self, status_code: int = 400, msg: str = "error"):
        self.status_code = status_code
        self.msg = msg


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=Response(code=exc.status_code, msg=exc.msg).model_dump(),
    )
