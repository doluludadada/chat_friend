from typing import Protocol

class KnowledgeBasePort(Protocol):
    async def search(self, query: str, limit: int = 3) -> str:
        ...
