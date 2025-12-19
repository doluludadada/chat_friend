from functools import cached_property
from typing import Any
import httpx
from openai import AsyncOpenAI, OpenAIError
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
        self._logger.debug("Initializing Grok client (xAI)...")
        return AsyncOpenAI(
            api_key=self._config.grok_api_key,
            base_url="https://api.x.ai/v1",
            timeout=httpx.Timeout(self._config.ai_model_connection_timeout),
        )

    async def _call_api(self, messages: tuple[Message, ...]) -> str:
        api_messages = self._convert_to_api_format(messages)
        tools: list[dict[str, Any]] = []

        if self._config.enable_web_search:
            web_search_tool: dict[str, Any] = {"type": "web_search"}
            web_search_filters: dict[str, Any] = {}

            if self._config.web_search_allowed_domains:
                web_search_filters["allowed_domains"] = list(
                    self._config.web_search_allowed_domains
                )
            if self._config.web_search_excluded_domains:
                web_search_filters["excluded_domains"] = list(
                    self._config.web_search_excluded_domains
                )

            if web_search_filters:
                web_search_tool["filters"] = web_search_filters

            tools.append(web_search_tool)

        if self._config.enable_x_search:
            x_search_tool: dict[str, Any] = {"type": "x_search"}
            x_search_filters: dict[str, Any] = {}

            if self._config.x_search_allowed_handles:
                x_search_filters["allowed_x_handles"] = list(
                    self._config.x_search_allowed_handles
                )
            if self._config.x_search_excluded_handles:
                x_search_filters["excluded_x_handles"] = list(
                    self._config.x_search_excluded_handles
                )

            if x_search_filters:
                x_search_tool["filters"] = x_search_filters

            tools.append(x_search_tool)

        extra_body: dict[str, Any] = {}

        if self._config.enable_inline_citations:
            extra_body["include"] = ["inline_citations"]

        if tools:
            extra_body["tools"] = tools

        try:
            params = {
                "model": self._model_name,
                "messages": api_messages,
                "temperature": 0.7,
                "stream": True,
            }

            if extra_body:
                params["extra_body"] = extra_body

            stream = await self._client.chat.completions.create(**params)

            full_content = ""
            async for chunk in stream:
                content_delta = chunk.choices[0].delta.content or ""
                full_content += content_delta

            return full_content

        except OpenAIError as e:
            self._logger.error(f"Grok API error for model {self._model_name}: {e}")
            return f"I'm sorry, I encountered an error connecting to Grok: {e}"
        except Exception as e:
            self._logger.critical(f"Unexpected error in Grok adapter: {e}")
            return "An unexpected error occurred."

    def _convert_to_api_format(self, messages: tuple[Message, ...]):
        api_messages = []
        for message in messages:
            role = "assistant"
            if message.role == MessageRole.SYSTEM:
                role = "system"
            elif message.role == MessageRole.USER:
                role = "user"
            api_messages.append({"role": role, "content": message.content})
        return api_messages
