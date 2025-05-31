"""
Integration system - Monitoring module for logging, metrics, and alerting.

This module provides comprehensive monitoring infrastructure:
- MonitoringManager class for coordinating monitoring across systems
- Integration logging with structured log formats
- Metrics collection and aggregation
- Alert system for integration failures
- Performance monitoring and profiling
"""

import logging
import time
import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import threading
import statistics

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Alert:
    """Represents a monitoring alert"""
    alert_id: str
    system_id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    threshold_value: float
    actual_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False
    
    def acknowledge(self):
        """Acknowledge the alert"""
        self.acknowledged = True
    
    def resolve(self):
        """Mark the alert as resolved"""
        self.resolved = True


@dataclass
class Metric:
    """Represents a monitoring metric"""
    name: str
    system_id: str
    metric_type: MetricType
    value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "name": self.name,
            "system_id": self.system_id,
            "type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels
        }


class IntegrationLogger:
    """
    Structured logging for integration events with correlation and tracing.
    """
    
    def __init__(self, system_id: str):
        self.system_id = system_id
        self.logger = logging.getLogger(f"integration.{system_id}")
        self._correlation_id = None
        self._trace_id = None
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for log correlation"""
        self._correlation_id = correlation_id
    
    def set_trace_id(self, trace_id: str):
        """Set trace ID for distributed tracing"""
        self._trace_id = trace_id
    
    def _get_log_context(self) -> Dict[str, Any]:
        """Get log context with correlation and trace IDs"""
        context = {
            "system_id": self.system_id,
            "timestamp": datetime.now().isoformat()
        }
        
        if self._correlation_id:
            context["correlation_id"] = self._correlation_id
        
        if self._trace_id:
            context["trace_id"] = self._trace_id
        
        return context
    
    def info(self, message: str, **kwargs):
        """Log info level message with context"""
        context = self._get_log_context()
        context.update(kwargs)
        self.logger.info(f"{message} | Context: {json.dumps(context)}")
    
    def warning(self, message: str, **kwargs):
        """Log warning level message with context"""
        context = self._get_log_context()
        context.update(kwargs)
        self.logger.warning(f"{message} | Context: {json.dumps(context)}")
    
    def error(self, message: str, **kwargs):
        """Log error level message with context"""
        context = self._get_log_context()
        context.update(kwargs)
        self.logger.error(f"{message} | Context: {json.dumps(context)}")
    
    def critical(self, message: str, **kwargs):
        """Log critical level message with context"""
        context = self._get_log_context()
        context.update(kwargs)
        self.logger.critical(f"{message} | Context: {json.dumps(context)}")
    
    def debug(self, message: str, **kwargs):
        """Log debug level message with context"""
        context = self._get_log_context()
        context.update(kwargs)
        self.logger.debug(f"{message} | Context: {json.dumps(context)}")


class IntegrationMetrics:
    """
    Metrics collection and aggregation for integration operations.
    """
    
    def __init__(self, system_id: str):
        self.system_id = system_id
        self._metrics: Dict[str, List[Metric]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        with self._lock:
            metric_key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
            self._counters[metric_key] += value
            
            metric = Metric(
                name=name,
                system_id=self.system_id,
                metric_type=MetricType.COUNTER,
                value=self._counters[metric_key],
                labels=labels or {}
            )
            self._metrics[name].append(metric)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        with self._lock:
            metric_key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
            self._gauges[metric_key] = value
            
            metric = Metric(
                name=name,
                system_id=self.system_id,
                metric_type=MetricType.GAUGE,
                value=value,
                labels=labels or {}
            )
            self._metrics[name].append(metric)
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a value in a histogram"""
        with self._lock:
            metric_key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
            self._histograms[metric_key].append(value)
            
            metric = Metric(
                name=name,
                system_id=self.system_id,
                metric_type=MetricType.HISTOGRAM,
                value=value,
                labels=labels or {}
            )
            self._metrics[name].append(metric)
    
    def record_timer(self, name: str, duration: float, labels: Optional[Dict[str, str]] = None):
        """Record a timer duration"""
        with self._lock:
            metric_key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
            self._timers[metric_key].append(duration)
            
            metric = Metric(
                name=name,
                system_id=self.system_id,
                metric_type=MetricType.TIMER,
                value=duration,
                labels=labels or {}
            )
            self._metrics[name].append(metric)
    
    def get_counter_value(self, name: str, labels: Optional[Dict[str, str]] = None) -> int:
        """Get current counter value"""
        metric_key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        return self._counters.get(metric_key, 0)
    
    def get_gauge_value(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current gauge value"""
        metric_key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        return self._gauges.get(metric_key, 0.0)
    
    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics"""
        metric_key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        values = self._histograms.get(metric_key, [])
        
        if not values:
            return {"count": 0, "min": 0, "max": 0, "mean": 0, "median": 0}
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values)
        }
    
    def get_timer_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get timer statistics"""
        metric_key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        values = self._timers.get(metric_key, [])
        
        if not values:
            return {"count": 0, "min": 0, "max": 0, "mean": 0, "median": 0}
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values)
        }
    
    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Get all metrics as dictionaries"""
        all_metrics = []
        for metrics_list in self._metrics.values():
            for metric in metrics_list:
                all_metrics.append(metric.to_dict())
        return all_metrics


