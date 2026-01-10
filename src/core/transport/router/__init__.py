from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Protocol

from kernel.logger import get_logger
from src.core.transport.errors import RoutingError
from src.core.transport.message import Envelope, Message

logger = get_logger(__name__)


class RouteHandler(Protocol):
	async def __call__(self, context: "RoutingContext") -> Any:  # pragma: no cover - protocol
		...


class RouteMiddleware(Protocol):
	async def __call__(
		self, context: "RoutingContext", call_next: Callable[["RoutingContext"], Awaitable[Any]]
	) -> Any:  # pragma: no cover - protocol
		...


@dataclass
class RoutingContext:
	message: Message
	envelope: Envelope | None = None
	attributes: dict[str, Any] = field(default_factory=dict)

	def with_attribute(self, key: str, value: Any) -> "RoutingContext":
		self.attributes[key] = value
		return self


class Router:
	"""Lightweight router with middleware chain and channel-based handlers."""

	def __init__(self, middleware: list[RouteMiddleware] | None = None) -> None:
		self._handlers: dict[str, RouteHandler] = {}
		self._default_handler: RouteHandler | None = None
		self._middleware: list[RouteMiddleware] = list(middleware) if middleware else []

	def use(self, middleware: RouteMiddleware) -> None:
		self._middleware.append(middleware)

	def register(self, channel: str, handler: RouteHandler) -> None:
		self._handlers[channel] = handler

	def set_default(self, handler: RouteHandler) -> None:
		self._default_handler = handler

	async def route(self, message: Message, envelope: Envelope | None = None) -> Any:
		message.ensure_defaults()
		context = RoutingContext(message=message, envelope=envelope)
		logger.debug("路由开始: channel=%s, message_id=%s", message.channel, message.id)

		async def call_next(index: int, ctx: RoutingContext) -> Any:
			if index < len(self._middleware):
				return await self._middleware[index](ctx, lambda next_ctx: call_next(index + 1, next_ctx))

			handler = self._handlers.get(ctx.message.channel or "")
			if handler is None:
				handler = self._default_handler
			if handler is None:
				logger.error("路由失败: 未找到处理器 channel=%s message_id=%s", ctx.message.channel, ctx.message.id)
				raise RoutingError(f"未找到路由处理器，channel='{ctx.message.channel}'")
			logger.debug("路由命中处理器: channel=%s, handler=%s", ctx.message.channel, getattr(handler, "__name__", handler.__class__.__name__))
			return await handler(ctx)

		return await call_next(0, context)


__all__ = [
	"RouteHandler",
	"RouteMiddleware",
	"RoutingContext",
	"Router",
]
