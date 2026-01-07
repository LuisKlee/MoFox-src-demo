# TaskManager监视器 (Task Manager Monitor)

⚠️ **示例模块** - 此模块将在后续开发过程中移除。如需持续使用，请根据实际需求进行改进或迁移。

## 概述

TaskManager监视器是一个**非入侵式**的监视工具，可以在不修改TaskManager代码的情况下，对其运行状态进行全面监控。

## 核心特性

- **非入侵式设计**: 完全不改动TaskManager的原有代码
- **任务生命周期追踪**: 从创建→启动→完成/失败的全过程
- **性能指标收集**: 执行时间、成功率等统计数据
- **事件日志记录**: 详细的事件时间线
- **错误跟踪**: 失败、超时、重试等事件监控
- **灵活启禁**: 随时启用或禁用监视功能

## 目录结构

```
src/app/performance_monitor/task_monitor/
├── __init__.py           # 模块导出
├── monitor.py           # 监视器核心实现
├── interceptor.py       # 拦截器（事件记录器）
└── metrics.py           # 指标数据结构
```

## 快速开始

### 1. 基本使用

```python
from kernel.concurrency import get_task_manager
from app.performance_monitor.task_monitor import attach_monitor

# 获取TaskManager
task_manager = get_task_manager()

# 附加监视器（不改动TaskManager）
monitor = attach_monitor(task_manager)

# 在任务事件发生时，调用监视记录
monitor.record_task_created('task-001', 'my_task')
monitor.record_task_started('task-001', 'my_task')
monitor.record_task_completed('task-001', 'my_task')

# 获取监视状态
status = monitor.get_status()
print(status)
```

### 2. 集成到TaskManager

在你的TaskManager使用代码中添加监视调用（**不修改TaskManager本身**）：

```python
from kernel.concurrency import get_task_manager
from app.performance_monitor.task_monitor import attach_monitor

# 初始化
task_manager = get_task_manager()
monitor = attach_monitor(task_manager)  # 启用监视

# 创建并执行任务
async def run_task(task_manager, monitor):
    task_id = 'task-001'
    task_name = 'data_processing'
    
    try:
        # 记录任务创建
        monitor.record_task_created(task_id, task_name, {'priority': 'high'})
        
        # 提交任务到TaskManager
        result = await task_manager.submit(task_id, coroutine_func)
        
        # 记录任务开始
        monitor.record_task_started(task_id, task_name)
        
        # 等待任务完成
        await result
        
        # 记录任务完成
        monitor.record_task_completed(task_id, task_name)
        
    except Exception as e:
        # 记录任务失败
        monitor.record_task_failed(task_id, task_name, str(e))
```

### 3. 查询监视数据

```python
# 获取监视器状态
status = monitor.get_status()

# 获取任务摘要
summary = monitor.get_summary()

# 获取特定任务统计
task_stats = monitor.get_task_stats('my_task')

# 获取所有任务统计
all_stats = monitor.get_all_tasks_stats()

# 获取事件日志
events = monitor.get_events(limit=100, task_name='my_task')
```

## API接口文档

### 监视控制

#### `enable()`
启用监视

#### `disable()`
禁用监视

#### `is_enabled()`
检查监视状态

### 事件记录

#### `record_task_created(task_id, task_name, metadata=None)`
记录任务创建事件

**参数:**
- `task_id` (str): 任务ID
- `task_name` (str): 任务名称
- `metadata` (dict, optional): 额外的元数据

#### `record_task_started(task_id, task_name, metadata=None)`
记录任务开始事件

#### `record_task_completed(task_id, task_name, metadata=None)`
记录任务完成事件

#### `record_task_failed(task_id, task_name, error, metadata=None)`
记录任务失败事件

**参数:**
- `task_id` (str): 任务ID
- `task_name` (str): 任务名称
- `error` (str): 错误信息
- `metadata` (dict, optional): 额外数据

#### `record_task_cancelled(task_id, task_name, metadata=None)`
记录任务取消事件

#### `record_task_timeout(task_id, task_name, timeout, metadata=None)`
记录任务超时事件

**参数:**
- `task_id` (str): 任务ID
- `task_name` (str): 任务名称
- `timeout` (float): 超时时间（秒）
- `metadata` (dict, optional): 额外数据

#### `record_task_retry(task_id, task_name, retry_count, metadata=None)`
记录任务重试事件

**参数:**
- `task_id` (str): 任务ID
- `task_name` (str): 任务名称
- `retry_count` (int): 重试次数
- `metadata` (dict, optional): 额外数据

### 数据查询

#### `get_status()`
获取监视器状态

**返回值:**
```python
{
    'status': 'success',
    'enabled': bool,
    'summary': {
        'total_created': int,
        'total_completed': int,
        'total_failed': int,
        'total_cancelled': int,
        'total_timeout': int,
        'success_rate': float,
        'unique_tasks': int,
        'events_count': int,
    },
    'timestamp': datetime_str
}
```

