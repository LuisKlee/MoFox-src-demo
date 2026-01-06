# 数据库内核模块（Database Kernel Module）

## 概述（Overview）

MoFox 数据库内核是一个高效的多数据库支持系统，提供统一的接口来访问不同的数据库后端，包括 SQLite、MySQL、PostgreSQL、Redis 和 MongoDB。该模块采用方言适配器模式，使开发者可以轻松切换数据库，而无需修改应用代码。

The MoFox Database Kernel is a comprehensive multi-database system that provides a unified interface for accessing different database backends including SQLite, MySQL, PostgreSQL, Redis, and MongoDB. Using the Dialect Adapter pattern, developers can easily switch databases without modifying application code.

---

## 核心特性（Key Features）

| 特性 | 说明 |
|------|------|
| **多数据库支持** | SQLite、MySQL、PostgreSQL、Redis、MongoDB |
| **统一接口** | 通过 Repository 模式提供一致的 CRUD 操作 |
| **引擎管理** | EngineManager 中央管理多个数据库引擎 |
| **方言适配** | 方言适配器模式支持灵活扩展新数据库 |
| **缓存系统** | 内置 LocalCache（本地）和 RedisCache（分布式）支持 |
| **会话管理** | SessionManager 自动处理事务和资源释放 |
| **查询规约** | QuerySpec 支持跨数据库统一查询接口 |
| **线程安全** | LocalCache 使用锁机制保证并发安全 |
| **完整本地化** | 中英文双语注释和文档 |

---

## 目录结构（Directory Structure）

```
src/kernel/db/
├── core/                          # 核心引擎与会话管理
│   ├── __init__.py
│   ├── dialect_adapter.py         # 方言适配器（4 个 SQL + 2 个 NoSQL）
│   ├── engine.py                  # 引擎管理器与工厂函数
│   ├── session.py                 # 会话和事务管理
│   └── exceptions.py              # 自定义异常
├── api/                           # 对外 API 接口
│   ├── __init__.py
│   ├── crud.py                    # CRUD 抽象与具体实现
│   └── query.py                   # 查询规约（QuerySpec）
├── optimization/                  # 缓存和优化
│   ├── __init__.py
│   ├── cache_manager.py           # 统一缓存管理器与装饰器
│   └── backends/
│       ├── __init__.py
│       ├── cache_backend.py       # 缓存后端抽象接口
│       ├── local_cache.py         # 本地内存缓存（LRU + TTL）
│       └── redis_cache.py         # Redis 分布式缓存
├── db/
│   ├── __init__.py
│   ├── api/                       # 数据库 API 层
│   ├── core/                      # 数据库核心层
│   └── optimization/              # 优化层（缓存）
└── README.md                      # 本文件
```

---

## 快速开始（Quick Start）

### 1. SQLite - 本地文件数据库

**用途** | 本地开发、小型应用、嵌入式系统

```python
from kernel.db.core import EngineManager, EngineConfig, SessionManager
from kernel.db.api import SQLAlchemyCRUDRepository, QuerySpec

# 创建 SQLite 引擎
engine = EngineManager().create(EngineConfig(
    dialect="sqlite",
    database="data/app.db"  # 自动创建目录
))

session_mgr = SessionManager(engine)
repo = SQLAlchemyCRUDRepository(session_mgr)

# 使用事务
with repo.session_scope() as session:
    user = repo.add(session, User(name="Alice"), flush=True)
    users = repo.list(session, User, QuerySpec(limit=10))
```

### 2. MySQL - 关系型数据库

**用途** | 生产环境、中型应用、Web 服务

