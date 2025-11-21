from src.a_domain.model.conversation import Conversation
from src.a_domain.model.message import Message
from src.a_domain.ports.bussiness.ai_port import AiPort
from src.a_domain.ports.bussiness.chat_styler_port import IChatStylerPort
from src.a_domain.ports.notification.logging_port import ILoggingPort


class AiProcessor:
    def __init__(self, ai_port: AiPort, styler_port: IChatStylerPort, logger: ILoggingPort):
        self._ai_port = ai_port
        self._styler_port = styler_port
        self._logger = logger

    async def execute(self, conversation: Conversation) -> tuple[Message, ...]:
        self._logger.debug("Generating AI reply...")
        try:
            raw_response = await self._ai_port.generate_reply(messages=conversation.messages)
            styled_messages = self._styler_port.format_response(raw_response)
            return styled_messages
        except Exception as e:
            self._logger.error(f"Error during AI processing: {e}")
            return ()
