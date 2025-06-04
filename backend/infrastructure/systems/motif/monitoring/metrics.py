"""
Monitoring and metrics collection for motif system.

Provides Prometheus metrics, health checks, and performance monitoring.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from functools import wraps
import asyncio

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Info, CollectorRegistry,
        generate_latest, CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    
from backend.infrastructure.systems.motif.models import MotifLifecycle, MotifScope

logger = logging.getLogger(__name__)


class MotifMetrics:
    """Prometheus metrics collector for motif system."""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize metrics collector."""
        self.registry = registry or CollectorRegistry()
        self.enabled = PROMETHEUS_AVAILABLE
        
        if not self.enabled:
            logger.warning("Prometheus client not available - metrics disabled")
            return
        
        # System info
        self.system_info = Info(
            'motif_system_info',
            'Motif system information',
            registry=self.registry
        )
        
        # Request metrics
        self.request_counter = Counter(
            'motif_requests_total',
            'Total requests to motif system',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'motif_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Business metrics
        self.motif_counter = Counter(
            'motif_operations_total',
            'Total motif operations',
            ['operation', 'category', 'scope'],
            registry=self.registry
        )
        
        self.active_motifs = Gauge(
            'motif_active_total',
            'Number of active motifs',
            ['scope', 'lifecycle'],
            registry=self.registry
        )
        
        self.motif_intensity = Histogram(
            'motif_intensity_distribution',
            'Distribution of motif intensities',
            buckets=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            registry=self.registry
        )
        
        # Evolution metrics
        self.evolution_counter = Counter(
            'motif_evolution_total',
            'Total motif evolutions',
            ['trigger_type', 'old_lifecycle', 'new_lifecycle'],
            registry=self.registry
        )
        
        # Conflict metrics
        self.conflict_gauge = Gauge(
            'motif_conflicts_active',
            'Number of active motif conflicts',
            ['conflict_type', 'severity'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_operations = Counter(
            'motif_cache_operations_total',
            'Total cache operations',
            ['operation', 'cache_type', 'result'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_operations = Counter(
            'motif_db_operations_total',
            'Total database operations',
            ['operation', 'table', 'result'],
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'motif_db_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table'],
            registry=self.registry
        )
        
        # System health metrics
        self.health_status = Gauge(
            'motif_system_health',
            'System health status (1=healthy, 0=unhealthy)',
            registry=self.registry
        )
        
        self.error_counter = Counter(
            'motif_errors_total',
            'Total system errors',
            ['error_type', 'component'],
            registry=self.registry
        )
        
        # Performance metrics
        self.memory_usage = Gauge(
            'motif_memory_usage_bytes',
            'Memory usage in bytes',
            ['component'],
            registry=self.registry
        )
        
        # Initialize system info
        self.system_info.info({
            'version': '1.0.0',
            'component': 'motif_system',
            'environment': 'production'
        })
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        if not self.enabled:
            return
        
        self.request_counter.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_motif_operation(self, operation: str, category: str, scope: str):
        """Record motif business operation."""
        if not self.enabled:
            return
        
        self.motif_counter.labels(
            operation=operation,
            category=category,
            scope=scope
        ).inc()
    
    def update_active_motifs(self, motifs_by_scope_lifecycle: Dict[str, Dict[str, int]]):
        """Update active motifs gauge."""
        if not self.enabled:
            return
        
        # Clear existing metrics
        self.active_motifs.clear()
        
        # Update with current counts
        for scope, lifecycle_counts in motifs_by_scope_lifecycle.items():
            for lifecycle, count in lifecycle_counts.items():
                self.active_motifs.labels(
                    scope=scope,
                    lifecycle=lifecycle
                ).set(count)
    
    def record_motif_intensity(self, intensity: int):
        """Record motif intensity for distribution analysis."""
        if not self.enabled:
            return
        
        self.motif_intensity.observe(intensity)
    
    def record_evolution(self, trigger_type: str, old_lifecycle: str, new_lifecycle: str):
        """Record motif evolution event."""
        if not self.enabled:
            return
        
        self.evolution_counter.labels(
            trigger_type=trigger_type,
            old_lifecycle=old_lifecycle,
            new_lifecycle=new_lifecycle
        ).inc()
    
    def update_conflicts(self, conflicts_by_type_severity: Dict[str, Dict[str, int]]):
        """Update active conflicts gauge."""
        if not self.enabled:
            return
        
        # Clear existing metrics
        self.conflict_gauge.clear()
        
        # Update with current counts
        for conflict_type, severity_counts in conflicts_by_type_severity.items():
            for severity, count in severity_counts.items():
                self.conflict_gauge.labels(
                    conflict_type=conflict_type,
                    severity=severity
                ).set(count)
    
    def record_cache_operation(self, operation: str, cache_type: str, result: str):
        """Record cache operation."""
        if not self.enabled:
            return
        
        self.cache_operations.labels(
            operation=operation,
            cache_type=cache_type,
            result=result
        ).inc()
    
    def record_db_operation(self, operation: str, table: str, result: str, duration: float):
        """Record database operation."""
        if not self.enabled:
            return
        
        self.db_operations.labels(
            operation=operation,
            table=table,
            result=result
        ).inc()
        
        self.db_query_duration.labels(
            operation=operation,
            table=table
        ).observe(duration)
    
    def set_health_status(self, healthy: bool):
        """Set system health status."""
        if not self.enabled:
            return
        
        self.health_status.set(1 if healthy else 0)
    
    def record_error(self, error_type: str, component: str):
        """Record system error."""
        if not self.enabled:
            return
        
        self.error_counter.labels(
            error_type=error_type,
            component=component
        ).inc()
    
    def set_memory_usage(self, component: str, bytes_used: int):
        """Set memory usage metric."""
        if not self.enabled:
            return
        
        self.memory_usage.labels(component=component).set(bytes_used)
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        if not self.enabled:
            return "# Prometheus metrics not available\n"
        
        return generate_latest(self.registry).decode('utf-8')


class PerformanceMonitor:
    """Performance monitoring and alerting."""
    
    def __init__(self, metrics: MotifMetrics):
        """Initialize performance monitor."""
        self.metrics = metrics
        self.alert_thresholds = {
            'response_time_ms': 5000,      # 5 seconds
            'error_rate_percent': 5.0,     # 5%
            'active_conflicts': 100,       # 100 conflicts
            'memory_usage_mb': 1024,       # 1GB
            'cache_hit_rate_percent': 80.0, # 80%
        }
        self.performance_history = []
        self.max_history_size = 1000
    
    def record_performance_data(self, data: Dict[str, Any]):
        """Record performance data point."""
        data['timestamp'] = datetime.utcnow()
        self.performance_history.append(data)
        
        # Trim history to max size
        if len(self.performance_history) > self.max_history_size:
            self.performance_history = self.performance_history[-self.max_history_size:]
    
    def check_alerts(self, current_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions."""
        alerts = []
        
        # Response time alert
        avg_response_time = current_stats.get('avg_response_time_ms', 0)
        if avg_response_time > self.alert_thresholds['response_time_ms']:
            alerts.append({
                'level': 'warning',
                'metric': 'response_time',
                'value': avg_response_time,
                'threshold': self.alert_thresholds['response_time_ms'],
                'message': f"High response time: {avg_response_time}ms"
            })
        
        # Error rate alert
        error_rate = current_stats.get('error_rate_percent', 0)
        if error_rate > self.alert_thresholds['error_rate_percent']:
            alerts.append({
                'level': 'critical',
                'metric': 'error_rate',
                'value': error_rate,
                'threshold': self.alert_thresholds['error_rate_percent'],
                'message': f"High error rate: {error_rate}%"
            })
        
        # Conflict alert
        active_conflicts = current_stats.get('active_conflicts', 0)
        if active_conflicts > self.alert_thresholds['active_conflicts']:
            alerts.append({
                'level': 'warning',
                'metric': 'conflicts',
                'value': active_conflicts,
                'threshold': self.alert_thresholds['active_conflicts'],
                'message': f"High number of conflicts: {active_conflicts}"
            })
        
        return alerts
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.performance_history:
            return {'status': 'no_data'}
        
        recent_data = self.performance_history[-100:]  # Last 100 data points
        
        response_times = [d.get('response_time_ms', 0) for d in recent_data if d.get('response_time_ms')]
        error_counts = [d.get('errors', 0) for d in recent_data]
        
        return {
            'avg_response_time_ms': sum(response_times) / len(response_times) if response_times else 0,
            'max_response_time_ms': max(response_times) if response_times else 0,
            'total_errors': sum(error_counts),
            'data_points': len(recent_data),
            'time_range': {
                'start': recent_data[0]['timestamp'].isoformat() if recent_data else None,
                'end': recent_data[-1]['timestamp'].isoformat() if recent_data else None
            }
        }


class HealthChecker:
    """System health monitoring."""
    
    def __init__(self, service, cache=None, database=None):
        """Initialize health checker."""
        self.service = service
        self.cache = cache
        self.database = database
        self.last_check = None
        self.health_status = {}
    
    async def check_service_health(self) -> Dict[str, Any]:
        """Check service layer health."""
        try:
            # Test basic service functionality
            stats = await self.service.get_motif_statistics()
            
            return {
                'status': 'healthy',
                'total_motifs': stats.get('total_motifs', 0),
                'system_health': stats.get('system_health', 'unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_cache_health(self) -> Dict[str, Any]:
        """Check cache health."""
        if not self.cache:
            return {'status': 'not_configured'}
        
        try:
            cache_stats = await self.cache.get_cache_stats()
            
            if cache_stats.get('connected', False):
                return {
                    'status': 'healthy',
                    'hit_rate': cache_stats.get('hit_rate', 0),
                    'memory_usage': cache_stats.get('memory_usage', 'unknown'),
                    'total_keys': cache_stats.get('total_keys', 0),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Redis not connected',
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        if not self.database:
            return {'status': 'not_configured'}
        
        try:
            # Simple database connectivity test
            start_time = time.time()
            
            # This would need to be implemented based on your database manager
            # For now, assume it's healthy if we have a database reference
            duration = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time_ms': round(duration * 1000, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        start_time = time.time()
        
        # Run all health checks
        service_health = await self.check_service_health()
        cache_health = await self.check_cache_health()
        database_health = await self.check_database_health()
        
        # Determine overall health
        components = [service_health, cache_health, database_health]
        healthy_components = sum(1 for c in components if c.get('status') == 'healthy')
        total_components = len([c for c in components if c.get('status') != 'not_configured'])
        
        overall_status = 'healthy' if healthy_components == total_components else 'degraded'
        if healthy_components == 0:
            overall_status = 'unhealthy'
        
        duration = time.time() - start_time
        
        health_report = {
            'status': overall_status,
            'components': {
                'service': service_health,
                'cache': cache_health,
                'database': database_health
            },
            'summary': {
                'healthy_components': healthy_components,
                'total_components': total_components,
                'check_duration_ms': round(duration * 1000, 2)
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.last_check = datetime.utcnow()
        self.health_status = health_report
        
        return health_report


def monitor_performance(metrics: MotifMetrics):
    """Decorator to monitor function performance."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = func.__name__
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record successful operation
                metrics.record_db_operation(
                    operation=operation,
                    table='motifs',
                    result='success',
                    duration=duration
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record failed operation
                metrics.record_db_operation(
                    operation=operation,
                    table='motifs',
                    result='error',
                    duration=duration
                )
                
                metrics.record_error(
                    error_type=e.__class__.__name__,
                    component='service'
                )
                
                raise
        
        return wrapper
    return decorator


# Global metrics instance
metrics = MotifMetrics() if PROMETHEUS_AVAILABLE else None 