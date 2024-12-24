from prometheus_client import Counter, Histogram, start_http_server, make_asgi_app

# Метрики
REQUEST_COUNT = Counter("app_requests_total", "Общее количество запросов", ['method', 'endpoint', 'status_code'])
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Время обработки запросов", ['method', 'endpoint'])

metrics_app = make_asgi_app()

def start_metrics_server(port=8001):
    start_http_server(port)
    print(f"Metrics server started on port {port}")

def record_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
