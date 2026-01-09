# MoFox 文档中心

本目录包含 MoFox 项目的完整文档，文档结构与源码目录一一对应。

## 📚 文档结构

```
docs/
├── kernel/              # Kernel 层文档 - 基础能力
│   ├── concurrency/     # 并发管理 ✅
│   │   ├── watchdog.md                          # Watchdog 监控器
│   │   ├── task_manager.md                      # TaskManager 管理器
│   │   ├── QUICK_REFERENCE.md                   # 快速参考
│   │   ├── TASK_MANAGER_QUICK_REFERENCE.md      # 任务管理快速参考
│   │   ├── INTEGRATION_IMPROVEMENTS.md          # 集成改进报告
│   │   └── TEST_RESULTS_REPORT.md               # 测试结果报告
│   ├── config/          # 配置系统 ✅
│   │   ├── README.md                            # 概览文档
│   │   ├── API_REFERENCE.md                     # API 参考
│   │   ├── QUICK_REFERENCE.md                   # 快速参考
│   │   └── BEST_PRACTICES.md                    # 最佳实践
│   ├── db/              # 数据库模块 ✅
│   │   ├── README.md                            # 概览与快速开始
│   │   ├── API_REFERENCE.md                     # API 参考
│   │   ├── QUICK_REFERENCE.md                   # 快速参考
│   │   ├── CACHE_GUIDE.md                       # 缓存系统指南
│   │   ├── DATABASE_GUIDE.md                    # 数据库配置指南
│   │   ├── OPTIMIZATION_GUIDE.md                # 优化与架构设计
│   │   └── COMPLETION_SUMMARY.md                # 完成总结
│   ├── llm/             # LLM 系统 ✅
│   │   ├── README.md                            # 概览文档
│   │   ├── API_REFERENCE.md                     # API 参考
│   │   ├── QUICK_REFERENCE.md                   # 快速参考
│   │   └── BEST_PRACTICES.md                    # 最佳实践
│   ├── logger/          # 日志系统 ✅
│   │   ├── README.md                            # 概览文档
│   │   ├── API_REFERENCE.md                     # API 参考
│   │   ├── QUICK_REFERENCE.md                   # 快速参考
│   │   ├── CONFIGURATION_GUIDE.md               # 配置指南
│   │   ├── BEST_PRACTICES.md                    # 最佳实践
│   │   ├── TROUBLESHOOTING.md                   # 故障排查
│   │   └── LOGGER_STORAGE_INTEGRATION.md        # 存储集成
│   ├── storage/         # 本地存储 ✅
│   │   ├── README.md                            # 概览文档
│   │   ├── API_REFERENCE.md                     # API 参考
│   │   ├── CONFIGURATION_GUIDE.md               # 配置指南
│   │   ├── BEST_PRACTICES.md                    # 最佳实践
│   │   └── TROUBLESHOOTING.md                   # 故障排查
│   └── vector_db/       # 向量数据库 ✅
│       ├── README.md                            # 概览文档
│       ├── API_REFERENCE.md                     # API 参考
│       ├── QUICK_REFERENCE.md                   # 快速参考
│       ├── LOGGING_GUIDE.md                     # 日志集成指南
│       └── BEST_PRACTICES.md                    # 最佳实践
│
└── core/                # Core 层文档 - 核心功能 ⏳
    ├── components/      # 组件系统
    │   ├── base/        # 基础组件
    │   └── managers/    # 组件管理器
    │       ├── mcp_manager/
    │       └── tool_manager/
    ├── models/          # 数据模型
    ├── perception/      # 感知学习
    │   ├── express/
    │   ├── knowledge/
    │   ├── meme/
    │   └── memory/
    ├── prompt/          # Prompt 系统
    └── transport/       # 通讯传输
        ├── message_receive/
        ├── message_send/
        ├── router/
        └── sink/
```

## 📖 文档规范

每个模块文档应包含：

1. **模块概述** - 功能描述和设计目标
2. **核心组件** - 主要类、函数、常量的说明
3. **使用示例** - 实际代码示例
4. **API 参考** - 详细的参数和返回值说明
5. **依赖关系** - 与其他模块的关系
6. **注意事项** - 使用限制和最佳实践

## 🔍 快速导航

### Kernel 层（基础能力）

