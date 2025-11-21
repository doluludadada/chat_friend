from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.a_domain.model.message import Message


@dataclass(frozen=True)
class Conversation:
    user_id: str
    id: UUID = field(default_factory=uuid4)
    selected_model_name: str | None = None
    messages: tuple[Message, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_message(self, message: Message):
        """ """
        new_messages = self.messages + (message,)
        return replace(self, messages=new_messages, updated_at=datetime.now(timezone.utc))

    def add_messages(self, messages: list[Message] | tuple[Message, ...]):
        """ """
        new_messages = self.messages + tuple(messages)
        return replace(self, messages=new_messages, updated_at=datetime.now(timezone.utc))

    def clear_history(self):
        """
        clean message history, but keep user's conversation stage.
        """
        return replace(self, messages=tuple(), updated_at=datetime.now(timezone.utc))
