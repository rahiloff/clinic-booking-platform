"""
Doctor Booking Platform — Request Logging Middleware

Combined middleware that:
1. Assigns a unique request ID to every request (or uses X-Request-ID header)
2. Binds request_id to structlog context (appears in all log lines for that request)
3. Logs request completion with method, path, status, and duration
4. Returns X-Request-ID in response headers for client-side correlation
"""

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Assigns request IDs and logs request lifecycle."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Bind to structlog context — all logs during this request include request_id
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error=str(exc),
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log at appropriate level based on status code
        log_method = logger.info if response.status_code < 400 else logger.warning
        log_method(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        # Return request ID to client
        response.headers["X-Request-ID"] = request_id
        return response
