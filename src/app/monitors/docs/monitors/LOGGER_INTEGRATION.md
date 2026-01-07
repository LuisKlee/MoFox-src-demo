# 监视器与日志系统集成指南

## 概述

监视器系统与日志系统的集成提供了一个完整的解决方案，用于：
- 📝 记录监视器事件和指标
- 🚨 捕获健康状态变化
- ⚠️ 记录异常告警
- 📊 生成综合报告
- 💾 持久化存储监控数据

## 核心特性

### 1. 自动事件记录
- ✅ 监视器启动/停止事件
- ✅ 性能指标周期记录
- ✅ 数据库指标记录
- ✅ 健康状态变化追踪

### 2. 智能告警系统
- ✅ 健康状态变化警告
- ✅ 新问题检测与记录
- ✅ 问题解决情况追踪
- ✅ 慢查询告警

### 3. 分类日志记录
- 📋 **监视器日志** (`monitors`): 监视器操作
- 📊 **性能日志** (`monitors.metrics`): 性能指标
- 💓 **健康日志** (`monitors.health`): 健康状态
- 🚨 **告警日志** (`monitors.alerts`): 异常和告警

### 4. 存储集成
- ✅ 与日志存储模块集成
- ✅ JSON格式存储
- ✅ 历史数据查询
- ✅ 统计分析

## 快速开始

### 最简单的方式

```python
from app.monitors import setup_monitor_logger_integration

# 一行代码初始化集成
integration = setup_monitor_logger_integration(app_name="myapp")

# 启动监视器
integration.start()

# 检查并记录健康状态
integration.check_and_log_health()

# 停止监视器
integration.stop()
```

### 完整的监控循环

```python
import time
from app.monitors import setup_monitor_logger_integration

# 初始化
integration = setup_monitor_logger_integration(
    app_name="myapp",
    log_dir="logs",
    enable_storage=True  # 启用存储集成
)

# 启动
integration.start()

# 定期监控
try:
    while True:
        # 检查健康状态
        health = integration.check_and_log_health()
        
        # 记录性能指标
        integration.log_performance_metrics()
        
        # 记录数据库指标
        integration.log_database_metrics()
        
        # 检查慢查询
        integration.log_slow_queries(threshold=0.5)
        
        # 每分钟检查一次
        time.sleep(60)

finally:
    integration.stop()
```

## API 文档

### 初始化函数

#### `setup_monitor_logger_integration()`
初始化并返回全局集成实例

```python
integration = setup_monitor_logger_integration(
    app_name="myapp",              # 应用名称
    log_dir="logs",                # 日志目录
    enable_storage=True            # 是否启用存储集成
)
```

#### `get_monitor_logger_integration()`
获取已初始化的全局实例

```python
integration = get_monitor_logger_integration()
```

### MonitorLoggerIntegration 类

#### 生命周期方法

##### `start()`
启动所有监视器

```python
integration.start()
# 日志输出: INFO 所有监视器已启用，开始监控
```

##### `stop()`
停止所有监视器

```python
integration.stop()
# 日志输出: INFO 所有监视器已禁用，监控停止
```

#### 日志记录方法

##### `log_status()`
记录当前监视器状态

```python
integration.log_status()
# 记录监视器的启用状态和指标计数
```

##### `log_performance_metrics()`
记录性能指标

```python
integration.log_performance_metrics()
# 记录: CPU%, 内存%, 进程数, 线程数等
```

**日志示例:**
```
INFO:myapp.monitors.metrics:性能指标快照
{
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "memory_mb": 4096,
    "process_count": 128,
    "thread_count": 2048
}
```

##### `log_database_metrics()`
记录数据库指标

```python
integration.log_database_metrics()
# 记录: 查询数, 成功/失败查询, 平均查询时间等
```

**日志示例:**
```
INFO:myapp.monitors.metrics:数据库指标快照
{
    "total_queries": 5432,
    "successful_queries": 5400,
    "failed_queries": 32,
    "avg_query_time": 0.234,
    "queries_per_second": 18.5,
    "slow_queries_count": 12
}
```

##### `check_and_log_health()`
检查并记录系统健康状态

```python
health = integration.check_and_log_health()

# 返回值:
# {
#     "health_score": 85,
#     "health_level": "良好",
#     "status": "warning",
#     "issues": ["CPU使用率高", "内存使用率高"],
#     "metrics": {...}
# }
```

**特性:**
- 自动检测状态变化并记录为WARNING
- 自动检测新问题并记录告警
- 自动检测问题消除并记录INFO
- 记录详细的健康评分和指标

**日志示例 - 状态变化:**
```
WARNING:myapp.monitors.health:系统健康状态从 healthy 变为 warning (评分: 72)
{
    "old_status": "healthy",
    "new_status": "warning",
    "health_score": 72
}
```

