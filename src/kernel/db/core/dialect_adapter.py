"""方言适配器：将配置转换为 SQLAlchemy 引擎
Dialect adapters translate config into SQLAlchemy engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .exceptions import UnsupportedDialectError


@dataclass
class EngineConfig:
    """最小化引擎配置，覆盖常见 SQL 后端
    Minimal engine configuration to cover common SQL backends."""

    dialect: str
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    host: str = "localhost"
    port: Optional[int] = None
    echo: bool = False
    pool_size: int = 5
    pool_timeout: int = 30
    connect_args: Dict[str, Any] = field(default_factory=dict)
    create_if_missing: bool = True

    @property
    def is_sqlite_memory(self) -> bool:
        return self.database in {":memory:", "memory"}


class DialectAdapter(ABC):
    """适配器接口：将配置转换为具体引擎
    Adapter interface for turning config into a concrete engine."""

    name: str

    @abstractmethod
    def create_engine(self, config: EngineConfig) -> Engine:
        """从提供的配置创建 SQLAlchemy 引擎
        Create a SQLAlchemy engine from the provided config."""


class SQLiteAdapter(DialectAdapter):
    """SQLite 适配器：为本地开发提供合理默认值
    SQLite adapter with sensible defaults for local development."""

    name = "sqlite"

    def create_engine(self, config: EngineConfig) -> Engine:
        if config.dialect != self.name:
            raise UnsupportedDialectError(f"Adapter {self.name} cannot handle {config.dialect}")

        if not config.is_sqlite_memory and config.create_if_missing:
            db_path = Path(config.database)
            db_path.parent.mkdir(parents=True, exist_ok=True)

        url = self._build_url(config)
        connect_args = {"check_same_thread": False}
        connect_args.update(config.connect_args)

        return create_engine(
            url,
            echo=config.echo,
            pool_pre_ping=True,
            pool_size=config.pool_size,
            pool_timeout=config.pool_timeout,
            connect_args=connect_args,
            future=True,
        )

    def _build_url(self, config: EngineConfig) -> str:
        if config.is_sqlite_memory:
            return "sqlite://"
        absolute_path = Path(config.database).expanduser().resolve()
        return f"sqlite:///{absolute_path}"


class MySQLAdapter(DialectAdapter):
    """MySQL 适配器：支持 pymysql 和 aiomysql 驱动
    MySQL adapter with support for both pymysql and aiomysql drivers."""

    name = "mysql"

    def create_engine(self, config: EngineConfig) -> Engine:
        if config.dialect != self.name:
            raise UnsupportedDialectError(f"Adapter {self.name} cannot handle {config.dialect}")

        url = self._build_url(config)
        connect_args = {}
        connect_args.update(config.connect_args)

        return create_engine(
            url,
            echo=config.echo,
            pool_pre_ping=True,
            pool_size=config.pool_size,
            pool_timeout=config.pool_timeout,
            connect_args=connect_args,
            future=True,
        )

    def _build_url(self, config: EngineConfig) -> str:
        """构建 MySQL 连接 URL
        Build MySQL connection URL.
        
        格式 Format: mysql+pymysql://user:password@host:port/database
        如果 connect_args 未指定，驱动默认为 pymysql
        Driver defaults to pymysql if not specified in connect_args.
        """
        driver = config.connect_args.get("driver", "pymysql")
        
        # 构建凭证 Build credentials
        auth = ""
        if config.username:
            auth = config.username
            if config.password:
                auth += f":{config.password}"
            auth += "@"
        
        # 构建主机和端口 Build host and port
        port = config.port or 3306
        host_port = f"{config.host}:{port}"
        
        return f"mysql+{driver}://{auth}{host_port}/{config.database}"


class PostgresAdapter(DialectAdapter):
    """PostgreSQL 适配器：支持 psycopg2 和 asyncpg 驱动
    PostgreSQL adapter with support for psycopg2 and asyncpg drivers."""

    name = "postgresql"

    def create_engine(self, config: EngineConfig) -> Engine:
        if config.dialect not in {self.name, "postgres"}:
            raise UnsupportedDialectError(f"Adapter {self.name} cannot handle {config.dialect}")

        url = self._build_url(config)
        connect_args = {}
        connect_args.update(config.connect_args)

        return create_engine(
            url,
            echo=config.echo,
            pool_pre_ping=True,
            pool_size=config.pool_size,
            pool_timeout=config.pool_timeout,
            connect_args=connect_args,
            future=True,
        )

    def _build_url(self, config: EngineConfig) -> str:
        """构建 PostgreSQL 连接 URL
        Build PostgreSQL connection URL.
        
        格式 Format: postgresql+psycopg2://user:password@host:port/database
        如果 connect_args 未指定，驱动默认为 psycopg2
        Driver defaults to psycopg2 if not specified in connect_args.
        """
        driver = config.connect_args.get("driver", "psycopg2")
        
        # 构建凭证 Build credentials
        auth = ""
        if config.username:
            auth = config.username
            if config.password:
                auth += f":{config.password}"
            auth += "@"
        
        # 构建主机和端口 Build host and port
        port = config.port or 5432
        host_port = f"{config.host}:{port}"
        
        return f"postgresql+{driver}://{auth}{host_port}/{config.database}"


class RedisAdapter(DialectAdapter):
    """Redis 适配器（非 SQLAlchemy，返回 redis 客户端封装）
    Redis adapter (non-SQLAlchemy, returns redis client wrapper)."""

    name = "redis"

    def create_engine(self, config: EngineConfig) -> Any:
        """创建 Redis 连接池并封装为'引擎'
        Create a Redis connection pool wrapped as an 'engine'."""
        if config.dialect != self.name:
            raise UnsupportedDialectError(f"Adapter {self.name} cannot handle {config.dialect}")

        try:
            import redis
        except ImportError as exc:
            raise ImportError("redis package is required for Redis adapter") from exc

        # Redis 使用整数索引作为数据库（通常是 0-15）
        # Redis uses database as integer index (0-15 typically)
        db_index = int(config.database) if config.database.isdigit() else 0
        
        # 构建连接参数 Build connection kwargs
        connection_kwargs = {
            "host": config.host,
            "port": config.port or 6379,
            "db": db_index,
            "decode_responses": True,
            "max_connections": config.pool_size,
            "socket_timeout": config.pool_timeout,
        }
        
        if config.password:
            connection_kwargs["password"] = config.password
        
        connection_kwargs.update(config.connect_args)
        
        # 返回封装为类引擎对象的连接池
        # Return connection pool wrapped as engine-like object
        pool = redis.ConnectionPool(**connection_kwargs)
        return redis.Redis(connection_pool=pool)

    def _build_url(self, config: EngineConfig) -> str:
        """构建 Redis URL（用于文档目的）
        Build Redis URL for documentation purposes."""
        auth = f":{config.password}@" if config.password else ""
        port = config.port or 6379
        return f"redis://{auth}{config.host}:{port}/{config.database}"


class MongoDBAdapter(DialectAdapter):
    """MongoDB 适配器（非 SQLAlchemy，返回 pymongo 客户端）
    MongoDB adapter (non-SQLAlchemy, returns pymongo client)."""

    name = "mongodb"

    def create_engine(self, config: EngineConfig) -> Any:
        """创建 MongoDB 客户端
        Create a MongoDB client."""
        if config.dialect not in {self.name, "mongo"}:
            raise UnsupportedDialectError(f"Adapter {self.name} cannot handle {config.dialect}")

        try:
            from pymongo import MongoClient
        except ImportError as exc:
            raise ImportError("pymongo package is required for MongoDB adapter") from exc

        url = self._build_url(config)
        
        # MongoDB 连接选项 MongoDB connection options
        client_kwargs = {
            "maxPoolSize": config.pool_size,
            "serverSelectionTimeoutMS": config.pool_timeout * 1000,
        }
        
        client_kwargs.update(config.connect_args)
        
        # 创建客户端并返回数据库引用
        # Create client and return database reference
        client = MongoClient(url, **client_kwargs)
        # 返回包含客户端和数据库的封装器
        # Return a wrapper with both client and database
        return MongoDBEngine(client, config.database)

    def _build_url(self, config: EngineConfig) -> str:
        """构建 MongoDB 连接 URL
        Build MongoDB connection URL.
        
        格式 Format: mongodb://user:password@host:port/
        """
        # 构建凭证 Build credentials
        auth = ""
        if config.username:
            auth = config.username
            if config.password:
                auth += f":{config.password}"
            auth += "@"
        
        # 构建主机和端口 Build host and port
        port = config.port or 27017
        host_port = f"{config.host}:{port}"
        
        return f"mongodb://{auth}{host_port}/"


class MongoDBEngine:
    """MongoDB 客户端封装器：提供类引擎接口
    Wrapper for MongoDB client to provide engine-like interface."""

    def __init__(self, client: Any, database_name: str):
        self.client = client
        self.database_name = database_name
        self._database = client[database_name]

    @property
    def database(self):
        """获取数据库引用
        Get the database reference."""
        return self._database

    def dispose(self):
        """关闭 MongoDB 客户端连接
        Close the MongoDB client connection."""
        self.client.close()

    def __repr__(self):
        return f"MongoDBEngine(database={self.database_name})"
