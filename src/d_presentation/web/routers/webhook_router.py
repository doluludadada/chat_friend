from fastapi import APIRouter
from src.d_presentation.web.endpoints import line_webhook

router = APIRouter()

router.include_router(line_webhook.router, prefix="/line", tags=["LINE Webhook"])
