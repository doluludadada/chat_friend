from src.a_domain.ports.bussiness.ai_port import AiPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AiModelType, AppConfig
from src.c_infrastructure.ai_models.ai_adapter.grok_adapter import GrokAdapter
from src.c_infrastructure.ai_models.ai_adapter.openai_adapter import OpenAIAdapter


class AiAdapterFactory:
    """
    Factory class responsible for creating AI model adapter instances based on configuration.
    """

    def __init__(self, config: AppConfig, logger: ILoggingPort):
        self._config = config
        self._logger = logger
        self._logger.trace(f"AI Adapter Factory initialised. Active model provider: {self._config.active_model.value}")

    def create_adapter(
        self, *, override_provider: AiModelType | None = None, override_model_name: str | None = None
    ) -> AiPort:
        provider = override_provider or self._config.active_model
        model_name = override_model_name or self._config.available_models.get(provider)

        if model_name is None:
            raise ValueError(
                f"No model id resolved for provider {provider!s}. "
                "Configure available_models or enable remote catalogue."
            )

        self._logger.debug(f"Creating AI adapter for provider: {provider.value} with model: {model_name}")

        if provider == AiModelType.OPENAI:
            return OpenAIAdapter(
                config=self._config,
                logger=self._logger,
                model_name=model_name,
            )

        if provider == AiModelType.GROK:
            return GrokAdapter(
                config=self._config,
                logger=self._logger,
                model_name=model_name,
            )

        raise ValueError(f"Unsupported provider: {provider!s}")
