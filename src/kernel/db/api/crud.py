"""基于 SQLAlchemy 构建的简单 CRUD 抽象，为其他后端预留空间
Simple CRUD abstraction built on SQLAlchemy with room for other backends."""

from __future__ import annotations

from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.session import SessionManager
from .query import QuerySpec, apply_query_spec
from kernel.logger import get_logger, MetadataContext

logger = get_logger(__name__)

ModelT = TypeVar("ModelT")


class CRUDRepository(Generic[ModelT]):
	"""后端无关的 CRUD 接口
	Backend-agnostic CRUD interface."""

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
	"""针对 SQLAlchemy 模型的默认 CRUD 实现
	Default CRUD implementation for SQLAlchemy models."""

	def __init__(self, session_manager: SessionManager) -> None:
		self._session_manager = session_manager

	def add(self, session: Session, obj: ModelT, *, flush: bool = False) -> ModelT:
		model_name = type(obj).__name__
		
		session.add(obj)
		if flush:
			session.flush()
		
		logger.debug(
			f"数据库添加操作: {model_name}",
			extra={
				'operation': 'add',
				'model': model_name,
				'flushed': flush
			}
		)
		return obj

	def get(self, session: Session, model: Type[ModelT], obj_id: Any) -> Optional[ModelT]:
		result = session.get(model, obj_id)
		
		logger.debug(
			f"数据库查询操作: {model.__name__}",
			extra={
				'operation': 'get',
				'model': model.__name__,
				'id': obj_id,
				'found': result is not None
			}
		)
		return result

	def list(self, session: Session, model: Type[ModelT], query_spec: Optional[QuerySpec] = None) -> Sequence[ModelT]:
		stmt = select(model)
		if query_spec:
			stmt = apply_query_spec(stmt, query_spec)
		results = list(session.execute(stmt).scalars().all())
		
		logger.debug(
			f"数据库列表查询: {model.__name__}",
			extra={
				'operation': 'list',
				'model': model.__name__,
				'has_query_spec': query_spec is not None,
				'result_count': len(results),
				'limit': query_spec.limit if query_spec else None,
				'offset': query_spec.offset if query_spec else None
			}
		)
		return results

	def delete(self, session: Session, obj: ModelT) -> None:
		model_name = type(obj).__name__
		
		session.delete(obj)
		
		logger.info(
			f"数据库删除操作: {model_name}",
			extra={
				'operation': 'delete',
				'model': model_name
			}
		)

	def update_fields(self, session: Session, obj: ModelT, fields: dict[str, Any]) -> ModelT:
		model_name = type(obj).__name__
		
		for key, value in fields.items():
			setattr(obj, key, value)
		session.flush()
		
		logger.info(
			f"数据库更新操作: {model_name}",
			extra={
				'operation': 'update',
				'model': model_name,
				'fields_updated': list(fields.keys()),
				'field_count': len(fields)
			}
		)
		return obj

	def session_scope(self):
		"""暴露底层的 session 作用域帮助器
		Expose the underlying session scope helper."""

		return self._session_manager.session_scope()


