"""基于 SQLAlchemy 构建的会话助手
Session helpers built on top of SQLAlchemy."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session, sessionmaker

from .exceptions import SessionError


class SessionManager:
    """为给定引擎创建和管理数据库会话
    Creates and manages database sessions for a given engine."""

    def __init__(self, engine) -> None:
        try:
            self._session_factory = sessionmaker(
                bind=engine,
                autoflush=False,
                autocommit=False,
                future=True,
            )
        except Exception as exc:  # pragma: no cover - defensive
            raise SessionError("Failed to initialize session factory") from exc

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """为一系列操作提供事务作用域
        Provide a transactional scope around a series of operations."""

        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
