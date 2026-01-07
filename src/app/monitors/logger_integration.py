"""
监视器系统与日志系统集成模块

将统一监视器系统的数据集成到日志系统中，支持：
1. 监视器事件日志记录
2. 健康状态变化日志
3. 性能指标周期性日志
4. 异常告警日志

示例：
    from app.monitors import MonitorLoggerIntegration
    
    # 初始化集成
    integration = MonitorLoggerIntegration(app_name="myapp")
    
    # 启用监控和日志记录
    integration.start()
    
    # 定期检查和记录
    while True:
        integration.check_and_log_health()
        time.sleep(60)
"""

import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from kernel.logger import get_logger, LoggerConfig, setup_logger
from kernel.logger.storage_integration import LoggerWithStorage
from .manager import MonitorManager, get_manager


class MonitorLoggerIntegration:
    """监视器与日志系统集成器"""
    
    def __init__(
        self,
        app_name: str = "monitor_system",
        log_dir: str = "logs",
        monitor_log_file: str = "monitor_metrics.log",
        enable_storage: bool = True,
        console_output: bool = True
    ):
        """
        初始化监视器日志集成
        
        Args:
            app_name: 应用名称
            log_dir: 日志目录
            monitor_log_file: 监视器日志文件名
            enable_storage: 是否使用存储集成
            console_output: 是否输出到控制台
        """
        self.app_name = app_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.monitor_log_file = self.log_dir / monitor_log_file
        
        # 初始化日志系统（可选的存储集成）
        if enable_storage:
            self.logger_system = LoggerWithStorage(
                app_name=app_name,
                log_dir=str(self.log_dir),
                console_output=console_output,
                json_storage=True
            )
        else:
            config = LoggerConfig(
                level="DEBUG",
                console_enabled=console_output,
                console_colors=True,
                file_enabled=True,
                file_path=str(self.log_dir / f"{app_name}.log")
            )
            setup_logger(config)
            self.logger_system = None
        
        # 获取监视器日志器
        self.logger = get_logger(f"{app_name}.monitors")
        self.health_logger = get_logger(f"{app_name}.monitors.health")
        self.metrics_logger = get_logger(f"{app_name}.monitors.metrics")
        self.alert_logger = get_logger(f"{app_name}.monitors.alerts")
        
        # 获取监视器管理器
        self.monitor_manager = get_manager()
        
        # 跟踪上一个健康状态（用于检测状态变化）
        self._last_health_status = None
        self._last_issues = []
        
        self.logger.info(f"监视器日志集成已初始化: {app_name}")
    
    def start(self) -> None:
        """启动监视器"""
        self.monitor_manager.enable_all()
        self.logger.info("所有监视器已启用，开始监控")
    
    def stop(self) -> None:
        """停止监视器"""
        self.monitor_manager.disable_all()
        self.logger.info("所有监视器已禁用，监控停止")
    
    def log_status(self) -> None:
        """记录当前监视器状态"""
        status = self.monitor_manager.get_status()
        
        self.metrics_logger.info(
            "监视器状态更新",
            extra={
                "performance_enabled": status['performance_monitor']['enabled'],
                "database_enabled": status['database_monitor']['enabled'],
                "performance_metrics": status['performance_monitor']['metrics_count'],
                "database_metrics": status['database_monitor']['query_history_count'],
            }
        )
    
    def log_performance_metrics(self) -> None:
        """记录性能指标"""
        snapshot = self.monitor_manager.get_performance_snapshot()
        
        self.metrics_logger.info(
            "性能指标快照",
            extra={
                "cpu_percent": snapshot.get('cpu_percent', 0),
                "memory_percent": snapshot.get('memory_percent', 0),
                "memory_mb": snapshot.get('memory_mb', 0),
                "process_count": snapshot.get('process_count', 0),
                "thread_count": snapshot.get('thread_count', 0),
            }
        )
    
    def log_database_metrics(self) -> None:
        """记录数据库指标"""
        snapshot = self.monitor_manager.get_database_snapshot()
        
        self.metrics_logger.info(
            "数据库指标快照",
            extra={
                "total_queries": snapshot.get('total_queries', 0),
                "successful_queries": snapshot.get('successful_queries', 0),
                "failed_queries": snapshot.get('failed_queries', 0),
                "avg_query_time": snapshot.get('avg_query_time', 0),
                "queries_per_second": snapshot.get('queries_per_second', 0),
                "slow_queries_count": snapshot.get('slow_queries_count', 0),
            }
        )
    
    def check_and_log_health(self) -> Dict[str, Any]:
        """
        检查健康状态并记录变化
        
        Returns:
            健康状态字典
        """
        health = self.monitor_manager.get_health_status()
        health_data = health.get('data', {})
        
        current_status = health_data.get('status', 'unknown')
        current_score = health_data.get('health_score', 0)
        current_issues = health_data.get('issues', [])
        
        # 检测状态变化
        if self._last_health_status != current_status:
            self._log_status_change(self._last_health_status, current_status, current_score)
            self._last_health_status = current_status
        
        # 检测新问题
        new_issues = set(current_issues) - set(self._last_issues)
        for issue in new_issues:
            self._log_new_issue(issue, current_score)
        
        # 检测问题消除
        resolved_issues = set(self._last_issues) - set(current_issues)
        for issue in resolved_issues:
            self._log_resolved_issue(issue, current_score)
        
        self._last_issues = current_issues
        
        # 记录健康状态
        self.health_logger.info(
            f"健康状态检查 (评分: {current_score}, 等级: {current_status})",
            extra={
                "health_score": current_score,
                "health_level": health_data.get('health_level', 'unknown'),
                "health_status": current_status,
                "issues_count": len(current_issues),
                "cpu_percent": health_data.get('metrics', {}).get('cpu_percent', 0),
                "memory_percent": health_data.get('metrics', {}).get('memory_percent', 0),
                "avg_query_time": health_data.get('metrics', {}).get('avg_query_time', 0),
            }
        )
        
        return health_data
    
    def _log_status_change(self, old_status: Optional[str], new_status: str, score: int) -> None:
        """记录健康状态变化"""
        if old_status is None:
            self.health_logger.warning(
                f"系统健康状态初始化为: {new_status} (评分: {score})",
                extra={
                    "old_status": "unknown",
                    "new_status": new_status,
                    "health_score": score,
                }
            )
        else:
            level = logging.WARNING if new_status in ['degraded', 'critical'] else logging.INFO
            self.health_logger.log(
                level,
                f"系统健康状态从 {old_status} 变为 {new_status} (评分: {score})",
                extra={
                    "old_status": old_status,
                    "new_status": new_status,
                    "health_score": score,
                }
            )
    
    def _log_new_issue(self, issue: str, score: int) -> None:
        """记录新问题"""
        self.alert_logger.warning(
            f"检测到新问题: {issue} (当前评分: {score})",
            extra={
                "issue": issue,
                "health_score": score,
                "alert_type": "new_issue",
            }
        )
    
    def _log_resolved_issue(self, issue: str, score: int) -> None:
        """记录已解决的问题"""
        self.alert_logger.info(
            f"问题已解决: {issue} (当前评分: {score})",
            extra={
                "issue": issue,
                "health_score": score,
                "alert_type": "resolved_issue",
            }
        )
    
    def log_slow_queries(self, threshold: Optional[float] = None, limit: int = 10) -> None:
        """记录慢查询"""
        slow_queries = self.monitor_manager.get_slow_queries(
            threshold=threshold,
            limit=limit
        )
        
        if slow_queries:
            self.alert_logger.warning(
                f"检测到 {len(slow_queries)} 个慢查询",
                extra={
                    "slow_queries_count": len(slow_queries),
                    "query_count": len(slow_queries),
                }
            )
            
            for query in slow_queries[:5]:  # 只记录前5个
                self.alert_logger.warning(
                    f"慢查询: {query.operation} {query.table_name} - {query.duration:.2f}秒",
                    extra={
                        "operation": query.operation,
                        "table_name": query.table_name,
                        "duration": query.duration,
                        "alert_type": "slow_query",
                    }
                )
    
    def log_comprehensive_report(self) -> Dict[str, Any]:
        """记录综合报告"""
        report = self.monitor_manager.get_summary_report()
        report_data = report.get('data', {})
        
        self.logger.info(
            "生成综合监控报告",
            extra={
                "health_score": report_data.get('health', {}).get('health_score', 0),
                "cpu_percent": report_data.get('performance', {}).get('cpu_percent', 0),
                "memory_percent": report_data.get('performance', {}).get('memory_percent', 0),
                "total_queries": report_data.get('database', {}).get('total_queries', 0),
                "avg_query_time": report_data.get('database', {}).get('avg_query_time', 0),
            }
        )
        
        return report_data
    
    def get_monitor_logs(self, days: int = 1) -> Dict[str, Any]:
        """
        获取监视器日志统计（如果使用了存储集成）
        
        Args:
            days: 获取最近N天的日志
            
        Returns:
            日志统计信息
        """
        if self.logger_system:
            return self.logger_system.get_logs(days=days)
        return {}
    
    def export_monitoring_report(self, output_file: Optional[str] = None) -> str:
        """
        导出监控报告
        
        Args:
            output_file: 输出文件路径，如果为None则自动生成
            
        Returns:
            生成的文件路径
        """
        import json
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = str(self.log_dir / f"monitor_report_{timestamp}.json")
        
        # 收集综合报告
        report = self.monitor_manager.get_summary_report()
        
        # 保存为JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"监控报告已导出: {output_file}")
        
        return output_file


# 全局集成实例
_integration_instance: Optional[MonitorLoggerIntegration] = None


def setup_monitor_logger_integration(
    app_name: str = "monitor_system",
    log_dir: str = "logs",
    enable_storage: bool = True
) -> MonitorLoggerIntegration:
    """
    初始化并返回全局监视器日志集成实例
    
    Args:
        app_name: 应用名称
        log_dir: 日志目录
        enable_storage: 是否使用存储集成
        
    Returns:
        MonitorLoggerIntegration 实例
    """
    global _integration_instance
    
    if _integration_instance is None:
        _integration_instance = MonitorLoggerIntegration(
            app_name=app_name,
            log_dir=log_dir,
            enable_storage=enable_storage
        )
    
    return _integration_instance


def get_monitor_logger_integration() -> MonitorLoggerIntegration:
    """获取全局监视器日志集成实例"""
    global _integration_instance
    
    if _integration_instance is None:
        _integration_instance = setup_monitor_logger_integration()
    
    return _integration_instance
