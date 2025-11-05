from typing import Protocol


class ModelCatalogPort(Protocol):

    async def list_chat_models(self) -> tuple[str, ...]: ...
