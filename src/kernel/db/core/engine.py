"""Engine registry and creation helpers."""

from __future__ import annotations

from typing import Dict, Mapping, Optional

from sqlalchemy.engine import Engine

from .dialect_adapter import DialectAdapter, EngineConfig, SQLiteAdapter
from .exceptions import EngineAlreadyExistsError, EngineNotInitializedError, UnsupportedDialectError


class EngineManager:
    """Manages database engines keyed by name."""

    def __init__(self) -> None:
        self._adapters: Dict[str, DialectAdapter] = {"sqlite": SQLiteAdapter()}
        self._engines: Dict[str, Engine] = {}
        self._default_name = "default"

    def register_adapter(self, adapter: DialectAdapter) -> None:
        """Register a new dialect adapter for future engine creation."""

        self._adapters[adapter.name] = adapter

    def create(self, config: EngineConfig, name: Optional[str] = None) -> Engine:
        """Create and store an engine using the chosen adapter."""

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
        """Retrieve a registered engine by name."""

        engine_name = name or self._default_name
        try:
            return self._engines[engine_name]
        except KeyError as exc:
            raise EngineNotInitializedError(f"Engine '{engine_name}' is not initialized") from exc

    def dispose(self, name: Optional[str] = None) -> None:
        """Dispose and remove a registered engine."""

        engine_name = name or self._default_name
        engine = self._engines.pop(engine_name, None)
        if engine:
            engine.dispose()

    def list_engines(self) -> Mapping[str, Engine]:
        """Return a shallow copy of registered engines."""

        return dict(self._engines)


def create_sqlite_engine(
    database: str,
    name: str = "default",
    echo: bool = False,
    pool_size: int = 5,
    pool_timeout: int = 30,
    connect_args: Optional[Dict[str, object]] = None,
) -> Engine:
    """Convenience helper to bootstrap a SQLite engine and register it as default."""

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


__all__ = ["EngineManager", "EngineConfig", "create_sqlite_engine"]
