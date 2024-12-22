import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from app.app import get_app

from fastapi import FastAPI, Request
from time import time
from app.core.metrics import start_metrics_server, record_request_metrics

app = FastAPI()

start_metrics_server()

@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
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


def run_api_app() -> None:
    print("Configuring logger...")

    print("Creating FastAPI app...")
    app = FastAPI(docs_url="/docs", openapi_url="/openapi.json", redoc_url="/redoc")
    print("FastAPI app created")

    print("Mounting FastAPI app...")
    app.mount(settings.app.app_mount, get_app())
    print("FastAPI app mounted")

    print("Running FastAPI app with Uvicorn...")
    uvicorn.run(
        app,
        host=settings.app.app_host,
        port=settings.app.app_port,
        log_config=None
    )
    print("FastAPI app running")

if __name__ == "__main__":
    run_api_app()
