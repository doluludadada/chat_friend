from __future__ import annotations

from typing import Protocol

from src.a_domain.model.web_search_result import WebSearchResult


class WebSearchPort(Protocol):
    async def search(self, query: str, limit: int = 3) -> list[WebSearchResult]:
        ...
