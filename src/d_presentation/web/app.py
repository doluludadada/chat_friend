import sys

from fastapi import FastAPI
from src.d_presentation.container import Container
from src.d_presentation.web.routers.api_v1 import router as api_v1_router


def create_app() -> FastAPI:
    container = Container()
    container.wire(
        modules=[
            sys.modules[__name__],
            "src.d_presentation.web.endpoints.line_webhook",
        ]
    )

    app = FastAPI(
        title="ChatFriend AI Assistant",
        description="An AI chat assistant service for WhatsApp and Line.",
        version="0.1.0",
    )
    app.state.container = container
    app.include_router(api_v1_router)
    return app
