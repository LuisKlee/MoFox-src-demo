# Transport 模块（通讯传输系统）

> 目标：为适配器、核心逻辑和下游服务之间提供稳定、可观测、可扩展的消息收发与路由能力。

## 模块组成

```
src/core/transport/
├── message_receive/   # 入站：适配器/通道 -> Core 的消息收集、预处理、归一化
├── message_send/      # 出站：Core -> 适配器/通道 的消息格式化与发送
├── router/            # 路由与分发：根据会话/适配器/意图将消息分发到对应处理链
└── sink/              # Sink：针对适配器的 Core 接入点（含 WS 接收器）
```

**文档导航**
- [API_REFERENCE](./API_REFERENCE.md) - 完整接口与内置中间件说明
- [BEST_PRACTICES](./BEST_PRACTICES.md) - 设计与接入建议
- [QUICK_REFERENCE](./QUICK_REFERENCE.md) - 速查示例与常见错误

### 角色划分
- **message_receive**：负责入站解包、校验、归一化（如时序戳、sender、channel、payload 类型）。
- **router**：根据 `channel`、`session_id`、`intent`、`tenant` 等上下文做路由；支持中间件链（鉴权/节流/审计）。
- **message_send**：统一出站格式和序列化；支持重试、超时、速率限制、观察指标（成功/失败/延迟）。
- **sink**：为不同适配器（IM、Webhook、WS、MQ 等）提供接入端口，负责协议差异抹平与回传通道绑定。

## 数据模型（建议）

| 字段 | 说明 |
|------|------|
| `id` | 消息唯一 ID（适配器生成或 Core 生成） |
| `session_id` | 会话/对话 ID，用于路由和上下文归属 |
| `channel` | 来源/去向通道（如 `slack`, `wechat`, `webhook`, `ws`） |
| `role` | 角色：`user` / `assistant` / `system` / `tool` |
| `content` | 主要文本内容（富文本/多模态可放在 `attachments`） |
| `attachments` | 可选，结构化负载（如图片、文件、tool-calls） |
| `metadata` | 透传元数据（tenant、locale、device、trace_id 等） |
| `timestamp` | 事件时间，用于排序和监控 |

## 入站流程（示例）
1) Sink 收到适配器原始事件（如 Slack event / Webhook / WS）。
2) message_receive 进行：鉴权校验 -> 去重 -> 归一化为统一 Message。
3) router 将消息分发到：
   - 对话编排（如核心对话服务）
   - 工具/命令处理（如 slash commands）
   - 监控/审计管道
4) 处理结果交给 message_send。

## 出站流程（示例）
1) 业务侧产出规范化 Message（带 `session_id`、`channel`）。
2) message_send 选择对应 adapter 的序列化器与发送器。
3) 支持重试/回退（如降级为文本）、速率限制、超时、指标上报。

## 扩展点
- **适配器扩展**：在 sink 层新增适配器接入；提供 decode/encode、鉴权、签名验证、长连接管理。
- **路由中间件**：按需挂载鉴权、节流、审计、内容安全、灰度分流等中间件。
- **序列化策略**：message_send 根据 channel 选择序列化器（纯文本/Markdown/卡片/多模态）。
- **监控与日志**：统一输出计数、延迟、错误率；携带 trace_id/tenant 透传。

## 最小可用实现建议
- 定义统一 `Message` 数据类（含上表字段）。
- message_receive：
  - 幂等去重（基于 id / nonce）。
  - 基础鉴权（签名/Token）。
  - 归一化为 `Message`。
- router：
  - 基于 `channel` 和 `session_id` 的分发表。
  - 中间件链（同步或异步）。
- message_send：
  - 适配器序列化器 + 发送器接口。
  - 重试、超时、错误回调。
- sink：
  - Webhook/WS 基础接入样例。

## TODO 列表
- [ ] 定义核心 `Message` / `Envelope` 数据结构与类型注解
- [ ] 设计 router 中间件协议（同步/异步、异常传播）
- [ ] 设计 adapter registry（出站/入站解耦）
- [ ] 接入日志与监控指标（计数/延迟/错误率）
- [ ] 提供示例适配器（如 webhook + 控制台）
- [ ] 编写单元测试与集成测试

## 参考集成
- 与 **core/prompt**：在路由后可直接渲染 Prompt -> 调用 LLM -> message_send 返回。
- 与 **kernel/llm**：核心对话服务可使用 prompt 管理器 + llm_generate，结果通过 message_send 发回。
- 与 **kernel/logger**/**concurrency**：记录链路日志与异步任务调度（如长耗时操作）。
