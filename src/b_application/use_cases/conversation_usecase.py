from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from src.a_domain.model.conversation import Conversation
from src.a_domain.model.message import Message, MessageRole
from src.a_domain.ports.bussiness.ai_port import AiPort
from src.a_domain.ports.bussiness.chat_styler_port import IChatStylerPort
from src.a_domain.ports.bussiness.platform_port import PlatformPort
from src.a_domain.ports.bussiness.repository_port import RepositoryPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig


class ConversationUsecase:
    def __init__(
        self,
        ai_port: AiPort,
        repository_port: RepositoryPort,
        platform_port: PlatformPort,
        logging_port: ILoggingPort,
        config: AppConfig,
        styler_port: IChatStylerPort,
    ) -> None:
        self._ai = ai_port
        self._repository = repository_port
        self._platform = platform_port
        self._logger = logging_port
        self._config = config
        self._styler_port = styler_port

    async def execute(self, user_id: str, incoming_content: str) -> Message | None:
        self._logger.trace(f'Use case execution started for user_id: {user_id} with content: "{incoming_content}"')
        try:
            conversation = await self._get_or_create_conversation(user_id)
            user_message = Message(role=MessageRole.USER, content=incoming_content)
            conversation_with_user_msg = self._add_message_to_conversation(conversation, user_message)

            self._logger.debug(f"Generating AI reply for user_id: {user_id}")
            raw_ai_response = await self._ai.generate_reply(messages=conversation_with_user_msg.messages)

            self._logger.debug("Styling AI response for chat platform.")
            styled_messages = self._styler_port.format_response(raw_ai_response)

            final_conversation = conversation_with_user_msg
            for msg in styled_messages:
                final_conversation = self._add_message_to_conversation(final_conversation, msg)

            await self._repository.save(final_conversation)
            self._logger.debug(f"Conversation saved for user_id: {user_id}")

            for msg_to_send in styled_messages:
                await self._platform.send_message(user_id, msg_to_send)

            self._logger.success(
                f"Successfully processed and sent {len(styled_messages)} reply messages to user_id: {user_id}"
            )

            return styled_messages[-1] if styled_messages else None

        except Exception as e:
            self._logger.error(f"An error occurred while handling message for user {user_id}: {e}")
            return None

    async def _get_or_create_conversation(self, user_id: str) -> Conversation:
        """Fetches a conversation or creates a new one if it doesn't exist."""
        conversation = await self._repository.get_conversation_by_user_id(user_id)
        if conversation:
            self._logger.debug(f"Found existing conversation for user_id: {user_id}")
            return conversation
        self._logger.info(f"No existing conversation found. Creating new one for user_id: {user_id}")

        initial_messages = []
        if self._config.ai_system_prompt:
            self._logger.info("Applying system prompt to new conversation.")
            system_message = Message(role=MessageRole.SYSTEM, content=self._config.ai_system_prompt)
            initial_messages.append(system_message)
        return Conversation(user_id=user_id, messages=tuple(initial_messages))

    def _add_message_to_conversation(self, conversation: Conversation, message: Message) -> Conversation:
        """
        Adds a new message to a conversation, returning a new Conversation instance.
        """
        new_messages = conversation.messages + (message,)
        return replace(conversation, messages=new_messages, updated_at=datetime.now(timezone.utc))
