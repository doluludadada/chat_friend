from fastapi import FastAPI
from src.d_presentation.web.routers.api_v1 import router as api_v1_router

def create_app() -> FastAPI:
    app = FastAPI(
        title='ChatFriend AI Assistant', 
        description='An AI chat assistant service for WhatsApp and Line.', 
        version='0.1.0'
    )
    app.include_router(api_v1_router)
    return app
