from __future__ import annotations
import asyncio
from functools import cached_property
from typing import Any
import google.generativeai as genai  # type: ignore[import-untyped]
from google.api_core.client_options import ClientOptions
from src.a_domain.model.message import Message, MessageRole
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig
from src.c_infrastructure.ai_models.base import BaseAIAdapter


class GeminiAIAdapter(BaseAIAdapter):
    def __init__(
        self, config: AppConfig, logger: ILoggingPort, model_name: str
    ) -> None:
        super().__init__(config, logger, model_name)
        if not self._config.gemini_api_key:
            raise ValueError("Missing gemini_api_key in configuration.")
        genai.configure(api_key=self._config.gemini_api_key)  # type: ignore[attr-defined]
        endpoint = getattr(self._config, "gemini_endpoint", None)
        if endpoint:
            try:
                genai.configure(client_options=ClientOptions(api_endpoint=endpoint))  # type: ignore[attr-defined]
            except Exception:
                try:
                    genai.configure(client_options={"api_endpoint": endpoint})  # type: ignore[attr-defined]
                except Exception:
                    self._logger.debug(
                        "[GeminiAIAdapter] genai.configure with custom endpoint not supported by installed library version"
                    )

    @cached_property
    def _client(self) -> Any:
        self._logger.debug(
            f"[{self.__class__.__name__}] Creating GenerativeModel for: {self._model_name}"
        )
        return genai.GenerativeModel(self._model_name)  # type: ignore[attr-defined]

    async def _call_api(self, messages: tuple[Message, ...]) -> str:
        prompt = self._convert_to_prompt(messages)
        self._logger.debug(
            f"[{self.__class__.__name__}] Calling Gemini, prompt length={len(prompt)}"
        )
        try:
            response = await asyncio.to_thread(
                lambda: self._client.generate_content(
                    prompt, generation_config={"temperature": 0.7}
                )
            )
        except Exception as e:
            self._logger.error(
                f"[{self.__class__.__name__}] Gemini API call failed: {e}"
            )
            raise
        text = self._extract_text_from_response(response)
        return text

    def _convert_to_prompt(self, messages: tuple[Message, ...]) -> str:
        lines: list[str] = []
        for m in messages:
            if m.role == MessageRole.SYSTEM:
                prefix = "[system]"
            elif m.role == MessageRole.USER:
                prefix = "[user]"
            else:
                prefix = "[assistant]"
            lines.append(f"{prefix} {m.content}")
        return "\n".join(lines)

    def _extract_text_from_response(self, resp: Any) -> str:
        try:
            text = getattr(resp, "text", None)
            if isinstance(text, str) and text.strip():
                return text
            candidates = getattr(resp, "candidates", None)
            if candidates:
                first = candidates[0]
                content = getattr(first, "content", None) or getattr(
                    first, "output", None
                )
                if content is not None:
                    parts = getattr(content, "parts", None)
                    if parts:
                        texts: list[str] = []
                        for part in parts:
                            part_text = getattr(part, "text", None)
                            if isinstance(part_text, str) and part_text.strip():
                                texts.append(part_text)
                        if texts:
                            return "\n".join(texts)
            if isinstance(resp, dict):
                t = resp.get("text")
                if isinstance(t, str) and t.strip():
                    return t
                out = resp.get("output")
                if isinstance(out, str) and out.strip():
                    return out
            return str(resp)
        except Exception as e:
            self._logger.error(
                f"[{self.__class__.__name__}] Failed to parse Gemini response, falling back to str(resp): {e}"
            )
            return str(resp)
