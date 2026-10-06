import sys
import uuid
import time
from contextvars import ContextVar
from loguru import logger
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


def setup_logging(level: str = "INFO"):
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "req=<cyan>{extra[request_id]}</cyan> | "
            "<level>{message}</level>"
        ),
        filter=lambda record: record["extra"].setdefault(
            "request_id", request_id_ctx.get()
        ),
    )


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request.state.request_id = rid
        token = request_id_ctx.set(rid)
        start = time.perf_counter()
        status = "-"
        response = None
        try:
            response = await call_next(request)
            status = response.status_code
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.info(
                "{} {} -> {} ({} ms)",
                request.method, request.url.path, status, duration_ms,
            )
            request_id_ctx.reset(token)
        response.headers["X-Request-ID"] = rid
        return response
