from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

from configs.redis_config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD


def _build_redis_uri() -> str:
    auth = f":{REDIS_PASSWORD}@" if REDIS_PASSWORD else ""
    return f"redis://{auth}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


def _key_func(request: Request) -> str:
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    return get_remote_address(request)


limiter = Limiter(
    key_func=_key_func,
    storage_uri=_build_redis_uri(),
    default_limits=["100/minute"],
    strategy="fixed-window",
    swallow_errors=True,
)


def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "")
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "detail": f"Rate limit exceeded: {exc.detail}",
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded: {exc.detail}",
                "details": [],
                "request_id": request_id,
            },
        },
        headers={"Retry-After": "60"},
    )
