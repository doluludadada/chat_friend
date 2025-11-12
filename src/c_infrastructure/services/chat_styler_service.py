import re

from src.a_domain.model.message import Message, MessageRole
from src.a_domain.ports.bussiness.chat_styler_port import IChatStylerPort


class ChatStylerService(IChatStylerPort):
    _MAX_MESSAGE_LENGTH = 400
    _SPLIT_DELIMITERS = r"\n\n+"

    def format_response(self, message: Message) -> tuple[Message, ...]:
        content = self._remove_markdown(message.content)

        raw_chunks = re.split(self._SPLIT_DELIMITERS, content)

        final_messages = []
        for chunk in raw_chunks:
            trimmed_chunk = chunk.strip()
            if not trimmed_chunk:
                continue

            if len(trimmed_chunk) > self._MAX_MESSAGE_LENGTH:
                final_messages.extend(self._force_split_long_text(trimmed_chunk))
            else:
                final_messages.append(Message(role=MessageRole.ASSISTANT, content=trimmed_chunk))

        if not final_messages:
            return (Message(role=MessageRole.ASSISTANT, content="Could you ask me again?🤔"),)

        return tuple(final_messages)

    def _remove_markdown(self, text: str) -> str:
        text = re.sub(r"\*\*(.*?)\*\*|\*(.*?)\*", r"\1\2", text)
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        return text.strip()

    def _force_split_long_text(self, text: str) -> list[Message]:
        parts = []
        while len(text) > self._MAX_MESSAGE_LENGTH:
            split_at = text.rfind("。", 0, self._MAX_MESSAGE_LENGTH)
            if split_at == -1:
                split_at = self._MAX_MESSAGE_LENGTH

            parts.append(Message(role=MessageRole.ASSISTANT, content=text[: split_at + 1].strip()))
            text = text[split_at + 1 :].strip()

        if text:
            parts.append(Message(role=MessageRole.ASSISTANT, content=text))

        return parts
