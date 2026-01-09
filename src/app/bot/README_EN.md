# MoFox Kernel API Documentation

[中文文档](README.md) | English

## Overview

`kernel_api.py` provides a unified high-level wrapper interface for the MoFox Kernel layer, integrating all core functionalities (configuration, logging, database, LLM, storage, vector database, task management) into a simple and easy-to-use API.

## Core Features

✅ **Unified Interface** - One class to manage all Kernel functions  
✅ **Auto Initialization** - Smart initialization of sub-modules  
✅ **Resource Management** - Automatic lifecycle and resource cleanup  
✅ **Clean API** - High-level convenience methods  
✅ **Type Hints** - Full type annotation support  
✅ **Async First** - Native async/await support  
✅ **Video Processing** - Integrated inkfox high-performance video keyframe extraction (Rust accelerated)  

## Quick Start

### Basic Usage

```python
from src.app.bot.kernel_api import init_kernel, shutdown_kernel

async def main():
    # Initialize kernel
    kernel = await init_kernel(
        app_name="my_app",
        log_dir="logs",
        data_dir="data"
    )
    
    # Use logger
    kernel.logger.info("Application started")
    
    # Use configuration
    kernel.set_config("debug", True)
    debug = kernel.get_config("debug")
    
    # Shutdown kernel
    await shutdown_kernel()

import asyncio
asyncio.run(main())
```

### Complete Example

```python
from src.app.bot.kernel_api import MoFoxKernel

async def main():
    # Create kernel instance
    kernel = MoFoxKernel(
        app_name="advanced_app",
        config_path="config.json",  # Optional
        log_dir="logs",
        data_dir="data",
        max_concurrent_tasks=20  # Other configurations
    )
    
    # Initialize all components
    await kernel.initialize()
    
    try:
        # Your application logic
        kernel.logger.info("Application running...")
        
    finally:
        # Cleanup resources
        await kernel.shutdown()

asyncio.run(main())
```

## Functional Modules

### 1. Configuration Management

```python
# Set configuration
kernel.set_config("api_key", "your-key")
kernel.set_config("database.host", "localhost")

# Get configuration
api_key = kernel.get_config("api_key")
host = kernel.get_config("database.host", "default_host")

# Access underlying config object
config = kernel.config
value = config.get("nested.key.path")
```

### 2. Logging Management

```python
# Get default logger
kernel.logger.info("Info log")
kernel.logger.warning("Warning log")
kernel.logger.error("Error log")
```

### 3. LLM and Video Processing

#### Basic Chat
```python
# Simple conversation
response = await kernel.llm.chat(
    message="Hello, introduce yourself",
    model="gpt-4",
    system_prompt="You are a friendly assistant"
)
print(response)

# Streaming conversation
async for chunk in kernel.llm.chat_stream(
    message="Tell me a story",
    model="gpt-4"
):
    print(chunk, end="", flush=True)
```

#### Video Keyframe Extraction (inkfox)

**Note**: Requires inkfox and FFmpeg
```bash
pip install inkfox  # Python >= 3.11
```

```python
# Check video processing support
if kernel.llm.check_video_support():
    print("✅ inkfox video processing available")
else:
    print("❌ inkfox not available, please install")

# Quick keyframe extraction
result = kernel.llm.extract_video_keyframes(
    video_path="video.mp4",
    output_dir="./keyframes",
    max_keyframes=10,
    use_simd=True  # SIMD acceleration
)

print(f"Extracted {result['keyframes_extracted']} keyframes")
print(f"Total frames: {result['total_frames']}")
print(f"Processing speed: {result['processing_fps']:.2f} FPS")
print(f"Time taken: {result['total_time_ms']:.2f}ms")

# Advanced usage: Create extractor instance
extractor = kernel.llm.create_video_extractor(
    threads=4,
    verbose=True
)

# Get CPU features
cpu_features = extractor.get_cpu_features()
print(f"CPU features: {cpu_features}")

# Extract keyframes
result = extractor.extract_keyframes(
    video_path="video.mp4",
    output_dir="./output",
    max_keyframes=20,
    use_simd=True
)

# Performance benchmark
benchmark = extractor.benchmark(
    video_path="video.mp4",
    max_keyframes=10,
    test_name="Performance Test"
)
print(f"Performance: {benchmark['processing_fps']:.2f} FPS")

# Get named logger
module_logger = kernel.get_logger("app.module")
module_logger.debug("Module log")

# Query log statistics
stats = kernel.get_logs(days=7)
# {'total': 100, 'by_level': {...}, 'by_logger': {...}}

# Query error logs
errors = kernel.get_error_logs(days=1)
for error in errors:
    print(f"{error['timestamp']}: {error['message']}")
```

### 3. LLM Features

