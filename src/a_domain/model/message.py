from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.a_domain.types.enums import MessageRole


@dataclass(frozen=True, kw_only=True)
class Message:
    id: UUID = field(default_factory=uuid4)
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
