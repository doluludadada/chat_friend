from typing import Protocol

from src.a_domain.model.ai_provider import AIModel


class ModelCatalogPort(Protocol):

    async def list_chat_models(self) -> tuple[AIModel, ...]: ...
