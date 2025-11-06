from abc import ABC, abstractmethod

from src.a_domain.model.message import Message, MessageRole
from src.a_domain.ports.bussiness.ai_port import AiPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig


class BaseAIAdapter(AiPort, ABC):
    """
    An abstract base class for AI model adapters.
    """

    def __init__(self, config: AppConfig, logger: ILoggingPort, model_name: str):
        self._config = config
        self._logger = logger
        self._model_name = model_name

    @abstractmethod
    async def _call_api(self, messages: tuple[Message, ...]) -> str: ...

    async def generate_reply(self, messages: tuple[Message, ...]) -> Message:
        """Orchestrates the reply generation process (Template Method)."""
        self._logger.debug(f"[{self.__class__.__name__}] Generating reply with model: {self._model_name}")
        self._logger.trace(f"[{self.__class__.__name__}] Sending {len(messages)} messages to model.")

        try:
            reply_content = await self._call_api(messages)
            self._logger.success(
                f"[{self.__class__.__name__}] Successfully received reply from model: {self._model_name}"
            )
            return Message(role=MessageRole.ASSISTANT, content=reply_content)
        except Exception as e:
            self._logger.critical(f"[{self.__class__.__name__}] An unexpected critical error occurred: {e}")
            return Message(
                role=MessageRole.ASSISTANT,
                content="I've encountered an unexpected error. The technical team has been notified.",
            )
