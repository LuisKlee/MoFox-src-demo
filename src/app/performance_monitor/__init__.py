"""
性能监视器模块 [测试/示例模块]

提供系统性能监控功能，包括：
- CPU使用率监控
- 内存使用率监控
- 任务执行时间监控
- 性能数据收集和分析

注意：此模块处于测试阶段，用于演示性能监控设计。
将在后续开发中根据实际需求进行改进、优化或移除。
"""

from .monitor import PerformanceMonitor, get_monitor
from .metrics import PerformanceMetrics, MetricsSnapshot
from .api import performance_api

__all__ = [
    'PerformanceMonitor',
    'get_monitor',
    'PerformanceMetrics',
    'MetricsSnapshot',
    'performance_api',
]
