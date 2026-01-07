"""
统一监视器系统演示示例

演示如何使用统一监视器管理系统整合性能和数据库监控

注意：这是一个测试/示例模块
"""

import time
import random
from datetime import datetime


def demo_basic_usage():
    """演示基本使用"""
    print("\n" + "="*60)
    print("演示1: 基本使用")
    print("="*60)
    
    from app.monitors import get_manager
    
    # 获取管理器实例
    manager = get_manager()
    
    # 启用所有监视器
    manager.enable_all()
    print("✓ 所有监视器已启用")
    
    # 等待收集一些数据
    print("\n等待收集数据...")
    time.sleep(2)
    
    # 获取综合快照
    snapshot = manager.get_comprehensive_snapshot()
    
    print("\n=== 综合快照 ===")
    print(f"时间: {snapshot['timestamp']}")
    
    print("\n性能指标:")
    perf = snapshot['performance']
    print(f"  CPU: {perf['cpu_percent']}%")
    print(f"  内存: {perf['memory_percent']}% ({perf['memory_mb']}MB)")
    print(f"  线程数: {perf['thread_count']}")
    
    print("\n数据库指标:")
    db = snapshot['database']
    print(f"  总查询数: {db['total_queries']}")
    print(f"  成功查询: {db['successful_queries']}")
    print(f"  平均查询时间: {db['avg_query_time']}秒")
    
    # 禁用所有监视器
    manager.disable_all()
    print("\n✓ 所有监视器已禁用")


def demo_unified_api():
    """演示统一API接口"""
    print("\n" + "="*60)
    print("演示2: 统一API接口")
    print("="*60)
    
    from app.monitors import unified_monitor_api
    
    # 启用所有监视器
    response = unified_monitor_api.enable_all_monitors()
    print(f"✓ {response['message']}")
    
    # 等待收集数据
    time.sleep(2)
    
    # 获取监视器状态
    print("\n=== 监视器状态 ===")
    response = unified_monitor_api.get_monitors_status()
    status = response['data']
    
    print(f"性能监视器: {'已启用' if status['performance_monitor']['enabled'] else '已禁用'}")
    print(f"  采样间隔: {status['performance_monitor']['sampling_interval']}秒")
    print(f"  指标数量: {status['performance_monitor']['metrics_count']}")
    
    print(f"\n数据库监视器: {'已启用' if status['database_monitor']['enabled'] else '已禁用'}")
    print(f"  慢查询阈值: {status['database_monitor']['slow_query_threshold']}秒")
    print(f"  查询历史数: {status['database_monitor']['query_history_count']}")
    
    # 获取综合快照
    print("\n=== 综合快照 ===")
    response = unified_monitor_api.get_comprehensive_snapshot()
    snapshot = response['data']
    
    print(f"CPU: {snapshot['performance']['cpu_percent']}%")
    print(f"内存: {snapshot['performance']['memory_mb']}MB")
    print(f"总查询: {snapshot['database']['total_queries']}")
    
    # 禁用所有监视器
    unified_monitor_api.disable_all_monitors()


def demo_health_monitoring():
    """演示健康状态监控"""
    print("\n" + "="*60)
    print("演示3: 健康状态监控")
    print("="*60)
    
    from app.monitors import get_manager
    from app.monitors.database_monitor import get_monitor as get_db_monitor
    
    manager = get_manager()
    manager.enable_all()
    
    db_monitor = get_db_monitor()
    
    # 模拟一些数据库操作
    print("\n模拟数据库操作...")
    
    # 正常查询
    for i in range(10):
        db_monitor.record_query(
            operation='select',
            duration=random.uniform(0.01, 0.1),
            table_name='users',
            rows_affected=random.randint(1, 50),
            success=True
        )
    
    # 添加一些慢查询
    for i in range(3):
        db_monitor.record_query(
            operation='select',
            duration=random.uniform(1.0, 2.0),
            table_name='orders',
            rows_affected=random.randint(100, 1000),
            success=True
        )
    
    # 添加失败的查询
    for i in range(2):
        db_monitor.record_query(
            operation='insert',
            duration=random.uniform(0.05, 0.1),
            table_name='users',
            success=False,
            error_message='Duplicate key error'
        )
    
    print("✓ 已模拟 15 个查询操作")
    
    # 等待收集性能数据
    time.sleep(2)
    
    # 获取健康状态
    print("\n=== 健康状态评估 ===")
    health = manager.get_health_status()
    
    print(f"健康评分: {health['health_score']}/100")
    print(f"健康等级: {health['health_level']}")
    print(f"系统状态: {health['status']}")
    
    if health['issues']:
        print(f"\n检测到 {len(health['issues'])} 个问题:")
        for i, issue in enumerate(health['issues'], 1):
            print(f"  {i}. {issue}")
    else:
        print("\n✓ 系统运行正常，未检测到问题")
    
    print("\n关键指标:")
    metrics = health['metrics']
    print(f"  CPU使用率: {metrics['cpu_percent']}%")
    print(f"  内存使用率: {metrics['memory_percent']}%")
    print(f"  平均查询时间: {metrics['avg_query_time']}秒")
    print(f"  慢查询数量: {metrics['slow_queries_count']}")
    print(f"  查询失败率: {metrics['query_failure_rate']}%")
    
    manager.disable_all()


