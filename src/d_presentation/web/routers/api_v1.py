from fastapi import APIRouter
from src.d_presentation.web.routers import webhook_router

router = APIRouter(prefix="/v1")

router.include_router(webhook_router.router, prefix="/webhook")
