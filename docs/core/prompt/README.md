# 提示词管理系统 (Prompt Management System)

## 概述

提示词管理系统是 MoFox Core 层的核心组件，提供了一个完整的、可扩展的提示词（Prompt）生命周期管理解决方案。该系统支持：

- 🎯 **多种提示词类型**：静态提示词、动态模板提示词、链式提示词
- 📦 **参数系统**：类型验证、默认值、自定义验证器
- 🎛️ **全局管理**：单例模式的全局 PromptManager
- 🔌 **扩展机制**：拦截器和生命周期钩子
- 📊 **分类和优先级**：灵活的组织和管理方式
- 📝 **模板管理**：注册和管理可复用的提示词模板
- 🤖 **LLM 联动**：内置 `llm_generate` / `llm_stream_generate` 快捷调用

## 系统架构

```
src/core/prompt/
├── params.py          # 参数系统（类型、验证、模板）
├── prompt.py          # Prompt基类和各类型实现
├── manager.py         # 全局管理器（单例模式）
└── __init__.py        # 公开 API 导出
```

### 核心模块

| 模块 | 职责 | 关键类 |
|------|------|--------|
| **params.py** | 参数定义和验证 | `ParamType`, `PromptParam`, `PromptTemplate` |
| **prompt.py** | 提示词实现 | `PromptBase`, `SimplePrompt`, `TemplatePrompt`, `ChainedPrompt` |
| **manager.py** | 全局管理 | `PromptManager`, `PromptCategory`, `PromptPriority` |

## 快速开始

### 1. 创建简单提示词

```python
from src.core.prompt import SimplePrompt, PromptType, register, render

# 创建静态提示词
system_prompt = SimplePrompt(
    name="system_greeting",
    content="You are a helpful AI assistant.",
    prompt_type=PromptType.SYSTEM
)

# 注册提示词
register(system_prompt)

# 渲染提示词
result = render("system_greeting")
print(result)  # Output: You are a helpful AI assistant.
```

### 2. 创建模板提示词

```python
from src.core.prompt import (
    TemplatePrompt, PromptParam, ParamType, PromptType, 
    register, render
)

# 创建模板提示词
user_prompt = TemplatePrompt(
    name="user_message",
    template="请回答关于{topic}的问题：{question}",
    prompt_type=PromptType.USER
)

# 添加参数定义
user_prompt.params.add_params([
    PromptParam("topic", ParamType.STRING, required=True, 
                description="讨论的主题"),
    PromptParam("question", ParamType.STRING, required=True,
                description="用户提出的问题")
])

# 注册提示词
register(user_prompt)

# 渲染提示词
result = render("user_message", topic="Python编程", question="如何使用列表推导式?")
print(result)  # Output: 请回答关于Python编程的问题：如何使用列表推导式?
```

### 3. 创建链式提示词

```python
from src.core.prompt import ChainedPrompt, register, render

# 创建链式提示词（组合多个提示词）
chain_prompt = ChainedPrompt(
    name="full_conversation",
    prompts=[system_prompt, user_prompt],
    separator="\n---\n"
)

register(chain_prompt)

result = render("full_conversation", topic="AI", question="什么是智能？")

### 4. 直接联动 LLM（非流式与流式）

```python
from src.core.prompt import llm_generate, llm_stream_generate

# 非流式：渲染提示词并调用 LLM
resp = await llm_generate(
    name="user_message",               # 已注册的提示词
    model="gpt-4o",                    # 模型名
    provider="openai",                 # 提供商
    prompt_vars={"topic": "Python", "question": "什么是生成器？"},
    role="user",                       # 渲染结果的消息角色
    temperature=0.3,
    max_tokens=256,
)
print(resp.content)

# 流式：逐块读取
async for chunk in llm_stream_generate(
    "user_message",
    model="gpt-4o",
    provider="openai",
    prompt_vars={"topic": "Python", "question": "什么是生成器？"},
    role="user",
):
    if chunk.delta:
        print(chunk.delta, end="", flush=True)
```
```

## 详细使用指南

### 参数系统

#### ParamType（参数类型）

```python
from src.core.prompt import ParamType

# 支持的参数类型
ParamType.STRING    # 字符串
ParamType.INTEGER   # 整数
ParamType.FLOAT     # 浮点数
ParamType.BOOLEAN   # 布尔值
ParamType.LIST      # 列表
ParamType.DICT      # 字典
ParamType.ANY       # 任意类型
```

