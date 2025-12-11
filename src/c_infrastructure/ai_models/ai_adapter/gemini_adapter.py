from __future__ import annotations

import asyncio
from functools import cached_property
from typing import Any, List, Tuple

import google.generativeai as genai
from google.api_core.client_options import ClientOptions

from src.a_domain.model.message import Message, MessageRole
from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig
from src.c_infrastructure.ai_models.base import BaseAIAdapter


class GeminiAIAdapter(BaseAIAdapter):
    """
    Infrastructure 層的 Gemini 實作，
    負責把 Domain 的 Message 轉成 Gemini 的輸入、呼叫 API、再把結果轉回純文字。
    """

    def __init__(self, config: AppConfig, logger: ILoggingPort, model_name: str) -> None:
        super().__init__(config, logger, model_name)

        if not self._config.gemini_api_key:
            raise ValueError("Missing gemini_api_key in configuration.")

        # 基本設定
        genai.configure(api_key=self._config.gemini_api_key)

        # 如有自訂 endpoint（例如企業 proxy / gateway）
        endpoint = getattr(self._config, "gemini_endpoint", None)
        if endpoint:
            try:
                genai.configure(client_options=ClientOptions(api_endpoint=endpoint))
            except Exception:
                try:
                    # 部分版本接受 dict 作為 client_options
                    genai.configure(client_options={"api_endpoint": endpoint})
                except Exception:
                    # 若上述方式皆不支援，記錄 debug 並繼續（只使用 api_key）
                    self._logger.debug(
                        "[GeminiAIAdapter] genai.configure with custom endpoint not supported by installed library version"
                    )

    @cached_property
    def _client(self) -> Any:
        """
        懶建立 Gemini GenerativeModel client。
        注意：這裡回傳型別用 Any，避免 stub 版本差異造成 type checker 噴錯。
        """
        self._logger.debug(
            f"[{self.__class__.__name__}] Creating GenerativeModel for: {self._model_name}"
        )
        return genai.GenerativeModel(self._model_name)

    async def _call_api(self, messages: Tuple[Message, ...]) -> str:
        """
        實作 BaseAIAdapter 的抽象方法。
        - 負責把 Domain messages -> prompt
        - 呼叫 Gemini API
        - 把 response 轉成純文字
        """
        prompt = self._convert_to_prompt(messages)
        self._logger.debug(
            f"[{self.__class__.__name__}] Calling Gemini, prompt length={len(prompt)}"
        )

        try:
            # Gemini SDK 是同步的，用 asyncio.to_thread 讓外層仍然是 async
            response = await asyncio.to_thread(
                lambda: self._client.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                    },
                )
            )
        except Exception:
            # 這裡只記錄 log，然後 re-raise，讓 BaseAIAdapter 統一處理對使用者的錯誤訊息
            self._logger.error(
                f"[{self.__class__.__name__}] Gemini API call failed",
                exc_info=True,
            )
            raise

        text = self._extract_text_from_response(response)
        return text

    # -------------------------------------------------------------------------
    # internal helpers
    # -------------------------------------------------------------------------
    def _convert_to_prompt(self, messages: Tuple[Message, ...]) -> str:
        """
        將 Domain 的 Message 序列轉成一段文字 prompt。
        目前是簡單在前面加上角色標籤，你可以依照需求再調整格式。
        """
        lines: List[str] = []
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
        """
        從 Gemini 的 response 物件中抽取出最終文字。
        主要支援新版 google.generativeai GenerativeModel 的結構：
        - resp.text
        - resp.candidates[0].content.parts[].text
        """
        try:
            # 1. 新版 SDK 最常用的就是 resp.text
            text = getattr(resp, "text", None)
            if isinstance(text, str) and text.strip():
                return text

            # 2. 從 candidates → content.parts[].text 抽文字
            candidates = getattr(resp, "candidates", None)
            if candidates:
                first = candidates[0]
                content = getattr(first, "content", None) or getattr(first, "output", None)
                if content is not None:
                    parts = getattr(content, "parts", None)
                    if parts:
                        texts: List[str] = []
                        for part in parts:
                            part_text = getattr(part, "text", None)
                            if isinstance(part_text, str) and part_text.strip():
                                texts.append(part_text)
                        if texts:
                            return "\n".join(texts)

            # 3. dict 形式的 fallback（較不常見，但保留以防之後 SDK 變形）
            if isinstance(resp, dict):
                t = resp.get("text")
                if isinstance(t, str) and t.strip():
                    return t
                out = resp.get("output")
                if isinstance(out, str) and out.strip():
                    return out

            # 4. 最後兜底：直接轉字串（方便 debug）
            return str(resp)

        except Exception:
            # 解析不到內容也不再往外丟 exception，免得蓋掉上層的錯誤處理邏輯
            self._logger.error(
                f"[{self.__class__.__name__}] Failed to parse Gemini response, falling back to str(resp)",
                exc_info=True,
            )
            return str(resp)
