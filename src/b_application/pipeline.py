from src.a_domain.model.message import Message, MessageRole
from src.b_application.configuration.schemas import AppConfig
from src.b_application.use_cases.collect.context_loader import ContextLoader
from src.b_application.use_cases.process.ai_processor import AiProcessor
from src.b_application.use_cases.ship.dispatcher import Dispatcher
from src.b_application.use_cases.ship.state_manager import StateManager


class Pipeline:
    def __init__(
        self,
        loader: ContextLoader,
        processor: AiProcessor,
        manager: StateManager,
        dispatcher: Dispatcher,
        config: AppConfig,
    ):
        self._loader = loader
        self._processor = processor
        self._manager = manager
        self._dispatcher = dispatcher
        self._config = config

    async def execute(self, user_id: str, incoming_content: str) -> None:
        conversation = await self._loader.execute(user_id)

        if incoming_content.strip() in self._config.reset_commands:
            await self._manager.reset_conversation(conversation)
            system_reply = Message(role=MessageRole.ASSISTANT, content="✨ 記憶已清除！我們重新開始吧。")
            await self._dispatcher.execute(user_id, (system_reply,))
            return

        user_message = Message(role=MessageRole.USER, content=incoming_content)
        conversation = self._manager.update_state(conversation, [user_message])

        reply_messages = await self._processor.execute(conversation)

        final_conversation = self._manager.update_state(conversation, list(reply_messages))
        await self._manager.save(final_conversation)

        await self._dispatcher.execute(user_id, reply_messages)
