from dataclasses import replace
from datetime import datetime, timezone

from src.a_domain.model.conversation import Conversation
from src.a_domain.model.message import Message
from src.a_domain.ports.bussiness.repository_port import RepositoryPort
from src.a_domain.ports.notification.logging_port import ILoggingPort


class StateManager:
    def __init__(self, repository: RepositoryPort, logger: ILoggingPort):
        self._repository = repository
        self._logger = logger

    def update_state(self, conversation: Conversation, new_messages: list[Message]) -> Conversation:
        if not new_messages:
            return conversation

        updated_msgs = conversation.messages + tuple(new_messages)
        updated_conversation = replace(conversation, messages=updated_msgs, updated_at=datetime.now(timezone.utc))
        return updated_conversation

    async def reset_conversation(self, conversation: Conversation):
        cleared_conversation = conversation.clear_history()
        await self._repository.save(cleared_conversation)
        self._logger.info(f"Conversation memory cleared for user_id: {conversation.user_id}")
        return cleared_conversation

    async def save(self, conversation: Conversation) -> None:
        await self._repository.save(conversation)
        self._logger.debug(f"Conversation state saved for user_id: {conversation.user_id}")
