import httpx
from openai import AsyncOpenAI, OpenAIError
from src.a_domain.ports.bussiness.model_catalog_port import ModelCatalogPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig


class ModelsCatalog(ModelCatalogPort):
    def __init__(self, api_key: str, logger: ILoggingPort, config: AppConfig):
        self._openai_client = AsyncOpenAI(
            api_key=api_key, timeout=httpx.Timeout(config.ai_model_connection_timeout)
        )
        self._xai_client = AsyncOpenAI(
            api_key=api_key, timeout=httpx.Timeout(config.ai_model_connection_timeout)
        )
        self._logger = logger

    async def list_chat_models(self) -> tuple[str, ...]:
        try:
            self._logger.debug("Fetching model list...")
            resp = await self._openai_client.models.list()
            ids = tuple(m.id for m in getattr(resp, "data", []) if getattr(m, "id", None))
            self._logger.info(f"Found {len(ids)} Grok models.")
            return ids
        except OpenAIError as e:
            self._logger.error(f"model listing error: {e}")
            return tuple()
        except Exception as e:
            self._logger.critical(f"Unexpected error fetching Grok models: {e}")
            return tuple()
