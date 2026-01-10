from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MessageDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Message:
    id: str | None = None
    session_id: str | None = None
    channel: str | None = None
    role: MessageRole = MessageRole.USER
    content: str | None = None
    attachments: list[Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime | None = None

    def ensure_defaults(self) -> None:
        if not self.id:
            self.id = str(uuid4())
        if not self.timestamp:
            self.timestamp = utc_now()
        if self.attachments is None:
            self.attachments = []
        if self.metadata is None:
            self.metadata = {}

    def to_payload(self) -> dict[str, Any]:
        self.ensure_defaults()
        return {
            "id": self.id,
            "session_id": self.session_id,
            "channel": self.channel,
            "role": self.role.value,
            "content": self.content,
            "attachments": self.attachments,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class Envelope:
    message: Message
    direction: MessageDirection
    trace_id: str | None = None
    tenant_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def ensure_defaults(self) -> None:
        self.message.ensure_defaults()
        if self.extra is None:
            self.extra = {}
