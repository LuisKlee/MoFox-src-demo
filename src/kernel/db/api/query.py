"""轻量级查询规约，保持 CRUD 后端无关性
Lightweight query specification to keep CRUD backend-agnostic."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

from sqlalchemy import Select


@dataclass
class QuerySpec:
	"""可扩展到其他后端的查询描述
	Query description that can be extended for other backends.
	
	对于 SQLAlchemy / For SQLAlchemy:
	- filters: SQLAlchemy 过滤表达式列表 / List of SQLAlchemy filter expressions
	- order_by: SQLAlchemy 排序表达式列表 / List of SQLAlchemy order expressions
	
	对于 MongoDB / For MongoDB:
	- filters: 字典或字典列表（MongoDB 查询过滤器）/ Dict or List of dicts (MongoDB query filter)
	- order_by: 元组列表如 [("field_name", 1)] 升序，[("field_name", -1)] 降序
	  / List of tuples like [("field_name", 1)] for ascending, [("field_name", -1)] for descending
	
	对于 Redis / For Redis:
	- 不适用（Redis 不支持复杂查询）/ Not applicable (Redis doesn't support complex queries)
	"""

	filters: Union[List[object], dict] = field(default_factory=list)
	order_by: Union[List[object], List[tuple]] = field(default_factory=list)
	limit: Optional[int] = None
	offset: Optional[int] = None
	# MongoDB 特定字段 MongoDB-specific fields
	projection: Optional[dict] = None  # 包含/排除的字段 Fields to include/exclude


def apply_query_spec(statement: Select, spec: QuerySpec) -> Select:
	"""将查询规约应用到 SQLAlchemy select 语句
	Apply query spec to a SQLAlchemy select statement."""

	if spec.filters:
		if isinstance(spec.filters, list):
			statement = statement.filter(*spec.filters)
	if spec.order_by:
		if isinstance(spec.order_by, list):
			statement = statement.order_by(*spec.order_by)
	if spec.limit is not None:
		statement = statement.limit(spec.limit)
	if spec.offset is not None:
		statement = statement.offset(spec.offset)
	return statement


def apply_mongo_query_spec(cursor: Any, spec: QuerySpec) -> Any:
	"""将查询规约应用到 MongoDB 游标
	Apply query spec to a MongoDB cursor.
	
	参数 Args:
		cursor: PyMongo 游标 / PyMongo cursor
		spec: 带有 MongoDB 兼容字段的 QuerySpec / QuerySpec with MongoDB-compatible fields
	
	返回 Returns:
		应用了查询规约的修改后游标 / Modified cursor with query spec applied
	"""
	if spec.order_by and isinstance(spec.order_by, list):
		cursor = cursor.sort(spec.order_by)
	if spec.limit is not None:
		cursor = cursor.limit(spec.limit)
	if spec.offset is not None:
		cursor = cursor.skip(spec.offset)
	return cursor


__all__ = ["QuerySpec", "apply_query_spec", "apply_mongo_query_spec"]
