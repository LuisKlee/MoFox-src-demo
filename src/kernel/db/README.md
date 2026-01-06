# 数据库内核说明

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
