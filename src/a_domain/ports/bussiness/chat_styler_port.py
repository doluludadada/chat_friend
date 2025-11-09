from typing import Protocol

from src.a_domain.model.message import Message


class IChatStylerPort(Protocol):
    """
    An interface for formatting AI-generated messages to be suitable for chat platforms.
    """

    def format_response(self, message: Message) -> tuple[Message, ...]:
        """
        Takes a single assistant message and returns one or more formatted messages.
        """
        ...