class RedisRepository:
	"""针对 Redis 操作的仓库模式
	Repository pattern for Redis operations."""

	def __init__(self, redis_client: Any) -> None:
		"""使用 Redis 客户端初始化
		Initialize with a Redis client."""
		self._client = redis_client
		logger.info(
			"Redis 仓库已初始化",
			extra={'repository_type': 'redis'}
		)

	# 字符串操作 String operations
	def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
		"""设置键值对，可选过期时间（秒）
		Set a key-value pair with optional expiration time (seconds)."""
		result = self._client.set(key, value, ex=ex)
		
		logger.debug(
			f"Redis SET 操作: {key}",
			extra={
				'operation': 'set',
				'key': key,
				'expiration': ex,
				'success': result
			}
		)
		return result

	def get(self, key: str) -> Optional[str]:
		"""按键获取值
		Get value by key."""
		result = self._client.get(key)
		
		logger.debug(
			f"Redis GET 操作: {key}",
			extra={
				'operation': 'get',
				'key': key,
				'found': result is not None
			}
		)
		return result

	def delete(self, *keys: str) -> int:
		"""删除一个或多个键
		Delete one or more keys."""
		count = self._client.delete(*keys)
		
		logger.info(
			f"Redis DELETE 操作",
			extra={
				'operation': 'delete',
				'keys': list(keys),
				'deleted_count': count
			}
		)
		return count

	def exists(self, *keys: str) -> int:
		"""检查键是否存在
		Check if keys exist."""
		return self._client.exists(*keys)

	def expire(self, key: str, seconds: int) -> bool:
		"""为键设置过期时间
		Set expiration time for a key."""
		return self._client.expire(key, seconds)

	# 哈希操作 Hash operations
	def hset(self, name: str, key: Optional[str] = None, value: Optional[str] = None, mapping: Optional[dict] = None) -> int:
		"""设置哈希字段
		Set hash field(s)."""
		return self._client.hset(name, key, value, mapping=mapping)

	def hget(self, name: str, key: str) -> Optional[str]:
		"""获取哈希字段值
		Get hash field value."""
		return self._client.hget(name, key)

	def hgetall(self, name: str) -> dict:
		"""获取所有哈希字段和值
		Get all hash fields and values."""
		return self._client.hgetall(name)

	def hdel(self, name: str, *keys: str) -> int:
		"""删除哈希字段
		Delete hash field(s)."""
		return self._client.hdel(name, *keys)

	# 列表操作 List operations
	def lpush(self, name: str, *values: Any) -> int:
		"""将值推入列表头部
		Push values to the head of a list."""
		return self._client.lpush(name, *values)

	def rpush(self, name: str, *values: Any) -> int:
		"""将值推入列表尾部
		Push values to the tail of a list."""
		return self._client.rpush(name, *values)

	def lpop(self, name: str) -> Optional[str]:
		"""移除并返回列表的第一个元素
		Remove and return the first element of a list."""
		return self._client.lpop(name)

	def rpop(self, name: str) -> Optional[str]:
		"""移除并返回列表的最后一个元素
		Remove and return the last element of a list."""
		return self._client.rpop(name)

	def lrange(self, name: str, start: int, end: int) -> list:
		"""从列表中获取一系列元素
		Get a range of elements from a list."""
		return self._client.lrange(name, start, end)

	# 集合操作 Set operations
	def sadd(self, name: str, *values: Any) -> int:
		"""向集合添加成员
		Add members to a set."""
		return self._client.sadd(name, *values)

	def smembers(self, name: str) -> set:
		"""获取集合的所有成员
		Get all members of a set."""
		return self._client.smembers(name)

	def srem(self, name: str, *values: Any) -> int:
		"""从集合中移除成员
		Remove members from a set."""
		return self._client.srem(name, *values)

	# 有序集合操作 Sorted set operations
	def zadd(self, name: str, mapping: dict, **kwargs) -> int:
		"""向有序集合添加带分数的成员
		Add members to a sorted set with scores."""
		return self._client.zadd(name, mapping, **kwargs)

	def zrange(self, name: str, start: int, end: int, withscores: bool = False) -> list:
		"""按索引从有序集合中获取范围
		Get a range from a sorted set by index."""
		return self._client.zrange(name, start, end, withscores=withscores)

	def zrem(self, name: str, *values: Any) -> int:
		"""从有序集合中移除成员
		Remove members from a sorted set."""
		return self._client.zrem(name, *values)

	@property
	def client(self):
		"""访问底层 Redis 客户端以进行高级操作
		Access underlying Redis client for advanced operations."""
		return self._client


