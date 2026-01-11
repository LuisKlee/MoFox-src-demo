"""
MoFox Bot Package

MoFox 机器人应用层，提供完整的 Bot 功能。

包含：
- Core API: Core 层统一接口
- Kernel API: Kernel 层统一接口
- Bot 启动器: 应用主入口

作者: MoFox Team
日期: 2026-01-11
"""

from app.bot.core_api.core_api import MoFoxCore, get_core, create_core
from app.bot.kernel_api_legacy.kernel_api import MoFoxKernel

__version__ = "0.1.0"
__author__ = "MoFox Team"

__all__ = [
    "MoFoxCore",
    "MoFoxKernel",
    "get_core",
    "create_core",
]
