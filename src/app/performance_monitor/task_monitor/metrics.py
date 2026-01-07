"""
任务管理器监视的数据结构和指标收集 [示例模块 - 将在后续开发中移除]

注意：此模块为示例模块，将在后续开发过程中移除。
如需持续使用，请根据实际需求进行改进或迁移。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class TaskEventType(Enum):
    """任务事件类型"""
    CREATED = "created"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRYING = "retrying"


@dataclass
class TaskEvent:
    """任务事件记录"""
    event_type: TaskEventType
    task_id: str
    task_name: str
    timestamp: datetime
    duration: Optional[float] = None  # 任务执行时间
    error: Optional[str] = None  # 错误信息
    metadata: Dict = field(default_factory=dict)  # 额外数据
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'event_type': self.event_type.value,
            'task_id': self.task_id,
            'task_name': self.task_name,
            'timestamp': self.timestamp.isoformat(),
            'duration': round(self.duration, 4) if self.duration else None,
            'error': self.error,
            'metadata': self.metadata,
        }


@dataclass
class TaskStats:
    """单个任务的统计信息"""
    task_name: str
    total_created: int = 0
    total_completed: int = 0
    total_failed: int = 0
    total_cancelled: int = 0
    total_timeout: int = 0
    total_retried: int = 0
    
    avg_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    
    executions: List[float] = field(default_factory=list)  # 所有执行时间
    
    def update_execution(self, duration: float):
        """更新执行时间"""
        self.executions.append(duration)
        self.total_completed += 1
        
        # 更新平均值
        self.avg_duration = sum(self.executions) / len(self.executions)
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'task_name': self.task_name,
            'total_created': self.total_created,
            'total_completed': self.total_completed,
            'total_failed': self.total_failed,
            'total_cancelled': self.total_cancelled,
            'total_timeout': self.total_timeout,
            'total_retried': self.total_retried,
            'success_rate': round(
                (self.total_completed / self.total_created * 100) 
                if self.total_created > 0 else 0,
                2
            ),
            'avg_duration': round(self.avg_duration, 4),
            'min_duration': round(self.min_duration, 4) if self.min_duration != float('inf') else 0.0,
            'max_duration': round(self.max_duration, 4),
            'execution_count': len(self.executions),
        }


@dataclass
class TaskManagerMetrics:
    """任务管理器监视指标"""
    events: List[TaskEvent] = field(default_factory=list)
    task_stats: Dict[str, TaskStats] = field(default_factory=dict)
    max_events: int = 10000  # 最大事件记录数
    
    @property
    def total_tasks_created(self) -> int:
        """总创建任务数"""
        return sum(s.total_created for s in self.task_stats.values())
    
    @property
    def total_tasks_completed(self) -> int:
        """总完成任务数"""
        return sum(s.total_completed for s in self.task_stats.values())
    
    @property
    def total_tasks_failed(self) -> int:
        """总失败任务数"""
        return sum(s.total_failed for s in self.task_stats.values())
    
    @property
    def total_tasks_cancelled(self) -> int:
        """总取消任务数"""
        return sum(s.total_cancelled for s in self.task_stats.values())
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_tasks_created == 0:
            return 0.0
        return round(
            (self.total_tasks_completed / self.total_tasks_created * 100),
            2
        )
    
    def record_event(self, event: TaskEvent):
        """记录事件"""
        self.events.append(event)
        
        # 保持事件数量在限制内
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # 更新任务统计
        if event.task_name not in self.task_stats:
            self.task_stats[event.task_name] = TaskStats(task_name=event.task_name)
        
        stats = self.task_stats[event.task_name]
        
        if event.event_type == TaskEventType.CREATED:
            stats.total_created += 1
        elif event.event_type == TaskEventType.COMPLETED:
            if event.duration:
                stats.update_execution(event.duration)
        elif event.event_type == TaskEventType.FAILED:
            stats.total_failed += 1
        elif event.event_type == TaskEventType.CANCELLED:
            stats.total_cancelled += 1
        elif event.event_type == TaskEventType.TIMEOUT:
            stats.total_timeout += 1
        elif event.event_type == TaskEventType.RETRYING:
            stats.total_retried += 1
    
    def get_task_stats(self, task_name: str) -> Optional[Dict]:
        """获取任务统计"""
        if task_name in self.task_stats:
            return self.task_stats[task_name].to_dict()
        return None
    
    def get_all_tasks_stats(self) -> Dict[str, Dict]:
        """获取所有任务统计"""
        return {
            name: stats.to_dict()
            for name, stats in self.task_stats.items()
        }
    
    def get_summary(self) -> Dict:
        """获取监视摘要"""
        return {
            'total_created': self.total_tasks_created,
            'total_completed': self.total_tasks_completed,
            'total_failed': self.total_tasks_failed,
            'total_cancelled': self.total_tasks_cancelled,
            'total_timeout': self.total_tasks_timeout,
            'success_rate': self.success_rate,
            'unique_tasks': len(self.task_stats),
            'events_count': len(self.events),
        }
    
    def clear(self):
        """清除所有数据"""
        self.events.clear()
        self.task_stats.clear()
