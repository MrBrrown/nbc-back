import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from app.application import get_app

from fastapi import FastAPI, Request
from time import time
from app.core.metrics import start_metrics_server, record_request_metrics
from app.api.v1.endpoints import users_api

app = FastAPI()
app.include_router(users_api.user_router, prefix="/api/v1", tags=["users"])

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
    app = FastAPI(docs_url=None)
    print("FastAPI app created")

    app.mount(settings.app.app_mount, get_app())
    uvicorn.run(
        app, host=settings.app.app_host, port=settings.app.app_port, log_config=None
    )
    print("FastAPI app running")

if __name__ == "__main__":
    run_api_app()
    
    
