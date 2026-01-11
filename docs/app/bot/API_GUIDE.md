# MoFox API 使用指南

完整的 Core API 和 Kernel API 使用说明

## 📋 目录

- [Core API](#core-api)
- [Kernel API](#kernel-api)
- [集成使用](#集成使用)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

## Core API

Core API 提供 Core 层功能的统一访问接口。

### 快速开始

```python
from app.bot.core_api import MoFoxCore, get_core, create_core

# 方式 1: 直接创建
async with MoFoxCore(app_name="my_app") as core:
    # 使用 core
    pass

# 方式 2: 获取单例
core = get_core()
await core.initialize()

# 方式 3: 创建并初始化
core = await create_core(app_name="my_app")
```

### 提示词系统 (Prompt)

#### 功能说明

提示词系统负责管理和构建 AI 提示词模板。

#### API 接口

```python
# 访问提示词管理器
prompt_manager = core.prompt

# 构建提示词（计划中的功能）
prompt = await core.prompt.build(
    template_name="chat",
    user_message="你好",
    context="聊天场景"
)

# 注册自定义模板
core.prompt.register_template(
    name="greeting",
    template="你好，{name}！欢迎使用 {product}。"
)

# 使用模板
result = core.prompt.render("greeting", name="张三", product="MoFox")
```

#### 使用示例

```python
async def example_prompt():
    async with MoFoxCore() as core:
        # 示例 1: 简单模板
        prompt = await core.prompt.build(
            "simple_chat",
            message="今天天气怎么样？"
        )
        print(prompt)
        
        # 示例 2: 复杂模板
        prompt = await core.prompt.build(
            "system_prompt",
            role="助手",
            personality="友好、专业",
            constraints=["不要透露个人信息", "保持礼貌"]
        )
        print(prompt)
```

#### 最佳实践

1. **模板复用**: 将常用的提示词保存为模板
2. **参数化**: 使用参数而不是硬编码
3. **版本管理**: 为不同版本的模板命名

### 传输系统 (Transport)

#### 功能说明

传输系统处理数据传输和网络通信。

#### API 接口

```python
# 访问传输管理器
transport = core.transport

# 发送数据
response = await core.transport.send(
    data={"message": "hello"},
    transport_type="http",
    endpoint="https://api.example.com"
)

# 配置传输选项
core.transport.configure(
    timeout=30,
    retry=3,
    headers={"Authorization": "Bearer token"}
)
```

#### 使用示例

```python
async def example_transport():
    async with MoFoxCore() as core:
        # HTTP 请求
        response = await core.transport.send(
            data={"prompt": "你好"},
            transport_type="http",
            method="POST",
            url="https://api.openai.com/v1/chat"
        )
        
        # WebSocket 连接
        async with core.transport.connect(
            transport_type="websocket",
            url="ws://localhost:8080"
        ) as ws:
            await ws.send({"type": "message", "content": "hello"})
            response = await ws.receive()
```

### 感知系统 (Perception)

#### 功能说明

感知系统处理输入数据的理解和预处理。

#### API 接口

```python
# 访问感知系统
perception = core.perception

# 处理输入
result = await core.perception.process(
    input_data="用户输入的文本",
    input_type="text"
)

# 多模态输入
result = await core.perception.process(
    input_data={
        "text": "这是什么？",
        "image": image_data
    },
    input_type="multimodal"
)
```

### 组件系统 (Components)

#### 功能说明

组件系统管理可复用的功能组件。

#### API 接口

```python
# 注册组件
core.components.register("my_component", MyComponent())

# 获取组件
component = core.components.get("my_component")

# 列出所有组件
components = core.components.list_all()
```

### 模型系统 (Models)

#### 功能说明

模型系统管理数据模型和验证。

#### API 接口

```python
# 注册模型
from pydantic import BaseModel

class UserModel(BaseModel):
    name: str
    age: int

core.models.register("user", UserModel)

# 验证数据
user_data = {"name": "张三", "age": 25}
validated = core.models.validate("user", user_data)
```

### 便捷函数

```python
from app.bot.core_api import build_prompt, send_data

# 快速构建提示词
prompt = await build_prompt("template_name", param1="value1")

# 快速发送数据
response = await send_data(data, transport_type="http")
```

## Kernel API

Kernel API 提供 Kernel 层功能的统一访问接口。

### 快速开始

```python
from app.bot.kernel_api_legacy.kernel_api import MoFoxKernel

# 创建并初始化
async with MoFoxKernel(app_name="my_app") as kernel:
    # 使用 kernel
    pass
```

### 配置管理 (Config)

#### 功能说明

配置管理系统处理应用配置和环境变量。

#### API 接口

```python
# 访问配置
config = kernel.config

# 获取配置值
db_host = config.get("database.host", default="localhost")
api_key = config.get("api.key")

# 设置配置
config.set("custom.setting", "value")

# 加载配置文件
await kernel.load_config("config.yaml")
```

#### 使用示例

```python
async def example_config():
    async with MoFoxKernel() as kernel:
        # 获取数据库配置
        db_config = kernel.config.get("database")
        print(f"数据库: {db_config['host']}:{db_config['port']}")
        
        # 获取 API 密钥
        api_key = kernel.config.get("openai.api_key")
        
        # 动态更新配置
        kernel.config.set("temp.value", "临时设置")
```

#### 配置文件格式

```yaml
# config.yaml
database:
  host: localhost
  port: 5432
  name: mofox_db

openai:
  api_key: ${OPENAI_API_KEY}  # 环境变量
  model: gpt-4

logging:
  level: INFO
  dir: ./logs
```

### 数据库 (Database)

#### 功能说明

数据库系统提供 CRUD 操作和数据持久化。

#### API 接口

```python
# 创建仓库
from kernel.db import SQLAlchemyCRUDRepository

repo = kernel.create_repository(MyModel)

# CRUD 操作
# Create
user = await repo.create({"name": "张三", "age": 25})

# Read
user = await repo.get(user_id)
users = await repo.find({"age": {"$gt": 20}})

# Update
await repo.update(user_id, {"age": 26})

# Delete
await repo.delete(user_id)
```

#### 使用示例

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))

async def example_database():
    async with MoFoxKernel() as kernel:
        # 创建仓库
        user_repo = kernel.create_repository(User)
        
        # 创建用户
        user = await user_repo.create({
            "name": "张三",
            "email": "zhangsan@example.com"
        })
        
        # 查询用户
        users = await user_repo.find({"name": "张三"})
        
        # 更新用户
        await user_repo.update(user.id, {"email": "new@example.com"})
```

### LLM 接口

#### 功能说明

LLM 接口提供统一的大语言模型调用。

#### API 接口

```python
# 简单对话
response = await kernel.llm.chat("你好")

# 流式生成
async for chunk in kernel.llm.stream("讲个故事"):
    print(chunk, end="")

# 使用工具
from kernel.llm import ToolBuilder

tool = ToolBuilder()\
    .name("search")\
    .description("搜索信息")\
    .add_parameter("query", "string", "搜索关键词")\
    .build()

response = await kernel.llm.chat_with_tools(
    message="帮我搜索最新新闻",
    tools=[tool]
)
```

#### 使用示例

```python
async def example_llm():
    async with MoFoxKernel() as kernel:
        # 基本对话
        response = await kernel.llm.chat("你好，介绍一下你自己")
        print(f"AI: {response}")
        
        # 流式输出
        print("AI: ", end="")
        async for token in kernel.llm.stream("讲一个短故事"):
            print(token, end="", flush=True)
        print()
        
        # 多轮对话
        messages = [
            {"role": "user", "content": "我叫张三"},
            {"role": "assistant", "content": "你好张三！"},
            {"role": "user", "content": "我刚才说我叫什么？"}
        ]
        response = await kernel.llm.chat(messages)
        print(f"AI: {response}")
```

### 日志系统 (Logger)

#### 功能说明

日志系统提供结构化日志记录和存储。

#### API 接口

```python
# 基本日志
kernel.logger.debug("调试信息")
kernel.logger.info("普通信息")
kernel.logger.warning("警告信息")
kernel.logger.error("错误信息")
kernel.logger.critical("严重错误")

# 结构化日志
kernel.logger.info("用户登录", extra={
    "user_id": "12345",
    "ip": "192.168.1.1",
    "action": "login"
})

# 上下文日志
with kernel.logger.context(request_id="req-123"):
    kernel.logger.info("处理请求")
    # 所有日志会自动包含 request_id
```

#### 使用示例

```python
async def example_logger():
    async with MoFoxKernel() as kernel:
        # 记录应用启动
        kernel.logger.info("应用启动", extra={
            "version": "0.1.0",
            "environment": "production"
        })
        
        # 记录业务操作
        try:
            result = await process_data()
            kernel.logger.info("数据处理完成", extra={
                "records": len(result),
                "time": "1.5s"
            })
        except Exception as e:
            kernel.logger.error(f"处理失败: {e}", exc_info=True)
```

### 存储系统 (Storage)

#### 功能说明

存储系统提供文件和数据的持久化存储。

#### API 接口

```python
# JSON 存储
from kernel.storage import JSONStore

store = kernel.get_store("data", store_type="json")
store.save("key", {"data": "value"})
data = store.load("key")

# 列表存储
from kernel.storage import ListJSONStore

list_store = kernel.get_store("items", store_type="list")
list_store.append({"item": "value"})
items = list_store.load_all()
```

#### 使用示例

```python
async def example_storage():
    async with MoFoxKernel() as kernel:
        # 保存用户配置
        config_store = kernel.storage.get_store("user_config")
        config_store.save("user_123", {
            "theme": "dark",
            "language": "zh-CN"
        })
        
        # 保存对话历史
        history_store = kernel.storage.get_store("chat_history", store_type="list")
        history_store.append({
            "user": "你好",
            "assistant": "你好！有什么我可以帮助的吗？",
            "timestamp": "2026-01-11 10:00:00"
        })
```

### 向量数据库 (Vector DB)

#### 功能说明

向量数据库用于存储和检索向量嵌入。

#### API 接口

```python
# 创建向量数据库
vector_db = await kernel.create_vector_db(
    name="documents",
    embedding_function=embed_func
)

# 添加文档
await vector_db.add_documents([
    {"text": "文档内容1", "metadata": {"source": "file1"}},
    {"text": "文档内容2", "metadata": {"source": "file2"}}
])

# 相似度搜索
results = await vector_db.search(
    query="搜索关键词",
    top_k=5
)
```

#### 使用示例

```python
async def example_vector_db():
    async with MoFoxKernel() as kernel:
        # 创建知识库
        kb = await kernel.create_vector_db("knowledge_base")
        
        # 添加知识
        await kb.add_documents([
            {"text": "MoFox 是一个 AI 框架", "metadata": {"type": "intro"}},
            {"text": "支持多种 LLM", "metadata": {"type": "feature"}},
        ])
        
        # 搜索相关知识
        results = await kb.search("什么是 MoFox", top_k=3)
        for doc in results:
            print(f"- {doc['text']} (相似度: {doc['score']})")
```

### 任务管理器 (Task Manager)

#### 功能说明

任务管理器提供异步任务的创建、调度和监控。

#### API 接口

```python
# 创建任务
task = await kernel.task_manager.create_task(
    func=my_async_function,
    args=(arg1, arg2),
    priority="HIGH",
    timeout=30.0
)

# 等待任务完成
result = await task.wait()

# 获取任务状态
status = task.get_status()

# 取消任务
await task.cancel()

# 获取统计信息
stats = kernel.task_manager.get_stats()
```

#### 使用示例

```python
async def process_data(data_id: int):
    # 模拟数据处理
    await asyncio.sleep(2)
    return f"处理完成: {data_id}"

async def example_task_manager():
    async with MoFoxKernel() as kernel:
        # 创建多个任务
        tasks = []
        for i in range(10):
            task = await kernel.task_manager.create_task(
                func=process_data,
                args=(i,),
                priority="NORMAL"
            )
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*[t.wait() for t in tasks])
        print(f"完成 {len(results)} 个任务")
        
        # 查看统计
        stats = kernel.task_manager.get_stats()
        print(f"总任务数: {stats['total']}")
        print(f"完成任务: {stats['completed']}")
