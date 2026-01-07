"""
数据库监视器核心实现 [测试/示例模块]

提供数据库操作监控、查询分析和连接池管理功能

注意：此模块处于测试阶段，用于演示数据库监控设计。
不修改底层数据库代码，通过装饰器和包装器模式进行监控。
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Optional, Callable, Any, List
from threading import Lock
from functools import wraps
import logging

from .metrics import (
    DatabaseMetrics,
    QueryMetrics,
    ConnectionMetrics,
    DatabaseSnapshot
)

logger = logging.getLogger(__name__)


class DatabaseMonitor:
    """数据库监视器"""
    
    _instance: Optional['DatabaseMonitor'] = None
    _lock = Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化数据库监视器"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.metrics = DatabaseMetrics()
        self._operation_lock = Lock()
        self._enabled = False
        self._slow_query_threshold = 1.0  # 慢查询阈值（秒）
        
        # 连接池状态（模拟）
        self._connection_pool_state = {
            'active': 0,
            'idle': 0,
            'total': 0,
            'max': 10
        }
        
        logger.info("数据库监视器已初始化")
    
    def enable(self) -> None:
        """启用监控"""
        self._enabled = True
        logger.info("数据库监控已启用")
    
    def disable(self) -> None:
        """禁用监控"""
        self._enabled = False
        logger.info("数据库监控已禁用")
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self._enabled
    
    def set_slow_query_threshold(self, threshold: float) -> None:
        """
        设置慢查询阈值
        
        Args:
            threshold: 阈值（秒）
        """
        self._slow_query_threshold = threshold
        logger.info(f"慢查询阈值已设置为: {threshold}秒")
    
    def record_query(
        self,
        operation: str,
        duration: float,
        table_name: Optional[str] = None,
        rows_affected: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> str:
        """
        记录查询操作
        
        Args:
            operation: 操作类型（select, insert, update, delete等）
            duration: 执行时间（秒）
            table_name: 表名
            rows_affected: 受影响的行数
            success: 是否成功
            error_message: 错误消息
            
        Returns:
            查询ID
        """
        if not self._enabled:
            return ""
        
        query_id = str(uuid.uuid4())
        
        query_metrics = QueryMetrics(
            query_id=query_id,
            operation=operation.lower(),
            duration=duration,
            timestamp=datetime.now(),
            table_name=table_name,
            rows_affected=rows_affected,
            success=success,
            error_message=error_message
        )
        
        with self._operation_lock:
            self.metrics.add_query(query_metrics)
        
        # 记录慢查询
        if duration >= self._slow_query_threshold:
            logger.warning(
                f"慢查询检测: {operation} on {table_name}, "
                f"耗时: {duration:.3f}秒"
            )
        
        return query_id
    
    def monitor_query(
        self,
        operation: str,
        table_name: Optional[str] = None
    ):
        """
        查询监控装饰器
        
        Args:
            operation: 操作类型
            table_name: 表名
            
        Usage:
            @monitor.monitor_query('select', 'users')
            def get_user(user_id):
                # 执行数据库查询
                pass
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self._enabled:
                    return func(*args, **kwargs)
                
                start_time = time.time()
                error_msg = None
                success = True
                result = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_msg = str(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    
                    # 尝试获取受影响的行数
                    rows_affected = None
                    if result is not None and hasattr(result, '__len__'):
                        try:
                            rows_affected = len(result)
                        except:
                            pass
                    
                    self.record_query(
                        operation=operation,
                        duration=duration,
                        table_name=table_name,
                        rows_affected=rows_affected,
                        success=success,
                        error_message=error_msg
                    )
            
            return wrapper
        return decorator
    
    def update_connection_pool(
        self,
        active: int,
        idle: int,
        total: int,
        max_connections: int,
        wait_time: float = 0.0
    ) -> None:
        """
        更新连接池状态
        
        Args:
            active: 活动连接数
            idle: 空闲连接数
            total: 总连接数
            max_connections: 最大连接数
            wait_time: 等待时间
        """
        if not self._enabled:
            return
        
        self._connection_pool_state = {
            'active': active,
            'idle': idle,
            'total': total,
            'max': max_connections
        }
        
        connection_metrics = ConnectionMetrics(
            timestamp=datetime.now(),
            active_connections=active,
            idle_connections=idle,
            total_connections=total,
            max_connections=max_connections,
            connection_wait_time=wait_time
        )
        
        with self._operation_lock:
            self.metrics.add_connection_snapshot(connection_metrics)
    
    def get_current_snapshot(self) -> DatabaseSnapshot:
        """获取当前数据库状态快照"""
        with self._operation_lock:
            summary = self.metrics.get_summary()
            operation_stats = self.metrics.get_operation_stats()
            
            # 计算慢查询数量
            slow_queries = self.metrics.get_slow_queries(
                threshold=self._slow_query_threshold
            )
            
            # 计算QPS（最近60秒）
            recent_time = datetime.now()
            recent_queries = [
                q for q in self.metrics.query_history
                if (recent_time - q.timestamp).total_seconds() <= 60
            ]
            qps = len(recent_queries) / 60.0 if recent_queries else 0.0
            
            snapshot = DatabaseSnapshot(
                timestamp=datetime.now(),
                total_queries=summary['total_queries'],
                successful_queries=summary['successful_queries'],
                failed_queries=summary['failed_queries'],
                avg_query_time=summary['avg_query_time'],
                max_query_time=summary['max_query_time'],
                min_query_time=summary['min_query_time'],
                queries_per_second=qps,
                active_connections=self._connection_pool_state['active'],
                idle_connections=self._connection_pool_state['idle'],
                total_connections=self._connection_pool_state['total'],
                operations_count={k: v['count'] for k, v in operation_stats.items()},
                slow_queries_count=len(slow_queries)
            )
            
            self.metrics.add_snapshot(snapshot)
            return snapshot
    
    def get_table_statistics(self, table_name: Optional[str] = None) -> Dict:
        """
        获取表统计信息
        
        Args:
            table_name: 表名，None表示所有表
            
        Returns:
            表统计信息字典
        """
        with self._operation_lock:
            return self.metrics.get_table_stats(table_name)
    
    def get_operation_statistics(self) -> Dict:
        """获取操作类型统计"""
        with self._operation_lock:
            return self.metrics.get_operation_stats()
    
    def get_slow_queries(
        self,
        threshold: Optional[float] = None,
        limit: int = 100
    ) -> List[QueryMetrics]:
        """
        获取慢查询列表
        
        Args:
            threshold: 慢查询阈值，None使用默认值
            limit: 返回数量限制
            
        Returns:
            慢查询列表
        """
        threshold = threshold or self._slow_query_threshold
        with self._operation_lock:
            return self.metrics.get_slow_queries(threshold, limit)
    
    def get_recent_queries(self, limit: int = 100) -> List[QueryMetrics]:
        """
        获取最近的查询记录
        
        Args:
            limit: 返回数量限制
            
        Returns:
            查询记录列表
        """
        with self._operation_lock:
            return self.metrics.get_recent_queries(limit)
    
    def clear_metrics(self) -> None:
        """清空所有监控指标"""
        with self._operation_lock:
            self.metrics.clear()
        logger.info("数据库监控指标已清空")
    
    def get_connection_pool_status(self) -> Dict:
        """获取连接池状态"""
        return dict(self._connection_pool_state)


# 全局单例实例
_monitor_instance: Optional[DatabaseMonitor] = None


def get_monitor() -> DatabaseMonitor:
    """
    获取数据库监视器单例实例
    
    Returns:
        DatabaseMonitor实例
    """
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = DatabaseMonitor()
    return _monitor_instance
