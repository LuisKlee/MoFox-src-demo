# Transport 最佳实践

## 设计原则
- **单一职责**：Sink 只做协议解码，入站中间件做验证/去重，Router 只做分发，Sender 只做发送。
- **中间件链**：把鉴权、节流、审计、监控拆成中间件，保持核心逻辑简洁。
- **显式 channel**：始终设置 `channel`；注册 sender/handler 时与 channel 保持一一对应。
- **幂等性**：利用 `InMemoryDeduplicateMiddleware` 或外部存储防重，确保上游重试不会重复执行。

## 校验与防护
- 入站务必挂载 `ValidateRequiredMiddleware`；对外部事件源建议再加签名校验中间件。
- 为避免雪崩，路由中间件可添加速率限制或熔断；出站可添加重试/退避且限制最大尝试次数。
- 在多租户场景，将 `tenant_id` 放入 Envelope.extra/metadata 并在路由或中间件中校验。

## 日志与观测
- 已内置关键节点日志；在自定义中间件/handler/sender 中补充 trace_id/tenant_id，使用 `metadata` 透传。
- 发送/路由失败需记录上下文（channel、session_id、message_id），避免输出敏感 content。

## 路由策略
- 设定默认处理器以兜底未注册 channel；在 handler 内根据 `session_id` 或 `attributes` 做二级分发。
- 将路由中间件用作“前置过滤器”（鉴权/AB/审计），避免在 handler 内重复实现。

## 出站策略
- Sender 应处理具体协议序列化（文本/卡片/多模态），失败时返回 `SendResult(success=False, detail=...)`。
- 对慢链路（如远端 API）可在出站中间件添加超时与重试，避免阻塞主流程。

## Sink 接入模式
- Webhook：decoder 做签名校验 + 事件体映射 -> Message。
- WebSocket/长连接：decoder 处理连接上下文（连接 id/用户 id），并把 session_id 绑定到连接。
- MQ/队列：decoder 从消息头提取 trace/tenant，利用去重中间件避免重复消费。

## 测试建议
- 针对校验、去重、路由未命中、发送器缺失编写单测。
- 用假 sender/fake handler 验证中间件链顺序和异常传播。
- 对日志可使用捕获 handler 验证关键错误信息被记录。