```

## 集成使用

### Core + Kernel 集成

```python
from app.bot.main import MoFoxBot

async def integrated_example():
    async with MoFoxBot(app_name="integrated_app") as bot:
        # 使用 Core API
        prompt = await bot.core.prompt.build("chat", message="你好")
        
        # 使用 Kernel API
        response = await bot.kernel.llm.chat(prompt)
        
        # 记录日志
        bot.kernel.logger.info("对话完成", extra={
            "prompt_length": len(prompt),
            "response_length": len(response)
        })
        
        # 保存对话历史
        history = bot.kernel.storage.get_store("chat_history", "list")
        history.append({
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
```

### 常见使用模式

#### 1. RAG (检索增强生成)

```python
async def rag_example(question: str):
    async with MoFoxBot() as bot:
        # 1. 向量搜索相关知识
        kb = await bot.kernel.create_vector_db("knowledge")
        docs = await kb.search(question, top_k=3)
        
        # 2. 构建提示词
        context = "\n".join([d['text'] for d in docs])
        prompt = await bot.core.prompt.build(
            "rag_template",
            question=question,
            context=context
        )
        
        # 3. 生成回答
        answer = await bot.kernel.llm.chat(prompt)
        
        return answer
```

#### 2. 多轮对话管理

```python
class ChatSession:
    def __init__(self, bot: MoFoxBot, user_id: str):
        self.bot = bot
        self.user_id = user_id
        self.history = []
    
    async def chat(self, message: str) -> str:
        # 加载历史
        history_store = self.bot.kernel.storage.get_store(
            f"chat_{self.user_id}",
            "list"
        )
        self.history = history_store.load_all()[-10:]  # 最近10轮
        
        # 构建完整上下文
        messages = []
        for h in self.history:
            messages.append({"role": "user", "content": h['user']})
            messages.append({"role": "assistant", "content": h['assistant']})
        messages.append({"role": "user", "content": message})
        
        # 生成回复
        response = await self.bot.kernel.llm.chat(messages)
        
        # 保存历史
        history_store.append({
            "user": message,
            "assistant": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
```

#### 3. 异步数据处理

```python
async def batch_processing(items: List[str]):
    async with MoFoxBot() as bot:
        # 创建处理任务
        async def process_item(item):
            result = await bot.kernel.llm.chat(f"分析: {item}")
            await bot.kernel.db.save_result(item, result)
            return result
        
        # 并发处理
        tasks = []
        for item in items:
            task = await bot.kernel.task_manager.create_task(
                func=process_item,
                args=(item,)
            )
            tasks.append(task)
        
        # 等待完成
        results = await asyncio.gather(*[t.wait() for t in tasks])
        
        # 统计
        bot.kernel.logger.info(f"批处理完成: {len(results)} 项")
        return results
```

## 最佳实践

### 1. 资源管理

**使用上下文管理器**
```python
# ✅ 好的做法
async with MoFoxBot() as bot:
    result = await bot.process()
# 自动清理资源

# ❌ 不好的做法
bot = MoFoxBot()
await bot.initialize()
result = await bot.process()
# 忘记调用 shutdown()
```

### 2. 错误处理

```python
async def robust_example():
    async with MoFoxBot() as bot:
        try:
            response = await bot.kernel.llm.chat("你好")
        except TimeoutError:
            bot.kernel.logger.warning("LLM 调用超时")
            response = "抱歉，响应超时"
        except Exception as e:
            bot.kernel.logger.error(f"处理失败: {e}", exc_info=True)
            response = "抱歉，处理出错了"
        
        return response
```

### 3. 配置管理

```python
# 使用环境变量
import os
os.environ['OPENAI_API_KEY'] = 'your-key'

# 或使用配置文件
async with MoFoxKernel(config_path="config.yaml") as kernel:
    api_key = kernel.config.get("openai.api_key")
```

### 4. 日志记录

```python
# 使用结构化日志
bot.kernel.logger.info("处理请求", extra={
    "user_id": user_id,
    "action": "chat",
    "duration": duration
})

# 不要记录敏感信息
bot.kernel.logger.info("用户登录", extra={
    "user_id": user_id,
    # ❌ "password": password  # 永远不要记录密码
})
```

### 5. 性能优化

```python
# 并发请求
async def parallel_requests(queries: List[str]):
    async with MoFoxBot() as bot:
        tasks = [bot.kernel.llm.chat(q) for q in queries]
        results = await asyncio.gather(*tasks)
        return results
```

## 常见问题

### Q1: 如何选择使用 Core API 还是 Kernel API？

**A**: 
- 使用 **Core API** 处理业务逻辑层面的功能（提示词、感知、传输等）
- 使用 **Kernel API** 处理基础设施层面的功能（数据库、日志、配置等）
- 大多数情况下，两者结合使用

### Q2: 可以同时创建多个 API 实例吗？

**A**: 可以，但建议使用单例模式：
```python
# 推荐
core = get_core()
kernel = get_kernel()

# 或在 MoFoxBot 中使用
bot = MoFoxBot()  # 自动管理两个 API 实例
```

### Q3: 如何处理 LLM 调用超时？

**A**:
```python
import asyncio

try:
    response = await asyncio.wait_for(
        bot.kernel.llm.chat("你好"),
        timeout=30.0
    )
except asyncio.TimeoutError:
    response = "请求超时"
```

### Q4: 如何实现流式输出？

**A**:
```python
async for chunk in bot.kernel.llm.stream("讲个故事"):
    print(chunk, end="", flush=True)
```

### Q5: 如何切换不同的 LLM 提供商？

**A**:
```python
# 在配置中设置
config = {
    "llm": {
        "provider": "openai",  # 或 "anthropic", "gemini"
        "model": "gpt-4"
    }
}

bot = MoFoxBot(config=config)
```

## 下一步

- 阅读[启动器使用指南](LAUNCHER_GUIDE.md)
- 查看[开发指南](DEVELOPMENT_GUIDE.md)了解如何扩展功能
- 参考[架构设计](BOT_ARCHITECTURE.md)深入理解系统设计

## 更新日志

- 2026-01-11: 初始版本，完成 API 基础文档