**日志示例 - 新问题:**
```
WARNING:myapp.monitors.alerts:检测到新问题: CPU使用率过高 (当前评分: 72)
{
    "issue": "CPU使用率过高",
    "health_score": 72,
    "alert_type": "new_issue"
}
```

**日志示例 - 问题消除:**
```
INFO:myapp.monitors.alerts:问题已解决: CPU使用率过高 (当前评分: 88)
{
    "issue": "CPU使用率过高",
    "health_score": 88,
    "alert_type": "resolved_issue"
}
```

##### `log_slow_queries(threshold=None, limit=10)`
记录慢查询

```python
integration.log_slow_queries(
    threshold=0.5,  # 查询时间 > 0.5秒 为慢查询
    limit=10        # 最多记录10个
)
```

**日志示例:**
```
WARNING:myapp.monitors.alerts:检测到 3 个慢查询
{
    "slow_queries_count": 3,
    "query_count": 3
}

WARNING:myapp.monitors.alerts:慢查询: SELECT user_table - 1.23秒
{
    "operation": "SELECT",
    "table_name": "user",
    "duration": 1.23,
    "alert_type": "slow_query"
}
```

##### `log_comprehensive_report()`
记录综合监控报告

```python
report = integration.log_comprehensive_report()

# 返回包含以下信息的报告:
# - 健康状态评分和等级
# - 性能指标
# - 数据库指标
# - 监视器状态
```

**日志示例:**
```
INFO:myapp.monitors:生成综合监控报告
{
    "health_score": 85,
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "total_queries": 5432,
    "avg_query_time": 0.234
}
```

#### 报告和统计方法

##### `export_monitoring_report(output_file=None)`
导出监控报告为JSON文件

```python
report_file = integration.export_monitoring_report()
# 返回: "logs/monitor_report_20240107_143052.json"

# 或指定自定义路径
report_file = integration.export_monitoring_report(
    output_file="reports/myreport.json"
)
```

**导出格式:**
```json
{
    "timestamp": "2024-01-07T14:30:52.123456",
    "health": {
        "health_score": 85,
        "health_level": "良好",
        "status": "warning",
        "issues": [...],
        "metrics": {...}
    },
    "performance": {...},
    "database": {...},
    "monitors_status": {...}
}
```

##### `get_monitor_logs(days=1)`
获取监控日志统计（仅当启用存储集成时可用）

```python
logs = integration.get_monitor_logs(days=7)

# 返回值示例:
# {
#     "total_logs": 1234,
#     "debug_count": 234,
#     "info_count": 567,
#     "warning_count": 289,
#     "error_count": 12
# }
```

### 属性访问

```python
# 获取日志器
logger = integration.logger              # 通用日志器
health_logger = integration.health_logger  # 健康状态日志器
metrics_logger = integration.metrics_logger # 指标日志器
alert_logger = integration.alert_logger    # 告警日志器

# 获取管理器
manager = integration.monitor_manager  # 监视器管理器

# 获取日志系统
logger_system = integration.logger_system  # LoggerWithStorage 实例
```

## 使用示例

### 示例 1: 基本监控

```python
from app.monitors import setup_monitor_logger_integration
import time

# 初始化
integration = setup_monitor_logger_integration(app_name="demo")
integration.start()

# 运行5次检查
for i in range(5):
    print(f"检查 {i+1}...")
    integration.check_and_log_health()
    integration.log_performance_metrics()
    time.sleep(2)

integration.stop()
```

### 示例 2: 连续监控服务

```python
from app.monitors import setup_monitor_logger_integration
import time
import signal

class MonitorService:
    def __init__(self):
        self.integration = setup_monitor_logger_integration(
            app_name="service",
            enable_storage=True
        )
        self.running = True
        signal.signal(signal.SIGINT, self.stop)
    
    def start(self):
        self.integration.start()
        
        while self.running:
            # 每分钟检查一次
            self.integration.check_and_log_health()
            self.integration.log_performance_metrics()
            self.integration.log_database_metrics()
            
            # 每5分钟生成一份报告
            if int(time.time()) % 300 == 0:
                self.integration.log_comprehensive_report()
            
            time.sleep(60)
    
    def stop(self, signum, frame):
        self.running = False
        self.integration.stop()

# 运行服务
service = MonitorService()
service.start()
```

### 示例 3: 告警集成

```python
from app.monitors import setup_monitor_logger_integration
import time

integration = setup_monitor_logger_integration(app_name="alerts")
integration.start()

# 定期检查并发送告警
while True:
    health = integration.check_and_log_health()
    
    # 如果状态恶劣，发送告警
    if health['status'] == 'critical':
        # 发送邮件告警
        send_alert_email(
            subject="系统健康状况恶劣",
            body=f"评分: {health['health_score']}\n问题: {health['issues']}"
        )
        
        # 记录严重告警
        integration.alert_logger.critical(
            f"系统状态恶劣: {health['health_level']}"
        )
    
    time.sleep(60)
```

