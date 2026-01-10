# 提示词管理系统 - 快速参考

## 导入

```python
# 基本导入
from src.core.prompt import (
    # 参数系统
    ParamType, PromptParam, PromptParams, PromptTemplate,
    # Prompt 类型
    PromptType, PromptMetadata, PromptBase,
    SimplePrompt, TemplatePrompt, ChainedPrompt,
    # 管理器
    PromptCategory, PromptPriority, PromptManager,
    # 便捷函数
    get_manager, register, unregister, get, render,
    render_multiple, list_all, list_names,
    # LLM 调用
    llm_generate, llm_stream_generate,
)
```

## 创建提示词

### SimplePrompt（静态提示词）

```python
prompt = SimplePrompt("name", "content")
```

### TemplatePrompt（模板提示词）

```python
prompt = TemplatePrompt("name", "template with {param}")
prompt.params.add_param(PromptParam("param", ParamType.STRING))
```

### ChainedPrompt（链式提示词）

```python
chain = ChainedPrompt("name", [prompt1, prompt2], separator="\n")
```

## 参数定义

### 创建参数

```python
param = PromptParam(
    "name",                                    # 参数名
    param_type=ParamType.STRING,              # 参数类型
    required=True,                             # 是否必需
    default=None,                              # 默认值
    description="参数描述",                    # 描述
    validator=lambda x: len(x) > 0           # 验证函数
)
```

### 参数类型

```python
ParamType.STRING    # 字符串
ParamType.INTEGER   # 整数
ParamType.FLOAT     # 浮点数
ParamType.BOOLEAN   # 布尔值
ParamType.LIST      # 列表
ParamType.DICT      # 字典
ParamType.ANY       # 任意类型
```

### 参数操作

```python
# 添加参数
params.add_param(param)
params.add_params([param1, param2])

# 设置值
params.set_value("name", "value")
params.set_values({"name": "value", "age": 25})

# 获取值
value = params.get_value("name")
all_values = params.get_all_values()

# 验证
valid = params.validate_all()
missing = params.get_missing_params()
```

## 模板操作

### 创建模板

```python
template = PromptTemplate("Hello {name}, you are {age}")
```

### 提取参数

```python
names = template.get_param_names()  # ['name', 'age']
```

### 渲染模板

```python
# 基本渲染
result = template.render({"name": "Alice", "age": 25})

# 使用默认值
result = template.render_with_defaults(
    {"name": "Bob"},
    {"age": 30}
)
```

## 管理器操作

### 注册

```python
# 直接注册
manager.register(prompt)
manager.register(prompt, PromptCategory.SYSTEM, PromptPriority.HIGH)

# 便捷函数
register(prompt)
register(prompt, PromptCategory.CUSTOM, PromptPriority.NORMAL)
```

### 获取

```python
# 获取单个
prompt = manager.get("name")
prompt = get("name")

# 按分类
prompts = manager.get_by_category(PromptCategory.SYSTEM)

# 按优先级
prompts = manager.get_by_priority(PromptPriority.HIGH)

# 获取全部
all_prompts = manager.get_all()
names = manager.list_names()
```

### 移除

```python
manager.unregister("name")
unregister("name")
```

### 渲染

```python
# 单个渲染
result = manager.render("name", param1="value")
result = render("name", param1="value")

# 批量渲染
results = manager.render_multiple(["name1", "name2"], param="value")
results = render_multiple(["name1", "name2"], param="value")
```

### LLM 调用

```python
# 非流式
resp = await llm_generate(
    "user_message",
    model="gpt-4o",
    provider="openai",
    prompt_vars={"topic": "Python", "question": "生成器是什么"},
    role="user",
    temperature=0.3,
    max_tokens=256,
)

# 流式
async for chunk in llm_stream_generate(
    "user_message",
    model="gpt-4o",
    provider="openai",
    prompt_vars={"topic": "Python", "question": "生成器是什么"},
    role="user",
):
    if chunk.delta:
        print(chunk.delta, end="", flush=True)
```

## 拦截器

### 添加拦截器

```python
def my_interceptor(rendered_text, name, prompt):
    return rendered_text.upper()

manager.add_interceptor(my_interceptor)
```

### 移除拦截器

```python
manager.remove_interceptor(my_interceptor)
```

## 生命周期钩子

### 支持的事件

