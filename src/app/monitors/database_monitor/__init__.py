"""
数据库监视器模块 [测试/示例模块]

提供数据库操作监控、性能指标收集和分析功能

注意：此模块处于测试阶段，用于演示数据库监控设计。
不修改底层数据库代码，仅通过包装器模式进行监控。
将在后续开发中根据实际需求进行改进、优化或移除。
"""

from .monitor import DatabaseMonitor, get_monitor
from .metrics import (
    DatabaseMetrics,
    QueryMetrics,
    ConnectionMetrics,
    DatabaseSnapshot
)
from .api import database_api

__all__ = [
    'DatabaseMonitor',
    'get_monitor',
    'DatabaseMetrics',
    'QueryMetrics',
    'ConnectionMetrics',
    'DatabaseSnapshot',
    'database_api',
]
