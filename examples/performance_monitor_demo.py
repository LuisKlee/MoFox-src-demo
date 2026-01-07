"""
性能监视器快速开始指南

展示如何使用性能监视器和API接口
"""

from app.monitors.performance_monitor import (
    get_monitor,
    init_monitor,
    performance_api,
)
import time


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("=== 示例1: 基本使用 ===")
    
    # 初始化并启动监视器
    monitor = init_monitor(sampling_interval=1.0, auto_start=True)
    
    # 模拟一些工作
    time.sleep(3)
    
    # 获取当前指标
    snapshot = monitor.get_current_snapshot()
    if snapshot:
        print(f"CPU使用率: {snapshot.cpu_percent:.2f}%")
        print(f"内存使用率: {snapshot.memory_percent:.2f}%")
        print(f"内存使用量: {snapshot.memory_mb:.2f}MB")
    
    monitor.stop()


def example_2_api_interface():
    """示例2: 使用API接口"""
    print("\n=== 示例2: 使用API接口 ===")
    
    # 启动监控
    response = performance_api.start_monitoring()
    print(f"启动结果: {response['status']}")
    
    # 模拟工作
    time.sleep(2)
    
    # 获取当前指标
    response = performance_api.get_current_metrics()
    if response['status'] == 'success':
        data = response['data']
        print(f"当前CPU: {data['cpu_percent']:.2f}%")
        print(f"当前内存: {data['memory_percent']:.2f}%")
    
    # 获取摘要
    response = performance_api.get_metrics_summary()
    if response['status'] == 'success':
        summary = response['data']
        print(f"平均CPU: {summary['cpu']['average']:.2f}%")
        print(f"最大CPU: {summary['cpu']['maximum']:.2f}%")
    
    # 停止监控
    performance_api.stop_monitoring()


def example_3_task_monitoring():
    """示例3: 任务执行监控"""
    print("\n=== 示例3: 任务执行监控 ===")
    
    monitor = get_monitor()
    
    # 模拟任务执行
    for i in range(5):
        start = time.time()
        time.sleep(0.1)  # 模拟任务
        duration = time.time() - start
        monitor.record_task_timing('data_processing', duration)
    
    for i in range(3):
        start = time.time()
        time.sleep(0.2)  # 模拟任务
        duration = time.time() - start
        monitor.record_task_timing('api_request', duration)
    
    # 查询任务统计
    response = performance_api.get_task_stats('data_processing')
    if response['status'] == 'success':
        stats = response['data']
        print(f"任务: {stats['task_name']}")
        print(f"  执行次数: {stats['count']}")
        print(f"  平均耗时: {stats['avg_time']:.4f}秒")
        print(f"  最小耗时: {stats['min_time']:.4f}秒")
        print(f"  最大耗时: {stats['max_time']:.4f}秒")


def example_4_api_endpoints():
    """示例4: 完整API端点总览"""
    print("\n=== 示例4: 完整API端点总览 ===")
    
    api_endpoints = {
        # 监控控制
        'start_monitoring()': '启动性能监控',
        'stop_monitoring()': '停止性能监控',
        'get_status()': '获取监视器状态',
        
        # 指标查询
        'get_current_metrics()': '获取当前性能指标',
        'get_metrics_summary()': '获取性能指标摘要',
        'get_history(limit=10)': '获取历史指标数据',
        
        # 任务监控
        'get_task_stats(task_name)': '获取特定任务统计',
        'get_all_tasks()': '获取所有任务统计',
        'record_task(task_name, duration)': '记录任务执行时间',
        
        # 数据管理
        'clear_all()': '清除所有性能数据',
        'reset_task(task_name=None)': '重置任务计时数据',
    }
    
    for endpoint, description in api_endpoints.items():
        print(f"  {endpoint:<40} - {description}")


if __name__ == '__main__':
    # 运行示例
    try:
        example_1_basic_usage()
        example_2_api_interface()
        example_3_task_monitoring()
        example_4_api_endpoints()
    except Exception as e:
        print(f"错误: {e}")