```python
from kernel.db.core import create_mysql_engine, SessionManager
from kernel.db.api import SQLAlchemyCRUDRepository

# 方式1：便捷函数
engine = create_mysql_engine(
    database="myapp",
    username="root",
    password="password123",
    host="localhost",
    port=3306,
    pool_size=10
)

# 方式2：EngineConfig
engine = EngineManager().create(EngineConfig(
    dialect="mysql",
    database="myapp",
    username="root",
    password="password123",
    host="localhost",
    port=3306,
    pool_size=10
))

session_mgr = SessionManager(engine)
repo = SQLAlchemyCRUDRepository(session_mgr)

with repo.session_scope() as session:
    user = repo.add(session, User(name="Bob"), flush=True)
```

**依赖** | `pymysql>=1.1.0`

### 3. PostgreSQL - 高性能数据库

**用途** | 高并发应用、分析查询、复杂数据结构

```python
from kernel.db.core import create_postgres_engine, SessionManager
from kernel.db.api import SQLAlchemyCRUDRepository

# 便捷函数
engine = create_postgres_engine(
    database="mofox",
    username="postgres",
    password="secure_password",
    host="localhost",
    port=5432,
    pool_size=20
)

session_mgr = SessionManager(engine)
repo = SQLAlchemyCRUDRepository(session_mgr)

with repo.session_scope() as session:
    user = repo.add(session, User(name="Charlie"), flush=True)
    
    # 使用查询规约
    result = repo.list(
        session,
        User,
        QuerySpec(
            filters={"age": (">", 18)},
            order_by="created_at DESC",
            limit=20
        )
    )
```

**依赖** | `psycopg2-binary>=2.9.0`

### 4. Redis - 内存数据库

**用途** | 缓存、会话存储、消息队列、实时排行榜

```python
from kernel.db.core import create_redis_engine
from kernel.db.api import RedisRepository

redis_client = create_redis_engine(
    database="0",
    host="localhost",
    port=6379,
    password="redis_password",  # 可选
    decode_responses=True
)

repo = RedisRepository(redis_client)

# String：简单键值
repo.set("user:1001:name", "Alice", ex=3600)

# Hash：结构化数据
repo.hset("user:1001", mapping={
    "name": "Alice",
    "age": "25",
    "email": "alice@example.com"
})
user_info = repo.hgetall("user:1001")

# List：消息队列
repo.lpush("notifications", "msg1", "msg2", "msg3")
msg = repo.rpop("notifications")

# Set：标签、好友
repo.sadd("user:1001:friends", "user2", "user3", "user4")
friends = repo.smembers("user:1001:friends")

# Sorted Set：排行榜
repo.zadd("leaderboard", {
    "player1": 1000,
    "player2": 2500,
    "player3": 1500
})
top_3 = repo.zrange("leaderboard", 0, 2, withscores=True)
```

**依赖** | `redis>=5.0.0`

### 5. MongoDB - 文档数据库

**用途** | 灵活架构、日志存储、用户生成内容、实时数据

```python
from kernel.db.core import create_mongodb_engine
from kernel.db.api import MongoDBRepository

mongo_client = create_mongodb_engine(
    database="mofox",
    uri="mongodb://localhost:27017",  # 或使用用户名密码
)

repo = MongoDBRepository(mongo_client["mofox"]["users"])

# 插入文档
doc_id = repo.insert_one({
    "name": "David",
    "email": "david@example.com",
    "tags": ["python", "ai"],
    "created_at": datetime.now()
})

# 查询文档
from kernel.db.api import QuerySpec

users = repo.find(
    QuerySpec(
        filters={"tags": "python"},
        limit=10
    )
)

# 更新文档
repo.update_one(
    filter={"_id": doc_id},
    update={"$set": {"status": "active"}}
)

# 聚合管道
result = repo.aggregate([
    {"$match": {"tags": "python"}},
    {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
])
```

**依赖** | `pymongo>=4.6.0`

---

## 核心组件（Core Components）

### EngineManager - 引擎管理器

```python
from kernel.db.core import EngineManager, EngineConfig

mgr = EngineManager()

# 创建引擎
config = EngineConfig(dialect="mysql", database="myapp", ...)
engine = mgr.create(config)

# 获取已有引擎
engine = mgr.get("mysql")

# 列出所有引擎
engines = mgr.list_engines()

# 清理资源
mgr.dispose("mysql")
```