#### PromptParam（参数定义）

```python
from src.core.prompt import PromptParam, ParamType

# 基础参数定义
param = PromptParam(
    name="user_name",
    param_type=ParamType.STRING,
    required=True,
    default="Anonymous",
    description="用户名称"
)

# 带自定义验证器的参数
def validate_age(value):
    return isinstance(value, int) and 0 <= value <= 150

age_param = PromptParam(
    name="age",
    param_type=ParamType.INTEGER,
    required=False,
    validator=validate_age,
    description="用户年龄"
)
```

#### PromptParams（参数集合）

```python
from src.core.prompt import PromptParams, PromptParam, ParamType

# 创建参数集合
params = PromptParams()

# 添加参数定义
params.add_param(PromptParam("name", ParamType.STRING, required=True))
params.add_param(PromptParam("age", ParamType.INTEGER, required=False, default=0))

# 设置参数值
params.set_value("name", "Alice")
params.set_value("age", 25)

# 获取参数值
name = params.get_value("name")  # "Alice"
age = params.get_value("age")    # 25

# 验证所有必需参数
is_valid = params.validate_all()  # True
```

#### PromptTemplate（模板引擎）

```python
from src.core.prompt import PromptTemplate

# 创建模板
template = PromptTemplate("Hello {name}, you are {age} years old.")

# 获取参数名列表
param_names = template.get_param_names()  # ['name', 'age']

# 渲染模板
result = template.render({"name": "Alice", "age": 25})
# Output: "Hello Alice, you are 25 years old."

# 使用默认值渲染
result = template.render_with_defaults(
    {"name": "Alice"},
    {"age": 0}
)
# Output: "Hello Alice, you are 0 years old."
```

### Prompt 类型

#### SimplePrompt（简单提示词）

静态、无参数的提示词：

```python
from src.core.prompt import SimplePrompt, PromptType

prompt = SimplePrompt(
    name="farewell",
    content="Goodbye!",
    prompt_type=PromptType.CUSTOM
)

# 渲染时忽略所有参数
result = prompt.render(any_param="value")  # "Goodbye!"
```

#### TemplatePrompt（模板提示词）

支持参数的动态提示词：

```python
from src.core.prompt import TemplatePrompt, PromptParam, ParamType

prompt = TemplatePrompt(
    name="greeting",
    template="Hello {name}!"
)

# 添加参数定义
prompt.params.add_param(PromptParam("name", ParamType.STRING, required=True))

# 验证提示词
is_valid = prompt.validate()  # True

# 渲染提示词
result = prompt.render(name="World")  # "Hello World!"
```

#### ChainedPrompt（链式提示词）

组合多个提示词：

```python
from src.core.prompt import ChainedPrompt

prompts = [prompt1, prompt2, prompt3]

chain = ChainedPrompt(
    name="combined",
    prompts=prompts,
    separator=" -> "
)

# 添加提示词
chain.add_prompt(prompt4)

# 移除提示词
chain.remove_prompt("prompt_name")

# 渲染所有子提示词
result = chain.render(param1="value1")
```

### 全局管理器

#### 注册和注销

```python
from src.core.prompt import (
    PromptManager, PromptCategory, PromptPriority, 
    SimplePrompt, register, unregister
)

manager = PromptManager()

# 创建提示词
prompt = SimplePrompt("my_prompt", "Content")

# 方法1：直接注册
success = manager.register(
    prompt,
    category=PromptCategory.SYSTEM,
    priority=PromptPriority.HIGH
)

# 方法2：使用便捷函数
register(prompt, PromptCategory.CUSTOM, PromptPriority.NORMAL)

# 注销
unregister("my_prompt")
```

#### 获取提示词

```python
from src.core.prompt import get, get_manager

manager = get_manager()

# 按名称获取
prompt = get("my_prompt")

# 按分类获取
system_prompts = manager.get_by_category(PromptCategory.SYSTEM)

# 按优先级获取
high_priority = manager.get_by_priority(PromptPriority.HIGH)

# 获取所有提示词
all_prompts = manager.get_all()

# 列出所有名称
names = manager.list_names()

# 检查是否存在
exists = manager.exists("my_prompt")

# 获取总数
count = manager.count()
```

#### 渲染提示词

