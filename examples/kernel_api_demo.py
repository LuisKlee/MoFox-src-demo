"""
MoFox Kernel API 使用示例

展示如何使用高级封装的 Kernel API 接口
"""

import asyncio
from src.app.bot.kernel_api import init_kernel, shutdown_kernel


async def basic_usage_demo():
    """基础使用示例"""
    print("=" * 60)
    print("基础使用示例")
    print("=" * 60)
    
    # 初始化 kernel
    kernel = await init_kernel(
        app_name="demo_app",
        log_dir="logs",
        data_dir="data"
    )
    
    # 使用日志
    kernel.logger.info("应用已启动")
    kernel.logger.debug("这是一条调试信息")
    
    # 使用配置
    kernel.set_config("debug_mode", True)
    debug = kernel.get_config("debug_mode")
    kernel.logger.info(f"调试模式: {debug}")
    
    # 查看日志统计
    stats = kernel.get_logs(days=1)
    print(f"日志统计: {stats}")
    
    # 关闭
    await shutdown_kernel()
    print("\n✅ 基础示例完成\n")


async def llm_demo():
    """LLM 功能示例"""
    print("=" * 60)
    print("LLM 功能示例")
    print("=" * 60)
    
    kernel = await init_kernel(app_name="llm_demo")
    
    # 简单聊天
    print("\n1. 简单聊天:")
    response = await kernel.llm.chat(
        "用一句话介绍 Python",
        model="gpt-4",
        system_prompt=kernel.llm.get_system_prompt("education")
    )
    print(f"回复: {response}")
    
    # 流式聊天
    print("\n2. 流式聊天:")
    print("回复: ", end="", flush=True)
    async for chunk in kernel.llm.chat_stream(
        "讲一个简短的笑话",
        model="gpt-4"
    ):
        print(chunk, end="", flush=True)
    print()
    
    # 创建消息
    print("\n3. 创建消息:")
    system_msg = kernel.llm.create_message("你是一个编程助手", role="system")
    user_msg = kernel.llm.create_message("Python 如何读取文件？")
    print(f"系统消息: {system_msg}")
    print(f"用户消息: {user_msg}")
    
    # 工具调用
    print("\n4. 工具调用:")
    tool = kernel.llm.create_tool(
        name="get_weather",
        description="获取指定城市的天气",
        parameters=[
            {"name": "city", "type": "string", "description": "城市名称", "required": True}
        ]
    )
    response = await kernel.llm.chat_with_tools(
        "北京今天天气怎么样？",
        tools=[tool],
        model="gpt-4"
    )
    print(f"工具调用响应: {response}")
    
    await shutdown_kernel()
    print("\n✅ LLM 示例完成\n")


async def storage_demo():
    """存储功能示例"""
    print("=" * 60)
    print("存储功能示例")
    print("=" * 60)
    
    kernel = await init_kernel(app_name="storage_demo")
    
    # JSON 存储
    print("\n1. JSON 存储:")
    kernel.storage.save("config", {"version": "1.0", "debug": True})
    config = kernel.storage.load("config")
    print(f"加载配置: {config}")
    
    # 字典存储
    print("\n2. 字典存储:")
    dict_store = kernel.storage.dict_store("users")
    dict_store.set("user1", {"name": "Alice", "age": 25})
    dict_store.set("user2", {"name": "Bob", "age": 30})
    users = dict_store.to_dict()
    print(f"所有用户: {users}")
    print(f"获取用户1: {dict_store.get('user1')}")
    
    # 列表存储
    print("\n3. 列表存储:")
    list_store = kernel.storage.list_store("events")
    list_store.append({"type": "login", "user": "Alice"})
    list_store.append({"type": "logout", "user": "Bob"})
    events = list_store.to_list()
    print(f"所有事件: {events}")
    print(f"事件数量: {list_store.count()}")
    
    # 日志存储
    print("\n4. 日志存储:")
    log_store = kernel.storage.log_store("app_logs")
    log_store.log("info", "Application started")
    log_store.log("error", "Something went wrong")
    logs = log_store.get_logs()
    print(f"日志数量: {len(logs)}")
    print(f"最近的日志: {logs[-1] if logs else 'None'}")
    
    await shutdown_kernel()
    print("\n✅ 存储示例完成\n")


