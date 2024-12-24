from fastapi import FastAPI
from app.api.v1.endpoints.routes import api_router

def setup_routes(app: FastAPI) -> None:
    app.include_router(api_router)

def get_app() -> FastAPI:
    app = FastAPI(title="NeoBitCloud")
    setup_routes(app)
    return app
