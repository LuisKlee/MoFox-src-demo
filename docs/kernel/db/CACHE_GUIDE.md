# 缓存管理器使用指南

## 概述

缓存管理器提供了统一的缓存接口，支持多种后端（本地内存、Redis）。

## 功能特性

- 🎯 **统一接口**：支持本地缓存和 Redis 缓存的无缝切换
- 🔄 **自动过期**：支持 TTL（生存时间）自动管理
- 🎨 **装饰器**：提供 `@cached` 装饰器自动缓存函数结果
- 🚀 **批量操作**：支持批量获取、设置、删除操作
- 🔢 **计数器**：支持原子递增/递减操作
- 🧵 **线程安全**：本地缓存实现线程安全的 LRU 策略

## 快速开始

### 1. 本地内存缓存

```python
from kernel.db.optimization import create_local_cache_manager

# 创建本地缓存管理器
cache = create_local_cache_manager(
    max_size=1000,      # 最大缓存条目数
    default_ttl=3600,   # 默认过期时间（秒）
    key_prefix="app"    # 键前缀
)

# 基本操作
cache.set("user:1001", {"name": "Alice", "age": 25}, ttl=300)
user = cache.get("user:1001")
cache.delete("user:1001")

# 检查键是否存在
if cache.exists("user:1001"):
    print("User exists in cache")

# 清空所有缓存
cache.clear()
```

### 2. Redis 缓存

```python
from kernel.db.core import create_redis_engine
from kernel.db.optimization import create_redis_cache_manager

# 创建 Redis 客户端
redis_client = create_redis_engine(
    database="0",
    host="localhost",
    port=6379
)

# 创建 Redis 缓存管理器
cache = create_redis_cache_manager(
    redis_client=redis_client,
    prefix="mofox:",        # Redis 键前缀
    default_ttl=3600,       # 默认过期时间
    key_prefix="cache",     # 全局键前缀
    serialize=True          # 自动序列化对象
)

# 使用方式与本地缓存相同
cache.set("session:abc123", {"user_id": 1001, "token": "xyz"})
session = cache.get("session:abc123")
```

### 3. 获取或设置模式

```python
# 如果缓存不存在，则调用工厂函数生成值
def fetch_user_from_db():
    # 从数据库查询用户
    return {"name": "Bob", "age": 30}

user = cache.get_or_set(
    "user:1002",
    default_factory=fetch_user_from_db,
    ttl=600
)
```

### 4. 批量操作

```python
# 批量设置
cache.set_many({
    "product:1": {"name": "Laptop", "price": 999},
    "product:2": {"name": "Mouse", "price": 29},
    "product:3": {"name": "Keyboard", "price": 79},
}, ttl=1800)

# 批量获取
products = cache.get_many(["product:1", "product:2", "product:3"])
# 返回: {"product:1": {...}, "product:2": {...}, "product:3": {...}}

# 批量删除
deleted_count = cache.delete_many(["product:1", "product:2"])
```

### 5. 计数器操作

```python
# 初始化计数器
cache.set("page_views", 0)

# 递增
cache.increment("page_views")          # +1
cache.increment("page_views", 10)      # +10

# 递减
cache.decrement("downloads", 1)        # -1

# 获取当前值
views = cache.get("page_views")
```

### 6. 函数缓存装饰器

```python
from kernel.db.optimization import CacheManager

cache = create_local_cache_manager()

# 使用装饰器缓存函数结果
@cache.cached(ttl=300)
def expensive_computation(x, y):
    """耗时的计算函数"""
    import time
    time.sleep(2)  # 模拟耗时操作
    return x ** y

# 第一次调用：执行函数并缓存结果（耗时 2 秒）
result1 = expensive_computation(2, 10)

# 第二次调用：直接从缓存返回（瞬间完成）
result2 = expensive_computation(2, 10)

# 自定义缓存键生成器
@cache.cached(
    ttl=600,
    key_builder=lambda user_id, dept: f"report:{dept}:{user_id}"
)
def generate_report(user_id, dept):
    """生成报告"""
    return f"Report for user {user_id} in {dept}"
```

## 高级用法

### LLM 响应缓存