```python
from src.core.prompt import render, render_multiple, get_manager

manager = get_manager()

# 单个渲染
result = render("prompt_name", param1="value1", param2="value2")

# 批量渲染
results = render_multiple(
    ["prompt1", "prompt2", "prompt3"],
    shared_param="value"
)
# Output: {"prompt1": "rendered1", "prompt2": "rendered2", ...}

# 或通过管理器
result = manager.render("prompt_name", param1="value1")
```

### 拦截器和钩子

#### 拦截器（Interceptor）

拦截器可以在渲染后处理结果：

```python
from src.core.prompt import get_manager

manager = get_manager()

# 定义拦截器
def uppercase_interceptor(rendered_text, name, prompt):
    """将结果转换为大写"""
    return rendered_text.upper()

def add_prefix_interceptor(rendered_text, name, prompt):
    """添加前缀"""
    return f"[{name}]: {rendered_text}"

# 添加拦截器
manager.add_interceptor(uppercase_interceptor)
manager.add_interceptor(add_prefix_interceptor)

# 渲染时会依次应用所有拦截器
result = manager.render("my_prompt")

# 移除拦截器
manager.remove_interceptor(uppercase_interceptor)
```

#### 生命周期钩子（Hooks）

支持的事件：

- `before_register`: 注册前
- `after_register`: 注册后
- `before_render`: 渲染前
- `after_render`: 渲染后
- `before_remove`: 移除前
- `after_remove`: 移除后

```python
from src.core.prompt import get_manager

manager = get_manager()

# 定义钩子
def log_registration(prompt):
    print(f"Registering prompt: {prompt.name}")

def log_rendering(prompt, rendered_text):
    print(f"Rendered {prompt.name}: {len(rendered_text)} chars")

# 添加钩子
manager.add_hook("before_register", log_registration)
manager.add_hook("after_render", log_rendering)

# 注册和渲染时会触发钩子
manager.register(prompt)
manager.render("prompt_name")

# 移除钩子
manager.remove_hook("before_register", log_registration)
```

### 模板管理

```python
from src.core.prompt import get_manager

manager = get_manager()

# 注册模板
manager.register_template(
    "greeting_template",
    "Hello {name}, welcome to {place}!"
)

# 获取模板
template = manager.get_template("greeting_template")

# 更新模板
manager.update_template(
    "greeting_template",
    "Hi {name}, nice to see you at {place}!"
)

# 移除模板
manager.remove_template("greeting_template")
```

### 管理器工具方法

```python
from src.core.prompt import get_manager

manager = get_manager()

# 清空所有提示词
manager.clear()

# 重置管理器（清空所有数据和配置）
manager.reset()

# 获取统计信息
stats = manager.get_statistics()
print(stats)
# Output:
# {
#     "total_prompts": 5,
#     "categories": {"system": 2, "custom": 3},
#     "templates": 2,
#     "interceptors": 1
# }
```

## 高级用法

### 自定义 Prompt 类

如果需要创建自定义的 Prompt 类型，继承 `PromptBase`：

```python
from src.core.prompt import PromptBase, PromptType, PromptMetadata

class CustomPrompt(PromptBase):
    def __init__(self, name: str, handler, metadata=None):
        super().__init__(name, PromptType.CUSTOM, metadata)
        self.handler = handler
    
    def render(self, **kwargs) -> str:
        return self.handler(**kwargs)
    
    def validate(self) -> bool:
        return callable(self.handler)

# 使用自定义 Prompt
def my_handler(name="Guest"):
    return f"Welcome, {name}!"

custom = CustomPrompt("custom_prompt", my_handler)
register(custom)
result = render("custom_prompt", name="Alice")
```

### 动态提示词管理

```python
from src.core.prompt import get_manager, TemplatePrompt

manager = get_manager()

# 运行时动态创建和注册提示词
for i in range(5):
    prompt = TemplatePrompt(
        name=f"dynamic_prompt_{i}",
        template=f"This is dynamic prompt {i} with param: {{param}}"
    )
    manager.register(prompt)

# 批量渲染
results = manager.render_multiple(
    [f"dynamic_prompt_{i}" for i in range(5)],
    param="test"
)
```

### 条件渲染