class MongoDBRepository:
	"""针对 MongoDB 操作的仓库模式
	Repository pattern for MongoDB operations."""

	def __init__(self, mongo_engine: Any) -> None:
		"""使用 MongoDBEngine 实例初始化
		Initialize with a MongoDBEngine instance."""
		self._engine = mongo_engine
		self._db = mongo_engine.database
		
		logger.info(
			"MongoDB 仓库已初始化",
			extra={
				'repository_type': 'mongodb',
				'database': self._db.name
			}
		)

	def collection(self, name: str):
		"""按名称获取集合
		Get a collection by name."""
		return self._db[name]

	# 文档操作 Document operations
	def insert_one(self, collection_name: str, document: dict) -> Any:
		"""插入单个文档
		Insert a single document."""
		result = self._db[collection_name].insert_one(document)
		
		logger.debug(
			f"MongoDB 插入文档: {collection_name}",
			extra={
				'operation': 'insert_one',
				'collection': collection_name,
				'inserted_id': str(result.inserted_id)
			}
		)
		return result

	def insert_many(self, collection_name: str, documents: list[dict]) -> Any:
		"""插入多个文档
		Insert multiple documents."""
		result = self._db[collection_name].insert_many(documents)
		
		logger.info(
			f"MongoDB 批量插入: {collection_name}",
			extra={
				'operation': 'insert_many',
				'collection': collection_name,
				'document_count': len(documents),
				'inserted_count': len(result.inserted_ids)
			}
		)
		return result

	def find_one(self, collection_name: str, filter: dict, projection: Optional[dict] = None) -> Optional[dict]:
		"""查找单个文档
		Find a single document."""
		result = self._db[collection_name].find_one(filter, projection)
		
		logger.debug(
			f"MongoDB 查询单个文档: {collection_name}",
			extra={
				'operation': 'find_one',
				'collection': collection_name,
				'has_filter': bool(filter),
				'has_projection': projection is not None,
				'found': result is not None
			}
		)
		return result

	def find(self, collection_name: str, filter: dict, query_spec: Optional[QuerySpec] = None) -> list[dict]:
		"""查找多个文档，可选查询规约
		Find multiple documents with optional query spec."""
		cursor = self._db[collection_name].find(filter)
		
		if query_spec:
			# 应用 MongoDB 特定的查询规约
			# Apply MongoDB-specific query spec
			if query_spec.order_by:
				# 预期元组格式如 ("field_name", 1/-1) 表示升序/降序
				# Expect tuples like ("field_name", 1/-1) for ascending/descending
				cursor = cursor.sort(query_spec.order_by)
			if query_spec.limit:
				cursor = cursor.limit(query_spec.limit)
			if query_spec.offset:
				cursor = cursor.skip(query_spec.offset)
		
		results = list(cursor)
		
		logger.debug(
			f"MongoDB 查询多个文档: {collection_name}",
			extra={
				'operation': 'find',
				'collection': collection_name,
				'has_filter': bool(filter),
				'has_query_spec': query_spec is not None,
				'result_count': len(results),
				'limit': query_spec.limit if query_spec else None
			}
		)
		return results

	def update_one(self, collection_name: str, filter: dict, update: dict, upsert: bool = False) -> Any:
		"""更新单个文档
		Update a single document."""
		result = self._db[collection_name].update_one(filter, update, upsert=upsert)
		
		logger.info(
			f"MongoDB 更新文档: {collection_name}",
			extra={
				'operation': 'update_one',
				'collection': collection_name,
				'matched_count': result.matched_count,
				'modified_count': result.modified_count,
				'upserted': upsert and result.upserted_id is not None
			}
		)
		return result

	def delete_one(self, collection_name: str, filter: dict) -> Any:
		"""删除单个文档
		Delete a single document."""
		result = self._db[collection_name].delete_one(filter)
		
		logger.info(
			f"MongoDB 删除文档: {collection_name}",
			extra={
				'operation': 'delete_one',
				'collection': collection_name,
				'deleted_count': result.deleted_count
			}
		)
		return result

	def delete_many(self, collection_name: str, filter: dict) -> Any:
		"""删除多个文档
		Delete multiple documents."""
		return self._db[collection_name].delete_many(filter, filter)

	def count_documents(self, collection_name: str, filter: dict) -> int:
		"""统计匹配过滤器的文档数
		Count documents matching filter."""
		return self._db[collection_name].count_documents(filter)

	# 聚合 Aggregation
	def aggregate(self, collection_name: str, pipeline: list[dict]) -> list[dict]:
		"""运行聚合管道
		Run an aggregation pipeline."""
		return list(self._db[collection_name].aggregate(pipeline))

	# 索引操作 Index operations
	def create_index(self, collection_name: str, keys: list, **kwargs) -> str:
		"""在集合上创建索引
		Create an index on a collection."""
		return self._db[collection_name].create_index(keys, **kwargs)

	def list_indexes(self, collection_name: str) -> list:
		"""列出集合上的所有索引
		List all indexes on a collection."""
		return list(self._db[collection_name].list_indexes())

	@property
	def database(self):
		"""访问底层数据库以进行高级操作
		Access underlying database for advanced operations."""
		return self._db

	@property
	def engine(self):
		"""访问底层 MongoDBEngine
		Access underlying MongoDBEngine."""
		return self._engine


__all__ = ["CRUDRepository", "SQLAlchemyCRUDRepository", "RedisRepository", "MongoDBRepository"]
