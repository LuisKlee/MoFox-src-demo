# 统一监视器管理系统 (Unified Monitor System)

⚠️ **测试/示例模块** - 此模块处于测试阶段，用于演示统一监控系统的设计模式。将在后续开发过程中根据实际需求进行改进、优化或移除。

## 概述

统一监视器管理系统整合了性能监视器和数据库监视器，提供统一的管理接口和API，方便统一监控和管理系统的各个方面。

## 核心特性

- **统一管理**: 一个接口管理所有监视器
- **综合分析**: 整合性能和数据库指标进行综合分析
- **健康评估**: 自动评估系统健康状况并给出建议
- **统一API**: 提供完整的RESTful API接口
- **摘要报告**: 生成包含所有监视器数据的综合报告
- **📝 日志集成**: 与日志系统深度集成，自动记录监视器事件和指标

## 架构

```
monitors/
├── __init__.py              # 模块导出
├── manager.py               # 监视器管理器
├── unified_api.py           # 统一API接口
├── logger_integration.py    # 日志系统集成（NEW）
├── logger_integration_examples.py  # 集成示例（NEW）
└── README.md               # 文档

整合的监视器：
├── performance_monitor/     # 性能监视器
└── database_monitor/        # 数据库监视器
```

## 快速开始

### 1. 基本使用

```python
from app.monitors import get_manager

# 获取管理器实例
manager = get_manager()

# 启用所有监视器
manager.enable_all()

# 获取综合快照
snapshot = manager.get_comprehensive_snapshot()
print(f"性能: CPU {snapshot['performance']['cpu_percent']}%")
print(f"数据库: {snapshot['database']['total_queries']} 个查询")

# 获取健康状态
health = manager.get_health_status()
print(f"健康评分: {health['health_score']}")
print(f"健康等级: {health['health_level']}")

# 禁用所有监视器
manager.disable_all()
```

### 2. 与日志系统集成（推荐）✨

```python
from app.monitors import setup_monitor_logger_integration

# 一行代码实现监视器与日志系统的完整集成
integration = setup_monitor_logger_integration(app_name="myapp")

# 启动监视器
integration.start()

# 自动记录日志
integration.check_and_log_health()           # 健康状态
integration.log_performance_metrics()        # 性能指标
integration.log_database_metrics()           # 数据库指标
integration.log_slow_queries()               # 慢查询告警
integration.log_comprehensive_report()       # 综合报告

# 停止监视器
integration.stop()
```

详细信息请查看：📖 [日志集成指南](../../docs/app/monitors/LOGGER_INTEGRATION.md)

### 3. 使用统一API

```python
from app.monitors import unified_monitor_api

# 启用所有监视器
response = unified_monitor_api.enable_all_monitors()
print(response)

# 获取综合快照
response = unified_monitor_api.get_comprehensive_snapshot()
print(response['data'])

# 获取健康状态
response = unified_monitor_api.get_health_status()
health = response['data']
print(f"健康评分: {health['health_score']}")
if health['issues']:
    print("检测到的问题:")
    for issue in health['issues']:
        print(f"  - {issue}")

# 获取摘要报告
response = unified_monitor_api.get_summary_report()
print(response['data'])
```

### 4. 分别访问各监视器

```python
from app.monitors import get_manager

manager = get_manager()
manager.enable_all()

# 访问性能监视器
perf_snapshot = manager.get_performance_snapshot()
print(f"CPU: {perf_snapshot['cpu_percent']}%")
print(f"内存: {perf_snapshot['memory_mb']}MB")

# 访问数据库监视器
db_snapshot = manager.get_database_snapshot()
print(f"查询数: {db_snapshot['total_queries']}")
print(f"平均查询时间: {db_snapshot['avg_query_time']}秒")

# 获取慢查询
slow_queries = manager.get_slow_queries(threshold=0.5, limit=10)
for query in slow_queries:
    print(f"慢查询: {query.operation} {query.table_name} - {query.duration}秒")
```

## API接口文档

### 统一控制接口

#### `enable_all_monitors()`
启用所有监视器

**返回值:**
```python
{
    'status': 'success',
    'message': '所有监视器已启用',
    'monitors': {
        'performance_monitor': True,
        'database_monitor': True
    },
    'timestamp': datetime_str
}
```

