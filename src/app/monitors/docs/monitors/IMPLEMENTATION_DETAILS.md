# 监视器与日志系统集成实现说明

## 📋 目录

1. [集成方案设计](#集成方案设计)
2. [实现架构](#实现架构)
3. [核心组件](#核心组件)
4. [集成流程](#集成流程)
5. [技术细节](#技术细节)
6. [测试用例](#测试用例)
7. [常见问题](#常见问题)

## 集成方案设计

### 设计目标

1. **最小化破坏**: 不修改现有的日志系统和监视器系统
2. **零配置**: 一行代码启动集成，无需复杂配置
3. **自动化**: 自动记录、检测和告警
4. **可扩展**: 易于扩展新的监控项目和告警规则
5. **持久化**: 支持长期数据存储和分析

### 设计原则

| 原则 | 实现方式 |
|------|---------|
| 单一职责 | 每个类只负责一个功能（集成、记录、告警等） |
| 开闭原则 | 易于扩展新功能，对修改关闭 |
| 依赖倒置 | 依赖抽象接口而非具体实现 |
| 组合优于继承 | 通过组合不同的日志器和管理器实现功能 |

## 实现架构

### 系统组件关系

```
┌─────────────────────────────────────────────────────────┐
│  应用层 (Application Layer)                             │
│  ├─ setup_monitor_logger_integration()                  │
│  └─ get_monitor_logger_integration()                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌─────────────────────▼────────────────────────────────────┐
│  集成层 (Integration Layer)                             │
│  └─ MonitorLoggerIntegration                            │
│     ├─ 生命周期管理: start() / stop()                   │
│     ├─ 事件记录: log_*() 系列方法                       │
│     ├─ 状态追踪: check_and_log_health()                │
│     └─ 报告生成: export_monitoring_report()             │
└────────────────────┬────────────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────────┐  ┌───▼────────┐  ┌───▼──────────┐
│ 监视器层   │  │ 日志层     │  │ 存储层       │
├────────────┤  ├────────────┤  ├──────────────┤
│ Monitor    │  │ Logger     │  │ Storage      │
│ Manager    │  │ With       │  │              │
│            │  │ Storage    │  │              │
├────────────┤  ├────────────┤  ├──────────────┤
│ • perf     │  │ • handlers │  │ • JSON       │
│ • database │  │ • formatters│  │   store     │
│ • metrics  │  │ • config   │  │              │
└────────────┘  └────────────┘  └──────────────┘
```

### 数据流

```
监视器数据采集
    │
    ├─→ MonitorManager.get_*_snapshot()
    │        │
    │        ├─→ Performance Monitor (CPU, Memory, etc.)
    │        └─→ Database Monitor (Queries, Performance)
    │
    ▼
MonitorLoggerIntegration
    │
    ├─→ log_performance_metrics()
    ├─→ log_database_metrics()
    ├─→ check_and_log_health()
    │     ├─→ 检测健康状态变化
    │     ├─→ 检测新问题
    │     └─→ 检测问题解决
    ├─→ log_slow_queries()
    └─→ log_comprehensive_report()
    │
    ├─→ health_logger.info/warning()
    ├─→ metrics_logger.info()
    ├─→ alert_logger.warning()
    └─→ logger.info()
    │
    ▼
logging.Handler
    │
    ├─→ ConsoleHandler (console output)
    ├─→ FileHandler (file output)
    └─→ LogStoreHandler (JSON storage)
    │
    ▼
输出：
- Console
- Log Files  
- JSON Storage
```

## 核心组件

### 1. MonitorLoggerIntegration 类

**职责**: 整合监视器和日志系统，提供统一接口

**核心属性**:
```python
self.monitor_manager         # 监视器管理器
self.logger_system           # 日志存储系统（可选）
self.logger                  # 通用日志器
self.health_logger           # 健康状态日志器
self.metrics_logger          # 指标日志器
self.alert_logger            # 告警日志器
```

**关键方法**:

| 方法 | 功能 | 日志输出 |
|------|------|---------|
| `start()` | 启动监视器 | INFO |
| `stop()` | 停止监视器 | INFO |
| `check_and_log_health()` | 检查健康状态 | INFO/WARNING |
| `log_performance_metrics()` | 记录性能指标 | INFO |
| `log_database_metrics()` | 记录数据库指标 | INFO |
| `log_slow_queries()` | 检测慢查询 | WARNING |
| `log_comprehensive_report()` | 生成综合报告 | INFO |

### 2. 日志器分类系统

```
根日志器 (root logger)
├─ myapp                    # 应用通用日志
│  └─ monitors             # 监视器模块
│     ├─ health           # 健康状态日志
│     ├─ metrics          # 性能/数据库指标
│     └─ alerts           # 异常告警
```

**日志级别映射**:

| 事件类型 | 日志级别 | 日志器 | 示例 |
|---------|---------|--------|------|
| 监视器启动/停止 | INFO | `logger` | "所有监视器已启用" |
| 正常指标记录 | INFO | `metrics_logger` | "性能指标快照" |
| 健康状态初始化 | INFO | `health_logger` | "系统健康状态初始化" |
| 状态变化 | WARNING | `health_logger` | "状态从 healthy 变为 warning" |
| 新问题检测 | WARNING | `alert_logger` | "检测到新问题: CPU过高" |
| 问题消除 | INFO | `alert_logger` | "问题已解决: CPU过高" |
| 慢查询 | WARNING | `alert_logger` | "检测到 N 个慢查询" |

### 3. 状态追踪机制

#### 健康状态变化检测

```python
# 保存上一次的状态
self._last_health_status = None
self._last_issues = []

# 检测变化
current_status = health['status']  # 'healthy', 'warning', 'degraded', 'critical'
current_issues = health['issues']

# 状态变化
if self._last_health_status != current_status:
    _log_status_change(old, new, score)

# 新问题
new_issues = set(current_issues) - set(self._last_issues)
for issue in new_issues:
    _log_new_issue(issue, score)

# 问题消除
resolved = set(self._last_issues) - set(current_issues)
for issue in resolved:
    _log_resolved_issue(issue, score)
```

## 集成流程

### 初始化流程

```python
# 1. 创建实例
integration = MonitorLoggerIntegration(
    app_name="myapp",
    enable_storage=True
)
    │
    ├─ 创建日志目录
    ├─ 初始化 LoggerWithStorage
    ├─ 配置日志系统
    ├─ 获取各类日志器
    └─ 获取监视器管理器

# 2. 启动
integration.start()
    │
    └─ monitor_manager.enable_all()
       ├─ performance_monitor.start()
       └─ database_monitor.enable()
```

### 运行流程

```python
# 定期执行
while True:
    # 1. 检查健康状态（最重要）
    health = integration.check_and_log_health()
        │
        ├─ 获取当前健康状态
        ├─ 与上次状态对比
        ├─ 检测状态变化 → 记录警告
        ├─ 检测新问题 → 记录告警
        ├─ 检测问题消除 → 记录信息
        └─ 记录详细指标
    
    # 2. 记录各项指标
    integration.log_performance_metrics()
    integration.log_database_metrics()
    
    # 3. 检查异常
    integration.log_slow_queries()
    
    # 4. 定期生成报告（比如每小时）
    if time_for_report:
        integration.log_comprehensive_report()
        integration.export_monitoring_report()
    
    time.sleep(60)  # 检查间隔
```

### 关闭流程

```python
integration.stop()
    │
    ├─ monitor_manager.disable_all()
    │  ├─ performance_monitor.stop()
    │  └─ database_monitor.disable()
    │
    └─ 记录停止日志
```

## 技术细节

### 1. 元数据支持

集成系统支持向日志中添加自定义元数据：

```python
# 日志记录包含以下元数据
extra={
    "cpu_percent": 45.2,
    "health_score": 85,
    "alert_type": "new_issue",
    # ... 其他字段
}
```

### 2. 异常处理

所有公共方法都包含异常处理：

```python
try:
    # 执行监视器操作
    health = self.monitor_manager.get_health_status()
except Exception as e:
    self.logger.error(f"获取健康状态失败: {e}")
    # 返回合理的默认值或重新抛出
```

### 3. 线程安全

- 使用监视器管理器的单例模式确保安全
- 日志系统内置线程安全机制
- 建议在后台线程中运行监控循环

### 4. 性能考虑

- `check_and_log_health()` 是相对高开销的操作（完整的系统评估）
- `log_*_metrics()` 是轻量级操作（仅读取当前快照）
- 建议每分钟检查一次健康状态，每10秒记录一次指标

## 测试用例

### 测试 1: 基本初始化

```python
def test_basic_initialization():
    integration = setup_monitor_logger_integration(app_name="test")
    
    # 验证
    assert integration is not None
    assert integration.monitor_manager is not None
    assert integration.logger is not None
    assert integration.health_logger is not None
    
    # 清理
    integration.stop()
```

### 测试 2: 启动和停止

```python
def test_start_stop():
    integration = setup_monitor_logger_integration(app_name="test")
    
    # 启动
    integration.start()
    status = integration.monitor_manager.get_status()
    assert status['all_enabled'] == True
    
    # 停止
    integration.stop()
    status = integration.monitor_manager.get_status()
    assert status['all_enabled'] == False
```

### 测试 3: 健康状态追踪

```python
def test_health_tracking():
    integration = setup_monitor_logger_integration(app_name="test")
    integration.start()
    
    # 第一次检查
    health1 = integration.check_and_log_health()
    initial_status = health1['status']
    
    # 第二次检查（状态可能不变）
    health2 = integration.check_and_log_health()
    
    # 验证状态变化检测正常工作
    # （日志中应该有状态变化的记录或没有，取决于实际情况）
    
    integration.stop()
```

### 测试 4: 日志输出

```python
def test_logging_output(caplog):
    integration = setup_monitor_logger_integration(app_name="test")
    integration.start()
    
    # 执行操作
    integration.log_performance_metrics()
    
    # 验证日志输出
    assert "性能指标快照" in caplog.text
    
    integration.stop()
```

### 测试 5: 报告导出

```python
def test_report_export(tmp_path):
    integration = setup_monitor_logger_integration(
        app_name="test",
        log_dir=str(tmp_path)
    )
    integration.start()
    
    # 导出报告
    report_file = integration.export_monitoring_report()
    
    # 验证文件生成
    assert Path(report_file).exists()
    
    # 验证文件内容
    with open(report_file) as f:
        data = json.load(f)
        assert 'health' in data
        assert 'performance' in data
        assert 'database' in data
    
    integration.stop()
```

## 常见问题

### Q1: 如何自定义日志级别？

**A**: 在创建 LoggerWithStorage 之前配置 LoggerConfig：

```python
from kernel.logger import LoggerConfig, setup_logger

config = LoggerConfig(
    level="DEBUG",  # 设置全局级别
    console_level="INFO",  # 控制台级别
    file_level="DEBUG"  # 文件级别
)
setup_logger(config)

integration = setup_monitor_logger_integration(...)
```

### Q2: 如何过滤特定类型的日志？

**A**: 直接使用相应的日志器：

```python
# 只获取告警日志
alert_logger = integration.alert_logger

# 设置级别或过滤器
alert_logger.setLevel(logging.WARNING)
```

### Q3: 如何修改健康评分规则？

**A**: 修改 MonitorManager 中的 get_health_status() 方法，或在 MonitorLoggerIntegration 中扩展：

```python
def custom_health_evaluation(self):
    # 获取原始评分
    health = self.monitor_manager.get_health_status()
    
    # 应用自定义规则
    if custom_condition:
        health['health_score'] -= 10
    
    return health
```

### Q4: 如何集成到已有的日志系统？

**A**: MonitorLoggerIntegration 会自动使用已配置的日志系统：

```python
# 先配置全局日志系统
from kernel.logger import setup_logger, LoggerConfig

config = LoggerConfig(...)
setup_logger(config)

# 然后初始化集成
integration = setup_monitor_logger_integration()
# 集成会使用已配置的日志系统
```

### Q5: 如何处理高频监控数据？

**A**: 调整检查间隔和使用异步日志记录：

```python
# 在 LoggerConfig 中启用异步
config = LoggerConfig(async_logging=True)

# 调整检查间隔
while True:
    integration.check_and_log_health()
    time.sleep(300)  # 5分钟检查一次，而不是1分钟
```

### Q6: 如何导出特定时间范围的日志？

**A**: 如果启用了存储集成，可以使用：

```python
from datetime import datetime, timedelta

# 获取过去7天的日志
logs = integration.get_monitor_logs(days=7)

# 或直接访问存储系统
if integration.logger_system:
    start_date = datetime.now() - timedelta(days=7)
    logs = integration.logger_system.log_store.get_logs(start_date=start_date)
```

---

**文档版本**: 1.0  
**最后更新**: 2026-01-07  
**作者**: System  
**审核状态**: ✅ 已完成
