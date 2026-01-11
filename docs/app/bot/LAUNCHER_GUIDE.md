# MoFox 启动器使用指南

完整的 MoFox Bot 启动器使用说明

## 📋 目录

- [快速开始](#快速开始)
- [启动方式](#启动方式)
- [命令行参数](#命令行参数)
- [配置文件](#配置文件)
- [启动流程](#启动流程)
- [使用场景](#使用场景)
- [故障排除](#故障排除)

## 快速开始

### 最简单的启动

```bash
# 确保在项目根目录
cd /path/to/MoFox-src-demo

# 方式 1: 使用启动脚本（推荐）
python start.py

# 方式 2: 使用模块方式
python -m app.bot.main

# 方式 3: 直接运行
python src/app/bot/main.py
```

### 使用虚拟环境

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python start.py

# Linux/Mac
source .venv/bin/activate
python start.py
```

## 启动方式

### 1. 使用 start.py（推荐）

**位置**: 项目根目录的 `start.py`

**优点**:
- 自动配置路径
- 简单方便
- 适合快速测试

```bash
python start.py
```

**输出示例**:
```
============================================================
  MoFox Bot - Quick Start
============================================================
🚀 正在初始化 mofox_bot...
📦 初始化 Core 层...
✅ Core 层初始化完成
📦 初始化 Kernel 层...
✅ Kernel 层初始化完成
✨ mofox_bot 初始化成功！

🤖 Bot 正在运行...
💡 提示：按 Ctrl+C 退出

欢迎使用 MoFox Bot！
输入 'quit' 或 'exit' 退出

You: 
```

### 2. 使用模块方式

**命令**: `python -m app.bot.main`

**优点**:
- Python 标准方式
- 路径管理规范
- 适合生产环境

```bash
# 基本启动
python -m app.bot.main

# 带参数启动
python -m app.bot.main --name my_bot --config config.yaml
```

### 3. 直接运行 main.py

**位置**: `src/app/bot/main.py`

**注意**: 需要确保从正确的目录运行

```bash
cd src
python app/bot/main.py
```

## 命令行参数

### 完整参数列表

```bash
python start.py [选项]

选项:
  --name NAME           应用名称（默认: mofox_bot）
  --config CONFIG       配置文件路径
  --no-core            禁用 Core 层
  --no-kernel          禁用 Kernel 层
  -h, --help           显示帮助信息
```

### 参数详解

#### --name

指定应用名称，用于日志标识和资源命名。

```bash
python start.py --name my_custom_bot
```

**使用场景**:
- 多个 Bot 实例运行时区分
- 自定义日志文件名
- 资源隔离

#### --config

指定配置文件路径。

```bash
python start.py --config configs/production.yaml
```

**支持的格式**:
- YAML (`.yaml`, `.yml`)
- JSON (`.json`)
- TOML (`.toml`)

**配置文件示例**:
```yaml
# config.yaml
app:
  name: my_bot
  version: 1.0.0

llm:
  provider: openai
  model: gpt-4
  api_key: ${OPENAI_API_KEY}

database:
  type: sqlite
  path: ./data/bot.db

logging:
  level: INFO
  dir: ./logs
```

#### --no-core

禁用 Core 层，只使用 Kernel 层功能。

```bash
python start.py --no-core
```

**使用场景**:
- 只需要基础设施功能（数据库、日志等）
- 减少启动时间
- 调试 Kernel 层功能

#### --no-kernel

禁用 Kernel 层，只使用 Core 层功能。

```bash
python start.py --no-kernel
```

**使用场景**:
- 只需要业务逻辑功能
- 轻量级运行
- 调试 Core 层功能

### 参数组合示例

```bash
# 生产环境启动
python start.py --name prod_bot --config configs/prod.yaml

# 开发环境（只启用 Core 层）
python start.py --name dev_bot --no-kernel

# 测试 Kernel 功能
python start.py --name test_kernel --no-core

# 完全自定义
python start.py \
  --name custom_bot \
  --config configs/custom.yaml
```

## 配置文件

### 配置文件结构

```yaml
# 完整配置示例
app:
  name: mofox_bot
  version: 0.1.0
  log_dir: ./logs
  data_dir: ./data

# Core 层配置
core:
  prompt:
    template_dir: ./templates
    default_language: zh-CN
  
  transport:
    timeout: 30
    retry: 3
  
  perception:
    max_input_length: 10000

# Kernel 层配置
kernel:
  config:
    env_file: .env
  
  database:
    type: sqlite
    path: ./data/mofox.db
    # 或使用 PostgreSQL
    # type: postgresql
    # host: localhost
    # port: 5432
    # database: mofox_db
    # username: postgres
    # password: ${DB_PASSWORD}
  
  llm:
    provider: openai
    model: gpt-4
    api_key: ${OPENAI_API_KEY}
    temperature: 0.7
    max_tokens: 2000
  
  logger:
    level: INFO
    format: json
    rotation: "1 day"
    retention: "7 days"
  
  storage:
    base_dir: ./data/storage
    compress: false
  
  vector_db:
    type: chromadb
    persist_dir: ./data/vectordb
  
  task_manager:
    max_workers: 10
    enable_watchdog: true
    watchdog_interval: 1.0
```

### 环境变量

创建 `.env` 文件：

```env
# .env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-xxxxxxxxxxxxx

DB_PASSWORD=your_password
REDIS_URL=redis://localhost:6379

LOG_LEVEL=DEBUG
```

### 配置优先级

1. 命令行参数（最高优先级）
2. 配置文件
3. 环境变量
4. 默认值（最低优先级）

示例：
```bash
# 命令行的 --name 会覆盖配置文件中的 app.name
python start.py --name cli_bot --config config.yaml
```

## 启动流程

### 详细流程图

```
1. 程序入口 (start.py / main.py)
   ↓
2. 解析命令行参数
   ├─ --name → 设置应用名称
   ├─ --config → 加载配置文件
   ├─ --no-core → 禁用 Core 层
   └─ --no-kernel → 禁用 Kernel 层
   ↓
3. 创建 MoFoxBot 实例
   ├─ 设置基本属性
   └─ 初始化标志设为 False
   ↓
4. 初始化阶段 (initialize)
   │
   ├─ Core 层初始化 (如果启用)
   │  ├─ 初始化提示词系统
   │  ├─ 初始化传输系统
   │  ├─ 初始化感知系统
   │  ├─ 初始化组件系统
   │  └─ 初始化模型系统
   │
   └─ Kernel 层初始化 (如果启用)
      ├─ 加载配置
      ├─ 初始化日志系统
      ├─ 连接数据库
      ├─ 启动任务管理器
      └─ 启动 Watchdog 监控
   ↓
5. 运行阶段 (run)
   ├─ 进入主循环 (_main_loop)
   ├─ 等待用户输入
   ├─ 处理输入 (_process_input)
   ├─ 生成响应
   └─ 输出结果
   ↓
6. 关闭阶段 (shutdown)
   ├─ 停止任务管理器
   ├─ 关闭数据库连接
   ├─ 刷新日志缓冲
   ├─ 关闭 Core 层
   └─ 清理所有资源
   ↓
7. 程序退出
```

### 启动日志解读

```
🚀 正在初始化 mofox_bot...
   └─ 开始初始化过程

📦 初始化 Core 层...
   ├─ 提示词系统初始化...
   ├─ 传输系统初始化...
   └─ 其他 Core 组件...

✅ Core 层初始化完成
   └─ Core 层所有组件就绪

📦 初始化 Kernel 层...
   ├─ [INFO] Logger system initialized
   ├─ [Watchdog] 监控器已启动
   └─ [INFO] TaskManager 已启动

✅ Kernel 层初始化完成
   └─ Kernel 层所有组件就绪

✨ mofox_bot 初始化成功！
   └─ 应用完全就绪

🤖 Bot 正在运行...
💡 提示：按 Ctrl+C 退出
   └─ 进入主循环，等待用户交互
```

## 使用场景

### 场景 1: 开发调试

```bash
# 启动开发模式
python start.py --name dev_bot --config configs/dev.yaml

# 只测试 Core 层
python start.py --no-kernel

# 只测试 Kernel 层
python start.py --no-core
```

### 场景 2: 生产运行

```bash
# 使用生产配置
python start.py --name prod_bot --config configs/production.yaml

# 使用环境变量
export OPENAI_API_KEY=sk-xxxxx
export LOG_LEVEL=WARNING
python start.py --config configs/production.yaml
```

### 场景 3: 多实例运行

```bash
# 实例 1: 客服 Bot
python start.py --name customer_service_bot --config configs/cs.yaml &

# 实例 2: 分析 Bot
python start.py --name analysis_bot --config configs/analysis.yaml &

# 实例 3: 监控 Bot
python start.py --name monitor_bot --config configs/monitor.yaml &
```

### 场景 4: 容器化部署

```dockerfile
# Dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "start.py", "--config", "configs/docker.yaml"]
```

```bash
# 构建镜像
docker build -t mofox-bot .

# 运行容器
docker run -d \
  --name mofox-bot \
  -e OPENAI_API_KEY=sk-xxxxx \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  mofox-bot
```

### 场景 5: 后台运行

```bash
# Linux/Mac
nohup python start.py --config configs/prod.yaml > output.log 2>&1 &

# 查看进程
ps aux | grep start.py

# 停止
kill <pid>
```

```powershell
# Windows PowerShell
Start-Process python -ArgumentList "start.py --config configs/prod.yaml" -WindowStyle Hidden
```

## 交互命令

### 内置命令

启动后，可以在 `You:` 提示符输入以下命令：

```
quit / exit / q    - 退出程序
help              - 显示帮助（计划中）
status            - 显示状态（计划中）
stats             - 显示统计信息（计划中）
config            - 显示配置（计划中）
```

### 使用示例

```
You: 你好
Bot: 收到消息：你好

You: 今天天气怎么样？
Bot: 收到消息：今天天气怎么样？

You: quit
[正在关闭...]
```

## 故障排除

### 问题 1: 导入错误

**错误信息**:
```
ModuleNotFoundError: No module named 'app'
```

**解决方法**:
```bash
# 确保从项目根目录运行
cd /path/to/MoFox-src-demo
python start.py

# 或使用模块方式
python -m app.bot.main
```

### 问题 2: 缺少依赖

**错误信息**:
```
ModuleNotFoundError: No module named 'PIL'
```

**解决方法**:
```bash
# 安装所有依赖
pip install -r requirements.txt

# 或安装特定包
pip install Pillow boto3
```

### 问题 3: 配置文件未找到

**错误信息**:
```
FileNotFoundError: config.yaml
```

**解决方法**:
```bash
# 使用绝对路径
python start.py --config /full/path/to/config.yaml

# 或使用相对路径（相对于运行目录）
python start.py --config ./configs/config.yaml
```

### 问题 4: API 密钥未设置

**错误信息**:
```
OpenAI API key not found
```

**解决方法**:
```bash
# 方式 1: 环境变量
export OPENAI_API_KEY=sk-xxxxx
python start.py

# 方式 2: .env 文件
echo "OPENAI_API_KEY=sk-xxxxx" > .env
python start.py

# 方式 3: 配置文件
# config.yaml
llm:
  api_key: sk-xxxxx
```

### 问题 5: 端口被占用

**错误信息**:
```
Address already in use: 8080
```

**解决方法**:
```bash
# 查找占用端口的进程
# Linux/Mac
lsof -i :8080

# Windows
netstat -ano | findstr :8080

# 停止进程或使用其他端口
python start.py --port 8081
```

### 问题 6: 权限错误

**错误信息**:
```
PermissionError: [Errno 13] Permission denied: './logs'
```

**解决方法**:
```bash
# 创建目录
mkdir -p logs data

# 设置权限
chmod 755 logs data

# 或更改输出目录
python start.py --config config.yaml  # 在配置中指定可写目录
```

### 问题 7: 内存不足

**症状**: 程序运行缓慢或崩溃

**解决方法**:
```yaml
# 调整配置
kernel:
  task_manager:
    max_workers: 5  # 减少并发数
  
  vector_db:
    batch_size: 100  # 减少批处理大小
```

### 问题 8: 日志错误

**错误信息**:
```
--- Logging error ---
TypeError: LogMetadata.get_custom() missing 1 required positional argument
```

**说明**: 这是一个已知的非致命警告，不影响功能

**临时解决**: 可以忽略，或等待下一版本修复

## 高级用法

### 自定义启动脚本

```python
# my_start.py
import asyncio
from app.bot.main import MoFoxBot

async def main():
    # 自定义配置
    config = {
        "llm": {"model": "gpt-4"},
        "logging": {"level": "DEBUG"}
    }
    
    # 创建并运行
    async with MoFoxBot(
        app_name="custom_bot",
        config=config
    ) as bot:
        # 自定义启动逻辑
        print("自定义启动完成")
        await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### 程序化控制

```python
# 不使用命令行界面
async def automated_bot():
    bot = MoFoxBot(app_name="auto_bot")
    await bot.initialize()
    
    # 处理预定义的任务
    tasks = ["任务1", "任务2", "任务3"]
    for task in tasks:
        result = await bot._process_input(task)
        print(f"完成: {result}")
    
    await bot.shutdown()
```

## 监控和维护

### 查看日志

```bash
# 实时查看日志
tail -f logs/mofox_bot.log

# 搜索错误
grep ERROR logs/mofox_bot.log

# 查看最近100条
tail -n 100 logs/mofox_bot.log
```

### 性能监控

```python
# 在代码中添加监控
bot.kernel.logger.info("性能指标", extra={
    "cpu_usage": cpu_percent(),
    "memory_usage": memory_percent(),
    "active_tasks": len(bot.kernel.task_manager.tasks)
})
```

### 健康检查

```python
# health_check.py
async def check_health():
    bot = MoFoxBot()
    await bot.initialize()
    
    checks = {
        "core": bot.core is not None,
        "kernel": bot.kernel is not None,
        "database": await bot.kernel.db.ping(),
        "llm": await bot.kernel.llm.test_connection()
    }
    
    return all(checks.values())
```

## 下一步

- 阅读 [API 使用指南](API_GUIDE.md) 了解如何使用 API
- 查看 [开发指南](DEVELOPMENT_GUIDE.md) 学习如何扩展功能
- 参考 [部署指南](DEPLOYMENT_GUIDE.md) 了解生产部署

## 更新日志

- 2026-01-11: 初始版本，完成启动器基础文档