### 示例 4: 与 Flask 集成

```python
from flask import Flask, jsonify
from app.monitors import setup_monitor_logger_integration

app = Flask(__name__)

# 初始化
integration = setup_monitor_logger_integration(
    app_name="flask_app",
    enable_storage=True
)
integration.start()

@app.route('/api/health')
def get_health():
    """获取系统健康状态"""
    health = integration.check_and_log_health()
    return jsonify(health)

@app.route('/api/metrics')
def get_metrics():
    """获取综合报告"""
    report = integration.monitor_manager.get_summary_report()
    return jsonify(report)

@app.route('/api/performance')
def get_performance():
    """获取性能指标"""
    integration.log_performance_metrics()
    snapshot = integration.monitor_manager.get_performance_snapshot()
    return jsonify(snapshot)

@app.route('/api/database')
def get_database():
    """获取数据库指标"""
    integration.log_database_metrics()
    snapshot = integration.monitor_manager.get_database_snapshot()
    return jsonify(snapshot)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

## 日志输出示例

### 完整的监控循环日志

```
INFO:myapp.monitors:监视器日志集成已初始化: myapp
INFO:myapp.monitors:所有监视器已启用，开始监控

INFO:myapp.monitors.metrics:性能指标快照
    cpu_percent: 45.2
    memory_percent: 62.1
    memory_mb: 4096

INFO:myapp.monitors.metrics:数据库指标快照
    total_queries: 5432
    avg_query_time: 0.234
    slow_queries_count: 12

INFO:myapp.monitors.health:健康状态检查 (评分: 85, 等级: warning)
    health_score: 85
    cpu_percent: 45.2
    memory_percent: 62.1

WARNING:myapp.monitors.alerts:检测到 3 个慢查询
WARNING:myapp.monitors.alerts:慢查询: SELECT users - 1.23秒

INFO:myapp.monitors:所有监视器已禁用，监控停止
```

## 日志存储位置

默认情况下，日志文件存储在 `logs/` 目录下：

```
logs/
├── myapp.log                           # 主应用日志
├── monitor_metrics.log                 # 监视器日志
├── monitor_report_20240107_143052.json # 导出的报告
└── logs.db/                            # JSON存储（如果启用了存储集成）
    ├── myapp_logs_001.json
    ├── myapp_logs_002.json
    └── ...
```

## 配置选项

### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `app_name` | str | "monitor_system" | 应用名称 |
| `log_dir` | str | "logs" | 日志目录 |
| `monitor_log_file` | str | "monitor_metrics.log" | 监视器日志文件 |
| `enable_storage` | bool | True | 是否启用存储集成 |
| `console_output` | bool | True | 是否输出到控制台 |

### 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息（默认）
- **WARNING**: 警告信息（状态变化、新问题）
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

## 最佳实践

### 1. 启用存储集成
```python
# 推荐：启用存储集成以便后续查询和分析
integration = setup_monitor_logger_integration(
    enable_storage=True
)
```

### 2. 定期检查和生成报告
```python
# 定期检查健康状态
integration.check_and_log_health()

# 定期生成综合报告
integration.log_comprehensive_report()

# 定期导出报告
integration.export_monitoring_report()
```

### 3. 设置合理的检查间隔
```python
# 生产环境：1分钟检查一次
# 开发环境：5秒检查一次
# 关键系统：10秒检查一次
```

### 4. 使用分类日志器
```python
# 不同的事件使用不同的日志器
integration.health_logger.warning("...")     # 健康状态
integration.alert_logger.warning("...")      # 告警
integration.metrics_logger.info("...")       # 指标
```

### 5. 结合告警系统
```python
health = integration.check_and_log_health()

if health['status'] in ['degraded', 'critical']:
    send_alert()  # 发送告警（邮件、Slack等）
```

## 故障排除

### 问题 1: 监视器未启动
**症状**: 没有收到监视器日志
**解决**: 确保调用了 `integration.start()`

### 问题 2: 存储集成不工作
**症状**: JSON存储文件未生成
**解决**: 确保 `enable_storage=True` 且 `kernel.storage` 模块正常

### 问题 3: 日志文件过大
**症状**: `logs/` 目录占用空间过大
**解决**: 启用自动轮转和清理（在日志配置中）

## 相关文档

- [监视器系统文档](./README.md)
- [日志系统文档](../../kernel/logger/README.md)
- [日志存储集成](../../kernel/logger/LOGGER_STORAGE_INTEGRATION.md)
- [性能监视器](./performance_monitor/README.md)
- [数据库监视器](./database_monitor/README.md)

## 许可证

遵循项目主许可证
