"""Redis 缓存实现
Redis cache implementation."""

from __future__ import annotations

import pickle
from typing import Any, Optional

from .cache_backend import CacheBackend


class RedisCache(CacheBackend):
    """Redis 缓存实现
    Redis cache implementation."""
    
    def __init__(
        self,
        redis_client: Any,
        prefix: str = "cache:",
        default_ttl: Optional[int] = 3600,
        serialize: bool = True
    ):
        """初始化 Redis 缓存
        Initialize Redis cache.
        
        参数 Args:
            redis_client: Redis 客户端实例 / Redis client instance
            prefix: 缓存键前缀 / Cache key prefix
            default_ttl: 默认过期时间（秒）/ Default TTL in seconds
            serialize: 是否序列化值 / Whether to serialize values
        """
        self._client = redis_client
        self._prefix = prefix
        self._default_ttl = default_ttl
        self._serialize = serialize
    
    def _make_key(self, key: str) -> str:
        """生成带前缀的完整键
        Generate prefixed cache key."""
        return f"{self._prefix}{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """序列化值
        Serialize value."""
        if self._serialize:
            return pickle.dumps(value)
        return str(value).encode('utf-8')
    
    def _deserialize_value(self, data: bytes) -> Any:
        """反序列化值
        Deserialize value."""
        if data is None:
            return None
        if self._serialize:
            try:
                return pickle.loads(data)
            except Exception:
                return data.decode('utf-8')
        return data.decode('utf-8')
    
    def get(self, key: str) -> Optional[Any]:
        """从缓存中获取值
        Get value from cache by key."""
        cache_key = self._make_key(key)
        data = self._client.get(cache_key)
        return self._deserialize_value(data)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值
        Set value in cache."""
        cache_key = self._make_key(key)
        serialized_value = self._serialize_value(value)
        
        if ttl is None:
            ttl = self._default_ttl
        
        if ttl is not None and ttl > 0:
            return bool(self._client.setex(cache_key, ttl, serialized_value))
        else:
            return bool(self._client.set(cache_key, serialized_value))
    
    def delete(self, key: str) -> bool:
        """删除缓存键
        Delete cache key."""
        cache_key = self._make_key(key)
        return bool(self._client.delete(cache_key))
    
    def exists(self, key: str) -> bool:
        """检查键是否存在
        Check if key exists."""
        cache_key = self._make_key(key)
        return bool(self._client.exists(cache_key))
    
    def clear(self) -> bool:
        """清空所有缓存（使用前缀匹配）
        Clear all cache entries (using prefix pattern)."""
        pattern = f"{self._prefix}*"
        keys = self._client.keys(pattern)
        if keys:
            self._client.delete(*keys)
        return True
    
    def get_many(self, keys: list[str]) -> dict[str, Any]:
        """批量获取多个键的值
        Get multiple values by keys."""
        if not keys:
            return {}
        
        cache_keys = [self._make_key(key) for key in keys]
        values = self._client.mget(cache_keys)
        
        result = {}
        for i, key in enumerate(keys):
            if values[i] is not None:
                result[key] = self._deserialize_value(values[i])
        
        return result
    
    def set_many(self, mapping: dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置多个键值对
        Set multiple key-value pairs."""
        if not mapping:
            return True
        
        # 使用 pipeline 提高性能 / Use pipeline for better performance
        pipe = self._client.pipeline()
        
        for key, value in mapping.items():
            cache_key = self._make_key(key)
            serialized_value = self._serialize_value(value)
            
            if ttl is None:
                ttl = self._default_ttl
            
            if ttl is not None and ttl > 0:
                pipe.setex(cache_key, ttl, serialized_value)
            else:
                pipe.set(cache_key, serialized_value)
        
        pipe.execute()
        return True
    
    def delete_many(self, keys: list[str]) -> int:
        """批量删除多个键
        Delete multiple keys."""
        if not keys:
            return 0
        
        cache_keys = [self._make_key(key) for key in keys]
        return self._client.delete(*cache_keys)
    
    def increment(self, key: str, delta: int = 1) -> int:
        """递增计数器
        Increment counter."""
        cache_key = self._make_key(key)
        return self._client.incrby(cache_key, delta)
    
    def decrement(self, key: str, delta: int = 1) -> int:
        """递减计数器
        Decrement counter."""
        cache_key = self._make_key(key)
        return self._client.decrby(cache_key, delta)
    
    def expire(self, key: str, ttl: int) -> bool:
        """设置键的过期时间
        Set expiration time for a key.
        
        参数 Args:
            key: 缓存键 / Cache key
            ttl: 过期时间（秒）/ Time to live in seconds
            
        返回 Returns:
            是否设置成功 / True if successful
        """
        cache_key = self._make_key(key)
        return bool(self._client.expire(cache_key, ttl))
    
    def ttl(self, key: str) -> int:
        """获取键的剩余生存时间
        Get remaining time to live for a key.
        
        参数 Args:
            key: 缓存键 / Cache key
            
        返回 Returns:
            剩余秒数，-1 表示永不过期，-2 表示键不存在
            Remaining seconds, -1 for no expiration, -2 for key not exists
        """
        cache_key = self._make_key(key)
        return self._client.ttl(cache_key)


__all__ = ["RedisCache"]
