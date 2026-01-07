"""
性能监视器核心实现 [测试/示例模块]

提供性能数据收集、分析和管理功能

注意：此模块处于测试阶段，用于演示性能监控设计。
将在后续开发中根据实际需求进行改进、优化或移除。
"""

import psutil
import time
from datetime import datetime
from typing import Dict, Optional, Callable
from threading import Thread, Lock
import logging

from .metrics import PerformanceMetrics, MetricsSnapshot

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """性能监视器"""
    
    def __init__(self, 
                 sampling_interval: float = 1.0,
                 max_snapshots: int = 1000,
                 enabled: bool = False):
        """
        初始化性能监视器
        
        Args:
            sampling_interval: 采样间隔（秒）
            max_snapshots: 最大快照数量
            enabled: 是否启用自动采样
        """
        self.sampling_interval = sampling_interval
        self.max_snapshots = max_snapshots
        self.enabled = enabled
        self.metrics = PerformanceMetrics()
        self._lock = Lock()
        self._sampling_thread: Optional[Thread] = None
        self._running = False
        self._process = psutil.Process()
    
    def start(self) -> None:
        """启动性能监控"""
        if self._running:
            logger.warning("性能监视器已在运行中")
            return
        
        self._running = True
        self._sampling_thread = Thread(
            target=self._sampling_loop,
            daemon=True,
            name='PerformanceMonitor-Sampling'
        )
        self._sampling_thread.start()
        logger.info(f"性能监视器已启动，采样间隔: {self.sampling_interval}秒")
    
    def stop(self) -> None:
        """停止性能监控"""
        if not self._running:
            logger.warning("性能监视器未运行")
            return
        
        self._running = False
        if self._sampling_thread:
            self._sampling_thread.join(timeout=5)
        logger.info("性能监视器已停止")
    
    def _sampling_loop(self) -> None:
        """采样循环"""
        try:
            while self._running:
                try:
                    self.collect_metrics()
                    time.sleep(self.sampling_interval)
                except Exception as e:
                    logger.error(f"采样出错: {e}")
                    time.sleep(self.sampling_interval)
        except Exception as e:
            logger.error(f"采样循环错误: {e}")
    
    def collect_metrics(self) -> MetricsSnapshot:
        """收集性能指标"""
        try:
            cpu_percent = self._process.cpu_percent(interval=0.1)
            memory_info = self._process.memory_info()
            memory_percent = self._process.memory_percent()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            snapshot = MetricsSnapshot(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_mb=memory_mb,
                process_count=len(psutil.pids()),
                thread_count=self._process.num_threads(),
            )
            
            with self._lock:
                self.metrics.snapshots.append(snapshot)
                # 保持快照数量在限制内
                if len(self.metrics.snapshots) > self.max_snapshots:
                    self.metrics.snapshots = self.metrics.snapshots[-self.max_snapshots:]
            
            return snapshot
        except Exception as e:
            logger.error(f"收集指标失败: {e}")
            raise
    
    def record_task_timing(self, task_name: str, duration: float) -> None:
        """记录任务执行时间"""
        with self._lock:
            if task_name not in self.metrics.task_timings:
                self.metrics.task_timings[task_name] = []
            self.metrics.task_timings[task_name].append(duration)
    
    def get_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        with self._lock:
            return self.metrics
    
    def get_current_snapshot(self) -> Optional[MetricsSnapshot]:
        """获取最新快照"""
        with self._lock:
            if self.metrics.snapshots:
                return self.metrics.snapshots[-1]
            return None
    
    def get_summary(self) -> Dict:
        """获取性能摘要"""
        with self._lock:
            return self.metrics.get_summary()
    
    def clear_metrics(self) -> None:
        """清除所有指标"""
        with self._lock:
            self.metrics = PerformanceMetrics()
        logger.info("性能指标已清除")
    
    def reset_task_timing(self, task_name: Optional[str] = None) -> None:
        """重置任务计时"""
        with self._lock:
            if task_name:
                if task_name in self.metrics.task_timings:
                    del self.metrics.task_timings[task_name]
            else:
                self.metrics.task_timings.clear()
        logger.info(f"任务计时已重置: {task_name or '所有任务'}")


# 全局实例
_monitor_instance: Optional[PerformanceMonitor] = None


def get_monitor() -> PerformanceMonitor:
    """获取全局监视器实例"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = PerformanceMonitor()
    return _monitor_instance


def init_monitor(sampling_interval: float = 1.0, 
                 max_snapshots: int = 1000,
                 auto_start: bool = False) -> PerformanceMonitor:
    """初始化监视器"""
    global _monitor_instance
    _monitor_instance = PerformanceMonitor(
        sampling_interval=sampling_interval,
        max_snapshots=max_snapshots,
        enabled=auto_start
    )
    if auto_start:
        _monitor_instance.start()
    return _monitor_instance