**支持的方言** | `sqlite`, `mysql`, `postgresql`, `postgres`, `redis`, `mongodb`

### SessionManager - 会话管理器

```python
from kernel.db.core import SessionManager

session_mgr = SessionManager(engine)

# 上下文管理器
with session_mgr.session_scope() as session:
    # 自动提交/回滚和关闭
    pass

# 或创建单独会话
session = session_mgr.create_session()
try:
    # 业务逻辑
    session.commit()
finally:
    session.close()
```

### Repository 模式 - CRUD 抽象

三个具体实现：

| Repository | 数据库 | 方法数 | 用途 |
|------------|--------|--------|------|
| SQLAlchemyCRUDRepository | SQL 系列 | 11 个 | 关系型数据库操作 |
| RedisRepository | Redis | 23 个 | 多种 Redis 数据类型 |
| MongoDBRepository | MongoDB | 13 个 | 文档查询与聚合 |

```python
from kernel.db.api import SQLAlchemyCRUDRepository, QuerySpec

repo = SQLAlchemyCRUDRepository(session_mgr)

# CRUD 操作
user = repo.add(session, User(name="Alice"), flush=True)
users = repo.list(session, User, QuerySpec(limit=10))
repo.update(session, user_id, {"name": "Bob"})
repo.delete(session, User, user_id)
```

### QuerySpec - 统一查询规约

```python
from kernel.db.api import QuerySpec

spec = QuerySpec(
    filters={"age": (">", 18), "city": "Beijing"},
    order_by="created_at DESC",
    limit=20,
    offset=0,
    projection=["name", "email"]  # MongoDB 用
)

# SQL 数据库
sql_results = repo.list(session, User, spec)

# MongoDB
mongo_results = repo.find(spec)
```

---

## 缓存系统（Cache System）

### 本地缓存（LocalCache）

```python
from kernel.db.optimization import create_local_cache_manager

mgr = create_local_cache_manager(max_size=1000, ttl=3600)

# 装饰器方式
@mgr.cached()
def get_user(user_id):
    return db.get(user_id)

# 直接调用
user = get_user(123)  # 首次查询
user = get_user(123)  # 从缓存返回

# 手动操作
mgr.backend.set("key", "value", ex=3600)
value = mgr.backend.get("key")
```

### Redis 缓存（RedisCache）

```python
from kernel.db.optimization import create_redis_cache_manager

mgr = create_redis_cache_manager(
    redis_client=redis_client,
    key_prefix="mofox:"
)

# LLM 响应缓存
@mgr.cached(key_builder=lambda args: f"llm:response:{args[0]}")
def call_llm(prompt):
    return llm_client.chat(prompt)

# 分布式可用
response = call_llm("你好")  # Redis 存储，所有进程可用
```

**详见** [CACHE_GUIDE.md](CACHE_GUIDE.md)

---

## API 参考（API Reference）

### SQLAlchemyCRUDRepository

```python
# 添加
obj = repo.add(session, model_instance, flush=False)

# 列表查询
items = repo.list(session, Model, QuerySpec(...))

# 获取单个
item = repo.get(session, Model, pk_value)

# 计数
count = repo.count(session, Model, QuerySpec(...))

# 更新
repo.update(session, pk, {"field": "value"})

# 删除
repo.delete(session, Model, pk)

# 批量操作
repo.add_many(session, [obj1, obj2, ...])
repo.delete_many(session, Model, [pk1, pk2, ...])
```

### RedisRepository

```python
# String
repo.set(key, value, ex=3600)
value = repo.get(key)

# Hash
repo.hset(key, mapping=dict)
data = repo.hgetall(key)

# List
repo.lpush(queue, item1, item2)
item = repo.rpop(queue)

# Set
repo.sadd(key, member1, member2)
members = repo.smembers(key)

# Sorted Set
repo.zadd(leaderboard, {member: score})
top = repo.zrange(leaderboard, 0, 9, withscores=True)
```

