# MoFox-src-demo

> ✅ **已完成的核心功能**：
> - **kernel 层**：完整的基础设施（配置、数据库、LLM、日志、任务管理等）
> - **core 层**：核心业务逻辑（组件、提示词、感知、传输等）
> - **app 层**：可运行的 Bot 应用和统一 API 接口 ✨ **NEW!**

> 📖 详细设计说明请参考 [MoFox 重构指导总览.md](MoFox%20重构指导总览.md)

## 🎯 快速开始

### 最快的方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动 Bot
python start.py
```

就是这么简单！Bot 会自动初始化所有组件并启动交互式命令行界面。

### 使用说明

启动后，你可以：
- 输入消息与 Bot 对话
- 输入 `quit` 或 `exit` 退出
- 查看详细文档了解更多功能

📚 **详细文档**：[启动器使用指南](docs/app/bot/LAUNCHER_GUIDE.md)

## 🏗️ 架构设计

MoFox 采用清晰的三层架构：

```
┌─────────────────────────────────────┐
│      Application Layer (app)        │  ← Bot 应用、API 接口 ✨
├─────────────────────────────────────┤
│         Core Layer (core)            │  ← 业务逻辑、组件系统
├─────────────────────────────────────┤
│       Kernel Layer (kernel)          │  ← 基础设施、工具库
└─────────────────────────────────────┘
```

### Application Layer (app) - 应用层 ✨ NEW

把 kernel 和 core 组装成可运行的 Bot 系统：

- **Bot 启动器**：一键启动完整应用
- **Core API**：Core 层统一接口（Prompt、Transport、Perception 等）
- **Kernel API**：Kernel 层统一接口（Config、Database、LLM、Logger 等）
- **命令行界面**：交互式用户界面
- **插件系统**：易于扩展的插件机制（规划中）

📚 **文档索引**：
- [应用层概览](docs/app/README.md)
- [Bot 架构设计](docs/app/bot/BOT_ARCHITECTURE.md)
- [API 使用指南](docs/app/bot/API_GUIDE.md)
- [启动器使用指南](docs/app/bot/LAUNCHER_GUIDE.md)
- [开发指南](docs/app/bot/DEVELOPMENT_GUIDE.md)

### Core Layer (core) - 核心层

使用 kernel 能力实现业务功能，不关心具体平台：

- **components**：组件系统（action、adapter、chatter、plugin 等）
- **prompt**：提示词管理和构建
- **perception**：感知学习（memory、knowledge 等）
- **transport**：消息传输和路由
- **models**：数据模型定义

### Kernel Layer (kernel) - 基础层

与业务无关的基础能力：

- **config**：灵活的配置管理
- **vector_db**：向量存储
- **llm**：LLM 请求系统（支持多提供商）
- **logger**：集中式日志管理
- **concurrency**：异步任务管理
- **db**：数据库接口
- **storage**：本地持久化

### 基本要求

- **Python 版本**：推荐 **Python 3.11+**（支持 3.10-3.12）
- **操作系统**：Windows、Linux、macOS
- **依赖管理**：pip 或虚拟环境

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd MoFox-src-demo

# 2. 创建虚拟环境（推荐）
python -m venv .venv

# 3. 激活虚拟环境
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 验证安装
python start.py
```

### Windows 编码提示

如遇到 `UnicodeDecodeError` 错误，先切换终端编码：

```bash
chcp 65001
pip install -r requirements.txt
```

### 开发工具（可选）

```bash
# 安装开发依赖
pip install pytest pytest-asyncio pytest-cov black flake8 mypy isort

# 代码格式化
black src/

# 运行测试
pytest tests/ --cov=src
```

## 📖 完整模块文档

## 📦 项目结构

