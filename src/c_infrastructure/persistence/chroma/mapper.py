import json
from dataclasses import asdict
from datetime import datetime
from uuid import UUID
from typing import Any

from src.a_domain.model.conversation import Conversation
from src.a_domain.model.message import Message
from src.a_domain.types.enums import MessageRole
from src.c_infrastructure.persistence.chroma.schema import ChromaMetadataKey

class ConversationMapper:
    
    @staticmethod
    def to_persistence(conversation: Conversation) -> tuple[str, dict[str, Any]]:
        """        """
        metadata: dict[str, Any] = {
            ChromaMetadataKey.UPDATED_AT: conversation.updated_at.isoformat(),
            ChromaMetadataKey.MESSAGE_COUNT: len(conversation.messages),
            ChromaMetadataKey.MODEL_NAME: conversation.selected_model_name or "unknown",
        }

        data = asdict(conversation)

        def _json_serializer(obj):
            if isinstance(obj, (datetime,)):
                return obj.isoformat()
            if isinstance(obj, (UUID,)):
                return str(obj)
            raise TypeError(f"Type {type(obj)} not serializable")

        json_str = json.dumps(data, default=_json_serializer, ensure_ascii=False)
        
        return json_str, metadata

    @staticmethod
    def to_domain(json_str: str) -> Conversation:
        data = json.loads(json_str)

        messages_list = [
            Message(
                id=UUID(msg["id"]),
                role=MessageRole(msg["role"]),
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
            )
            for msg in data.get("messages", [])
        ]

        return Conversation(
            user_id=data["user_id"],
            id=UUID(data["id"]),
            selected_model_name=data.get("selected_model_name"),
            messages=tuple(messages_list),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
