# MoFox Bot

MoFox Bot 应用层，整合 Core 和 Kernel 功能的完整机器人应用。

## 📂 目录结构

```
bot/
├── main.py                  # Bot 启动器（主入口）
├── __init__.py              # 包初始化文件
├── core_api/                # Core 层 API
│   ├── core_api.py
│   ├── README.md
│   └── README_EN.md
└── kernel_api_legacy/       # Kernel 层 API（存档）
    ├── kernel_api.py
    ├── README.md
    └── README_EN.md
```

## 🚀 快速开始

### 1. 基本启动

从项目根目录运行：

```bash
# 激活虚拟环境（如果有）
.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate    # Linux/Mac

# 启动 Bot
python -m app.bot.main
```

或者直接运行：

```bash
cd src
python app/bot/main.py
```

### 2. 带参数启动

```bash
# 指定应用名称
python -m app.bot.main --name my_custom_bot

# 使用配置文件
python -m app.bot.main --config config.yaml

# 只使用 Core 层
python -m app.bot.main --no-kernel

# 只使用 Kernel 层
python -m app.bot.main --no-core
```

### 3. 在代码中使用

```python
import asyncio
from app.bot.main import MoFoxBot

async def run_bot():
    # 使用上下文管理器（推荐）
    async with MoFoxBot(app_name="my_bot") as bot:
        await bot.run()

# 运行
asyncio.run(run_bot())
```

## 💡 功能特性

### Bot 启动器 (main.py)

- ✅ 自动初始化 Core 和 Kernel 层
- ✅ 异步上下文管理器支持
- ✅ 命令行参数解析
- ✅ 优雅的错误处理和关闭
- ✅ 交互式命令行界面（示例）
- ✅ 模块化设计，易于扩展

### Core API

提供 Core 层功能：
- 提示词系统 (Prompt)
- 传输系统 (Transport)
- 感知系统 (Perception)
- 组件系统 (Components)
- 模型系统 (Models)

详见：[Core API 文档](core_api/README.md)

### Kernel API

提供 Kernel 层功能：
- 配置管理 (Config)
- 数据库 (Database)
- LLM 接口
- 日志系统 (Logger)
- 存储系统 (Storage)
- 向量数据库 (Vector DB)
- 任务管理器 (Task Manager)

详见：[Kernel API 文档](kernel_api_legacy/README.md)

## 📖 使用示例

### 示例 1: 最简单的 Bot

```python
import asyncio
from app.bot.main import MoFoxBot

async def main():
    bot = MoFoxBot(app_name="simple_bot")
    await bot.initialize()
    
    # 处理单个消息
    response = await bot._process_input("你好")
    print(response)
    
    await bot.shutdown()

asyncio.run(main())
```

### 示例 2: 自定义业务逻辑

```python
from app.bot.main import MoFoxBot

class MyCustomBot(MoFoxBot):
    """自定义 Bot"""
    
    async def _process_input(self, user_input: str) -> str:
        """重写处理逻辑"""
        # 自定义业务逻辑
        if "天气" in user_input:
            return "今天天气很好！"
        
        # 调用 LLM
        if self.kernel:
            # response = await self.kernel.llm.chat(user_input)
            # return response
            pass
        
        return f"收到: {user_input}"

# 使用自定义 Bot
async def main():
    async with MyCustomBot(app_name="weather_bot") as bot:
        await bot.run()
```

### 示例 3: 使用 Core 和 Kernel 功能

```python
from app.bot.main import MoFoxBot

async def main():
    async with MoFoxBot() as bot:
        # 使用 Core API
        if bot.core:
            prompt = await bot.core.prompt.build(
                "greeting",
                name="User"
            )
            print(f"Prompt: {prompt}")
        
        # 使用 Kernel API
        if bot.kernel:
            # 使用日志
            bot.kernel.logger.info("Bot 已启动")
            
            # 使用存储
            bot.kernel.storage.save("key", {"data": "value"})
            
            # 使用配置
            config = bot.kernel.config
            print(f"配置: {config}")
```

## 🛠️ 开发指南

### 扩展 Bot 功能

1. **继承 MoFoxBot 类**

```python
class MyBot(MoFoxBot):
    async def initialize(self):
        await super().initialize()
        # 自定义初始化
        
    async def _main_loop(self):
        # 自定义主循环
        pass
```

2. **添加新的命令行参数**

在 `main()` 函数中添加参数：

```python
parser.add_argument(
    "--my-option",
    type=str,
    help="我的自定义选项"
)
```

3. **集成其他服务**

```python
class BotWithWebAPI(MoFoxBot):
    async def initialize(self):
        await super().initialize()
        # 启动 Web 服务
        self.web_server = await start_web_server()
```

### 调试模式

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

async with MoFoxBot(app_name="debug_bot") as bot:
    await bot.run()
```

## 📋 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--name` | 应用名称 | `mofox_bot` |
| `--config` | 配置文件路径 | `None` |
| `--no-core` | 禁用 Core 层 | `False` |
| `--no-kernel` | 禁用 Kernel 层 | `False` |

## ⚠️ 注意事项

1. **异步编程**: 所有方法都是异步的，需要使用 `async/await`
2. **资源管理**: 使用上下文管理器确保正确关闭
3. **路径问题**: 从项目根目录运行，或使用 `-m` 模块方式运行
4. **依赖检查**: 确保安装了所需的依赖包

## 🔧 故障排除

### 导入错误

如果遇到导入错误：

```bash
# 确保在项目根目录
cd /path/to/MoFox-src-demo

# 使用模块方式运行
python -m app.bot.main
```

### 初始化失败

检查日志输出，确认：
- 配置文件路径正确
- 必要的目录存在（logs, data）
- 依赖包已安装

## 🔗 相关链接

- [Core API 文档](core_api/README.md)
- [Kernel API 文档](kernel_api_legacy/README.md)
- [项目重构指导](../../../MoFox%20重构指导总览.md)

## 📝 更新日志

### v0.1.0 (2026-01-11)
- ✨ 初始版本
- ✅ 基本启动器实现
- ✅ Core 和 Kernel 层整合
- ✅ 命令行界面
- ✅ 异步支持

## 📄 许可证

MIT License
