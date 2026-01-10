# Transport 快速参考

## 组件速览
- Message/Envelope：统一消息载体，调用 `ensure_defaults()` 补齐 id/timestamp 等。
- 入站：`InboundPipeline` + 中间件（校验/默认值/去重） -> `Router`。
- 路由：按 `channel` 分发，可设置默认处理器，支持路由中间件。
- 出站：`OutboundPipeline` + 中间件 -> `SenderRegistry` 调用对应 `Sender`。
- Sink：适配器入口，`handle_event(raw)` -> decoder -> Message -> 入站管道。

## 常用中间件/工具
- 入站：`ValidateRequiredMiddleware`，`NormalizeDefaultsMiddleware`，`InMemoryDeduplicateMiddleware`。
- 出站：`EnsureOutboundDefaultsMiddleware`。
- 辅助：`simple_decoder(channel)` 快速将 dict 事件转为 Message。

## 最小工作流
```python
router = Router()
router.register("console", handler)

inbound = InboundPipeline(router, [ValidateRequiredMiddleware(), NormalizeDefaultsMiddleware()])
registry = SenderRegistry()
registry.register("console", sender)

outbound = OutboundPipeline(registry, [EnsureOutboundDefaultsMiddleware()])

sink = Sink("console", inbound, simple_decoder("console"))
await sink.handle_event({"session_id": "s1", "content": "hi"})
await outbound.send(Message(session_id="s1", channel="console", content="pong"))
```

## 常见错误
- `缺少 session_id，无法路由`：入站消息缺 session_id。
- `缺少 channel，无法路由`：入站消息未指定 channel。
- `不支持的角色`：`role` 不在 MessageRole 枚举内。
- `检测到重复的消息 id`：触发去重中间件。
- `未找到路由处理器`：对应 channel 未注册且无默认处理器。
- `发送失败：未找到频道对应的发送器` / `缺少消息 channel，无法分发`：出站未注册 sender 或缺 channel。

## 日志观察点
- 入站开始/出站开始：debug
- 校验失败/缺字段：error
- 重复消息：warning
- 路由命中/缺失、发送器缺失：debug/error

## 集成提示
- 适配器接入：用 Sink+decoder 适配协议差异；WS/Webhook 事件体可直接映射到 Message 字段。
- 路由中间件：可插入鉴权、节流、审计、A/B 分流。
- 出站中间件：可插入重试、速率限制、格式渲染、监控上报。
