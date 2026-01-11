# MoFox Bot 架构设计

## 📋 目录

- [概述](#概述)
- [系统架构](#系统架构)
- [分层设计](#分层设计)
- [组件说明](#组件说明)
- [数据流](#数据流)
- [设计原则](#设计原则)

## 概述

MoFox Bot 是一个多层架构的智能机器人应用，采用模块化设计，提供灵活、可扩展的 AI 能力。

### 设计目标

1. **模块化**: 各层职责清晰，相互独立
2. **可扩展**: 易于添加新功能和集成新服务
3. **易用性**: 提供简洁的 API 和启动器
4. **可靠性**: 完善的错误处理和资源管理
5. **高性能**: 异步设计，支持并发处理

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                     Application Layer                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │              MoFox Bot (启动器)                  │   │
│  │  ┌─────────────────┐  ┌──────────────────────┐ │   │
│  │  │   命令行界面    │  │   业务逻辑处理        │ │   │
│  │  └─────────────────┘  └──────────────────────┘ │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                        API Layer                         │
│  ┌──────────────────┐         ┌──────────────────────┐ │
│  │   Core API       │         │   Kernel API         │ │
│  │  ┌────────────┐  │         │  ┌───────────────┐  │ │
│  │  │ MoFoxCore  │  │         │  │  MoFoxKernel  │  │ │
│  │  └────────────┘  │         │  └───────────────┘  │ │
│  └──────────────────┘         └──────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                     Core & Kernel Layer                  │
│  ┌──────────────────┐         ┌──────────────────────┐ │
│  │   Core Layer     │         │   Kernel Layer       │ │
│  │  • Prompt        │         │  • Config            │ │
│  │  • Transport     │         │  • Database          │ │
│  │  • Perception    │         │  • LLM               │ │
│  │  • Components    │         │  • Logger            │ │
│  │  • Models        │         │  • Storage           │ │
│  │                  │         │  • Vector DB         │ │
│  │                  │         │  • Task Manager      │ │
│  └──────────────────┘         └──────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 分层设计

### 1. Application Layer (应用层)

**职责**: 提供用户交互界面和业务流程控制

**主要组件**:
- `MoFoxBot`: 主应用类，整合所有功能
- 启动器 (`start.py`): 快速启动入口
- 命令行界面: 交互式用户界面

**特点**:
- 处理用户输入输出
- 控制应用生命周期
- 协调 Core 和 Kernel 层的调用

### 2. API Layer (接口层)

**职责**: 提供统一、简洁的 API 接口

#### 2.1 Core API

**模块**: `app.bot.core_api`

**提供功能**:
```python
class MoFoxCore:
    @property
    def prompt        # 提示词系统
    @property
    def transport     # 传输系统
    @property
    def perception    # 感知系统
    @property
    def components    # 组件系统
    @property
    def models        # 模型系统
```

**使用场景**:
- 构建和管理 AI 提示词
- 处理数据传输和通信
- 处理多模态输入（文本、图像、音频等）
- 管理可复用组件
- 数据模型验证

#### 2.2 Kernel API

**模块**: `app.bot.kernel_api_legacy`

**提供功能**:
```python
class MoFoxKernel:
    @property
    def config        # 配置管理
    @property
    def db            # 数据库访问
    @property
    def llm           # LLM 接口
    @property
    def logger        # 日志系统
    @property
    def storage       # 存储系统
    @property
    def vector_db     # 向量数据库
    @property
    def task_manager  # 任务管理
```

**使用场景**:
- 配置管理和环境变量
- 数据库 CRUD 操作
- LLM 模型调用
- 结构化日志记录
- 文件和数据存储
- 向量数据库操作
- 异步任务管理

### 3. Core & Kernel Layer (核心层)

**职责**: 实现具体的功能模块

**Core Layer 模块**:
- `core.prompt`: 提示词模板和构建
- `core.transport`: 网络传输和通信
- `core.perception`: 感知和理解
- `core.components`: 组件注册和管理
- `core.models`: 数据模型定义

**Kernel Layer 模块**:
- `kernel.config`: 配置文件解析
- `kernel.db`: 数据库引擎和操作
- `kernel.llm`: LLM 客户端封装
- `kernel.logger`: 日志处理器
- `kernel.storage`: 存储抽象层
- `kernel.vector_db`: 向量数据库接口
- `kernel.concurrency`: 任务和并发管理

## 组件说明

### MoFoxBot (主应用)

```python
class MoFoxBot:
    """Bot 主应用类"""
    
    # 核心属性
    core: MoFoxCore           # Core API 实例
    kernel: MoFoxKernel       # Kernel API 实例
    
    # 生命周期方法
    async def initialize()    # 初始化所有组件
    async def run()           # 运行主循环
    async def shutdown()      # 关闭和清理
    
    # 业务方法
    async def _process_input() # 处理用户输入
    async def _main_loop()     # 主业务循环
```

### 启动流程

```
1. start.py 入口
   ↓
2. 创建 MoFoxBot 实例
   ↓
3. 初始化阶段
   ├─ 初始化 Core 层
   │  ├─ 提示词系统
   │  ├─ 传输系统
   │  ├─ 感知系统
   │  ├─ 组件系统
   │  └─ 模型系统
   │
   └─ 初始化 Kernel 层
      ├─ 配置管理器
      ├─ 日志系统
      ├─ 数据库连接
      ├─ 任务管理器
      └─ 监控系统
   ↓
4. 运行主循环
   ├─ 等待用户输入
   ├─ 处理输入
   ├─ 生成响应
   └─ 输出结果
   ↓
5. 关闭阶段
   ├─ 停止任务管理器
   ├─ 关闭数据库连接
   ├─ 刷新日志缓冲
   └─ 清理资源
```

## 数据流

### 用户请求处理流程

```
用户输入
   ↓
MoFoxBot._process_input()
   ↓
┌─────────────────────────┐
│   预处理和验证          │
└─────────────────────────┘
   ↓
┌─────────────────────────┐
│   Core.perception       │  感知和理解输入
└─────────────────────────┘
   ↓
┌─────────────────────────┐
│   Core.prompt           │  构建提示词
└─────────────────────────┘
   ↓
┌─────────────────────────┐
│   Kernel.llm            │  调用 LLM 生成
└─────────────────────────┘
   ↓
┌─────────────────────────┐
│   Kernel.logger         │  记录日志
└─────────────────────────┘
   ↓
┌─────────────────────────┐
│   Kernel.storage        │  保存历史（可选）
└─────────────────────────┘
   ↓
返回响应给用户
```

### 异步任务处理流程

```
提交任务
   ↓
Kernel.task_manager.create_task()
   ↓
┌─────────────────────────┐
│   任务队列              │
└─────────────────────────┘
   ↓
┌─────────────────────────┐
│   任务调度器            │
└─────────────────────────┘
   ↓
┌─────────────────────────┐
│   执行任务              │
│   • 并发控制            │
│   • 优先级管理          │
│   • 超时控制            │
└─────────────────────────┘
   ↓
┌─────────────────────────┐
│   Watchdog 监控         │
│   • 健康检查            │
│   • 死锁检测            │
└─────────────────────────┘
   ↓
任务完成
   ↓
记录结果和日志
```

## 设计原则

### 1. 单一职责原则 (SRP)

每个模块和类只负责一项功能：
- Core API 只负责 Core 层的接口封装
- Kernel API 只负责 Kernel 层的接口封装
- MoFoxBot 只负责应用流程控制

### 2. 依赖倒置原则 (DIP)

高层模块不依赖低层模块，都依赖抽象：
```python
# 应用层依赖 API 层的抽象
class MoFoxBot:
    def __init__(self):
        self.core: MoFoxCore     # 依赖抽象
        self.kernel: MoFoxKernel # 依赖抽象
```

### 3. 开闭原则 (OCP)

对扩展开放，对修改关闭：
```python
# 通过继承扩展功能
class MyCustomBot(MoFoxBot):
    async def _process_input(self, user_input: str):
        # 自定义处理逻辑
        pass
```

### 4. 接口隔离原则 (ISP)

提供多个专门的接口而不是一个庞大的接口：
- Core API 分为 prompt、transport、perception 等独立接口
- Kernel API 分为 config、db、llm 等独立接口

### 5. 最少知识原则 (LoD)

模块之间松耦合：
```python
# Bot 不直接访问底层模块，通过 API 访问
# 好的做法
response = await bot.kernel.llm.chat(message)

# 不好的做法（直接访问底层）
# from kernel.llm import OpenAIClient
# response = await OpenAIClient().chat(message)
```

## 扩展点

### 1. 自定义 Bot 类型

```python
class WebBot(MoFoxBot):
    """Web 服务 Bot"""
    async def initialize(self):
        await super().initialize()
        self.web_server = await start_web_server()
```

### 2. 自定义 API 模块

```python
# 扩展 Core API
class ExtendedCore(MoFoxCore):
    @property
    def custom_module(self):
        return self._custom_module
```

### 3. 插件系统（规划中）

```python
# 注册插件
bot.register_plugin(MyPlugin())
```

## 性能优化

### 1. 异步设计

所有 I/O 操作都是异步的：
```python
async def _process_input(self):
    # 并发执行多个任务
    tasks = [
        self.core.perception.process(input),
        self.kernel.db.query(condition),
    ]
    results = await asyncio.gather(*tasks)
```

### 2. 资源池化

- 数据库连接池
- LLM 客户端复用
- 任务队列管理

### 3. 缓存策略

- 配置缓存
- 提示词模板缓存
- 向量嵌入缓存

## 监控和调试

### 日志级别

```python
# 设置日志级别
kernel.logger.setLevel("DEBUG")

# 结构化日志
kernel.logger.info("处理请求", extra={
    "user_id": user_id,
    "request_type": "chat"
})
```

### 性能监控

```python
# 任务执行统计
stats = kernel.task_manager.get_stats()
print(f"完成任务数: {stats['completed']}")
print(f"平均执行时间: {stats['avg_time']}")
```

### 调试模式

```bash
# 启用调试模式
python start.py --debug
```

## 安全考虑

### 1. 输入验证

所有用户输入都应该验证和清理

### 2. 错误处理

```python
try:
    response = await bot.process(input)
except Exception as e:
    logger.error(f"处理失败: {e}")
    # 优雅降级
    response = "抱歉，处理出错了"
```

### 3. 资源限制

- 请求速率限制
- 并发任务数量限制
- 内存使用限制

## 未来规划

### 短期目标

- [ ] 完善 Core API 的各个模块实现
- [ ] 添加更多 LLM 提供商支持
- [ ] 实现插件系统
- [ ] 添加 Web API 接口

### 长期目标

- [ ] 分布式部署支持
- [ ] 多机器人协作
- [ ] 可视化管理界面
- [ ] 自动化测试和 CI/CD

## 参考资料

- [Core Layer 文档](../../core/README.md)
- [Kernel Layer 文档](../../kernel/README.md)
- [API 使用指南](API_GUIDE.md)
- [开发指南](DEVELOPMENT_GUIDE.md)

## 更新日志

- 2026-01-11: 初始版本，完成基础架构设计
