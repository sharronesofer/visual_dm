"""
Performance Monitor

Monitors and tracks performance metrics for the chaos system.
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

from backend.systems.chaos.core.config import ChaosConfig

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Types of performance metrics to track"""
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    PRESSURE_CALCULATION_TIME = "pressure_calculation_time"
    EVENT_PROCESSING_TIME = "event_processing_time"
    DATABASE_QUERY_TIME = "database_query_time"
    CACHE_HIT_RATE = "cache_hit_rate"
    SYSTEM_RESPONSE_TIME = "system_response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"


@dataclass
class PerformanceSnapshot:
    """Point-in-time performance snapshot"""
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    active_threads: int
    chaos_engine_status: str
    
    # Chaos-specific metrics
    pressure_calculation_time_ms: float = 0.0
    event_processing_time_ms: float = 0.0
    chaos_score_calculation_time_ms: float = 0.0
    mitigation_processing_time_ms: float = 0.0
    
    # System integration metrics
    system_connection_count: int = 0
    failed_system_connections: int = 0
    event_dispatcher_latency_ms: float = 0.0
    
    # Performance indicators
    pressure_collection_success_rate: float = 1.0
    event_trigger_success_rate: float = 1.0
    cache_hit_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_mb': self.memory_usage_mb,
            'memory_usage_percent': self.memory_usage_percent,
            'active_threads': self.active_threads,
            'chaos_engine_status': self.chaos_engine_status,
            'pressure_calculation_time_ms': self.pressure_calculation_time_ms,
            'event_processing_time_ms': self.event_processing_time_ms,
            'chaos_score_calculation_time_ms': self.chaos_score_calculation_time_ms,
            'mitigation_processing_time_ms': self.mitigation_processing_time_ms,
            'system_connection_count': self.system_connection_count,
            'failed_system_connections': self.failed_system_connections,
            'event_dispatcher_latency_ms': self.event_dispatcher_latency_ms,
            'pressure_collection_success_rate': self.pressure_collection_success_rate,
            'event_trigger_success_rate': self.event_trigger_success_rate,
            'cache_hit_rate': self.cache_hit_rate
        }


