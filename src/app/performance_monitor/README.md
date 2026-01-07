# 性能监视器 (Performance Monitor)

⚠️ **测试/示例模块** - 此模块处于测试阶段，用于演示性能监控的设计模式。将在后续开发过程中根据实际需求进行改进、优化或移除。

## 概述

性能监视器是一个轻量级的系统性能监控工具，提供实时和历史性能数据收集、分析和API接口访问。

## 功能特性

- **实时性能监控**: CPU和内存使用率监控
- **任务执行统计**: 记录和分析任务执行时间
- **数据持久化**: 保存性能历史数据
- **RESTful API接口**: 完整的API接口供外部调用
- **线程安全**: 使用锁机制确保并发访问安全
- **灵活配置**: 可配置采样间隔和数据保留量

## 目录结构

```
src/app/performance_monitor/
├── __init__.py          # 模块导出
├── monitor.py           # 核心监视器实现
├── metrics.py           # 性能指标数据结构
└── api.py              # API接口定义
```

## 快速开始

### 1. 基本使用

```python
from app.performance_monitor import get_monitor

# 获取监视器实例
monitor = get_monitor()

# 启动监控
monitor.start()

# 执行一些工作...
import time
time.sleep(5)

# 获取当前指标
snapshot = monitor.get_current_snapshot()
print(f"CPU: {snapshot.cpu_percent:.2f}%")
print(f"Memory: {snapshot.memory_percent:.2f}%")

# 停止监控
monitor.stop()
```

### 2. 使用API接口

```python
from app.performance_monitor import performance_api

# 启动监控
response = performance_api.start_monitoring()
print(response)  # {'status': 'success', 'message': '...', ...}

# 获取当前指标
response = performance_api.get_current_metrics()
print(response['data'])

# 停止监控
performance_api.stop_monitoring()
```

### 3. 任务执行监控

```python
from app.performance_monitor import performance_api
import time

# 记录任务执行时间
start = time.time()
# 执行任务...
duration = time.time() - start
performance_api.record_task('my_task', duration)

# 获取任务统计
stats = performance_api.get_task_stats('my_task')
print(stats)
```

## API接口文档

### 监控控制

#### `start_monitoring()`
启动性能监控

**返回值:**
```python
{
    'status': 'success' | 'error',
    'message': str,
    'timestamp': datetime_str
}
```

#### `stop_monitoring()`
停止性能监控

#### `get_status()`
获取监视器状态

**返回值:**
```python
{
    'status': 'success',
    'running': bool,
    'sampling_interval': float,
    'metrics_count': int,
    'task_count': int,
    'timestamp': datetime_str
}
```

### 指标查询

#### `get_current_metrics()`
获取当前性能指标

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'timestamp': datetime_str,
        'cpu_percent': float,        # 0-100
        'memory_percent': float,     # 0-100
        'memory_mb': float,
        'process_count': int,
        'thread_count': int,
    },
    'timestamp': datetime_str
}
```

#### `get_metrics_summary()`
获取性能指标摘要（平均值、最大值等）

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'snapshots_count': int,
        'cpu': {
            'average': float,
            'maximum': float,
        },
        'memory': {
            'average': float,
            'maximum': float,
        },
        'tasks': {
            'task_name': {...},  # 任务统计
        }
    },
    'timestamp': datetime_str
}
```

#### `get_history(limit=10)`
获取历史指标数据

**参数:**
- `limit` (int): 返回的最大记录数，默认10

**返回值:**
```python
{
    'status': 'success',
    'data': [
        {snapshot_data},  # MetricsSnapshot.to_dict()
        ...
    ],
    'count': int,
    'timestamp': datetime_str
}
```

### 任务监控

#### `get_task_stats(task_name)`
获取特定任务执行统计

**参数:**
- `task_name` (str): 任务名称

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'task_name': str,
        'count': int,              # 执行次数
        'avg_time': float,         # 平均执行时间（秒）
        'min_time': float,         # 最小执行时间
        'max_time': float,         # 最大执行时间
        'total_time': float,       # 总执行时间
    },
    'timestamp': datetime_str
}
```

#### `get_all_tasks()`
获取所有任务执行统计

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'task_name1': {...},
        'task_name2': {...},
    },
    'count': int,
    'timestamp': datetime_str
}
```

#### `record_task(task_name, duration)`
记录任务执行时间

**参数:**
- `task_name` (str): 任务名称
- `duration` (float): 执行时间（秒）

**返回值:**
```python
{
    'status': 'success' | 'error',
    'message': str,
    'timestamp': datetime_str
}
```

### 数据管理

#### `clear_all()`
清除所有性能数据

#### `reset_task(task_name=None)`
重置任务计时数据

**参数:**
- `task_name` (str, optional): 任务名称，如果为None则重置所有任务

## 配置选项

### 初始化参数

```python
from app.performance_monitor import init_monitor

monitor = init_monitor(
    sampling_interval=1.0,    # 采样间隔（秒），默认1.0
    max_snapshots=1000,       # 最大快照数，默认1000
    auto_start=False          # 是否自动启动，默认False
)
```

## 性能考虑

- **采样间隔**: 较小的间隔（<0.5秒）可能影响系统性能，建议1秒及以上
- **快照数量**: 大量快照会消耗内存，通过`max_snapshots`参数限制
- **任务数量**: 监控大量不同的任务时，使用字典存储可能消耗更多内存
- **后台线程**: 采样通过后台线程执行，不会阻塞主线程

## 使用场景

1. **应用性能分析**: 实时监控应用CPU和内存使用情况
2. **任务性能优化**: 记录和分析各个任务的执行时间
3. **系统健康检查**: 定期采集性能数据用于健康检查
4. **瓶颈识别**: 识别高耗时任务和资源消耗
5. **性能报告**: 生成性能摘要用于性能报告

## 依赖

- `psutil`: 用于系统性能指标收集

## 注意事项

- 监视器使用线程安全的锁机制，可以在多线程环境中安全使用
- 清除数据会丢失所有历史记录，请谨慎操作
- 采样线程为daemon线程，不会阻止程序退出
- **测试模块**: 此模块仍在测试阶段，API和功能设计可能会改变，请勿在生产环境中依赖此模块
