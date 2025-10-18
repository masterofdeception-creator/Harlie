from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
import uuid


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Conversation:
    id: str
    messages: List[Message] = field(default_factory=list)

    def append(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))

    def as_openai_input(self) -> List[dict]:
        return [{"role": message.role, "content": message.content} for message in self.messages]


class ConversationStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, Conversation] = {}

    def get(self, conversation_id: str | None) -> Conversation:
        if conversation_id and conversation_id in self._sessions:
            return self._sessions[conversation_id]
        new_id = conversation_id or str(uuid.uuid4())
        conversation = Conversation(id=new_id)
        self._sessions[new_id] = conversation
        return conversation


store = ConversationStore()
