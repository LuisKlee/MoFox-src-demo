from __future__ import annotations

from collections import OrderedDict
from typing import Any, Awaitable, Callable, Protocol

from kernel.logger import get_logger
from src.core.transport.errors import DuplicateMessageError, ValidationError
from src.core.transport.message import Envelope, Message, MessageDirection, MessageRole
from src.core.transport.router import Router

logger = get_logger(__name__)


class InboundMiddleware(Protocol):
	async def __call__(self, message: Message, call_next: Callable[[Message], Awaitable[Any]]) -> Any:  # pragma: no cover - protocol
		...


class InboundPipeline:
	"""Inbound pipeline: middleware chain -> router."""

	def __init__(self, router: Router, middleware: list[InboundMiddleware] | None = None) -> None:
		self.router = router
		self.middleware: list[InboundMiddleware] = list(middleware) if middleware else []

	async def handle(self, message: Message, envelope: Envelope | None = None) -> Any:
		envelope = envelope or Envelope(message=message, direction=MessageDirection.INBOUND)
		envelope.ensure_defaults()
		logger.debug("入站处理开始: channel=%s, message_id=%s", message.channel, message.id)

		async def call_next(index: int, msg: Message) -> Any:
			if index < len(self.middleware):
				return await self.middleware[index](msg, lambda next_msg: call_next(index + 1, next_msg))
			envelope.message = msg
			return await self.router.route(msg, envelope=envelope)

		return await call_next(0, message)


class ValidateRequiredMiddleware:
	"""Validate required fields and normalize role."""

	async def __call__(self, message: Message, call_next: Callable[[Message], Awaitable[Any]]) -> Any:
		if isinstance(message.role, str):
			try:
				message.role = MessageRole(message.role)
			except ValueError as exc:  # pragma: no cover - defensive
				logger.error("校验失败: 角色无效 role=%s message_id=%s", message.role, message.id)
				raise ValidationError(f"不支持的角色: {message.role}") from exc

		if not message.session_id:
			logger.error("校验失败: 缺少 session_id message_id=%s", message.id)
			raise ValidationError("缺少 session_id，无法路由")
		if not message.channel:
			logger.error("校验失败: 缺少 channel message_id=%s", message.id)
			raise ValidationError("缺少 channel，无法路由")
		return await call_next(message)


class NormalizeDefaultsMiddleware:
	"""Ensure attachments/metadata/timestamps/ids are present."""

	async def __call__(self, message: Message, call_next: Callable[[Message], Awaitable[Any]]) -> Any:
		message.ensure_defaults()
		return await call_next(message)


class InMemoryDeduplicateMiddleware:
	"""Best-effort in-memory deduplication based on message id."""

	def __init__(self, max_size: int = 1024) -> None:
		self._seen: OrderedDict[str, None] = OrderedDict()
		self._max_size = max_size

	async def __call__(self, message: Message, call_next: Callable[[Message], Awaitable[Any]]) -> Any:
		message.ensure_defaults()
		if message.id and message.id in self._seen:
			logger.warning("拒绝重复消息: message_id=%s", message.id)
			raise DuplicateMessageError(f"检测到重复的消息 id: {message.id}")

		if message.id:
			self._seen[message.id] = None
			self._seen.move_to_end(message.id)
			if len(self._seen) > self._max_size:
				self._seen.popitem(last=False)

		return await call_next(message)


__all__ = [
	"InboundMiddleware",
	"InboundPipeline",
	"ValidateRequiredMiddleware",
	"NormalizeDefaultsMiddleware",
	"InMemoryDeduplicateMiddleware",
]
