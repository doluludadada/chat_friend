# src/d_presentation/web/endpoints/line_webhook.py

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Header, Request
from src.c_infrastructure.platforms.line.line_handler import LineWebhookHandler
from src.d_presentation.container import Container

router = APIRouter()


@router.post("/")
@inject
async def handle_line_webhook(
    request: Request,
    x_line_signature: str | None = Header(None),
    handler: LineWebhookHandler = Depends(Provide[Container.line_webhook_handler]),
):
    await handler.handle(request, x_line_signature)
    return {"status": "ok"}
