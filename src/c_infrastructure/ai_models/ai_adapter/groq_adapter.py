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
from src.a_domain.ports.bussiness.web_search_port import WebSearchPort
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
        web_search: WebSearchPort | None = None,
    ):
        super().__init__(config, logger, model_name)

        if not self._config.groq_api_key:
            raise ValueError("Missing groq_api_key in configuration. ")

        self._web_search = web_search

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
        try:
            api_messages = self._convert_to_api_format(messages)

            # 先進行搜尋
            if self._should_search(messages):
                search_results = await self._enrich_with_search(messages)
                if search_results:
                    template = (
                        self._config.ai_rag_injection_prompt
                    )
                    rag_instruction = {
                        "role": "system",
                        "content": template.format(search_results=search_results),
                    }
                    
                    # 調整訊息順序
                    # 如果最後一則訊息是 User，我們把 Context 插在它前面，效果通常最好
                    if api_messages and api_messages[-1]['role'] == 'user':
                        api_messages.insert(-1, rag_instruction)
                    else:
                        api_messages.append(rag_instruction)
            self._logger.info("執行查詢流程結束")
        except Exception as e:
            self._logger.error(f"Unexpected error calling tailivy : {e}")
            return "I'm sorry, something went wrong. Please try again."

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
            return f"GROQ API error for model {self._model_name}: {e}" + "I'm sorry, I'm having trouble connecting to GROQ right now. Please try again in a moment."
        except Exception as e:
            self._logger.error(f"Unexpected error calling GROQ ({self._model_name}): {e}")
            return "I'm sorry, something went wrong. Please try again."

    async def _enrich_with_search(self, messages: tuple[Message, ...]) -> str:
        """Execute web search and format results."""
        if not self._web_search:
            return ""
        
        # Extract the latest user query
        user_query = ""
        for msg in reversed(messages):
            if msg.role == MessageRole.USER:
                user_query = msg.content
                break
        
        if not user_query:
            return ""
        
        try:
            self._logger.debug(f"Performing web search for: {user_query}")
            self._logger.info(f"Performing web search for: {user_query}")
            results = await self._web_search.search(
                user_query, 
                limit=getattr(self._config, "web_search_max_results", 3)
            )
            self._logger.info(f"查詢結果: {results}")
            if not results:
                return ""
            
            # Format results
            formatted = "Recent web search results:\n"
            for i, result in enumerate(results, 1):
                formatted += f"\n[{i}] {result.title}\n"
                formatted += f"URL: {result.url}\n"
                formatted += f"Content: {result.content}\n"
            
            return formatted
        except Exception as e:
            self._logger.error(f"Web search failed: {e}")
            return ""

    def _should_search(self, messages: tuple[Message, ...]) -> bool:
        """Determine if web search should be triggered."""
        if not getattr(self._config, "enable_web_search", False) or not self._web_search:
            return False
        
        # Get the latest user message
        for msg in reversed(messages):
            if msg.role == MessageRole.USER:
                content = msg.content.lower()
                # Keywords that trigger search
                search_triggers = {
                    "latest", "recent", "news", "current", "today",
                    "stock", "weather", "時事", "今天", "最新", "新聞" ,"查詢"
                }
                hit = any(t in content for t in search_triggers)
                self._logger.debug(f"search trigger hit={hit}, content={content}")
                return hit
        
        return False

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