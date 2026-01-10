"""
提示词管理系统导出模块
"""
from typing import Optional
from .params import (
    ParamType,
    PromptParam,
    PromptParams,
    PromptTemplate,
)

from .prompt import (
    PromptType,
    PromptMetadata,
    PromptBase,
    SimplePrompt,
    TemplatePrompt,
    ChainedPrompt,
)

from .manager import (
    PromptPriority,
    PromptCategory,
    PromptManager,
)

# 创建全局管理器实例
_manager_instance = PromptManager()

# 导出便捷函数
def get_manager() -> PromptManager:
    """获取全局PromptManager实例"""
    return _manager_instance

def register(
    prompt: PromptBase,
    category: PromptCategory = PromptCategory.CUSTOM,
    priority: PromptPriority = PromptPriority.NORMAL
) -> bool:
    """注册提示词"""
    return _manager_instance.register(prompt, category, priority)

def unregister(name: str) -> bool:
    """移除提示词"""
    return _manager_instance.unregister(name)

def get(name: str) -> Optional[PromptBase]:
    """获取提示词"""
    return _manager_instance.get(name)

def render(name: str, **kwargs) -> Optional[str]:
    """渲染提示词"""
    return _manager_instance.render(name, **kwargs)

def render_multiple(names: list, **kwargs) -> dict:
    """渲染多个提示词"""
    return _manager_instance.render_multiple(names, **kwargs)

def list_all() -> dict:
    """列出所有提示词"""
    return _manager_instance.get_all()

def list_names() -> list:
    """列出所有提示词名称"""
    return _manager_instance.list_names()

# LLM 便捷函数
async def llm_generate(*args, **kwargs):
    """渲染提示词并调用 LLM（非流式）"""
    return await _manager_instance.llm_generate(*args, **kwargs)


async def llm_stream_generate(*args, **kwargs):
    """渲染提示词并以流式方式调用 LLM"""
    async for chunk in _manager_instance.llm_stream_generate(*args, **kwargs):
        yield chunk

# 导出所有公开类和函数
__all__ = [
    # 参数系统
    "ParamType",
    "PromptParam",
    "PromptParams",
    "PromptTemplate",
    # Prompt基类
    "PromptType",
    "PromptMetadata",
    "PromptBase",
    "SimplePrompt",
    "TemplatePrompt",
    "ChainedPrompt",
    # 管理器
    "PromptPriority",
    "PromptCategory",
    "PromptManager",
    # 便捷函数
    "get_manager",
    "register",
    "unregister",
    "get",
    "render",
    "render_multiple",
    "list_all",
    "list_names",
    "llm_generate",
    "llm_stream_generate",
]
