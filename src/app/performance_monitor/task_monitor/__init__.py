"""
任务管理器监视模块 [示例模块 - 将在后续开发中移除]

提供对TaskManager的非入侵式监视，不改动TaskManager的原有代码
支持：
- 任务生命周期监控
- 任务执行时间统计
- 任务队列状态监控
- 任务错误/异常跟踪

注意：此模块为示例模块，将在后续开发过程中移除。
如需持续使用，请根据实际需求进行改进或迁移。
"""

from .interceptor import TaskManagerInterceptor
from .metrics import TaskManagerMetrics
from .monitor import TaskManagerMonitor, attach_monitor

__all__ = [
    'TaskManagerInterceptor',
    'TaskManagerMetrics',
    'TaskManagerMonitor',
    'attach_monitor',
]
