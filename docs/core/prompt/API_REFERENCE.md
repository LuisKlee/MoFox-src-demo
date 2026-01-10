# 提示词管理系统 - API 参考

## 目录

- [参数系统](#参数系统)
- [Prompt 基类](#prompt-基类)
- [Prompt 实现](#prompt-实现)
- [全局管理器](#全局管理器)
- [便捷 API](#便捷-api)
- [LLM 联动](#llm-联动)
- [异常和错误](#异常和错误)

---

## 参数系统

### ParamType (枚举)

提示词参数的类型定义。

**成员:**

```python
class ParamType(Enum):
    STRING = "string"      # 字符串类型
    INTEGER = "integer"    # 整数类型
    FLOAT = "float"        # 浮点数类型
    BOOLEAN = "boolean"    # 布尔类型
    LIST = "list"          # 列表类型
    DICT = "dict"          # 字典类型
    ANY = "any"            # 任意类型
```

**示例:**

```python
from src.core.prompt import ParamType

param_type = ParamType.STRING
```

---

### PromptParam (数据类)

单个提示词参数定义，包含类型、验证等信息。

**属性:**

| 属性 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | `str` | ✓ | 参数名称 |
| `param_type` | `ParamType` | | 参数类型，默认 `STRING` |
| `required` | `bool` | | 是否必需，默认 `True` |
| `default` | `Any` | | 默认值，默认 `None` |
| `description` | `Optional[str]` | | 参数描述 |
| `validator` | `Optional[Callable]` | | 自定义验证函数 |

**方法:**

```python
def validate(self, value: Any) -> bool:
    """
    验证参数值
    
    Args:
        value: 要验证的值
        
    Returns:
        bool: 验证是否通过
    """
```

**示例:**

```python
from src.core.prompt import PromptParam, ParamType

# 基础参数
param = PromptParam(
    name="user_id",
    param_type=ParamType.INTEGER,
    required=True,
    description="用户ID"
)

# 带验证器的参数
def validate_email(value):
    return "@" in value

email_param = PromptParam(
    name="email",
    param_type=ParamType.STRING,
    required=True,
    validator=validate_email,
    description="用户邮箱"
)

# 验证
is_valid = email_param.validate("user@example.com")  # True
is_valid = email_param.validate("invalid")           # False
```

---

### PromptParams (类)

提示词参数集合管理器，用于管理一组相关参数的定义和值。

**属性:**

| 属性 | 类型 | 说明 |
|------|------|------|
| `params` | `Dict[str, PromptParam]` | 参数定义字典 |
| `values` | `Dict[str, Any]` | 参数值字典 |

**方法:**

```python
def add_param(self, param: PromptParam) -> None:
    """添加单个参数定义"""

def add_params(self, params: List[PromptParam]) -> None:
    """批量添加参数定义"""

def set_value(self, name: str, value: Any) -> bool:
    """
    设置参数值（会进行类型和自定义验证）
    
    Args:
        name: 参数名
        value: 参数值
        
    Returns:
        bool: 是否设置成功
    """

def set_values(self, values: Dict[str, Any]) -> bool:
    """批量设置参数值"""

def get_value(self, name: str, default: Optional[Any] = None) -> Any:
    """
    获取参数值
    
    返回顺序: 已设置值 > 默认值 > default 参数
    """

def get_all_values(self) -> Dict[str, Any]:
    """获取所有参数值（包含默认值）"""

def validate_all(self) -> bool:
    """验证所有必需参数是否已设置"""

def get_missing_params(self) -> List[str]:
    """获取缺失的必需参数列表"""
```

**示例:**

```python
from src.core.prompt import PromptParams, PromptParam, ParamType

params = PromptParams()

# 添加参数定义
params.add_params([
    PromptParam("name", ParamType.STRING, required=True),
    PromptParam("age", ParamType.INTEGER, required=False, default=0),
])

# 设置参数值
params.set_value("name", "Alice")  # True
params.set_value("age", 25)         # True

# 获取参数值
name = params.get_value("name")     # "Alice"
age = params.get_value("age")       # 25
missing = params.get_value("city", "Unknown")  # "Unknown"

# 验证
is_valid = params.validate_all()    # True

# 获取所有值
all_values = params.get_all_values()
# {"name": "Alice", "age": 25}
```

---

### PromptTemplate (类)

提示词模板引擎，支持 `{param_name}` 格式的变量插值。

**属性:**

| 属性 | 类型 | 说明 |
|------|------|------|
| `template` | `str` | 模板字符串 |

**方法:**

```python
def __init__(self, template: str):
    """初始化模板"""

def get_param_names(self) -> List[str]:
    """获取模板中的参数名列表"""

def render(self, params: Dict[str, Any]) -> str:
    """
    使用参数渲染模板
    
    Args:
        params: 参数字典，必须包含模板中的所有参数
        
    Returns:
        str: 渲染后的字符串
    """

def render_with_defaults(self, params: Dict[str, Any], 
                        defaults: Dict[str, Any]) -> str:
    """
    使用参数和默认值渲染模板
    
    Args:
        params: 参数字典（覆盖默认值）
        defaults: 默认值字典
        
    Returns:
        str: 渲染后的字符串
    """
```

**示例:**

```python
from src.core.prompt import PromptTemplate

template = PromptTemplate("Welcome {name}! Your order #{order_id} is ready.")

# 获取参数名
names = template.get_param_names()  # ['name', 'order_id']

# 渲染
result = template.render({
    "name": "Alice",
    "order_id": "12345"
})
# Output: "Welcome Alice! Your order #12345 is ready."

# 使用默认值
result = template.render_with_defaults(
    {"name": "Bob"},
    {"order_id": "99999"}
)
# Output: "Welcome Bob! Your order #99999 is ready."
```

---

## Prompt 基类

### PromptType (枚举)

提示词的类型分类。

**成员:**

```python
class PromptType(Enum):
    SYSTEM = "system"         # 系统提示词
    USER = "user"             # 用户提示词
    ASSISTANT = "assistant"   # 助手提示词
    CUSTOM = "custom"         # 自定义提示词
```

---

### PromptMetadata (数据类)

提示词的元数据，包含描述性信息。

**属性:**

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 提示词名称 |
| `description` | `Optional[str]` | 描述 |
| `version` | `str` | 版本号，默认 "1.0.0" |
| `author` | `Optional[str]` | 作者 |
| `tags` | `List[str]` | 标签列表 |
| `created_at` | `Optional[str]` | 创建时间 |
| `updated_at` | `Optional[str]` | 更新时间 |

---

### PromptBase (抽象基类)

所有提示词的基类，定义了接口和通用功能。

**属性:**

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 提示词名称 |
| `prompt_type` | `PromptType` | 提示词类型 |
| `metadata` | `PromptMetadata` | 元数据 |
| `params` | `PromptParams` | 参数集合 |

**方法:**

```python
@abstractmethod
def render(self, **kwargs) -> str:
    """
    渲染提示词
    
    Args:
        **kwargs: 动态参数
        
    Returns:
        str: 渲染后的文本
    """

@abstractmethod
def validate(self) -> bool:
    """验证提示词是否有效"""

def to_dict(self) -> Dict[str, Any]:
    """转换为字典表示"""
```

**属性访问器:**

```python
@property
def template(self) -> Optional[PromptTemplate]:
    """获取模板对象"""

@template.setter
def template(self, value: Union[str, PromptTemplate]) -> None:
    """设置模板（支持字符串或 PromptTemplate 对象）"""
```

---

## Prompt 实现

### SimplePrompt (类)

静态、无参数的提示词。

```python
class SimplePrompt(PromptBase):
    def __init__(
        self,
        name: str,
        content: str,
        prompt_type: PromptType = PromptType.CUSTOM,
        metadata: Optional[PromptMetadata] = None
    )
```

**示例:**

```python
from src.core.prompt import SimplePrompt, PromptType

prompt = SimplePrompt(
    name="system_role",
    content="You are an AI assistant specialized in Python programming.",
    prompt_type=PromptType.SYSTEM
)

result = prompt.render()  # 返回 content，忽略参数
```

---

### TemplatePrompt (类)

支持参数的动态提示词。

```python
class TemplatePrompt(PromptBase):
    def __init__(
        self,
        name: str,
        template: Union[str, PromptTemplate],
        prompt_type: PromptType = PromptType.CUSTOM,
        metadata: Optional[PromptMetadata] = None
    )
```

**示例:**

```python
from src.core.prompt import (
    TemplatePrompt, PromptParam, ParamType
)

prompt = TemplatePrompt(
    name="user_question",
    template="Question about {topic}: {question}"
)

prompt.params.add_params([
    PromptParam("topic", ParamType.STRING, required=True),
    PromptParam("question", ParamType.STRING, required=True),
])

result = prompt.render(
    topic="Python",
    question="How to use list comprehension?"
)
```

---

### ChainedPrompt (类)

链式提示词，用于组合多个提示词。

```python
class ChainedPrompt(PromptBase):
    def __init__(
        self,
        name: str,
        prompts: List[PromptBase],
        separator: str = "\n",
        prompt_type: PromptType = PromptType.CUSTOM,
        metadata: Optional[PromptMetadata] = None
    )
```

**属性:**

| 属性 | 类型 | 说明 |
|------|------|------|
| `prompts` | `List[PromptBase]` | 子提示词列表 |
| `separator` | `str` | 子提示词之间的分隔符 |

**方法:**

```python
def add_prompt(self, prompt: PromptBase) -> None:
    """添加提示词"""

def remove_prompt(self, name: str) -> bool:
    """
    移除提示词
    
    Returns:
        bool: 是否成功移除
    """
```

**示例:**

```python
from src.core.prompt import ChainedPrompt

chain = ChainedPrompt(
    name="full_conversation",
    prompts=[system_prompt, user_prompt, assistant_prompt],
    separator="\n---\n"
)

chain.add_prompt(another_prompt)
chain.remove_prompt("user_prompt")
```

---

## 全局管理器

### PromptCategory (枚举)

提示词分类。

```python
class PromptCategory(Enum):
    SYSTEM = "system"    # 系统级提示词
    DOMAIN = "domain"    # 领域相关提示词
    DIALOG = "dialog"    # 对话相关提示词
    TASK = "task"        # 任务相关提示词
    CUSTOM = "custom"    # 自定义提示词
```

---

### PromptPriority (枚举)

提示词优先级。

```python
class PromptPriority(Enum):
    LOW = 1              # 低优先级
    NORMAL = 2           # 正常优先级
    HIGH = 3             # 高优先级
    CRITICAL = 4         # 紧急优先级
```

---

### PromptManager (类)

全局提示词管理器（单例模式）。

```python
class PromptManager:
    """全局提示词管理器"""
```

#### 生命周期管理

```python
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
        bool: 是否注册成功
    """

def unregister(self, name: str) -> bool:
    """
    移除提示词
    
    Args:
        name: 提示词名称
        
    Returns:
        bool: 是否移除成功
    """
```

#### 获取提示词

```python
def get(self, name: str) -> Optional[PromptBase]:
    """获取单个提示词"""

def get_by_category(
    self, category: PromptCategory
) -> List[PromptBase]:
    """按分类获取提示词"""

def get_by_priority(
    self, priority: PromptPriority
) -> List[PromptBase]:
    """按优先级获取提示词"""

def get_all(self) -> Dict[str, PromptBase]:
    """获取所有提示词"""

def list_names(self) -> List[str]:
    """列出所有提示词名称"""
```

#### 渲染

```python
def render(self, name: str, **kwargs) -> Optional[str]:
    """
    渲染提示词
    
    Args:
        name: 提示词名称
        **kwargs: 渲染参数
        
    Returns:
        Optional[str]: 渲染后的文本，不存在返回 None
    """

def render_multiple(
    self, names: List[str], **kwargs
) -> Dict[str, str]:
    """
    渲染多个提示词
    
    Args:
        names: 提示词名称列表
        **kwargs: 共享的渲染参数
        
    Returns:
        Dict[str, str]: 名称 -> 渲染结果
    """
```

#### 拦截器

```python
def add_interceptor(
    self, interceptor: Callable[[str, str, PromptBase], str]
) -> None:
    """
    添加渲染拦截器
    
    Args:
        interceptor: 拦截器函数，签名为 
                    (rendered_text, name, prompt) -> str
    """

def remove_interceptor(self, interceptor: Callable) -> bool:
    """移除拦截器"""
```

#### 生命周期钩子

```python
def add_hook(self, event: str, hook: Callable) -> bool:
    """
    添加生命周期钩子
    
    Args:
        event: 事件名 (before_register, after_register, 
              before_render, after_render, before_remove, after_remove)
        hook: 钩子函数
        
    Returns:
        bool: 是否添加成功
    """

def remove_hook(self, event: str, hook: Callable) -> bool:
    """移除钩子"""
```

#### 模板管理

```python
def register_template(
    self, template_id: str, template_text: str
) -> bool:
    """注册模板"""

def get_template(self, template_id: str) -> Optional[str]:
    """获取模板"""

def update_template(
    self, template_id: str, template_text: str
) -> bool:
    """更新模板"""

def remove_template(self, template_id: str) -> bool:
    """移除模板"""
```

#### 工具方法

```python
def exists(self, name: str) -> bool:
    """检查提示词是否存在"""

def count(self) -> int:
    """获取提示词总数"""

def clear(self) -> None:
    """清空所有提示词"""

def reset(self) -> None:
    """重置管理器（包括所有配置）"""

def get_statistics(self) -> Dict[str, Any]:
    """
    获取统计信息
    
    Returns:
        dict: 包含 total_prompts, categories, templates, interceptors
    """
```

---

## 便捷 API

### 模块级函数

```python
from src.core.prompt import (
    get_manager,
    register,
    unregister,
    get,
    render,
    render_multiple,
    list_all,
    list_names,
)

def get_manager() -> PromptManager:
    """获取全局 PromptManager 实例"""

def register(
    prompt: PromptBase,
    category: PromptCategory = PromptCategory.CUSTOM,
    priority: PromptPriority = PromptPriority.NORMAL
) -> bool:
    """注册提示词"""

def unregister(name: str) -> bool:
    """移除提示词"""

def get(name: str) -> Optional[PromptBase]:
    """获取提示词"""

def render(name: str, **kwargs) -> Optional[str]:
    """渲染提示词"""

def render_multiple(names: list, **kwargs) -> dict:
    """渲染多个提示词"""

def list_all() -> dict:
    """列出所有提示词"""

def list_names() -> list:
    """列出所有提示词名称"""
```

---

## LLM 联动

### llm_generate (异步函数)

渲染指定提示词并调用 LLM（非流式）。

```python
async def llm_generate(
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
) -> Optional[LLMResponse]:
    ...
```

**要点:**
- 先使用 `PromptManager.render()` 渲染提示词；失败时返回 `None`。
- 渲染结果按 `role`（默认 user）追加为一条消息；`base_messages` 可预置 system/上下文消息。
- 若传入 `tools`/`tool_choice`，自动走工具调用；否则普通生成。

### llm_stream_generate (异步生成器)

渲染提示词并以流式方式调用 LLM。

```python
async def llm_stream_generate(... ) -> AsyncIterator[StreamChunk]:
    ...
```

**要点:**
- 逻辑与 `llm_generate` 相同，内部强制 `stream=True`。
- 按块产出 `StreamChunk`，`chunk.delta` 可用于逐步拼接。

---

## 异常和错误

当前版本不抛出自定义异常，而是通过返回值（`None`, `False` 等）表示错误。

| 操作 | 失败返回 | 检查方式 |
|------|---------|---------|
| `register()` | `False` | `if not success:` |
| `unregister()` | `False` | `if not success:` |
| `get()` | `None` | `if prompt is None:` |
| `render()` | `None` | `if result is None:` |
| `validate()` | `False` | `if not valid:` |
| `set_value()` | `False` | `if not success:` |

**错误处理示例:**

```python
from src.core.prompt import register, render, get

# 注册错误处理
if not register(prompt):
    print("Failed to register prompt")

# 获取错误处理
prompt = get("name")
if prompt is None:
    print("Prompt not found")

# 渲染错误处理
result = render("name")
if result is None:
    print("Rendering failed")
else:
    print(result)
```

---

## 完整示例

```python
from src.core.prompt import (
    PromptTemplate,
    TemplatePrompt,
    SimplePrompt,
    PromptParam,
    ParamType,
    PromptType,
    PromptCategory,
    PromptPriority,
    register,
    render,
    get_manager,
)

# 1. 创建系统提示词
system = SimplePrompt(
    name="system",
    content="You are a helpful assistant.",
    prompt_type=PromptType.SYSTEM
)

# 2. 创建用户提示词模板
user = TemplatePrompt(
    name="user_input",
    template="User: {message}",
    prompt_type=PromptType.USER
)
user.params.add_param(
    PromptParam("message", ParamType.STRING, required=True)
)

# 3. 注册提示词
register(system, PromptCategory.SYSTEM, PromptPriority.CRITICAL)
register(user, PromptCategory.DIALOG, PromptPriority.NORMAL)

# 4. 使用拦截器
manager = get_manager()
manager.add_interceptor(
    lambda text, name, prompt: f"[{name}]: {text}"
)

# 5. 渲染提示词
system_text = render("system")
user_text = render("user_input", message="Hello!")

print(system_text)  # [system]: You are a helpful assistant.
print(user_text)    # [user_input]: User: Hello!
```