async def database_demo():
    """数据库功能示例"""
    print("=" * 60)
    print("数据库功能示例")
    print("=" * 60)
    
    kernel = await init_kernel(app_name="db_demo")
    
    # 初始化数据库
    await kernel.init_database("data/demo.db")
    
    # 使用数据库会话
    print("\n使用数据库会话:")
    async with kernel.db_session() as session:
        print(f"数据库会话已创建: {session}")
        # 在这里执行数据库操作
        # 例如: kernel.db.add(session, model_instance)
    
    print("✅ 数据库会话已关闭")
    
    await shutdown_kernel()
    print("\n✅ 数据库示例完成\n")


async def task_management_demo():
    """任务管理示例"""
    print("=" * 60)
    print("任务管理示例")
    print("=" * 60)
    
    kernel = await init_kernel(app_name="task_demo")
    
    # 定义一些示例任务
    async def task1(x):
        await asyncio.sleep(0.5)
        return x * 2
    
    async def task2(x):
        await asyncio.sleep(0.3)
        return x + 10
    
    async def task3(x):
        await asyncio.sleep(0.2)
        return x ** 2
    
    # 单个任务
    print("\n1. 运行单个任务:")
    result = await kernel.run_task(task1, 5, name="multiply_task")
    print(f"任务结果: {result}")
    
    # 并行任务
    print("\n2. 并行运行多个任务:")
    tasks = [
        (task1, (3,)),
        (task2, (5,)),
        (task3, (4,))
    ]
    results = await kernel.run_tasks_parallel(tasks)
    print(f"所有任务结果: {results}")
    
    # 使用任务管理器
    print("\n3. 直接使用任务管理器:")
    task_id = kernel.tasks.submit_task(
        task1,
        10,
        name="direct_task"
    )
    result = await kernel.tasks.wait_for_task(task_id)
    print(f"任务 {task_id} 结果: {result}")
    
    # 获取任务状态
    status = kernel.tasks.get_task_status(task_id)
    print(f"任务状态: {status}")
    
    await shutdown_kernel()
    print("\n✅ 任务管理示例完成\n")


async def vector_db_demo():
    """向量数据库示例"""
    print("=" * 60)
    print("向量数据库示例")
    print("=" * 60)
    
    kernel = await init_kernel(app_name="vector_demo")
    
    # 初始化向量数据库
    await kernel.init_vector_db(
        db_type="chromadb",
        persist_dir="data/vector_db"
    )
    
    # 创建集合
    print("\n1. 创建集合:")
    collection_name = "documents"
    exists = await kernel.vector_db.collection_exists(collection_name)
    if not exists:
        await kernel.vector_db.create_collection(collection_name)
        print(f"✅ 集合 '{collection_name}' 已创建")
    else:
        print(f"ℹ️  集合 '{collection_name}' 已存在")
    
    # 添加文档
    print("\n2. 添加文档:")
    from src.app.bot.kernel_api import VectorDocument
    docs = [
        VectorDocument(
            id="doc1",
            content="Python 是一种解释型编程语言",
            vector=[0.1, 0.2, 0.3],  # 实际应使用真实的嵌入向量
            metadata={"category": "programming"}
        ),
        VectorDocument(
            id="doc2",
            content="机器学习是人工智能的一个分支",
            vector=[0.2, 0.3, 0.4],
            metadata={"category": "ai"}
        )
    ]
    await kernel.vector_db.add_documents(collection_name, docs)
    print(f"✅ 已添加 {len(docs)} 个文档")
    
    # 查询文档
    print("\n3. 查询文档:")
    count = await kernel.vector_db.count_documents(collection_name)
    print(f"文档总数: {count}")
    
    # 向量搜索
    print("\n4. 向量搜索:")
    results = await kernel.vector_search(
        collection=collection_name,
        query=[0.15, 0.25, 0.35],
        top_k=2
    )
    print(f"搜索结果数量: {len(results)}")
    for i, doc in enumerate(results):
        print(f"  {i+1}. {doc.content[:50]}...")
    
    await shutdown_kernel()
    print("\n✅ 向量数据库示例完成\n")


