# TODO: This file will be replaced later
from src.a_domain.model.conversation import Conversation
from src.a_domain.ports.bussiness.repository_port import RepositoryPort
from src.a_domain.ports.notification.logging_port import ILoggingPort


class InMemoryRepositoryAdapter(RepositoryPort):

    _store: dict[str, Conversation] = {}

    def __init__(self, logger: ILoggingPort):
        self._logger = logger
        self._logger.warning("Using InMemoryRepositoryAdapter. Data is not persistent.")

    async def get_conversation_by_user_id(self, user_id: str) -> Conversation | None:
        self._logger.debug(f"Searching for conversation for user_id: {user_id} in memory.")
        return self._store.get(user_id)

    async def save(self, conversation: Conversation) -> bool:
        self._logger.debug(f"Saving conversation for user_id: {conversation.user_id} in memory.")
        self._store[conversation.user_id] = conversation
        return True