#### `disable_all_monitors()`
禁用所有监视器

**返回值:** 类似 `enable_all_monitors`

#### `get_monitors_status()`
获取所有监视器状态

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'performance_monitor': {
            'enabled': bool,
            'sampling_interval': float,
            'metrics_count': int
        },
        'database_monitor': {
            'enabled': bool,
            'slow_query_threshold': float,
            'query_history_count': int
        },
        'all_enabled': bool
    },
    'timestamp': datetime_str
}
```

#### `clear_all_metrics()`
清空所有监视器的指标数据

**返回值:**
```python
{
    'status': 'success',
    'message': '所有监视器指标已清空',
    'timestamp': datetime_str
}
```

### 综合数据接口

#### `get_comprehensive_snapshot()`
获取综合快照（性能 + 数据库）

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'timestamp': datetime_str,
        'performance': {
            'cpu_percent': float,
            'memory_percent': float,
            'memory_mb': float,
            'process_count': int,
            'thread_count': int
        },
        'database': {
            'total_queries': int,
            'successful_queries': int,
            'failed_queries': int,
            'avg_query_time': float,
            'queries_per_second': float,
            'slow_queries_count': int
        },
        'status': {...}
    },
    'timestamp': datetime_str
}
```

#### `get_health_status()`
获取系统健康状态评估

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'health_score': int,        # 0-100分
        'health_level': str,        # 优秀/良好/一般/较差
        'status': str,              # healthy/warning/degraded/critical
        'issues': [str],            # 检测到的问题列表
        'metrics': {
            'cpu_percent': float,
            'memory_percent': float,
            'avg_query_time': float,
            'slow_queries_count': int,
            'query_failure_rate': float
        }
    },
    'timestamp': datetime_str
}
```

**健康评分规则:**
- CPU > 80%: -20分
- CPU > 60%: -10分
- 内存 > 80%: -20分
- 内存 > 60%: -10分
- 平均查询时间 > 1秒: -20分
- 平均查询时间 > 0.5秒: -10分
- 慢查询 > 10个: -15分
- 慢查询 > 5个: -5分
- 查询失败率 > 10%: -20分
- 查询失败率 > 5%: -10分

**健康等级:**
- 90-100分: 优秀 (healthy)
- 70-89分: 良好 (warning)
- 50-69分: 一般 (degraded)
- 0-49分: 较差 (critical)

#### `get_summary_report()`
获取综合摘要报告

**返回值:**
```python
{
    'status': 'success',
    'data': {
        'timestamp': datetime_str,
        'health': {...},            # 健康状态
        'performance': {...},        # 性能指标
        'database': {...},          # 数据库指标
        'monitors_status': {...}    # 监视器状态
    },
    'timestamp': datetime_str
}
```

### 性能监视器接口

#### `get_performance_snapshot()`
获取性能快照

#### `get_performance_history(limit: int = 100)`
获取性能历史数据

#### `get_task_statistics(task_name: Optional[str] = None)`
获取任务统计

### 数据库监视器接口

#### `get_database_snapshot()`
获取数据库快照

#### `get_slow_queries(threshold: Optional[float] = None, limit: int = 50)`
获取慢查询列表

#### `get_table_statistics(table_name: Optional[str] = None)`
获取表统计信息

#### `get_operation_statistics()`
获取数据库操作统计

详细的参数和返回值请参考各监视器的文档。

## 使用场景

### 1. 系统健康监控

```python
from app.monitors import unified_monitor_api
import time

# 启用监控
unified_monitor_api.enable_all_monitors()

# 定期检查健康状态
while True:
    health = unified_monitor_api.get_health_status()
    
    if health['data']['status'] == 'critical':
        print(f"⚠️ 系统健康状况严重: {health['data']['health_score']}分")
        for issue in health['data']['issues']:
            print(f"  - {issue}")
        # 发送告警...
    
    time.sleep(60)  # 每分钟检查一次
```

### 2. 性能分析

```python
from app.monitors import get_manager

manager = get_manager()
manager.enable_all()

# 执行一些操作...
# ...

# 获取综合报告
report = manager.get_summary_report()

