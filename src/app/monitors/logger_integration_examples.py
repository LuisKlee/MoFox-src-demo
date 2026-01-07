"""
监视器与日志系统集成示例

演示如何将监视器数据集成到日志系统中
"""

import time
import logging
from app.monitors import setup_monitor_logger_integration


def example_basic_integration():
    """基本集成示例"""
    print("=== 基本集成示例 ===\n")
    
    # 初始化集成
    integration = setup_monitor_logger_integration(
        app_name="myapp",
        log_dir="logs",
        enable_storage=True
    )
    
    # 启动监视器
    integration.start()
    
    # 模拟应用运行
    for i in range(5):
        print(f"循环 {i+1}...")
        
        # 记录性能指标
        integration.log_performance_metrics()
        
        # 记录数据库指标
        integration.log_database_metrics()
        
        # 检查并记录健康状态
        integration.check_and_log_health()
        
        # 检查慢查询
        integration.log_slow_queries(threshold=0.5, limit=5)
        
        time.sleep(1)
    
    # 停止监视器
    integration.stop()
    
    print("\n✓ 基本集成示例完成")


def example_continuous_monitoring():
    """连续监控示例"""
    print("\n=== 连续监控示例 ===\n")
    
    integration = setup_monitor_logger_integration(
        app_name="continuous_monitor",
        log_dir="logs",
        enable_storage=True
    )
    
    integration.start()
    
    # 模拟30秒的连续监控
    print("启动30秒的连续监控...")
    start_time = time.time()
    check_interval = 5  # 每5秒检查一次
    report_interval = 15  # 每15秒生成一份报告
    
    last_check = time.time()
    last_report = time.time()
    
    while time.time() - start_time < 30:
        current_time = time.time()
        
        # 定期检查健康状态
        if current_time - last_check >= check_interval:
            integration.check_and_log_health()
            last_check = current_time
        
        # 定期生成综合报告
        if current_time - last_report >= report_interval:
            integration.log_comprehensive_report()
            last_report = current_time
        
        time.sleep(1)
    
    integration.stop()
    
    print("\n✓ 连续监控示例完成")


def example_alert_monitoring():
    """告警监控示例"""
    print("\n=== 告警监控示例 ===\n")
    
    integration = setup_monitor_logger_integration(
        app_name="alert_monitor",
        log_dir="logs",
        enable_storage=True
    )
    
    integration.start()
    
    logger = integration.logger
    alert_logger = integration.alert_logger
    
    # 模拟不同的告警场景
    print("模拟告警监控...")
    
    for i in range(3):
        print(f"检查周期 {i+1}...")
        
        # 检查健康状态并检测问题
        health = integration.check_and_log_health()
        
        # 如果有问题，记录详细信息
        if health.get('issues'):
            alert_logger.warning(
                f"检测到 {len(health['issues'])} 个问题",
                extra={
                    "issues_count": len(health['issues']),
                    "issues": health['issues'],
                }
            )
        else:
            logger.info("系统运行正常")
        
        # 检查慢查询
        integration.log_slow_queries(threshold=0.3)
        
        time.sleep(2)
    
    integration.stop()
    
    print("\n✓ 告警监控示例完成")


def example_report_export():
    """报告导出示例"""
    print("\n=== 报告导出示例 ===\n")
    
    integration = setup_monitor_logger_integration(
        app_name="report_export",
        log_dir="logs",
        enable_storage=True
    )
    
    integration.start()
    
    # 运行一段时间
    print("收集监控数据...")
    for i in range(5):
        integration.check_and_log_health()
        integration.log_performance_metrics()
        integration.log_database_metrics()
        time.sleep(1)
    
    # 生成综合报告
    print("\n生成综合报告...")
    integration.log_comprehensive_report()
    
    # 导出监控报告
    print("导出监控报告...")
    report_file = integration.export_monitoring_report()
    print(f"✓ 报告已导出到: {report_file}")
    
    # 如果使用了存储集成，获取日志统计
    logs = integration.get_monitor_logs(days=1)
    if logs:
        print("\n日志统计信息:")
        print(f"  总日志数: {logs.get('total_logs', 0)}")
        print(f"  DEBUG: {logs.get('debug_count', 0)}")
        print(f"  INFO: {logs.get('info_count', 0)}")
        print(f"  WARNING: {logs.get('warning_count', 0)}")
        print(f"  ERROR: {logs.get('error_count', 0)}")
    
    integration.stop()
    
    print("\n✓ 报告导出示例完成")


def example_with_logger_system():
    """与完整日志系统集成示例"""
    print("\n=== 与日志系统完整集成示例 ===\n")
    
    from kernel.logger import get_logger, setup_logger, LoggerConfig
    
    # 使用完整的日志配置
    config = LoggerConfig(
        level="DEBUG",
        console_enabled=True,
        console_colors=True,
        file_enabled=True,
        file_path="logs/monitor_integration.log",
        include_metadata=True
    )
    
    setup_logger(config)
    
    # 初始化监视器日志集成
    integration = setup_monitor_logger_integration(
        app_name="full_integration",
        log_dir="logs",
        enable_storage=True
    )
    
    # 获取自定义日志器
    app_logger = get_logger("myapp")
    
    integration.start()
    
    print("运行应用并记录日志...\n")
    
    # 应用日志
    app_logger.info("应用启动")
    
    # 监控检查
    integration.check_and_log_health()
    integration.log_performance_metrics()
    
    app_logger.debug("执行核心业务逻辑")
    
    # 再次检查
    integration.check_and_log_health()
    
    app_logger.info("应用运行正常")
    
    integration.stop()
    
    print("\n✓ 完整集成示例完成")


if __name__ == "__main__":
    # 运行所有示例
    try:
        example_basic_integration()
        example_alert_monitoring()
        example_report_export()
        
        print("\n" + "="*50)
        print("所有示例完成！")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 示例执行失败: {e}")
        import traceback
        traceback.print_exc()
