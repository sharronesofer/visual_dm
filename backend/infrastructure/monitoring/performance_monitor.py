"""
Infrastructure Performance Monitor

Monitors and tracks performance metrics for all systems.
Provides real-time performance monitoring and optimization insights.
"""

import asyncio
import gc
import logging
import psutil
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
from uuid import uuid4
from pathlib import Path
from threading import Lock

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Types of performance metrics to track"""
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DATABASE_QUERY_TIME = "database_query_time"
    CACHE_HIT_RATE = "cache_hit_rate"
    SYSTEM_RESPONSE_TIME = "system_response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"


@dataclass
class OperationMetrics:
    """Metrics for a specific operation type"""
    operation_name: str
    total_calls: int = 0
    success_count: int = 0
    error_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    last_execution_time_ms: float = 0.0
    
    @property
    def average_time_ms(self) -> float:
        """Calculate average execution time"""
        if self.total_calls == 0:
            return 0.0
        return self.total_time_ms / self.total_calls
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage"""
        if self.total_calls == 0:
            return 0.0
        return (self.success_count / self.total_calls) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate as a percentage"""
        if self.total_calls == 0:
            return 0.0
        return (self.error_count / self.total_calls) * 100


@dataclass
class PerformanceSnapshot:
    """Snapshot of system performance at a point in time"""
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    active_threads: int
    open_file_descriptors: int
    
    # Generic operation metrics
    database_query_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    average_response_time_ms: float = 0.0
    system_health_score: float = 0.0
    
    # Custom metrics can be added by individual systems
    custom_metrics: Dict[str, float] = field(default_factory=dict)


class PerformanceMonitor:
    """
    Comprehensive performance monitoring for all systems
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Performance data storage
        self.snapshots = deque(maxlen=1000)  # Keep last 1000 snapshots
        self.operation_metrics: Dict[str, OperationMetrics] = {}
        self.timing_data = defaultdict(list)
        
        # System monitoring
        self.process = psutil.Process()
        self.monitoring_enabled = True
        self.snapshot_interval = self.config.get('snapshot_interval', 30)  # seconds
        self.last_snapshot_time = datetime.now()
        
        # Performance thresholds
        self.thresholds = {
            'high_cpu_percent': self.config.get('high_cpu_percent', 80.0),
            'high_memory_percent': self.config.get('high_memory_percent', 85.0),
            'slow_operation_ms': self.config.get('slow_operation_ms', 1000.0),
            'high_error_rate': self.config.get('high_error_rate', 0.05),  # 5%
            'low_cache_hit_rate': self.config.get('low_cache_hit_rate', 0.7)  # 70%
        }
        
        # Optimization tracking
        self.optimization_suggestions: List[Dict[str, Any]] = []
        self.performance_alerts: List[Dict[str, Any]] = []
        
        # Thread safety
        self.metrics_lock = Lock()
        
        # Current operation tracking
        self.active_operations: Dict[str, datetime] = {}
        
        logger.info("Performance Monitor initialized")
    
    async def initialize(self) -> None:
        """Initialize performance monitoring"""
        try:
            # Start background monitoring task
            if self.monitoring_enabled:
                asyncio.create_task(self._background_monitoring())
            
            # Initial snapshot
            await self.take_performance_snapshot()
            
            logger.info("Performance Monitor initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Performance Monitor: {e}")
            raise
    
    def start_operation(self, operation_name: str) -> str:
        """Start timing an operation and return a context ID"""
        context_id = f"{operation_name}_{int(time.time() * 1000000)}"
        self.active_operations[context_id] = datetime.now()
        return context_id
    
    def end_operation(self, context_id: str, success: bool = True, 
                     operation_name: Optional[str] = None) -> float:
        """End timing an operation and record metrics"""
        try:
            start_time = self.active_operations.pop(context_id, None)
            if not start_time:
                logger.warning(f"No start time found for operation context: {context_id}")
                return 0.0
            
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Extract operation name if not provided
            if not operation_name:
                operation_name = context_id.split('_')[0] if '_' in context_id else context_id
            
            # Record metrics
            with self.metrics_lock:
                if operation_name not in self.operation_metrics:
                    self.operation_metrics[operation_name] = OperationMetrics(operation_name)
                
                metrics = self.operation_metrics[operation_name]
                metrics.total_calls += 1
                metrics.total_time_ms += execution_time_ms
                metrics.last_execution_time_ms = execution_time_ms
                
                if success:
                    metrics.success_count += 1
                else:
                    metrics.error_count += 1
                
                # Update min/max times
                metrics.min_time_ms = min(metrics.min_time_ms, execution_time_ms)
                metrics.max_time_ms = max(metrics.max_time_ms, execution_time_ms)
                
                # Check for performance issues
                self._check_performance_thresholds(operation_name, execution_time_ms, success)
            
            return execution_time_ms
            
        except Exception as e:
            logger.error(f"Error ending operation {context_id}: {e}")
            return 0.0
    
    def _check_performance_thresholds(self, operation_name: str, execution_time_ms: float, success: bool):
        """Check if operation performance exceeds thresholds"""
        try:
            # Check for slow operations
            if execution_time_ms > self.thresholds['slow_operation_ms']:
                self.performance_alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'slow_operation',
                    'operation': operation_name,
                    'execution_time_ms': execution_time_ms,
                    'threshold_ms': self.thresholds['slow_operation_ms']
                })
            
            # Check error rate for this operation
            metrics = self.operation_metrics[operation_name]
            if metrics.total_calls >= 10 and metrics.error_rate > self.thresholds['high_error_rate'] * 100:
                self.performance_alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'high_error_rate',
                    'operation': operation_name,
                    'error_rate': metrics.error_rate,
                    'threshold': self.thresholds['high_error_rate'] * 100
                })
                
        except Exception as e:
            logger.error(f"Error checking performance thresholds: {e}")
    
    async def take_performance_snapshot(self) -> PerformanceSnapshot:
        """Take a snapshot of current system performance"""
        try:
            # System metrics
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            # Thread and file descriptor counts
            try:
                thread_count = self.process.num_threads()
            except (psutil.AccessDenied, AttributeError):
                thread_count = 0
            
            try:
                fd_count = self.process.num_fds() if hasattr(self.process, 'num_fds') else 0
            except (psutil.AccessDenied, AttributeError):
                fd_count = 0
            
            # Create snapshot
            snapshot = PerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_usage_percent=cpu_percent,
                memory_usage_mb=memory_info.rss / 1024 / 1024,  # Convert to MB
                memory_usage_percent=memory_percent,
                active_threads=thread_count,
                open_file_descriptors=fd_count
            )
            
            # Add system-specific metrics
            self._populate_custom_metrics(snapshot)
            
            # Store snapshot
            self.snapshots.append(snapshot)
            self.last_snapshot_time = datetime.now()
            
            # Check system health thresholds
            self._check_system_health_thresholds(snapshot)
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error taking performance snapshot: {e}")
            # Return minimal snapshot on error
            return PerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_usage_percent=0,
                memory_usage_mb=0,
                memory_usage_percent=0,
                active_threads=0,
                open_file_descriptors=0
            )
    
    def _populate_custom_metrics(self, snapshot: PerformanceSnapshot) -> None:
        """Populate custom metrics in the snapshot - override in subclasses"""
        try:
            with self.metrics_lock:
                # Get recent operation metrics
                db_metrics = self.operation_metrics.get('database_query')
                if db_metrics:
                    snapshot.database_query_time_ms = db_metrics.average_time_ms
                
                # Calculate cache hit rate from recent data
                cache_metrics = [
                    (timestamp, value) for timestamp, value in self.timing_data.get('cache_hit_rate', [])
                    if (datetime.now() - timestamp).total_seconds() < 300  # Last 5 minutes
                ]
                if cache_metrics:
                    snapshot.cache_hit_rate = sum(value for _, value in cache_metrics) / len(cache_metrics)
                
                # Calculate average response time
                all_operations = list(self.operation_metrics.values())
                if all_operations:
                    total_avg_time = sum(op.average_time_ms for op in all_operations)
                    snapshot.average_response_time_ms = total_avg_time / len(all_operations)
                
                # Calculate system health score
                snapshot.system_health_score = self._calculate_system_health_score()
                
        except Exception as e:
            logger.error(f"Error populating custom metrics: {e}")
    
    def _check_system_health_thresholds(self, snapshot: PerformanceSnapshot):
        """Check if system metrics exceed health thresholds"""
        try:
            if snapshot.cpu_usage_percent > self.thresholds['high_cpu_percent']:
                self.performance_alerts.append({
                    'timestamp': snapshot.timestamp.isoformat(),
                    'type': 'high_cpu_usage',
                    'cpu_percent': snapshot.cpu_usage_percent,
                    'threshold': self.thresholds['high_cpu_percent']
                })
            
            if snapshot.memory_usage_percent > self.thresholds['high_memory_percent']:
                self.performance_alerts.append({
                    'timestamp': snapshot.timestamp.isoformat(),
                    'type': 'high_memory_usage',
                    'memory_percent': snapshot.memory_usage_percent,
                    'memory_mb': snapshot.memory_usage_mb,
                    'threshold': self.thresholds['high_memory_percent']
                })
                
        except Exception as e:
            logger.error(f"Error checking system health thresholds: {e}")
    
    def _calculate_system_health_score(self) -> float:
        """Calculate an overall system health score (0-100)"""
        try:
            recent_snapshot = self.snapshots[-1] if self.snapshots else None
            if not recent_snapshot:
                return 0.0
            
            # Base score starts at 100
            health_score = 100.0
            
            # Deduct for high CPU usage
            if recent_snapshot.cpu_usage_percent > self.thresholds['high_cpu_percent']:
                health_score -= (recent_snapshot.cpu_usage_percent - self.thresholds['high_cpu_percent'])
            
            # Deduct for high memory usage
            if recent_snapshot.memory_usage_percent > self.thresholds['high_memory_percent']:
                health_score -= (recent_snapshot.memory_usage_percent - self.thresholds['high_memory_percent'])
            
            # Deduct for high error rates
            with self.metrics_lock:
                total_calls = sum(m.total_calls for m in self.operation_metrics.values())
                total_errors = sum(m.error_count for m in self.operation_metrics.values())
                if total_calls > 0:
                    overall_error_rate = total_errors / total_calls
                    if overall_error_rate > self.thresholds['high_error_rate']:
                        health_score -= (overall_error_rate - self.thresholds['high_error_rate']) * 100
            
            # Ensure score is between 0 and 100
            return max(0.0, min(100.0, health_score))
            
        except Exception as e:
            logger.error(f"Error calculating system health score: {e}")
            return 0.0
    
    async def _background_monitoring(self):
        """Background task for periodic performance monitoring"""
        while self.monitoring_enabled:
            try:
                await asyncio.sleep(self.snapshot_interval)
                await self.take_performance_snapshot()
                
                # Clean up old timing data (keep last 1 hour)
                cutoff_time = datetime.now() - timedelta(hours=1)
                for metric_name in list(self.timing_data.keys()):
                    self.timing_data[metric_name] = [
                        (timestamp, value) for timestamp, value in self.timing_data[metric_name]
                        if timestamp > cutoff_time
                    ]
                
            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a comprehensive performance summary"""
        try:
            recent_snapshot = self.snapshots[-1] if self.snapshots else None
            
            with self.metrics_lock:
                operation_count = len(self.operation_metrics)
                total_calls = sum(m.total_calls for m in self.operation_metrics.values())
                total_errors = sum(m.error_count for m in self.operation_metrics.values())
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'system_health_score': self._calculate_system_health_score(),
                    'current_performance': {
                        'cpu_usage_percent': recent_snapshot.cpu_usage_percent if recent_snapshot else 0,
                        'memory_usage_mb': recent_snapshot.memory_usage_mb if recent_snapshot else 0,
                        'memory_usage_percent': recent_snapshot.memory_usage_percent if recent_snapshot else 0,
                        'active_threads': recent_snapshot.active_threads if recent_snapshot else 0
                    },
                    'operation_statistics': {
                        'tracked_operations': operation_count,
                        'total_calls': total_calls,
                        'total_errors': total_errors,
                        'overall_error_rate': total_errors / max(1, total_calls)
                    },
                    'monitoring_status': {
                        'is_enabled': self.monitoring_enabled,
                        'snapshots_taken': len(self.snapshots),
                        'last_snapshot': self.last_snapshot_time.isoformat(),
                        'active_alerts': len(self.performance_alerts)
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        return self.performance_alerts[-count:] if self.performance_alerts else []
    
    def clear_alerts(self) -> None:
        """Clear all performance alerts"""
        self.performance_alerts.clear()
        logger.info("Performance alerts cleared")
    
    def reset_metrics(self) -> None:
        """Reset all performance metrics"""
        with self.metrics_lock:
            self.operation_metrics.clear()
            self.timing_data.clear()
            self.performance_alerts.clear()
            self.optimization_suggestions.clear()
        
        logger.info("Performance metrics reset")
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring"""
        self.monitoring_enabled = False
        logger.info("Performance monitoring stopped")
    
    def start_monitoring(self) -> None:
        """Start background monitoring"""
        if not self.monitoring_enabled:
            self.monitoring_enabled = True
            asyncio.create_task(self._background_monitoring())
            logger.info("Performance monitoring started") 