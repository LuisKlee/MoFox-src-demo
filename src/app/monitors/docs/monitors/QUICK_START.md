# 监视器-日志集成快速参考

## 一行代码启动

```python
from app.monitors import setup_monitor_logger_integration

integration = setup_monitor_logger_integration(app_name="myapp")
```

## 核心操作

| 操作 | 代码 |
|------|------|
| 启动 | `integration.start()` |
| 停止 | `integration.stop()` |
| 检查健康状态 | `integration.check_and_log_health()` |
| 记录性能指标 | `integration.log_performance_metrics()` |
| 记录数据库指标 | `integration.log_database_metrics()` |
| 检查慢查询 | `integration.log_slow_queries()` |
| 生成综合报告 | `integration.log_comprehensive_report()` |
| 导出报告 | `integration.export_monitoring_report()` |

## 完整循环示例

```python
import time
from app.monitors import setup_monitor_logger_integration

# 初始化
integration = setup_monitor_logger_integration(
    app_name="myapp",
    enable_storage=True  # 推荐启用
)

# 启动
integration.start()

# 定期监控
try:
    while True:
        integration.check_and_log_health()
        integration.log_performance_metrics()
        integration.log_database_metrics()
        time.sleep(60)  # 每分钟检查一次
finally:
    integration.stop()
```

## 日志位置

- **主日志**: `logs/myapp.log`
- **指标日志**: `logs/monitor_metrics.log`
- **报告**: `logs/monitor_report_*.json`
- **存储**: `logs/logs.db/` (如果启用了存储集成)

## 访问日志器

```python
# 自定义日志记录
integration.logger.info("信息")              # 通用
integration.health_logger.warning("警告")     # 健康状态
integration.metrics_logger.info("指标")       # 性能/数据库
integration.alert_logger.warning("告警")      # 异常告警
```

## 获取监视器数据

```python
# 直接访问监视器管理器
manager = integration.monitor_manager

# 获取快照
perf = manager.get_performance_snapshot()
db = manager.get_database_snapshot()
health = manager.get_health_status()
report = manager.get_summary_report()

# 获取慢查询
slow_queries = manager.get_slow_queries(threshold=0.5, limit=10)
```

## 告警示例

```python
integration.start()

while True:
    health = integration.check_and_log_health()
    
    # 检测严重问题
    if health['status'] == 'critical':
        send_alert_email(f"系统状态严重: {health['issues']}")
    
    time.sleep(60)
```

## Web 服务集成（Flask）

```python
from flask import Flask, jsonify
from app.monitors import setup_monitor_logger_integration

app = Flask(__name__)
integration = setup_monitor_logger_integration(app_name="api")
integration.start()

@app.route('/api/health')
def health():
    health = integration.check_and_log_health()
    return jsonify(health)

@app.route('/api/report')
def report():
    return jsonify(integration.monitor_manager.get_summary_report())
```

## 配置参数

```python
setup_monitor_logger_integration(
    app_name="myapp",              # 应用名称
    log_dir="logs",                # 日志目录
    enable_storage=True,           # 启用 JSON 存储
    console_output=True,           # 控制台输出
)
```

## 日志示例

### 健康状态变化
```
WARNING:myapp.monitors.health:系统健康状态从 healthy 变为 warning (评分: 72)
```

### 新问题检测
```
WARNING:myapp.monitors.alerts:检测到新问题: CPU使用率过高
```

### 性能指标
```
INFO:myapp.monitors.metrics:性能指标快照
  cpu_percent: 45.2, memory_percent: 62.1, memory_mb: 4096
```

## 常用模式

### 模式 1: 定期监控 + 告警
```python
integration = setup_monitor_logger_integration(app_name="monitor")
integration.start()

while True:
    health = integration.check_and_log_health()
    if health['status'] in ['degraded', 'critical']:
        # 发送告警
        send_notification(health['issues'])
    time.sleep(60)
```

### 模式 2: 定时报告生成
```python
integration = setup_monitor_logger_integration(app_name="reporter")
integration.start()

# 每天生成一份报告
while True:
    if is_report_time():  # 比如每天晚上10点
        integration.log_comprehensive_report()
        integration.export_monitoring_report()
    time.sleep(3600)
```

### 模式 3: 服务健康检查
```python
integration = setup_monitor_logger_integration(app_name="service")
integration.start()

# 定期检查，如果发现问题立即重启服务
while True:
    health = integration.check_and_log_health()
    if health['health_score'] < 30:
        restart_service()
    time.sleep(300)  # 每5分钟检查
```

## 获取监控统计（需启用存储集成）

```python
# 获取最近7天的日志统计
logs = integration.get_monitor_logs(days=7)
print(f"总日志: {logs['total_logs']}")
print(f"警告: {logs['warning_count']}")
print(f"错误: {logs['error_count']}")
```

## 文档链接

- 📖 [详细指南](LOGGER_INTEGRATION.md)
- 📝 [集成总结](INTEGRATION_SUMMARY.md)
- 💻 [完整示例](../src/app/monitors/logger_integration_examples.py)
- 🔧 [API 文档](LOGGER_INTEGRATION.md#api-文档)

---

**提示**: 大多数情况下，只需要 `check_and_log_health()` 就足够了，其他方法根据需要调用。
