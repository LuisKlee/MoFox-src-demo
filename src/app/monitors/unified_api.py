"""
统一监视器API接口 [测试/示例模块]

提供统一的RESTful API端点，整合性能监视器和数据库监视器

注意：此模块处于测试阶段，用于演示监控API的设计模式。
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .manager import get_manager

logger = logging.getLogger(__name__)


class UnifiedMonitorAPI:
    """统一监视器API接口"""
    
    def __init__(self):
        self.manager = get_manager()
    
    # ==================== 统一控制接口 ====================
    
    def enable_all_monitors(self) -> Dict[str, Any]:
        """
        启用所有监视器
        
        Returns:
            {
                'status': 'success' | 'error',
                'message': str,
                'timestamp': datetime
            }
        """
        try:
            self.manager.enable_all()
            return {
                'status': 'success',
                'message': '所有监视器已启用',
                'monitors': {
                    'performance_monitor': True,
                    'database_monitor': True,
                },
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"启用所有监视器失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def disable_all_monitors(self) -> Dict[str, Any]:
        """
        禁用所有监视器
        
        Returns:
            {
                'status': 'success' | 'error',
                'message': str,
                'timestamp': datetime
            }
        """
        try:
            self.manager.disable_all()
            return {
                'status': 'success',
                'message': '所有监视器已禁用',
                'monitors': {
                    'performance_monitor': False,
                    'database_monitor': False,
                },
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"禁用所有监视器失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_monitors_status(self) -> Dict[str, Any]:
        """
        获取所有监视器状态
        
        Returns:
            {
                'status': 'success',
                'data': {...},
                'timestamp': datetime
            }
        """
        try:
            status = self.manager.get_status()
            return {
                'status': 'success',
                'data': status,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取监视器状态失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def clear_all_metrics(self) -> Dict[str, Any]:
        """
        清空所有监视器的指标数据
        
        Returns:
            {
                'status': 'success' | 'error',
                'message': str,
                'timestamp': datetime
            }
        """
        try:
            self.manager.clear_all_metrics()
            return {
                'status': 'success',
                'message': '所有监视器指标已清空',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"清空指标失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    # ==================== 综合数据接口 ====================
    
    def get_comprehensive_snapshot(self) -> Dict[str, Any]:
        """
        获取综合快照（性能 + 数据库）
        
        Returns:
            {
                'status': 'success',
                'data': {
                    'performance': {...},
                    'database': {...},
                    'status': {...}
                },
                'timestamp': datetime
            }
        """
        try:
            snapshot = self.manager.get_comprehensive_snapshot()
            return {
                'status': 'success',
                'data': snapshot,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取综合快照失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        获取系统健康状态评估
        
        Returns:
            {
                'status': 'success',
                'data': {
                    'health_score': int,
                    'health_level': str,
                    'status': str,
                    'issues': list,
                    'metrics': {...}
                },
                'timestamp': datetime
            }
        """
        try:
            health = self.manager.get_health_status()
            return {
                'status': 'success',
                'data': health,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取健康状态失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_summary_report(self) -> Dict[str, Any]:
        """
        获取综合摘要报告
        
        Returns:
            {
                'status': 'success',
                'data': {
                    'health': {...},
                    'performance': {...},
                    'database': {...},
                    'monitors_status': {...}
                },
                'timestamp': datetime
            }
        """
        try:
            report = self.manager.get_summary_report()
            return {
                'status': 'success',
                'data': report,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取摘要报告失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    # ==================== 性能监视器接口 ====================
    
    def get_performance_snapshot(self) -> Dict[str, Any]:
        """
        获取性能快照
        
        Returns:
            {
                'status': 'success',
                'data': {...},
                'timestamp': datetime
            }
        """
        try:
            snapshot = self.manager.get_performance_snapshot()
            return {
                'status': 'success',
                'data': snapshot,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取性能快照失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_performance_history(self, limit: int = 100) -> Dict[str, Any]:
        """
        获取性能历史数据
        
        Args:
            limit: 返回数量限制
            
        Returns:
            {
                'status': 'success',
                'data': [...],
                'count': int,
                'timestamp': datetime
            }
        """
        try:
            history = self.manager.get_performance_history(limit)
            return {
                'status': 'success',
                'data': history,
                'count': len(history),
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取性能历史失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_task_statistics(
        self,
        task_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取任务统计
        
        Args:
            task_name: 任务名称，None表示所有任务
            
        Returns:
            {
                'status': 'success',
                'data': {...},
                'timestamp': datetime
            }
        """
        try:
            stats = self.manager.get_task_statistics(task_name)
            return {
                'status': 'success',
                'data': stats,
                'task_name': task_name,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取任务统计失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    # ==================== 数据库监视器接口 ====================
    
    def get_database_snapshot(self) -> Dict[str, Any]:
        """
        获取数据库快照
        
        Returns:
            {
                'status': 'success',
                'data': {...},
                'timestamp': datetime
            }
        """
        try:
            snapshot = self.manager.get_database_snapshot()
            return {
                'status': 'success',
                'data': snapshot,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取数据库快照失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_slow_queries(
        self,
        threshold: Optional[float] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取慢查询列表
        
        Args:
            threshold: 慢查询阈值（秒），None使用默认值
            limit: 返回数量限制
            
        Returns:
            {
                'status': 'success',
                'data': [...],
                'count': int,
                'threshold': float,
                'timestamp': datetime
            }
        """
        try:
            slow_queries = self.manager.get_slow_queries(threshold, limit)
            
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
                'threshold': threshold or self.manager.database_monitor._slow_query_threshold,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取慢查询失败: {e}")
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
            {
                'status': 'success',
                'data': {...},
                'timestamp': datetime
            }
        """
        try:
            stats = self.manager.get_table_statistics(table_name)
            
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
        获取数据库操作统计
        
        Returns:
            {
                'status': 'success',
                'data': {...},
                'timestamp': datetime
            }
        """
        try:
            stats = self.manager.get_operation_statistics()
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


# 全局API实例
unified_monitor_api = UnifiedMonitorAPI()
