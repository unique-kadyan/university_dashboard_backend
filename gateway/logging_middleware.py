import json
import logging
import sys
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

EXTRA_FIELDS = (
    "request_id",
    "method",
    "path",
    "status_code",
    "duration_ms",
    "user_id",
    "client_ip",
    "user_agent",
)


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in EXTRA_FIELDS:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        if record.exc_info and record.exc_info[0]:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, default=str)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("gateway")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

    logging.getLogger("uvicorn.access").handlers = []

    return logger


SKIP_PATHS = {"/health", "/"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger: logging.Logger = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger("gateway")

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        if request.url.path in SKIP_PATHS:
            return response

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        request_id = getattr(request.state, "request_id", "")
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)

        self.logger.info(
            "%s %s -> %s (%.2fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "user_id": user_id,
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", ""),
            },
        )
        return response
