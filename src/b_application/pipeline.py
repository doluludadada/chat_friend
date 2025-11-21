from src.a_domain.model.message import Message, MessageRole
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
        dispatcher: Dispatcher
    ):
        self._loader = loader
        self._processor = processor
        self._manager = manager
        self._dispatcher = dispatcher

    async def execute(self, user_id: str, incoming_content: str) -> None:
        conversation = await self._loader.execute(user_id)
        
        user_message = Message(role=MessageRole.USER, content=incoming_content)
        conversation = self._manager.update_state(conversation, [user_message])

        reply_messages = await self._processor.execute(conversation)

        final_conversation = self._manager.update_state(conversation, list(reply_messages))
        await self._manager.save(final_conversation)

        await self._dispatcher.execute(user_id, reply_messages)
