"""
数据库监视器演示示例

演示如何使用数据库监视器进行数据库操作监控

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
    
    from app.monitors.database_monitor import get_monitor
    
    # 获取监视器实例
    monitor = get_monitor()
    
    # 启用监控
    monitor.enable()
    print("✓ 监控已启用")
    
    # 模拟一些数据库查询
    print("\n执行数据库查询...")
    
    # SELECT查询
    monitor.record_query(
        operation='select',
        duration=0.125,
        table_name='users',
        rows_affected=10,
        success=True
    )
    print("  - SELECT查询已记录 (0.125秒, 10行)")
    
    # INSERT查询
    monitor.record_query(
        operation='insert',
        duration=0.089,
        table_name='users',
        rows_affected=1,
        success=True
    )
    print("  - INSERT查询已记录 (0.089秒, 1行)")
    
    # 慢查询
    monitor.record_query(
        operation='select',
        duration=1.523,
        table_name='orders',
        rows_affected=1000,
        success=True
    )
    print("  - 慢SELECT查询已记录 (1.523秒, 1000行)")
    
    # 失败的查询
    monitor.record_query(
        operation='update',
        duration=0.056,
        table_name='users',
        success=False,
        error_message='Duplicate key error'
    )
    print("  - 失败的UPDATE查询已记录")
    
    # 获取当前快照
    print("\n获取当前状态快照...")
    snapshot = monitor.get_current_snapshot()
    print(f"\n当前数据库状态:")
    print(f"  总查询数: {snapshot.total_queries}")
    print(f"  成功: {snapshot.successful_queries}, 失败: {snapshot.failed_queries}")
    print(f"  平均查询时间: {snapshot.avg_query_time:.4f}秒")
    print(f"  最大查询时间: {snapshot.max_query_time:.4f}秒")
    print(f"  慢查询数量: {snapshot.slow_queries_count}")


def demo_decorator_pattern():
    """演示装饰器模式"""
    print("\n" + "="*60)
    print("演示2: 装饰器模式")
    print("="*60)
    
    from app.monitors.database_monitor import get_monitor
    
    monitor = get_monitor()
    monitor.enable()
    
    # 使用装饰器监控函数
    @monitor.monitor_query('select', 'users')
    def get_user_by_id(user_id: int):
        """模拟查询用户"""
        time.sleep(random.uniform(0.01, 0.1))
        return {'id': user_id, 'name': f'User{user_id}'}
    
    @monitor.monitor_query('insert', 'users')
    def create_user(user_data: dict):
        """模拟创建用户"""
        time.sleep(random.uniform(0.02, 0.08))
        return {'id': random.randint(1, 1000), **user_data}
    
    @monitor.monitor_query('update', 'users')
    def update_user(user_id: int, data: dict):
        """模拟更新用户"""
        time.sleep(random.uniform(0.03, 0.12))
        return True
    
    print("\n执行被监控的函数...")
    
    # 执行一些操作
    for i in range(5):
        user = get_user_by_id(i + 1)
        print(f"  - 查询用户: {user}")
    
    new_user = create_user({'name': 'Alice', 'email': 'alice@example.com'})
    print(f"  - 创建用户: {new_user}")
    
    update_user(1, {'email': 'newemail@example.com'})
    print(f"  - 更新用户成功")
    
    # 查看统计
    print("\n查看操作统计:")
    stats = monitor.get_operation_statistics()
    for operation, data in stats.items():
        print(f"  {operation.upper()}: {data['count']}次, 平均 {data['avg_time']:.4f}秒")


def demo_api_interface():
    """演示API接口"""
    print("\n" + "="*60)
    print("演示3: API接口")
    print("="*60)
    
    from app.monitors.database_monitor import database_api
    
    # 启用监控
    response = database_api.enable_monitoring()
    print(f"✓ {response['message']}")
    
    # 设置慢查询阈值
    response = database_api.set_slow_query_threshold(0.5)
    print(f"✓ {response['message']}")
    
    # 模拟一些查询
    print("\n模拟数据库操作...")
    operations = [
        ('select', 'users', 0.123),
        ('select', 'orders', 0.234),
        ('insert', 'users', 0.089),
        ('update', 'users', 0.156),
        ('delete', 'orders', 0.067),
        ('select', 'products', 0.678),  # 慢查询
        ('select', 'users', 1.234),     # 慢查询
    ]
    
    for op, table, duration in operations:
        database_api.record_query(
            operation=op,
            duration=duration,
            table_name=table,
            rows_affected=random.randint(1, 100)
        )
        print(f"  - {op.upper()} {table} ({duration}秒)")
    
    # 获取当前快照
    print("\n获取当前快照...")
    response = database_api.get_current_snapshot()
    data = response['data']
    print(f"\n数据库状态:")
    print(f"  总查询数: {data['total_queries']}")
    print(f"  平均时间: {data['avg_query_time']}秒")
    print(f"  慢查询数: {data['slow_queries_count']}")
    
    # 获取表统计
    print("\n表统计信息:")
    response = database_api.get_table_statistics()
    for table, stats in response['data'].items():
        print(f"  {table}: {stats['total_queries']}次查询, "
              f"平均 {stats['avg_time']:.4f}秒")
    
    # 获取慢查询
    print("\n慢查询列表:")
    response = database_api.get_slow_queries(limit=10)
    for query in response['data']:
        print(f"  - {query['operation'].upper()} {query['table_name']}: "
              f"{query['duration']}秒")


def demo_connection_pool():
    """演示连接池监控"""
    print("\n" + "="*60)
    print("演示4: 连接池监控")
    print("="*60)
    
    from app.monitors.database_monitor import database_api
    
    database_api.enable_monitoring()
    
    # 模拟连接池状态变化
    print("\n模拟连接池状态变化...")
    
    scenarios = [
        (2, 8, 10, 20, "空闲状态"),
        (5, 5, 10, 20, "正常负载"),
        (8, 2, 10, 20, "高负载"),
        (10, 0, 10, 20, "满负载"),
        (3, 7, 10, 20, "恢复正常"),
    ]
    
    for active, idle, total, max_conn, desc in scenarios:
        database_api.update_connection_pool(
            active=active,
            idle=idle,
            total=total,
            max_connections=max_conn
        )
        
        response = database_api.get_connection_pool_status()
        status = response['data']
        
        print(f"\n{desc}:")
        print(f"  活动连接: {status['active']}")
        print(f"  空闲连接: {status['idle']}")
        print(f"  总连接数: {status['total']}/{status['max']}")
        print(f"  使用率: {status['active']/status['max']*100:.1f}%")
        
        time.sleep(0.5)


def demo_statistics():
    """演示统计功能"""
    print("\n" + "="*60)
    print("演示5: 统计分析")
    print("="*60)
    
    from app.monitors.database_monitor import get_monitor, database_api
    
    monitor = get_monitor()
    monitor.enable()
    
    # 模拟大量查询
    print("\n生成测试数据...")
    tables = ['users', 'orders', 'products', 'customers']
    operations = ['select', 'insert', 'update', 'delete']
    
    for _ in range(50):
        table = random.choice(tables)
        operation = random.choice(operations)
        duration = random.uniform(0.01, 2.0)
        
        monitor.record_query(
            operation=operation,
            duration=duration,
            table_name=table,
            rows_affected=random.randint(1, 100)
        )
    
    print(f"✓ 已生成 50 条查询记录")
    
    # 整体统计
    print("\n=== 整体统计 ===")
    response = database_api.get_current_snapshot()
    data = response['data']
    print(f"总查询数: {data['total_queries']}")
    print(f"成功率: {data['successful_queries']/data['total_queries']*100:.1f}%")
    print(f"平均时间: {data['avg_query_time']:.4f}秒")
    print(f"QPS: {data['queries_per_second']:.2f}")
    
    # 按操作类型统计
    print("\n=== 操作类型统计 ===")
    response = database_api.get_operation_statistics()
    for operation, stats in response['data'].items():
        print(f"{operation.upper():8s}: {stats['count']:3d}次, "
              f"平均 {stats['avg_time']:.4f}秒")
    
    # 按表统计
    print("\n=== 表访问统计 ===")
    response = database_api.get_table_statistics()
    for table, stats in response['data'].items():
        print(f"{table:12s}: {stats['total_queries']:3d}次, "
              f"平均 {stats['avg_time']:.4f}秒, "
              f"最大 {stats['max_time']:.4f}秒")
    
    # 慢查询分析
    print("\n=== 慢查询分析 (>0.5秒) ===")
    response = database_api.get_slow_queries(threshold=0.5, limit=10)
    print(f"慢查询总数: {response['count']}")
    if response['data']:
        print("\nTop 10 慢查询:")
        for i, query in enumerate(response['data'][:10], 1):
            print(f"{i:2d}. {query['operation'].upper():8s} {query['table_name']:12s} "
                  f"{query['duration']:.4f}秒 ({query['rows_affected']}行)")


def demo_real_world_scenario():
    """演示真实场景"""
    print("\n" + "="*60)
    print("演示6: 真实应用场景")
    print("="*60)
    
    from app.monitors.database_monitor import get_monitor
    
    monitor = get_monitor()
    monitor.enable()
    monitor.set_slow_query_threshold(0.2)
    
    print("\n模拟电商系统的数据库操作...")
    
    # 定义监控装饰器的函数
    @monitor.monitor_query('select', 'users')
    def authenticate_user(username: str, password: str):
        """用户认证"""
        time.sleep(random.uniform(0.05, 0.15))
        return True
    
    @monitor.monitor_query('select', 'products')
    def get_product_list(category: str):
        """获取产品列表"""
        time.sleep(random.uniform(0.1, 0.3))
        return [{'id': i} for i in range(20)]
    
    @monitor.monitor_query('select', 'products')
    def get_product_detail(product_id: int):
        """获取产品详情"""
        time.sleep(random.uniform(0.02, 0.08))
        return {'id': product_id, 'name': f'Product {product_id}'}
    
    @monitor.monitor_query('insert', 'orders')
    def create_order(user_id: int, items: list):
        """创建订单"""
        time.sleep(random.uniform(0.1, 0.25))
        return {'order_id': random.randint(1000, 9999)}
    
    @monitor.monitor_query('update', 'orders')
    def update_order_status(order_id: int, status: str):
        """更新订单状态"""
        time.sleep(random.uniform(0.05, 0.12))
        return True
    
    @monitor.monitor_query('select', 'orders')
    def get_user_orders(user_id: int):
        """获取用户订单"""
        time.sleep(random.uniform(0.15, 0.35))
        return [{'id': i} for i in range(5)]
    
    # 模拟用户行为
    print("\n用户行为流程:")
    
    # 1. 用户登录
    print("  1. 用户登录")
    authenticate_user('alice', 'password123')
    
    # 2. 浏览产品
    print("  2. 浏览产品列表")
    products = get_product_list('electronics')
    
    # 3. 查看多个产品详情
    print("  3. 查看产品详情")
    for i in range(5):
        get_product_detail(random.randint(1, 100))
    
    # 4. 创建订单
    print("  4. 创建订单")
    order = create_order(1, [1, 2, 3])
    
    # 5. 更新订单状态
    print("  5. 更新订单状态")
    update_order_status(order['order_id'], 'paid')
    
    # 6. 查看订单历史
    print("  6. 查看订单历史")
    orders = get_user_orders(1)
    
    # 显示统计结果
    print("\n" + "-"*60)
    snapshot = monitor.get_current_snapshot()
    print(f"\n性能统计:")
    print(f"  总请求数: {snapshot.total_queries}")
    print(f"  平均响应时间: {snapshot.avg_query_time:.4f}秒")
    print(f"  最大响应时间: {snapshot.max_query_time:.4f}秒")
    
    if snapshot.slow_queries_count > 0:
        print(f"\n⚠️  检测到 {snapshot.slow_queries_count} 个慢查询!")
        slow_queries = monitor.get_slow_queries(limit=5)
        print("\n慢查询详情:")
        for query in slow_queries:
            print(f"  - {query.operation.upper()} {query.table_name}: "
                  f"{query.duration:.4f}秒")
    
    print("\n操作分布:")
    ops = monitor.get_operation_statistics()
    for op, stats in ops.items():
        print(f"  {op.upper():8s}: {stats['count']:2d}次")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("数据库监视器演示程序")
    print("="*60)
    
    try:
        # 运行所有演示
        demo_basic_usage()
        demo_decorator_pattern()
        demo_api_interface()
        demo_connection_pool()
        demo_statistics()
        demo_real_world_scenario()
        
        print("\n" + "="*60)
        print("所有演示完成!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