### MongoDBRepository

```python
# 插入
doc_id = repo.insert_one(document)
ids = repo.insert_many([doc1, doc2])

# 查询
result = repo.find(QuerySpec(...))

# 获取单个
doc = repo.find_one(filter)

# 更新
repo.update_one(filter, update)
repo.update_many(filter, update)

# 删除
repo.delete_one(filter)
repo.delete_many(filter)

# 聚合
result = repo.aggregate(pipeline)
```

---

## 配置示例（Configuration Examples）

### 生产环境配置（Production）

```python
# MySQL + Redis 缓存 + MongoDB 日志

from kernel.db.core import EngineManager, EngineConfig

# 主数据库：MySQL
mysql_engine = EngineManager().create(EngineConfig(
    dialect="mysql",
    database="mofox",
    username="app_user",
    password="${DB_PASSWORD}",
    host="db.example.com",
    port=3306,
    pool_size=30,
    pool_recycle=3600,
    echo=False
))

# 缓存：Redis
redis_engine = EngineManager().create(EngineConfig(
    dialect="redis",
    database="0",
    host="cache.example.com",
    port=6379,
    password="${REDIS_PASSWORD}",
    ssl=True
))

# 日志：MongoDB
mongo_engine = EngineManager().create(EngineConfig(
    dialect="mongodb",
    database="mofox_logs",
    uri="mongodb+srv://${USER}:${PASS}@cluster.mongodb.net"
))
```

### 开发环境配置（Development）

```python
# SQLite + LocalCache

from kernel.db.core import EngineManager, EngineConfig

# 开发数据库
sqlite_engine = EngineManager().create(EngineConfig(
    dialect="sqlite",
    database="data/dev.db"
))

# 开发缓存
from kernel.db.optimization import create_local_cache_manager

cache_mgr = create_local_cache_manager(max_size=500, ttl=600)
```

---

## 最佳实践（Best Practices）

### 1. 数据库选择

| 场景 | 推荐 | 原因 |
|------|------|------|
| 本地开发 | SQLite | 无需外部服务 |
| 生产 Web | MySQL/PostgreSQL | 稳定、成熟、支持好 |
| 高并发 | PostgreSQL | 性能优于 MySQL |
| 缓存/会话 | Redis | 高速内存访问 |
| 灵活架构 | MongoDB | 无固定 schema |
| 日志/分析 | MongoDB | 易于扩展 |

### 2. 连接池管理

```python
# 设置合理的池大小
pool_size = 10  # 基础连接数
max_overflow = 20  # 溢出连接数

engine = EngineManager().create(EngineConfig(
    dialect="mysql",
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_recycle=3600  # 1 小时回收连接
))
```

### 3. 事务管理

```python
# 始终使用上下文管理器
with repo.session_scope() as session:
    # 自动处理提交/回滚
    user = repo.add(session, user_obj, flush=True)

# 避免长事务
# ❌ 错误
session = session_mgr.create_session()
for i in range(100000):
    repo.add(session, obj)
session.commit()

# ✅ 正确
for batch in batches:
    with repo.session_scope() as session:
        for obj in batch:
            repo.add(session, obj)
```

### 4. 缓存策略

```python
from kernel.db.optimization import create_redis_cache_manager

# LLM 响应缓存（重）
@cache_mgr.cached(key_prefix="llm:", ttl=86400)
def call_llm(prompt):
    return llm.chat(prompt)

# 数据库查询缓存（中）
@cache_mgr.cached(key_prefix="user:", ttl=3600)
def get_user(user_id):
    return repo.get(user_id)

# 配置缓存（轻）
@cache_mgr.cached(key_prefix="config:", ttl=300)
def get_config(key):
    return config_repo.get(key)
```

### 5. 错误处理

