import os

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from gateway.error_handlers import register_error_handlers
from gateway.health import health_router
from gateway.logging_middleware import RequestLoggingMiddleware, setup_logging
from gateway.middleware import RequestTimingMiddleware
from gateway.rate_limiter import limiter, rate_limit_exceeded_handler
from gateway.request_context import RequestContextMiddleware


def setup_gateway(app: FastAPI, log_level: str = "INFO") -> None:

    logger = setup_logging(log_level)

    register_error_handlers(app)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(RequestLoggingMiddleware, logger=logger)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RequestContextMiddleware)

    app.include_router(health_router)

    logger.info("API Gateway initialized")
