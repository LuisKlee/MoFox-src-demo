# MoFox Core API

MoFox Core 层的统一对外接口，提供简洁、易用的 API 来访问核心功能。

## 📋 目录

- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [API 文档](#api-文档)
- [使用示例](#使用示例)

## 🚀 快速开始

### 基本使用

```python
from app.bot.core_api import MoFoxCore

# 创建并初始化 Core 实例
async def main():
    core = MoFoxCore(app_name="my_app")
    await core.initialize()
    
    # 使用各种功能
    # ...
    
    # 关闭
    await core.shutdown()

# 使用异步上下文管理器（推荐）
async def main():
    async with MoFoxCore(app_name="my_app") as core:
        # Core 自动初始化
        # 使用各种功能
        pass
    # Core 自动关闭
```

### 使用单例模式

```python
from app.bot.core_api import get_core, create_core

# 获取全局单例（需要手动初始化）
core = get_core()
await core.initialize()

# 或者直接创建并初始化
core = await create_core(app_name="my_app")
```

## 🎯 核心功能

### 1. 提示词系统 (Prompt)

管理和构建 AI 提示词模板。

```python
# 构建提示词
prompt = await core.prompt.build("greeting", name="张三")

# 使用便捷函数
from app.bot.core_api import build_prompt
prompt = await build_prompt("greeting", name="张三")
```

### 2. 传输系统 (Transport)

处理数据传输和通信。

```python
# 发送数据
response = await core.transport.send(data)

# 使用便捷函数
from app.bot.core_api import send_data
response = await send_data(data, transport_type="http")
```

### 3. 感知系统 (Perception)

处理输入数据的感知和理解。

```python
# 处理感知数据
result = await core.perception.process(input_data)
```

### 4. 组件系统 (Components)

管理可复用的组件。

```python
# 注册和使用组件
component = core.components.get("my_component")
```

### 5. 模型系统 (Models)

管理数据模型和模型验证。

```python
# 使用模型
model = core.models.get("user_model")
```

## 📖 API 文档

### MoFoxCore

Core 层的统一管理器类。

#### 构造函数

```python
MoFoxCore(
    app_name: str = "mofox_app",
    config: Optional[Dict[str, Any]] = None,
    **kwargs
)
```

**参数：**
- `app_name`: 应用名称
- `config`: 配置字典
- `**kwargs`: 其他配置参数

#### 方法

##### initialize()

初始化所有核心组件。

```python
await core.initialize()
```

##### shutdown()

关闭所有核心组件，释放资源。

```python
await core.shutdown()
```

#### 属性

- `prompt`: 提示词管理器
- `transport`: 传输管理器
- `perception`: 感知系统
- `components`: 组件注册表
- `models`: 模型管理器

### 便捷函数

#### get_core()

获取全局 Core 实例（单例模式）。

```python
core = get_core(app_name="my_app")
```

#### create_core()

创建并初始化新的 Core 实例。

```python
core = await create_core(app_name="my_app")
```

#### build_prompt()

构建提示词的便捷函数。

```python
prompt = await build_prompt("template_name", param1="value1")
```

#### send_data()

发送数据的便捷函数。

```python
response = await send_data(data, transport_type="default")
```

## 💡 使用示例

### 示例 1: 完整的应用流程

```python
from app.bot.core_api import MoFoxCore

async def main():
    # 使用上下文管理器
    async with MoFoxCore(app_name="chat_app") as core:
        # 构建提示词
        prompt = await core.prompt.build(
            "chat_template",
            user_message="你好",
            context="这是一个聊天场景"
        )
        
        # 发送数据（例如发送到 LLM）
        response = await core.transport.send({
            "prompt": prompt,
            "model": "gpt-4"
        })
        
        print(f"响应: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 示例 2: 使用便捷函数

```python
from app.bot.core_api import build_prompt, send_data, get_core

async def quick_chat(message: str):
    # 初始化（首次调用）
    core = get_core()
    await core.initialize()
    
    # 构建提示词
    prompt = await build_prompt("chat", message=message)
    
    # 发送数据
    response = await send_data({"prompt": prompt})
    
    return response

# 使用
response = await quick_chat("你好，MoFox！")
```

### 示例 3: 自定义配置

```python
from app.bot.core_api import MoFoxCore

config = {
    "transport": {
        "type": "http",
        "timeout": 30,
        "base_url": "https://api.example.com"
    },
    "prompt": {
        "template_dir": "./templates",
        "default_language": "zh-CN"
    }
}

async with MoFoxCore(app_name="custom_app", config=config) as core:
    # 使用自定义配置的 core
    pass
```

## 🔗 相关链接

- [Kernel API](./kernel_api_legacy/README.md) - Kernel 层 API 文档
- [Core 层文档](../../core/README.md) - Core 层详细文档
- [MoFox 重构指导](../../../MoFox%20重构指导总览.md) - 项目重构指导

## 📝 注意事项

1. **异步编程**: 所有主要方法都是异步的，需要使用 `await` 关键字
2. **资源管理**: 使用完成后记得调用 `shutdown()` 或使用上下文管理器
3. **单例模式**: `get_core()` 返回全局单例，适合在应用中共享状态
4. **错误处理**: 建议使用 try-except 捕获可能的异常

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
