"""
MoFox Core API - Core层对外暴露接口

这个模块封装了 core 层的所有核心功能，提供统一、简洁的 API 接口。
包括：
- 组件系统 (components)
- 模型系统 (models)
- 感知系统 (perception)
- 提示词系统 (prompt)
- 传输系统 (transport)

作者: MoFox Team
日期: 2026-01-11
"""

from typing import Any, Dict, List, Optional, Union, Callable, AsyncIterator
from pathlib import Path
from datetime import datetime
import asyncio

# ==================== 组件系统 (Components) ====================
# TODO: 根据实际的 components 模块导入相应的类和函数
try:
    from core.components import *
except ImportError:
    pass

# ==================== 模型系统 (Models) ====================
# TODO: 根据实际的 models 模块导入相应的类和函数
try:
    from core.models import *
except ImportError:
    pass

# ==================== 感知系统 (Perception) ====================
# TODO: 根据实际的 perception 模块导入相应的类和函数
try:
    from core.perception import *
except ImportError:
    pass

# ==================== 提示词系统 (Prompt) ====================
try:
    from core.prompt import (
        PromptTemplate,
        PromptBuilder,
        PromptManager,
        PromptRegistry,
    )
except ImportError:
    pass

# ==================== 传输系统 (Transport) ====================
try:
    from core.transport import (
        Transport,
        TransportManager,
        TransportConfig,
    )
except ImportError:
    pass


# ==================== Core 统一管理器 ====================
class MoFoxCore:
    """
    MoFox Core 统一管理器
    
    提供所有 core 层功能的统一访问入口，管理核心组件实例。
    
    示例:
        >>> core = MoFoxCore(app_name="my_app")
        >>> await core.initialize()
        >>> 
        >>> # 使用提示词系统
        >>> prompt = await core.prompt.build("greeting", name="User")
        >>> 
        >>> # 使用传输系统
        >>> response = await core.transport.send(data)
        >>> 
        >>> # 使用感知系统
        >>> perception_result = await core.perception.process(input_data)
    """
    
    def __init__(
        self,
        app_name: str = "mofox_app",
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        初始化 MoFox Core
        
        Args:
            app_name: 应用名称
            config: 配置字典
            **kwargs: 其他配置参数
        """
        self.app_name = app_name
        self.config = config or {}
        self.extra_config = kwargs
        
        # 各模块管理器
        self._prompt_manager = None
        self._transport_manager = None
        self._perception_system = None
        self._component_registry = None
        self._model_manager = None
        
        self._initialized = False
    
    async def initialize(self):
        """初始化所有核心组件"""
        if self._initialized:
            return
        
        # 1. 初始化提示词系统
        await self._init_prompt_system()
        
        # 2. 初始化传输系统
        await self._init_transport_system()
        
        # 3. 初始化感知系统
        await self._init_perception_system()
        
        # 4. 初始化组件系统
        await self._init_component_system()
        
        # 5. 初始化模型系统
        await self._init_model_system()
        
        self._initialized = True
    
    async def _init_prompt_system(self):
        """初始化提示词系统"""
        try:
            self._prompt_manager = PromptManager()
            # TODO: 加载默认提示词模板
        except Exception as e:
            print(f"警告: 提示词系统初始化失败: {e}")
    
    async def _init_transport_system(self):
        """初始化传输系统"""
        try:
            transport_config = self.config.get("transport", {})
            self._transport_manager = TransportManager(config=transport_config)
        except Exception as e:
            print(f"警告: 传输系统初始化失败: {e}")
    
    async def _init_perception_system(self):
        """初始化感知系统"""
        try:
            # TODO: 根据实际的 perception 模块进行初始化
            pass
        except Exception as e:
            print(f"警告: 感知系统初始化失败: {e}")
    
    async def _init_component_system(self):
        """初始化组件系统"""
        try:
            # TODO: 根据实际的 components 模块进行初始化
            pass
        except Exception as e:
            print(f"警告: 组件系统初始化失败: {e}")
    
    async def _init_model_system(self):
        """初始化模型系统"""
        try:
            # TODO: 根据实际的 models 模块进行初始化
            pass
        except Exception as e:
            print(f"警告: 模型系统初始化失败: {e}")
    
    @property
    def prompt(self):
        """获取提示词管理器"""
        return self._prompt_manager
    
    @property
    def transport(self):
        """获取传输管理器"""
        return self._transport_manager
    
    @property
    def perception(self):
        """获取感知系统"""
        return self._perception_system
    
    @property
    def components(self):
        """获取组件注册表"""
        return self._component_registry
    
    @property
    def models(self):
        """获取模型管理器"""
        return self._model_manager
    
    async def shutdown(self):
        """关闭所有核心组件"""
        if not self._initialized:
            return
        
        # 关闭传输系统
        if self._transport_manager:
            try:
                await self._transport_manager.close()
            except Exception as e:
                print(f"关闭传输系统失败: {e}")
        
        # 关闭其他系统
        # TODO: 添加其他系统的关闭逻辑
        
        self._initialized = False
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.shutdown()


# ==================== 便捷函数 ====================

# 全局单例
_core_instance: Optional[MoFoxCore] = None


def get_core(app_name: str = "mofox_app", **kwargs) -> MoFoxCore:
    """
    获取全局 Core 实例（单例模式）
    
    Args:
        app_name: 应用名称
        **kwargs: 其他配置参数
        
    Returns:
        MoFoxCore 实例
    """
    global _core_instance
    if _core_instance is None:
        _core_instance = MoFoxCore(app_name=app_name, **kwargs)
    return _core_instance


async def create_core(app_name: str = "mofox_app", **kwargs) -> MoFoxCore:
    """
    创建并初始化 Core 实例
    
    Args:
        app_name: 应用名称
        **kwargs: 其他配置参数
        
    Returns:
        已初始化的 MoFoxCore 实例
    """
    core = MoFoxCore(app_name=app_name, **kwargs)
    await core.initialize()
    return core


# ==================== 提示词系统便捷函数 ====================

async def build_prompt(template_name: str, **kwargs) -> str:
    """
    构建提示词
    
    Args:
        template_name: 模板名称
        **kwargs: 模板参数
        
    Returns:
        构建好的提示词字符串
    """
    core = get_core()
    if not core._initialized:
        await core.initialize()
    return await core.prompt.build(template_name, **kwargs)


# ==================== 传输系统便捷函数 ====================

async def send_data(data: Any, transport_type: str = "default", **kwargs) -> Any:
    """
    发送数据
    
    Args:
        data: 要发送的数据
        transport_type: 传输类型
        **kwargs: 其他参数
        
    Returns:
        传输结果
    """
    core = get_core()
    if not core._initialized:
        await core.initialize()
    return await core.transport.send(data, transport_type=transport_type, **kwargs)


# ==================== 导出所有公共接口 ====================

__all__ = [
    # 主要类
    "MoFoxCore",
    
    # 便捷函数
    "get_core",
    "create_core",
    "build_prompt",
    "send_data",
]
