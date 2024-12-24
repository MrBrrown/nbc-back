import time
from enum import Enum
from typing import Annotated

import uvicorn
from typer import Typer, Argument

from app.core.config import settings

cli = Typer(help="NeoBitCloud CLI")

class Apps(str, Enum):
    api = "api"
    background_tasks = "background_tasks"

@cli.command(help="Run API app")
def run(
        app: Annotated[Apps, Argument(help="App to run")] = Apps.api
):
    print("Run command started")
    match app:
        case Apps.api:
            print("Running API app")
            uvicorn.run(
                "app.main:app",
                host=settings.app.app_host,
                port=settings.app.app_port,
                reload=False
            )

        case Apps.background_tasks:
            print("Running background tasks")
            run_background_tasks()

def run_background_tasks():
    print("Starting background tasks...")
    while True:
        print("Executing periodic task...")
        time.sleep(10)

cli()
