from fastapi import HTTPException, Request, status
from pydantic import ValidationError
from src.b_application.pipeline import Pipeline
from src.c_infrastructure.platforms.line.dto.line_dto import LineWebhookPayload
from src.c_infrastructure.platforms.line.line_constants import EVENT_TYPE_MESSAGE, MESSAGE_TYPE_TEXT
from src.c_infrastructure.platforms.line.line_security import LineSecurityService

class LineWebhookHandler:
    def __init__(self, security_service: LineSecurityService, pipeline: Pipeline):
        self._security_service = security_service
        self._pipeline = pipeline

    async def handle(self, request: Request, signature: str | None):
        body = await request.body()
        if not self._security_service.verify_signature(body, signature):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid signature')
        
        try:
            payload = LineWebhookPayload.model_validate_json(body)
        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Invalid payload: {e}')

        for event in payload.events:
            if event.type == EVENT_TYPE_MESSAGE and event.message and (event.message.type == MESSAGE_TYPE_TEXT):
                user_id = event.source.userId
                text_content = event.message.text
                if text_content:
                    await self._pipeline.execute(user_id=user_id, incoming_content=text_content)
