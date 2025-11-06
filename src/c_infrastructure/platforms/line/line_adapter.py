# ***********************************************************************
#  Author:        Shiou
#  Created:       2025-11-06
#  Description:   Description of the file
#  Location:      src\c_infrastructure\platforms\line\line_adapter.py
# ***********************************************************************
import httpx
from src.a_domain.model.message import Message
from src.a_domain.ports.bussiness.platform_port import PlatformPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig
from src.c_infrastructure.platforms.line.line_constants import PUSH_MESSAGE_URL


class LinePlatformAdapter(PlatformPort):
    def __init__(self, config: AppConfig, logger: ILoggingPort):
        if not config.line_channel_access_token:
            raise ValueError("Missing line_channel_access_token in configuration. Cannot send messages.")

        self._channel_access_token = config.line_channel_access_token
        self._timeout = config.ai_model_connection_timeout
        self._logger = logger
        self._base_url = PUSH_MESSAGE_URL

    async def send_message(self, user_id: str, message: Message) -> bool:

        headers = {
            "Authorization": f"Bearer {self._channel_access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "to": user_id,
            "messages": [
                {"type": "text", "text": message.content},
            ],
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                self._logger.debug(f"Sending LINE message to user_id: {user_id}")
                resp = await client.post(self._base_url, headers=headers, json=payload)

                if 200 <= resp.status_code < 300:
                    self._logger.success(f"Successfully sent LINE message to user_id: {user_id}.")
                    return True
                else:
                    self._logger.error(
                        f"Failed to send LINE message to user_id: {user_id}. "
                        f"Status: {resp.status_code}, Response: {resp.text}"
                    )
                    return False
            except httpx.RequestError as e:
                self._logger.error(f"An HTTP error occurred while sending message to LINE for user {user_id}: {e}")
                return False
            except Exception as e:
                self._logger.critical(
                    f"An unexpected error occurred during LINE message sending for user {user_id}: {e}"
                )
                return False
