# MoFox Kernel API 使用文档

## 概述

`kernel_api.py` 提供了 MoFox Kernel 层的统一高级封装接口，将所有核心功能（配置、日志、数据库、LLM、存储、向量数据库、任务管理）整合到一个简洁易用的 API 中。

## 核心特性

✅ **统一接口** - 一个类管理所有 Kernel 功能  
✅ **自动初始化** - 智能初始化各个子模块  
✅ **资源管理** - 自动管理生命周期和资源释放  
✅ **简洁 API** - 提供高层次的便捷方法  
✅ **类型提示** - 完整的类型注解支持  
✅ **异步优先** - 原生支持 async/await  

## 快速开始

### 基础使用

```python
from src.app.bot.kernel_api import init_kernel, shutdown_kernel

async def main():
    # 初始化 kernel
    kernel = await init_kernel(
        app_name="my_app",
        log_dir="logs",
        data_dir="data"
    )
    
    # 使用日志
    kernel.logger.info("应用已启动")
    
    # 使用配置
    kernel.set_config("debug", True)
    debug = kernel.get_config("debug")
    
    # 关闭 kernel
    await shutdown_kernel()

import asyncio
asyncio.run(main())
```

### 完整示例

```python
from src.app.bot.kernel_api import MoFoxKernel

async def main():
    # 创建 kernel 实例
    kernel = MoFoxKernel(
        app_name="advanced_app",
        config_path="config.json",  # 可选
        log_dir="logs",
        data_dir="data",
        max_concurrent_tasks=20  # 其他配置
    )
    
    # 初始化所有组件
    await kernel.initialize()
    
    try:
        # 你的应用逻辑
        kernel.logger.info("应用运行中...")
        
    finally:
        # 清理资源
        await kernel.shutdown()

asyncio.run(main())
```

## 功能模块

### 1. 配置管理

```python
# 设置配置
kernel.set_config("api_key", "your-key")
kernel.set_config("database.host", "localhost")

# 获取配置
api_key = kernel.get_config("api_key")
host = kernel.get_config("database.host", "default_host")

# 访问底层配置对象
config = kernel.config
value = config.get("nested.key.path")
```

### 2. 日志管理

```python
# 获取默认日志器
kernel.logger.info("信息日志")
kernel.logger.warning("警告日志")
kernel.logger.error("错误日志")

# 获取命名日志器
module_logger = kernel.get_logger("app.module")
module_logger.debug("模块日志")

# 查询日志统计
stats = kernel.get_logs(days=7)
# {'total': 100, 'by_level': {...}, 'by_logger': {...}}

# 查询错误日志
errors = kernel.get_error_logs(days=1)
for error in errors:
    print(f"{error['timestamp']}: {error['message']}")
```

### 3. LLM 功能

```python
# 简单聊天
response = await kernel.llm.chat(
    "用一句话介绍 Python",
    model="gpt-4",
    provider="openai"
)
print(response)

# 流式聊天
async for chunk in kernel.llm.chat_stream(
    "讲个故事",
    model="gpt-4"
):
    print(chunk, end="", flush=True)

# 使用系统提示词
system_prompt = kernel.llm.get_system_prompt("coding")
response = await kernel.llm.chat(
    "如何读取文件？",
    system_prompt=system_prompt
)

# 工具调用
tool = kernel.llm.create_tool(
    name="get_weather",
    description="获取天气信息",
    parameters=[
        {
            "name": "city",
            "type": "string",
            "description": "城市名称",
            "required": True
        }
    ]
)

response = await kernel.llm.chat_with_tools(
    "北京天气如何？",
    tools=[tool]
)

if response.tool_calls:
    for call in response.tool_calls:
        print(f"调用工具: {call['function']['name']}")
        print(f"参数: {call['function']['arguments']}")

# 创建多模态消息
message = kernel.llm.create_message(
    "这是什么？",
    images=["image.jpg"]
)
```

### 4. 数据库操作

