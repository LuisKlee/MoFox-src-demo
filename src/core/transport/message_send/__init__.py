from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Protocol

from kernel.logger import get_logger
from src.core.transport.errors import SenderNotFoundError
from src.core.transport.message import Envelope, Message, MessageDirection

logger = get_logger(__name__)


@dataclass
class SendResult:
	success: bool
	detail: str | None = None
	metadata: dict[str, Any] = field(default_factory=dict)


class Sender(Protocol):
	async def __call__(self, envelope: Envelope) -> SendResult:  # pragma: no cover - protocol
		...


class OutboundMiddleware(Protocol):
	async def __call__(
		self, envelope: Envelope, call_next: Callable[[Envelope], Awaitable[SendResult]]
	) -> SendResult:  # pragma: no cover - protocol
		...


class SenderRegistry:
	def __init__(self) -> None:
		self._senders: dict[str, Sender] = {}

	def register(self, channel: str, sender: Sender) -> None:
		self._senders[channel] = sender

	def unregister(self, channel: str) -> None:
		self._senders.pop(channel, None)

	async def dispatch(self, envelope: Envelope) -> SendResult:
		channel = envelope.message.channel
		if not channel:
			logger.error("发送失败: 缺少 channel message_id=%s", envelope.message.id)
			raise SenderNotFoundError("发送失败：缺少消息 channel，无法分发")
		sender = self._senders.get(channel)
		if sender is None:
			logger.error("发送失败: 未注册发送器 channel=%s message_id=%s", channel, envelope.message.id)
			raise SenderNotFoundError(f"发送失败：未找到频道对应的发送器，channel='{channel}'")
		return await sender(envelope)


class OutboundPipeline:
	"""Outbound pipeline: middleware chain -> sender registry."""

	def __init__(self, registry: SenderRegistry, middleware: list[OutboundMiddleware] | None = None) -> None:
		self.registry = registry
		self.middleware: list[OutboundMiddleware] = list(middleware) if middleware else []

	async def send(self, message: Message, envelope: Envelope | None = None) -> SendResult:
		envelope = envelope or Envelope(message=message, direction=MessageDirection.OUTBOUND)
		envelope.ensure_defaults()
		logger.debug("出站发送开始: channel=%s, message_id=%s", envelope.message.channel, envelope.message.id)

		async def call_next(index: int, env: Envelope) -> SendResult:
			if index < len(self.middleware):
				return await self.middleware[index](env, lambda next_env: call_next(index + 1, next_env))
			return await self.registry.dispatch(env)

		return await call_next(0, envelope)


class EnsureOutboundDefaultsMiddleware:
	"""Ensure outbound envelope has defaults before sending."""

	async def __call__(self, envelope: Envelope, call_next: Callable[[Envelope], Awaitable[SendResult]]) -> SendResult:
		envelope.ensure_defaults()
		if envelope.direction != MessageDirection.OUTBOUND:
			envelope.direction = MessageDirection.OUTBOUND
		return await call_next(envelope)


__all__ = [
	"SendResult",
	"Sender",
	"OutboundMiddleware",
	"SenderRegistry",
	"OutboundPipeline",
	"EnsureOutboundDefaultsMiddleware",
]
