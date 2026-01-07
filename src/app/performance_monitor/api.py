"""
性能监视器API接口 [测试/示例模块]

提供RESTful API端点用于性能监控

注意：此模块处于测试阶段，用于演示性能监控设计。
将在后续开发中根据实际需求进行改进、优化或移除。
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from functools import wraps
import logging

from .monitor import get_monitor

logger = logging.getLogger(__name__)


class PerformanceAPI:
    """性能监视器API接口"""
    
    def __init__(self):
        self.monitor = get_monitor()
    
    # ==================== 监控控制 ====================
    
    def start_monitoring(self) -> Dict[str, Any]:
        """
        启动性能监控
        
        Returns:
            {
                'status': 'success' | 'error',
                'message': str,
                'timestamp': datetime
            }
        """
        try:
            self.monitor.start()
            return {
                'status': 'success',
                'message': '性能监视器已启动',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"启动监控失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """
        停止性能监控
        
        Returns:
            {
                'status': 'success' | 'error',
                'message': str,
                'timestamp': datetime
            }
        """
        try:
            self.monitor.stop()
            return {
                'status': 'success',
                'message': '性能监视器已停止',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"停止监控失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取监视器状态
        
        Returns:
            {
                'status': 'success' | 'error',
                'running': bool,
                'sampling_interval': float,
                'metrics_count': int,
                'timestamp': datetime
            }
        """
        try:
            return {
                'status': 'success',
                'running': self.monitor._running,
                'sampling_interval': self.monitor.sampling_interval,
                'metrics_count': len(self.monitor.metrics.snapshots),
                'task_count': len(self.monitor.metrics.task_timings),
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    # ==================== 指标查询 ====================
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """
        获取当前性能指标
        
        Returns:
            {
                'status': 'success' | 'error',
                'data': {
                    'cpu_percent': float,
                    'memory_percent': float,
                    'memory_mb': float,
                    'process_count': int,
                    'thread_count': int,
                    'timestamp': datetime
                },
                'timestamp': datetime
            }
        """
        try:
            snapshot = self.monitor.get_current_snapshot()
            if snapshot:
                return {
                    'status': 'success',
                    'data': snapshot.to_dict(),
                    'timestamp': datetime.now().isoformat(),
                }
            else:
                return {
                    'status': 'error',
                    'message': '暂无数据',
                    'timestamp': datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"获取当前指标失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        获取性能指标摘要
        
        Returns:
            {
                'status': 'success' | 'error',
                'data': {
                    'snapshots_count': int,
                    'cpu': {'average': float, 'maximum': float},
                    'memory': {'average': float, 'maximum': float},
                    'tasks': {...}
                },
                'timestamp': datetime
            }
        """
        try:
            summary = self.monitor.get_summary()
            return {
                'status': 'success',
                'data': summary,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取摘要失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        获取历史指标数据
        
        Args:
            limit: 返回的最大记录数
        
        Returns:
            {
                'status': 'success' | 'error',
                'data': [
                    {snapshot data}, ...
                ],
                'count': int,
                'timestamp': datetime
            }
        """
        try:
            metrics = self.monitor.get_metrics()
            snapshots = metrics.snapshots[-limit:]
            return {
                'status': 'success',
                'data': [s.to_dict() for s in snapshots],
                'count': len(snapshots),
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    # ==================== 任务监控 ====================
    
    def get_task_stats(self, task_name: str) -> Dict[str, Any]:
        """
        获取任务执行统计
        
        Args:
            task_name: 任务名称
        
        Returns:
            {
                'status': 'success' | 'error',
                'data': {
                    'task_name': str,
                    'count': int,
                    'avg_time': float,
                    'min_time': float,
                    'max_time': float,
                    'total_time': float
                },
                'timestamp': datetime
            }
        """
        try:
            stats = self.monitor.metrics.get_task_stats(task_name)
            return {
                'status': 'success',
                'data': stats,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取任务统计失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_all_tasks(self) -> Dict[str, Any]:
        """
        获取所有任务统计
        
        Returns:
            {
                'status': 'success' | 'error',
                'data': {
                    'task_name': {stats}, ...
                },
                'count': int,
                'timestamp': datetime
            }
        """
        try:
            metrics = self.monitor.get_metrics()
            tasks = {
                task_name: metrics.get_task_stats(task_name)
                for task_name in metrics.task_timings.keys()
            }
            return {
                'status': 'success',
                'data': tasks,
                'count': len(tasks),
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取所有任务失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def record_task(self, task_name: str, duration: float) -> Dict[str, Any]:
        """
        记录任务执行时间
        
        Args:
            task_name: 任务名称
            duration: 执行时间（秒）
        
        Returns:
            {
                'status': 'success' | 'error',
                'message': str,
                'timestamp': datetime
            }
        """
        try:
            if duration < 0:
                return {
                    'status': 'error',
                    'message': '执行时间不能为负数',
                    'timestamp': datetime.now().isoformat(),
                }
            
            self.monitor.record_task_timing(task_name, duration)
            return {
                'status': 'success',
                'message': f'已记录任务 {task_name} 的执行时间: {duration}秒',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"记录任务失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    # ==================== 数据管理 ====================
    
    def clear_all(self) -> Dict[str, Any]:
        """
        清除所有性能数据
        
        Returns:
            {
                'status': 'success' | 'error',
                'message': str,
                'timestamp': datetime
            }
        """
        try:
            self.monitor.clear_metrics()
            return {
                'status': 'success',
                'message': '所有性能数据已清除',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"清除数据失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def reset_task(self, task_name: Optional[str] = None) -> Dict[str, Any]:
        """
        重置任务计时数据
        
        Args:
            task_name: 任务名称，如果为None则重置所有任务
        
        Returns:
            {
                'status': 'success' | 'error',
                'message': str,
                'timestamp': datetime
            }
        """
        try:
            self.monitor.reset_task_timing(task_name)
            msg = f'任务 {task_name} 已重置' if task_name else '所有任务已重置'
            return {
                'status': 'success',
                'message': msg,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"重置任务失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }


# 全局API实例
performance_api = PerformanceAPI()
