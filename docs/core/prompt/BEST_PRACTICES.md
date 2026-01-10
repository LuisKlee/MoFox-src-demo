# 提示词管理系统 - 最佳实践

## 目录

- [设计原则](#设计原则)
- [命名规范](#命名规范)
- [参数管理](#参数管理)
- [提示词设计](#提示词设计)
- [管理器使用](#管理器使用)
- [拦截器和钩子](#拦截器和钩子)
- [错误处理](#错误处理)
- [性能优化](#性能优化)
- [常见模式](#常见模式)

---

## 设计原则

### 1. 单一职责原则

每个提示词应该只做一件事情，保持职责单一。

**❌ 不推荐:**

```python
# 这个提示词做了太多事情
prompt = TemplatePrompt(
    name="all_in_one",
    template="""
    System: {system_role}
    User: {user_input}
    Previous: {history}
    Instructions: {instructions}
    """
)
```

**✅ 推荐:**

```python
# 分离关注点
system_prompt = SimplePrompt("system_role", "You are a helpful assistant.")
user_prompt = TemplatePrompt("user_input", "User: {message}")
history_prompt = TemplatePrompt("history", "Previous: {history_text}")
instruction_prompt = TemplatePrompt("instructions", "Do: {instruction}")

# 用 ChainedPrompt 组合它们
chain = ChainedPrompt(
    "full_prompt",
    [system_prompt, user_prompt, history_prompt, instruction_prompt],
    separator="\n"
)
```

### 2. 可组合性

设计提示词时考虑可组合性，支持灵活的重组。

**✅ 推荐:**

```python
# 基础提示词片段
greeting = SimplePrompt("greeting", "Hello {name}")
role = SimplePrompt("role", "I am a {role_type} assistant")
capability = SimplePrompt("capability", "I can help with {topics}")

# 可根据需要组合不同的片段
minimal_prompt = ChainedPrompt("minimal", [greeting, role])
full_prompt = ChainedPrompt("full", [greeting, role, capability])
```

### 3. 可维护性

使用清晰的命名和文档，使提示词易于维护。

**✅ 推荐:**

```python
# 清晰的命名和元数据
prompt = TemplatePrompt(
    name="customer_service_response",
    template="Respond professionally to: {customer_question}",
)

prompt.metadata.description = "用于客户服务的回复模板"
prompt.metadata.version = "2.0.0"
prompt.metadata.author = "Support Team"
prompt.metadata.tags = ["customer-service", "response"]

# 详细的参数文档
prompt.params.add_param(
    PromptParam(
        "customer_question",
        ParamType.STRING,
        required=True,
        description="客户提出的问题，长度不超过 500 字符"
    )
)
```

---

## 命名规范

### 提示词名称

使用下划线分隔的小写字母，格式为: `domain_purpose` 或 `domain_component_action`

**✅ 推荐:**

```python
# 好的命名示例
"system_base_instruction"
"user_query_handler"
"assistant_response_formatter"
"dialog_context_manager"
"task_validation_rules"
"chain_full_conversation"
```

**❌ 避免:**

```python
# 不清晰的命名
"p1", "prompt", "temp", "myPrompt"
"system", "user", "assistant"  # 太通用
"SystemPrompt", "UserPrompt"   # 使用 CamelCase
"系统提示词", "用户输入"       # 中文变量名
```

### 参数名称

参数名称应该清晰表达其含义。

**✅ 推荐:**

```python
PromptParam("user_name", ...)           # 清晰
PromptParam("conversation_history", ...) # 清晰
PromptParam("max_tokens", ...)          # 清晰
```

**❌ 避免:**

```python
PromptParam("u", ...)        # 太短
PromptParam("x", ...)        # 无意义
PromptParam("p1", "p2", ...) # 通用名
```

### 分类和优先级

合理使用分类组织提示词，设置符合实际的优先级。

**✅ 推荐:**

```python
from src.core.prompt import PromptCategory, PromptPriority

# 核心系统指令 - 最高优先级
register(
    system_instruction,
    category=PromptCategory.SYSTEM,
    priority=PromptPriority.CRITICAL
)

# 对话流程 - 普通优先级
register(
    dialog_handler,
    category=PromptCategory.DIALOG,
    priority=PromptPriority.NORMAL
)

# 可选功能 - 低优先级
register(
    enhancement_prompt,
    category=PromptCategory.CUSTOM,
    priority=PromptPriority.LOW
)
```

---

## 参数管理

### 1. 始终定义参数

对于 TemplatePrompt，始终定义参数和验证器。

**✅ 推荐:**

```python
prompt = TemplatePrompt(
    "user_input",
    "Process: {data}"
)

# 添加参数定义
prompt.params.add_param(
    PromptParam(
        "data",
        ParamType.STRING,
        required=True,
        validator=lambda x: len(x) > 0,
        description="输入数据"
    )
)

# 验证提示词
assert prompt.validate(), "Prompt validation failed"
```

### 2. 使用类型验证

利用 ParamType 进行类型检查。

**✅ 推荐:**

```python
# 指定正确的类型
prompt.params.add_params([
    PromptParam("user_id", ParamType.INTEGER, required=True),
    PromptParam("score", ParamType.FLOAT, required=True),
    PromptParam("is_active", ParamType.BOOLEAN, required=False),
    PromptParam("tags", ParamType.LIST, required=False),
])

# 渲染时传入正确类型的值
render("prompt_name", user_id=123, score=95.5, is_active=True, tags=["tag1", "tag2"])
```

### 3. 提供默认值

为可选参数提供合理的默认值。

**✅ 推荐:**

```python
prompt.params.add_params([
    PromptParam("name", ParamType.STRING, required=True),
    PromptParam("language", ParamType.STRING, required=False, default="en"),
    PromptParam("max_length", ParamType.INTEGER, required=False, default=100),
])

# 渲染时可以省略有默认值的参数
render("prompt_name", name="Alice")  # language 和 max_length 使用默认值
```

### 4. 自定义验证

为复杂的验证需求编写验证器。

**✅ 推荐:**

```python
import re

def validate_email(value):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, value) is not None

def validate_age(value):
    """验证年龄范围"""
    return isinstance(value, int) and 0 <= value <= 150

def validate_list_not_empty(value):
    """验证列表不为空"""
    return isinstance(value, list) and len(value) > 0

# 使用验证器
prompt.params.add_params([
    PromptParam("email", ParamType.STRING, required=True, 
               validator=validate_email, description="用户邮箱"),
    PromptParam("age", ParamType.INTEGER, required=False,
               validator=validate_age, description="用户年龄"),
    PromptParam("tags", ParamType.LIST, required=True,
               validator=validate_list_not_empty, description="标签列表"),
])
```

---

## 提示词设计

### 1. 分离关注点

不要在一个提示词中混合多个目标。

**❌ 不推荐:**

```python
prompt = TemplatePrompt(
    "mixed_prompt",
    """You are {role}. Answer {question}. 
    Remember: {rules}. Also {additional_task}."""
)
```

**✅ 推荐:**

```python
# 分离成多个提示词
role_prompt = SimplePrompt("role_instruction", "You are {role}")
question_prompt = TemplatePrompt("question_handler", "Answer: {question}")
rules_prompt = SimplePrompt("rules", "Remember: {rules}")
task_prompt = TemplatePrompt("additional_task", "Also: {task}")

# 根据需要组合
complete_prompt = ChainedPrompt(
    "complete_instruction",
    [role_prompt, question_prompt, rules_prompt, task_prompt],
    separator="\n"
)
```

### 2. 使用模板化

避免硬编码值，使用参数让提示词更灵活。

**❌ 不推荐:**

```python
static_prompt = SimplePrompt(
    "greeting",
    "Hello Alice! Welcome to the system."
)
```

**✅ 推荐:**

```python
dynamic_prompt = TemplatePrompt(
    "greeting",
    "Hello {user_name}! Welcome to {system_name}."
)

dynamic_prompt.params.add_params([
    PromptParam("user_name", ParamType.STRING, required=True),
    PromptParam("system_name", ParamType.STRING, required=False, default="MoFox"),
])
```

### 3. 版本管理

维护提示词的版本信息。

**✅ 推荐:**

```python
from src.core.prompt import PromptMetadata

metadata = PromptMetadata(
    name="customer_support",
    description="客户支持对话提示词",
    version="3.2.1",
    author="Support Team",
    tags=["customer-support", "v3"],
)

prompt = TemplatePrompt("customer_support", "template", metadata=metadata)

# 更新时记录变化
metadata.version = "3.3.0"
metadata.updated_at = "2024-01-10"
```

---

## 管理器使用

### 1. 集中管理

将所有提示词注册到全局管理器。

**✅ 推荐:**

```python
from src.core.prompt import register, PromptCategory, PromptPriority

# 在应用启动时注册所有提示词
def initialize_prompts():
    register(system_prompt, PromptCategory.SYSTEM, PromptPriority.CRITICAL)
    register(user_prompt, PromptCategory.DIALOG, PromptPriority.NORMAL)
    register(task_prompt, PromptCategory.TASK, PromptPriority.NORMAL)
    # ... 更多提示词

# 在应用启动时调用
initialize_prompts()
```

### 2. 分类和优先级

使用分类和优先级有效地组织提示词。

**✅ 推荐:**

```python
# 按分类获取
system_prompts = manager.get_by_category(PromptCategory.SYSTEM)
dialog_prompts = manager.get_by_category(PromptCategory.DIALOG)

# 按优先级获取（用于性能优化）
critical_prompts = manager.get_by_priority(PromptPriority.CRITICAL)
```

### 3. 动态创建

支持运行时动态创建和注册提示词。

**✅ 推荐:**

```python
def register_dynamic_prompts(config):
    """根据配置动态创建提示词"""
    for name, template in config.items():
        prompt = TemplatePrompt(name, template)
        register(prompt)

# 使用配置文件或数据库中的提示词
config = {
    "greeting": "Hello {name}!",
    "farewell": "Goodbye {name}!",
}
register_dynamic_prompts(config)
```

### 4. 查询和检查

在使用前检查提示词是否存在。

**✅ 推荐:**

```python
from src.core.prompt import get_manager

manager = get_manager()

# 检查存在性
if not manager.exists("my_prompt"):
    print("Prompt not found")

# 安全地获取
prompt = manager.get("my_prompt")
if prompt:
    # 使用提示词
    pass

# 获取统计信息
stats = manager.get_statistics()
print(f"Total prompts: {stats['total_prompts']}")
```

---

## 拦截器和钩子

### 1. 拦截器使用场景

拦截器用于在渲染后处理结果。

**✅ 推荐用途:**

```python
from src.core.prompt import get_manager

manager = get_manager()

# 添加日志
def log_interceptor(text, name, prompt):
    import logging
    logging.info(f"Rendered {name}: {len(text)} chars")
    return text

# 添加格式化
def format_interceptor(text, name, prompt):
    return f"[{name}]\n{text}\n[/{name}]"

# 添加验证
def validate_length_interceptor(text, name, prompt):
    if len(text) > 1000:
        print(f"Warning: {name} is too long ({len(text)} chars)")
    return text

manager.add_interceptor(log_interceptor)
manager.add_interceptor(format_interceptor)
manager.add_interceptor(validate_length_interceptor)
```

### 2. 钩子使用场景

钩子用于在特定生命周期事件时执行操作。

**✅ 推荐用途:**

```python
from src.core.prompt import get_manager

manager = get_manager()

# 记录注册事件
def log_registration(prompt):
    print(f"Registering: {prompt.name}")

# 发送通知
def notify_after_registration(prompt):
    # 发送消息队列或发送邮件
    pass

# 验证参数
def validate_before_render(prompt, kwargs):
    if not prompt.params.validate_all():
        raise ValueError(f"Missing required parameters for {prompt.name}")

manager.add_hook("before_register", log_registration)
manager.add_hook("after_register", notify_after_registration)
manager.add_hook("before_render", validate_before_render)
```

### 3. 最少化副作用

保持拦截器和钩子简单，避免复杂的副作用。

**✅ 推荐:**

```python
# 简单且快速的操作
def simple_hook(prompt):
    prompt.metadata.last_accessed = time.time()

manager.add_hook("after_render", simple_hook)
```

**❌ 避免:**

```python
# 复杂的操作可能影响性能
def complex_hook(prompt):
    # 不要在钩子中做 I/O 操作
    db.update_prompt_stats(prompt.name)
    send_network_request(prompt.name)
    write_to_file(prompt.name)
```

---

## 错误处理

### 1. 检查返回值

始终检查操作返回值。

**✅ 推荐:**

```python
from src.core.prompt import register, render, get

# 注册检查
if not register(prompt):
    print("Failed to register prompt")
    return False

# 获取检查
prompt = get("name")
if prompt is None:
    print("Prompt not found")
    return None

# 渲染检查
result = render("name", param1="value")
if result is None:
    print("Rendering failed - prompt not found or validation error")
    return None

print(result)
```

### 2. 参数验证

在设置参数值前进行验证。

**✅ 推荐:**

```python
from src.core.prompt import PromptParams, PromptParam, ParamType

params = PromptParams()
params.add_param(PromptParam("age", ParamType.INTEGER, required=True))

# 验证后再设置
if params.validate_all():
    if params.set_value("age", 25):
        print("Value set successfully")
    else:
        print("Invalid value")
else:
    missing = params.get_missing_params()
    print(f"Missing required parameters: {missing}")
```

### 3. 安全的渲染

处理渲染失败的情况。

**✅ 推荐:**

```python
def safe_render(name, default_value="", **kwargs):
    """安全渲染，失败时返回默认值"""
    result = render(name, **kwargs)
    return result if result is not None else default_value

# 使用
greeting = safe_render("greeting", default_value="Hello!", user="Alice")
```

---

## 性能优化

### 1. 缓存参数提取

模板参数只需提取一次。

**✅ 推荐:**

```python
# 参数已在初始化时缓存
template = PromptTemplate("Hello {name}, you are {age} years old")
param_names = template.get_param_names()  # ['name', 'age'] - 已缓存

# 后续使用不需要重新提取
for _ in range(1000):
    result = template.render({"name": "Alice", "age": 25})
```

### 2. 批量渲染

需要渲染多个提示词时使用批量 API。

**✅ 推荐:**

```python
from src.core.prompt import render_multiple

# 批量渲染 - 共享参数，减少开销
results = render_multiple(
    ["prompt1", "prompt2", "prompt3", "prompt4"],
    shared_param="value"
)
```

**❌ 避免:**

```python
# 逐个渲染 - 重复的开销
results = {}
for name in ["prompt1", "prompt2", "prompt3", "prompt4"]:
    results[name] = render(name, shared_param="value")
```

### 3. 拦截器优化

保持拦截器简单快速。

**✅ 推荐:**

```python
# 快速的字符串操作
def fast_interceptor(text, name, prompt):
    return text.strip()

manager.add_interceptor(fast_interceptor)
```

**❌ 避免:**

```python
# 避免在拦截器中做昂贵操作
def slow_interceptor(text, name, prompt):
    # 不要在这里做数据库查询
    user = db.query(User).filter(...).first()
    # 不要做网络请求
    response = requests.get(f"http://api.example.com/{name}")
    return text
```

### 4. 预先加载

应用启动时预加载所有提示词。

**✅ 推荐:**

```python
# 应用启动时
def initialize_app():
    # 注册所有提示词
    register_all_prompts()
    
    # 预热缓存
    manager = get_manager()
    for name in manager.list_names():
        prompt = manager.get(name)
        if prompt:
            prompt.validate()

# 避免运行时延迟
initialize_app()
```

---

## 常见模式

### 1. 角色扮演（Role Playing）

```python
from src.core.prompt import SimplePrompt, PromptType, register

# 定义不同的角色
roles = {
    "assistant": "You are a helpful AI assistant.",
    "developer": "You are an expert software developer.",
    "teacher": "You are an experienced teacher.",
}

for role_name, instruction in roles.items():
    prompt = SimplePrompt(
        f"role_{role_name}",
        instruction,
        prompt_type=PromptType.SYSTEM
    )
    register(prompt)

# 使用
from src.core.prompt import render
instruction = render("role_developer")
```

### 2. 上下文管理（Context Management）

```python
from src.core.prompt import ChainedPrompt, SimplePrompt

# 构建上下文
context_parts = [
    SimplePrompt("system_role", "You are a helpful assistant."),
    SimplePrompt("context_knowledge", "You have knowledge about AI and ML."),
    SimplePrompt("output_format", "Format your response as JSON."),
]

context_prompt = ChainedPrompt(
    "full_context",
    context_parts,
    separator="\n"
)

register(context_prompt)
```

### 3. 条件提示词（Conditional Prompts）

```python
from src.core.prompt import TemplatePrompt, PromptParam, ParamType, get_manager

# 创建带条件的提示词
prompt = TemplatePrompt(
    "conditional_response",
    "Handle {request_type}: {details}"
)

prompt.params.add_params([
    PromptParam("request_type", ParamType.STRING, required=True),
    PromptParam("details", ParamType.STRING, required=True),
])

register(prompt)

# 使用条件逻辑
manager = get_manager()
manager.add_interceptor(lambda text, name, prompt: 
    "[URGENT] " + text if "urgent" in text.lower() else text
)
```

### 4. 多语言提示词（Multi-language Prompts）

```python
from src.core.prompt import SimplePrompt, register, PromptCategory, PromptPriority

languages = {
    "en": "Hello, how can I help you?",
    "zh": "你好，我能帮助你什么？",
    "es": "Hola, ¿cómo puedo ayudarte?",
}

for lang, greeting in languages.items():
    prompt = SimplePrompt(f"greeting_{lang}", greeting)
    register(prompt, category=PromptCategory.CUSTOM)

# 使用
from src.core.prompt import render
greeting = render(f"greeting_{user_language}")
```

### 5. 提示词模板库（Prompt Library）

```python
# prompts/library.py
from src.core.prompt import SimplePrompt, TemplatePrompt, register

class PromptLibrary:
    @staticmethod
    def register_all():
        # 基础提示词
        register(SimplePrompt("system_base", "You are helpful."))
        
        # 对话提示词
        register(TemplatePrompt("user_greeting", "User says: {message}"))
        
        # 格式提示词
        register(SimplePrompt("format_json", "Format response as JSON."))
        
        # ... 更多提示词

# 应用启动时
PromptLibrary.register_all()
```

---

## 总结

遵循这些最佳实践能够帮助：

- ✅ 编写可维护和可读的提示词代码
- ✅ 避免常见的设计陷阱
- ✅ 提高性能和可靠性
- ✅ 支持团队协作和代码复用
- ✅ 便于测试和调试

记住：**好的提示词设计是可组合、可测试、可维护的。**
