"""
TaskManager 任务管理器模块

负责管理和调度异步任务，提供：
- 任务创建与执行
- 任务优先级管理
- 任务依赖关系处理
- 任务队列管理
- 任务重试机制
- 与 Watchdog 集成的任务监控
- 并发控制
"""

from .manager import TaskManager, get_task_manager
from .models import TaskPriority, TaskState, TaskConfig, ManagedTask

__all__ = [
    'TaskManager',
    'get_task_manager',
    'TaskPriority',
    'TaskState',
    'TaskConfig',
    'ManagedTask',
]