#### 并发管理 (Concurrency)
- [📘 Watchdog 全局任务监控器](kernel/concurrency/watchdog.md) - 异步任务监控和管理
- [📘 TaskManager 任务管理器](kernel/concurrency/task_manager.md) - 异步任务生命周期管理
- [📄 快速参考](kernel/concurrency/QUICK_REFERENCE.md) - 并发管理快速查阅手册
- [📄 TaskManager 快速参考](kernel/concurrency/TASK_MANAGER_QUICK_REFERENCE.md) - 任务管理器速查手册
- [📊 集成改进报告](kernel/concurrency/INTEGRATION_IMPROVEMENTS.md) - Watchdog 与 TaskManager 集成优化
- [📊 测试报告](kernel/concurrency/TEST_RESULTS_REPORT.md) - 并发模块测试结果

#### 配置系统 (Config)
- [📘 README](kernel/config/README.md) - 配置系统概览
- [📄 API 参考](kernel/config/API_REFERENCE.md) - 配置系统 API 完整文档
- [📄 快速参考](kernel/config/QUICK_REFERENCE.md) - 配置系统快速查阅手册
- [💡 最佳实践](kernel/config/BEST_PRACTICES.md) - 配置系统使用最佳实践

#### 数据库模块 (Database)
- [📘 README](kernel/db/README.md) - 数据库模块概览与快速开始
- [📄 API 参考](kernel/db/API_REFERENCE.md) - 数据库 API 完整文档
- [📄 快速参考](kernel/db/QUICK_REFERENCE.md) - 数据库快速查阅手册
- [📖 缓存指南](kernel/db/CACHE_GUIDE.md) - 缓存系统完整指南
- [📖 数据库指南](kernel/db/DATABASE_GUIDE.md) - 数据库选择与配置指南
- [📖 优化指南](kernel/db/OPTIMIZATION_GUIDE.md) - 性能优化与架构设计
- [✅ 完成总结](kernel/db/COMPLETION_SUMMARY.md) - 数据库模块实现总结

#### LLM 系统 (Large Language Model)
- [📘 README](kernel/llm/README.md) - LLM 系统概览
- [📄 API 参考](kernel/llm/API_REFERENCE.md) - LLM API 完整文档
- [📄 快速参考](kernel/llm/QUICK_REFERENCE.md) - LLM 快速查阅手册
- [💡 最佳实践](kernel/llm/BEST_PRACTICES.md) - LLM 使用最佳实践

#### 日志系统 (Logger)
- [📘 README](kernel/logger/README.md) - 日志系统概览
- [📄 API 参考](kernel/logger/API_REFERENCE.md) - 日志系统 API 完整文档
- [📄 快速参考](kernel/logger/QUICK_REFERENCE.md) - 日志系统快速查阅手册
- [📖 配置指南](kernel/logger/CONFIGURATION_GUIDE.md) - 日志系统配置详解
- [💡 最佳实践](kernel/logger/BEST_PRACTICES.md) - 日志系统使用最佳实践
- [🔧 故障排查](kernel/logger/TROUBLESHOOTING.md) - 日志系统常见问题解决
- [📊 存储集成](kernel/logger/LOGGER_STORAGE_INTEGRATION.md) - 日志与存储系统集成

#### 存储系统 (Storage)
- [📘 README](kernel/storage/README.md) - 存储系统概览
- [📄 API 参考](kernel/storage/API_REFERENCE.md) - 存储系统 API 完整文档
- [📖 配置指南](kernel/storage/CONFIGURATION_GUIDE.md) - 存储系统配置详解
- [💡 最佳实践](kernel/storage/BEST_PRACTICES.md) - 存储系统使用最佳实践
- [🔧 故障排查](kernel/storage/TROUBLESHOOTING.md) - 存储系统常见问题解决

#### 向量数据库 (Vector Database)
- [📘 README](kernel/vector_db/README.md) - 向量数据库概览
- [📄 API 参考](kernel/vector_db/API_REFERENCE.md) - 向量数据库 API 完整文档
- [📄 快速参考](kernel/vector_db/QUICK_REFERENCE.md) - 向量数据库快速查阅手册
- [📖 日志指南](kernel/vector_db/LOGGING_GUIDE.md) - 向量数据库日志集成指南
- [💡 最佳实践](kernel/vector_db/BEST_PRACTICES.md) - 向量数据库使用最佳实践

### Core 层（核心功能）

#### 组件系统
- 组件基类 - 待完善
- 组件管理器 - 待完善
- MCP 管理 - 待完善
- 工具管理 - 待完善

#### Prompt 系统
- Prompt 管理器 - 待完善
- 参数系统 - 待完善

#### 感知学习
- 记忆系统 - 待完善
- 知识系统 - 待完善
- 表达系统 - 待完善

