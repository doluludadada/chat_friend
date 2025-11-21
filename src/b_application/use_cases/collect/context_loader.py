from src.a_domain.model.conversation import Conversation
from src.a_domain.model.message import Message, MessageRole
from src.a_domain.ports.bussiness.repository_port import RepositoryPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig


class ContextLoader:
    def __init__(self, repository: RepositoryPort, config: AppConfig, logger: ILoggingPort):
        self._repository = repository
        self._config = config
        self._logger = logger

    async def execute(self, user_id: str) -> Conversation:
        conversation = await self._repository.get_conversation_by_user_id(user_id)
        if conversation:
            self._logger.debug(f"Found existing conversation for user_id: {user_id}")
            return conversation

        self._logger.info(f"Creating new conversation context for user_id: {user_id}")
        initial_messages = []
        if self._config.ai_system_prompt:
            initial_messages.append(Message(role=MessageRole.SYSTEM, content=self._config.ai_system_prompt))
        return Conversation(user_id=user_id, messages=tuple(initial_messages))
