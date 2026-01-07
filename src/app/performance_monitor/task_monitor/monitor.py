"""
任务管理器监视器 [示例模块 - 将在后续开发中移除]

提供非入侵式的TaskManager监视功能

注意：此模块为示例模块，将在后续开发过程中移除。
如需持续使用，请根据实际需求进行改进或迁移。
"""

from typing import Any, Optional, Dict
from datetime import datetime
import logging

from .interceptor import TaskManagerInterceptor
from .metrics import TaskManagerMetrics

logger = logging.getLogger(__name__)


class TaskManagerMonitor:
    """
    任务管理器监视器
    
    通过拦截器模式对TaskManager进行非入侵式监视
    """
    
    def __init__(self, task_manager: Any):
        """
        初始化监视器
        
        Args:
            task_manager: TaskManager实例
        """
        self.task_manager = task_manager
        self.metrics = TaskManagerMetrics()
        self.interceptor = TaskManagerInterceptor(task_manager, self.metrics)
        self._enabled = False
    
    def enable(self) -> Dict[str, Any]:
        """启用监视"""
        self._enabled = True
        return {
            'status': 'success',
            'message': '任务管理器监视已启用',
            'timestamp': datetime.now().isoformat(),
        }
    
    def disable(self) -> Dict[str, Any]:
        """禁用监视"""
        self._enabled = False
        return {
            'status': 'success',
            'message': '任务管理器监视已禁用',
            'timestamp': datetime.now().isoformat(),
        }
    
    def is_enabled(self) -> bool:
        """检查监视是否启用"""
        return self._enabled
    
    def record_task_created(self, task_id: str, task_name: str, metadata: Optional[dict] = None) -> None:
        """记录任务创建"""
        if self._enabled:
            self.interceptor.on_task_created(task_id, task_name, metadata)
    
    def record_task_started(self, task_id: str, task_name: str, metadata: Optional[dict] = None) -> None:
        """记录任务开始"""
        if self._enabled:
            self.interceptor.on_task_started(task_id, task_name, metadata)
    
    def record_task_completed(self, task_id: str, task_name: str, metadata: Optional[dict] = None) -> None:
        """记录任务完成"""
        if self._enabled:
            self.interceptor.on_task_completed(task_id, task_name, metadata)
    
    def record_task_failed(self, task_id: str, task_name: str, error: str, metadata: Optional[dict] = None) -> None:
        """记录任务失败"""
        if self._enabled:
            self.interceptor.on_task_failed(task_id, task_name, error, metadata)
    
    def record_task_cancelled(self, task_id: str, task_name: str, metadata: Optional[dict] = None) -> None:
        """记录任务取消"""
        if self._enabled:
            self.interceptor.on_task_cancelled(task_id, task_name, metadata)
    
    def record_task_timeout(self, task_id: str, task_name: str, timeout: float, metadata: Optional[dict] = None) -> None:
        """记录任务超时"""
        if self._enabled:
            self.interceptor.on_task_timeout(task_id, task_name, timeout, metadata)
    
    def record_task_retry(self, task_id: str, task_name: str, retry_count: int, metadata: Optional[dict] = None) -> None:
        """记录任务重试"""
        if self._enabled:
            self.interceptor.on_task_retry(task_id, task_name, retry_count, metadata)
    
    # ==================== 数据查询 ====================
    
    def get_status(self) -> Dict[str, Any]:
        """获取监视器状态"""
        summary = self.metrics.get_summary()
        return {
            'status': 'success',
            'enabled': self._enabled,
            'summary': summary,
            'timestamp': datetime.now().isoformat(),
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取任务统计摘要"""
        return {
            'status': 'success',
            'data': self.metrics.get_summary(),
            'timestamp': datetime.now().isoformat(),
        }
    
    def get_task_stats(self, task_name: str) -> Dict[str, Any]:
        """获取特定任务统计"""
        stats = self.metrics.get_task_stats(task_name)
        if stats:
            return {
                'status': 'success',
                'data': stats,
                'timestamp': datetime.now().isoformat(),
            }
        else:
            return {
                'status': 'error',
                'message': f'未找到任务: {task_name}',
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_all_tasks_stats(self) -> Dict[str, Any]:
        """获取所有任务统计"""
        return {
            'status': 'success',
            'data': self.metrics.get_all_tasks_stats(),
            'count': len(self.metrics.task_stats),
            'timestamp': datetime.now().isoformat(),
        }
    
    def get_events(self, limit: int = 100, task_name: Optional[str] = None) -> Dict[str, Any]:
        """获取事件日志"""
        events = self.metrics.events
        
        # 按任务名过滤
        if task_name:
            events = [e for e in events if e.task_name == task_name]
        
        # 获取最新的limit个事件
        events = events[-limit:]
        
        return {
            'status': 'success',
            'data': [e.to_dict() for e in events],
            'count': len(events),
            'timestamp': datetime.now().isoformat(),
        }
    
    def clear_metrics(self) -> Dict[str, Any]:
        """清除所有监视数据"""
        self.metrics.clear()
        return {
            'status': 'success',
            'message': '监视数据已清除',
            'timestamp': datetime.now().isoformat(),
        }


# 全局监视器实例
_task_monitor: Optional[TaskManagerMonitor] = None


def attach_monitor(task_manager: Any) -> TaskManagerMonitor:
    """
    将监视器附加到TaskManager
    
    Args:
        task_manager: TaskManager实例
    
    Returns:
        TaskManagerMonitor实例
    """
    global _task_monitor
    _task_monitor = TaskManagerMonitor(task_manager)
    _task_monitor.enable()
    return _task_monitor


def get_task_monitor() -> Optional[TaskManagerMonitor]:
    """获取全局任务监视器"""
    return _task_monitor
