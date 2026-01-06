"""数据库优化模块：缓存管理
Database optimization module: Cache management."""

from .backends import CacheBackend, CacheEntry, LocalCache, RedisCache
from .cache_manager import (
    CacheManager,
    create_local_cache_manager,
    create_redis_cache_manager,
)

__all__ = [
    # 缓存后端 Cache backends
    "CacheBackend",
    "LocalCache",
    "RedisCache",
    "CacheEntry",
    # 缓存管理器 Cache manager
    "CacheManager",
    "create_local_cache_manager",
    "create_redis_cache_manager",
]
