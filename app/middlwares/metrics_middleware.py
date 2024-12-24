from time import time

from loguru import logger
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.routing import Match
from starlette.types import ASGIApp

from ..core.metrics import record_request_metrics


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time()

        # Исключаем эндпоинт /metrics из метрик
        if any(request.url.path == "/metrics" for route in request.app.routes if isinstance(route, Match)):
            return await call_next(request)

        response = await call_next(request)
        process_time = time() - start_time

        record_request_metrics(request.method, request.url.path, response.status_code, process_time)

        return response