```python
"before_register"   # 注册前
"after_register"    # 注册后
"before_render"     # 渲染前
"after_render"      # 渲染后
"before_remove"     # 移除前
"after_remove"      # 移除后
```

### 使用钩子

```python
def hook_function(prompt):
    print(f"Registering {prompt.name}")

manager.add_hook("before_register", hook_function)
manager.remove_hook("before_register", hook_function)
```

## 模板管理

### 模板操作

```python
# 注册
manager.register_template("id", "template text")

# 获取
template = manager.get_template("id")

# 更新
manager.update_template("id", "new template")

# 移除
manager.remove_template("id")
```

## 工具方法

```python
# 检查
manager.exists("name")          # True/False

# 计数
count = manager.count()         # int

# 清空
manager.clear()                 # 清空所有提示词

# 重置
manager.reset()                 # 重置管理器

# 统计
stats = manager.get_statistics()
# {
#   "total_prompts": 5,
#   "categories": {...},
#   "templates": 2,
#   "interceptors": 1
# }
```

## 常见代码片段

### 完整流程

```python
from src.core.prompt import *

# 1. 创建
prompt = TemplatePrompt("greeting", "Hello {name}")
prompt.params.add_param(PromptParam("name", ParamType.STRING, required=True))

# 2. 注册
register(prompt, PromptCategory.CUSTOM, PromptPriority.NORMAL)

# 3. 渲染
result = render("greeting", name="Alice")
# Output: "Hello Alice"
```

### 带拦截器的渲染

```python
manager = get_manager()
manager.add_interceptor(lambda t, n, p: f"[{n}]: {t}")

result = render("greeting", name="Alice")
# Output: "[greeting]: Hello Alice"
```

### 错误处理

```python
# 注册检查
if not register(prompt):
    print("Registration failed")

# 获取检查
prompt = get("name")
if prompt is None:
    print("Not found")

# 渲染检查
result = render("name")
if result is None:
    print("Rendering failed")
else:
    print(result)
```

### 参数验证

```python
prompt = TemplatePrompt("test", "{x}")
prompt.params.add_param(PromptParam("x", ParamType.STRING, required=True))

# 验证提示词定义
if not prompt.validate():
    raise ValueError("Invalid prompt")

# 验证参数值
if not prompt.params.set_value("x", "value"):
    raise ValueError("Invalid parameter value")
```

### 动态创建

```python
for i in range(5):
    p = SimplePrompt(f"prompt_{i}", f"Content {i}")
    register(p)

# 批量渲染
results = render_multiple([f"prompt_{i}" for i in range(5)])
```

## 分类和优先级枚举值

### 分类

```python
PromptCategory.SYSTEM   # "system"
PromptCategory.DOMAIN   # "domain"
PromptCategory.DIALOG   # "dialog"
PromptCategory.TASK     # "task"
PromptCategory.CUSTOM   # "custom"
```

### 优先级

```python
PromptPriority.LOW      # 1
PromptPriority.NORMAL   # 2
PromptPriority.HIGH     # 3
PromptPriority.CRITICAL # 4
```

## 提示词类型

```python
PromptType.SYSTEM      # "system"
PromptType.USER        # "user"
PromptType.ASSISTANT   # "assistant"
PromptType.CUSTOM      # "custom"
```

## 快速检查表

- [ ] 为 TemplatePrompt 定义了参数
- [ ] 为参数添加了验证器
- [ ] 验证了提示词定义
- [ ] 检查了注册结果
- [ ] 检查了渲染结果
- [ ] 使用了正确的分类和优先级
- [ ] 添加了有意义的元数据
- [ ] 使用了清晰的命名约定
- [ ] 考虑了提示词的可组合性
- [ ] 考虑了错误处理

## 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| 渲染返回 `None` | 提示词不存在 | 检查提示词名称 |
| 渲染返回 `None` | 参数验证失败 | 检查参数值类型 |
| 注册返回 `False` | 提示词已存在 | 使用不同的名称 |
| 注册返回 `False` | 验证失败 | 调用 `validate()` 检查 |
| `set_value()` 返回 `False` | 值验证失败 | 检查参数类型和验证器 |

## 相关文档

- [README.md](./README.md) - 完整使用指南
- [API_REFERENCE.md](./API_REFERENCE.md) - API 详细参考
- [BEST_PRACTICES.md](./BEST_PRACTICES.md) - 最佳实践
