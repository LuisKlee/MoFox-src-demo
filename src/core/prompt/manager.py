"""
全局Prompt管理器 - 管理、存储、检索和生命周期控制所有提示词
"""
from typing import Any, Dict, List, Optional, Callable, AsyncIterator, TYPE_CHECKING
from enum import Enum
import logging
from .prompt import PromptBase

if TYPE_CHECKING:
    from kernel.llm import (
        LLMRequest,
        LLMRequestManager,
        LLMResponse,
        StreamChunk,
    )


logger = logging.getLogger(__name__)


class PromptPriority(Enum):
    """提示词优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class PromptCategory(Enum):
    """提示词分类"""
    SYSTEM = "system"  # 系统级提示词
    DOMAIN = "domain"  # 领域相关提示词
    DIALOG = "dialog"  # 对话相关提示词
    TASK = "task"  # 任务相关提示词
    CUSTOM = "custom"  # 自定义提示词


class PromptManager:
    """全局提示词管理器 - 单例模式"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """实现单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化提示词管理器"""
        if not PromptManager._initialized:
            self._prompts: Dict[str, PromptBase] = {}  # 名称 -> 提示词
            self._categories: Dict[str, List[str]] = {}  # 分类 -> 名称列表
            self._priorities: Dict[str, PromptPriority] = {}  # 名称 -> 优先级
            self._templates: Dict[str, str] = {}  # 模板ID -> 模板文本
            self._interceptors: List[Callable] = []  # 渲染拦截器
            self._hooks: Dict[str, List[Callable]] = {  # 生命周期钩子
                "before_register": [],
                "after_register": [],
                "before_render": [],
                "after_render": [],
                "before_remove": [],
                "after_remove": [],
            }
            # LLM 请求管理器（延迟导入以避免路径问题）
            self._llm_module = self._load_llm_module()
            self._llm_manager = self._llm_module.get_manager()
            PromptManager._initialized = True
            logger.info("PromptManager initialized")
    
    # ==================== 注册和移除 ====================
    
    def register(
        self,
        prompt: PromptBase,
        category: PromptCategory = PromptCategory.CUSTOM,
        priority: PromptPriority = PromptPriority.NORMAL
    ) -> bool:
        """
        注册提示词
        
        Args:
            prompt: 提示词对象
            category: 分类
            priority: 优先级
            
        Returns:
            是否注册成功
        """
        # 执行前置钩子
        for hook in self._hooks["before_register"]:
            try:
                hook(prompt)
            except (ValueError, TypeError, RuntimeError) as e:
                logger.warning("Hook error: %s", e)
        
        # 检查名称是否已存在
        if prompt.name in self._prompts:
            logger.warning("Prompt '%s' already exists", prompt.name)
            return False
        
        # 验证提示词
        if not prompt.validate():
            logger.error("Prompt '%s' validation failed", prompt.name)
            return False
        
        # 注册提示词
        self._prompts[prompt.name] = prompt
        self._priorities[prompt.name] = priority
        
        # 添加到分类
        category_name = category.value
        if category_name not in self._categories:
            self._categories[category_name] = []
        self._categories[category_name].append(prompt.name)
        
        # 执行后置钩子
        for hook in self._hooks["after_register"]:
            try:
                hook(prompt)
            except (ValueError, TypeError, RuntimeError) as e:
                logger.warning("Hook error: %s", e)
        
        logger.info("Prompt '%s' registered successfully", prompt.name)
        return True
    
    def unregister(self, name: str) -> bool:
        """
        移除提示词
        
        Args:
            name: 提示词名称
            
        Returns:
            是否移除成功
        """
        if name not in self._prompts:
            logger.warning("Prompt '%s' not found", name)
            return False
        
        prompt = self._prompts[name]
        
        # 执行前置钩子
        for hook in self._hooks["before_remove"]:
            try:
                hook(prompt)
            except (ValueError, TypeError, RuntimeError) as e:
                logger.warning("Hook error: %s", e)
        
        # 从类别中移除
        for names in self._categories.values():
            if name in names:
                names.remove(name)
        
        # 移除优先级记录
        del self._priorities[name]
        
        # 移除提示词
        del self._prompts[name]
        
        # 执行后置钩子
        for hook in self._hooks["after_remove"]:
            try:
                hook(prompt)
            except (ValueError, TypeError, RuntimeError) as e:
                logger.warning("Hook error: %s", e)
        
        logger.info("Prompt '%s' unregistered successfully", name)
        return True
    
    # ==================== 获取提示词 ====================
    
    def get(self, name: str) -> Optional[PromptBase]:
        """获取提示词"""
        return self._prompts.get(name)
    
    def get_by_category(self, category: PromptCategory) -> List[PromptBase]:
        """按分类获取提示词"""
        category_name = category.value
        names = self._categories.get(category_name, [])
        return [self._prompts[name] for name in names if name in self._prompts]
    
    def get_by_priority(self, priority: PromptPriority) -> List[PromptBase]:
        """按优先级获取提示词"""
        names = [
            name for name, p in self._priorities.items()
            if p == priority and name in self._prompts
        ]
        return [self._prompts[name] for name in names]
    
    def get_all(self) -> Dict[str, PromptBase]:
        """获取所有提示词"""
        return self._prompts.copy()
    
    def list_names(self) -> List[str]:
        """列出所有提示词名称"""
        return list(self._prompts.keys())
    
    # ==================== 渲染 ====================
    
    def render(self, name: str, **kwargs) -> Optional[str]:
        """
        渲染提示词
        
        Args:
            name: 提示词名称
            **kwargs: 渲染参数
            
        Returns:
            渲染后的文本，如果不存在则返回None
        """
        prompt = self.get(name)
        if not prompt:
            logger.error("Prompt '%s' not found", name)
            return None
        
        # 执行前置钩子
        for hook in self._hooks["before_render"]:
            try:
                hook(prompt, kwargs)
            except (ValueError, TypeError, RuntimeError) as e:
                logger.warning("Hook error: %s", e)
        
        try:
            # 渲染提示词
            result = prompt.render(**kwargs)
            
            # 应用拦截器
            for interceptor in self._interceptors:
                result = interceptor(result, name, prompt)
            
            # 执行后置钩子
            for hook in self._hooks["after_render"]:
                try:
                    hook(prompt, result)
                except (ValueError, TypeError, RuntimeError) as e:
                    logger.warning("Hook error: %s", e)
            
            return result
        except (ValueError, TypeError, KeyError, RuntimeError) as e:
            logger.error("Error rendering prompt '%s': %s", name, e)
            return None
    
    def render_multiple(self, names: List[str], **kwargs) -> Dict[str, str]:
        """
        渲染多个提示词
        
        Args:
            names: 提示词名称列表
            **kwargs: 渲染参数
            
        Returns:
            名称 -> 渲染结果的字典
        """
        results = {}
        for name in names:
            result = self.render(name, **kwargs)
            if result:
                results[name] = result
        return results
    
    # ==================== 拦截器和钩子 ====================
    
    def add_interceptor(self, interceptor: Callable[[str, str, PromptBase], str]) -> None:
        """
        添加渲染拦截器
        
        Args:
            interceptor: 拦截器函数，签名为 (rendered_text, name, prompt) -> str
        """
        self._interceptors.append(interceptor)
    
    def remove_interceptor(self, interceptor: Callable) -> bool:
        """移除拦截器"""
        try:
            self._interceptors.remove(interceptor)
            return True
        except ValueError:
            return False
    
    def add_hook(self, event: str, hook: Callable) -> bool:
        """
        添加生命周期钩子
        
        Args:
            event: 事件名称
            hook: 钩子函数
            
        Returns:
            是否添加成功
        """
        if event not in self._hooks:
            logger.warning("Unknown event: %s", event)
            return False
        
        self._hooks[event].append(hook)
        return True
    
    def remove_hook(self, event: str, hook: Callable) -> bool:
        """移除钩子"""
        if event not in self._hooks:
            return False
        
        try:
            self._hooks[event].remove(hook)
            return True
        except ValueError:
            return False
    
    # ==================== 模板管理 ====================
    
    def register_template(self, template_id: str, template_text: str) -> bool:
        """注册模板"""
        if template_id in self._templates:
            logger.warning("Template '%s' already exists", template_id)
            return False
        
        self._templates[template_id] = template_text
        logger.info("Template '%s' registered", template_id)
        return True
    
    def get_template(self, template_id: str) -> Optional[str]:
        """获取模板"""
        return self._templates.get(template_id)
    
    def update_template(self, template_id: str, template_text: str) -> bool:
        """更新模板"""
        if template_id not in self._templates:
            logger.warning("Template '%s' not found", template_id)
            return False
        
        self._templates[template_id] = template_text
        logger.info("Template '%s' updated", template_id)
        return True
    
    def remove_template(self, template_id: str) -> bool:
        """移除模板"""
        if template_id not in self._templates:
            return False
        
        del self._templates[template_id]
        logger.info("Template '%s' removed", template_id)
        return True
    
    # ==================== 工具方法 ====================
    
    def exists(self, name: str) -> bool:
        """检查提示词是否存在"""
        return name in self._prompts
    
    def count(self) -> int:
        """获取提示词总数"""
        return len(self._prompts)
    
    def clear(self) -> None:
        """清空所有提示词"""
        self._prompts.clear()
        self._categories.clear()
        self._priorities.clear()
        logger.info("All prompts cleared")
    
    def reset(self) -> None:
        """重置管理器（清空所有数据和配置）"""
        self.clear()
        self._templates.clear()
        self._interceptors.clear()
        for hooks in self._hooks.values():
            hooks.clear()
        PromptManager._initialized = False
        logger.info("PromptManager reset")

    def _load_llm_module(self):
        """延迟加载 kernel.llm 模块"""
        import importlib

        module = importlib.import_module("kernel.llm")
        self._llm_module = module
        return module
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_prompts": len(self._prompts),
            "categories": {
                cat: len(names) for cat, names in self._categories.items()
            },
            "templates": len(self._templates),
            "interceptors": len(self._interceptors),
        }

    # ==================== LLM 联动 ====================

    async def llm_generate(
        self,
        name: str,
        model: str,
        provider: Optional[str] = None,
        *,
        role: str = "user",
        base_messages: Optional[List[Dict[str, Any]]] = None,
        prompt_vars: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[Any] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Any] = None,
        response_format: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        seed: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional["LLMResponse"]:
        """
        渲染指定提示词并调用 LLM（非流式）

        Args:
            name: 提示词名称
            model: 模型名称
            provider: 提供商名称
            role: 渲染后注入消息的角色（system/user/assistant）
            base_messages: 预置消息列表，会在渲染结果前追加
            prompt_vars: 渲染提示词所需的参数
            temperature, max_tokens, top_p, frequency_penalty, presence_penalty, stop: 生成参数
            tools, tool_choice: 工具调用相关配置
            response_format: 响应格式（如 JSON mode）
            user: 用户标识
            seed: 随机种子
            metadata: 附加元数据

        Returns:
            LLMResponse 或 None（渲染失败时）
        """
        rendered = self.render(name, **(prompt_vars or {}))
        if not rendered:
            logger.error("Prompt '%s' render failed", name)
            return None

        messages = list(base_messages) if base_messages else []
        messages.append({"role": role, "content": rendered})

        llm_module = getattr(self, "_llm_module", None) or self._load_llm_module()
        LLMRequest = llm_module.LLMRequest

        request = LLMRequest(
            model=model,
            messages=messages,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
            user=user,
            seed=seed,
            metadata=metadata or {},
        )

        if tools:
            return await self._llm_manager.generate_with_tools(request)

        return await self._llm_manager.generate(request)

    async def llm_stream_generate(
        self,
        name: str,
        model: str,
        provider: Optional[str] = None,
        *,
        role: str = "user",
        base_messages: Optional[List[Dict[str, Any]]] = None,
        prompt_vars: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[Any] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Any] = None,
        response_format: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        seed: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator["StreamChunk"]:
        """
        渲染提示词并以流式方式调用 LLM
        """
        rendered = self.render(name, **(prompt_vars or {}))
        if not rendered:
            logger.error("Prompt '%s' render failed", name)
            return

        messages = list(base_messages) if base_messages else []
        messages.append({"role": role, "content": rendered})

        llm_module = getattr(self, "_llm_module", None) or self._load_llm_module()
        LLMRequest = llm_module.LLMRequest

        request = LLMRequest(
            model=model,
            messages=messages,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
            user=user,
            seed=seed,
            metadata=metadata or {},
            stream=True,
        )

        async for chunk in self._llm_manager.stream_generate(request):
            yield chunk
