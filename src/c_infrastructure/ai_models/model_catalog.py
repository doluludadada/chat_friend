import asyncio

import httpx
from openai import AsyncOpenAI, OpenAIError
from src.a_domain.model.ai_provider import AIModel
from src.a_domain.ports.bussiness.model_catalog_port import ModelCatalogPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.a_domain.types.enums import AiProvider
from src.b_application.configuration.schemas import AppConfig


class ModelsCatalog(ModelCatalogPort):

    def __init__(self, config: AppConfig, logger: ILoggingPort):
        self._config = config
        self._logger = logger
        self._timeout = httpx.Timeout(self._config.ai_model_connection_timeout)

        self._openai_client = (
            AsyncOpenAI(api_key=self._config.openai_api_key, timeout=self._timeout)
            if self._config.openai_api_key
            else None
        )
        self._xai_client = (
            AsyncOpenAI(api_key=self._config.grok_api_key, base_url="https://api.x.ai/v1", timeout=self._timeout)
            if self._config.grok_api_key
            else None
        )

    async def _fetch_openai_models(self) -> tuple[AIModel, ...]:  # [*] MODIFIED return type
        if not self._openai_client:
            self._logger.debug("OpenAI API key not configured. Skipping model fetch.")
            return tuple()
        self._logger.debug("Fetching models from OpenAI...")
        try:
            resp = await self._openai_client.models.list()
            # [*] MODIFIED: Create AIModel objects
            models = tuple(
                AIModel(provider=AiProvider.OPENAI, name=m.id)
                for m in getattr(resp, "data", [])
                if "gpt" in getattr(m, "id", "")
            )
            self._logger.info(f"Found {len(models)} compatible models from OpenAI.")
            return models
        except OpenAIError as e:
            self._logger.error(f"OpenAI API error while listing models: {e}")
            return tuple()
        except Exception as e:
            self._logger.critical(f"Unexpected error fetching OpenAI models: {e}")
            return tuple()

    async def _fetch_grok_models(self) -> tuple[AIModel, ...]:  # [*] MODIFIED return type
        if not self._xai_client:
            self._logger.debug("Grok API key not configured. Skipping model fetch.")
            return tuple()
        self._logger.debug("Fetching models from Grok (X.ai)...")
        try:
            resp = await self._xai_client.models.list()
            # [*] MODIFIED: Create AIModel objects
            models = tuple(
                AIModel(provider=AiProvider.GROK, name=m.id)
                for m in getattr(resp, "data", [])
                if getattr(m, "id", None)
            )
            self._logger.info(f"Found {len(models)} models from Grok (X.ai).")
            return models
        except OpenAIError as e:
            self._logger.error(f"Grok API error while listing models: {e}")
            return tuple()
        except Exception as e:
            self._logger.critical(f"Unexpected error fetching Grok models: {e}")
            return tuple()

    async def list_chat_models(self) -> tuple[AIModel, ...]:
        self._logger.info("Starting to fetch model lists from all configured providers.")
        tasks = []
        if self._openai_client:
            tasks.append(self._fetch_openai_models())
        if self._xai_client:
            tasks.append(self._fetch_grok_models())
        if not tasks:
            self._logger.warning("No AI providers are configured with API keys. Cannot fetch any models.")
            return tuple()
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_models: list[AIModel] = []  # [*] MODIFIED
        for result in results:
            if isinstance(result, Exception):
                self._logger.error(f"A task failed during model fetching: {result}")
            elif isinstance(result, tuple):
                all_models.extend(result)  # [*] MODIFIED

        # Sort by provider, then by name
        sorted_models = sorted(all_models, key=lambda m: (m.provider.value, m.name))
        self._logger.success(f"Total unique models fetched from all providers: {len(sorted_models)}")
        return tuple(sorted_models)
