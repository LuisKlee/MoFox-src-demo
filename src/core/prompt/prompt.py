"""
Prompt基类 - 定义提示词的基本接口和功能
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from .params import PromptParams, PromptTemplate


class PromptType(Enum):
    """提示词类型"""
    SYSTEM = "system"  # 系统提示词
    USER = "user"  # 用户提示词
    ASSISTANT = "assistant"  # 助手提示词
    CUSTOM = "custom"  # 自定义提示词


@dataclass
class PromptMetadata:
    """提示词元数据"""
    name: str  # 提示词名称
    description: Optional[str] = None  # 描述
    version: str = "1.0.0"  # 版本号
    author: Optional[str] = None  # 作者
    tags: List[str] = field(default_factory=list)  # 标签
    created_at: Optional[str] = None  # 创建时间
    updated_at: Optional[str] = None  # 更新时间


class PromptBase(ABC):
    """提示词基类"""
    
    def __init__(
        self,
        name: str,
        prompt_type: PromptType = PromptType.CUSTOM,
        metadata: Optional[PromptMetadata] = None
    ):
        """
        初始化Prompt基类
        
        Args:
            name: 提示词名称
            prompt_type: 提示词类型
            metadata: 元数据
        """
        self.name = name
        self.prompt_type = prompt_type
        self.metadata = metadata or PromptMetadata(name=name)
        self.params = PromptParams()
        self._template = None
    
    @property
    def template(self) -> Optional[PromptTemplate]:
        """获取模板"""
        return self._template
    
    @template.setter
    def template(self, value: Union[str, PromptTemplate]) -> None:
        """设置模板"""
        if isinstance(value, str):
            self._template = PromptTemplate(value)
        else:
            self._template = value
    
    @abstractmethod
    def render(self, **kwargs) -> str:
        """
        渲染提示词
        
        Args:
            **kwargs: 动态参数
            
        Returns:
            渲染后的提示词文本
        """
    
    @abstractmethod
    def validate(self) -> bool:
        """验证提示词"""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "type": self.prompt_type.value,
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "version": self.metadata.version,
                "author": self.metadata.author,
                "tags": self.metadata.tags,
            }
        }


class SimplePrompt(PromptBase):
    """简单提示词 - 无参数的静态提示词"""
    
    def __init__(
        self,
        name: str,
        content: str,
        prompt_type: PromptType = PromptType.CUSTOM,
        metadata: Optional[PromptMetadata] = None
    ):
        """
        初始化简单提示词
        
        Args:
            name: 提示词名称
            content: 提示词内容
            prompt_type: 提示词类型
            metadata: 元数据
        """
        super().__init__(name, prompt_type, metadata)
        self.content = content
    
    def render(self, **kwargs) -> str:
        """直接返回内容，忽略参数"""
        return self.content
    
    def validate(self) -> bool:
        """验证提示词"""
        return bool(self.content)


class TemplatePrompt(PromptBase):
    """模板提示词 - 支持参数的动态提示词"""
    
    def __init__(
        self,
        name: str,
        template: Union[str, PromptTemplate],
        prompt_type: PromptType = PromptType.CUSTOM,
        metadata: Optional[PromptMetadata] = None
    ):
        """
        初始化模板提示词
        
        Args:
            name: 提示词名称
            template: 模板字符串或PromptTemplate对象
            prompt_type: 提示词类型
            metadata: 元数据
        """
        super().__init__(name, prompt_type, metadata)
        self.template = template
    
    def render(self, **kwargs) -> str:
        """使用参数渲染模板"""
        if not self._template:
            return ""
        
        return self._template.render(kwargs)
    
    def validate(self) -> bool:
        """验证提示词"""
        if not self._template:
            return False
        
        # 检查所有参数是否都有默认值或被提供
        missing = []
        for param_name in self._template.get_param_names():
            if param_name not in self.params.params:
                missing.append(param_name)
        
        return len(missing) == 0


class ChainedPrompt(PromptBase):
    """链式提示词 - 由多个提示词组成的复合提示词"""
    
    def __init__(
        self,
        name: str,
        prompts: List[PromptBase],
        separator: str = "\n",
        prompt_type: PromptType = PromptType.CUSTOM,
        metadata: Optional[PromptMetadata] = None
    ):
        """
        初始化链式提示词
        
        Args:
            name: 提示词名称
            prompts: 提示词列表
            separator: 提示词之间的分隔符
            prompt_type: 提示词类型
            metadata: 元数据
        """
        super().__init__(name, prompt_type, metadata)
        self.prompts = prompts
        self.separator = separator
    
    def render(self, **kwargs) -> str:
        """依次渲染所有提示词并连接"""
        results = []
        for prompt in self.prompts:
            try:
                result = prompt.render(**kwargs)
                if result:
                    results.append(result)
            except (ValueError, TypeError, KeyError):
                pass
        
        return self.separator.join(results)
    
    def validate(self) -> bool:
        """验证所有子提示词"""
        return all(prompt.validate() for prompt in self.prompts)
    
    def add_prompt(self, prompt: PromptBase) -> None:
        """添加提示词"""
        self.prompts.append(prompt)
    
    def remove_prompt(self, name: str) -> bool:
        """移除提示词"""
        initial_length = len(self.prompts)
        self.prompts = [p for p in self.prompts if p.name != name]
        return len(self.prompts) < initial_length