```python
# 初始化数据库
await kernel.init_database(
    db_path="data/app.db",
    enable_wal=True,
    pool_size=20
)

# 使用会话
async with kernel.db_session() as session:
    # CRUD 操作
    user = User(name="Alice", age=25)
    kernel.db.add(session, user, flush=True)
    
    # 查询
    users = kernel.db.list(session, User)
    user = kernel.db.get(session, User, user_id)
    
    # 更新
    kernel.db.update_fields(session, user, {"age": 26})
    
    # 删除
    kernel.db.delete(session, user)

# 直接访问数据库仓库
repo = kernel.db
```

### 5. 存储操作

```python
# 快速保存/加载
kernel.storage.save("config", {"version": "1.0"})
config = kernel.storage.load("config", default={})

# JSON 存储器
json_store = kernel.storage.json_store("settings")
json_store.write({"key": "value"})
data = json_store.read()

# 字典存储器
dict_store = kernel.storage.dict_store("users")
dict_store.set("user1", {"name": "Alice"})
dict_store.set("user2", {"name": "Bob"})
user = dict_store.get("user1")
all_users = dict_store.to_dict()

# 列表存储器
list_store = kernel.storage.list_store("events")
list_store.append({"type": "login", "user": "Alice"})
list_store.extend([event1, event2])
events = list_store.to_list()
count = list_store.count()

# 日志存储器
log_store = kernel.storage.log_store("app_logs")
log_store.log("info", "Application started")
log_store.log("error", "Error occurred", {"code": 500})
logs = log_store.get_logs()
```

### 6. 向量数据库

```python
# 初始化向量数据库
await kernel.init_vector_db(
    db_type="chromadb",
    persist_dir="data/vectors"
)

# 创建集合
await kernel.vector_db.create_collection("documents")

# 添加文档
from src.app.bot.kernel_api import VectorDocument

docs = [
    VectorDocument(
        id="doc1",
        content="Python 编程语言",
        vector=[0.1, 0.2, 0.3],
        metadata={"category": "tech"}
    )
]
await kernel.vector_db.add_documents("documents", docs)

# 向量搜索（使用向量）
results = await kernel.vector_search(
    collection="documents",
    query=[0.15, 0.25, 0.35],
    top_k=5
)

# 文本搜索（需要嵌入函数）
results = await kernel.vector_search(
    collection="documents",
    query="Python 编程",
    top_k=5
)

# 管理集合
collections = await kernel.vector_db.list_collections()
exists = await kernel.vector_db.collection_exists("documents")
count = await kernel.vector_db.count_documents("documents")
await kernel.vector_db.delete_collection("documents")
```

### 7. 任务管理

```python
# 定义异步任务
async def process_data(data):
    await asyncio.sleep(1)
    return data * 2

# 运行单个任务
result = await kernel.run_task(
    process_data,
    42,
    priority=TaskPriority.HIGH,
    name="process_task"
)

# 并行运行多个任务
tasks = [
    (process_data, (10,)),
    (process_data, (20,)),
    (process_data, (30,))
]
results = await kernel.run_tasks_parallel(tasks)
# [20, 40, 60]

# 使用任务管理器
task_id = kernel.tasks.submit_task(
    process_data,
    100,
    name="my_task",
    config=TaskConfig(priority=TaskPriority.HIGH)
)

# 等待任务完成
result = await kernel.tasks.wait_for_task(task_id)

# 查询任务状态
status = kernel.tasks.get_task_status(task_id)

# 取消任务
kernel.tasks.cancel_task(task_id)

# 获取所有任务
all_tasks = kernel.tasks.get_all_tasks()
```

## 高级用法

### 上下文管理器

```python
from src.app.bot.kernel_api import MoFoxKernel

async def main():
    kernel = MoFoxKernel(app_name="context_app")
    await kernel.initialize()
    
    try:
        # 数据库会话
        async with kernel.db_session() as session:
            # 数据库操作
            pass
        
        # 日志元数据上下文
        from src.app.bot.kernel_api import MetadataContext
        with MetadataContext(user_id="123", request_id="req_456"):
            kernel.logger.info("带元数据的日志")
    
    finally:
        await kernel.shutdown()
```

