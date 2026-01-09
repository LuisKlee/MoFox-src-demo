"""
MoFox Kernel API - 高级对外暴露接口

这个模块封装了 kernel 层的所有核心功能，提供统一、简洁的 API 接口。
适合快速集成和使用 MoFox 的各项能力。

作者: MoFox Team
日期: 2026-01-09
"""

from typing import Any, Dict, List, Optional, Union, Callable, AsyncIterator
from pathlib import Path
from datetime import datetime, timedelta
import asyncio
from contextlib import asynccontextmanager

# ==================== 配置管理 ====================
from kernel.config import (
    Config,
    ConfigManager,
    get_manager as get_config_manager,
    get_config,
    load_config,
    register_config
)

# ==================== 数据库 ====================
from kernel.db.core import create_sqlite_engine
from kernel.db.api import SQLAlchemyCRUDRepository, QuerySpec

# ==================== LLM ====================
from kernel.llm import (
    generate,
    stream_generate,
    generate_with_tools,
    MessageBuilder,
    ToolBuilder,
    get_system_prompt,
    PromptTemplates
)

# ==================== 日志 ====================
from kernel.logger.storage_integration import LoggerWithStorage
from kernel.logger import MetadataContext, LogMetadata

# ==================== 存储 ====================
from kernel.storage import (
    JSONStore,
    DictJSONStore,
    ListJSONStore,
    LogStore
)

# ==================== 向量数据库 ====================
from kernel.vector_db import (
    create_vector_db,
    create_vector_db_async,
    VectorDocument
)

# ==================== 并发任务管理 ====================
from kernel.concurrency.task_manager import (
    get_task_manager,
    TaskManager,
    TaskPriority,
    TaskState,
    TaskConfig,
    ManagedTask
)


