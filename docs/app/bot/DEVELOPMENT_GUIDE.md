# MoFox 开发指南

Bot 应用的后续开发指南和最佳实践

## 📋 目录

- [开发环境](#开发环境)
- [自定义 Bot 开发](#自定义-bot-开发)
- [扩展功能开发](#扩展功能开发)
- [API 扩展](#api-扩展)
- [测试开发](#测试开发)
- [调试技巧](#调试技巧)
- [性能优化](#性能优化)
- [后续开发计划](#后续开发计划)

## 开发环境

### 环境搭建

```bash
# 1. 克隆项目
git clone <repository-url>
cd MoFox-src-demo

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
# Windows
.\.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 安装开发依赖（可选）
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

### 项目结构理解

```
MoFox-src-demo/
├── src/
│   ├── app/
│   │   └── bot/
│   │       ├── main.py              # Bot 主入口 ⭐ 开发重点
│   │       ├── core_api/            # Core API 封装
│   │       │   └── core_api.py      # ⭐ Core API 扩展点
│   │       └── kernel_api_legacy/   # Kernel API 封装
│   │           └── kernel_api.py    # ⭐ Kernel API 扩展点
│   ├── core/                        # Core 层实现
│   │   ├── prompt/                  # ⭐ 提示词系统
│   │   ├── transport/               # ⭐ 传输系统
│   │   └── ...
│   └── kernel/                      # Kernel 层实现
│       ├── llm/                     # ⭐ LLM 集成
│       ├── db/                      # ⭐ 数据库
│       └── ...
├── docs/                            # 文档
├── tests/                           # 测试代码 ⭐ 添加测试
├── start.py                         # 快速启动
└── requirements.txt                 # 依赖列表
```

### 开发工具配置

#### VS Code 配置

创建 `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}
```

#### Git 忽略文件

```.gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/

# 数据和日志
logs/
data/
*.db
*.log

# 配置
.env
config.local.yaml

# IDE
.vscode/
.idea/
```

## 自定义 Bot 开发

### 方式 1: 继承 MoFoxBot

最推荐的方式，通过继承扩展功能。

```python
# my_bot.py
from app.bot.main import MoFoxBot
import asyncio

class MyCustomBot(MoFoxBot):
    """自定义 Bot 实现"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加自定义属性
        self.custom_data = {}
    
    async def initialize(self):
        """扩展初始化"""
        # 调用父类初始化
        await super().initialize()
        
        # 自定义初始化逻辑
        print("🔧 初始化自定义功能...")
        await self._init_custom_features()
        print("✅ 自定义功能初始化完成")
    
    async def _init_custom_features(self):
        """初始化自定义功能"""
        # 加载自定义数据
        self.custom_data = await self._load_custom_data()
        
        # 注册自定义命令
        self.register_command("custom", self._handle_custom)
    
    async def _load_custom_data(self):
        """加载自定义数据"""
        if self.kernel:
            store = self.kernel.storage.get_store("custom_data")
            return store.load("data", default={})
        return {}
    
    async def _process_input(self, user_input: str) -> str:
        """重写输入处理逻辑"""
        # 自定义预处理
        user_input = self._preprocess(user_input)
        
        # 检查自定义命令
        if user_input.startswith("/"):
            return await self._handle_command(user_input)
        
        # 自定义业务逻辑
        if "天气" in user_input:
            return await self._handle_weather(user_input)
        
        if "新闻" in user_input:
            return await self._handle_news(user_input)
        
        # 默认使用 LLM
        if self.kernel and hasattr(self.kernel, 'llm'):
            try:
                response = await self.kernel.llm.chat(user_input)
                return response
            except Exception as e:
                self.kernel.logger.error(f"LLM 调用失败: {e}")
        
        return f"收到消息：{user_input}"
    
    def _preprocess(self, text: str) -> str:
        """预处理输入"""
        # 去除多余空格
        text = " ".join(text.split())
        # 转小写
        text = text.lower()
        return text
    
    async def _handle_command(self, command: str) -> str:
        """处理命令"""
        parts = command.split()
        cmd = parts[0][1:]  # 去除 /
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "help":
            return self._get_help()
        elif cmd == "stats":
            return await self._get_stats()
        elif cmd == "custom":
            return await self._handle_custom(args)
        else:
            return f"未知命令: {cmd}"
    
    def _get_help(self) -> str:
        """获取帮助信息"""
        return """
可用命令：
/help     - 显示帮助
/stats    - 显示统计信息
/custom   - 自定义命令
quit/exit - 退出程序
"""
    
    async def _get_stats(self) -> str:
        """获取统计信息"""
        if self.kernel and self.kernel.task_manager:
            stats = self.kernel.task_manager.get_stats()
            return f"""
统计信息：
- 总任务数: {stats.get('total', 0)}
- 完成任务: {stats.get('completed', 0)}
- 运行中: {stats.get('running', 0)}
- 失败任务: {stats.get('failed', 0)}
"""
        return "统计信息不可用"
    
    async def _handle_custom(self, args: list) -> str:
        """处理自定义命令"""
        return f"自定义命令执行: {args}"
    
    async def _handle_weather(self, query: str) -> str:
        """处理天气查询"""
        # TODO: 集成天气 API
        return "今天天气晴朗，温度 20°C"
    
    async def _handle_news(self, query: str) -> str:
        """处理新闻查询"""
        # TODO: 集成新闻 API
        return "最新新闻：MoFox 发布新版本"
    
    async def shutdown(self):
        """扩展关闭逻辑"""
        # 保存自定义数据
        if self.kernel:
            store = self.kernel.storage.get_store("custom_data")
            store.save("data", self.custom_data)
        
        # 调用父类关闭
        await super().shutdown()


# 使用自定义 Bot
async def main():
    async with MyCustomBot(app_name="my_bot") as bot:
        await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### 方式 2: 组合模式

不继承，而是组合使用 API。

```python
# composed_bot.py
from app.bot.core_api import MoFoxCore
from app.bot.kernel_api_legacy import MoFoxKernel
import asyncio

class ComposedBot:
    """使用组合模式的 Bot"""
    
    def __init__(self, app_name: str = "composed_bot"):
        self.app_name = app_name
        self.core = None
        self.kernel = None
    
    async def initialize(self):
        """初始化"""
        # 初始化 Core
        self.core = MoFoxCore(app_name=self.app_name)
        await self.core.initialize()
        
        # 初始化 Kernel
        self.kernel = MoFoxKernel(app_name=self.app_name)
        await self.kernel.initialize()
    
    async def process(self, user_input: str) -> str:
        """处理输入"""
        # 使用 Core API
        # prompt = await self.core.prompt.build("chat", message=user_input)
        
        # 使用 Kernel API
        response = await self.kernel.llm.chat(user_input)
        
        # 记录日志
        self.kernel.logger.info(f"处理完成: {user_input[:50]}...")
        
        return response
    
    async def run(self):
        """运行循环"""
        print("Bot 运行中...")
        while True:
            user_input = await asyncio.to_thread(input, "You: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            
            response = await self.process(user_input)
            print(f"Bot: {response}\n")
    
    async def shutdown(self):
        """关闭"""
        if self.core:
            await self.core.shutdown()
        if self.kernel:
            await self.kernel.shutdown()
```

## 扩展功能开发

### 添加新的命令处理器

```python
# commands.py
from typing import Dict, Callable, Awaitable

class CommandHandler:
    """命令处理器"""
    
    def __init__(self):
        self.commands: Dict[str, Callable[[list], Awaitable[str]]] = {}
    
    def register(self, name: str, handler: Callable):
        """注册命令"""
        self.commands[name] = handler
    
    async def execute(self, command: str) -> str:
        """执行命令"""
        parts = command.split()
        if not parts or not parts[0].startswith('/'):
            return "无效命令"
        
        cmd_name = parts[0][1:]
        args = parts[1:]
        
        if cmd_name in self.commands:
            return await self.commands[cmd_name](args)
        else:
            return f"未知命令: {cmd_name}"


# 在 Bot 中使用
class ExtendedBot(MoFoxBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmd_handler = CommandHandler()
        
        # 注册命令
        self.cmd_handler.register("time", self._cmd_time)
        self.cmd_handler.register("echo", self._cmd_echo)
    
    async def _cmd_time(self, args: list) -> str:
        """时间命令"""
        from datetime import datetime
        return f"当前时间: {datetime.now()}"
    
    async def _cmd_echo(self, args: list) -> str:
        """回声命令"""
        return " ".join(args)
    
    async def _process_input(self, user_input: str) -> str:
        if user_input.startswith('/'):
            return await self.cmd_handler.execute(user_input)
        return await super()._process_input(user_input)
```

### 添加插件系统

```python
# plugin.py
from abc import ABC, abstractmethod
from typing import Any

class Plugin(ABC):
    """插件基类"""
    
    @abstractmethod
    async def initialize(self, bot: 'MoFoxBot'):
        """初始化插件"""
        pass
    
    @abstractmethod
    async def process(self, user_input: str, context: dict) -> Any:
        """处理输入"""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """关闭插件"""
        pass


class WeatherPlugin(Plugin):
    """天气插件示例"""
    
    async def initialize(self, bot):
        self.bot = bot
        print("天气插件已加载")
    
    async def process(self, user_input: str, context: dict):
        if "天气" in user_input:
            # TODO: 调用天气 API
            return "今天天气晴朗"
        return None
    
    async def shutdown(self):
        print("天气插件已关闭")


# 在 Bot 中集成
class PluginBot(MoFoxBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugins = []
    
    def add_plugin(self, plugin: Plugin):
        """添加插件"""
        self.plugins.append(plugin)
    
    async def initialize(self):
        await super().initialize()
        
        # 初始化所有插件
        for plugin in self.plugins:
            await plugin.initialize(self)
    
    async def _process_input(self, user_input: str) -> str:
        context = {"bot": self}
        
        # 让插件处理
        for plugin in self.plugins:
            result = await plugin.process(user_input, context)
            if result is not None:
                return result
        
        # 默认处理
        return await super()._process_input(user_input)
    
    async def shutdown(self):
        # 关闭所有插件
        for plugin in self.plugins:
            await plugin.shutdown()
        
        await super().shutdown()


# 使用
bot = PluginBot()
bot.add_plugin(WeatherPlugin())
bot.add_plugin(NewsPlugin())
```

### 添加中间件系统

```python
# middleware.py
from typing import Callable, Awaitable

class Middleware:
    """中间件基类"""
    
    async def process(
        self,
        user_input: str,
        next_handler: Callable[[str], Awaitable[str]]
    ) -> str:
        # 前置处理
        user_input = await self.before(user_input)
        
        # 调用下一个处理器
        response = await next_handler(user_input)
        
        # 后置处理
        response = await self.after(response)
        
        return response
    
    async def before(self, user_input: str) -> str:
        """前置处理"""
        return user_input
    
    async def after(self, response: str) -> str:
        """后置处理"""
        return response


class LoggingMiddleware(Middleware):
    """日志中间件"""
    
    async def before(self, user_input: str) -> str:
        print(f"[LOG] 收到输入: {user_input}")
        return user_input
    
    async def after(self, response: str) -> str:
        print(f"[LOG] 生成响应: {response[:50]}...")
        return response


class FilterMiddleware(Middleware):
    """过滤中间件"""
    
    async def before(self, user_input: str) -> str:
        # 过滤敏感词
        sensitive_words = ["敏感词1", "敏感词2"]
        for word in sensitive_words:
            user_input = user_input.replace(word, "***")
        return user_input


# 中间件管理器
class MiddlewareStack:
    def __init__(self):
        self.middlewares = []
    
    def use(self, middleware: Middleware):
        """添加中间件"""
        self.middlewares.append(middleware)
    
    async def process(
        self,
        user_input: str,
        final_handler: Callable[[str], Awaitable[str]]
    ) -> str:
        """处理请求"""
        async def create_chain(index: int):
            if index >= len(self.middlewares):
                return final_handler
            
            async def handler(inp: str) -> str:
                next_handler = await create_chain(index + 1)
                return await self.middlewares[index].process(inp, next_handler)
            
            return handler
        
        chain = await create_chain(0)
        return await chain(user_input)
```

## API 扩展

### 扩展 Core API

```python
# extended_core_api.py
from app.bot.core_api.core_api import MoFoxCore

class ExtendedCore(MoFoxCore):
    """扩展的 Core API"""
    
    async def initialize(self):
        await super().initialize()
        
        # 添加新模块
        await self._init_custom_module()
    
    async def _init_custom_module(self):
        """初始化自定义模块"""
        self._custom_module = MyCustomModule()
    
    @property
    def custom(self):
        """访问自定义模块"""
        return self._custom_module
```

### 扩展 Kernel API

```python
# extended_kernel_api.py
from app.bot.kernel_api_legacy.kernel_api import MoFoxKernel

class ExtendedKernel(MoFoxKernel):
    """扩展的 Kernel API"""
    
    async def initialize(self):
        await super().initialize()
        
        # 添加新功能
        await self._init_cache()
    
    async def _init_cache(self):
        """初始化缓存"""
        from kernel.cache import RedisCache
        self._cache = RedisCache()
        await self._cache.connect()
    
    @property
    def cache(self):
        """访问缓存"""
        return self._cache
```

## 测试开发

### 单元测试

```python
# tests/test_bot.py
import pytest
from app.bot.main import MoFoxBot

@pytest.mark.asyncio
async def test_bot_initialization():
    """测试 Bot 初始化"""
    bot = MoFoxBot(app_name="test_bot")
    await bot.initialize()
    
    assert bot._initialized == True
    assert bot.core is not None
    assert bot.kernel is not None
    
    await bot.shutdown()


@pytest.mark.asyncio
async def test_bot_process_input():
    """测试输入处理"""
    bot = MoFoxBot(app_name="test_bot")
    await bot.initialize()
    
    response = await bot._process_input("测试消息")
    assert response is not None
    assert isinstance(response, str)
    
    await bot.shutdown()


@pytest.mark.asyncio
async def test_custom_bot():
    """测试自定义 Bot"""
    class TestBot(MoFoxBot):
        async def _process_input(self, user_input: str) -> str:
            return f"Echo: {user_input}"
    
    bot = TestBot()
    await bot.initialize()
    
    response = await bot._process_input("Hello")
    assert response == "Echo: Hello"
    
    await bot.shutdown()
```

### 集成测试

```python
# tests/test_integration.py
import pytest
from app.bot.main import MoFoxBot

@pytest.mark.asyncio
async def test_end_to_end_flow():
    """端到端测试"""
    async with MoFoxBot(app_name="e2e_test") as bot:
        # 测试核心流程
        response1 = await bot._process_input("你好")
        assert response1 is not None
        
        response2 = await bot._process_input("再见")
        assert response2 is not None
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_bot.py

# 查看覆盖率
pytest --cov=app.bot --cov-report=html

# 详细输出
pytest -v -s
```

## 调试技巧

### 1. 使用日志调试

```python
# 在代码中添加详细日志
self.kernel.logger.debug(f"变量值: {variable}")
self.kernel.logger.info(f"执行到步骤 X")
```

### 2. 使用 pdb 调试

```python
import pdb

async def _process_input(self, user_input: str) -> str:
    pdb.set_trace()  # 断点
    # ... 代码
```

### 3. 使用 VS Code 调试器

创建 `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Start Bot",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/start.py",
      "console": "integratedTerminal",
      "justMyCode": true
    }
  ]
}
```

### 4. 性能分析

```python
import cProfile
import pstats

# 分析代码性能
cProfile.run('asyncio.run(main())', 'output.prof')

# 查看结果
stats = pstats.Stats('output.prof')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## 性能优化

### 1. 异步优化

```python
# 并发执行多个任务
async def parallel_processing(items):
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 缓存优化

```python
from functools import lru_cache

# 缓存函数结果
@lru_cache(maxsize=128)
def expensive_computation(arg):
    # 耗时计算
    return result
```

### 3. 数据库优化

```python
# 批量操作
await repo.bulk_create(items)

# 使用索引
# 在数据库模型中添加索引
```

### 4. 连接池

```python
# 使用连接池
# 在配置中设置
database:
  pool_size: 20
  max_overflow: 10
```

## 后续开发计划

### 短期目标（1-2周）

- [ ] **完善 Core API 实现**
  - 实现 PromptManager
  - 实现 TransportManager
  - 实现 PerceptionSystem

- [ ] **增强命令系统**
  - 添加更多内置命令
  - 实现命令自动补全
  - 添加命令历史记录

- [ ] **改进日志系统**
  - 修复 LogMetadata 错误
  - 添加日志过滤功能
  - 实现日志归档

### 中期目标（1个月）

- [ ] **插件系统**
  - 设计插件接口
  - 实现插件加载器
  - 提供插件示例

- [ ] **Web 界面**
  - 实现 REST API
  - 添加 WebSocket 支持
  - 创建简单的 Web UI

- [ ] **多模态支持**
  - 图像输入处理
  - 语音输入处理
  - 文件上传处理

### 长期目标（3个月+）

- [ ] **分布式部署**
  - 支持多实例运行
  - 实现负载均衡
  - 添加服务发现

- [ ] **监控和告警**
  - 实现性能监控
  - 添加告警系统
  - 创建监控面板

- [ ] **AI Agent 能力**
  - 实现 ReAct 模式
  - 支持工具调用
  - 多 Agent 协作

## 参考资料

- [Bot 架构设计](BOT_ARCHITECTURE.md)
- [API 使用指南](API_GUIDE.md)
- [启动器使用指南](LAUNCHER_GUIDE.md)
- [Core 层文档](../../core/README.md)
- [Kernel 层文档](../../kernel/README.md)

## 贡献代码

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 更新日志

- 2026-01-11: 初始版本，完成开发指南基础框架
