"""
Groq AI adapter implementation.

Infrastructure layer adapter that calls GroqCloud via OpenAI-compatible API.
"""
from __future__ import annotations
import asyncio
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
from src.c_infrastructure.ai_models.base import BaseAIAdapter
from src.b_application.configuration.schemas import AppConfig



class GroqAIAdapter(BaseAIAdapter):
    """
    Groq (GroqCloud) adapter via OpenAI-compatible API.
    """

    groq_base_url = "https://api.groq.com/openai/v1"

    def __init__(
        self,
        config: AppConfig,
        logger: ILoggingPort,
        model_name: str = "openai/gpt-oss-20b",
    ):
        super().__init__(config, logger, model_name)

        if not self._config.groq_api_key:
            raise ValueError("Missing groq_api_key in configuration. ")

    @cached_property
    def _client(self) -> AsyncOpenAI:
        self._logger.debug("Initialising AsyncOpenAI client...")
        return AsyncOpenAI(
            api_key=self._config.groq_api_key,
            base_url=self.groq_base_url,
            timeout=httpx.Timeout(self._config.ai_model_connection_timeout),
        )

    async def _call_api(self, messages: tuple[Message, ...]) -> str:
        """
        Calls Groq Chat Completions and returns assistant text.
        """
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
        except asyncio.CancelledError:
            raise
        except (OpenAIError, httpx.HTTPError) as e:
            self._logger.error(f"GROQ API error for model {self._model_name}: {e}")
            return "I'm sorry, I'm having trouble connecting to GROQ right now. Please try again in a moment."
        except Exception as e:
            self._logger.error(f"Unexpected error calling GROQ ({self._model_name}): {e}")
            return "I'm sorry, something went wrong. Please try again."

    def _convert_to_api_format(
        self, messages: tuple[Message, ...]
    ) -> list[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam]:
        api_messages = []
        for message in messages:
            if message.role == MessageRole.SYSTEM:
                api_messages.append(ChatCompletionSystemMessageParam(role="system", content=message.content))
            elif message.role == MessageRole.USER:
                api_messages.append(ChatCompletionUserMessageParam(role="user", content=message.content))
            elif message.role == MessageRole.ASSISTANT:
                api_messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=message.content))
        return api_messages