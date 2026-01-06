"""Database core exports."""

from .dialect_adapter import (
    DialectAdapter,
    EngineConfig,
    MongoDBAdapter,
    MongoDBEngine,
    MySQLAdapter,
    PostgresAdapter,
    RedisAdapter,
    SQLiteAdapter,
)
from .engine import (
    EngineManager,
    create_mongodb_engine,
    create_mysql_engine,
    create_postgres_engine,
    create_redis_engine,
    create_sqlite_engine,
)
from .exceptions import (
    DatabaseError,
    EngineAlreadyExistsError,
    EngineNotInitializedError,
    SessionError,
    UnsupportedDialectError,
)
from .session import SessionManager

__all__ = [
    "DatabaseError",
    "EngineAlreadyExistsError",
    "EngineNotInitializedError",
    "SessionError",
    "UnsupportedDialectError",
    "DialectAdapter",
    "EngineConfig",
    "SQLiteAdapter",
    "MySQLAdapter",
    "PostgresAdapter",
    "RedisAdapter",
    "MongoDBAdapter",
    "MongoDBEngine",
    "EngineManager",
    "create_sqlite_engine",
    "create_mysql_engine",
    "create_postgres_engine",
    "create_redis_engine",
    "create_mongodb_engine",
    "SessionManager",
]
