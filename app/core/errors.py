from fastapi import Request
from fastapi.responses import JSONResponse


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code


async def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})