```python
from kernel.db.optimization import create_redis_cache_manager
from kernel.db.core import create_redis_engine

# 使用 Redis 缓存 LLM 响应
redis_client = create_redis_engine(database="1")
llm_cache = create_redis_cache_manager(
    redis_client=redis_client,
    prefix="llm:",
    default_ttl=7200,  # 2 小时
    key_prefix="response"
)

@llm_cache.cached(ttl=3600)
def call_llm(prompt: str, model: str = "gpt-4"):
    """调用 LLM（带缓存）"""
    # 实际的 LLM 调用
    response = llm_client.chat(prompt, model=model)
    return response

# 相同的 prompt 会直接返回缓存结果，节省 API 调用
response1 = call_llm("什么是人工智能？")
response2 = call_llm("什么是人工智能？")  # 从缓存返回
```

### 会话管理

```python
# 使用 Redis 管理用户会话
session_cache = create_redis_cache_manager(
    redis_client=redis_client,
    prefix="session:",
    default_ttl=1800  # 30 分钟
)

# 创建会话
session_cache.set("session_abc123", {
    "user_id": 1001,
    "username": "alice",
    "permissions": ["read", "write"],
    "created_at": "2026-01-06T10:00:00Z"
}, ttl=1800)

# 获取会话
session_data = session_cache.get("session_abc123")

# 会话续期（刷新过期时间）
if session_cache.exists("session_abc123"):
    session_data = session_cache.get("session_abc123")
    session_cache.set("session_abc123", session_data, ttl=1800)
```

### 多层缓存策略

```python
from kernel.db.optimization import CacheManager, LocalCache, RedisCache

# L1: 本地内存缓存（快速）
local_backend = LocalCache(max_size=100, default_ttl=300)

# L2: Redis 缓存（持久）
redis_backend = RedisCache(
    redis_client=redis_client,
    prefix="app:",
    default_ttl=3600
)

class TwoLevelCache:
    """两级缓存"""
    def __init__(self):
        self.l1 = CacheManager(backend=local_backend)
        self.l2 = CacheManager(backend=redis_backend)
    
    def get(self, key: str):
        # 先查 L1
        value = self.l1.get(key)
        if value is not None:
            return value
        
        # 再查 L2
        value = self.l2.get(key)
        if value is not None:
            # 回填到 L1
            self.l1.set(key, value, ttl=300)
        return value
    
    def set(self, key: str, value, ttl=None):
        # 同时写入两级缓存
        self.l1.set(key, value, ttl=300)
        self.l2.set(key, value, ttl=ttl)

cache = TwoLevelCache()
```

## API 参考

### CacheManager

#### 构造函数
```python
CacheManager(
    backend: Optional[CacheBackend] = None,  # 缓存后端
    default_ttl: int = 3600,                 # 默认 TTL
    key_prefix: str = ""                     # 键前缀
)
```

#### 方法

| 方法 | 说明 |
|------|------|
| `get(key, default=None)` | 获取缓存值 |
| `set(key, value, ttl=None)` | 设置缓存值 |
| `delete(key)` | 删除缓存键 |
| `exists(key)` | 检查键是否存在 |
| `clear()` | 清空所有缓存 |
| `get_or_set(key, default_factory, ttl=None)` | 获取或设置 |
| `get_many(keys)` | 批量获取 |
| `set_many(mapping, ttl=None)` | 批量设置 |
| `delete_many(keys)` | 批量删除 |
| `increment(key, delta=1)` | 递增计数器 |
| `decrement(key, delta=1)` | 递减计数器 |
| `cached(ttl=None, key_builder=None)` | 装饰器 |

## 最佳实践

1. **选择合适的后端**
   - 开发环境：使用本地缓存
   - 生产环境：使用 Redis（支持分布式）

2. **设置合理的 TTL**
   - 频繁变化的数据：短 TTL（60-300 秒）
   - 静态数据：长 TTL（3600-86400 秒）
   - 会话数据：中等 TTL（1800-3600 秒）

3. **使用键前缀**
   - 便于管理和清理特定类型的缓存
   - 避免键冲突

4. **监控缓存命中率**
   - 定期检查缓存效果
   - 调整 TTL 和缓存策略

5. **处理缓存穿透**
   - 对空值也进行缓存（短 TTL）
   - 使用布隆过滤器

## 注意事项

- 本地缓存不支持跨进程共享
- Redis 缓存需要确保 Redis 服务可用
- 序列化的对象需要是可 pickle 的
- 计数器操作是原子的（Redis）或线程安全的（本地）
