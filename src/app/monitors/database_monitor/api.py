"""
数据库监视器API接口 [测试/示例模块]

提供RESTful API端点用于数据库监控

注意：此模块处于测试阶段，用于演示数据库监控设计。
将在后续开发中根据实际需求进行改进、优化或移除。
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from .monitor import get_monitor
from .metrics import QueryMetrics

logger = logging.getLogger(__name__)


class DatabaseAPI:
    """数据库监视器API接口"""
    
    def __init__(self):
        self.monitor = get_monitor()
    
    # ==================== 监控控制 ====================
    
    def enable_monitoring(self) -> Dict[str, Any]:
        """
        启用数据库监控
        
        Returns:
            {
                'status': 'success' | 'error',
                'message': str,
                'timestamp': datetime
            }
        """
        try:
            self.monitor.enable()
            return {
                'status': 'success',
                'message': '数据库监控已启用',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"启用监控失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def disable_monitoring(self) -> Dict[str, Any]:
        """
        禁用数据库监控
        
        Returns:
            {
                'status': 'success' | 'error',
                'message': str,
                'timestamp': datetime
            }
        """
        try:
            self.monitor.disable()
            return {
                'status': 'success',
                'message': '数据库监控已禁用',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"禁用监控失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取监控状态
        
        Returns:
            {
                'status': 'success',
                'enabled': bool,
                'slow_query_threshold': float,
                'metrics_count': int,
                'timestamp': datetime
            }
        """
        try:
            return {
                'status': 'success',
                'enabled': self.monitor.is_enabled(),
                'slow_query_threshold': self.monitor._slow_query_threshold,
                'query_history_count': len(self.monitor.metrics.query_history),
                'connection_history_count': len(self.monitor.metrics.connection_history),
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def set_slow_query_threshold(self, threshold: float) -> Dict[str, Any]:
        """
        设置慢查询阈值
        
        Args:
            threshold: 阈值（秒）
            
        Returns:
            响应字典
        """
        try:
            if threshold <= 0:
                return {
                    'status': 'error',
                    'message': '阈值必须大于0',
                    'timestamp': datetime.now().isoformat(),
                }
            
            self.monitor.set_slow_query_threshold(threshold)
            return {
                'status': 'success',
                'message': f'慢查询阈值已设置为: {threshold}秒',
                'threshold': threshold,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"设置慢查询阈值失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    # ==================== 数据查询 ====================
    
    def get_current_snapshot(self) -> Dict[str, Any]:
        """
        获取当前数据库状态快照
        
        Returns:
            {
                'status': 'success',
                'data': {...},
                'timestamp': datetime
            }
        """
        try:
            snapshot = self.monitor.get_current_snapshot()
            return {
                'status': 'success',
                'data': {
                    'timestamp': snapshot.timestamp.isoformat(),
                    'total_queries': snapshot.total_queries,
                    'successful_queries': snapshot.successful_queries,
                    'failed_queries': snapshot.failed_queries,
                    'avg_query_time': round(snapshot.avg_query_time, 4),
                    'max_query_time': round(snapshot.max_query_time, 4),
                    'min_query_time': round(snapshot.min_query_time, 4),
                    'queries_per_second': round(snapshot.queries_per_second, 2),
                    'active_connections': snapshot.active_connections,
                    'idle_connections': snapshot.idle_connections,
                    'total_connections': snapshot.total_connections,
                    'operations_count': snapshot.operations_count,
                    'slow_queries_count': snapshot.slow_queries_count,
                },
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取快照失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_table_statistics(
        self,
        table_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取表统计信息
        
        Args:
            table_name: 表名，None表示所有表
            
        Returns:
            表统计信息响应
        """
        try:
            stats = self.monitor.get_table_statistics(table_name)
            
            # 处理无穷大值
            for table, table_stats in stats.items():
                if table_stats.get('min_time') == float('inf'):
                    table_stats['min_time'] = 0.0
            
            return {
                'status': 'success',
                'data': stats,
                'table_name': table_name,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取表统计失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_operation_statistics(self) -> Dict[str, Any]:
        """
        获取操作类型统计
        
        Returns:
            操作统计信息响应
        """
        try:
            stats = self.monitor.get_operation_statistics()
            return {
                'status': 'success',
                'data': stats,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取操作统计失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_slow_queries(
        self,
        threshold: Optional[float] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        获取慢查询列表
        
        Args:
            threshold: 慢查询阈值（秒），None使用默认值
            limit: 返回数量限制
            
        Returns:
            慢查询列表响应
        """
        try:
            slow_queries = self.monitor.get_slow_queries(threshold, limit)
            
            # 转换为字典列表
            queries_data = [
                {
                    'query_id': q.query_id,
                    'operation': q.operation,
                    'duration': round(q.duration, 4),
                    'timestamp': q.timestamp.isoformat(),
                    'table_name': q.table_name,
                    'rows_affected': q.rows_affected,
                    'success': q.success,
                    'error_message': q.error_message,
                }
                for q in slow_queries
            ]
            
            return {
                'status': 'success',
                'data': queries_data,
                'count': len(queries_data),
                'threshold': threshold or self.monitor._slow_query_threshold,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取慢查询失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_recent_queries(self, limit: int = 100) -> Dict[str, Any]:
        """
        获取最近的查询记录
        
        Args:
            limit: 返回数量限制
            
        Returns:
            查询记录列表响应
        """
        try:
            queries = self.monitor.get_recent_queries(limit)
            
            # 转换为字典列表
            queries_data = [
                {
                    'query_id': q.query_id,
                    'operation': q.operation,
                    'duration': round(q.duration, 4),
                    'timestamp': q.timestamp.isoformat(),
                    'table_name': q.table_name,
                    'rows_affected': q.rows_affected,
                    'success': q.success,
                    'error_message': q.error_message,
                }
                for q in queries
            ]
            
            return {
                'status': 'success',
                'data': queries_data,
                'count': len(queries_data),
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取最近查询失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_connection_pool_status(self) -> Dict[str, Any]:
        """
        获取连接池状态
        
        Returns:
            连接池状态响应
        """
        try:
            status = self.monitor.get_connection_pool_status()
            return {
                'status': 'success',
                'data': status,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取连接池状态失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    # ==================== 数据管理 ====================
    
    def clear_metrics(self) -> Dict[str, Any]:
        """
        清空所有监控指标
        
        Returns:
            响应字典
        """
        try:
            self.monitor.clear_metrics()
            return {
                'status': 'success',
                'message': '监控指标已清空',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"清空指标失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    # ==================== 手动记录 ====================
    
    def record_query(
        self,
        operation: str,
        duration: float,
        table_name: Optional[str] = None,
        rows_affected: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        手动记录查询操作
        
        Args:
            operation: 操作类型
            duration: 执行时间（秒）
            table_name: 表名
            rows_affected: 受影响的行数
            success: 是否成功
            error_message: 错误消息
            
        Returns:
            响应字典
        """
        try:
            query_id = self.monitor.record_query(
                operation=operation,
                duration=duration,
                table_name=table_name,
                rows_affected=rows_affected,
                success=success,
                error_message=error_message
            )
            
            return {
                'status': 'success',
                'query_id': query_id,
                'message': '查询已记录',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"记录查询失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def update_connection_pool(
        self,
        active: int,
        idle: int,
        total: int,
        max_connections: int,
        wait_time: float = 0.0
    ) -> Dict[str, Any]:
        """
        更新连接池状态
        
        Args:
            active: 活动连接数
            idle: 空闲连接数
            total: 总连接数
            max_connections: 最大连接数
            wait_time: 等待时间
            
        Returns:
            响应字典
        """
        try:
            self.monitor.update_connection_pool(
                active=active,
                idle=idle,
                total=total,
                max_connections=max_connections,
                wait_time=wait_time
            )
            
            return {
                'status': 'success',
                'message': '连接池状态已更新',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"更新连接池状态失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }


# 全局API实例
database_api = DatabaseAPI()
