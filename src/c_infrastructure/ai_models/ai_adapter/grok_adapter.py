from functools import cached_property

import httpx
from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from src.a_domain.model.message import Message, MessageRole
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig
from src.c_infrastructure.ai_models.base import BaseAIAdapter


class GrokAdapter(BaseAIAdapter):

    def __init__(self, config: AppConfig, logger: ILoggingPort, model_name: str):
        super().__init__(config, logger, model_name)
        if not self._config.grok_api_key:
            raise ValueError("Missing grok_api_key in configuration.")

    @cached_property
    def _client(self) -> AsyncOpenAI:
        """Lazy-initialized, cached Grok client (using OpenAI-compatible API)."""
        self._logger.debug("Initializing Grok client...")
        return AsyncOpenAI(
            api_key=self._config.grok_api_key,
            base_url="https://api.x.ai/v1",
            timeout=httpx.Timeout(self._config.ai_model_connection_timeout),
        )

    async def _call_api(self, messages: tuple[Message, ...]) -> str:
        api_messages = self._convert_to_api_format(messages)
        try:
            stream = await self._client.chat.completions.create(
                model=self._model_name,
                messages=api_messages,
                temperature=0.7,
                stream=True,
            )

            full_content = ""
            async for chunk in stream:
                content_delta = chunk.choices[0].delta.content or ""
                full_content += content_delta

            return full_content

        except OpenAIError as e:
            self._logger.error(f"Grok API error for model {self._model_name}: {e}")
            return "I'm sorry, I'm having trouble connecting to Grok right now. Please try again in a moment."

    def _convert_to_api_format(
        self, messages: tuple[Message, ...]
    ) -> list[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam]:
        """Converts domain messages to the format required by the Grok API."""
        api_messages = []
        for message in messages:
            if message.role == MessageRole.SYSTEM:
                api_messages.append(ChatCompletionSystemMessageParam(role="system", content=message.content))
            elif message.role == MessageRole.USER:
                api_messages.append(ChatCompletionUserMessageParam(role="user", content=message.content))
            elif message.role == MessageRole.ASSISTANT:
                api_messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=message.content))
        return api_messages