print("=== 性能分析报告 ===")
print(f"CPU使用率: {report['performance']['cpu_percent']}%")
print(f"内存使用率: {report['performance']['memory_percent']}%")
print(f"总查询数: {report['database']['total_queries']}")
print(f"平均查询时间: {report['database']['avg_query_time']}秒")
print(f"QPS: {report['database']['queries_per_second']}")

if report['health']['status'] != 'healthy':
    print(f"\n健康状况: {report['health']['health_level']}")
    print("问题列表:")
    for issue in report['health']['issues']:
        print(f"  - {issue}")
```

### 3. 定时生成报告

```python
from app.monitors import unified_monitor_api
import time
import json
from datetime import datetime

# 启用所有监视器
unified_monitor_api.enable_all_monitors()

# 每小时生成一次报告
while True:
    # 获取摘要报告
    response = unified_monitor_api.get_summary_report()
    report = response['data']
    
    # 保存为JSON文件
    filename = f"monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"报告已生成: {filename}")
    print(f"健康评分: {report['health']['health_score']}")
    
    time.sleep(3600)  # 每小时
```

### 4. 结合Web框架（Flask示例）

```python
from flask import Flask, jsonify
from app.monitors import unified_monitor_api

app = Flask(__name__)

# 启用监控
unified_monitor_api.enable_all_monitors()

@app.route('/api/monitors/health')
def get_health():
    """获取健康状态"""
    return jsonify(unified_monitor_api.get_health_status())

@app.route('/api/monitors/snapshot')
def get_snapshot():
    """获取综合快照"""
    return jsonify(unified_monitor_api.get_comprehensive_snapshot())

@app.route('/api/monitors/report')
def get_report():
    """获取摘要报告"""
    return jsonify(unified_monitor_api.get_summary_report())

@app.route('/api/monitors/performance')
def get_performance():
    """获取性能指标"""
    return jsonify(unified_monitor_api.get_performance_snapshot())

@app.route('/api/monitors/database')
def get_database():
    """获取数据库指标"""
    return jsonify(unified_monitor_api.get_database_snapshot())

@app.route('/api/monitors/slow-queries')
def get_slow_queries():
    """获取慢查询"""
    return jsonify(unified_monitor_api.get_slow_queries(limit=50))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## 管理器方法

### MonitorManager

#### 统一控制
- `enable_all()`: 启用所有监视器
- `disable_all()`: 禁用所有监视器
- `is_all_enabled()`: 检查是否所有监视器都已启用
- `get_status()`: 获取所有监视器状态
- `clear_all_metrics()`: 清空所有指标

#### 性能监视器访问
- `get_performance_snapshot()`: 获取性能快照
- `get_performance_history(limit)`: 获取性能历史
- `get_task_statistics(task_name)`: 获取任务统计

#### 数据库监视器访问
- `get_database_snapshot()`: 获取数据库快照
- `get_slow_queries(threshold, limit)`: 获取慢查询
- `get_table_statistics(table_name)`: 获取表统计
- `get_operation_statistics()`: 获取操作统计

#### 综合分析
- `get_comprehensive_snapshot()`: 获取综合快照
- `get_health_status()`: 获取健康状态评估
- `get_summary_report()`: 获取综合摘要报告

## 最佳实践

1. **统一启用**: 使用 `enable_all()` 一次性启用所有监视器

2. **定期检查**: 定期调用 `get_health_status()` 检查系统健康状况

3. **告警设置**: 根据健康评分设置告警阈值，及时发现问题

4. **数据清理**: 长期运行时定期调用 `clear_all_metrics()` 清理旧数据

5. **分级监控**: 根据健康等级采取不同的监控策略
   - healthy: 降低检查频率
   - warning: 增加日志记录
   - degraded: 提高检查频率
   - critical: 发送告警

## 注意事项

- 此模块处于测试阶段，API可能会发生变化
- 默认情况下所有监视器都是禁用的，需要手动启用
- 健康评分算法可根据实际需求调整
- 长期运行建议定期清理历史数据

## 相关文档

- [性能监视器](../performance_monitor/README.md)
- [数据库监视器](../database_monitor/README.md)

## 许可证

遵循项目主许可证
