"""引擎注册表与创建帮助器
Engine registry and creation helpers."""

from __future__ import annotations

from typing import Dict, Mapping, Optional

from sqlalchemy.engine import Engine

from .dialect_adapter import (
    DialectAdapter,
    EngineConfig,
    MongoDBAdapter,
    MySQLAdapter,
    PostgresAdapter,
    RedisAdapter,
    SQLiteAdapter,
)
from .exceptions import EngineAlreadyExistsError, EngineNotInitializedError, UnsupportedDialectError


class EngineManager:
    """按名称管理数据库引擎
    Manages database engines keyed by name."""

    def __init__(self) -> None:
        self._adapters: Dict[str, DialectAdapter] = {
            "sqlite": SQLiteAdapter(),
            "mysql": MySQLAdapter(),
            "postgresql": PostgresAdapter(),
            "postgres": PostgresAdapter(),
            "redis": RedisAdapter(),
            "mongodb": MongoDBAdapter(),
            "mongo": MongoDBAdapter(),
        }
        self._engines: Dict[str, Engine] = {}
        self._default_name = "default"

    def register_adapter(self, adapter: DialectAdapter) -> None:
        """注册新的方言适配器，用于未来的引擎创建
        Register a new dialect adapter for future engine creation."""

        self._adapters[adapter.name] = adapter

    def create(self, config: EngineConfig, name: Optional[str] = None) -> Engine:
        """使用选定的适配器创建并存储引擎
        Create and store an engine using the chosen adapter."""

        engine_name = name or self._default_name
        if engine_name in self._engines:
            raise EngineAlreadyExistsError(f"Engine '{engine_name}' already exists")

        adapter = self._adapters.get(config.dialect)
        if not adapter:
            raise UnsupportedDialectError(f"Dialect '{config.dialect}' is not supported")

        engine = adapter.create_engine(config)
        self._engines[engine_name] = engine
        return engine

    def get(self, name: Optional[str] = None) -> Engine:
        """按名称检索已注册的引擎
        Retrieve a registered engine by name."""

        engine_name = name or self._default_name
        try:
            return self._engines[engine_name]
        except KeyError as exc:
            raise EngineNotInitializedError(f"Engine '{engine_name}' is not initialized") from exc

    def dispose(self, name: Optional[str] = None) -> None:
        """释放并移除已注册的引擎
        Dispose and remove a registered engine."""

        engine_name = name or self._default_name
        engine = self._engines.pop(engine_name, None)
        if engine:
            engine.dispose()

    def list_engines(self) -> Mapping[str, Engine]:
        """返回已注册引擎的浅拷贝
        Return a shallow copy of registered engines."""

        return dict(self._engines)


def create_sqlite_engine(
    database: str,
    name: str = "default",
    echo: bool = False,
    pool_size: int = 5,
    pool_timeout: int = 30,
    connect_args: Optional[Dict[str, object]] = None,
) -> Engine:
    """便捷帮助器：启动 SQLite 引擎并注册为默认
    Convenience helper to bootstrap a SQLite engine and register it as default."""

    manager = EngineManager()
    config = EngineConfig(
        dialect="sqlite",
        database=database,
        echo=echo,
        pool_size=pool_size,
        pool_timeout=pool_timeout,
        connect_args=connect_args or {},
    )
    return manager.create(config, name=name)


def create_mysql_engine(
    database: str,
    username: str,
    password: str,
    host: str = "localhost",
    port: int = 3306,
    name: str = "default",
    echo: bool = False,
    pool_size: int = 5,
    pool_timeout: int = 30,
    connect_args: Optional[Dict[str, object]] = None,
) -> Engine:
    """便捷帮助器：启动 MySQL 引擎并注册为默认
    Convenience helper to bootstrap a MySQL engine and register it as default."""

    manager = EngineManager()
    config = EngineConfig(
        dialect="mysql",
        database=database,
        username=username,
        password=password,
        host=host,
        port=port,
        echo=echo,
        pool_size=pool_size,
        pool_timeout=pool_timeout,
        connect_args=connect_args or {},
    )
    return manager.create(config, name=name)


def create_postgres_engine(
    database: str,
    username: str,
    password: str,
    host: str = "localhost",
    port: int = 5432,
    name: str = "default",
    echo: bool = False,
    pool_size: int = 5,
    pool_timeout: int = 30,
    connect_args: Optional[Dict[str, object]] = None,
) -> Engine:
    """便捷帮助器：启动 PostgreSQL 引擎并注册为默认
    Convenience helper to bootstrap a PostgreSQL engine and register it as default."""

    manager = EngineManager()
    config = EngineConfig(
        dialect="postgresql",
        database=database,
        username=username,
        password=password,
        host=host,
        port=port,
        echo=echo,
        pool_size=pool_size,
        pool_timeout=pool_timeout,
        connect_args=connect_args or {},
    )
    return manager.create(config, name=name)


def create_redis_engine(
    database: str = "0",
    host: str = "localhost",
    port: int = 6379,
    password: Optional[str] = None,
    name: str = "default",
    pool_size: int = 10,
    pool_timeout: int = 30,
    connect_args: Optional[Dict[str, object]] = None,
) -> object:
    """便捷帮助器：创建 Redis 连接并注册
    Convenience helper to create a Redis connection and register it."""

    manager = EngineManager()
    config = EngineConfig(
        dialect="redis",
        database=database,
        password=password,
        host=host,
        port=port,
        pool_size=pool_size,
        pool_timeout=pool_timeout,
        connect_args=connect_args or {},
    )
    return manager.create(config, name=name)


def create_mongodb_engine(
    database: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    host: str = "localhost",
    port: int = 27017,
    name: str = "default",
    pool_size: int = 10,
    pool_timeout: int = 30,
    connect_args: Optional[Dict[str, object]] = None,
) -> object:
    """便捷帮助器：创建 MongoDB 连接并注册
    Convenience helper to create a MongoDB connection and register it."""

    manager = EngineManager()
    config = EngineConfig(
        dialect="mongodb",
        database=database,
        username=username,
        password=password,
        host=host,
        port=port,
        pool_size=pool_size,
        pool_timeout=pool_timeout,
        connect_args=connect_args or {},
    )
    return manager.create(config, name=name)


__all__ = [
    "EngineManager",
    "EngineConfig",
    "create_sqlite_engine",
    "create_mysql_engine",
    "create_postgres_engine",
    "create_redis_engine",
    "create_mongodb_engine",
]
