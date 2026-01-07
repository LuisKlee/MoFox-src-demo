"""
任务管理器拦截器 [示例模块 - 将在后续开发中移除]

通过代理模式拦截TaskManager的方法调用，实现非入侵式监视

注意：此模块为示例模块，将在后续开发过程中移除。
如需持续使用，请根据实际需求进行改进或迁移。
"""

import time
from typing import Any, Callable, Optional
from datetime import datetime
from functools import wraps
import logging

from .metrics import TaskEvent, TaskEventType, TaskManagerMetrics

logger = logging.getLogger(__name__)


class TaskManagerInterceptor:
    """
    任务管理器拦截器
    
    使用代理模式拦截TaskManager的方法调用
    """
    
    def __init__(self, task_manager: Any, metrics: TaskManagerMetrics):
        """
        初始化拦截器
        
        Args:
            task_manager: 原始TaskManager实例
            metrics: 监视指标对象
        """
        self._manager = task_manager
        self._metrics = metrics
        self._task_start_times = {}  # 记录任务开始时间
    
    def on_task_created(self, task_id: str, task_name: str, metadata: Optional[dict] = None):
        """记录任务创建事件"""
        event = TaskEvent(
            event_type=TaskEventType.CREATED,
            task_id=task_id,
            task_name=task_name,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self._metrics.record_event(event)
        logger.debug(f"任务创建: {task_name} (ID: {task_id})")
    
    def on_task_started(self, task_id: str, task_name: str, metadata: Optional[dict] = None):
        """记录任务开始执行事件"""
        self._task_start_times[task_id] = time.time()
        event = TaskEvent(
            event_type=TaskEventType.STARTED,
            task_id=task_id,
            task_name=task_name,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self._metrics.record_event(event)
        logger.debug(f"任务开始: {task_name} (ID: {task_id})")
    
    def on_task_completed(self, task_id: str, task_name: str, metadata: Optional[dict] = None):
        """记录任务完成事件"""
        duration = None
        if task_id in self._task_start_times:
            duration = time.time() - self._task_start_times.pop(task_id)
        
        event = TaskEvent(
            event_type=TaskEventType.COMPLETED,
            task_id=task_id,
            task_name=task_name,
            timestamp=datetime.now(),
            duration=duration,
            metadata=metadata or {}
        )
        self._metrics.record_event(event)
        logger.debug(f"任务完成: {task_name} (ID: {task_id}, 耗时: {duration:.4f}s)" if duration else f"任务完成: {task_name} (ID: {task_id})")
    
    def on_task_failed(self, task_id: str, task_name: str, error: str, metadata: Optional[dict] = None):
        """记录任务失败事件"""
        duration = None
        if task_id in self._task_start_times:
            duration = time.time() - self._task_start_times.pop(task_id)
        
        event = TaskEvent(
            event_type=TaskEventType.FAILED,
            task_id=task_id,
            task_name=task_name,
            timestamp=datetime.now(),
            duration=duration,
            error=error,
            metadata=metadata or {}
        )
        self._metrics.record_event(event)
        logger.warning(f"任务失败: {task_name} (ID: {task_id}), 错误: {error}")
    
    def on_task_cancelled(self, task_id: str, task_name: str, metadata: Optional[dict] = None):
        """记录任务取消事件"""
        duration = None
        if task_id in self._task_start_times:
            duration = time.time() - self._task_start_times.pop(task_id)
        
        event = TaskEvent(
            event_type=TaskEventType.CANCELLED,
            task_id=task_id,
            task_name=task_name,
            timestamp=datetime.now(),
            duration=duration,
            metadata=metadata or {}
        )
        self._metrics.record_event(event)
        logger.debug(f"任务取消: {task_name} (ID: {task_id})")
    
    def on_task_timeout(self, task_id: str, task_name: str, timeout: float, metadata: Optional[dict] = None):
        """记录任务超时事件"""
        duration = None
        if task_id in self._task_start_times:
            duration = time.time() - self._task_start_times.pop(task_id)
        
        event = TaskEvent(
            event_type=TaskEventType.TIMEOUT,
            task_id=task_id,
            task_name=task_name,
            timestamp=datetime.now(),
            duration=duration,
            error=f"Task timeout after {timeout}s",
            metadata=metadata or {'timeout': timeout}
        )
        self._metrics.record_event(event)
        logger.warning(f"任务超时: {task_name} (ID: {task_id}), 超时: {timeout}s")
    
    def on_task_retry(self, task_id: str, task_name: str, retry_count: int, metadata: Optional[dict] = None):
        """记录任务重试事件"""
        event = TaskEvent(
            event_type=TaskEventType.RETRYING,
            task_id=task_id,
            task_name=task_name,
            timestamp=datetime.now(),
            metadata={
                **(metadata or {}),
                'retry_count': retry_count
            }
        )
        self._metrics.record_event(event)
        logger.info(f"任务重试: {task_name} (ID: {task_id}), 第 {retry_count} 次重试")
    
    def get_manager(self) -> Any:
        """获取原始TaskManager实例"""
        return self._manager


def wrap_task_manager(task_manager: Any, metrics: TaskManagerMetrics) -> TaskManagerInterceptor:
    """
    包装TaskManager实例
    
    Args:
        task_manager: 原始TaskManager实例
        metrics: 监视指标对象
    
    Returns:
        拦截器实例
    """
    return TaskManagerInterceptor(task_manager, metrics)
