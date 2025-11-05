import httpx
from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from src.a_domain.model.message import Message, MessageRole
from src.a_domain.ports.bussiness.ai_port import AiPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig


class GrokAdapter(AiPort):

    def __init__(self, api_key: str, logger: ILoggingPort, config: AppConfig, model: str):
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            timeout=httpx.Timeout(config.ai_model_connection_timeout),
        )
        self._model = model
        self._logger = logger

    async def generate_reply(self, messages: tuple[Message, ...]) -> Message:
        self._logger.debug(f"Sending {len(messages)} messages to Grok model {self._model}.")
        api_messages = []
        for message in messages:
            if message.role == MessageRole.SYSTEM:
                api_messages.append(ChatCompletionSystemMessageParam(role="system", content=message.content))
            elif message.role == MessageRole.USER:
                api_messages.append(ChatCompletionUserMessageParam(role="user", content=message.content))
            elif message.role == MessageRole.ASSISTANT:
                api_messages.append(
                    ChatCompletionAssistantMessageParam(role="assistant", content=message.content)
                )
        try:
            response = await self._client.chat.completions.create(
                model=self._model, messages=api_messages, temperature=0.7
            )
            choice = response.choices[0]
            reply_content = choice.message.content or ""
            self._logger.info("Successfully received reply from Grok.")
            return Message(role=MessageRole.ASSISTANT, content=reply_content)
        except OpenAIError as e:
            self._logger.error(f"Grok API error: {e}")
            return Message(
                role=MessageRole.ASSISTANT,
                content="I'm sorry, I'm having connection issues at the moment. Please try again soon.",
            )
        except Exception as e:
            self._logger.critical(f"An unexpected error occurred with the Grok adapter: {e}")
            return Message(
                role=MessageRole.ASSISTANT,
                content="I've encountered an unexpected error. The technical team has been notified.",
            )
