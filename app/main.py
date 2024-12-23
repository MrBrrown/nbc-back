import asyncio
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .application import get_app
from .core.config import settings
from .core.logging import configure_logger
from .core.metrics import start_metrics_server, metrics_app
from .models.bucket import Bucket
from .models.object import Object
from .models.user import User
from .db import init_alembic, mapper_registry
from .middlwares.metrics_middleware import MetricsMiddleware

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


async def configure_app() -> None:
    print("Configuring logger...")
    configure_logger(enable_json_logs=True, enable_sql_logs=False, level="INFO")
    print("Logger configured")

    print("Configuring database...")
    mapper_registry.configure()

    if settings.app.environment == "dev":
        await init_alembic()
    print("Database configured")

async def startup():
    await configure_app()
    print("starting app...")

app = FastAPI(
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc",
    on_startup=[startup],
    title="NeoBitCloud",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost:3001",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Add metrics middleware...")
app.add_middleware(MetricsMiddleware)
print("Metrics middleware added")

print("Mounting FastAPI app...")
app.mount(settings.app.app_mount, get_app())
print("FastAPI app mounted")

print("Starting metrics server...")
start_metrics_server()
app.mount("/metrics", metrics_app)
print("Metrics server started")
