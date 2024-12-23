import asyncio
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from application import get_app
from core.config import settings
from core.logging import configure_logger
from core.metrics import start_metrics_server
from models.bucket import Bucket
from models.object import Object
from models.user import User
from db import init_alembic, mapper_registry
from middlwares.metrics_middleware import MetricsMiddleware

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_api_app() -> None:
    print("Configuring logger...")
    configure_logger()
    print("Logger configured")

    print("Configuring database...")
    mapper_registry.configure()
    #TODO if ENVIRONMENT = "DEV"
    asyncio.run(init_alembic())
    print("Database configured")

    print("Creating FastAPI app...")
    app = FastAPI(docs_url="/docs", openapi_url="/openapi.json", redoc_url="/redoc")
    print("FastAPI app created")

    # CORS configuration
    origins = [
        "http://localhost:3001"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],  # Or specify: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        allow_headers=["*"],  # Or specify: ["Content-Type", "Authorization", "buckets"]
    )

    print("Add metrics middleware...")
    app.add_middleware(MetricsMiddleware)
    print("Metrics middleware added")

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

    print("Starting metrics server...")
    start_metrics_server()
    print("Metrics server started")

if __name__ == "__main__":
    run_api_app()