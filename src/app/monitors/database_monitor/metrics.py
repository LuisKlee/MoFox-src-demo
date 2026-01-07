"""
数据库监控指标数据结构 [测试/示例模块]

定义数据库监控的各种指标和数据结构

注意：此模块处于测试阶段，用于演示数据库监控的设计模式。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


@dataclass
class QueryMetrics:
    """查询指标"""
    query_id: str
    operation: str  # select, insert, update, delete, etc.
    duration: float  # 执行时间（秒）
    timestamp: datetime
    table_name: Optional[str] = None
    rows_affected: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class ConnectionMetrics:
    """连接池指标"""
    timestamp: datetime
    active_connections: int = 0
    idle_connections: int = 0
    total_connections: int = 0
    max_connections: int = 0
    connection_wait_time: float = 0.0  # 平均等待时间（秒）


@dataclass
class DatabaseSnapshot:
    """数据库状态快照"""
    timestamp: datetime
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    avg_query_time: float = 0.0
    max_query_time: float = 0.0
    min_query_time: float = 0.0
    queries_per_second: float = 0.0
    
    # 连接池信息
    active_connections: int = 0
    idle_connections: int = 0
    total_connections: int = 0
    
    # 按操作类型统计
    operations_count: Dict[str, int] = field(default_factory=dict)
    
    # 慢查询数量（>1秒）
    slow_queries_count: int = 0


class DatabaseMetrics:
    """数据库指标管理"""
    
    def __init__(self, max_history: int = 10000):
        """
        初始化数据库指标管理器
        
        Args:
            max_history: 保存的最大历史记录数
        """
        self.max_history = max_history
        
        # 查询历史
        self.query_history: List[QueryMetrics] = []
        
        # 连接池历史
        self.connection_history: List[ConnectionMetrics] = []
        
        # 快照历史
        self.snapshots: List[DatabaseSnapshot] = []
        
        # 按表统计
        self.table_stats: Dict[str, Dict] = defaultdict(
            lambda: {
                'total_queries': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf')
            }
        )
        
        # 按操作类型统计
        self.operation_stats: Dict[str, Dict] = defaultdict(
            lambda: {
                'count': 0,
                'total_time': 0.0,
                'avg_time': 0.0
            }
        )
    
    def add_query(self, query: QueryMetrics) -> None:
        """添加查询记录"""
        self.query_history.append(query)
        
        # 更新按表统计
        if query.table_name:
            stats = self.table_stats[query.table_name]
            stats['total_queries'] += 1
            stats['total_time'] += query.duration
            stats['avg_time'] = stats['total_time'] / stats['total_queries']
            stats['max_time'] = max(stats['max_time'], query.duration)
            stats['min_time'] = min(stats['min_time'], query.duration)
        
        # 更新按操作类型统计
        op_stats = self.operation_stats[query.operation]
        op_stats['count'] += 1
        op_stats['total_time'] += query.duration
        op_stats['avg_time'] = op_stats['total_time'] / op_stats['count']
        
        # 限制历史记录数量
        if len(self.query_history) > self.max_history:
            self.query_history.pop(0)
    
    def add_connection_snapshot(self, metrics: ConnectionMetrics) -> None:
        """添加连接池快照"""
        self.connection_history.append(metrics)
        
        # 限制历史记录数量
        if len(self.connection_history) > self.max_history:
            self.connection_history.pop(0)
    
    def add_snapshot(self, snapshot: DatabaseSnapshot) -> None:
        """添加数据库快照"""
        self.snapshots.append(snapshot)
        
        # 限制快照数量
        if len(self.snapshots) > 1000:
            self.snapshots.pop(0)
    
    def get_recent_queries(self, limit: int = 100) -> List[QueryMetrics]:
        """获取最近的查询记录"""
        return self.query_history[-limit:]
    
    def get_slow_queries(self, threshold: float = 1.0, limit: int = 100) -> List[QueryMetrics]:
        """
        获取慢查询记录
        
        Args:
            threshold: 慢查询阈值（秒）
            limit: 返回数量限制
        """
        slow_queries = [
            q for q in self.query_history 
            if q.duration >= threshold
        ]
        return slow_queries[-limit:]
    
    def get_table_stats(self, table_name: Optional[str] = None) -> Dict:
        """
        获取表统计信息
        
        Args:
            table_name: 表名，如果为None则返回所有表的统计
        """
        if table_name:
            return dict(self.table_stats.get(table_name, {}))
        return {k: dict(v) for k, v in self.table_stats.items()}
    
    def get_operation_stats(self) -> Dict:
        """获取操作类型统计"""
        return {k: dict(v) for k, v in self.operation_stats.items()}
    
    def clear(self) -> None:
        """清空所有指标"""
        self.query_history.clear()
        self.connection_history.clear()
        self.snapshots.clear()
        self.table_stats.clear()
        self.operation_stats.clear()
    
    def get_summary(self) -> Dict:
        """获取整体统计摘要"""
        if not self.query_history:
            return {
                'total_queries': 0,
                'successful_queries': 0,
                'failed_queries': 0,
                'avg_query_time': 0.0,
                'max_query_time': 0.0,
                'min_query_time': 0.0,
            }
        
        durations = [q.duration for q in self.query_history if q.success]
        successful = sum(1 for q in self.query_history if q.success)
        failed = len(self.query_history) - successful
        
        return {
            'total_queries': len(self.query_history),
            'successful_queries': successful,
            'failed_queries': failed,
            'avg_query_time': sum(durations) / len(durations) if durations else 0.0,
            'max_query_time': max(durations) if durations else 0.0,
            'min_query_time': min(durations) if durations else 0.0,
        }