```python
# Simple chat
response = await kernel.llm.chat(
    "Introduce Python in one sentence",
    model="gpt-4",
    provider="openai"
)
print(response)

# Streaming chat
async for chunk in kernel.llm.chat_stream(
    "Tell me a story",
    model="gpt-4"
):
    print(chunk, end="", flush=True)

# Use system prompt
system_prompt = kernel.llm.get_system_prompt("coding")
response = await kernel.llm.chat(
    "How to read a file?",
    system_prompt=system_prompt
)

# Tool calling
tool = kernel.llm.create_tool(
    name="get_weather",
    description="Get weather information",
    parameters=[
        {
            "name": "city",
            "type": "string",
            "description": "City name",
            "required": True
        }
    ]
)

response = await kernel.llm.chat_with_tools(
    "What's the weather in Beijing?",
    tools=[tool]
)

if response.tool_calls:
    for call in response.tool_calls:
        print(f"Tool called: {call['function']['name']}")
        print(f"Arguments: {call['function']['arguments']}")

# Create multimodal message
message = kernel.llm.create_message(
    "What is this?",
    images=["image.jpg"]
)
```

### 4. Database Operations

```python
# Initialize database
await kernel.init_database(
    db_path="data/app.db",
    enable_wal=True,
    pool_size=20
)

# Use session
async with kernel.db_session() as session:
    # CRUD operations
    user = User(name="Alice", age=25)
    kernel.db.add(session, user, flush=True)
    
    # Query
    users = kernel.db.list(session, User)
    user = kernel.db.get(session, User, user_id)
    
    # Update
    kernel.db.update_fields(session, user, {"age": 26})
    
    # Delete
    kernel.db.delete(session, user)

# Direct access to database repository
repo = kernel.db
```

### 5. Storage Operations

```python
# Quick save/load
kernel.storage.save("config", {"version": "1.0"})
config = kernel.storage.load("config", default={})

# JSON storage
json_store = kernel.storage.json_store("settings")
json_store.write({"key": "value"})
data = json_store.read()

# Dictionary storage
dict_store = kernel.storage.dict_store("users")
dict_store.set("user1", {"name": "Alice"})
dict_store.set("user2", {"name": "Bob"})
user = dict_store.get("user1")
all_users = dict_store.to_dict()

# List storage
list_store = kernel.storage.list_store("events")
list_store.append({"type": "login", "user": "Alice"})
list_store.extend([event1, event2])
events = list_store.to_list()
count = list_store.count()

# Log storage
log_store = kernel.storage.log_store("app_logs")
log_store.log("info", "Application started")
log_store.log("error", "Error occurred", {"code": 500})
logs = log_store.get_logs()
```

### 6. Vector Database

```python
# Initialize vector database
await kernel.init_vector_db(
    db_type="chromadb",
    persist_dir="data/vectors"
)

# Create collection
await kernel.vector_db.create_collection("documents")

# Add documents
from src.app.bot.kernel_api import VectorDocument

docs = [
    VectorDocument(
        id="doc1",
        content="Python programming language",
        vector=[0.1, 0.2, 0.3],
        metadata={"category": "tech"}
    )
]
await kernel.vector_db.add_documents("documents", docs)

# Vector search (using vector)
results = await kernel.vector_search(
    collection="documents",
    query=[0.15, 0.25, 0.35],
    top_k=5
)

# Text search (requires embedding function)
results = await kernel.vector_search(
    collection="documents",
    query="Python programming",
    top_k=5
)

# Manage collections
collections = await kernel.vector_db.list_collections()
exists = await kernel.vector_db.collection_exists("documents")
count = await kernel.vector_db.count_documents("documents")
await kernel.vector_db.delete_collection("documents")
```

### 7. Task Management

```python
# Define async task
async def process_data(data):
    await asyncio.sleep(1)
    return data * 2

# Run single task
result = await kernel.run_task(
    process_data,
    42,
    priority=TaskPriority.HIGH,
    name="process_task"
)

# Run multiple tasks in parallel
tasks = [
    (process_data, (10,)),
    (process_data, (20,)),
    (process_data, (30,))
]
results = await kernel.run_tasks_parallel(tasks)
# [20, 40, 60]

# Use task manager
task_id = kernel.tasks.submit_task(
    process_data,
    100,
    name="my_task",
    config=TaskConfig(priority=TaskPriority.HIGH)
)

# Wait for task completion
result = await kernel.tasks.wait_for_task(task_id)

# Query task status
status = kernel.tasks.get_task_status(task_id)

# Cancel task
kernel.tasks.cancel_task(task_id)

# Get all tasks
all_tasks = kernel.tasks.get_all_tasks()
```

## Advanced Usage

### Context Managers