```python
from src.core.prompt import get_manager

manager = get_manager()

# 使用拦截器实现条件渲染
def conditional_interceptor(rendered_text, name, prompt):
    if "ERROR" in rendered_text:
        return "[ERROR] " + rendered_text
    elif "WARNING" in rendered_text:
        return "[WARNING] " + rendered_text
    return rendered_text

manager.add_interceptor(conditional_interceptor)
```

## 最佳实践

### 1. 命名规范

为提示词使用有意义的名称，建议使用下划线分隔：

```python
# 好的命名
prompt = SimplePrompt("system_greeting", "...")
prompt = TemplatePrompt("user_query_handler", "...")

# 避免
prompt = SimplePrompt("p1", "...")
prompt = TemplatePrompt("prompt", "...")
```

### 2. 参数验证

始终为模板提示词定义参数和验证器：

```python
from src.core.prompt import PromptTemplate, PromptParam, ParamType

prompt = TemplatePrompt("user_input", "User: {message}")

# 添加参数定义和验证
prompt.params.add_param(
    PromptParam(
        "message",
        ParamType.STRING,
        required=True,
        validator=lambda x: len(x) > 0,
        description="用户输入的消息"
    )
)

# 验证
if not prompt.validate():
    raise ValueError("Prompt validation failed")
```

### 3. 分类和优先级

合理使用分类和优先级组织提示词：

```python
from src.core.prompt import register, PromptCategory, PromptPriority

# 系统级高优先级提示词
register(system_prompt, PromptCategory.SYSTEM, PromptPriority.CRITICAL)

# 任务级普通优先级提示词
register(task_prompt, PromptCategory.TASK, PromptPriority.NORMAL)

# 自定义低优先级提示词
register(custom_prompt, PromptCategory.CUSTOM, PromptPriority.LOW)
```

### 4. 错误处理

始终检查渲染结果：

```python
from src.core.prompt import render

result = render("prompt_name", param1="value1")
if result is None:
    print("Prompt not found or rendering failed")
else:
    print(f"Success: {result}")
```

### 5. 模块化设计

在大型项目中，为不同的功能域分离提示词定义：

```
src/core/prompt_definitions/
├── system_prompts.py      # 系统级提示词
├── dialog_prompts.py      # 对话相关提示词
├── task_prompts.py        # 任务相关提示词
└── __init__.py            # 统一导出
```

## 测试

### 单元测试示例

```python
import pytest
from src.core.prompt import (
    SimplePrompt, TemplatePrompt, PromptParam, 
    ParamType, get_manager, register, unregister
)

def test_simple_prompt():
    prompt = SimplePrompt("test_simple", "Content")
    assert prompt.validate()
    assert prompt.render() == "Content"

def test_template_prompt():
    prompt = TemplatePrompt("test_template", "Hello {name}")
    prompt.params.add_param(PromptParam("name", ParamType.STRING))
    assert prompt.validate()
    assert prompt.render(name="World") == "Hello World"

def test_manager_registration():
    manager = get_manager()
    prompt = SimplePrompt("test_reg", "Test")
    
    assert manager.register(prompt)
    assert manager.exists("test_reg")
    assert manager.get("test_reg") is not None
    assert manager.unregister("test_reg")
    assert not manager.exists("test_reg")
```

## 常见问题

### Q: 如何实现动态提示词？
A: 使用 `TemplatePrompt` 并定义参数，在渲染时传入动态值。

### Q: 能否覆盖已注册的提示词？
A: 不能直接覆盖。需要先使用 `unregister()` 移除旧提示词，再注册新的。

### Q: 拦截器的执行顺序是什么？
A: 拦截器按照添加顺序依次执行，结果作为下一个拦截器的输入。

### Q: 如何处理提示词渲染错误？
A: 渲染失败会返回 `None`，应当检查返回值进行错误处理。

### Q: 支持异步渲染吗？
A: 当前版本不支持异步，future 版本可能支持。

## 性能考虑

- PromptManager 是单例，全局共享，注册和渲染操作都是 O(1) 时间复杂度
- 大量拦截器会影响渲染性能，建议按需使用
- 模板引擎使用正则表达式提取参数，一次性计算后缓存
- 参数验证在 `set_value()` 时执行，避免验证开销重复

## 相关文档

- [参数系统详细指南](./API_REFERENCE.md#参数系统)
- [PromptManager API 参考](./API_REFERENCE.md#全局管理器)
- [最佳实践指南](./BEST_PRACTICES.md)
- [快速参考](./QUICK_REFERENCE.md)
