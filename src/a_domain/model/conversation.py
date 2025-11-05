from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.a_domain.model.message import Message


@dataclass(frozen=True)
class Conversation:
    user_id: str
    id: UUID = field(default_factory=uuid4)
    messages: tuple[Message, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
