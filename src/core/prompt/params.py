"""
Prompt参数系统 - 管理Prompt中的动态参数、变量和模板
"""
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import re


class ParamType(Enum):
    """参数类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    ANY = "any"


@dataclass
class PromptParam:
    """单个提示词参数定义"""
    name: str  # 参数名称
    param_type: ParamType = ParamType.STRING  # 参数类型
    required: bool = True  # 是否必需
    default: Optional[Any] = None  # 默认值
    description: Optional[str] = None  # 参数描述
    validator: Optional[Callable[[Any], bool]] = None  # 验证函数
    
    def validate(self, value: Any) -> bool:
        """验证参数值"""
        if value is None:
            return not self.required
        
        # 类型检查
        if self.param_type == ParamType.STRING and not isinstance(value, str):
            return False
        elif self.param_type == ParamType.INTEGER and not isinstance(value, int):
            return False
        elif self.param_type == ParamType.FLOAT and not isinstance(value, (int, float)):
            return False
        elif self.param_type == ParamType.BOOLEAN and not isinstance(value, bool):
            return False
        elif self.param_type == ParamType.LIST and not isinstance(value, list):
            return False
        elif self.param_type == ParamType.DICT and not isinstance(value, dict):
            return False
        
        # 自定义验证
        if self.validator and not self.validator(value):
            return False
        
        return True


@dataclass
class PromptParams:
    """提示词参数集合管理"""
    params: Dict[str, PromptParam] = field(default_factory=dict)
    values: Dict[str, Any] = field(default_factory=dict)
    
    def add_param(self, param: PromptParam) -> None:
        """添加参数定义"""
        self.params[param.name] = param
    
    def add_params(self, params: List[PromptParam]) -> None:
        """批量添加参数定义"""
        for param in params:
            self.add_param(param)
    
    def set_value(self, name: str, value: Any) -> bool:
        """设置参数值"""
        if name not in self.params:
            return False
        
        param = self.params[name]
        if not param.validate(value):
            return False
        
        self.values[name] = value
        return True
    
    def set_values(self, values: Dict[str, Any]) -> bool:
        """批量设置参数值"""
        for name, value in values.items():
            if not self.set_value(name, value):
                return False
        return True
    
    def get_value(self, name: str, default: Optional[Any] = None) -> Any:
        """获取参数值"""
        if name in self.values:
            return self.values[name]
        
        if name in self.params:
            param = self.params[name]
            if param.default is not None:
                return param.default
        
        return default
    
    def get_all_values(self) -> Dict[str, Any]:
        """获取所有参数值"""
        result = {}
        for name, param in self.params.items():
            if name in self.values:
                result[name] = self.values[name]
            elif param.default is not None:
                result[name] = param.default
        return result
    
    def validate_all(self) -> bool:
        """验证所有必需参数是否已设置"""
        for name, param in self.params.items():
            if param.required:
                if name not in self.values and param.default is None:
                    return False
        return True
    
    def get_missing_params(self) -> List[str]:
        """获取缺失的必需参数列表"""
        missing = []
        for name, param in self.params.items():
            if param.required:
                if name not in self.values and param.default is None:
                    missing.append(name)
        return missing


class PromptTemplate:
    """提示词模板 - 支持变量插值和动态内容"""
    
    def __init__(self, template: str):
        """
        初始化模板
        
        Args:
            template: 模板字符串，使用 {param_name} 格式表示参数
        """
        self.template = template
        self._param_names = self._extract_param_names()
    
    def _extract_param_names(self) -> List[str]:
        """提取模板中的所有参数名"""
        pattern = r'\{(\w+)\}'
        matches = re.findall(pattern, self.template)
        return list(set(matches))  # 去重
    
    def get_param_names(self) -> List[str]:
        """获取模板中的参数名列表"""
        return self._param_names
    
    def render(self, params: Dict[str, Any]) -> str:
        """
        使用参数渲染模板
        
        Args:
            params: 参数字典
            
        Returns:
            渲染后的字符串
        """
        result = self.template
        for param_name in self._param_names:
            if param_name in params:
                value = params[param_name]
                result = result.replace(f"{{{param_name}}}", str(value))
        return result
    
    def render_with_defaults(self, params: Dict[str, Any], defaults: Dict[str, Any]) -> str:
        """
        使用参数和默认值渲染模板
        
        Args:
            params: 参数字典
            defaults: 默认值字典
            
        Returns:
            渲染后的字符串
        """
        merged = {**defaults, **params}
        return self.render(merged)