```python
from src.app.bot.kernel_api import MoFoxKernel

async def main():
    kernel = MoFoxKernel(app_name="context_app")
    await kernel.initialize()
    
    try:
        # Database session
        async with kernel.db_session() as session:
            # Database operations
            pass
        
        # Log metadata context
        from src.app.bot.kernel_api import MetadataContext
        with MetadataContext(user_id="123", request_id="req_456"):
            kernel.logger.info("Log with metadata")
    
    finally:
        await kernel.shutdown()
```

### Combined Usage

```python
async def intelligent_qa_system():
    """Intelligent Q&A system example"""
    kernel = await init_kernel(app_name="qa_system")
    
    # Initialize all components
    await kernel.init_database("data/qa.db")
    await kernel.init_vector_db(persist_dir="data/vectors")
    
    # 1. Store Q&A knowledge base
    qa_store = kernel.storage.dict_store("knowledge")
    qa_store.set("python", {
        "question": "What is Python?",
        "answer": "Python is a programming language"
    })
    
    # 2. Store knowledge in vector database (for semantic search)
    await kernel.vector_db.create_collection("qa_vectors")
    doc = VectorDocument(
        id="q1",
        content="What is Python? Python is a programming language",
        vector=[0.1, 0.2, 0.3],  # Should use embedding model in practice
        metadata={"type": "qa"}
    )
    await kernel.vector_db.add_documents("qa_vectors", [doc])
    
    # 3. User question
    user_question = "What is Python?"
    kernel.logger.info(f"User question: {user_question}")
    
    # 4. Semantic search for relevant questions
    similar_docs = await kernel.vector_search(
        collection="qa_vectors",
        query=user_question,  # Or use embedding vector
        top_k=3
    )
    
    # 5. Generate answer using LLM
    context = "\n".join([doc.content for doc in similar_docs])
    prompt = f"Answer based on context:\n{context}\n\nQuestion: {user_question}"
    
    answer = await kernel.llm.chat(
        prompt,
        system_prompt=kernel.llm.get_system_prompt("education")
    )
    
    # 6. Record Q&A history
    history = kernel.storage.list_store("qa_history")
    history.append({
        "question": user_question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    })
    
    kernel.logger.info(f"Answer: {answer}")
    
    await shutdown_kernel()
    return answer
```

### Concurrent Task Processing

```python
async def batch_processing():
    """Batch data processing example"""
    kernel = await init_kernel(app_name="batch_processor")
    
    # Define processing task
    async def process_item(item_id):
        # Get data from storage
        store = kernel.storage.dict_store("items")
        item = store.get(item_id)
        
        # Process using LLM
        result = await kernel.llm.chat(
            f"Analyze this data: {item}",
            model="gpt-4"
        )
        
        # Save result
        result_store = kernel.storage.dict_store("results")
        result_store.set(item_id, result)
        
        kernel.logger.info(f"Processing completed: {item_id}")
        return result
    
    # Batch parallel processing
    item_ids = [f"item_{i}" for i in range(10)]
    tasks = [(process_item, (item_id,)) for item_id in item_ids]
    
    results = await kernel.run_tasks_parallel(tasks)
    
    kernel.logger.info(f"Batch processing completed, total {len(results)} items")
    
    await shutdown_kernel()
```

## API Reference

### MoFoxKernel Class

| Method/Property | Description |
|-----------------|-------------|
| `__init__(app_name, config_path, log_dir, data_dir, **kwargs)` | Create Kernel instance |
| `async initialize()` | Initialize all components |
| `async shutdown()` | Shutdown and cleanup resources |
| `config` | Configuration manager |
| `logger` | Default logger |
| `llm` | LLM interface |
| `storage` | Storage interface |
| `db` | Database repository |
| `vector_db` | Vector database |
| `tasks` | Task manager |

### Convenience Functions

| Function | Description |
|----------|-------------|
| `get_kernel(app_name, **kwargs)` | Get global Kernel singleton |
| `init_kernel(app_name, **kwargs)` | Initialize and get global Kernel |
| `shutdown_kernel()` | Shutdown global Kernel |

## Configuration Options

### Kernel Initialization Parameters

```python
kernel = MoFoxKernel(
    app_name="my_app",              # Application name
    config_path="config.json",      # Config file path (optional)
    log_dir="logs",                 # Log directory
    data_dir="data",                # Data directory
    max_concurrent_tasks=10,        # Max concurrent tasks
    # Other custom configurations...
)
```

### Database Initialization Parameters

```python
await kernel.init_database(
    db_path="data/app.db",          # Database path
    pool_size=20,                   # Connection pool size
    pool_timeout=60,                # Timeout
    enable_wal=True,                # WAL mode
    enable_foreign_keys=True        # Foreign key constraints
)
```

### Vector Database Initialization Parameters

```python
await kernel.init_vector_db(
    db_type="chromadb",             # Database type
    persist_dir="data/vectors",     # Persistence directory
    # Other database-specific parameters...
)
```

