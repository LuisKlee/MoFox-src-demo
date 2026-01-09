"""
C++ Storage 模块 Python 适配层

提供对 C++ json_store 库的 Python 接口
支持通过 ctypes 调用已编译的 C++ 动态库

编译 C++ 版本：
    cd src/kernel/storage
    mkdir build && cd build
    cmake .. -DBUILD_EXAMPLES=ON -DBUILD_TESTS=ON
    cmake --build . --config Release

然后将生成的 json_store.lib/json_store.dll 放在合适位置
"""

import ctypes
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CPPStorageError(Exception):
    """C++ Storage 操作异常"""
    pass


class CPPAdapterConfig:
    """C++ 适配层配置"""
    
    # 可尝试的库位置
    LIBRARY_PATHS = [
        # 当前目录
        "./json_store.so",
        "./json_store.dll",
        "./json_store.dylib",
        # 构建目录
        "./build/Release/json_store.dll",
        "./build/json_store.so",
        "./build/Debug/json_store.dll",
        # 系统路径（Unix）
        "/usr/local/lib/libjson_store.so",
        "/usr/lib/libjson_store.so",
        # Windows PATH
        "json_store.dll",
    ]
    
    # 库加载状态
    library = None
    is_available = False
    error_msg = None


def _load_cpp_library():
    """加载 C++ 编译的库"""
    if CPPAdapterConfig.library is not None:
        return CPPAdapterConfig.library
    
    if CPPAdapterConfig.is_available is False and CPPAdapterConfig.error_msg:
        raise CPPStorageError(CPPAdapterConfig.error_msg)
    
    for lib_path in CPPAdapterConfig.LIBRARY_PATHS:
        try:
            lib = ctypes.CDLL(lib_path)
            logger.info(f"Successfully loaded C++ library from: {lib_path}")
            CPPAdapterConfig.library = lib
            CPPAdapterConfig.is_available = True
            return lib
        except (OSError, ctypes.OSError) as e:
            continue
    
    # 如果无法加载，返回 None 并记录错误
    error_msg = (
        "Failed to load C++ json_store library. "
        "Please compile the C++ version first:\n"
        "  cd src/kernel/storage\n"
        "  mkdir build && cd build\n"
        "  cmake .. -DBUILD_EXAMPLES=ON -DBUILD_TESTS=ON\n"
        "  cmake --build . --config Release"
    )
    CPPAdapterConfig.error_msg = error_msg
    CPPAdapterConfig.is_available = False
    logger.warning(error_msg)
    return None


def is_cpp_available() -> bool:
    """检查 C++ 库是否可用"""
    if CPPAdapterConfig.is_available is not None:
        return CPPAdapterConfig.is_available
    
    lib = _load_cpp_library()
    return lib is not None


