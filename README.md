# MoFox 重构概览

> 说明：本文件仅提供分层和目录的框架性概览，暂未包含具体实现或使用示例，可结合 [MoFox 重构指导总览.md](MoFox%20重构指导总览.md) 查看更详细的设计描述。

## 分层设计
- **kernel**：与具体业务无关的基础能力，包括配置、数据库、向量库、LLM 请求、日志、并发、存储等。
- **core**：使用 kernel 能力实现记忆、对话、行为等核心功能，不关心插件或具体平台。
- **app**：把 kernel 与 core 组装成可运行的 Bot 系统，对外暴露高级 API 与插件扩展点（当前文档未详细展开）。

## 目录速览
```
mofox-src/
  kernel/
  core/
```

## kernel 模块一览
- **db**：数据库接口与核心（dialect 适配、engine、session、异常）；优化模块含多级缓存（cache backend/local/redis 与 cache_manager）；API 提供 CRUD 与 Query 入口。
- **vector_db**：向量存储抽象与 chromadb 实现，入口工厂初始化服务实例。
- **config**：配置基类与读取、修改、更新的实现。
- **llm**：LLM 请求系统（utils、llm_request、异常、client 注册）；clients 包含 base、aiohttp gemini、bedrock、openai；payload 包含 message、resp_format、tool_option、standard_prompt。
- **logger**：日志入口、清理、元数据、格式化器、配置与处理器（console/file）。
- **concurrency**：异步任务管理与全局 watchdog。
- **storage**：JSON 本地持久化操作器。

## core 模块一览
- **components**：
  - base 组件基类：action、adapter、chatter、command、event_handler、router、service、plugin、prompt、tool。
  - managers：action/adapter/chatter/event/service/permission/plugin/prompt_component 管理器；MCP 管理（client/tool）；tool 管理（history、use）。
  - registry：组件注册；state_manager：组件状态管理；types：组件类型定义。
- **prompt**：Prompt 基类、全局管理器、参数系统。
- **perception**：感知学习，含 memory/knowledge/meme/express 等子模块。
- **transport**：通讯传输，含 message_receive、message_send、router、sink（针对适配器与 WS）。
- **models**：基础模型入口。