#### `get_summary()`
获取任务统计摘要

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'total_created': int,
        'total_completed': int,
        'total_failed': int,
        'total_cancelled': int,
        'total_timeout': int,
        'success_rate': float,
        'unique_tasks': int,
        'events_count': int,
    },
    'timestamp': datetime_str
}
```

#### `get_task_stats(task_name)`
获取特定任务的执行统计

**参数:**
- `task_name` (str): 任务名称

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'task_name': str,
        'total_created': int,
        'total_completed': int,
        'total_failed': int,
        'total_cancelled': int,
        'total_timeout': int,
        'total_retried': int,
        'success_rate': float,
        'avg_duration': float,         # 秒
        'min_duration': float,         # 秒
        'max_duration': float,         # 秒
        'execution_count': int,
    },
    'timestamp': datetime_str
}
```

#### `get_all_tasks_stats()`
获取所有任务的统计信息

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'task_name1': {...},
        'task_name2': {...},
        ...
    },
    'count': int,
    'timestamp': datetime_str
}
```

#### `get_events(limit=100, task_name=None)`
获取事件日志

**参数:**
- `limit` (int): 返回的最大事件数，默认100
- `task_name` (str, optional): 按任务名过滤，为None时返回所有任务的事件

**返回值:**
```python
{
    'status': 'success',
    'data': [
        {
            'event_type': 'created|started|completed|failed|cancelled|timeout|retrying',
            'task_id': str,
            'task_name': str,
            'timestamp': datetime_str,
            'duration': float,  # 任务执行时间（秒），可选
            'error': str,       # 错误信息，可选
            'metadata': dict,   # 额外数据
        },
        ...
    ],
    'count': int,
    'timestamp': datetime_str
}
```

#### `clear_metrics()`
清除所有监视数据

### 全局函数

#### `attach_monitor(task_manager)`
将监视器附加到TaskManager实例

**参数:**
- `task_manager`: TaskManager实例

**返回值:**
- TaskManagerMonitor实例

#### `get_task_monitor()`
获取全局任务监视器实例

## 监视模式

### 模式1: 手动记录（最灵活）

在应用代码中手动调用监视方法：

```python
monitor = attach_monitor(task_manager)

# 创建任务时
monitor.record_task_created('task-001', 'process')

# 开始执行时
monitor.record_task_started('task-001', 'process')

# 完成时
monitor.record_task_completed('task-001', 'process')
```

### 模式2: 回调集成

如果TaskManager支持回调，可以通过回调集成监视：

```python
def on_task_created(task_id, task_name):
    monitor.record_task_created(task_id, task_name)

task_manager.on_created_callbacks.append(on_task_created)
```

### 模式3: 包装器模式

创建一个包装器来自动化监视调用：

```python
class MonitoredTaskManager:
    def __init__(self, task_manager, monitor):
        self.manager = task_manager
        self.monitor = monitor
    
    async def submit(self, task_id, task_name, coro):
        self.monitor.record_task_created(task_id, task_name)
        try:
            self.monitor.record_task_started(task_id, task_name)
            result = await self.manager.submit(task_id, coro)
            self.monitor.record_task_completed(task_id, task_name)
            return result
        except Exception as e:
            self.monitor.record_task_failed(task_id, task_name, str(e))
            raise
```

## 事件类型

- `created`: 任务创建
- `started`: 任务开始执行
- `completed`: 任务完成
- `failed`: 任务失败
- `cancelled`: 任务取消
- `timeout`: 任务超时
- `retrying`: 任务重试

## 最佳实践

1. **初始化时附加监视器**
   ```python
   # 应用启动时
   monitor = attach_monitor(task_manager)
   ```

2. **使用清晰的任务名称**
   ```python
   # 好的做法
   monitor.record_task_created('task-001', 'data_processing')
   
   # 避免
   monitor.record_task_created('task-001', 'task')
   ```

3. **记录关键元数据**
   ```python
   monitor.record_task_created(
       task_id,
       task_name,
       metadata={'priority': 'high', 'user_id': 123}
   )
   ```

4. **定期清理旧数据**
   ```python
   # 定期清除监视数据以节省内存
   monitor.clear_metrics()
   ```

5. **根据需要启禁监视**
   ```python
   # 生产环境可能想禁用部分监视
   if not production:
       monitor.enable()
   ```

## 性能考虑

- 事件记录是O(1)操作，性能开销极小
- 默认保存最多10000个事件，超出时自动删除旧事件
- 统计数据的计算是O(n)，其中n是唯一任务数
- 建议定期清理历史数据以保持内存占用

## 注意事项

- **不修改TaskManager**: 监视器设计不需要修改TaskManager代码
- **线程安全**: 所有记录操作都是线程安全的
- **可选性**: 监视可随时启用或禁用
- **数据丢失**: 清除数据是永久的，请谨慎操作
- **示例模块**: 此模块为示例，将在后续开发中移除，如需持续使用请进行迁移或改进
