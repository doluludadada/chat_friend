from enum import StrEnum


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AiProvider(StrEnum):
    OPENAI = "openai"
    GROK = "grok"


class DatabaseProvider(StrEnum):
    MEMORY = "memory"
    CHROMA = "chroma"