class IntegrationAlerting:
    """
    Alert system for integration issues with configurable thresholds.
    """
    
    def __init__(self, system_id: str):
        self.system_id = system_id
        self._alert_rules: Dict[str, Dict[str, Any]] = {}
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        self._alert_handlers: List[Callable] = []
        self._lock = threading.Lock()
    
    def add_alert_rule(
        self,
        metric_name: str,
        threshold: float,
        operator: str = "greater_than",
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        message_template: str = "Metric {metric_name} triggered alert"
    ):
        """Add an alert rule for a metric"""
        with self._lock:
            self._alert_rules[metric_name] = {
                "threshold": threshold,
                "operator": operator,
                "severity": severity,
                "message_template": message_template
            }
    
    def remove_alert_rule(self, metric_name: str):
        """Remove an alert rule"""
        with self._lock:
            if metric_name in self._alert_rules:
                del self._alert_rules[metric_name]
    
    def check_metric(self, metric: Metric):
        """Check if a metric triggers any alerts"""
        with self._lock:
            if metric.name not in self._alert_rules:
                return
            
            rule = self._alert_rules[metric.name]
            threshold = rule["threshold"]
            operator = rule["operator"]
            
            should_alert = False
            
            if operator == "greater_than" and metric.value > threshold:
                should_alert = True
            elif operator == "less_than" and metric.value < threshold:
                should_alert = True
            elif operator == "equals" and metric.value == threshold:
                should_alert = True
            elif operator == "not_equals" and metric.value != threshold:
                should_alert = True
            
            if should_alert:
                alert_id = f"{metric.name}_{metric.timestamp.timestamp()}"
                
                alert = Alert(
                    alert_id=alert_id,
                    system_id=self.system_id,
                    metric_name=metric.name,
                    severity=rule["severity"],
                    message=rule["message_template"].format(
                        metric_name=metric.name,
                        threshold=threshold,
                        actual_value=metric.value
                    ),
                    threshold_value=threshold,
                    actual_value=metric.value
                )
                
                self._active_alerts[alert_id] = alert
                self._alert_history.append(alert)
                
                # Notify alert handlers
                for handler in self._alert_handlers:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.error(f"Alert handler failed: {e}")
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        with self._lock:
            if alert_id in self._active_alerts:
                self._active_alerts[alert_id].acknowledge()
                return True
            return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        with self._lock:
            if alert_id in self._active_alerts:
                self._active_alerts[alert_id].resolve()
                del self._active_alerts[alert_id]
                return True
            return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self._active_alerts.values())
    
    def get_alert_history(self, limit: Optional[int] = None) -> List[Alert]:
        """Get alert history"""
        if limit:
            return self._alert_history[-limit:]
        return self._alert_history
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add an alert handler function"""
        self._alert_handlers.append(handler)


class MonitoringManager:
    """
    Coordinates monitoring across systems with logging, metrics, and alerting.
    """
    
    def __init__(self):
        self._system_loggers: Dict[str, IntegrationLogger] = {}
        self._system_metrics: Dict[str, IntegrationMetrics] = {}
        self._system_alerting: Dict[str, IntegrationAlerting] = {}
        self._global_metrics = IntegrationMetrics("global")
        self._performance_profiles: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    def get_logger(self, system_id: str) -> IntegrationLogger:
        """Get or create a logger for a system"""
        if system_id not in self._system_loggers:
            self._system_loggers[system_id] = IntegrationLogger(system_id)
        return self._system_loggers[system_id]
    
    def get_metrics(self, system_id: str) -> IntegrationMetrics:
        """Get or create metrics collector for a system"""
        if system_id not in self._system_metrics:
            self._system_metrics[system_id] = IntegrationMetrics(system_id)
        return self._system_metrics[system_id]
    
    def get_alerting(self, system_id: str) -> IntegrationAlerting:
        """Get or create alerting manager for a system"""
        if system_id not in self._system_alerting:
            self._system_alerting[system_id] = IntegrationAlerting(system_id)
        return self._system_alerting[system_id]
    
    async def record_performance_profile(
        self,
        system_id: str,
        operation: str,
        duration: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a performance profile for an operation"""
        async with self._lock:
            profile = {
                "operation": operation,
                "duration": duration,
                "timestamp": datetime.now(),
                "metadata": metadata or {}
            }
            
            self._performance_profiles[system_id].append(profile)
            
            # Record as metric
            metrics = self.get_metrics(system_id)
            metrics.record_timer(f"operation_duration_{operation}", duration)
            
            # Check for performance alerts
            alerting = self.get_alerting(system_id)
            metric = Metric(
                name=f"operation_duration_{operation}",
                system_id=system_id,
                metric_type=MetricType.TIMER,
                value=duration
            )
            alerting.check_metric(metric)
    
    def get_performance_summary(self, system_id: str) -> Dict[str, Any]:
        """Get performance summary for a system"""
        profiles = self._performance_profiles.get(system_id, [])
        
        if not profiles:
            return {"total_operations": 0}
        
        operations = defaultdict(list)
        for profile in profiles:
            operations[profile["operation"]].append(profile["duration"])
        
        summary = {
            "total_operations": len(profiles),
            "operations": {}
        }
        
        for operation, durations in operations.items():
            summary["operations"][operation] = {
                "count": len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "avg_duration": statistics.mean(durations),
                "median_duration": statistics.median(durations)
            }
        
        return summary
    
    def get_system_health(self, system_id: str) -> Dict[str, Any]:
        """Get overall health status for a system"""
        alerting = self.get_alerting(system_id)
        metrics = self.get_metrics(system_id)
        
        active_alerts = alerting.get_active_alerts()
        critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        high_alerts = [a for a in active_alerts if a.severity == AlertSeverity.HIGH]
        
        health_status = "healthy"
        if critical_alerts:
            health_status = "critical"
        elif high_alerts:
            health_status = "warning"
        elif active_alerts:
            health_status = "degraded"
        
        return {
            "system_id": system_id,
            "status": health_status,
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "high_alerts": len(high_alerts),
            "metrics_collected": len(metrics.get_all_metrics()),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_global_health(self) -> Dict[str, Any]:
        """Get global health status across all systems"""
        all_systems_health = {}
        overall_status = "healthy"
        total_alerts = 0
        
        for system_id in self._system_alerting.keys():
            system_health = self.get_system_health(system_id)
            all_systems_health[system_id] = system_health
            
            total_alerts += system_health["active_alerts"]
            
            if system_health["status"] == "critical":
                overall_status = "critical"
            elif system_health["status"] in ["warning", "degraded"] and overall_status == "healthy":
                overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "total_systems": len(all_systems_health),
            "total_alerts": total_alerts,
            "systems": all_systems_health,
            "timestamp": datetime.now().isoformat()
        }


# Global instances
monitoring_manager = MonitoringManager()

# Convenience accessors
def get_integration_logger(system_id: str) -> IntegrationLogger:
    """Get integration logger for a system"""
    return monitoring_manager.get_logger(system_id)

def get_integration_metrics(system_id: str) -> IntegrationMetrics:
    """Get integration metrics for a system"""
    return monitoring_manager.get_metrics(system_id)

def get_integration_alerting(system_id: str) -> IntegrationAlerting:
    """Get integration alerting for a system"""
    return monitoring_manager.get_alerting(system_id)

# Global accessors for backward compatibility
integration_logger = get_integration_logger("global")
integration_metrics = get_integration_metrics("global")
integration_alerting = get_integration_alerting("global")