def demo_summary_report():
    """演示摘要报告"""
    print("\n" + "="*60)
    print("演示4: 综合摘要报告")
    print("="*60)
    
    from app.monitors import unified_monitor_api
    from app.monitors.database_monitor import get_monitor as get_db_monitor
    
    # 启用监控
    unified_monitor_api.enable_all_monitors()
    
    db_monitor = get_db_monitor()
    
    # 模拟一段时间的操作
    print("\n模拟系统运行...")
    
    operations = [
        ('select', 'users', 0.05, 10),
        ('select', 'products', 0.08, 20),
        ('insert', 'orders', 0.12, 1),
        ('update', 'users', 0.15, 1),
        ('select', 'orders', 0.45, 100),
        ('delete', 'cache', 0.03, 5),
    ]
    
    for _ in range(3):
        for op, table, base_time, rows in operations:
            db_monitor.record_query(
                operation=op,
                duration=base_time + random.uniform(-0.02, 0.05),
                table_name=table,
                rows_affected=rows + random.randint(-2, 5),
                success=random.random() > 0.05  # 95%成功率
            )
            time.sleep(0.1)
    
    print("✓ 模拟完成")
    
    # 获取摘要报告
    print("\n" + "="*60)
    print("=== 综合摘要报告 ===")
    print("="*60)
    
    response = unified_monitor_api.get_summary_report()
    report = response['data']
    
    # 健康状态
    print("\n【健康状态】")
    health = report['health']
    print(f"  评分: {health['health_score']}/100")
    print(f"  等级: {health['health_level']}")
    print(f"  状态: {health['status']}")
    
    # 性能指标
    print("\n【性能指标】")
    perf = report['performance']
    print(f"  CPU使用率: {perf['cpu_percent']}%")
    print(f"  内存使用率: {perf['memory_percent']}%")
    print(f"  内存占用: {perf['memory_mb']}MB")
    print(f"  线程数: {perf['thread_count']}")
    
    # 数据库指标
    print("\n【数据库指标】")
    db = report['database']
    print(f"  总查询数: {db['total_queries']}")
    print(f"  成功查询: {db['successful_queries']}")
    print(f"  失败查询: {db['failed_queries']}")
    print(f"  平均查询时间: {db['avg_query_time']}秒")
    print(f"  QPS: {db['queries_per_second']}")
    print(f"  慢查询数: {db['slow_queries_count']}")
    
    # 监视器状态
    print("\n【监视器状态】")
    monitors = report['monitors_status']
    print(f"  所有监视器: {'已启用' if monitors['all_enabled'] else '已禁用'}")
    
    unified_monitor_api.disable_all_monitors()


