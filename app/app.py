from fastapi import FastAPI
from app.api.v1.endpoints.routes import ROUTES


def setup_routes(app: FastAPI) -> None:
    for prefix, router in ROUTES.items():
        app.include_router(router, prefix=prefix)



def get_app() -> FastAPI:
    app = FastAPI(title="NeoBitCloud")
    setup_routes(app)
    return app