# ==================== 全局单例管理器 ====================
class MoFoxKernel:
    """
    MoFox Kernel 统一管理器
    
    提供所有 kernel 功能的统一访问入口，管理全局单例实例。
    
    示例:
        >>> kernel = MoFoxKernel(app_name="my_app")
        >>> await kernel.initialize()
        >>> 
        >>> # 使用 LLM
        >>> response = await kernel.llm.chat("你好")
        >>> 
        >>> # 使用日志
        >>> kernel.logger.info("应用启动")
        >>> 
        >>> # 使用存储
        >>> kernel.storage.save("key", {"data": "value"})
    """
    
    def __init__(
        self,
        app_name: str = "mofox_app",
        config_path: Optional[str] = None,
        log_dir: str = "logs",
        data_dir: str = "data",
        **kwargs
    ):
        """
        初始化 MoFox Kernel
        
        Args:
            app_name: 应用名称
            config_path: 配置文件路径
            log_dir: 日志目录
            data_dir: 数据目录
            **kwargs: 其他配置参数
        """
        self.app_name = app_name
        self.config_path = config_path
        self.log_dir = log_dir
        self.data_dir = data_dir
        self.extra_config = kwargs
        
        # 各模块管理器
        self._config: Optional[Config] = None
        self._logger_system: Optional[LoggerWithStorage] = None
        self._task_manager: Optional[TaskManager] = None
        self._db_engine = None
        self._db_repo: Optional[SQLAlchemyCRUDRepository] = None
        self._vector_db = None
        
        self._initialized = False
    
    async def initialize(self):
        """初始化所有核心组件"""
        if self._initialized:
            return
        
        # 1. 初始化配置
        await self._init_config()
        
        # 2. 初始化日志系统
        await self._init_logger()
        
        # 3. 初始化任务管理器
        await self._init_task_manager()
        
        self._initialized = True
        self.logger.info(f"MoFox Kernel 初始化完成: {self.app_name}")
    
    async def _init_config(self):
        """初始化配置管理"""
        if self.config_path:
            self._config = Config.from_file(self.config_path)
        else:
            self._config = Config(**self.extra_config)
    
    async def _init_logger(self):
        """初始化日志系统"""
        self._logger_system = LoggerWithStorage(
            app_name=self.app_name,
            log_dir=self.log_dir,
            console_output=True,
            json_storage=True
        )
        self._logger = self._logger_system.get_logger(f"{self.app_name}.kernel")
    
    async def _init_task_manager(self):
        """初始化任务管理器"""
        max_tasks = self._config.get("max_concurrent_tasks", 10) if self._config else 10
        self._task_manager = get_task_manager(max_concurrent_tasks=max_tasks)
        await self._task_manager.start()
    
    async def shutdown(self):
        """关闭所有资源"""
        if not self._initialized:
            return
        
        # 停止任务管理器
        if self._task_manager:
            await self._task_manager.stop()
        
        # 关闭数据库连接
        if self._db_engine:
            await self._db_engine.dispose()
        
        # 关闭向量数据库
        if self._vector_db:
            await self._vector_db.close()
        
        self._initialized = False
        self.logger.info(f"MoFox Kernel 已关闭: {self.app_name}")
    
    # ==================== 配置管理接口 ====================
    
    @property
    def config(self) -> Config:
        """获取配置管理器"""
        return self._config
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default) if self._config else default
    
    def set_config(self, key: str, value: Any):
        """设置配置值"""
        if self._config:
            self._config[key] = value
    
    # ==================== 日志管理接口 ====================
    
    @property
    def logger(self):
        """获取日志器"""
        return self._logger
    
    def get_logger(self, name: str):
        """获取指定名称的日志器"""
        return self._logger_system.get_logger(name)
    
    def get_logs(self, days: int = 1) -> Dict[str, Any]:
        """获取日志统计"""
        return self._logger_system.get_logs(days=days)
    
    def get_error_logs(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取错误日志"""
        return self._logger_system.get_error_logs(days=days)
    
    # ==================== LLM 接口 ====================
    
    class LLMInterface:
        """LLM 功能接口"""
        
        def __init__(self, logger):
            self.logger = logger
        
        async def chat(
            self,
            message: str,
            model: str = "gpt-4",
            provider: str = "openai",
            system_prompt: Optional[str] = None,
            **kwargs
        ) -> str:
            """
            简单聊天接口
            
            Args:
                message: 用户消息
                model: 模型名称
                provider: 提供商
                system_prompt: 系统提示词
                **kwargs: 其他参数
            
            Returns:
                模型回复内容
            """
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": message})
            
            response = await generate(
                model=model,
                messages=messages,
                provider=provider,
                **kwargs
            )
            return response.content
        
        async def chat_stream(
            self,
            message: str,
            model: str = "gpt-4",
            provider: str = "openai",
            system_prompt: Optional[str] = None,
            **kwargs
        ) -> AsyncIterator[str]:
            """
            流式聊天接口
            
            Args:
                message: 用户消息
                model: 模型名称
                provider: 提供商
                system_prompt: 系统提示词
                **kwargs: 其他参数
            
            Yields:
                逐块返回的内容
            """
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": message})
            
            async for chunk in stream_generate(
                model=model,
                messages=messages,
                provider=provider,
                **kwargs
            ):
                yield chunk.content
        
        async def chat_with_tools(
            self,
            message: str,
            tools: List[Dict[str, Any]],
            model: str = "gpt-4",
            provider: str = "openai",
            **kwargs
        ) -> Any:
            """
            带工具调用的聊天
            
            Args:
                message: 用户消息
                tools: 工具定义列表
                model: 模型名称
                provider: 提供商
                **kwargs: 其他参数
            
            Returns:
                模型响应（可能包含工具调用）
            """
            messages = [{"role": "user", "content": message}]
            return await generate_with_tools(
                model=model,
                messages=messages,
                tools=tools,
                provider=provider,
                **kwargs
            )
        
        def create_message(
            self,
            content: str,
            role: str = "user",
            images: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            创建消息
            
            Args:
                content: 消息内容
                role: 角色 (user/system/assistant)
                images: 图片路径列表（多模态）
            
            Returns:
                消息字典
            """
            if role == "system":
                return MessageBuilder.create_system_message(content)
            elif role == "assistant":
                return MessageBuilder.create_assistant_message(content)
            elif images:
                return MessageBuilder.create_multimodal_message(content, images)
            else:
                return MessageBuilder.create_user_message(content)
        
        def create_tool(
            self,
            name: str,
            description: str,
            parameters: List[Dict[str, Any]]
        ) -> Dict[str, Any]:
            """
            创建工具定义
            
            Args:
                name: 工具名称
                description: 工具描述
                parameters: 参数列表
            
            Returns:
                工具定义字典
            """
            return ToolBuilder.create_tool(name, description, parameters)
        
        def get_system_prompt(self, prompt_type: str) -> str:
            """
            获取预设系统提示词
            
            Args:
                prompt_type: 提示词类型
                    - coding: 编程助手
                    - translation: 翻译助手
                    - data_analysis: 数据分析
                    - creative: 创意写作
                    - education: 教育辅导
                    - customer_service: 客服
            
            Returns:
                系统提示词
            """
            return get_system_prompt(prompt_type)
    
    @property
    def llm(self) -> LLMInterface:
        """获取 LLM 接口"""
        if not hasattr(self, "_llm_interface"):
            self._llm_interface = self.LLMInterface(self.logger)
        return self._llm_interface
    
    # ==================== 数据库接口 ====================
    
    async def init_database(self, db_path: Optional[str] = None, **kwargs):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
            **kwargs: 数据库配置参数
        """
        if not db_path:
            db_path = f"{self.data_dir}/{self.app_name}.db"
        
        self._db_engine = create_sqlite_engine(db_path, **kwargs)
        self._db_repo = SQLAlchemyCRUDRepository(self._db_engine)
        self.logger.info(f"数据库已初始化: {db_path}")
    
    @property
    def db(self) -> SQLAlchemyCRUDRepository:
        """获取数据库仓库"""
        if not self._db_repo:
            raise RuntimeError("数据库未初始化，请先调用 init_database()")
        return self._db_repo
    
    @asynccontextmanager
    async def db_session(self):
        """数据库会话上下文管理器"""
        if not self._db_repo:
            raise RuntimeError("数据库未初始化，请先调用 init_database()")
        async with self._db_repo.session_scope() as session:
            yield session
    
    # ==================== 存储接口 ====================
    
    class StorageInterface:
        """存储功能接口"""
        
        def __init__(self, data_dir: str, logger):
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.logger = logger
            self._stores: Dict[str, Any] = {}
        
        def json_store(self, name: str, **kwargs) -> JSONStore:
            """
            获取 JSON 存储器
            
            Args:
                name: 存储器名称
                **kwargs: JSONStore 参数
            
            Returns:
                JSONStore 实例
            """
            if name not in self._stores:
                file_path = self.data_dir / f"{name}.json"
                self._stores[name] = JSONStore(file_path, **kwargs)
            return self._stores[name]
        
        def dict_store(self, name: str, **kwargs) -> DictJSONStore:
            """
            获取字典存储器
            
            Args:
                name: 存储器名称
                **kwargs: DictJSONStore 参数
            
            Returns:
                DictJSONStore 实例
            """
            if name not in self._stores:
                file_path = self.data_dir / f"{name}.json"
                self._stores[name] = DictJSONStore(file_path, **kwargs)
            return self._stores[name]
        
        def list_store(self, name: str, **kwargs) -> ListJSONStore:
            """
            获取列表存储器
            
            Args:
                name: 存储器名称
                **kwargs: ListJSONStore 参数
            
            Returns:
                ListJSONStore 实例
            """
            if name not in self._stores:
                file_path = self.data_dir / f"{name}.json"
                self._stores[name] = ListJSONStore(file_path, **kwargs)
            return self._stores[name]
        
        def log_store(self, name: str, **kwargs) -> LogStore:
            """
            获取日志存储器
            
            Args:
                name: 存储器名称
                **kwargs: LogStore 参数
            
            Returns:
                LogStore 实例
            """
            if name not in self._stores:
                file_path = self.data_dir / f"{name}.json"
                self._stores[name] = LogStore(file_path, **kwargs)
            return self._stores[name]
        
        def save(self, name: str, data: Any, store_type: str = "json"):
            """
            快速保存数据
            
            Args:
                name: 存储名称
                data: 要保存的数据
                store_type: 存储类型 (json/dict/list)
            """
            if store_type == "dict" and isinstance(data, dict):
                store = self.dict_store(name)
                store.update(data)
            elif store_type == "list" and isinstance(data, list):
                store = self.list_store(name)
                store.extend(data)
            else:
                store = self.json_store(name)
                store.write(data)
            
            self.logger.debug(f"数据已保存: {name}")
        
        def load(self, name: str, default: Any = None, store_type: str = "json") -> Any:
            """
            快速加载数据
            
            Args:
                name: 存储名称
                default: 默认值
                store_type: 存储类型 (json/dict/list)
            
            Returns:
                加载的数据
            """
            try:
                if store_type == "dict":
                    store = self.dict_store(name)
                    return store.to_dict()
                elif store_type == "list":
                    store = self.list_store(name)
                    return store.to_list()
                else:
                    store = self.json_store(name)
                    return store.read(default=default)
            except Exception as e:
                self.logger.warning(f"加载数据失败: {name}, 错误: {e}")
                return default
    
    @property
    def storage(self) -> StorageInterface:
        """获取存储接口"""
        if not hasattr(self, "_storage_interface"):
            self._storage_interface = self.StorageInterface(self.data_dir, self.logger)
        return self._storage_interface
    
    # ==================== 向量数据库接口 ====================
    
    async def init_vector_db(
        self,
        db_type: str = "chromadb",
        persist_dir: Optional[str] = None,
        **kwargs
    ):
        """
        初始化向量数据库
        
        Args:
            db_type: 数据库类型 (chromadb)
            persist_dir: 持久化目录
            **kwargs: 其他配置参数
        """
        if not persist_dir:
            persist_dir = f"{self.data_dir}/vector_db"
        
        config = {"persist_directory": persist_dir, **kwargs}
        self._vector_db = await create_vector_db_async(db_type, config)
        self.logger.info(f"向量数据库已初始化: {db_type} at {persist_dir}")
    
    @property
    def vector_db(self):
        """获取向量数据库"""
        if not self._vector_db:
            raise RuntimeError("向量数据库未初始化，请先调用 init_vector_db()")
        return self._vector_db
    
    async def vector_search(
        self,
        collection: str,
        query: Union[str, List[float]],
        top_k: int = 5,
        **kwargs
    ) -> List[VectorDocument]:
        """
        向量搜索
        
        Args:
            collection: 集合名称
            query: 查询向量或文本
            top_k: 返回结果数量
            **kwargs: 其他参数
        
        Returns:
            搜索结果列表
        """
        if isinstance(query, str):
            return await self.vector_db.query_similar(
                collection_name=collection,
                query_text=query,
                top_k=top_k,
                **kwargs
            )
        else:
            return await self.vector_db.query_similar(
                collection_name=collection,
                query_vector=query,
                top_k=top_k,
                **kwargs
            )
    
    # ==================== 任务管理接口 ====================
    
    @property
    def tasks(self) -> TaskManager:
        """获取任务管理器"""
        if not self._task_manager:
            raise RuntimeError("任务管理器未初始化")
        return self._task_manager
    
    async def run_task(
        self,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        name: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        运行异步任务
        
        Args:
            func: 任务函数
            *args: 位置参数
            priority: 任务优先级
            name: 任务名称
            **kwargs: 关键字参数
        
        Returns:
            任务结果
        """
        config = TaskConfig(priority=priority)
        task_id = self._task_manager.submit_task(
            func,
            *args,
            name=name or func.__name__,
            config=config,
            **kwargs
        )
        return await self._task_manager.wait_for_task(task_id)
    
    async def run_tasks_parallel(
        self,
        tasks: List[tuple],
        **kwargs
    ) -> List[Any]:
        """
        并行运行多个任务
        
        Args:
            tasks: 任务列表，每个元素为 (func, args, kwargs)
            **kwargs: 通用任务配置
        
        Returns:
            所有任务结果列表
        """
        task_ids = []
        for task_info in tasks:
            func = task_info[0]
            args = task_info[1] if len(task_info) > 1 else ()
            task_kwargs = task_info[2] if len(task_info) > 2 else {}
            
            task_id = self._task_manager.submit_task(
                func,
                *args,
                name=func.__name__,
                **task_kwargs
            )
            task_ids.append(task_id)
        
        results = []
        for task_id in task_ids:
            result = await self._task_manager.wait_for_task(task_id)
            results.append(result)
        
        return results


# ==================== 便捷函数 ====================

_global_kernel: Optional[MoFoxKernel] = None


def get_kernel(
    app_name: str = "mofox_app",
    **kwargs
) -> MoFoxKernel:
    """
    获取全局 MoFox Kernel 实例
    
    Args:
        app_name: 应用名称
        **kwargs: 其他配置参数
    
    Returns:
        MoFoxKernel 实例
    """
    global _global_kernel
    if _global_kernel is None:
        _global_kernel = MoFoxKernel(app_name=app_name, **kwargs)
    return _global_kernel


async def init_kernel(
    app_name: str = "mofox_app",
    **kwargs
) -> MoFoxKernel:
    """
    初始化并获取全局 MoFox Kernel 实例
    
    Args:
        app_name: 应用名称
        **kwargs: 其他配置参数
    
    Returns:
        已初始化的 MoFoxKernel 实例
    """
    kernel = get_kernel(app_name, **kwargs)
    await kernel.initialize()
    return kernel


async def shutdown_kernel():
    """关闭全局 MoFox Kernel"""
    global _global_kernel
    if _global_kernel:
        await _global_kernel.shutdown()
        _global_kernel = None


# ==================== 导出列表 ====================

__all__ = [
    # 核心类
    "MoFoxKernel",
    
    # 便捷函数
    "get_kernel",
    "init_kernel",
    "shutdown_kernel",
    
    # 配置
    "Config",
    "ConfigManager",
    "get_config_manager",
    "get_config",
    "load_config",
    "register_config",
    
    # 数据库
    "create_sqlite_engine",
    "SQLAlchemyCRUDRepository",
    "QuerySpec",
    
    # LLM
    "generate",
    "stream_generate",
    "generate_with_tools",
    "MessageBuilder",
    "ToolBuilder",
    "get_system_prompt",
    "PromptTemplates",
    
    # 日志
    "LoggerWithStorage",
    "MetadataContext",
    "LogMetadata",
    
    # 存储
    "JSONStore",
    "DictJSONStore",
    "ListJSONStore",
    "LogStore",
    
    # 向量数据库
    "create_vector_db",
    "create_vector_db_async",
    "VectorDocument",
    
    # 任务管理
    "get_task_manager",
    "TaskManager",
    "TaskPriority",
    "TaskState",
    "TaskConfig",
    "ManagedTask",
]
