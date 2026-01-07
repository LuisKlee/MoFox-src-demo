"""
性能指标数据结构 [测试/示例模块]

定义性能监控的数据模型和指标记录

注意：此模块处于测试阶段，用于演示性能监控设计。
将在后续开发中根据实际需求进行改进、优化或移除。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import psutil


@dataclass
class MetricsSnapshot:
    """性能指标快照"""
    
    timestamp: datetime
    cpu_percent: float  # CPU使用百分比 (0-100)
    memory_percent: float  # 内存使用百分比 (0-100)
    memory_mb: float  # 内存使用MB数
    process_count: int  # 进程数
    thread_count: int  # 线程数
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': round(self.cpu_percent, 2),
            'memory_percent': round(self.memory_percent, 2),
            'memory_mb': round(self.memory_mb, 2),
            'process_count': self.process_count,
            'thread_count': self.thread_count,
        }


@dataclass
class PerformanceMetrics:
    """性能指标统计"""
    
    snapshots: List[MetricsSnapshot] = field(default_factory=list)
    task_timings: Dict[str, List[float]] = field(default_factory=dict)  # 任务名: [执行时间列表]
    
    @property
    def avg_cpu(self) -> float:
        """平均CPU使用率"""
        if not self.snapshots:
            return 0.0
        return sum(s.cpu_percent for s in self.snapshots) / len(self.snapshots)
    
    @property
    def max_cpu(self) -> float:
        """最大CPU使用率"""
        if not self.snapshots:
            return 0.0
        return max(s.cpu_percent for s in self.snapshots)
    
    @property
    def avg_memory(self) -> float:
        """平均内存使用百分比"""
        if not self.snapshots:
            return 0.0
        return sum(s.memory_percent for s in self.snapshots) / len(self.snapshots)
    
    @property
    def max_memory(self) -> float:
        """最大内存使用百分比"""
        if not self.snapshots:
            return 0.0
        return max(s.memory_percent for s in self.snapshots)
    
    def get_task_stats(self, task_name: str) -> Dict:
        """获取任务执行统计"""
        if task_name not in self.task_timings:
            return {
                'task_name': task_name,
                'count': 0,
                'avg_time': 0.0,
                'min_time': 0.0,
                'max_time': 0.0,
            }
        
        timings = self.task_timings[task_name]
        return {
            'task_name': task_name,
            'count': len(timings),
            'avg_time': round(sum(timings) / len(timings), 4),
            'min_time': round(min(timings), 4),
            'max_time': round(max(timings), 4),
            'total_time': round(sum(timings), 4),
        }
    
    def get_summary(self) -> Dict:
        """获取性能摘要"""
        return {
            'snapshots_count': len(self.snapshots),
            'cpu': {
                'average': round(self.avg_cpu, 2),
                'maximum': round(self.max_cpu, 2),
            },
            'memory': {
                'average': round(self.avg_memory, 2),
                'maximum': round(self.max_memory, 2),
            },
            'tasks': {
                task_name: self.get_task_stats(task_name)
                for task_name in self.task_timings.keys()
            },
        }
