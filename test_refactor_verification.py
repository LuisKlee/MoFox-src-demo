#!/usr/bin/env python
"""
TaskManager 重构验证脚本

验证以下内容：
1. 导入兼容性
2. 功能完整性
3. 模块分离
"""

import sys
import asyncio


def test_imports():
    """测试导入"""
    print("\n" + "="*60)
    print("测试 1: 导入兼容性")
    print("="*60)
    
    try:
        # 测试从兼容层导入（旧方式）
        from src.kernel.concurrency.task_manager import (
            TaskManager,
            get_task_manager,
            TaskPriority,
            TaskState,
            TaskConfig,
            ManagedTask
        )
        print("✓ 从兼容层成功导入所有类和函数")
        
        # 测试从包导入（新方式）
        from src.kernel.concurrency.task_manager import TaskManager as TM
        print("✓ TaskManager 导入成功")
        
        # 验证优先级
        assert hasattr(TaskPriority, 'HIGH')
        assert hasattr(TaskPriority, 'NORMAL')
        assert hasattr(TaskPriority, 'LOW')
        assert hasattr(TaskPriority, 'CRITICAL')
        print("✓ TaskPriority 枚举验证成功")
        
        # 验证状态
        assert hasattr(TaskState, 'RUNNING')
        assert hasattr(TaskState, 'COMPLETED')
        assert hasattr(TaskState, 'FAILED')
        print("✓ TaskState 枚举验证成功")
        
        # 验证配置
        config = TaskConfig()
        assert config.priority == TaskPriority.NORMAL
        assert config.timeout is None
        assert config.max_retries == 0
        print("✓ TaskConfig 数据类验证成功")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_functionality():
    """测试基本功能"""
    print("\n" + "="*60)
    print("测试 2: 功能完整性")
    print("="*60)
    
    try:
        from src.kernel.concurrency.task_manager import (
            get_task_manager,
            TaskConfig,
            TaskPriority
        )
        
        # 重置全局实例
        import src.kernel.concurrency.task_manager as tm_module
        tm_module._task_manager_instance = None
        
        # 创建管理器
        manager = get_task_manager(max_concurrent_tasks=5)
        print(f"✓ TaskManager 实例创建成功")
        
        # 启动管理器
        await manager.start()
        print(f"✓ TaskManager 启动成功")
        
        # 定义测试任务
        async def simple_task(x):
            await asyncio.sleep(0.1)
            return x * 2
        
        async def failing_task():
            raise ValueError("测试错误")
        
        # 测试1: 提交和执行任务
        task_id = manager.submit_task(simple_task, 5, name="test_task")
        print(f"✓ 任务提交成功 (ID: {task_id})")
        
        result = await manager.wait_for_task(task_id, timeout=5)
        assert result == 10, f"期望结果 10，得到 {result}"
        print(f"✓ 任务执行成功，结果: {result}")
        
        # 测试2: 获取统计信息
        stats = manager.get_stats()
        assert stats['total_submitted'] >= 1
        assert stats['total_completed'] >= 1
        print(f"✓ 统计信息获取成功: {stats['total_submitted']} 个任务已提交, {stats['total_completed']} 个已完成")
        
        # 测试3: 优先级
        task_id_high = manager.submit_task(
            simple_task, 
            3, 
            name="high_priority",
            config=TaskConfig(priority=TaskPriority.HIGH)
        )
        print(f"✓ 高优先级任务提交成功")
        
        # 测试4: 重试机制
        task_id_retry = manager.submit_task(
            failing_task,
            name="retry_task",
            config=TaskConfig(max_retries=2, retry_delay=0.1)
        )
        print(f"✓ 可重试任务提交成功")
        
        # 等待任务处理
        await asyncio.sleep(1)
        
        # 停止管理器
        await manager.stop(cancel_running_tasks=True)
        print(f"✓ TaskManager 停止成功")
        
        return True
    except Exception as e:
        print(f"✗ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_structure():
    """测试模块结构"""
    print("\n" + "="*60)
    print("测试 3: 模块分离验证")
    print("="*60)
    
    try:
        import src.kernel.concurrency.task_manager.models as models
        import src.kernel.concurrency.task_manager.manager as manager_mod
        import src.kernel.concurrency.task_manager.scheduler as scheduler
        import src.kernel.concurrency.task_manager.executor as executor
        import src.kernel.concurrency.task_manager.dependency as dependency
        import src.kernel.concurrency.task_manager.callbacks as callbacks
        
        print("✓ models.py 模块导入成功")
        print("✓ manager.py 模块导入成功")
        print("✓ scheduler.py 模块导入成功")
        print("✓ executor.py 模块导入成功")
        print("✓ dependency.py 模块导入成功")
        print("✓ callbacks.py 模块导入成功")
        
        # 验证关键类存在
        assert hasattr(models, 'TaskPriority')
        assert hasattr(models, 'TaskState')
        assert hasattr(models, 'TaskConfig')
        assert hasattr(models, 'ManagedTask')
        print("✓ 所有数据模型类验证成功")
        
        assert hasattr(manager_mod, 'TaskManager')
        assert hasattr(manager_mod, 'get_task_manager')
        print("✓ TaskManager 和全局函数验证成功")
        
        assert hasattr(scheduler, 'TaskScheduler')
        print("✓ TaskScheduler 验证成功")
        
        assert hasattr(executor, 'TaskExecutor')
        print("✓ TaskExecutor 验证成功")
        
        assert hasattr(dependency, 'DependencyManager')
        print("✓ DependencyManager 验证成功")
        
        assert hasattr(callbacks, 'CallbackManager')
        print("✓ CallbackManager 验证成功")
        
        return True
    except Exception as e:
        print(f"✗ 模块结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("TaskManager 重构验证测试")
    print("="*60)
    
    results = []
    
    # 运行测试
    results.append(("导入兼容性", test_imports()))
    results.append(("模块分离", test_module_structure()))
    results.append(("功能完整性", await test_functionality()))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总体结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！TaskManager 重构验证成功！")
        return 0
    else:
        print(f"\n❌ 有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
