# 数据库模块 - 快速参考（Database Module - Quick Reference）

## 🎯 核心概念速查表

### 数据库选择速查（Database Selection）

```
应用规模        推荐方案              理由
─────────────────────────────────────────────────────
小型/个人      SQLite                无需服务器，零配置
原型开发       SQLite + LocalCache   快速迭代
中型 Web       MySQL + Redis         成熟生态，够用
大型应用       PostgreSQL + Redis    性能优、功能全
日志/分析      MongoDB               灵活架构、高吞吐
高并发         PostgreSQL + Redis    最佳组合
分布式         MongoDB + Redis       天然支持分片
```

### 数据库对比（At a Glance）

| 特性 | SQLite | MySQL | PostgreSQL | Redis | MongoDB |
|------|:------:|:-----:|:----------:|:-----:|:-------:|
| 本地部署 | ✓ | ✗ | ✗ | ✗ | ✗ |
| 零配置 | ✓✓✓ | ✗ | ✗ | ✗ | ✗ |
| 写入并发 | ✗ | ✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ |
| 复杂查询 | ✓ | ✓ | ✓✓✓ | ✗ | ✓✓ |
| 事务 | ✓ | ✓✓ | ✓✓✓ | ✓ | ✓ |
| 分布式 | ✗ | ✗ | ✓ | ✓✓ | ✓✓✓ |
| 生态成熟 | ✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ |

---

## 🚀 常见模式

### 1. 创建引擎（Create Engine）

```python
# SQLite - 文件数据库
engine = EngineManager().create(EngineConfig(
    dialect="sqlite",
    database="data/app.db"
))

# MySQL - 关系型数据库
engine = create_mysql_engine(
    database="myapp",
    username="root",
    password="password",
    host="localhost"
)

# PostgreSQL - 高性能数据库
engine = create_postgres_engine(
    database="myapp",
    username="postgres",
    password="password"
)

# Redis - 缓存数据库
redis_client = create_redis_engine(
    host="localhost",
    port=6379
)

# MongoDB - 文档数据库
mongo_client = create_mongodb_engine(
    uri="mongodb://localhost:27017",
    database="myapp"
)
```

### 2. CRUD 操作（CRUD Operations）

```python
# 插入（Create）
user = repo.add(session, User(name="Alice"), flush=True)

# 查询（Read）
user = repo.get(session, User, 1)
users = repo.list(session, User, QuerySpec(limit=10))

# 更新（Update）
repo.update(session, 1, {"name": "Bob"})

# 删除（Delete）
repo.delete(session, User, 1)
```

### 3. 批量操作（Batch Operations）

```python
# 批量插入
users = [User(name=f"user{i}") for i in range(100)]
repo.add_many(session, users)

# 批量删除
ids = [1, 2, 3, 4, 5]
repo.delete_many(session, User, ids)

# 批量更新
for uid in ids:
    repo.update(session, uid, {"status": "active"})
```

### 4. 分页查询（Pagination）

```python
page_size = 20
total = repo.count(session, User)

for page in range(0, total, page_size):
    users = repo.list(
        session,
        User,
        QuerySpec(
            limit=page_size,
            offset=page,
            order_by="created_at DESC"
        )
    )
    process(users)
```

### 5. 条件查询（Filtering）

```python
# 简单条件
users = repo.list(session, User, QuerySpec(
    filters={"status": "active"}
))

# 复杂条件
users = repo.list(session, User, QuerySpec(
    filters={
        "age": (">", 18),
        "city": "Beijing",
        "status": "active"
    }
))

# MongoDB 条件
result = repo.find(QuerySpec(
    filters={"tags": "python"}  # 数组包含
))
```

### 6. 缓存操作（Caching）

```python
# 创建缓存管理器
cache_mgr = create_local_cache_manager(max_size=1000)

# 装饰器方式
@cache_mgr.cached()
def get_user(user_id):
    return db.get_user(user_id)

# 直接使用
cache_mgr.backend.set("key", "value", ex=3600)
value = cache_mgr.backend.get("key")

# 删除缓存
cache_mgr.backend.delete("key")
cache_mgr.backend.clear()
```

