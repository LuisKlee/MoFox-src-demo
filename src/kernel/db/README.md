# 数据库内核说明

## 特性

- 🗄️ **多数据库支持**：SQLite、MySQL、PostgreSQL、Redis、MongoDB
- 🔄 **事务管理**：自动提交/回滚，异常安全
- 📦 **CRUD 封装**：简洁的增删改查接口
- 🔍 **查询规约**：统一的过滤、排序、分页
- 🎯 **仓库模式**：针对不同数据库的专用仓库
- 📝 **日志集成**：与 Logger 模块深度集成，自动记录所有数据库操作
- ⚡ **性能监控**：记录查询时长、事务状态、操作统计

## 目录结构
- core/：数据库引擎与会话管理
  - dialect_adapter.py：方言适配器接口与 SQLite、MySQL、PostgreSQL、Redis、MongoDB 实现
  - engine.py：引擎注册与创建
  - session.py：会话管理器（事务作用域）
  - exceptions.py：数据库相关异常
- api/：对外 CRUD / 查询接口
  - crud.py：CRUD 抽象与 SQLAlchemy 实现
  - query.py：查询规约（QuerySpec）与应用器

## 当前能力
- 支持 SQLite 引擎创建（文件或内存模式），自动创建目录。
- 支持 MySQL 引擎创建（使用 pymysql 驱动）。
- 支持 PostgreSQL 引擎创建（使用 psycopg2 驱动）。
- 支持 Redis 连接（使用 redis-py）。
- 支持 MongoDB 连接（使用 pymongo）。
- 通过 EngineManager 按名称管理多个引擎，可扩展其他方言适配器。
- SessionManager 提供事务作用域，自动提交/回滚与关闭。
- SQLAlchemyCRUDRepository 封装常用增删改查，接受 QuerySpec 以复用过滤/排序/分页。

## 快速使用示例

### SQLite 示例（同步 SQLAlchemy）
```python
from kernel.db.core import EngineManager, EngineConfig, SessionManager
from kernel.db.api import SQLAlchemyCRUDRepository, QuerySpec

engine = EngineManager().create(EngineConfig(dialect="sqlite", database="data/app.db"))
session_mgr = SessionManager(engine)
repo = SQLAlchemyCRUDRepository(session_mgr)

with repo.session_scope() as session:
    obj = repo.add(session, MyModel(name="demo"), flush=True)
    rows = repo.list(session, MyModel, QuerySpec(limit=10))
```

### MySQL 示例
```python
from kernel.db.core import create_mysql_engine, SessionManager
from kernel.db.api import SQLAlchemyCRUDRepository

# 方式1：使用便捷函数
engine = create_mysql_engine(
    database="myapp",
    username="root",
    password="password123",
    host="localhost",
    port=3306,
)

# 方式2：使用 EngineConfig
from kernel.db.core import EngineManager, EngineConfig

engine = EngineManager().create(EngineConfig(
    dialect="mysql",
    database="myapp",
    username="root",
    password="password123",
    host="localhost",
    port=3306,
    pool_size=10,
))

session_mgr = SessionManager(engine)
repo = SQLAlchemyCRUDRepository(session_mgr)

with repo.session_scope() as session:
    user = repo.add(session, User(name="Alice"), flush=True)
    users = repo.list(session, User, QuerySpec(limit=20))
```

### PostgreSQL 示例
```python
from kernel.db.core import create_postgres_engine, SessionManager
from kernel.db.api import SQLAlchemyCRUDRepository

# 方式1：使用便捷函数
engine = create_postgres_engine(
    database="mofox",
    username="postgres",
    password="password123",
    host="localhost",
    port=5432,
)

# 方式2：使用 EngineConfig
from kernel.db.core import EngineManager, EngineConfig

engine = EngineManager().create(EngineConfig(
    dialect="postgresql",
    database="mofox",
    username="postgres",
    password="password123",
    pool_size=20,
))

session_mgr = SessionManager(engine)
repo = SQLAlchemyCRUDRepository(session_mgr)

with repo.session_scope() as session:
    user = repo.add(session, User(name="Bob"), flush=True)
```