```
MoFox-src-demo/
├── start.py                 # 快速启动脚本 ⭐
├── requirements.txt         # 项目依赖
├── README.md               # 本文件
├── src/
│   ├── app/                # 应用层 ✨ NEW
│   │   └── bot/
│   │       ├── main.py              # Bot 主入口
│   │       ├── __init__.py          # 包初始化
│   │       ├── core_api/            # Core API 封装
│   │       ├── kernel_api_legacy/   # Kernel API 封装
│   │       └── examples/            # 使用示例
│   ├── core/               # 核心层
│   │   ├── components/     # 组件系统
│   │   ├── prompt/         # 提示词系统
│   │   ├── perception/     # 感知系统
│   │   ├── transport/      # 传输系统
│   │   └── models/         # 数据模型
│   └── kernel/             # 基础层
│       ├── config/         # 配置管理 ✅
│       ├── db/             # 数据库 ✅
│       ├── llm/            # LLM 接口 ✅
│       ├── logger/         # 日志系统 ✅
│       ├── storage/        # 存储系统 ✅
│       ├── vector_db/      # 向量数据库 ✅
│       └── concurrency/    # 任务管理 ✅
├── docs/                   # 完整文档
│   ├── app/                # 应用层文档 ✨ NEW
│   │   └── bot/
│   │       ├── BOT_ARCHITECTURE.md
│   │       ├── API_GUIDE.md
│   │       ├── LAUNCHER_GUIDE.md
│   │       └── DEVELOPMENT_GUIDE.md
│   ├── core/               # Core 层文档
│   └── kernel/             # Kernel 层文档
├── tests/                  # 测试代码
│   ├── app/
│   ├── core/
│   └── kernel/
└── logs/                   # 日志目录（自动创建）
```

## 🚀 使用示例

### 示例 1: 基本使用

```python
from app.bot.main import MoFoxBot
import asyncio

async def main():
    # 使用上下文管理器（推荐）
    async with MoFoxBot(app_name="my_bot") as bot:
        # Bot 自动初始化
        await bot.run()  # 启动交互式界面

asyncio.run(main())
```

### 示例 2: API 调用

```python
from app.bot.main import MoFoxBot

async def api_example():
    async with MoFoxBot() as bot:
        # 使用 Core API
        prompt = await bot.core.prompt.build("chat", message="你好")
        
        # 使用 Kernel API
        response = await bot.kernel.llm.chat("你好，世界！")
        print(f"回复: {response}")
        
        # 记录日志
        bot.kernel.logger.info("处理完成")
```

### 示例 3: 自定义 Bot

```python
from app.bot.main import MoFoxBot

class MyBot(MoFoxBot):
    async def _process_input(self, user_input: str) -> str:
        # 自定义处理逻辑
        if "天气" in user_input:
            return "今天天气很好！"
        
        # 调用 LLM
        return await self.kernel.llm.chat(user_input)

# 使用自定义 Bot
async with MyBot(app_name="weather_bot") as bot:
    await bot.run()
```

### 示例 4: 命令行参数

```bash
# 指定应用名称
python start.py --name my_custom_bot

# 使用配置文件
python start.py --config config.yaml

# 只使用 Core 层
python start.py --no-kernel

# 只使用 Kernel 层
python start.py --no-core
```

更多示例请查看 [API 使用指南](docs/app/bot/API_GUIDE.md)。

## 🎯 主要特性

### ✨ 应用层特性

- **一键启动**：`python start.py` 即可运行
- **双 API 设计**：Core API 和 Kernel API 分离，职责清晰
- **异步架构**：完整的异步支持，高性能
- **灵活配置**：支持命令行参数、配置文件、环境变量
- **易于扩展**：支持继承、组合、插件等多种扩展方式
- **完善文档**：详细的架构、API、使用文档

### 🔧 Kernel 层特性

- **配置管理**：支持 JSON/YAML/ENV 多种格式
- **多 LLM 支持**：OpenAI、Google Gemini、AWS Bedrock
- **向量数据库**：ChromaDB 集成，支持语义搜索
- **任务管理**：异步任务调度、监控、超时控制
- **日志系统**：结构化日志、自动轮转、元数据支持
- **数据库抽象**：统一的 CRUD 接口，支持多种数据库

### 🧠 Core 层特性

