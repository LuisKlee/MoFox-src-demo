"""
任务管理器监视器使用示例

展示如何在不修改TaskManager代码的情况下监视其运行状态
"""

from app.performance_monitor.task_monitor import (
    attach_monitor,
    get_task_monitor,
)


def example_1_basic_monitoring():
    """示例1: 基本监视"""
    print("=== 示例1: 基本监视 ===")
    
    # 假设你已经有一个TaskManager实例
    # from kernel.concurrency import get_task_manager
    # task_manager = get_task_manager()
    
    # 这里用简单对象模拟
    class MockTaskManager:
        pass
    
    task_manager = MockTaskManager()
    
    # 附加监视器（不改动TaskManager）
    monitor = attach_monitor(task_manager)
    
    # 在你的代码中，当任务事件发生时，调用监视器的方法来记录
    # 例如：在创建任务时
    monitor.record_task_created('task-001', 'data_process', {'priority': 'high'})
    
    # 任务开始执行
    monitor.record_task_started('task-001', 'data_process')
    
    # 任务完成
    monitor.record_task_completed('task-001', 'data_process')
    
    # 获取监视状态
    status = monitor.get_status()
    print(f"监视状态: {status['enabled']}")
    print(f"摘要: {status['summary']}")


def example_2_event_tracking():
    """示例2: 事件跟踪"""
    print("\n=== 示例2: 事件跟踪 ===")
    
    class MockTaskManager:
        pass
    
    task_manager = MockTaskManager()
    monitor = attach_monitor(task_manager)
    
    # 模拟多个任务生命周期
    # 成功完成的任务
    monitor.record_task_created('task-001', 'fetch_data')
    monitor.record_task_started('task-001', 'fetch_data')
    monitor.record_task_completed('task-001', 'fetch_data')
    
    # 失败的任务
    monitor.record_task_created('task-002', 'parse_data')
    monitor.record_task_started('task-002', 'parse_data')
    monitor.record_task_failed('task-002', 'parse_data', 'Invalid JSON format')
    
    # 超时的任务
    monitor.record_task_created('task-003', 'api_request')
    monitor.record_task_started('task-003', 'api_request')
    monitor.record_task_timeout('task-003', 'api_request', timeout=30.0)
    
    # 获取事件日志
    events = monitor.get_events(limit=10)
    print(f"事件数: {events['count']}")
    for event in events['data']:
        print(f"  - {event['event_type']}: {event['task_name']} (ID: {event['task_id']})")


def example_3_task_statistics():
    """示例3: 任务统计"""
    print("\n=== 示例3: 任务统计 ===")
    
    class MockTaskManager:
        pass
    
    task_manager = MockTaskManager()
    monitor = attach_monitor(task_manager)
    
    # 模拟多次执行同一个任务
    for i in range(5):
        monitor.record_task_created(f'task-{i:03d}', 'data_process')
        monitor.record_task_started(f'task-{i:03d}', 'data_process')
        monitor.record_task_completed(f'task-{i:03d}', 'data_process')
    
    # 获取任务统计
    stats = monitor.get_task_stats('data_process')
    print(f"任务统计: {stats['data']}")
    
    # 获取所有任务统计
    all_stats = monitor.get_all_tasks_stats()
    print(f"\n所有任务数: {all_stats['count']}")
    for task_name, stats in all_stats['data'].items():
        print(f"  {task_name}:")
        print(f"    - 成功率: {stats['success_rate']}%")
        print(f"    - 平均耗时: {stats['avg_duration']:.4f}s")


def example_4_error_tracking():
    """示例4: 错误跟踪"""
    print("\n=== 示例4: 错误跟踪 ===")
    
    class MockTaskManager:
        pass
    
    task_manager = MockTaskManager()
    monitor = attach_monitor(task_manager)
    
    # 模拟任务失败
    monitor.record_task_created('task-001', 'process', {'input': 'data1'})
    monitor.record_task_started('task-001', 'process')
    monitor.record_task_failed('task-001', 'process', 'NullPointerException')
    
    # 重试
    monitor.record_task_retry('task-001', 'process', retry_count=1)
    monitor.record_task_started('task-001', 'process')
    monitor.record_task_completed('task-001', 'process')
    
    # 获取摘要
    summary = monitor.get_summary()
    print(f"摘要: {summary['data']}")


def example_5_integration_pattern():
    """示例5: 集成模式 - 如何在TaskManager中集成监视"""
    print("\n=== 示例5: 集成模式 ===")
    
    print("""
    在你的TaskManager代码中集成监视（不修改TaskManager本身）：
    
    1. 获取或创建TaskManager:
       from kernel.concurrency import get_task_manager
       task_manager = get_task_manager()
    
    2. 附加监视器（在应用初始化时）:
       from app.performance_monitor.task_monitor import attach_monitor
       monitor = attach_monitor(task_manager)
    
    3. 在Task执行的相关地方手动调用监视记录（可以通过回调或包装器）:
       
       # 在任务创建时:
       monitor.record_task_created(task_id, task_name)
       
       # 在任务开始时:
       monitor.record_task_started(task_id, task_name)
       
       # 在任务完成时:
       monitor.record_task_completed(task_id, task_name)
       
       # 在任务失败时:
       monitor.record_task_failed(task_id, task_name, str(error))
    
    4. 查询监视数据:
       status = monitor.get_status()
       stats = monitor.get_all_tasks_stats()
       events = monitor.get_events(limit=100)
    
    优点：
    - TaskManager代码保持不变
    - 可以随时启用/禁用监视
    - 监视逻辑完全独立
    - 易于扩展和测试
    """)


if __name__ == '__main__':
    try:
        example_1_basic_monitoring()
        example_2_event_tracking()
        example_3_task_statistics()
        example_4_error_tracking()
        example_5_integration_pattern()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
