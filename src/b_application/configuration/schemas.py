from __future__ import annotations

from pathlib import Path

from pydantic import computed_field, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.a_domain.types.enums import AiProvider, DatabaseProvider


class AppConfig(BaseSettings):
    """
    Defines the configuration schema required by the application.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )
    project_root: Path

    # -------------------------- AI Model Configuration -------------------------- #

    active_model: AiProvider = Field(description="The AI model currently in use.")
    available_models: dict[AiProvider, str] = Field(
        default_factory=dict,
        description="Mapping of AI provider to concrete model name/id.",
    )
    openai_api_key: str | None = Field(
        default=None, description="API key for OpenAI models."
    )
    grok_api_key: str | None = Field(
        default=None, description="API key for Grok models."
    )
    gemini_api_key: str | None = Field(
        default=None, description="API key for Gemini models."
    )
    groq_api_key: str | None = Field(
        default=None, description="API Key for Groq models."
    )
    ai_model_connection_timeout: int = Field(
        default=60, description="Timeout in seconds for AI model connections."
    )
    ai_system_prompt: str | None = Field(
        default=None, description="The system prompt defining the AI personality."
    )

    # --------------------- Messaging Platform Configuration --------------------- #

    line_channel_id: str | None = Field(
        default=None, description="Access token for the LINE Messaging API."
    )
    line_channel_secret: str | None = Field(
        default=None, description="Secret for LINE Messaging API webhook validation."
    )
    line_channel_access_token: str | None = Field(
        default=None, description="Access token for the LINE Messaging API."
    )

    # --------------------------- Application Behavior --------------------------- #

    log_level: str | int = Field(
        default="INFO",
        description="Logging level for the application (e.g., 'DEBUG', 10).",
    )
    enable_web_search: bool = Field(
        default=False, description="Enable native web search for supported models."
    )
    enable_x_search: bool = Field(
        default=False, description="Enable X (Twitter) search. Only for Grok."
    )
    enable_inline_citations: bool = Field(
        default=True, description="Request inline citations (e.g. [1]) in responses."
    )
    web_search_max_results: int = Field(
        default=2, ge=1, le=5, description="Max sources to retrieve per search."
    )
    web_search_allowed_domains: set[str] | None = Field(default=None)
    web_search_excluded_domains: set[str] | None = Field(default=None)
    x_search_allowed_handles: set[str] | None = Field(default=None)
    x_search_excluded_handles: set[str] | None = Field(default=None)

    # ---------------------------------------------------------------------------- #
    #                                  DB Setting                                  #
    # ---------------------------------------------------------------------------- #
    database_provider: DatabaseProvider = Field(
        default=DatabaseProvider.MEMORY, description="The persistence layer to use."
    )
    chroma_persist_path: str = Field(
        default="chroma_db", description="Path to store ChromaDB data locally."
    )

    reset_commands: set[str] = Field(
        default={"clear"},
        description="List of text commands that trigger a conversation reset.",
    )

    # TODO: Move to somewhere.

    @model_validator(mode="after")
    def _validate_active_model_present(self) -> "AppConfig":
        if self.available_models and self.active_model not in self.available_models:
            raise ValueError(
                f"active_model={self.active_model} is not present in available_models keys: {list(self.available_models)}"
            )
        return self

    @computed_field
    def active_model_name(self) -> str:
        # Convenience accessor for the concrete model id/name of the active provider.

        try:
            return self.available_models[self.active_model]
        except KeyError as exc:
            raise KeyError(
                f"No model mapping for active_model={self.active_model!s}. Please configure available_models."
            ) from exc