## Best Practices

### 1. Resource Management

```python
# ✅ Recommended: Use init_kernel and shutdown_kernel
async def main():
    kernel = await init_kernel("my_app")
    try:
        # Application logic
        pass
    finally:
        await shutdown_kernel()

# ✅ Recommended: Explicit initialization and shutdown
async def main():
    kernel = MoFoxKernel("my_app")
    await kernel.initialize()
    try:
        # Application logic
        pass
    finally:
        await kernel.shutdown()
```

### 2. Logging

```python
# ✅ Recommended: Use different loggers for different modules
class MyModule:
    def __init__(self, kernel):
        self.logger = kernel.get_logger("app.mymodule")
    
    async def process(self):
        self.logger.info("Processing started")
        # ...
        self.logger.info("Processing completed")
```

### 3. Error Handling

```python
# ✅ Recommended: Use try-except for exception handling
try:
    result = await kernel.llm.chat("question")
except Exception as e:
    kernel.logger.error(f"LLM call failed: {e}")
    # Fallback handling
```

### 4. Storage Organization

```python
# ✅ Recommended: Use different stores for different data types
config_store = kernel.storage.dict_store("config")
users_store = kernel.storage.dict_store("users")
events_store = kernel.storage.list_store("events")
logs_store = kernel.storage.log_store("app_logs")
```

## FAQ

### Q: How to configure LLM API keys?

```python
# Method 1: Environment variable
import os
os.environ["OPENAI_API_KEY"] = "your-key"

# Method 2: Configuration file
kernel.set_config("openai.api_key", "your-key")

# Method 3: Direct passing
response = await kernel.llm.chat(
    "question",
    api_key="your-key"
)
```

### Q: How to handle concurrency limits?

```python
# Set max concurrent tasks
kernel = MoFoxKernel(
    app_name="my_app",
    max_concurrent_tasks=5  # Max 5 concurrent tasks
)
```

### Q: How to persist vector database?

```python
# Use persist_dir parameter
await kernel.init_vector_db(
    db_type="chromadb",
    persist_dir="data/persistent_vectors"
)
```

### Q: How to check task execution status?

```python
# Submit task
task_id = kernel.tasks.submit_task(my_func, arg)

# Check status
status = kernel.tasks.get_task_status(task_id)
print(f"Status: {status.state}")  # PENDING, RUNNING, COMPLETED, FAILED

# Get all tasks
all_tasks = kernel.tasks.get_all_tasks()
for task in all_tasks:
    print(f"{task.name}: {task.state}")
```

### Q: How to use video processing features?

```python
# Check support
if not kernel.llm.check_video_support():
    print("Please install inkfox: pip install inkfox")
    return

# Extract keyframes
result = kernel.llm.extract_video_keyframes(
    video_path="video.mp4",
    output_dir="./keyframes",
    max_keyframes=10,
    use_simd=True  # SIMD acceleration
)

print(f"Extracted {result['keyframes_extracted']} keyframes")
print(f"Processing speed: {result['processing_fps']:.2f} FPS")

# Note: Requires Python >= 3.11 and FFmpeg
```

### Q: How to combine LLM with video analysis?

```python
# 1. Extract keyframes
result = kernel.llm.extract_video_keyframes(
    video_path="video.mp4",
    output_dir="./keyframes",
    max_keyframes=5
)

# 2. Convert keyframes to Base64 (using image tools from kernel.llm)
from kernel.llm import image_to_base64
from pathlib import Path

keyframe_files = sorted(Path("./keyframes").glob("keyframe_*.jpg"))
image_urls = []
for frame in keyframe_files[:3]:  # Take first 3
    base64_str = image_to_base64(str(frame), compress=True)
    image_urls.append(f"data:image/jpeg;base64,{base64_str}")

# 3. Send to vision LLM for analysis
response = await kernel.llm.chat(
    message="Please analyze these video keyframes and describe the main content and scenes",
    model="gpt-4-vision",
    images=image_urls  # Multimodal input
)
print(response)
```

## Example Code

See complete examples at: [examples/kernel_api_demo.py](../../examples/kernel_api_demo.py)

## Related Documentation

- [Config Module](../../docs/kernel/config/README.md)
- [Database Module](../../docs/kernel/db/README.md)
- [LLM Module](../../docs/kernel/llm/README.md)
- [inkfox Video Processing Integration](../../docs/kernel/llm/INKFOX_INTEGRATION.md) ✨
- [Logger Module](../../docs/kernel/logger/README.md)
- [Storage Module](../../docs/kernel/storage/README.md)
- [Vector DB Module](../../docs/kernel/vector_db/README.md)
- [Concurrency Module](../../docs/kernel/concurrency/README.md)

## Contributing

Issues and Pull Requests are welcome!
