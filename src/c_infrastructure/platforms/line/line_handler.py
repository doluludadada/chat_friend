from fastapi import Request
from src.b_application.use_cases.conversation_usecase import ConversationUsecase
from src.c_infrastructure.platforms.line.line_security import LineSecurityService


class LineWebhookHandler:
    def __init__(
        self,
        security_service: LineSecurityService,
        usecase: ConversationUsecase,
    ):
        self._security_service = security_service
        self._usecase = usecase

    async def handle(self, request: Request, signature: str | None):
        pass
