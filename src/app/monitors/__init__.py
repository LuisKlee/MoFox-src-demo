"""
统一监视器管理模块 [测试/示例模块]

整合性能监视器和数据库监视器，提供统一的API接口

注意：此模块处于测试阶段，用于演示监控系统的设计模式。
将在后续开发中根据实际需求进行改进、优化或移除。
"""

from .manager import MonitorManager, get_manager
from .unified_api import unified_monitor_api
from .logger_integration import (
    MonitorLoggerIntegration,
    setup_monitor_logger_integration,
    get_monitor_logger_integration,
)

__all__ = [
    'MonitorManager',
    'get_manager',
    'unified_monitor_api',
    'MonitorLoggerIntegration',
    'setup_monitor_logger_integration',
    'get_monitor_logger_integration',
]
