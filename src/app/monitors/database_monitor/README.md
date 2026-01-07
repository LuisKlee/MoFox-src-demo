# 数据库监视器 (Database Monitor)

⚠️ **测试/示例模块** - 此模块处于测试阶段，用于演示数据库监控的设计模式。将在后续开发过程中根据实际需求进行改进、优化或移除。

## 概述

数据库监视器是一个轻量级的数据库操作监控工具，通过装饰器和包装器模式提供非侵入式的数据库性能监控功能，不修改底层数据库代码。

## 核心特性

- **非侵入式监控**: 通过装饰器模式，不修改底层数据库代码
- **查询性能追踪**: 记录每个查询的执行时间、操作类型、受影响行数
- **慢查询检测**: 自动识别和记录慢查询，可配置阈值
- **连接池监控**: 跟踪数据库连接池状态
- **多维度统计**: 按表、按操作类型进行统计分析
- **RESTful API接口**: 完整的API接口供外部调用
- **线程安全**: 使用锁机制确保并发访问安全

## 目录结构

```
src/app/database_monitor/
├── __init__.py          # 模块导出
├── monitor.py           # 核心监视器实现
├── metrics.py           # 监控指标数据结构
└── api.py              # API接口定义
```

## 快速开始

### 1. 基本使用

```python
from app.database_monitor import get_monitor

# 获取监视器实例
monitor = get_monitor()

# 启用监控
monitor.enable()

# 手动记录查询
monitor.record_query(
    operation='select',
    duration=0.125,
    table_name='users',
    rows_affected=10,
    success=True
)

# 获取当前快照
snapshot = monitor.get_current_snapshot()
print(f"总查询数: {snapshot.total_queries}")
print(f"平均查询时间: {snapshot.avg_query_time:.4f}秒")
print(f"QPS: {snapshot.queries_per_second:.2f}")
```

### 2. 使用装饰器监控查询

```python
from app.database_monitor import get_monitor

monitor = get_monitor()
monitor.enable()

@monitor.monitor_query('select', 'users')
def get_user_by_id(user_id: int):
    # 执行数据库查询
    # ...
    return user_data

@monitor.monitor_query('insert', 'users')
def create_user(user_data: dict):
    # 执行插入操作
    # ...
    return result
```

### 3. 使用API接口

```python
from app.database_monitor import database_api

# 启用监控
response = database_api.enable_monitoring()
print(response)  # {'status': 'success', ...}

# 设置慢查询阈值（默认1秒）
database_api.set_slow_query_threshold(0.5)

# 获取当前指标
response = database_api.get_current_snapshot()
print(response['data'])

# 获取慢查询列表
slow_queries = database_api.get_slow_queries(limit=50)
print(f"慢查询数量: {slow_queries['count']}")
```

## API接口文档

### 监控控制

#### `enable_monitoring()`
启用数据库监控

**返回值:**
```python
{
    'status': 'success' | 'error',
    'message': str,
    'timestamp': datetime_str
}
```

#### `disable_monitoring()`
禁用数据库监控

**返回值:** 同上

#### `get_status()`
获取监控状态

**返回值:**
```python
{
    'status': 'success',
    'enabled': bool,
    'slow_query_threshold': float,
    'query_history_count': int,
    'connection_history_count': int,
    'timestamp': datetime_str
}
```

#### `set_slow_query_threshold(threshold: float)`
设置慢查询阈值

**参数:**
- `threshold`: 阈值（秒），必须大于0

**返回值:**
```python
{
    'status': 'success',
    'message': str,
    'threshold': float,
    'timestamp': datetime_str
}
```

### 数据查询

#### `get_current_snapshot()`
获取当前数据库状态快照

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'timestamp': datetime_str,
        'total_queries': int,
        'successful_queries': int,
        'failed_queries': int,
        'avg_query_time': float,
        'max_query_time': float,
        'min_query_time': float,
        'queries_per_second': float,
        'active_connections': int,
        'idle_connections': int,
        'total_connections': int,
        'operations_count': dict,
        'slow_queries_count': int
    },
    'timestamp': datetime_str
}
```

#### `get_table_statistics(table_name: Optional[str] = None)`
获取表统计信息

**参数:**
- `table_name`: 表名，None表示所有表

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'table_name': {
            'total_queries': int,
            'total_time': float,
            'avg_time': float,
            'max_time': float,
            'min_time': float
        },
        ...
    },
    'table_name': str | None,
    'timestamp': datetime_str
}
```

#### `get_operation_statistics()`
获取操作类型统计

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'select': {'count': int, 'total_time': float, 'avg_time': float},
        'insert': {...},
        'update': {...},
        'delete': {...},
        ...
    },
    'timestamp': datetime_str
}
```

#### `get_slow_queries(threshold: Optional[float] = None, limit: int = 100)`
获取慢查询列表

**参数:**
- `threshold`: 慢查询阈值（秒），None使用默认值
- `limit`: 返回数量限制

**返回值:**
```python
{
    'status': 'success',
    'data': [
        {
            'query_id': str,
            'operation': str,
            'duration': float,
            'timestamp': datetime_str,
            'table_name': str | None,
            'rows_affected': int | None,
            'success': bool,
            'error_message': str | None
        },
        ...
    ],
    'count': int,
    'threshold': float,
    'timestamp': datetime_str
}
```

#### `get_recent_queries(limit: int = 100)`
获取最近的查询记录

**参数:**
- `limit`: 返回数量限制

**返回值:** 同 `get_slow_queries` 的数据格式

#### `get_connection_pool_status()`
获取连接池状态

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'active': int,
        'idle': int,
        'total': int,
        'max': int
    },
    'timestamp': datetime_str
}
```

