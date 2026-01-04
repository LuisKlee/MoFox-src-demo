"""Simple CRUD abstraction built on SQLAlchemy with room for other backends."""

from __future__ import annotations

from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.session import SessionManager
from .query import QuerySpec, apply_query_spec

ModelT = TypeVar("ModelT")


class CRUDRepository(Generic[ModelT]):
	"""Backend-agnostic CRUD interface."""

	def add(self, session: Any, obj: ModelT, *, flush: bool = False) -> ModelT:
		raise NotImplementedError

	def get(self, session: Any, model: Type[ModelT], obj_id: Any) -> Optional[ModelT]:
		raise NotImplementedError

	def list(self, session: Any, model: Type[ModelT], query_spec: Optional[QuerySpec] = None) -> Sequence[ModelT]:
		raise NotImplementedError

	def delete(self, session: Any, obj: ModelT) -> None:
		raise NotImplementedError

	def update_fields(self, session: Any, obj: ModelT, fields: dict[str, Any]) -> ModelT:
		raise NotImplementedError


class SQLAlchemyCRUDRepository(CRUDRepository[ModelT]):
	"""Default CRUD implementation for SQLAlchemy models."""

	def __init__(self, session_manager: SessionManager) -> None:
		self._session_manager = session_manager

	def add(self, session: Session, obj: ModelT, *, flush: bool = False) -> ModelT:
		session.add(obj)
		if flush:
			session.flush()
		return obj

	def get(self, session: Session, model: Type[ModelT], obj_id: Any) -> Optional[ModelT]:
		return session.get(model, obj_id)

	def list(self, session: Session, model: Type[ModelT], query_spec: Optional[QuerySpec] = None) -> Sequence[ModelT]:
		stmt = select(model)
		if query_spec:
			stmt = apply_query_spec(stmt, query_spec)
		return list(session.execute(stmt).scalars().all())

	def delete(self, session: Session, obj: ModelT) -> None:
		session.delete(obj)

	def update_fields(self, session: Session, obj: ModelT, fields: dict[str, Any]) -> ModelT:
		for key, value in fields.items():
			setattr(obj, key, value)
		session.flush()
		return obj

	def session_scope(self):
		"""Expose the underlying session scope helper."""

		return self._session_manager.session_scope()


__all__ = ["CRUDRepository", "SQLAlchemyCRUDRepository"]
