from enum import Enum
from typing import Annotated

from typer import Typer, Argument
from app.main import run_api_app

cli = Typer(help="NeoBitCloud CLI")


class Apps(str, Enum):
    api = "api"
    background_tasks = "background_tasks"


@cli.command(help="Run API app")
def run(
        app: Annotated[Apps, Argument(help="App to run")] = Apps.api
):
    match app:
        case Apps.api:
            run_api_app()

        case Apps.background_tasks:
            #TODO make background tasks
            pass


cli()