### Redis 示例
```python
from kernel.db.core import create_redis_engine
from kernel.db.api import RedisRepository

# Redis 返回的是 redis.Redis 客户端，而不是 SQLAlchemy 引擎
redis_client = create_redis_engine(
    database="0",  # Redis 数据库索引 (0-15)
    host="localhost",
    port=6379,
    password="redis_password",  # 可选
)

# 使用 RedisRepository 封装常用操作
repo = RedisRepository(redis_client)

# String 操作
repo.set("user:1001:name", "Alice", ex=3600)  # 1小时后过期
name = repo.get("user:1001:name")

# Hash 操作 - 存储用户信息
repo.hset("user:1001", mapping={"name": "Alice", "age": "25", "city": "Beijing"})
user_data = repo.hgetall("user:1001")

# List 操作 - 消息队列
repo.lpush("task_queue", "task1", "task2", "task3")
task = repo.rpop("task_queue")

# Set 操作 - 标签
repo.sadd("user:1001:tags", "python", "ai", "backend")
tags = repo.smembers("user:1001:tags")

# Sorted Set 操作 - 排行榜
repo.zadd("leaderboard", {"user1": 100, "user2": 200, "user3": 150})
top_users = repo.zrange("leaderboard", 0, 9, withscores=True)

# 缓存 LLM 响应
repo.set("llm:response:123", "cached response", ex=3600)

# 直接访问底层客户端进行高级操作
repo.client.pipeline()  # 管道操作
```

### MongoDB 示例
```python
from kernel.db.core import create_mongodb_engine
from kernel.db.api import MongoDBRepository, QuerySpec

# MongoDB 返回的是 MongoDBEngine 封装器
mongo_engine = create_mongodb_engine(
    database="mofox_knowledge",
    username="admin",
    password="password123",
    host="localhost",
    port=27017,
)

# 使用 MongoDBRepository 封装常用操作
repo = MongoDBRepository(mongo_engine)

# 插入文档
result = repo.insert_one("conversations", {
    "user_id": "user123",
    "message": "Hello, AI!",
    "timestamp": "2026-01-06T10:00:00Z",
    "metadata": {"model": "gpt-4", "tokens": 150}
})

# 批量插入
repo.insert_many("conversations", [
    {"user_id": "user123", "message": "Question 1"},
    {"user_id": "user123", "message": "Question 2"},
])

# 查询单个文档
doc = repo.find_one("conversations", {"user_id": "user123"})

# 使用 QuerySpec 查询多个文档
results = repo.find(
    "conversations",
    {"user_id": "user123"},
    QuerySpec(
        order_by=[("timestamp", -1)],  # 按时间倒序
        limit=10,
        offset=0
    )
)

# 更新文档
repo.update_one(
    "conversations",
    {"user_id": "user123"},
    {"$set": {"status": "archived"}}
)

# 批量更新
repo.update_many(
    "conversations",
    {"user_id": "user123"},
    {"$set": {"reviewed": True}}
)

# 删除文档
repo.delete_one("conversations", {"_id": result.inserted_id})

# 统计文档数量
count = repo.count_documents("conversations", {"user_id": "user123"})

# 聚合查询
pipeline = [
    {"$match": {"user_id": "user123"}},
    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
]
stats = repo.aggregate("conversations", pipeline)

# 创建索引
repo.create_index("conversations", [("user_id", 1), ("timestamp", -1)])

# 直接访问集合进行高级操作
collection = repo.collection("conversations")
collection.create_index([("message", "text")])  # 全文索引

# 关闭连接
mongo_engine.dispose()
```

## 日志集成

数据库模块已与 Logger 模块深度集成，所有数据库操作都会自动记录。

### 自动记录的操作

**会话管理**
- ✅ 会话创建：记录会话ID
- ✅ 事务提交：记录执行时长、状态
- ✅ 事务回滚：记录错误信息、堆栈跟踪
- ✅ 会话关闭：记录会话生命周期

**CRUD 操作**
- ✅ 添加记录：记录模型名称、是否 flush
- ✅ 查询记录：记录模型名称、查询条件、结果数量
- ✅ 更新记录：记录更新的字段、字段数量
- ✅ 删除记录：记录删除的模型

**Redis 操作**
- ✅ SET/GET：记录键名、是否找到、过期时间
- ✅ DELETE：记录删除的键列表、删除数量
- ✅ Hash/List/Set 操作：记录操作类型、键名

**MongoDB 操作**
- ✅ 插入文档：记录集合名、文档数量、插入ID
- ✅ 查询文档：记录集合名、过滤条件、结果数量
- ✅ 更新文档：记录匹配数、修改数、是否 upsert
- ✅ 删除文档：记录删除数量

### 日志元数据

每条数据库操作日志都包含：

```python
{
    "session_id": "session_123456",
    "operation": "add",
    "model": "User",
    "duration": 0.123,
    "status": "committed",
    "level": "INFO",
    "timestamp": "2026-01-06T10:30:45"
}
```

### 使用日志集成

#### 方式 1：使用 Logger-Storage 集成（推荐）

