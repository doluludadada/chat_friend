from src.a_domain.model.message import Message
from src.a_domain.ports.bussiness.platform_port import PlatformPort
from src.a_domain.ports.notification.logging_port import ILoggingPort


class Dispatcher:
    def __init__(self, platform: PlatformPort, logger: ILoggingPort):
        self._platform = platform
        self._logger = logger

    async def execute(self, user_id: str, messages: tuple[Message, ...]) -> None:
        if not messages:
            self._logger.warning("No messages to dispatch.")
            return

        count = 0
        for msg in messages:
            success = await self._platform.send_message(user_id, msg)
            if success:
                count += 1

        self._logger.success(f"Dispatched {count}/{len(messages)} messages to user_id: {user_id}")
