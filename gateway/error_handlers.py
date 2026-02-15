import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.responses import JSONResponse

logger = logging.getLogger("gateway")


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    type: Optional[str] = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: List[ErrorDetail] = []
    request_id: str = ""


class ErrorResponse(BaseModel):
    success: bool = False
    detail: str = ""
    error: ErrorBody


STATUS_CODE_MAP = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMIT_EXCEEDED",
    500: "INTERNAL_SERVER_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


def _get_error_code(status_code: int) -> str:
    return STATUS_CODE_MAP.get(status_code, f"HTTP_{status_code}")


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "")


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = _get_request_id(request)
    detail_str = str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=detail_str,
            error=ErrorBody(
                code=_get_error_code(exc.status_code),
                message=detail_str,
                request_id=request_id,
            ),
        ).model_dump(),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = _get_request_id(request)
    details = []
    for error in exc.errors():
        loc = error.get("loc", ())
        field = ".".join(str(part) for part in loc) if loc else None
        details.append(
            ErrorDetail(
                field=field,
                message=error.get("msg", "Validation error"),
                type=error.get("type"),
            )
        )

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            detail="Request validation failed",
            error=ErrorBody(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                details=details,
                request_id=request_id,
            ),
        ).model_dump(),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        extra={"request_id": request_id},
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail="An unexpected error occurred. Please try again later.",
            error=ErrorBody(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred. Please try again later.",
                request_id=request_id,
            ),
        ).model_dump(),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