### 数据管理

#### `clear_metrics()`
清空所有监控指标

**返回值:**
```python
{
    'status': 'success',
    'message': str,
    'timestamp': datetime_str
}
```

### 手动记录

#### `record_query(...)`
手动记录查询操作

**参数:**
- `operation`: 操作类型（select, insert, update, delete等）
- `duration`: 执行时间（秒）
- `table_name`: 表名（可选）
- `rows_affected`: 受影响的行数（可选）
- `success`: 是否成功（默认True）
- `error_message`: 错误消息（可选）

**返回值:**
```python
{
    'status': 'success',
    'query_id': str,
    'message': str,
    'timestamp': datetime_str
}
```

#### `update_connection_pool(...)`
更新连接池状态

**参数:**
- `active`: 活动连接数
- `idle`: 空闲连接数
- `total`: 总连接数
- `max_connections`: 最大连接数
- `wait_time`: 等待时间（可选，默认0.0）

**返回值:**
```python
{
    'status': 'success',
    'message': str,
    'timestamp': datetime_str
}
```

## 集成示例

### 与SQLAlchemy集成

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.database_monitor import get_monitor
import time

monitor = get_monitor()
monitor.enable()

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    duration = time.time() - context._query_start_time
    
    # 解析操作类型
    operation = statement.strip().split()[0].lower()
    
    # 记录查询
    monitor.record_query(
        operation=operation,
        duration=duration,
        success=True
    )
```

### 与pymongo集成

```python
from pymongo import monitoring
from app.database_monitor import get_monitor

monitor = get_monitor()
monitor.enable()

class DatabaseMonitoringListener(monitoring.CommandListener):
    def started(self, event):
        # 记录开始时间
        pass
    
    def succeeded(self, event):
        # 计算执行时间
        duration = event.duration_micros / 1_000_000  # 转换为秒
        
        monitor.record_query(
            operation=event.command_name,
            duration=duration,
            table_name=event.command.get('collection'),
            success=True
        )
    
    def failed(self, event):
        duration = event.duration_micros / 1_000_000
        
        monitor.record_query(
            operation=event.command_name,
            duration=duration,
            success=False,
            error_message=event.failure
        )

# 注册监听器
monitoring.register(DatabaseMonitoringListener())
```

### 自定义数据库包装器

```python
from app.database_monitor import get_monitor

monitor = get_monitor()
monitor.enable()

class MonitoredDatabaseConnection:
    """带监控的数据库连接包装器"""
    
    def __init__(self, connection):
        self.connection = connection
    
    def execute(self, query, params=None):
        """执行SQL查询并监控"""
        import time
        
        # 解析操作类型
        operation = query.strip().split()[0].lower()
        
        start_time = time.time()
        error_msg = None
        success = True
        result = None
        
        try:
            result = self.connection.execute(query, params)
            return result
        except Exception as e:
            success = False
            error_msg = str(e)
            raise
        finally:
            duration = time.time() - start_time
            
            # 记录查询
            monitor.record_query(
                operation=operation,
                duration=duration,
                rows_affected=result.rowcount if result else None,
                success=success,
                error_message=error_msg
            )
```

## 监控指标说明

### 查询指标 (QueryMetrics)
- `query_id`: 唯一查询标识
- `operation`: 操作类型（select, insert, update, delete等）
- `duration`: 执行时间（秒）
- `timestamp`: 查询时间戳
- `table_name`: 表名
- `rows_affected`: 受影响的行数
- `success`: 是否成功
- `error_message`: 错误消息

### 连接池指标 (ConnectionMetrics)
- `timestamp`: 时间戳
- `active_connections`: 活动连接数
- `idle_connections`: 空闲连接数
- `total_connections`: 总连接数
- `max_connections`: 最大连接数
- `connection_wait_time`: 平均等待时间

### 数据库快照 (DatabaseSnapshot)
- `timestamp`: 快照时间
- `total_queries`: 总查询数
- `successful_queries`: 成功查询数
- `failed_queries`: 失败查询数
- `avg_query_time`: 平均查询时间
- `max_query_time`: 最大查询时间
- `min_query_time`: 最小查询时间
- `queries_per_second`: QPS（每秒查询数）
- `active_connections`: 活动连接数
- `idle_connections`: 空闲连接数
- `total_connections`: 总连接数
- `operations_count`: 按操作类型统计
- `slow_queries_count`: 慢查询数量

## 最佳实践

1. **慢查询阈值设置**: 根据业务需求设置合理的慢查询阈值，通常设置为0.5-1.0秒

2. **数据清理**: 定期调用 `clear_metrics()` 清理历史数据，避免内存占用过高

3. **装饰器使用**: 优先使用装饰器模式，保持代码整洁

4. **监控开关**: 在开发环境启用监控，生产环境可根据需要选择性启用

5. **性能影响**: 监控本身会带来少量性能开销，建议在关键路径上使用采样监控

## 注意事项

- 此模块处于测试阶段，API可能会发生变化
- 默认情况下监控是禁用的，需要手动启用
- 历史数据存储在内存中，重启后会丢失
- 不适合在高并发场景下记录所有查询，建议使用采样

## 未来规划

- [ ] 添加数据持久化支持
- [ ] 添加实时告警功能
- [ ] 添加可视化仪表盘
- [ ] 添加分布式追踪支持
- [ ] 添加查询计划分析
- [ ] 添加自动性能优化建议

## 相关文档

- [性能监视器](../performance_monitor/README.md)
- [数据库模块](../../../kernel/db/README.md)

## 许可证

遵循项目主许可证
