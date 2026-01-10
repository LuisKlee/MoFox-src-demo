from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from kernel.logger import get_logger
from src.core.transport.message import Message
from src.core.transport.message_receive import InboundPipeline

logger = get_logger(__name__)


class Sink:
	"""Adapter entry that converts raw events into Message objects and feeds inbound pipeline."""

	def __init__(self, name: str, inbound: InboundPipeline, decoder: Callable[[Any], Message]) -> None:
		self.name = name
		self.inbound = inbound
		self.decoder = decoder

	async def handle_event(self, raw_event: Any) -> Any:
		message = self.decoder(raw_event)
		if not message.channel:
			message.channel = self.name
		logger.debug("Sink 接收事件: sink=%s, channel=%s, message_id=%s", self.name, message.channel, message.id)
		return await self.inbound.handle(message)


def simple_decoder(channel: str) -> Callable[[dict[str, Any]], Message]:
	def _to_timestamp(value: Any) -> datetime | None:
		if isinstance(value, datetime):
			return value
		if isinstance(value, str):
			try:
				return datetime.fromisoformat(value)
			except ValueError:
				return None
		return None

	def _decode(payload: dict[str, Any]) -> Message:
		return Message(
			id=payload.get("id"),
			session_id=payload.get("session_id"),
			channel=payload.get("channel", channel),
			role=payload.get("role", "user"),
			content=payload.get("content"),
			attachments=payload.get("attachments"),
			metadata=payload.get("metadata", {}),
			timestamp=_to_timestamp(payload.get("timestamp")),
		)

	return _decode


__all__ = [
	"Sink",
	"simple_decoder",
]
