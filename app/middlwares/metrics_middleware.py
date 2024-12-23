from fastapi import  Request
from time import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import structlog

logger = structlog.get_logger()

def record_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    logger.info("Request processed", method=method, endpoint=endpoint, status_code=status_code, duration=duration)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time()
        response = await call_next(request)
        process_time = time() - start_time
        record_request_metrics(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=process_time
        )
        return response