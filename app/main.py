import asyncio
import os
import sys

import uvicorn
from fastapi import FastAPI

from application import get_app
from core.config import settings
from core.logging import configure_logger
from db import init_alembic

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_api_app() -> None:
    print("Configuring logger...")
    configure_logger()
    print("Logger configured")

    print("Creating FastAPI app...")
    app = FastAPI(docs_url="/docs", openapi_url="/openapi.json", redoc_url="/redoc")
    print("FastAPI app created")

    print("Mounting FastAPI app...")
    app.mount(settings.app.app_mount, get_app())
    print("FastAPI app mounted")

    print("Initializing database...")
    #TODO if ENVIRONMENT = "DEV"
    asyncio.run(init_alembic())
    print("Database initialized")

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