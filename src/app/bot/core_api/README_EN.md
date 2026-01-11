# MoFox Core API

Unified external interface for MoFox Core layer, providing clean and easy-to-use APIs to access core functionalities.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Core Features](#core-features)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)

## 🚀 Quick Start

### Basic Usage

```python
from app.bot.core_api import MoFoxCore

# Create and initialize Core instance
async def main():
    core = MoFoxCore(app_name="my_app")
    await core.initialize()
    
    # Use various features
    # ...
    
    # Shutdown
    await core.shutdown()

# Use async context manager (recommended)
async def main():
    async with MoFoxCore(app_name="my_app") as core:
        # Core auto-initialized
        # Use various features
        pass
    # Core auto-shutdown
```

### Using Singleton Pattern

```python
from app.bot.core_api import get_core, create_core

# Get global singleton (requires manual initialization)
core = get_core()
await core.initialize()

# Or create and initialize directly
core = await create_core(app_name="my_app")
```

## 🎯 Core Features

### 1. Prompt System

Manage and build AI prompt templates.

```python
# Build prompt
prompt = await core.prompt.build("greeting", name="John")

# Use convenience function
from app.bot.core_api import build_prompt
prompt = await build_prompt("greeting", name="John")
```

### 2. Transport System

Handle data transmission and communication.

```python
# Send data
response = await core.transport.send(data)

# Use convenience function
from app.bot.core_api import send_data
response = await send_data(data, transport_type="http")
```

### 3. Perception System

Process perception and understanding of input data.

```python
# Process perception data
result = await core.perception.process(input_data)
```

### 4. Component System

Manage reusable components.

```python
# Register and use components
component = core.components.get("my_component")
```

### 5. Model System

Manage data models and model validation.

```python
# Use models
model = core.models.get("user_model")
```

## 📖 API Documentation

### MoFoxCore

The unified manager class for Core layer.

#### Constructor

```python
MoFoxCore(
    app_name: str = "mofox_app",
    config: Optional[Dict[str, Any]] = None,
    **kwargs
)
```

**Parameters:**
- `app_name`: Application name
- `config`: Configuration dictionary
- `**kwargs`: Other configuration parameters

#### Methods

##### initialize()

Initialize all core components.

```python
await core.initialize()
```

##### shutdown()

Shutdown all core components and release resources.

```python
await core.shutdown()
```

#### Properties

- `prompt`: Prompt manager
- `transport`: Transport manager
- `perception`: Perception system
- `components`: Component registry
- `models`: Model manager

### Convenience Functions

#### get_core()

Get global Core instance (singleton pattern).

```python
core = get_core(app_name="my_app")
```

#### create_core()

Create and initialize a new Core instance.

```python
core = await create_core(app_name="my_app")
```

#### build_prompt()

Convenience function for building prompts.

```python
prompt = await build_prompt("template_name", param1="value1")
```

#### send_data()

Convenience function for sending data.

```python
response = await send_data(data, transport_type="default")
```

## 💡 Usage Examples

### Example 1: Complete Application Flow

```python
from app.bot.core_api import MoFoxCore

async def main():
    # Use context manager
    async with MoFoxCore(app_name="chat_app") as core:
        # Build prompt
        prompt = await core.prompt.build(
            "chat_template",
            user_message="Hello",
            context="This is a chat scenario"
        )
        
        # Send data (e.g., to LLM)
        response = await core.transport.send({
            "prompt": prompt,
            "model": "gpt-4"
        })
        
        print(f"Response: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Example 2: Using Convenience Functions

```python
from app.bot.core_api import build_prompt, send_data, get_core

async def quick_chat(message: str):
    # Initialize (first call)
    core = get_core()
    await core.initialize()
    
    # Build prompt
    prompt = await build_prompt("chat", message=message)
    
    # Send data
    response = await send_data({"prompt": prompt})
    
    return response

# Usage
response = await quick_chat("Hello, MoFox!")
```

### Example 3: Custom Configuration

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
        "default_language": "en-US"
    }
}

async with MoFoxCore(app_name="custom_app", config=config) as core:
    # Use core with custom configuration
    pass
```

## 🔗 Related Links

- [Kernel API](./kernel_api_legacy/README.md) - Kernel Layer API Documentation
- [Core Layer Documentation](../../core/README.md) - Detailed Core Layer Documentation
- [MoFox Refactoring Guide](../../../MoFox%20重构指导总览.md) - Project Refactoring Guide

## 📝 Notes

1. **Asynchronous Programming**: All main methods are asynchronous and require the `await` keyword
2. **Resource Management**: Remember to call `shutdown()` after use or use context manager
3. **Singleton Pattern**: `get_core()` returns a global singleton, suitable for sharing state across the application
4. **Error Handling**: It's recommended to use try-except to catch possible exceptions

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License
