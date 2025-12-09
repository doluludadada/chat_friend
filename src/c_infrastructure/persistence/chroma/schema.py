from enum import StrEnum

class ChromaCollection(StrEnum):
    CHAT_HISTORY = "chat_history"

class ChromaMetadataKey(StrEnum):
    UPDATED_AT = "updated_at"
    MESSAGE_COUNT = "message_count"
    MODEL_NAME = "model"

class ChromaResultKey(StrEnum):
    DOCUMENTS = "documents"
    METADATAS = "metadatas"
    IDS = "ids"
