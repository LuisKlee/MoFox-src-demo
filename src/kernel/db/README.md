# 数据库内核说明

## 目录结构
- core/：数据库引擎与会话管理
  - dialect_adapter.py：方言适配器接口与 SQLite 实现
  - engine.py：引擎注册与创建
  - session.py：会话管理器（事务作用域）
  - exceptions.py：数据库相关异常
- api/：对外 CRUD / 查询接口
  - crud.py：CRUD 抽象与 SQLAlchemy 实现
  - query.py：查询规约（QuerySpec）与应用器

## 当前能力
- 支持 SQLite 引擎创建（文件或内存模式），自动创建目录。
- 通过 EngineManager 按名称管理多个引擎，可扩展其他方言适配器。
- SessionManager 提供事务作用域，自动提交/回滚与关闭。
- SQLAlchemyCRUDRepository 封装常用增删改查，接受 QuerySpec 以复用过滤/排序/分页。

## 快速使用示例（同步 SQLAlchemy）
```python
from kernel.db.core import EngineManager, EngineConfig, SessionManager
from kernel.db.api import SQLAlchemyCRUDRepository, QuerySpec

engine = EngineManager().create(EngineConfig(dialect="sqlite", database="data/app.db"))
session_mgr = SessionManager(engine)
repo = SQLAlchemyCRUDRepository(session_mgr)

with repo.session_scope() as session:
    obj = repo.add(session, MyModel(name="demo"), flush=True)
    rows = repo.list(session, MyModel, QuerySpec(limit=10))
```

## 扩展指引
- 新增数据库方言：实现 DialectAdapter（如 Postgres/MySQL），在 EngineManager.register_adapter 注册。
- 自定义 CRUD：继承 CRUDRepository，替换 SQLAlchemy 实现，或封装异步版本。
- 查询扩展：在 QuerySpec 中增加字段，并在 apply_query_spec 内映射到后端查询表达式。

## TODO
- 添加 PostgreSQL / MySQL 适配器
- 提供异步会话/CRUD 版本
- 集成迁移与健康检查工具
