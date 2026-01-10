# Core 层文档

## 概述

Core 层是 MoFox 的核心业务逻辑层，实现了记忆、对话、行为等核心功能。该层建立在 Kernel 层之上，不关心插件或具体平台，专注于提供通用的智能体能力。

## 核心模块

### 1. Prompt（提示词管理系统）

提示词管理系统提供了完整的提示词生命周期管理方案。

**核心功能:**
- 🎯 多种提示词类型（静态、动态模板、链式）
- 📦 参数系统（定义、验证、默认值）
- 🎛️ 全局管理（单例管理器）
- 🔌 扩展机制（拦截器、钩子）
- 📊 分类和优先级

**快速开始:**

```python
from src.core.prompt import TemplatePrompt, PromptParam, ParamType, register, render

# 创建动态提示词
prompt = TemplatePrompt(
    "greeting",
    "Hello {name}, welcome!"
)
prompt.params.add_param(PromptParam("name", ParamType.STRING, required=True))

# 注册和渲染
register(prompt)
result = render("greeting", name="Alice")
```

**相关文档:**
- [README](./prompt/README.md) - 完整使用指南
- [API_REFERENCE](./prompt/API_REFERENCE.md) - API 详细参考
- [BEST_PRACTICES](./prompt/BEST_PRACTICES.md) - 最佳实践
- [QUICK_REFERENCE](./prompt/QUICK_REFERENCE.md) - 快速参考

---

### 2. Components（基本插件组件管理）

*待开发*

基本插件组件系统，用于管理各类组件（Action、Adapter、Chatter 等）。

---

### 3. Perception（感知学习系统）

*待开发*

感知学习系统，包括：
- Memory（常规记忆）
- Knowledge（知识库）
- Meme（黑话库）
- Express（表达学习）

---

### 4. Transport（通讯传输系统）

*进行中*

通讯传输系统，包括：
- Message Receive（消息接收）
- Message Send（消息发送）
- Router（API 路由）
- Sink（适配器接收器）

文档：
- [Transport 概览](./transport/README.md)
- [Transport API](./transport/API_REFERENCE.md)
- [Transport 最佳实践](./transport/BEST_PRACTICES.md)
- [Transport 快速参考](./transport/QUICK_REFERENCE.md)

---

### 5. Models（基本模型）

*待开发*

基本数据模型定义。

---

## 架构图

```
Core 层
├── Prompt（提示词管理系统）✅
│   ├── params.py          - 参数系统
│   ├── prompt.py          - Prompt 基类和实现
│   ├── manager.py         - 全局管理器
│   └── __init__.py        - 公开 API
│
├── Components（插件组件管理）
│   ├── base/              - 组件基类
│   ├── managers/          - 组件应用管理
│   ├── types.py           - 组件类型
│   ├── registry.py        - 组件注册管理
│   └── state_manager.py   - 组件状态管理
│
├── Perception（感知学习系统）
│   ├── memory/            - 常规记忆
│   ├── knowledge/         - 知识库
│   ├── meme/              - 黑话库
│   └── express/           - 表达学习
│
├── Transport（通讯传输系统）
│   ├── message_receive/   - 消息接收
│   ├── message_send/      - 消息发送
│   ├── router/            - API 路由
│   └── sink/              - 适配器接收器
│
└── Models（基本模型）
    └── ...                - 数据模型
```

---

## 模块间依赖关系

```
Kernel 层
  ↑
  └─── Core 层
        ├─── Prompt
        ├─── Components
        ├─── Perception
        ├─── Transport
        └─── Models
        
App 层
  ↑
  └─── Core 层 + Kernel 层
```

---

## 最新状态

| 模块 | 状态 | 文档 | 测试 |
|------|------|------|------|
| Prompt | ✅ 完成 | ✅ 完整 | 待完成 |
| Components | ⏳ 计划中 | - | - |
| Perception | ⏳ 计划中 | - | - |
| Transport | ⏳ 进行中 | ✅ 概览 | - |
| Models | ⏳ 计划中 | - | - |

---

## 下一步

1. **编写 Prompt 单元测试** - 确保所有功能正常工作
2. **开发 Components 模块** - 实现插件组件系统
3. **实现 Perception 模块** - 感知学习能力
4. **完成 Transport 模块** - 通讯和消息处理
5. **集成测试** - Core 层与 Kernel 层的集成测试

---

## 贡献指南

在开发新模块时，请参考：

1. **代码结构** - 遵循现有的模块组织方式
2. **文档** - 为每个新模块编写：
   - README.md（使用指南）
   - API_REFERENCE.md（API 参考）
   - BEST_PRACTICES.md（最佳实践）
   - QUICK_REFERENCE.md（快速参考）
3. **测试** - 在 tests/core/ 下编写单元测试
4. **验证** - 运行代码检查和测试套件

---

## 相关资源

- [MoFox 重构指导总览](../../MoFox%20重构指导总览.md) - 整体架构
- [Kernel 层文档](../kernel/) - Kernel 模块
- [App 层文档](../app/) - App 模块

---

*最后更新: 2026-01-10*
