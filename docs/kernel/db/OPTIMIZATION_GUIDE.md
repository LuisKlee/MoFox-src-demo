# 数据库优化与架构设计指南（Database Optimization & Architecture Guide）

## 目录

1. [系统架构](#系统架构)
2. [连接池优化](#连接池优化)
3. [查询优化](#查询优化)
4. [缓存策略](#缓存策略)
5. [事务管理](#事务管理)
6. [监控与诊断](#监控与诊断)
7. [高可用设计](#高可用设计)

---

## 系统架构

### 分层架构

```
┌────────────────────────────────────────────────────────┐
│              应用业务层（Application）                 │
│          • LLM 服务  • 用户服务  • 消息服务           │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│            缓存层（Cache Layer）                      │
│   ┌─────────────┐        ┌──────────────┐           │
│   │ LocalCache  │◄────►  │ RedisCache   │           │
│   │ (本地内存)  │        │ (分布式)     │           │
│   └─────────────┘        └──────────────┘           │
│                                                       │
│  • @cached 装饰器                                    │
│  • 自动序列化/反序列化                               │
│  • TTL 和过期策略                                    │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│           Repository 层（数据访问）                  │
│   ┌──────────┐  ┌────────┐  ┌──────────┐           │
│   │SQL-CRUD  │  │Redis   │  │MongoDB   │           │
│   │Repository│  │Repo    │  │Repo      │           │
│   └────┬─────┘  └───┬────┘  └────┬─────┘           │
└───────┼─────────────┼─────────────┼────────────────┘
        │             │             │
┌───────▼─────────────▼─────────────▼────────────────┐
│         API 层（QuerySpec、会话管理）              │
│   ┌────────────────────────────────────────────┐  │
│   │  QuerySpec (统一查询规约)                  │  │
│   │  SessionManager (事务管理器)               │  │
│   │  EngineConfig (配置管理)                   │  │
│   └────────────────────────────────────────────┘  │
└───────┬─────────────────────────────────────────┬──┘
        │                                         │
┌───────▼─────────────────────┐   ┌──────────────▼──┐
│   SQLAlchemy ORM 层         │   │  驱动集成层    │
│  (MySQL/PostgreSQL)         │   │ (Redis/Mongo) │
└───────┬─────────────────────┘   └──────────────┬──┘
        │                                         │
┌───────▼─────────────────────────────────────────▼──┐
│           数据库引擎层（Database Layer）          │
│  ┌─────────┬────────┬───────────┬─────┬────────┐ │
│  │SQLite   │ MySQL  │PostgreSQL │Redis│MongoDB │ │
│  └─────────┴────────┴───────────┴─────┴────────┘ │
└──────────────────────────────────────────────────┘
```

### 多数据库选择矩阵

```python
# 根据需求选择合适的数据库组合

配置示例：
{
    "primary": {
        "type": "mysql" | "postgresql",  # 主业务数据
        "role": "master",
        "replication": True
    },
    "cache": {
        "type": "redis",                  # 缓存层
        "role": "cache",
        "ttl": 3600
    },
    "analytics": {
        "type": "mongodb" | "postgresql",  # 分析数据
        "role": "analytics",
        "archive": True
    },
    "log": {
        "type": "mongodb",                # 日志存储
        "role": "log",
        "retention": "30d"
    }
}
```

---

## 连接池优化

### 连接池参数调优

```python
from kernel.db.core import EngineManager, EngineConfig

def create_optimized_engine(db_type: str, concurrent_users: int):
    """
    根据并发用户数优化连接池参数
    
    Args:
        db_type: 数据库类型 (mysql, postgresql)
        concurrent_users: 并发用户数
    
    Returns:
        优化后的数据库引擎
    """
    
    # 连接池计算公式
    # pool_size = concurrent_users / 2  (数据库通常时间片很短)
    # max_overflow = pool_size / 2
    # max_idle_time = 300-600 秒
    
    pool_size = max(5, concurrent_users // 2)
    max_overflow = pool_size // 2
    
    return EngineManager().create(EngineConfig(
        dialect=db_type,
        database="mofox",
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=30,          # 等待可用连接的超时时间
        pool_recycle=3600,        # 连接回收周期
        pool_pre_ping=True,       # 使用前检查连接活跃性
        echo=False,               # 关闭 SQL 日志（提高性能）
        engine_kwargs={
            "pool_use_lifo": True  # 使用 LIFO（减少连接复用）
        }
    ))

# 使用示例
# 10 个并发用户
small_app_engine = create_optimized_engine("mysql", 10)

# 100 个并发用户
medium_app_engine = create_optimized_engine("postgresql", 100)

# 1000+ 并发用户
large_app_engine = create_optimized_engine("postgresql", 1000)
```

### 连接池监控

```python
from sqlalchemy import event, pool

def log_pool_events(dbapi_conn, connection_record):
    """记录连接池事件用于诊断"""
    print(f"新连接: {id(dbapi_conn)}")

def log_pool_checkout(dbapi_conn, connection_record, connection_proxy):
    """记录连接取出"""
    print(f"连接签出: {id(dbapi_conn)}")

def log_pool_checkin(dbapi_conn, connection_record):
    """记录连接归还"""
    print(f"连接归还: {id(dbapi_conn)}")

# 为引擎绑定事件
engine = create_optimized_engine("mysql", 100)

event.listen(engine.pool, "connect", log_pool_events)
event.listen(engine.pool, "checkout", log_pool_checkout)
event.listen(engine.pool, "checkin", log_pool_checkin)

# 获取连接池状态
pool_stats = {
    "size": engine.pool.size(),
    "checked_out": engine.pool.checkedout(),
    "overflow": engine.pool.overflow(),
    "total": engine.pool.size() + engine.pool.overflow()
}

print(f"连接池状态: {pool_stats}")
```

---

## 查询优化

### 1. 使用 QuerySpec 进行分页

```python
from kernel.db.api import QuerySpec, SQLAlchemyCRUDRepository

repo = SQLAlchemyCRUDRepository(session_mgr)

# ❌ 错误：加载所有数据到内存
with repo.session_scope() as session:
    all_users = repo.list(session, User)  # 可能 100 万条！
    for user in all_users:
        process(user)

# ✅ 正确：分页处理
page_size = 1000
offset = 0

with repo.session_scope() as session:
    while True:
        users = repo.list(
            session,
            User,
            QuerySpec(limit=page_size, offset=offset)
        )
        
        if not users:
            break
        
        for user in users:
            process(user)
        
        offset += page_size
```

### 2. 索引优化

```python
from sqlalchemy import Index, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)  # 唯一索引
    username = Column(String(255))
    created_at = Column(DateTime)
    
    # 复合索引：常用于查询过滤
    __table_args__ = (
        Index('idx_created_at_username', 'created_at', 'username'),
        Index('idx_email_created_at', 'email', 'created_at'),
    )

# 创建表并索引
Base.metadata.create_all(engine)

# 查询时，使用索引的字段条件
from kernel.db.api import QuerySpec

# 使用索引，查询快
spec = QuerySpec(
    filters={
        "created_at": (">", datetime.now() - timedelta(days=7)),
        "username": "admin"
    },
    order_by="created_at DESC"
)

users = repo.list(session, User, spec)
```

### 3. MongoDB 查询优化

```python
from kernel.db.api import MongoDBRepository, QuerySpec

repo = MongoDBRepository(collection)

# ❌ 低效：聚合前没有 $match 过滤
result = repo.aggregate([
    {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 100}}}  # 在后面才过滤
])

# ✅ 高效：先过滤再聚合
result = repo.aggregate([
    {"$match": {"created_at": {"$gte": datetime.now() - timedelta(days=7)}}},
    {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 100}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
])

# MongoDB 索引
collection.create_index("email")
collection.create_index([("created_at", -1)])
collection.create_index([("tags", 1), ("created_at", -1)])
```

### 4. Redis 查询优化

```python
from kernel.db.api import RedisRepository

repo = RedisRepository(redis_client)

# ❌ 低效：多个 get 请求
user_ids = [1, 2, 3, 4, 5]
for uid in user_ids:
    user = repo.get(f"user:{uid}")  # 5 个网络往返

# ✅ 高效：管道批量获取
with redis_client.pipeline() as pipe:
    for uid in user_ids:
        pipe.get(f"user:{uid}")
    users = pipe.execute()  # 1 个网络往返

# 或直接使用 Repository 的批量方法
keys = [f"user:{uid}" for uid in user_ids]
users = repo.get_many(keys)
```

---

## 缓存策略

### 1. 多级缓存架构

```python
from kernel.db.optimization import (
    create_local_cache_manager,
    create_redis_cache_manager
)

# 第一层：本地内存缓存（热数据）
local_cache_mgr = create_local_cache_manager(
    max_size=500,       # 500 条记录
    ttl=300             # 5 分钟
)

# 第二层：Redis 缓存（分布式）
redis_cache_mgr = create_redis_cache_manager(
    redis_client=redis_client,
    key_prefix="mofox:",
    ttl=3600            # 1 小时
)

# 使用多级缓存
def get_user_optimized(user_id):
    """获取用户，优先使用多级缓存"""
    
    # L1: 本地缓存
    key = f"user:{user_id}"
    user = local_cache_mgr.backend.get(key)
    if user:
        return user
    
    # L2: Redis 缓存
    user = redis_cache_mgr.backend.get(key)
    if user:
        # 回写到本地缓存
        local_cache_mgr.backend.set(key, user, ex=300)
        return user
    
    # L3: 数据库
    user = db.get_user(user_id)
    
    # 写入双层缓存
    local_cache_mgr.backend.set(key, user, ex=300)
    redis_cache_mgr.backend.set(key, user, ex=3600)
    
    return user
```

### 2. 缓存更新策略

```python
class CacheStrategy:
    """缓存更新策略"""
    
    # 缓存穿透：大量查询不存在的键
    @staticmethod
    def cache_through(key: str, db_getter, cache_mgr, ttl=3600):
        """
        缓存穿透保护：缓存空值
        """
        cached = cache_mgr.backend.get(key)
        if cached is not None:
            return cached
        
        # 数据库查询
        value = db_getter()
        
        if value is None:
            # 缓存空值（短 TTL）防止穿透
            cache_mgr.backend.set(key, "NULL", ex=60)
            return None
        
        cache_mgr.backend.set(key, value, ex=ttl)
        return value
    
    # 缓存击穿：热键过期导致数据库压力
    @staticmethod
    def cache_stampede_protection(key: str, db_getter, cache_mgr, ttl=3600):
        """
        缓存击穿保护：使用互斥锁
        """
        cached = cache_mgr.backend.get(key)
        if cached:
            return cached
        
        # 尝试获取锁（1 秒超时）
        lock_key = f"{key}:lock"
        lock_value = str(uuid.uuid4())
        
        if cache_mgr.backend.set_if_not_exists(lock_key, lock_value, ex=1):
            try:
                # 获得锁，进行数据库查询并更新缓存
                value = db_getter()
                cache_mgr.backend.set(key, value, ex=ttl)
            finally:
                # 释放锁
                cache_mgr.backend.delete(lock_key)
        else:
            # 未获得锁，自旋等待缓存更新
            for _ in range(10):
                import time
                time.sleep(0.1)
                value = cache_mgr.backend.get(key)
                if value:
                    return value
        
        return cache_mgr.backend.get(key)
    
    # 缓存雪崩：大量键同时过期
    @staticmethod
    def cache_avalanche_protection(keys_getters: dict, cache_mgr):
        """
        缓存雪崩保护：随机 TTL
        """
        import random
        
        for key, db_getter in keys_getters.items():
            # 随机 TTL（±10%）
            base_ttl = 3600
            random_ttl = int(base_ttl * (0.9 + random.random() * 0.2))
            
            value = db_getter()
            cache_mgr.backend.set(key, value, ex=random_ttl)
```

### 3. 缓存预热

```python
def warm_cache(cache_mgr, db_repo):
    """
    缓存预热：启动时加载热数据
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("开始缓存预热...")
    
    # 预热用户数据
    from kernel.db.api import QuerySpec
    
    with db_repo.session_scope() as session:
        # 获取最活跃的 1000 个用户
        active_users = db_repo.list(
            session,
            User,
            QuerySpec(
                filters={"status": "active"},
                order_by="last_login DESC",
                limit=1000
            )
        )
        
        for user in active_users:
            key = f"user:{user.id}"
            cache_mgr.backend.set(
                key,
                pickle.dumps(user),
                ex=86400  # 24 小时
            )
    
    logger.info(f"缓存预热完成，共 {len(active_users)} 条记录")

# 启动时调用
if __name__ == "__main__":
    from kernel.db.optimization import create_redis_cache_manager
    
    cache_mgr = create_redis_cache_manager(redis_client)
    warm_cache(cache_mgr, repo)
    
    # 启动应用
    app.run()
```

---

## 事务管理

### 1. 基础事务

```python
from kernel.db.core import SessionManager

session_mgr = SessionManager(engine)
repo = SQLAlchemyCRUDRepository(session_mgr)

# ✅ 推荐：使用上下文管理器
with repo.session_scope() as session:
    # 自动提交/回滚
    user = repo.add(session, User(name="Alice"), flush=True)
    # 提交时点
```

### 2. 嵌套事务与保存点

```python
with repo.session_scope() as session:
    user = repo.add(session, User(name="Alice"))
    
    try:
        with session.begin_nested() as sp:
            # 嵌套事务
            profile = repo.add(session, Profile(user_id=user.id))
            # 某个操作失败
            if error:
                sp.rollback()  # 仅回滚此部分
    except:
        pass  # 继续处理

# 手动事务管理（不推荐）
session = session_mgr.create_session()
try:
    user = repo.add(session, User(name="Bob"))
    session.commit()
except Exception as e:
    session.rollback()
    logger.error(f"事务失败: {e}")
finally:
    session.close()
```

### 3. 分布式事务处理

```python
# 场景：在 MySQL 和 Redis 中原子性操作

def update_user_with_cache(user_id, updates):
    """
    更新用户信息并更新缓存（两阶段提交模式）
    """
    cache_key = f"user:{user_id}"
    
    # Phase 1: Prepare
    try:
        with repo.session_scope() as session:
            user = repo.get(session, User, user_id)
            if not user:
                raise ValueError("用户不存在")
            
            # 检查更新的有效性
            for key, value in updates.items():
                if not is_valid(key, value):
                    raise ValueError(f"非法更新: {key}={value}")
        
        # Phase 2: Commit
        with repo.session_scope() as session:
            repo.update(session, user_id, updates)
            
            # 更新缓存
            updated_user = repo.get(session, User, user_id)
            cache_mgr.backend.set(
                cache_key,
                pickle.dumps(updated_user),
                ex=3600
            )
        
        return True
    
    except Exception as e:
        # 回滚：删除缓存或保持原值
        logger.error(f"事务失败: {e}")
        return False
```

---

## 监控与诊断

### 1. 查询性能监控

```python
from sqlalchemy import event
from time import time
import logging

logger = logging.getLogger(__name__)

class QueryMonitor:
    """SQL 查询性能监控"""
    
    queries = []
    
    @classmethod
    def before_cursor_execute(cls, conn, cursor, statement, parameters, context, executemany):
        """查询执行前"""
        conn.info.setdefault('query_start_time', []).append(time())
    
    @classmethod
    def after_cursor_execute(cls, conn, cursor, statement, parameters, context, executemany):
        """查询执行后"""
        total_time = time() - conn.info['query_start_time'].pop(-1)
        
        if total_time > 0.1:  # 超过 100ms 的慢查询
            logger.warning(
                f"慢查询 ({total_time:.3f}s): {statement[:100]}..."
            )
        
        cls.queries.append({
            'statement': statement[:200],
            'time': total_time,
            'parameters': str(parameters)[:100]
        })
    
    @classmethod
    def register(cls, engine):
        """为引擎注册监控"""
        event.listen(engine, "before_cursor_execute", cls.before_cursor_execute)
        event.listen(engine, "after_cursor_execute", cls.after_cursor_execute)
    
    @classmethod
    def report(cls):
        """生成性能报告"""
        if not cls.queries:
            return "无查询记录"
        
        total_time = sum(q['time'] for q in cls.queries)
        avg_time = total_time / len(cls.queries)
        max_time = max(q['time'] for q in cls.queries)
        
        return f"""
        查询统计：
        - 总查询数: {len(cls.queries)}
        - 总耗时: {total_time:.3f}s
        - 平均耗时: {avg_time:.3f}s
        - 最长耗时: {max_time:.3f}s
        """

# 使用
engine = create_optimized_engine("mysql", 100)
QueryMonitor.register(engine)

# 应用运行...

# 输出报告
print(QueryMonitor.report())
```

### 2. 连接池健康检查

```python
def check_connection_pool_health(engine):
    """检查连接池健康状态"""
    
    pool = engine.pool
    
    stats = {
        'pool_size': pool.size(),
        'checked_out': pool.checkedout(),
        'overflow': pool.overflow(),
        'total_connections': pool.size() + pool.overflow(),
        'utilization': (pool.checkedout() / (pool.size() + pool.overflow())) * 100
        if pool.size() > 0 else 0
    }
    
    # 健康检查
    health_status = "OK"
    if stats['utilization'] > 90:
        health_status = "WARNING: 连接池使用率过高"
    elif stats['overflow'] > stats['pool_size']:
        health_status = "CRITICAL: 溢出连接过多"
    
    return stats, health_status

# 定期检查
import threading

def monitor_pool_health(engine, interval=60):
    """定期监控连接池"""
    def check():
        while True:
            stats, status = check_connection_pool_health(engine)
            logger.info(f"连接池: {stats} - {status}")
            time.sleep(interval)
    
    thread = threading.Thread(target=check, daemon=True)
    thread.start()

# 使用
monitor_pool_health(engine, interval=30)
```

### 3. Redis 性能监控

```python
def monitor_redis_health(redis_client):
    """监控 Redis 服务健康"""
    
    # 基础健康检查
    ping_result = redis_client.ping()
    
    # 获取服务器统计
    info = redis_client.info()
    
    stats = {
        'connected_clients': info.get('connected_clients', 0),
        'used_memory': info.get('used_memory_human', '0B'),
        'used_memory_peak': info.get('used_memory_peak_human', '0B'),
        'total_keys': redis_client.dbsize(),
        'evicted_keys': info.get('evicted_keys', 0),
        'keyspace_hits': info.get('keyspace_hits', 0),
        'keyspace_misses': info.get('keyspace_misses', 0),
    }
    
    # 计算缓存命中率
    total = stats['keyspace_hits'] + stats['keyspace_misses']
    hit_rate = (stats['keyspace_hits'] / total * 100) if total > 0 else 0
    
    return {
        'status': 'OK' if ping_result else 'FAILED',
        'stats': stats,
        'hit_rate': f"{hit_rate:.2f}%"
    }

# 使用
redis_health = monitor_redis_health(redis_client)
print(f"缓存命中率: {redis_health['hit_rate']}")
```

---

## 高可用设计

### 1. 主从复制（MySQL/PostgreSQL）

```python
# Master 配置（写入）
master_engine = EngineManager().create(EngineConfig(
    dialect="mysql",
    database="mofox",
    username="app_user",
    password="password",
    host="master.db.example.com",
    port=3306,
    pool_size=20
))

# Slave 配置（读取）
slave_engine = EngineManager().create(EngineConfig(
    dialect="mysql",
    database="mofox",
    username="app_user",
    password="password",
    host="slave.db.example.com",
    port=3306,
    pool_size=30  # 读库连接数更多
))

class ReadWriteSeparation:
    """读写分离"""
    
    def __init__(self, master_session_mgr, slave_session_mgr):
        self.master_session_mgr = master_session_mgr
        self.slave_session_mgr = slave_session_mgr
    
    def write(self, func):
        """写操作使用 Master"""
        with self.master_session_mgr.session_scope() as session:
            return func(session)
    
    def read(self, func):
        """读操作使用 Slave"""
        with self.slave_session_mgr.session_scope() as session:
            return func(session)

# 使用
rw = ReadWriteSeparation(master_session_mgr, slave_session_mgr)

# 写入
def add_user(user_data):
    def _add(session):
        return repo.add(session, User(**user_data), flush=True)
    return rw.write(_add)

# 读取
def get_user(user_id):
    def _get(session):
        return repo.get(session, User, user_id)
    return rw.read(_get)
```

### 2. MongoDB 副本集

```python
# 副本集连接
mongo_client = create_mongodb_engine(
    uri="mongodb://node1:27017,node2:27017,node3:27017",
    replicaSet="rs0",
    database="mofox",
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    retryWrites=True
)

# 定义读偏好
from pymongo import ReadPreference

# 读取从副本（降低主节点压力）
db = mongo_client["mofox"]
db.read_preference = ReadPreference.SECONDARY_PREFERRED

# 写入总是到主节点
collection = db["users"]
result = collection.insert_one({"name": "Alice"})  # 写到主节点
```

### 3. Redis 高可用

```python
# Sentinel 配置（自动故障转移）
from redis.sentinel import Sentinel

sentinels = [
    ("sentinel1.example.com", 26379),
    ("sentinel2.example.com", 26379),
    ("sentinel3.example.com", 26379),
]

sentinel = Sentinel(sentinels, socket_timeout=0.1)

# 主节点
master = sentinel.master_for("mymaster", socket_timeout=0.1)

# 从节点（读取）
slave = sentinel.slave_for("mymaster", socket_timeout=0.1)

# 写入到主
master.set("key", "value")

# 读取从从（可能延迟）
try:
    value = slave.get("key")
except:
    # 故障转移，使用主节点
    value = master.get("key")
```

### 4. 健康检查与自动故障转移

```python
import threading
import time

class HealthChecker:
    """定期健康检查"""
    
    def __init__(self, engine, interval=30):
        self.engine = engine
        self.interval = interval
        self.is_healthy = True
    
    def check(self):
        """检查数据库连接健康状态"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            self.is_healthy = True
            logger.info("✓ 数据库连接正常")
        except Exception as e:
            self.is_healthy = False
            logger.error(f"✗ 数据库连接失败: {e}")
    
    def start_monitoring(self):
        """启动后台监控"""
        def monitor():
            while True:
                self.check()
                time.sleep(self.interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

# 使用
checker = HealthChecker(engine, interval=30)
checker.start_monitoring()

# 应用中检查状态
def safe_query():
    if not checker.is_healthy:
        # 切换到备用数据库或使用缓存
        return get_from_cache_or_backup()
    
    return query_database()
```

---

## 性能基准测试

```python
import timeit

def benchmark_operations():
    """基准测试不同操作的性能"""
    
    # 单条插入
    insert_time = timeit.timeit(
        lambda: repo.add(session, User(name="test")),
        number=1000
    )
    print(f"单条插入: {insert_time/1000:.3f}ms")
    
    # 批量插入
    batch_insert_time = timeit.timeit(
        lambda: [repo.add(session, User(name=f"user{i}")) for i in range(100)],
        number=10
    )
    print(f"批量插入(100条): {batch_insert_time/10:.1f}ms")
    
    # 查询
    query_time = timeit.timeit(
        lambda: repo.list(session, User, QuerySpec(limit=100)),
        number=100
    )
    print(f"查询(100条): {query_time/100:.3f}ms")
    
    # 缓存读取
    cache_time = timeit.timeit(
        lambda: cache_mgr.backend.get("key"),
        number=10000
    )
    print(f"缓存读取: {cache_time/10000:.3f}ms")

benchmark_operations()
```

---

**最后更新** | 2026 年 1月 6日

