"""
MoFox Storage - 本地持久化存储模块

提供统一的JSON本地持久化操作，支持字典、列表、日志等多种存储方式

支持两个版本：
- Python 版本：标准实现，无额外依赖
- C++ 版本：性能优化版本（需要编译）

基本使用：
    from kernel.storage import JSONStore, DictJSONStore, ListJSONStore
    
    # 通用JSON存储
    store = JSONStore("data/config.json")
    data = store.read()
    store.write({"key": "value"})
    
    # 字典存储
    dict_store = DictJSONStore("data/settings.json")
    dict_store.set("theme", "dark")
    theme = dict_store.get("theme")
    
    # 列表存储
    list_store = ListJSONStore("data/items.json")
    list_store.append({"id": 1, "name": "Item 1"})
    
    # 日志存储
    log_store = LogStore("logs/app_logs")
    log_store.add_log({"level": "INFO", "message": "Application started"})

切换版本：
    # 使用 C++ 版本（如果可用）
    from kernel.storage import use_cpp_version
    use_cpp_version(True)
    
    # 检查当前使用的版本
    from kernel.storage import get_current_backend
    backend = get_current_backend()  # 返回 'cpp' 或 'python'
"""

import os
import logging

logger = logging.getLogger(__name__)

# 版本控制
_use_cpp = os.getenv('MOFOX_USE_CPP_STORAGE', 'false').lower() in ('true', '1', 'yes')
_cpp_available = False


def _try_load_cpp():
    """尝试加载 C++ 版本"""
    global _cpp_available
    try:
        from .cpp_adapter import is_cpp_available
        _cpp_available = is_cpp_available()
        return _cpp_available
    except Exception as e:
        logger.debug(f"Failed to load C++ adapter: {e}")
        _cpp_available = False
        return False


def use_cpp_version(enabled: bool = True) -> bool:
    """
    切换到 C++ 版本
    
    Args:
        enabled: 是否启用 C++ 版本
    
    Returns:
        是否成功切换（C++ 版本是否可用）
    """
    global _use_cpp
    
    if enabled:
        if not _cpp_available:
            _try_load_cpp()
        
        if not _cpp_available:
            logger.warning(
                "C++ version is not available. "
                "Please compile it first in src/kernel/storage/. "
                "Falling back to Python version."
            )
            _use_cpp = False
            return False
        else:
            _use_cpp = True
            logger.info("Switched to C++ storage backend")
            return True
    else:
        _use_cpp = False
        logger.info("Switched to Python storage backend")
        return True


def get_current_backend() -> str:
    """获取当前使用的后端"""
    return 'cpp' if _use_cpp else 'python'


def is_cpp_available() -> bool:
    """检查 C++ 版本是否可用"""
    if not _cpp_available:
        _try_load_cpp()
    return _cpp_available


# 条件导入
if _use_cpp and _try_load_cpp():
    # 使用 C++ 版本
    logger.info("Loading C++ storage backend")
    from .cpp_adapter import (
        JSONStoreCPP as JSONStore,
        DictJSONStoreCPP as DictJSONStore,
        ListJSONStoreCPP as ListJSONStore,
        LogStoreCPP as LogStore,
        CPPStorageError as JSONStoreError,
    )
    # 定义异常别名
    FileNotFoundError = JSONStoreError
    ValidationError = JSONStoreError
else:
    # 使用 Python 版本（默认）
    if _use_cpp:
        logger.warning("C++ backend requested but not available, using Python backend")
    
    from .json_store import (
        # 核心类
        JSONStore,
        DictJSONStore,
        ListJSONStore,
        LogStore,
        
        # 异常类
        JSONStoreError,
        FileNotFoundError,
        ValidationError,
    )


__all__ = [
    # 存储类
    'JSONStore',
    'DictJSONStore',
    'ListJSONStore',
    'LogStore',
    
    # 异常
    'JSONStoreError',
    'FileNotFoundError',
    'ValidationError',
    
    # 版本控制函数
    'use_cpp_version',
    'get_current_backend',
    'is_cpp_available',
]


__version__ = '1.0.0'
__author__ = 'MoFox Team'
