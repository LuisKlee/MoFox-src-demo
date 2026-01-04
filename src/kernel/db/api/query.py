"""Lightweight query specification to keep CRUD backend-agnostic."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from sqlalchemy import Select


@dataclass
class QuerySpec:
	"""Query description that can be extended for other backends."""

	filters: List[object] = field(default_factory=list)
	order_by: List[object] = field(default_factory=list)
	limit: Optional[int] = None
	offset: Optional[int] = None


def apply_query_spec(statement: Select, spec: QuerySpec) -> Select:
	"""Apply query spec to a SQLAlchemy select statement."""

	if spec.filters:
		statement = statement.filter(*spec.filters)
	if spec.order_by:
		statement = statement.order_by(*spec.order_by)
	if spec.limit is not None:
		statement = statement.limit(spec.limit)
	if spec.offset is not None:
		statement = statement.offset(spec.offset)
	return statement


__all__ = ["QuerySpec", "apply_query_spec"]
