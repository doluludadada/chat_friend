import httpx
from src.a_domain.model.message import Message
from src.a_domain.ports.bussiness.platform_port import PlatformPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig


class LinePlatformAdapter(PlatformPort):
    def __init__(self, config: AppConfig, logger: ILoggingPort):
        if not config.line_channel_id:
            raise ValueError("Missing line_channel_access_token.")
        self._channel_id = config.line_channel_id
        self._timeout = config.ai_model_connection_timeout
        self._logger = logger
        self._base_url = "https://api.line.me/v2/bot/message/push"

    async def send_message(self, user_id: str, message: Message) -> bool:
        is_success: bool = True

        headers = {
            "Authorization": f"Bearer {self._channel_id}",
            "Content-Type": "application/json",
        }

        payload = {
            "to": user_id,
            "messages": [{"type": "text", "text": message.content}],
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                resp = await client.post(self._base_url, headers=headers, json=payload)
                if 200 <= resp.status_code < 300:
                    self._logger.info(f"LINE message sent to {user_id}.")
                    return is_success
                self._logger.error(f"LINE send failed ({resp.status_code}): {resp.text}")
                is_success = False
                return is_success
            except Exception as e:
                self._logger.error(f"LINE send exception: {e}")
                is_success = False
                return is_success