#### 通讯传输
- 消息接收 - 待完善
- 消息发送 - 待完善
- 路由系统 - 待完善

## 📝 文档编写指南

### 文档命名规范
- 文档文件名与对应的 Python 模块文件同名
- 扩展名为 `.md`
- 例如：`watchdog.py` → `watchdog.md`

### 目录结构规范
- 文档目录结构与源码目录结构完全一致
- 例如：`src/kernel/concurrency/watchdog.py` → `docs/kernel/concurrency/watchdog.md`

### 内容编写规范

#### 标题层级
```markdown
# 模块名称（一级标题）

## 概述（二级标题）

### 功能特性（三级标题）

#### 具体功能点（四级标题）
```

#### 代码示例
使用代码块，并指定语言：
````markdown
```python
# 示例代码
import asyncio
```
````

#### API 文档
```markdown
**`function_name(param1, param2) -> ReturnType`**

功能描述

参数:
- `param1` (type): 参数说明
- `param2` (type): 参数说明

返回:
- `ReturnType`: 返回值说明

示例:
    代码示例
```

## 🚀 贡献文档

欢迎为 MoFox 项目贡献文档！

### 步骤
1. 选择一个待完善的模块
2. 在对应目录创建 `.md` 文件
3. 按照文档规范编写内容
4. 更新本 README 的快速导航链接

### 质量要求
- 内容准确、清晰
- 包含实际可运行的示例代码
- 说明模块的设计意图和使用场景
- 标注注意事项和最佳实践

## 📊 文档完成度

### Kernel 层
- [x] **concurrency/** - 并发管理模块（已完成）
  - [x] watchdog.md - 全局任务监控器
  - [x] task_manager.md - 任务管理器
  - [x] QUICK_REFERENCE.md - 快速参考
  - [x] TASK_MANAGER_QUICK_REFERENCE.md - 任务管理器快速参考
  - [x] 测试与集成报告
  
- [x] **config/** - 配置系统（已完成）
  - [x] README.md - 概览文档
  - [x] API_REFERENCE.md - API 参考
  - [x] QUICK_REFERENCE.md - 快速参考
  - [x] BEST_PRACTICES.md - 最佳实践
  
- [x] **db/** - 数据库模块（已完成）
  - [x] README.md - 概览文档
  - [x] API_REFERENCE.md - API 参考
  - [x] QUICK_REFERENCE.md - 快速参考
  - [x] CACHE_GUIDE.md - 缓存指南
  - [x] DATABASE_GUIDE.md - 数据库指南
  - [x] OPTIMIZATION_GUIDE.md - 优化指南
  
- [x] **llm/** - LLM 系统（已完成）
  - [x] README.md - 概览文档
  - [x] API_REFERENCE.md - API 参考
  - [x] QUICK_REFERENCE.md - 快速参考
  - [x] BEST_PRACTICES.md - 最佳实践
  
- [x] **logger/** - 日志系统（已完成）
  - [x] README.md - 概览文档
  - [x] API_REFERENCE.md - API 参考
  - [x] QUICK_REFERENCE.md - 快速参考
  - [x] CONFIGURATION_GUIDE.md - 配置指南
  - [x] BEST_PRACTICES.md - 最佳实践
  - [x] TROUBLESHOOTING.md - 故障排查
  - [x] LOGGER_STORAGE_INTEGRATION.md - 存储集成
  
- [x] **storage/** - 存储系统（已完成）
  - [x] README.md - 概览文档
  - [x] API_REFERENCE.md - API 参考
  - [x] CONFIGURATION_GUIDE.md - 配置指南
  - [x] BEST_PRACTICES.md - 最佳实践
  - [x] TROUBLESHOOTING.md - 故障排查
  
- [x] **vector_db/** - 向量数据库（已完成）
  - [x] README.md - 概览文档
  - [x] API_REFERENCE.md - API 参考
  - [x] QUICK_REFERENCE.md - 快速参考
  - [x] LOGGING_GUIDE.md - 日志指南
  - [x] BEST_PRACTICES.md - 最佳实践

### Core 层
- [ ] components/* - 组件系统（待完善）
- [ ] models/* - 数据模型（待完善）
- [ ] perception/* - 感知学习（待完善）
- [ ] prompt/* - Prompt 系统（待完善）
- [ ] transport/* - 通讯传输（待完善）

### 📈 完成统计
- **Kernel 层**: 7/7 模块已完成 ✅ (100%)
- **Core 层**: 0/5 模块已完成 ⏳ (0%)
- **总体进度**: 7/12 模块已完成 (58%)

---

*最后更新: 2026年1月1日*