- **组件系统**：灵活的组件注册和管理
- **提示词系统**：模板化提示词构建
- **感知系统**：多模态输入处理
- **传输系统**：消息路由和传输抽象

## 📚 文档导航

### 新手入门
1. [快速开始](#快速开始) - 5分钟上手
2. [启动器使用指南](docs/app/bot/LAUNCHER_GUIDE.md) - 详细的启动说明
3. [API 使用指南](docs/app/bot/API_GUIDE.md) - API 完整说明

### 开发者
1. [Bot 架构设计](docs/app/bot/BOT_ARCHITECTURE.md) - 理解系统设计
2. [开发指南](docs/app/bot/DEVELOPMENT_GUIDE.md) - 自定义开发
3. [Kernel 层文档](docs/kernel/) - 基础设施详解
4. [Core 层文档](docs/core/) - 核心功能详解

### 运维部署
1. [启动器使用指南](docs/app/bot/LAUNCHER_GUIDE.md) - 启动和配置
2. 部署指南（规划中）

## 🔨 开发环境搭建

### 基本要求

## 📖 完整模块文档

### Application Layer (app) - 应用层 ✨

#### Bot 应用
完整的可运行 Bot 系统：
- [应用层概览](docs/app/README.md) - 文档导航
- [Bot 架构设计](docs/app/bot/BOT_ARCHITECTURE.md) - 系统架构和设计原则
- [API 使用指南](docs/app/bot/API_GUIDE.md) - Core API 和 Kernel API 详解
- [启动器使用指南](docs/app/bot/LAUNCHER_GUIDE.md) - 启动、配置、故障排除
- [开发指南](docs/app/bot/DEVELOPMENT_GUIDE.md) - 自定义开发、扩展、测试

### Kernel Layer (kernel) - 基础层 ✅

所有 kernel 模块已完成实现和文档：

#### config - 配置管理
灵活的多格式配置系统
- 📚 [README](docs/kernel/config/README.md) | [API](docs/kernel/config/API_REFERENCE.md) | [最佳实践](docs/kernel/config/BEST_PRACTICES.md)

#### vector_db - 向量数据库
向量存储和相似度搜索
- 📚 [README](docs/kernel/vector_db/README.md) | [API](docs/kernel/vector_db/API_REFERENCE.md) | [日志集成](docs/kernel/vector_db/LOGGING_GUIDE.md)

#### llm - LLM 接口
多提供商 LLM 请求系统
- 📚 [README](docs/kernel/llm/README.md) | [API](docs/kernel/llm/API_REFERENCE.md) | [最佳实践](docs/kernel/llm/BEST_PRACTICES.md)

#### logger - 日志系统
集中式日志管理
- 📚 [README](docs/kernel/logger/README.md) | [API](docs/kernel/logger/API_REFERENCE.md)

#### concurrency - 任务管理
异步任务调度和监控
- 📚 [README](docs/kernel/concurrency/README.md) | [任务管理](docs/kernel/concurrency/task_manager.md)

#### db - 数据库
统一的数据库接口
- 📚 [README](docs/kernel/db/README.md) | [数据库指南](docs/kernel/db/DATABASE_GUIDE.md)

#### storage - 本地存储
JSON 格式持久化
- 📚 [README](docs/kernel/storage/README.md) | [API](docs/kernel/storage/API_REFERENCE.md)

### Core Layer (core) - 核心层

#### components - 组件系统
- **base**：组件基类（action、adapter、chatter、command、event_handler、router、service、plugin、prompt、tool）
- **managers**：各类管理器（action/adapter/chatter/event/service/permission/plugin/prompt_component、MCP、tool）
- **registry**：组件注册表
- **state_manager**：组件状态管理
- **types**：组件类型定义

#### prompt - 提示词系统
Prompt 基类、全局管理器、参数系统

#### perception - 感知学习
含 memory/knowledge/meme/express 等子模块

#### transport - 通讯传输
含 message_receive、message_send、router、sink（针对适配器与 WS）

#### models - 数据模型
基础模型入口

详细规划请查看[开发指南](docs/app/bot/DEVELOPMENT_GUIDE.md#后续开发计划)。

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 贡献方式
- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码

### 贡献流程
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

详细信息请查看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📋 版本信息

- **当前版本**：v0.1.0
- **更新日期**：2026-01-11
- **Python 要求**：3.10+（推荐 3.11+）

### 更新日志

#### v0.1.0 (2026-01-11)
- ✨ 新增 Bot 应用层和启动器
- ✨ 新增 Core API 和 Kernel API 统一接口
- ✨ 新增完整的应用层文档
- ✅ 完成 Kernel 层所有模块
- 📚 完善项目文档结构


## 📞 联系方式

- **项目主页**：[GitHub Repository]
- **问题反馈**：[Issues]
- **文档**：[docs/](docs/)

---

**MoFox** - 模块化 AI 机器人框架 | Made with ❤️ by MoFox Team

## 开发规范与质量要求

### 强制性规范（kernel & core 层）

#### 1. 测试覆盖率要求
- **kernel 层和 core 层必须达到 100% pytest 测试覆盖率**
- 每个模块文件必须有对应的独立测试文件
- 测试文件命名规范：`test_<module_name>.py`
- 测试位置：与源码目录结构对应的 `tests/` 目录下

#### 2. 测试文件结构要求
```
src/
├── kernel/
│   ├── concurrency/
│   │   ├── watchdog.py
│   │   └── task_manager.py
│   └── ...
└── tests/
    ├── kernel/
    │   ├── concurrency/
    │   │   ├── test_watchdog.py
    │   │   └── test_task_manager.py
    │   └── ...
    └── core/
        └── ...
```

#### 3. 文档要求
- 每个模块文件必须有对应的 Markdown 文档
- 文档命名规范：与模块文件同名，扩展名为 `.md`
- 文档位置：`docs/` 目录下，保持与源码相同的目录结构
- 文档内容必须包含：
  - 模块功能概述
  - 主要类/函数说明
  - 使用示例
  - API 参考
  - 依赖关系说明

#### 4. 文档结构示例
```
docs/
├── kernel/
│   ├── concurrency/
│   │   ├── watchdog.md
│   │   └── task_manager.md
│   └── ...
└── core/
    └── ...
```

#### 5. 测试规范
- 单元测试：测试独立函数和方法
- 集成测试：测试模块间协作
- 异步测试：使用 `pytest-asyncio` 测试异步代码
- Mock 测试：使用 `pytest-mock` 隔离外部依赖
- 覆盖率检查：运行 `pytest --cov=mofox_src --cov-report=html`

#### 6. 代码质量检查
所有提交必须通过以下检查：
```bash
# 代码格式化
black src/

# 代码风格检查
flake8 src/

# 类型检查
mypy src/

# 导入排序
isort src/

# 运行测试
pytest tests/ --cov=mofox_src --cov-report=term-missing
```

#### 7. 提交前检查清单
- [ ] 代码已通过所有单元测试
- [ ] 测试覆盖率达到 100%
- [ ] 已编写模块文档
- [ ] 代码已格式化（black）
- [ ] 已通过 flake8 检查
- [ ] 已通过 mypy 类型检查
- [ ] 文档示例代码已验证可运行

## 合并到发行版本说明
- 在合并到发行版本之前，请确保所有功能经过充分测试。
- 任何不稳定的功能应在合并前进行审查。
- 合并后，需更新版本号并记录变更。

### 推荐开发流程

1. **编写接口和类型定义** - 先定义清晰的接口
2. **编写文档** - 描述预期行为和使用方式
3. **编写测试用例** - TDD（测试驱动开发）
4. **实现功能代码** - 让测试通过
5. **代码审查** - 确保符合规范
6. **提交代码** - 附带测试和文档

### 质量目标

- **kernel 层**：零依赖外部业务逻辑，100% 可复用
- **core 层**：最小化对 kernel 的耦合，清晰的抽象边界
- **测试覆盖率**：kernel & core 层保持 100%
- **文档完整性**：每个公开 API 都有文档和示例
- **代码可维护性**：新人可通过文档快速上手

