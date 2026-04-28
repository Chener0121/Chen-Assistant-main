from typing import Any

from pydantic import BaseModel


class Response(BaseModel):
    code: int = 0
    msg: str = "success"
    data: Any = None