```python
from kernel.logger.storage_integration import LoggerWithStorage

# 初始化日志系统
logger_system = LoggerWithStorage(app_name="myapp")

# 使用数据库
from kernel.db.core import create_sqlite_engine, SessionManager
from kernel.db.api import SQLAlchemyCRUDRepository

engine = create_sqlite_engine("data/app.db")
session_mgr = SessionManager(engine)
repo = SQLAlchemyCRUDRepository(session_mgr)

with repo.session_scope() as session:
    # 所有操作自动记录日志
    user = repo.add(session, User(name="Alice"), flush=True)
    users = repo.list(session, User)

# 查询数据库操作日志
db_logs = logger_system.log_store.get_logs(
    filter_func=lambda log: 'session_id' in log
)

# 分析慢查询
slow_queries = [
    log for log in db_logs
    if log.get('duration', 0) > 1.0  # 超过1秒
]
```

#### 方式 2：仅使用标准 Logger

```python
from kernel.logger import setup_logger

# 初始化标准 Logger（控制台 + 文件）
setup_logger()

# 使用数据库（自动记录到日志）
with repo.session_scope() as session:
    user = repo.add(session, User(name="Bob"), flush=True)
```

### 查询数据库日志

```python
from datetime import datetime, timedelta

# 查询最近1小时的数据库操作
recent_logs = logger_system.log_store.get_logs(
    start_date=datetime.now() - timedelta(hours=1),
    filter_func=lambda log: log.get('operation') in ['add', 'update', 'delete']
)

# 按操作类型分组统计
from collections import Counter

operation_stats = Counter(
    log.get('operation') for log in recent_logs
)
print(f"添加: {operation_stats['add']}次")
print(f"更新: {operation_stats['update']}次")
print(f"删除: {operation_stats['delete']}次")
```

### 错误追踪

```python
# 查询数据库错误
error_logs = logger_system.get_error_logs(days=1)

db_errors = [
    log for log in error_logs
    if 'session_id' in log or log.get('operation')
]

for error in db_errors:
    print(f"时间: {error['timestamp']}")
    print(f"操作: {error.get('operation', 'unknown')}")
    print(f"错误: {error.get('error_message', '')}")
    print("---")
```

### 性能分析

```python
# 分析事务执行时长
transactions = logger_system.log_store.get_logs(
    filter_func=lambda log: log.get('status') == 'committed'
)

durations = [log['duration'] for log in transactions if 'duration' in log]

if durations:
    avg_duration = sum(durations) / len(durations)
    max_duration = max(durations)
    
    print(f"平均事务时长: {avg_duration:.3f}秒")
    print(f"最长事务时长: {max_duration:.3f}秒")
    print(f"总事务数: {len(durations)}")
```

### 审计日志

```python
from kernel.logger import MetadataContext

# 记录用户操作的数据库变更
with MetadataContext(user_id="user123", action="update_profile"):
    with repo.session_scope() as session:
        user = repo.get(session, User, user_id)
        repo.update_fields(session, user, {"email": "new@example.com"})

# 查询特定用户的数据库操作
user_operations = logger_system.log_store.get_logs(
    filter_func=lambda log: log.get('user_id') == 'user123'
)
```

## 扩展指引
- 新增数据库方言：实现 DialectAdapter，在 EngineManager.register_adapter 注册。
- 自定义 CRUD：继承 CRUDRepository，替换 SQLAlchemy 实现，或封装异步版本。
- 查询扩展：在 QuerySpec 中增加字段，并在 apply_query_spec 内映射到后端查询表达式。

## 数据库选择指南
- **SQLite**：本地开发、小型项目、嵌入式应用
- **MySQL**：Web 应用、中等规模、需要主从复制
- **PostgreSQL**：复杂查询、数据完整性、高级特性 (JSON/GIS)
- **Redis**：缓存、会话存储、消息队列、实时数据
- **MongoDB**：文档存储、日志、非结构化数据、快速原型

## TODO
- 提供异步会话/CRUD 版本（asyncpg、aiomysql、motor、aioredis）
- 集成迁移与健康检查工具
- 添加连接池监控与性能指标
- 支持数据库读写分离配置

## 相关文档

- 📖 [Logger 模块文档](../logger/README.md)
- 📖 [Logger-Storage 集成指南](../../docs/kernel/logger/LOGGER_STORAGE_INTEGRATION.md)
- 🚀 [Logger 快速参考](../../docs/kernel/logger/QUICK_REFERENCE.md)
- 📖 [Storage 模块文档](../storage/README.md)
- 📖 [数据库优化指南](../../docs/kernel/db/OPTIMIZATION_GUIDE.md)
- 📖 [数据库缓存指南](../../docs/kernel/db/CACHE_GUIDE.md)