async def integrated_demo():
    """综合示例 - 实际应用场景"""
    print("=" * 60)
    print("综合示例 - 智能问答系统")
    print("=" * 60)
    
    kernel = await init_kernel(
        app_name="qa_system",
        log_dir="logs/qa",
        data_dir="data/qa"
    )
    
    # 1. 初始化各个组件
    kernel.logger.info("初始化智能问答系统")
    
    # 初始化向量数据库
    await kernel.init_vector_db(persist_dir="data/qa/vectors")
    
    # 初始化普通数据库
    await kernel.init_database("data/qa/qa.db")
    
    # 2. 存储一些问题和答案
    print("\n1. 存储知识库:")
    qa_store = kernel.storage.dict_store("qa_knowledge")
    qa_store.set("python_basics", {
        "question": "什么是 Python？",
        "answer": "Python 是一种高级、解释型、通用编程语言"
    })
    qa_store.set("python_features", {
        "question": "Python 有什么特点？",
        "answer": "Python 语法简洁、可读性强、拥有丰富的库"
    })
    print(f"✅ 已存储 {len(qa_store.keys())} 个知识点")
    
    # 3. 模拟用户提问
    print("\n2. 处理用户提问:")
    user_question = "Python 有什么优势？"
    kernel.logger.info(f"用户提问: {user_question}")
    
    # 使用 LLM 生成回答
    async def answer_question(question: str) -> str:
        system_prompt = kernel.llm.get_system_prompt("education")
        response = await kernel.llm.chat(
            f"请简洁回答: {question}",
            system_prompt=system_prompt
        )
        return response
    
    # 作为任务运行
    answer = await kernel.run_task(
        answer_question,
        user_question,
        name="answer_task"
    )
    print(f"回答: {answer}")
    
    # 4. 记录问答历史
    print("\n3. 记录问答历史:")
    history_store = kernel.storage.list_store("qa_history")
    history_store.append({
        "question": user_question,
        "answer": answer,
        "timestamp": str(asyncio.get_event_loop().time())
    })
    print(f"✅ 历史记录已保存，总计 {history_store.count()} 条")
    
    # 5. 查看日志统计
    print("\n4. 系统运行统计:")
    stats = kernel.get_logs(days=1)
    print(f"日志统计: {stats}")
    
    await shutdown_kernel()
    print("\n✅ 综合示例完成\n")


async def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("MoFox Kernel API 示例集")
    print("=" * 60 + "\n")
    
    demos = [
        ("基础使用", basic_usage_demo),
        ("LLM 功能", llm_demo),
        ("存储功能", storage_demo),
        ("数据库功能", database_demo),
        ("任务管理", task_management_demo),
        ("向量数据库", vector_db_demo),
        ("综合应用", integrated_demo),
    ]
    
    print("请选择要运行的示例:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"{i}. {name}")
    print(f"{len(demos) + 1}. 运行所有示例")
    print("0. 退出")
    
    try:
        choice = input("\n请输入选项 (0-{}): ".format(len(demos) + 1))
        choice = int(choice)
        
        if choice == 0:
            print("再见！")
            return
        elif choice == len(demos) + 1:
            # 运行所有示例
            for name, demo_func in demos:
                try:
                    await demo_func()
                except Exception as e:
                    print(f"\n❌ {name} 示例出错: {e}\n")
        elif 1 <= choice <= len(demos):
            # 运行选定的示例
            name, demo_func = demos[choice - 1]
            await demo_func()
        else:
            print("无效的选项！")
    except ValueError:
        print("请输入有效的数字！")
    except KeyboardInterrupt:
        print("\n\n中断执行")
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")


if __name__ == "__main__":
    # 注意: 某些示例需要配置 API 密钥等
    # 请确保环境变量或配置文件已正确设置
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已终止")