---

## 🔧 配置参数

### EngineConfig 参数

```python
EngineConfig(
    dialect="mysql",              # 方言：mysql, postgresql, sqlite, redis, mongodb
    database="myapp",              # 数据库名
    username="root",               # 用户名（SQL 数据库）
    password="password",           # 密码（SQL 数据库）
    host="localhost",              # 主机地址
    port=3306,                     # 端口
    pool_size=10,                  # 连接池大小
    max_overflow=5,                # 最大溢出连接
    pool_timeout=30,               # 获取连接超时（秒）
    pool_recycle=3600,             # 连接回收时间（秒）
    echo=False,                    # 是否打印 SQL
    charset="utf8mb4"              # 字符集
)
```

### QuerySpec 参数

```python
QuerySpec(
    filters={                      # 过滤条件字典
        "age": (">", 18),
        "status": "active"
    },
    order_by="created_at DESC",    # 排序
    limit=20,                      # 结果数量限制
    offset=0,                      # 偏移量
    projection=["id", "name"]      # 字段投影（MongoDB）
)
```

---

## 📊 性能参考

```
操作               耗时（100万条记录）   最佳实践
────────────────────────────────────────────
单条查询           1-5ms                使用索引
列表查询           50-200ms             分页查询
聚合操作           200-1000ms           使用投影
插入（单条）       0.5-2ms              批量插入
插入（批量）       10-50μs/条           使用事务
更新               1-5ms                更新必要字段
删除               1-5ms                建议物理删除
缓存读取           0.1-1μs              使用 Redis
```

---

## ⚠️ 常见错误

### 错误 1：不使用事务上下文管理器

```python
# ❌ 错误：连接可能未关闭
session = session_mgr.create_session()
user = repo.add(session, User(name="Alice"))
session.commit()

# ✅ 正确：自动管理
with repo.session_scope() as session:
    user = repo.add(session, User(name="Alice"))
```

### 错误 2：加载所有数据到内存

```python
# ❌ 错误：100万条数据全在内存
all_users = repo.list(session, User)

# ✅ 正确：分页处理
users = repo.list(session, User, QuerySpec(limit=1000, offset=offset))
```

### 错误 3：没有缓存热数据

```python
# ❌ 错误：每次都查询数据库
def get_user(user_id):
    return repo.get(session, User, user_id)

# ✅ 正确：使用缓存
@cache_mgr.cached()
def get_user(user_id):
    return repo.get(session, User, user_id)
```

### 错误 4：连接池配置不当

```python
# ❌ 错误：连接池太小
engine = EngineManager().create(EngineConfig(
    dialect="mysql",
    pool_size=2,  # 太小！
))

# ✅ 正确：根据并发数调整
engine = EngineManager().create(EngineConfig(
    dialect="mysql",
    pool_size=20,      # 并发用户数 / 2
    max_overflow=10
))
```

### 错误 5：MongoDB 认证失败

```python
# ❌ 错误：未指定认证数据库
mongo_client = create_mongodb_engine(
    uri="mongodb://user:password@localhost"
)

# ✅ 正确：指定 authSource
mongo_client = create_mongodb_engine(
    uri="mongodb://user:password@localhost",
    authSource="admin"
)
```

---

## 🎓 学习路径

