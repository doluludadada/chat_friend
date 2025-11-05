from typing import Awaitable

from src.a_domain.ports.bussiness.ai_port import AiPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AiModelType, AppConfig
from src.c_infrastructure.ai_models.grok_adapter import GrokAdapter
from src.c_infrastructure.ai_models.openai_adapter import OpenAIAdapter


async def build_ai_adapter(
    config: AppConfig,
    logger: ILoggingPort,
    *,
    override_provider: AiModelType | None = None,
    override_model_id: str | None = None,
) -> AiPort:
    provider = override_provider or config.active_model
    model_id = override_model_id or config.available_models.get(provider)

    if model_id is None:
        raise ValueError(
            f"No model id resolved for provider {provider!s}. "
            f"Configure available_models or enable remote catalogue."
        )

    if provider == AiModelType.OPENAI:
        if not config.openai_api_key:
            raise ValueError("Missing openai_api_key.")
        return OpenAIAdapter(api_key=config.openai_api_key, logger=logger, config=config, model=model_id)

    if provider == AiModelType.GROK:
        if not config.grok_api_key:
            raise ValueError("Missing grok_api_key.")
        return GrokAdapter(api_key=config.grok_api_key, logger=logger, config=config, model=model_id)

    raise ValueError(f"Unsupported provider: {provider!s}")