```python
from kernel.db.core import DBException

try:
    with repo.session_scope() as session:
        user = repo.add(session, user_obj)
except DBException as e:
    logger.error(f"数据库错误: {e}")
    # 重试逻辑
except Exception as e:
    logger.error(f"未知错误: {e}")
    raise
```

---

## 架构设计（Architecture）

```
┌─────────────────────────────────────────────┐
│      应用层（Application Layer）            │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│      Repository 层（CRUD 抽象）             │
│  ┌─────────┐  ┌────────┐  ┌──────────┐     │
│  │ SQLAlch │  │ Redis  │  │ MongoDB  │     │
│  │Repository │  │Repo   │  │Repo      │     │
│  └────┬────┘  └───┬────┘  └────┬─────┘     │
└───────┼──────────┼─────────────┼───────────┘
        │          │             │
┌───────▼──────────▼─────────────▼───────────┐
│       API 层（QuerySpec、会话）             │
│    ┌──────────────────────────────────┐    │
│    │     QuerySpec 统一查询规约       │    │
│    │  SessionManager（事务管理）      │    │
│    └──────────────────────────────────┘    │
└───────┬──────────────────────────────────┘
        │
┌───────▼──────────────────────────────────┐
│    方言适配器层（Dialect Adapters）      │
│ ┌───────┬────────┬──────────┬─────────┐  │
│ │SQLite│ MySQL │PostgreSQL│ Redis │  │
│ │      │        │          │        │  │
│ │      │        │          │MongoDB│  │
│ └───────┴────────┴──────────┴─────────┘  │
└───────┬──────────────────────────────────┘
        │
┌───────▼──────────────────────────────────┐
│    底层驱动（Database Drivers）          │
│ sqlite3│pymysql│psycopg2│redis │pymongo│
└───────────────────────────────────────────┘

缓存层：
┌──────────────────────────────────┐
│    CacheManager（统一管理）       │
│  ┌────────────┬────────────┐     │
│  │ LocalCache │ RedisCache │     │
│  └────────────┴────────────┘     │
│  • @cached 装饰器                │
│  • 自动序列化/反序列化           │
│  • TTL 和过期策略               │
└──────────────────────────────────┘
```

---

## 相关文档（Related Documentation）

- [CACHE_GUIDE.md](CACHE_GUIDE.md) - 缓存系统完整指南
- [src/kernel/db/README.md](../../src/kernel/db/README.md) - 数据库模块源代码说明
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - 贡献指南

---

## 常见问题（FAQ）

### Q: SQLite 为什么适合开发而不是生产？
A: SQLite 是单文件数据库，不支持并发写入，没有网络访问控制。适合本地开发和演示，生产环境应使用 MySQL 或 PostgreSQL。

### Q: MySQL 和 PostgreSQL 如何选择？
A: 
- **MySQL**: 生态成熟、易上手、适合中小型应用
- **PostgreSQL**: 功能强大、性能优越、支持复杂查询、适合大型应用

### Q: Redis 可以替代数据库吗？
A: 不推荐。Redis 是内存数据库，数据不持久化（除非配置 AOF/RDB），适合缓存和会话，关键业务数据应存储在 SQL 数据库。

### Q: MongoDB 和关系型数据库如何选择？
A: 
- **关系型**（MySQL/PostgreSQL）: 数据结构固定、需要 JOIN、事务一致性要求高
- **MongoDB**: 灵活架构、嵌套文档、分析日志、快速迭代

### Q: 如何实现多数据库事务？
A: 单个事务只能跨单个数据库。多数据库场景使用两阶段提交（2PC）或最终一致性模式。

### Q: 缓存是否支持失效？
A: 支持。LocalCache 在达到 `max_size` 时自动 LRU 清理，RedisCache 支持 `ex` 参数设置 TTL。也可手动调用 `clear()` 清空。

---

## 贡献（Contributing）

欢迎提交 Issue 和 Pull Request 改进本模块！

---

**最后更新** | 2026 年 1月 6日

