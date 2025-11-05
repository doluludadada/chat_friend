from typing import Protocol

from src.a_domain.model.conversation import Conversation


class RepositoryPort(Protocol):
    async def get_conversation_by_user_id(self, user_id: str) -> Conversation | None: ...

    async def save(self, conversation: Conversation) -> bool: ...
