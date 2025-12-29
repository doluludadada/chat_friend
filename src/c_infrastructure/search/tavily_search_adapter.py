from __future__ import annotations

import httpx

from src.a_domain.model.web_search_result import WebSearchResult
from src.a_domain.ports.bussiness.web_search_port import WebSearchPort
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig


class TavilySearchAdapter(WebSearchPort):
    """
    Tavily web search adapter.
    """

    def __init__(self, config: AppConfig, logger: ILoggingPort) -> None:
        self._config = config
        self._logger = logger

        if not self._config.tavily_api_key:
            raise ValueError("Missing tavily_api_key in configuration.")

        timeout = getattr(self._config, "ai_model_connection_timeout", 30)
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))

    async def search(self, query: str, limit: int = 3) -> list[WebSearchResult]:
        payload: dict = {
            "api_key": self._config.tavily_api_key,
            "query": query,
            "max_results": limit,
            "search_depth": self._config.tavily_search_depth,  # "basic" | "advanced"
            "include_answer": False,
            "include_raw_content": False,
        }

        # 可沿用你原本的 domain allow/exclude 設定（你專案已經有 web_search_allowed_domains/excluded_domains 的概念）
        allowed = getattr(self._config, "web_search_allowed_domains", None)
        excluded = getattr(self._config, "web_search_excluded_domains", None)

        if allowed:
            payload["include_domains"] = list(allowed)
        if excluded:
            payload["exclude_domains"] = list(excluded)

        try:
            resp = await self._client.post("https://api.tavily.com/search", json=payload)
            resp.raise_for_status()
            data = resp.json()

            results: list[WebSearchResult] = []
            for item in (data.get("results") or [])[:limit]:
                results.append(
                    WebSearchResult(
                        title=(item.get("title") or "").strip(),
                        url=(item.get("url") or "").strip(),
                        content=(item.get("content") or item.get("snippet") or "").strip(),
                    )
                )
            return results

        except Exception as e:
            self._logger.error(f"[TavilySearchAdapter] search failed: {e}")
            return []