### 初级（Beginner）
1. 学习 SQLite 基础：[README.md](README.md#快速开始)
2. 掌握 CRUD 操作：[API 参考](#2-crud-操作)
3. 理解查询规约：[QuerySpec](#querysecspec-参数)

### 中级（Intermediate）
1. 迁移到 MySQL/PostgreSQL：[DATABASE_GUIDE.md](DATABASE_GUIDE.md)
2. 添加缓存层：[CACHE_GUIDE.md](CACHE_GUIDE.md)
3. 优化查询性能：[OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md#查询优化)

### 高级（Advanced）
1. 读写分离：[高可用设计](OPTIMIZATION_GUIDE.md#高可用设计)
2. 多级缓存：[缓存策略](OPTIMIZATION_GUIDE.md#缓存策略)
3. 性能监控：[监控与诊断](OPTIMIZATION_GUIDE.md#监控与诊断)

---

## 🔗 快速导航

| 文档 | 内容 | 适合场景 |
|------|------|---------|
| [README.md](README.md) | 📌 全面概览 + 快速开始 | 新手入门 |
| [DATABASE_GUIDE.md](DATABASE_GUIDE.md) | 🎯 数据库选择 + 配置 | 选型与部署 |
| [CACHE_GUIDE.md](CACHE_GUIDE.md) | ⚡ 缓存系统详解 | 缓存使用 |
| [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md) | 🚀 性能优化 + 高可用 | 生产优化 |

---

## 💡 实战示例

### 场景 1：简单 Web 应用

```python
# 初始化
engine = create_sqlite_engine("data/app.db")
session_mgr = SessionManager(engine)
repo = SQLAlchemyCRUDRepository(session_mgr)

# 获取用户
with repo.session_scope() as session:
    user = repo.get(session, User, 1)
    
# 保存用户
with repo.session_scope() as session:
    repo.update(session, 1, {"name": "Alice"})
```

### 场景 2：生产级应用

```python
# 主数据库 + 缓存 + 日志
master_engine = create_mysql_engine(...)
cache_mgr = create_redis_cache_manager(redis_client)
mongo_client = create_mongodb_engine(...)  # 日志

# 使用缓存查询
@cache_mgr.cached(ttl=3600)
def get_user(user_id):
    with SessionManager(master_engine).session_scope() as session:
        return repo.get(session, User, user_id)

# 记录日志
log_repo = MongoDBRepository(mongo_client["logs"]["user_actions"])
log_repo.insert_one({
    "user_id": user_id,
    "action": "login",
    "timestamp": datetime.now()
})
```

### 场景 3：高并发应用

```python
# PostgreSQL + 多级缓存
engine = create_postgres_engine(..., pool_size=50)
local_cache = create_local_cache_manager(max_size=500)
redis_cache = create_redis_cache_manager(redis_client)

# 三层缓存查询
def get_user_optimized(user_id):
    # L1: 本地
    key = f"user:{user_id}"
    user = local_cache.backend.get(key)
    if user: return user
    
    # L2: Redis
    user = redis_cache.backend.get(key)
    if user:
        local_cache.backend.set(key, user, ex=300)
        return user
    
    # L3: 数据库
    with SessionManager(engine).session_scope() as session:
        user = repo.get(session, User, user_id)
        redis_cache.backend.set(key, user, ex=3600)
        return user
```

---

## 📞 常见问题速答

| 问题 | 答案 |
|------|------|
| **我应该使用哪个数据库？** | 看这张表：[数据库选择](#数据库选择速查) |
| **如何加快查询速度？** | 使用 QuerySpec 分页 + 缓存 + 索引 |
| **连接池应该多大？** | 并发数 / 2-4（见[配置参数](#连接池优化)） |
| **缓存多久失效？** | 热数据 300-600s，冷数据 3600s |
| **MongoDB 怎么写事务？** | 使用副本集 + `session` 对象 |
| **如何监控性能？** | [监控与诊断](OPTIMIZATION_GUIDE.md#监控与诊断) |

---

## 🏆 最佳实践总结

✅ **DO：**
- 使用 `with repo.session_scope()` 管理事务
- 对高频数据使用缓存（@cached 装饰器）
- 分页查询大数据集（limit + offset）
- 为常用条件建立索引
- 使用查询规约（QuerySpec）统一接口

❌ **DON'T：**
- 不在事务外保持长连接
- 不一次性加载所有数据
- 不忽视缓存穿透/雪崩问题
- 不使用 N+1 查询模式
- 不跳过连接池配置

---

**版本** | 1.0 | **更新** | 2026年 1月 6日

