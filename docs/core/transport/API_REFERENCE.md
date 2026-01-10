# Transport 模块 API 参考

> 覆盖当前已实现的核心接口：数据模型、入站/出站管道、路由、Sink、错误类型。

## 数据模型
- `Message`（src/core/transport/message.py）
  - 字段：`id` | `session_id` | `channel` | `role`(`MessageRole`) | `content` | `attachments` | `metadata` | `timestamp`
  - 方法：`ensure_defaults()` 补齐 id/timestamp/attachments/metadata；`to_payload()` 返回序列化字典
- `Envelope`
  - 字段：`message` | `direction`(`MessageDirection`) | `trace_id` | `tenant_id` | `extra`
  - 方法：`ensure_defaults()`：传递给 message 确保默认值

## 错误类型（src/core/transport/errors.py）
- `TransportError`：基类
- `ValidationError`：入站校验失败（缺字段/角色非法）
- `DuplicateMessageError`：入站重复消息
- `RoutingError`：路由未命中或处理失败
- `SenderNotFoundError`：出站未注册发送器或缺少 channel

## 入站管道（message_receive）
- 协议 `InboundMiddleware`: `(message, call_next) -> Awaitable`
- `InboundPipeline(router, middleware=[])`
  - `handle(message, envelope=None)`：依次执行中间件，最终调用 router.route
- 内置中间件
  - `ValidateRequiredMiddleware`：角色合法性 + `session_id`、`channel` 必填
  - `NormalizeDefaultsMiddleware`：补齐 id/timestamp/attachments/metadata
  - `InMemoryDeduplicateMiddleware(max_size=1024)`：基于 message.id 的 LRU 去重

## 路由（router）
- 协议 `RouteHandler(RoutingContext) -> Awaitable`
- 协议 `RouteMiddleware(context, call_next) -> Awaitable`
- `Router(middleware=[])`
  - `use(middleware)`：追加路由中间件
  - `register(channel, handler)`：按 channel 注册处理器
  - `set_default(handler)`：未命中时使用默认处理器
  - `route(message, envelope=None)`：执行中间件链并调用对应处理器
- `RoutingContext`：包含 `message`、`envelope`、`attributes`，可通过 `with_attribute` 传递信息

## 出站管道（message_send）
- 协议 `Sender(envelope) -> Awaitable[SendResult]`
- 协议 `OutboundMiddleware(envelope, call_next) -> Awaitable[SendResult]`
- `SendResult(success: bool, detail: str | None, metadata: dict)`
- `SenderRegistry`
  - `register(channel, sender)` / `unregister(channel)`
  - `dispatch(envelope)`：按 channel 调用对应 sender
- `OutboundPipeline(registry, middleware=[])`
  - `send(message, envelope=None)`：执行中间件链后调用 registry.dispatch
- 内置中间件：`EnsureOutboundDefaultsMiddleware`

## Sink（sink）
- `Sink(name, inbound_pipeline, decoder)`
  - `handle_event(raw_event)`：使用 decoder 转换 raw_event->Message，补 channel，送入 inbound
- `simple_decoder(channel)`：返回 dict->Message 的简单解码器，支持 ISO 时间解析

## 日志
- 已接入 `kernel.logger.get_logger`：
  - 入站开始、出站开始、Sink 接收、路由命中/缺失、校验失败、重复拒绝、发送器缺失等都会记录 debug/error/warning。

## 使用示例（简版）
```python
from src.core.transport import (
    Message, Router, InboundPipeline, OutboundPipeline, SenderRegistry,
    ValidateRequiredMiddleware, NormalizeDefaultsMiddleware, InMemoryDeduplicateMiddleware,
    EnsureOutboundDefaultsMiddleware, Sink, simple_decoder, SendResult
)

router = Router()

@router.register("console")
async def console_handler(ctx):
    print("recv", ctx.message.to_payload())
    return "ok"

inbound = InboundPipeline(
    router,
    middleware=[InMemoryDeduplicateMiddleware(), ValidateRequiredMiddleware(), NormalizeDefaultsMiddleware()]
)

registry = SenderRegistry()

@registry.register("console")
async def console_sender(envelope):
    print("send", envelope.message.to_payload())
    return SendResult(success=True)

outbound = OutboundPipeline(registry, middleware=[EnsureOutboundDefaultsMiddleware()])

sink = Sink("console", inbound, simple_decoder("console"))
await sink.handle_event({"session_id": "s1", "content": "hi"})
await outbound.send(Message(session_id="s1", channel="console", content="pong"))
```
