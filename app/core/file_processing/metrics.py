"""Performance metrics collection for the concurrent file processing system."""

import threading
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
from statistics import mean, median

@dataclass
class OperationMetrics:
    """Metrics for a single operation."""
    operation_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "pending"
    retries: int = 0
    error: Optional[str] = None

    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate operation duration if completed."""
        if self.end_time:
            return self.end_time - self.start_time
        return None

class MetricsCollector:
    """Collects and analyzes performance metrics for file operations."""
    
    def __init__(self, window_size: int = 1000):
        """Initialize metrics collector.
        
        Args:
            window_size: Number of recent operations to keep for rolling metrics.
        """
        self.window_size = window_size
        self._metrics_lock = threading.Lock()
        self._recent_operations = deque(maxlen=window_size)
        self._operation_counts: Dict[str, int] = {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        self._operation_type_counts: Dict[str, int] = {}
        self._start_time = datetime.now()

    def record_operation_start(self, operation_type: str) -> OperationMetrics:
        """Record the start of an operation."""
        metrics = OperationMetrics(
            operation_type=operation_type,
            start_time=datetime.now()
        )
        with self._metrics_lock:
            self._operation_counts["total"] += 1
            self._operation_type_counts[operation_type] = \
                self._operation_type_counts.get(operation_type, 0) + 1
        return metrics

    def record_operation_end(self, metrics: OperationMetrics, status: str, error: Optional[str] = None):
        """Record the completion of an operation."""
        metrics.end_time = datetime.now()
        metrics.status = status
        metrics.error = error
        
        with self._metrics_lock:
            self._recent_operations.append(metrics)
            if status == "completed":
                self._operation_counts["completed"] += 1
            elif status == "failed":
                self._operation_counts["failed"] += 1
            elif status == "cancelled":
                self._operation_counts["cancelled"] += 1

    def record_retry(self, metrics: OperationMetrics):
        """Record an operation retry."""
        metrics.retries += 1

    def get_metrics(self) -> Dict:
        """Get current performance metrics."""
        with self._metrics_lock:
            recent_ops = list(self._recent_operations)
            completed_ops = [op for op in recent_ops if op.status == "completed"]
            durations = [op.duration.total_seconds() for op in completed_ops if op.duration]
            
            metrics = {
                "operations": {
                    "total": self._operation_counts["total"],
                    "completed": self._operation_counts["completed"],
                    "failed": self._operation_counts["failed"],
                    "cancelled": self._operation_counts["cancelled"],
                    "by_type": dict(self._operation_type_counts)
                },
                "performance": {
                    "avg_duration": mean(durations) if durations else 0,
                    "median_duration": median(durations) if durations else 0,
                    "operations_per_second": len(completed_ops) / self.window_size \
                        if completed_ops else 0
                },
                "errors": {
                    "total": self._operation_counts["failed"],
                    "retry_rate": sum(1 for op in recent_ops if op.retries > 0) / \
                        len(recent_ops) if recent_ops else 0,
                    "recent_errors": [
                        {
                            "type": op.operation_type,
                            "error": op.error,
                            "retries": op.retries
                        }
                        for op in recent_ops
                        if op.status == "failed"
                    ][:10]  # Last 10 errors
                },
                "uptime": (datetime.now() - self._start_time).total_seconds()
            }
            
            return metrics

    def reset(self):
        """Reset all metrics."""
        with self._metrics_lock:
            self._recent_operations.clear()
            self._operation_counts = {
                "total": 0,
                "completed": 0,
                "failed": 0,
                "cancelled": 0
            }
            self._operation_type_counts.clear()
            self._start_time = datetime.now() 