def demo_continuous_monitoring():
    """演示持续监控"""
    print("\n" + "="*60)
    print("演示5: 持续监控（10秒）")
    print("="*60)
    
    from app.monitors import unified_monitor_api
    from app.monitors.database_monitor import get_monitor as get_db_monitor
    
    # 启用监控
    unified_monitor_api.enable_all_monitors()
    print("✓ 监控已启动\n")
    
    db_monitor = get_db_monitor()
    
    # 持续监控10秒
    start_time = time.time()
    check_count = 0
    
    while time.time() - start_time < 10:
        # 模拟一些数据库操作
        for _ in range(random.randint(1, 3)):
            db_monitor.record_query(
                operation=random.choice(['select', 'insert', 'update']),
                duration=random.uniform(0.01, 0.3),
                table_name=random.choice(['users', 'orders', 'products']),
                rows_affected=random.randint(1, 50),
                success=random.random() > 0.05
            )
        
        # 每2秒检查一次健康状态
        if check_count % 4 == 0:
            response = unified_monitor_api.get_health_status()
            health = response['data']
            
            elapsed = time.time() - start_time
            print(f"[{elapsed:.1f}s] 健康评分: {health['health_score']}/100 "
                  f"({health['health_level']}) - "
                  f"CPU: {health['metrics']['cpu_percent']}% "
                  f"查询: {health['metrics']['slow_queries_count']}个慢查询")
            
            if health['issues']:
                for issue in health['issues']:
                    print(f"       ⚠️  {issue}")
        
        check_count += 1
        time.sleep(0.5)
    
    print("\n✓ 监控完成")
    
    # 最终报告
    print("\n=== 最终报告 ===")
    response = unified_monitor_api.get_summary_report()
    report = response['data']
    
    print(f"总查询数: {report['database']['total_queries']}")
    print(f"平均QPS: {report['database']['queries_per_second']:.2f}")
    print(f"最终健康评分: {report['health']['health_score']}/100")
    
    unified_monitor_api.disable_all_monitors()


def demo_individual_monitors():
    """演示分别访问各监视器"""
    print("\n" + "="*60)
    print("演示6: 分别访问各监视器")
    print("="*60)
    
    from app.monitors import unified_monitor_api
    from app.monitors.database_monitor import get_monitor as get_db_monitor
    
    # 启用所有监视器
    unified_monitor_api.enable_all_monitors()
    
    db_monitor = get_db_monitor()
    
    # 模拟一些数据库操作
    print("\n模拟数据库操作...")
    for i in range(20):
        db_monitor.record_query(
            operation=random.choice(['select', 'insert', 'update', 'delete']),
            duration=random.uniform(0.01, 0.5),
            table_name=random.choice(['users', 'orders', 'products', 'customers']),
            rows_affected=random.randint(1, 100),
            success=True
        )
    
    time.sleep(2)
    
    # 访问性能监视器
    print("\n=== 性能监视器数据 ===")
    response = unified_monitor_api.get_performance_snapshot()
    perf = response['data']
    
    print(f"CPU使用率: {perf['cpu_percent']}%")
    print(f"内存使用: {perf['memory_mb']}MB ({perf['memory_percent']}%)")
    print(f"进程数: {perf['process_count']}")
    print(f"线程数: {perf['thread_count']}")
    
    # 获取性能历史
    print("\n性能历史（最近5条）:")
    response = unified_monitor_api.get_performance_history(limit=5)
    for i, record in enumerate(response['data'], 1):
        print(f"  {i}. CPU: {record['cpu_percent']}%, "
              f"内存: {record['memory_mb']}MB")
    
    # 访问数据库监视器
    print("\n=== 数据库监视器数据 ===")
    response = unified_monitor_api.get_database_snapshot()
    db = response['data']
    
    print(f"总查询数: {db['total_queries']}")
    print(f"成功率: {db['successful_queries']}/{db['total_queries']}")
    print(f"平均查询时间: {db['avg_query_time']}秒")
    print(f"最大查询时间: {db['max_query_time']}秒")
    print(f"QPS: {db['queries_per_second']}")
    
    # 获取表统计
    print("\n表统计:")
    response = unified_monitor_api.get_table_statistics()
    for table, stats in response['data'].items():
        print(f"  {table}: {stats['total_queries']}次查询, "
              f"平均 {stats['avg_time']:.4f}秒")
    
    # 获取操作统计
    print("\n操作统计:")
    response = unified_monitor_api.get_operation_statistics()
    for operation, stats in response['data'].items():
        print(f"  {operation.upper()}: {stats['count']}次, "
              f"平均 {stats['avg_time']:.4f}秒")
    
    unified_monitor_api.disable_all_monitors()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("统一监视器系统演示程序")
    print("="*60)
    
    try:
        # 运行所有演示
        demo_basic_usage()
        demo_unified_api()
        demo_health_monitoring()
        demo_summary_report()
        demo_continuous_monitoring()
        demo_individual_monitors()
        
        print("\n" + "="*60)
        print("所有演示完成!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