### 组合使用

```python
async def intelligent_qa_system():
    """智能问答系统示例"""
    kernel = await init_kernel(app_name="qa_system")
    
    # 初始化所有组件
    await kernel.init_database("data/qa.db")
    await kernel.init_vector_db(persist_dir="data/vectors")
    
    # 1. 存储问答知识库
    qa_store = kernel.storage.dict_store("knowledge")
    qa_store.set("python", {
        "question": "什么是 Python？",
        "answer": "Python 是一种编程语言"
    })
    
    # 2. 将知识存入向量数据库（用于语义搜索）
    await kernel.vector_db.create_collection("qa_vectors")
    doc = VectorDocument(
        id="q1",
        content="什么是 Python？Python 是一种编程语言",
        vector=[0.1, 0.2, 0.3],  # 实际应使用嵌入模型
        metadata={"type": "qa"}
    )
    await kernel.vector_db.add_documents("qa_vectors", [doc])
    
    # 3. 用户提问
    user_question = "Python 是什么？"
    kernel.logger.info(f"用户提问: {user_question}")
    
    # 4. 语义搜索找到相关问题
    similar_docs = await kernel.vector_search(
        collection="qa_vectors",
        query=user_question,  # 或使用嵌入向量
        top_k=3
    )
    
    # 5. 使用 LLM 生成答案
    context = "\n".join([doc.content for doc in similar_docs])
    prompt = f"基于以下上下文回答问题:\n{context}\n\n问题: {user_question}"
    
    answer = await kernel.llm.chat(
        prompt,
        system_prompt=kernel.llm.get_system_prompt("education")
    )
    
    # 6. 记录问答历史
    history = kernel.storage.list_store("qa_history")
    history.append({
        "question": user_question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    })
    
    kernel.logger.info(f"回答: {answer}")
    
    await shutdown_kernel()
    return answer
```

### 并发任务处理

```python
async def batch_processing():
    """批量数据处理示例"""
    kernel = await init_kernel(app_name="batch_processor")
    
    # 定义处理任务
    async def process_item(item_id):
        # 从存储获取数据
        store = kernel.storage.dict_store("items")
        item = store.get(item_id)
        
        # 使用 LLM 处理
        result = await kernel.llm.chat(
            f"分析这个数据: {item}",
            model="gpt-4"
        )
        
        # 保存结果
        result_store = kernel.storage.dict_store("results")
        result_store.set(item_id, result)
        
        kernel.logger.info(f"处理完成: {item_id}")
        return result
    
    # 批量并行处理
    item_ids = [f"item_{i}" for i in range(10)]
    tasks = [(process_item, (item_id,)) for item_id in item_ids]
    
    results = await kernel.run_tasks_parallel(tasks)
    
    kernel.logger.info(f"批量处理完成，共 {len(results)} 项")
    
    await shutdown_kernel()
```

## API 参考

### MoFoxKernel 类

| 方法/属性 | 说明 |
|----------|------|
| `__init__(app_name, config_path, log_dir, data_dir, **kwargs)` | 创建 Kernel 实例 |
| `async initialize()` | 初始化所有组件 |
| `async shutdown()` | 关闭并清理资源 |
| `config` | 配置管理器 |
| `logger` | 默认日志器 |
| `llm` | LLM 接口 |
| `storage` | 存储接口 |
| `db` | 数据库仓库 |
| `vector_db` | 向量数据库 |
| `tasks` | 任务管理器 |

### 便捷函数

| 函数 | 说明 |
|------|------|
| `get_kernel(app_name, **kwargs)` | 获取全局 Kernel 单例 |
| `init_kernel(app_name, **kwargs)` | 初始化并获取全局 Kernel |
| `shutdown_kernel()` | 关闭全局 Kernel |

## 配置选项

### Kernel 初始化参数

