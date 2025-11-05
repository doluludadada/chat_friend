from typing import Protocol

from src.a_domain.model.message import Message


class AiPort(Protocol):
    async def generate_reply(self, messages: tuple[Message, ...]) -> Message: ...
