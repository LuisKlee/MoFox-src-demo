"""Database core exports."""

from .dialect_adapter import DialectAdapter, EngineConfig, SQLiteAdapter
from .engine import EngineManager, create_sqlite_engine
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
    "EngineManager",
    "create_sqlite_engine",
    "SessionManager",
]