@dataclass
class OperationMetrics:
    """Metrics for a specific operation"""
    operation_name: str
    total_calls: int = 0
    total_time_ms: float = 0.0
    success_count: int = 0
    error_count: int = 0
    last_execution_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    
    @property
    def average_time_ms(self) -> float:
        """Calculate average execution time"""
        return self.total_time_ms / max(1, self.total_calls)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        return self.success_count / max(1, self.total_calls)
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate"""
        return self.error_count / max(1, self.total_calls)


class PerformanceMonitor:
    """
    Comprehensive performance monitoring for the chaos system
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        
        # Performance data storage
        self.snapshots = deque(maxlen=1000)  # Keep last 1000 snapshots
        self.operation_metrics: Dict[str, OperationMetrics] = {}
        self.timing_data = defaultdict(list)
        
        # System monitoring
        self.process = psutil.Process()
        self.monitoring_enabled = True
        self.snapshot_interval = 30  # seconds
        self.last_snapshot_time = datetime.now()
        
        # Performance thresholds
        self.thresholds = {
            'high_cpu_percent': 80.0,
            'high_memory_percent': 85.0,
            'slow_operation_ms': 1000.0,
            'high_error_rate': 0.05,  # 5%
            'low_cache_hit_rate': 0.7  # 70%
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
    
    def record_metric(self, metric_type: PerformanceMetric, value: float, 
                     operation_name: Optional[str] = None) -> None:
        """Record a specific performance metric"""
        try:
            with self.metrics_lock:
                timestamp = datetime.now()
                metric_key = f"{metric_type.value}_{operation_name}" if operation_name else metric_type.value
                
                # Store in timing data for trend analysis
                self.timing_data[metric_key].append((timestamp, value))
                
                # Keep only recent data (last 1000 points)
                if len(self.timing_data[metric_key]) > 1000:
                    self.timing_data[metric_key] = self.timing_data[metric_key][-1000:]
                
                # Check thresholds
                self._check_metric_thresholds(metric_type, value, operation_name)
                
        except Exception as e:
            logger.error(f"Error recording metric {metric_type}: {e}")
    
    async def take_performance_snapshot(self) -> PerformanceSnapshot:
        """Take a comprehensive performance snapshot"""
        try:
            # Get system metrics
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            memory_percent = self.process.memory_percent()
            thread_count = self.process.num_threads()
            
            # Create snapshot
            snapshot = PerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_usage_percent=cpu_percent,
                memory_usage_mb=memory_mb,
                memory_usage_percent=memory_percent,
                active_threads=thread_count,
                chaos_engine_status="running"  # This should be updated by chaos engine
            )
            
            # Add chaos-specific metrics if available
            self._populate_chaos_metrics(snapshot)
            
            # Store snapshot
            self.snapshots.append(snapshot)
            self.last_snapshot_time = datetime.now()
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error taking performance snapshot: {e}")
            # Return a basic snapshot with error status
            return PerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_usage_percent=0.0,
                memory_usage_mb=0.0,
                memory_usage_percent=0.0,
                active_threads=0,
                chaos_engine_status="error"
            )
    
    def _populate_chaos_metrics(self, snapshot: PerformanceSnapshot) -> None:
        """Populate chaos-specific metrics in the snapshot"""
        try:
            with self.metrics_lock:
                # Get recent operation metrics
                pressure_calc = self.operation_metrics.get('pressure_calculation')
                if pressure_calc:
                    snapshot.pressure_calculation_time_ms = pressure_calc.average_time_ms
                    snapshot.pressure_collection_success_rate = pressure_calc.success_rate
                
                event_proc = self.operation_metrics.get('event_processing')
                if event_proc:
                    snapshot.event_processing_time_ms = event_proc.average_time_ms
                    snapshot.event_trigger_success_rate = event_proc.success_rate
                
                chaos_calc = self.operation_metrics.get('chaos_calculation')
                if chaos_calc:
                    snapshot.chaos_score_calculation_time_ms = chaos_calc.average_time_ms
                
                mitigation = self.operation_metrics.get('mitigation_processing')
                if mitigation:
                    snapshot.mitigation_processing_time_ms = mitigation.average_time_ms
                
                # Calculate cache hit rate from recent data
                cache_metrics = [
                    (timestamp, value) for timestamp, value in self.timing_data.get('cache_hit_rate', [])
                    if (datetime.now() - timestamp).total_seconds() < 300  # Last 5 minutes
                ]
                if cache_metrics:
                    snapshot.cache_hit_rate = sum(value for _, value in cache_metrics) / len(cache_metrics)
                
        except Exception as e:
            logger.error(f"Error populating chaos metrics: {e}")
    
    def _check_performance_thresholds(self, operation_name: str, execution_time_ms: float, 
                                    success: bool) -> None:
        """Check if operation performance crosses thresholds"""
        try:
            # Check slow operation threshold
            if execution_time_ms > self.thresholds['slow_operation_ms']:
                self._add_performance_alert(
                    alert_type="slow_operation",
                    message=f"Operation '{operation_name}' took {execution_time_ms:.2f}ms",
                    severity="warning",
                    details={'operation': operation_name, 'time_ms': execution_time_ms}
                )
            
            # Check error rate
            if not success:
                metrics = self.operation_metrics.get(operation_name)
                if metrics and metrics.error_rate > self.thresholds['high_error_rate']:
                    self._add_performance_alert(
                        alert_type="high_error_rate",
                        message=f"Operation '{operation_name}' has high error rate: {metrics.error_rate:.2%}",
                        severity="error",
                        details={'operation': operation_name, 'error_rate': metrics.error_rate}
                    )
            
        except Exception as e:
            logger.error(f"Error checking performance thresholds: {e}")
    
    def _check_metric_thresholds(self, metric_type: PerformanceMetric, value: float,
                               operation_name: Optional[str]) -> None:
        """Check if metric value crosses thresholds"""
        try:
            if metric_type == PerformanceMetric.CPU_USAGE and value > self.thresholds['high_cpu_percent']:
                self._add_performance_alert(
                    alert_type="high_cpu_usage",
                    message=f"High CPU usage: {value:.1f}%",
                    severity="warning",
                    details={'cpu_percent': value}
                )
            
            elif metric_type == PerformanceMetric.MEMORY_USAGE and value > self.thresholds['high_memory_percent']:
                self._add_performance_alert(
                    alert_type="high_memory_usage",
                    message=f"High memory usage: {value:.1f}%",
                    severity="warning",
                    details={'memory_percent': value}
                )
            
            elif metric_type == PerformanceMetric.CACHE_HIT_RATE and value < self.thresholds['low_cache_hit_rate']:
                self._add_performance_alert(
                    alert_type="low_cache_hit_rate",
                    message=f"Low cache hit rate: {value:.1%}",
                    severity="warning",
                    details={'cache_hit_rate': value}
                )
            
        except Exception as e:
            logger.error(f"Error checking metric thresholds: {e}")
    
    def _add_performance_alert(self, alert_type: str, message: str, severity: str,
                             details: Dict[str, Any]) -> None:
        """Add a performance alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity,
            'details': details
        }
        
        self.performance_alerts.append(alert)
        
        # Keep only recent alerts (last 100)
        if len(self.performance_alerts) > 100:
            self.performance_alerts = self.performance_alerts[-100:]
        
        # Log alert
        log_level = getattr(logger, severity.lower(), logger.info)
        log_level(f"Performance Alert [{alert_type}]: {message}")
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends and provide insights"""
        try:
            if len(self.snapshots) < 10:
                return {"message": "Insufficient data for trend analysis"}
            
            recent_snapshots = list(self.snapshots)[-50:]  # Last 50 snapshots
            
            # Calculate trends
            cpu_trend = self._calculate_trend([s.cpu_usage_percent for s in recent_snapshots])
            memory_trend = self._calculate_trend([s.memory_usage_mb for s in recent_snapshots])
            
            # Operation performance analysis
            operation_analysis = self._analyze_operation_performance()
            
            # System health score
            health_score = self._calculate_system_health_score()
            
            # Optimization suggestions
            suggestions = self._generate_optimization_suggestions()
            
            return {
                'trends': {
                    'cpu_usage_trend': cpu_trend,
                    'memory_usage_trend': memory_trend,
                    'performance_degradation': health_score < 0.8
                },
                'operation_performance': operation_analysis,
                'system_health_score': health_score,
                'optimization_suggestions': suggestions,
                'recent_alerts': self.performance_alerts[-10:],  # Last 10 alerts
                'snapshot_count': len(self.snapshots)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {"error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (positive = increasing, negative = decreasing)"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _analyze_operation_performance(self) -> Dict[str, Any]:
        """Analyze performance of different operations"""
        analysis = {}
        
        with self.metrics_lock:
            for operation_name, metrics in self.operation_metrics.items():
                analysis[operation_name] = {
                    'average_time_ms': metrics.average_time_ms,
                    'min_time_ms': metrics.min_time_ms,
                    'max_time_ms': metrics.max_time_ms,
                    'success_rate': metrics.success_rate,
                    'error_rate': metrics.error_rate,
                    'total_calls': metrics.total_calls,
                    'performance_grade': self._grade_operation_performance(metrics)
                }
        
        return analysis
    
    def _grade_operation_performance(self, metrics: OperationMetrics) -> str:
        """Grade operation performance (A-F)"""
        score = 0
        
        # Time performance (40% weight)
        if metrics.average_time_ms < 50:
            score += 40
        elif metrics.average_time_ms < 200:
            score += 30
        elif metrics.average_time_ms < 500:
            score += 20
        elif metrics.average_time_ms < 1000:
            score += 10
        
        # Success rate (40% weight)
        score += metrics.success_rate * 40
        
        # Consistency (20% weight) - based on variance
        time_variance = (metrics.max_time_ms - metrics.min_time_ms) / max(1, metrics.average_time_ms)
        if time_variance < 0.5:
            score += 20
        elif time_variance < 1.0:
            score += 15
        elif time_variance < 2.0:
            score += 10
        elif time_variance < 3.0:
            score += 5
        
        # Convert to letter grade
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _calculate_system_health_score(self) -> float:
        """Calculate overall system health score (0-1)"""
        try:
            if not self.snapshots:
                return 0.5  # Unknown
            
            recent_snapshot = self.snapshots[-1]
            score = 1.0
            
            # CPU usage impact
            if recent_snapshot.cpu_usage_percent > 80:
                score -= 0.3
            elif recent_snapshot.cpu_usage_percent > 60:
                score -= 0.1
            
            # Memory usage impact
            if recent_snapshot.memory_usage_percent > 85:
                score -= 0.3
            elif recent_snapshot.memory_usage_percent > 70:
                score -= 0.1
            
            # Error rate impact
            total_errors = sum(m.error_count for m in self.operation_metrics.values())
            total_calls = sum(m.total_calls for m in self.operation_metrics.values())
            if total_calls > 0:
                error_rate = total_errors / total_calls
                if error_rate > 0.1:
                    score -= 0.4
                elif error_rate > 0.05:
                    score -= 0.2
            
            # Performance consistency
            if recent_snapshot.pressure_collection_success_rate < 0.9:
                score -= 0.2
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating system health score: {e}")
            return 0.5
    
    def _generate_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on performance data"""
        suggestions = []
        
        try:
            with self.metrics_lock:
                # Check for slow operations
                for operation_name, metrics in self.operation_metrics.items():
                    if metrics.average_time_ms > 500:
                        suggestions.append({
                            'type': 'performance',
                            'priority': 'high' if metrics.average_time_ms > 1000 else 'medium',
                            'operation': operation_name,
                            'issue': f"Slow operation (avg: {metrics.average_time_ms:.1f}ms)",
                            'suggestion': f"Consider optimizing {operation_name} or adding caching"
                        })
                
                # Check for high error rates
                for operation_name, metrics in self.operation_metrics.items():
                    if metrics.error_rate > 0.05:
                        suggestions.append({
                            'type': 'reliability',
                            'priority': 'high',
                            'operation': operation_name,
                            'issue': f"High error rate ({metrics.error_rate:.1%})",
                            'suggestion': f"Investigate and fix errors in {operation_name}"
                        })
                
                # Check memory usage
                if self.snapshots:
                    recent_memory = self.snapshots[-1].memory_usage_percent
                    if recent_memory > 80:
                        suggestions.append({
                            'type': 'resource',
                            'priority': 'high' if recent_memory > 90 else 'medium',
                            'issue': f"High memory usage ({recent_memory:.1f}%)",
                            'suggestion': "Consider implementing data cleanup or increasing memory limits"
                        })
                
                # Check cache hit rate
                cache_data = self.timing_data.get('cache_hit_rate', [])
                if cache_data:
                    recent_cache_rate = cache_data[-1][1] if cache_data else 0
                    if recent_cache_rate < 0.7:
                        suggestions.append({
                            'type': 'performance',
                            'priority': 'medium',
                            'issue': f"Low cache hit rate ({recent_cache_rate:.1%})",
                            'suggestion': "Review caching strategy and cache invalidation policies"
                        })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {e}")
            return []
    
    async def _background_monitoring(self) -> None:
        """Background task for continuous monitoring"""
        try:
            while self.monitoring_enabled:
                # Take performance snapshot
                await self.take_performance_snapshot()
                
                # Check if optimization analysis is needed
                if len(self.snapshots) % 20 == 0:  # Every 20 snapshots
                    self.analyze_performance_trends()
                
                # Wait for next snapshot
                await asyncio.sleep(self.snapshot_interval)
                
        except asyncio.CancelledError:
            logger.info("Background monitoring cancelled")
        except Exception as e:
            logger.error(f"Error in background monitoring: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
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