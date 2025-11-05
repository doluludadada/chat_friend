from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from src.a_domain.model.conversation import Conversation
from src.a_domain.model.message import Message, MessageRole
from src.a_domain.ports.bussiness.ai_port import AiPort
from src.a_domain.ports.bussiness.platform_port import PlatformPort
from src.a_domain.ports.bussiness.repository_port import RepositoryPort
from src.a_domain.ports.notification.logging_port import ILoggingPort


class ConversationUsecase:
    def __init__(
        self,
        ai_port: AiPort,
        repository_port: RepositoryPort,
        platform_port: PlatformPort,
        logging_port: ILoggingPort,
    ) -> None:
        self._ai_port = ai_port
        self._repository_port = repository_port
        self._platform_port = platform_port
        self._logger = logging_port

    async def execute(self, user_id: str, incoming_content: str) -> Message | None:
        self._logger.info(f"Starting to handle new message for user_id: {user_id}")

        try:
            # 1. Get existing conversation or create a new one
            conversation = await self._get_or_create_conversation(user_id)

            # 2. Create a new message for the user's input and add it to the conversation
            user_message = Message(role=MessageRole.USER, content=incoming_content)

            conversation_with_user_msg = self._add_message_to_conversation(conversation, user_message)

            # 3. Generate a reply using the AI port
            self._logger.debug(f"Generating AI reply for user_id: {user_id}")
            assistant_message = await self._ai_port.generate_reply(
                messages=conversation_with_user_msg.messages
            )

            # 4. Add the assistant's reply to the conversation
            final_conversation = self._add_message_to_conversation(
                conversation_with_user_msg, assistant_message
            )

            # 5. Save the final state of the conversation
            await self._repository_port.save(final_conversation)
            self._logger.debug(f"Conversation saved for user_id: {user_id}")

            # 6. Send the reply back to the user via the platform port
            await self._platform_port.send_message(user_id, assistant_message)
            self._logger.info(f"Reply sent successfully to user_id: {user_id}")

            return assistant_message

        except Exception as e:
            self._logger.error(f"An error occurred while handling message for user {user_id}: {e}")
            return None

    async def _get_or_create_conversation(self, user_id: str) -> Conversation:
        """Fetches a conversation or creates a new one if it doesn't exist."""
        conversation = await self._repository_port.get_conversation_by_user_id(user_id)
        if conversation:
            self._logger.debug(f"Found existing conversation for user_id: {user_id}")
            return conversation

        self._logger.info(f"No existing conversation found. Creating new one for user_id: {user_id}")
        return Conversation(user_id=user_id)

    def _add_message_to_conversation(self, conversation: Conversation, message: Message) -> Conversation:
        """
        Adds a new message to a conversation, returning a new Conversation instance.
        """
        new_messages = conversation.messages + (message,)
        return replace(conversation, messages=new_messages, updated_at=datetime.now(timezone.utc))
