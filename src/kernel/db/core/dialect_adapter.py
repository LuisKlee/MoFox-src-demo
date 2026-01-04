"""Dialect adapters translate config into SQLAlchemy engines."""

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
    """Minimal engine configuration to cover common SQL backends."""

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
    """Adapter interface for turning config into a concrete engine."""

    name: str

    @abstractmethod
    def create_engine(self, config: EngineConfig) -> Engine:
        """Create a SQLAlchemy engine from the provided config."""


class SQLiteAdapter(DialectAdapter):
    """SQLite adapter with sensible defaults for local development."""

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