```python
kernel = MoFoxKernel(
    app_name="my_app",              # 应用名称
    config_path="config.json",      # 配置文件路径（可选）
    log_dir="logs",                 # 日志目录
    data_dir="data",                # 数据目录
    max_concurrent_tasks=10,        # 最大并发任务数
    # 其他自定义配置...
)
```

### 数据库初始化参数

```python
await kernel.init_database(
    db_path="data/app.db",          # 数据库路径
    pool_size=20,                   # 连接池大小
    pool_timeout=60,                # 超时时间
    enable_wal=True,                # WAL 模式
    enable_foreign_keys=True        # 外键约束
)
```

### 向量数据库初始化参数

```python
await kernel.init_vector_db(
    db_type="chromadb",             # 数据库类型
    persist_dir="data/vectors",     # 持久化目录
    # 其他数据库特定参数...
)
```

## 最佳实践

### 1. 资源管理

```python
# ✅ 推荐：使用 init_kernel 和 shutdown_kernel
async def main():
    kernel = await init_kernel("my_app")
    try:
        # 应用逻辑
        pass
    finally:
        await shutdown_kernel()

# ✅ 推荐：显式初始化和关闭
async def main():
    kernel = MoFoxKernel("my_app")
    await kernel.initialize()
    try:
        # 应用逻辑
        pass
    finally:
        await kernel.shutdown()
```

### 2. 日志记录

```python
# ✅ 推荐：为不同模块使用不同的日志器
class MyModule:
    def __init__(self, kernel):
        self.logger = kernel.get_logger("app.mymodule")
    
    async def process(self):
        self.logger.info("开始处理")
        # ...
        self.logger.info("处理完成")
```

### 3. 错误处理

```python
# ✅ 推荐：使用 try-except 处理异常
try:
    result = await kernel.llm.chat("问题")
except Exception as e:
    kernel.logger.error(f"LLM 调用失败: {e}")
    # 降级处理
```

### 4. 存储组织

```python
# ✅ 推荐：为不同类型的数据使用不同的存储器
config_store = kernel.storage.dict_store("config")
users_store = kernel.storage.dict_store("users")
events_store = kernel.storage.list_store("events")
logs_store = kernel.storage.log_store("app_logs")
```

## 常见问题

### Q: 如何配置 LLM API 密钥？

```python
# 方式 1：环境变量
import os
os.environ["OPENAI_API_KEY"] = "your-key"

# 方式 2：配置文件
kernel.set_config("openai.api_key", "your-key")

# 方式 3：直接传递
response = await kernel.llm.chat(
    "问题",
    api_key="your-key"
)
```

### Q: 如何处理并发限制？

```python
# 设置最大并发任务数
kernel = MoFoxKernel(
    app_name="my_app",
    max_concurrent_tasks=5  # 最多同时运行 5 个任务
)
```

### Q: 如何持久化向量数据库？

```python
# 使用 persist_dir 参数
await kernel.init_vector_db(
    db_type="chromadb",
    persist_dir="data/persistent_vectors"
)
```

### Q: 如何查看任务执行状态？

```python
# 提交任务
task_id = kernel.tasks.submit_task(my_func, arg)

# 查看状态
status = kernel.tasks.get_task_status(task_id)
print(f"状态: {status.state}")  # PENDING, RUNNING, COMPLETED, FAILED

# 获取所有任务
all_tasks = kernel.tasks.get_all_tasks()
for task in all_tasks:
    print(f"{task.name}: {task.state}")
```

## 示例代码

完整示例请查看：[examples/kernel_api_demo.py](../../examples/kernel_api_demo.py)

## 相关文档

- [Config 模块](../../docs/kernel/config/README.md)
- [Database 模块](../../docs/kernel/db/README.md)
- [LLM 模块](../../docs/kernel/llm/README.md)
- [Logger 模块](../../docs/kernel/logger/README.md)
- [Storage 模块](../../docs/kernel/storage/README.md)
- [Vector DB 模块](../../docs/kernel/vector_db/README.md)
- [Concurrency 模块](../../docs/kernel/concurrency/README.md)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
