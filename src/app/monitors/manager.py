"""
监视器管理器 [测试/示例模块]

统一管理性能监视器和数据库监视器

注意：此模块处于测试阶段，用于演示监控管理的设计模式。
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

# 导入两个监视器
from .performance_monitor import get_monitor as get_performance_monitor
from .database_monitor import get_monitor as get_database_monitor

logger = logging.getLogger(__name__)


class MonitorManager:
    """统一监视器管理器"""
    
    _instance: Optional['MonitorManager'] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化管理器"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # 获取两个监视器实例
        self.performance_monitor = get_performance_monitor()
        self.database_monitor = get_database_monitor()
        
        self._all_enabled = False
        
        logger.info("监视器管理器已初始化")
    
    # ==================== 统一控制 ====================
    
    def enable_all(self) -> None:
        """启用所有监视器"""
        self.performance_monitor.start()
        self.database_monitor.enable()
        self._all_enabled = True
        logger.info("所有监视器已启用")
    
    def disable_all(self) -> None:
        """禁用所有监视器"""
        self.performance_monitor.stop()
        self.database_monitor.disable()
        self._all_enabled = False
        logger.info("所有监视器已禁用")
    
    def is_all_enabled(self) -> bool:
        """检查是否所有监视器都已启用"""
        return (self.performance_monitor._running and 
                self.database_monitor.is_enabled())
    
    def get_status(self) -> Dict[str, Any]:
        """获取所有监视器状态"""
        return {
            'performance_monitor': {
                'enabled': self.performance_monitor._running,
                'sampling_interval': self.performance_monitor.sampling_interval,
                'metrics_count': len(self.performance_monitor.metrics.snapshots),
            },
            'database_monitor': {
                'enabled': self.database_monitor.is_enabled(),
                'slow_query_threshold': self.database_monitor._slow_query_threshold,
                'query_history_count': len(self.database_monitor.metrics.query_history),
            },
            'all_enabled': self.is_all_enabled(),
            'timestamp': datetime.now().isoformat(),
        }
    
    def clear_all_metrics(self) -> None:
        """清空所有监视器的指标数据"""
        self.performance_monitor.clear_metrics()
        self.database_monitor.clear_metrics()
        logger.info("所有监视器指标已清空")
    
    # ==================== 性能监视器访问 ====================
    
    def get_performance_snapshot(self) -> Dict[str, Any]:
        """获取性能快照"""
        snapshot = self.performance_monitor.get_current_snapshot()
        if snapshot is None:
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'memory_mb': 0.0,
                'process_count': 0,
                'thread_count': 0,
            }
        return {
            'timestamp': snapshot.timestamp.isoformat(),
            'cpu_percent': round(snapshot.cpu_percent, 2),
            'memory_percent': round(snapshot.memory_percent, 2),
            'memory_mb': round(snapshot.memory_mb, 2),
            'process_count': snapshot.process_count,
            'thread_count': snapshot.thread_count,
        }
    
    def get_performance_history(self, limit: int = 100) -> list:
        """获取性能历史数据"""
        snapshots = self.performance_monitor.metrics.snapshots[-limit:]
        return [
            {
                'timestamp': s.timestamp.isoformat(),
                'cpu_percent': round(s.cpu_percent, 2),
                'memory_percent': round(s.memory_percent, 2),
                'memory_mb': round(s.memory_mb, 2),
            }
            for s in snapshots
        ]
    
    def get_task_statistics(self, task_name: Optional[str] = None) -> Dict:
        """获取任务统计"""
        if task_name:
            return self.performance_monitor.metrics.get_task_stats(task_name)
        return dict(self.performance_monitor.metrics.task_timings)
    
    # ==================== 数据库监视器访问 ====================
    
    def get_database_snapshot(self) -> Dict[str, Any]:
        """获取数据库快照"""
        snapshot = self.database_monitor.get_current_snapshot()
        return {
            'timestamp': snapshot.timestamp.isoformat(),
            'total_queries': snapshot.total_queries,
            'successful_queries': snapshot.successful_queries,
            'failed_queries': snapshot.failed_queries,
            'avg_query_time': round(snapshot.avg_query_time, 4),
            'max_query_time': round(snapshot.max_query_time, 4),
            'queries_per_second': round(snapshot.queries_per_second, 2),
            'active_connections': snapshot.active_connections,
            'slow_queries_count': snapshot.slow_queries_count,
        }
    
    def get_slow_queries(self, threshold: Optional[float] = None, limit: int = 50):
        """获取慢查询列表"""
        return self.database_monitor.get_slow_queries(threshold, limit)
    
    def get_table_statistics(self, table_name: Optional[str] = None) -> Dict:
        """获取表统计"""
        return self.database_monitor.get_table_statistics(table_name)
    
    def get_operation_statistics(self) -> Dict:
        """获取数据库操作统计"""
        return self.database_monitor.get_operation_statistics()
    
    # ==================== 综合分析 ====================
    
    def get_comprehensive_snapshot(self) -> Dict[str, Any]:
        """获取综合快照（包含性能和数据库）"""
        return {
            'timestamp': datetime.now().isoformat(),
            'performance': self.get_performance_snapshot(),
            'database': self.get_database_snapshot(),
            'status': self.get_status(),
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态评估"""
        perf_snapshot = self.performance_monitor.get_current_snapshot()
        db_snapshot = self.database_monitor.get_current_snapshot()
        
        # 如果没有性能快照，返回默认健康状态
        if perf_snapshot is None:
            return {
                'timestamp': datetime.now().isoformat(),
                'health_score': 100,
                'health_level': '优秀',
                'status': 'healthy',
                'issues': [],
                'metrics': {
                    'cpu_percent': 0.0,
                    'memory_percent': 0.0,
                    'avg_query_time': 0.0,
                    'slow_queries_count': 0,
                    'query_failure_rate': 0.0,
                }
            }
        
        # 简单的健康评分逻辑
        health_score = 100
        issues = []
        
        # 检查CPU
        if perf_snapshot.cpu_percent > 80:
            health_score -= 20
            issues.append(f"CPU使用率过高: {perf_snapshot.cpu_percent:.1f}%")
        elif perf_snapshot.cpu_percent > 60:
            health_score -= 10
            issues.append(f"CPU使用率较高: {perf_snapshot.cpu_percent:.1f}%")
        
        # 检查内存
        if perf_snapshot.memory_percent > 80:
            health_score -= 20
            issues.append(f"内存使用率过高: {perf_snapshot.memory_percent:.1f}%")
        elif perf_snapshot.memory_percent > 60:
            health_score -= 10
            issues.append(f"内存使用率较高: {perf_snapshot.memory_percent:.1f}%")
        
        # 检查数据库查询
        if db_snapshot.avg_query_time > 1.0:
            health_score -= 20
            issues.append(f"平均查询时间过长: {db_snapshot.avg_query_time:.3f}秒")
        elif db_snapshot.avg_query_time > 0.5:
            health_score -= 10
            issues.append(f"平均查询时间较长: {db_snapshot.avg_query_time:.3f}秒")
        
        # 检查慢查询
        if db_snapshot.slow_queries_count > 10:
            health_score -= 15
            issues.append(f"慢查询数量过多: {db_snapshot.slow_queries_count}")
        elif db_snapshot.slow_queries_count > 5:
            health_score -= 5
            issues.append(f"检测到慢查询: {db_snapshot.slow_queries_count}")
        
        # 检查失败查询率
        if db_snapshot.total_queries > 0:
            failure_rate = (db_snapshot.failed_queries / db_snapshot.total_queries) * 100
            if failure_rate > 10:
                health_score -= 20
                issues.append(f"查询失败率过高: {failure_rate:.1f}%")
            elif failure_rate > 5:
                health_score -= 10
                issues.append(f"查询失败率较高: {failure_rate:.1f}%")
        
        # 确定健康等级
        if health_score >= 90:
            health_level = "优秀"
            status = "healthy"
        elif health_score >= 70:
            health_level = "良好"
            status = "warning"
        elif health_score >= 50:
            health_level = "一般"
            status = "degraded"
        else:
            health_level = "较差"
            status = "critical"
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health_score': max(0, health_score),
            'health_level': health_level,
            'status': status,
            'issues': issues,
            'metrics': {
                'cpu_percent': round(perf_snapshot.cpu_percent, 2),
                'memory_percent': round(perf_snapshot.memory_percent, 2),
                'avg_query_time': round(db_snapshot.avg_query_time, 4),
                'slow_queries_count': db_snapshot.slow_queries_count,
                'query_failure_rate': round(
                    (db_snapshot.failed_queries / db_snapshot.total_queries * 100)
                    if db_snapshot.total_queries > 0 else 0,
                    2
                ),
            }
        }
    
    def get_summary_report(self) -> Dict[str, Any]:
        """获取综合摘要报告"""
        perf_snapshot = self.performance_monitor.get_current_snapshot()
        db_snapshot = self.database_monitor.get_current_snapshot()
        health = self.get_health_status()
        
        # 默认性能数据
        perf_data = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_mb': 0.0,
            'thread_count': 0,
        }
        
        if perf_snapshot is not None:
            perf_data = {
                'cpu_percent': round(perf_snapshot.cpu_percent, 2),
                'memory_percent': round(perf_snapshot.memory_percent, 2),
                'memory_mb': round(perf_snapshot.memory_mb, 2),
                'thread_count': perf_snapshot.thread_count,
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health': health,
            'performance': perf_data,
            'database': {
                'total_queries': db_snapshot.total_queries,
                'successful_queries': db_snapshot.successful_queries,
                'failed_queries': db_snapshot.failed_queries,
                'avg_query_time': round(db_snapshot.avg_query_time, 4),
                'queries_per_second': round(db_snapshot.queries_per_second, 2),
                'slow_queries_count': db_snapshot.slow_queries_count,
            },
            'monitors_status': self.get_status(),
        }


# 全局单例实例
_manager_instance: Optional[MonitorManager] = None


def get_manager() -> MonitorManager:
    """
    获取监视器管理器单例实例
    
    Returns:
        MonitorManager实例
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = MonitorManager()
    return _manager_instance
