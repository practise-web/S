from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request, Response
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)

class RateLimitExceeded(Exception):
    pass

async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests, try again later."}
    )