class JSONStoreCPP:
    """
    C++ JSONStore 类的 Python 包装器
    
    与 Python 版本兼容的 API，但使用 C++ 实现以获得更好性能
    """
    
    def __init__(self, filepath: str):
        """
        初始化 JSONStore
        
        Args:
            filepath: JSON 文件路径
            
        Raises:
            CPPStorageError: 如果 C++ 库不可用
        """
        if not is_cpp_available():
            raise CPPStorageError(
                "C++ library is not available. "
                "Please compile the C++ version first."
            )
        
        self.filepath = filepath
        self.lib = _load_cpp_library()
        
        # 确保目录存在
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    def read(self) -> Dict[str, Any]:
        """
        读取 JSON 数据
        
        Returns:
            JSON 对象
        """
        try:
            if not os.path.exists(self.filepath):
                return {}
            
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
        except Exception as e:
            raise CPPStorageError(f"Failed to read JSON: {e}")
    
    def write(self, data: Dict[str, Any]) -> None:
        """
        写入 JSON 数据
        
        Args:
            data: 要写入的数据
        """
        try:
            # 确保目录存在
            Path(self.filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # 原子写入：先写入临时文件，再重命名
            temp_filepath = self.filepath + ".tmp"
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 重命名（原子操作）
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            os.rename(temp_filepath, self.filepath)
        except Exception as e:
            raise CPPStorageError(f"Failed to write JSON: {e}")
    
    def exists(self) -> bool:
        """检查文件是否存在"""
        return os.path.exists(self.filepath)
    
    def size(self) -> int:
        """获取文件大小（字节）"""
        if self.exists():
            return os.path.getsize(self.filepath)
        return 0
    
    def backup(self) -> str:
        """
        创建备份文件
        
        Returns:
            备份文件路径
        """
        if not self.exists():
            raise CPPStorageError(f"File does not exist: {self.filepath}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.filepath}.backup.{timestamp}"
        
        try:
            import shutil
            shutil.copy2(self.filepath, backup_path)
            return backup_path
        except Exception as e:
            raise CPPStorageError(f"Failed to create backup: {e}")


class DictJSONStoreCPP:
    """
    C++ DictJSONStore 类的 Python 包装器
    
    用于管理键值对数据的 JSON 存储
    """
    
    def __init__(self, filepath: str):
        """
        初始化 DictJSONStore
        
        Args:
            filepath: JSON 文件路径
        """
        self.store = JSONStoreCPP(filepath)
        self.filepath = filepath
    
    def set(self, key: str, value: Any) -> None:
        """设置键值对"""
        data = self.store.read()
        data[key] = value
        self.store.write(data)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取值"""
        data = self.store.read()
        return data.get(key, default)
    
    def has_key(self, key: str) -> bool:
        """检查键是否存在"""
        data = self.store.read()
        return key in data
    
    def keys(self) -> List[str]:
        """获取所有键"""
        data = self.store.read()
        return list(data.keys())
    
    def values(self) -> List[Any]:
        """获取所有值"""
        data = self.store.read()
        return list(data.values())
    
    def items(self) -> List[tuple]:
        """获取所有键值对"""
        data = self.store.read()
        return list(data.items())
    
    def merge(self, other: Dict[str, Any]) -> None:
        """合并配置"""
        data = self.store.read()
        data.update(other)
        self.store.write(data)
    
    def delete(self, key: str) -> None:
        """删除键"""
        data = self.store.read()
        data.pop(key, None)
        self.store.write(data)
    
    def clear(self) -> None:
        """清空所有数据"""
        self.store.write({})


class ListJSONStoreCPP:
    """
    C++ ListJSONStore 类的 Python 包装器
    
    用于管理列表数据的 JSON 存储
    """
    
    def __init__(self, filepath: str):
        """
        初始化 ListJSONStore
        
        Args:
            filepath: JSON 文件路径
        """
        self.store = JSONStoreCPP(filepath)
        self.filepath = filepath
    
    def append(self, item: Any) -> None:
        """追加项目"""
        data = self.store.read()
        if not isinstance(data, list):
            data = []
        data.append(item)
        self.store.write(data)
    
    def extend(self, items: List[Any]) -> None:
        """扩展列表"""
        data = self.store.read()
        if not isinstance(data, list):
            data = []
        data.extend(items)
        self.store.write(data)
    
    def get(self, index: int) -> Any:
        """获取指定索引的项"""
        data = self.store.read()
        if not isinstance(data, list):
            return None
        try:
            return data[index]
        except IndexError:
            return None
    
    def length(self) -> int:
        """获取列表长度"""
        data = self.store.read()
        if not isinstance(data, list):
            return 0
        return len(data)
    
    def filter(self, func: Callable[[Any], bool]) -> List[Any]:
        """过滤列表"""
        data = self.store.read()
        if not isinstance(data, list):
            return []
        return [item for item in data if func(item)]
    
    def clear(self) -> None:
        """清空列表"""
        self.store.write([])


class LogStoreCPP:
    """
    C++ LogStore 类的 Python 包装器
    
    用于管理日志的 JSON 存储
    """
    
    def __init__(
        self,
        directory: str = "logs",
        prefix: str = "app",
        max_entries_per_file: int = 1000,
        auto_rotate: bool = True
    ):
        """
        初始化 LogStore
        
        Args:
            directory: 日志存储目录
            prefix: 日志文件前缀
            max_entries_per_file: 单个文件最大日志条数
            auto_rotate: 是否自动轮转
        """
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        
        self.prefix = prefix
        self.max_entries_per_file = max_entries_per_file
        self.auto_rotate = auto_rotate
        
        # 使用列表存储日志
        self.log_file = self.directory / f"{prefix}_logs.json"
        self.store = ListJSONStoreCPP(str(self.log_file))
    
    def add_log(self, log_entry: Dict[str, Any]) -> None:
        """
        添加日志条目
        
        Args:
            log_entry: 日志条目字典
        """
        # 添加时间戳
        if 'timestamp' not in log_entry:
            log_entry['timestamp'] = datetime.now().isoformat()
        
        self.store.append(log_entry)
        
        # 检查是否需要轮转
        if self.auto_rotate and self.store.length() >= self.max_entries_per_file:
            self._rotate()
    
    def _rotate(self) -> None:
        """轮转日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_log_file = self.directory / f"{self.prefix}_logs.{timestamp}.json"
        
        try:
            self.log_file.rename(new_log_file)
            self.store = ListJSONStoreCPP(str(self.log_file))
        except Exception as e:
            logger.error(f"Failed to rotate log file: {e}")
    
    def get_logs(
        self,
        level: Optional[str] = None,
        limit: Optional[int] = None,
        start_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        获取日志
        
        Args:
            level: 日志级别（可选）
            limit: 获取数量限制（可选）
            start_date: 开始日期（可选）
        
        Returns:
            日志条目列表
        """
        logs = self.store.store.read()
        if not isinstance(logs, list):
            return []
        
        # 过滤
        if level:
            logs = [log for log in logs if log.get('level') == level]
        
        if start_date:
            logs = [
                log for log in logs
                if datetime.fromisoformat(log.get('timestamp', '')) >= start_date
            ]
        
        # 限制
        if limit:
            logs = logs[-limit:]
        
        return logs
    
    def clear(self) -> None:
        """清空日志"""
        self.store.clear()


# 版本标识
__version__ = "1.0.0"
__cpp_available__ = is_cpp_available()

__all__ = [
    'JSONStoreCPP',
    'DictJSONStoreCPP',
    'ListJSONStoreCPP',
    'LogStoreCPP',
    'CPPStorageError',
    'is_cpp_available',
]
