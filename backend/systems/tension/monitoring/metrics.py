"""
Tension Metrics Collection and Analysis

Provides comprehensive metrics collection and analysis for the tension system
following Development Bible standards.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import json


@dataclass
class TensionMetric:
    """Individual tension metric data point"""
    timestamp: datetime
    region_id: str
    poi_id: str
    tension_level: float
    event_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealthMetric:
    """System health and performance metrics"""
    timestamp: datetime
    total_tension_updates: int
    conflicts_triggered: int
    revolts_triggered: int
    modifiers_expired: int
    average_response_time_ms: float
    memory_usage_mb: float
    error_count: int = 0


class TensionMetrics:
    """
    Comprehensive tension system metrics collection and analysis.
    Provides real-time monitoring and historical analysis.
    """
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        
        # Historical data storage
        self.tension_history: deque = deque(maxlen=max_history_size)
        self.system_health_history: deque = deque(maxlen=1000)
        self.event_history: deque = deque(maxlen=max_history_size)
        
        # Real-time aggregations
        self.region_metrics: Dict[str, Dict] = defaultdict(lambda: {
            'current_tension': 0.0,
            'average_tension': 0.0,
            'peak_tension': 0.0,
            'event_count': 0,
            'last_update': None
        })
        
        # Performance tracking
        self.performance_metrics = {
            'calculation_times': deque(maxlen=1000),
            'api_response_times': deque(maxlen=1000),
            'error_count': 0,
            'uptime_start': datetime.utcnow()
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'high_tension': 0.8,
            'critical_tension': 0.9,
            'response_time_threshold_ms': 1000,
            'error_rate_threshold': 0.05
        }

    def record_tension_metric(
        self,
        region_id: str,
        poi_id: str,
        tension_level: float,
        event_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a tension measurement"""
        metric = TensionMetric(
            timestamp=datetime.utcnow(),
            region_id=region_id,
            poi_id=poi_id,
            tension_level=tension_level,
            event_type=event_type,
            metadata=metadata or {}
        )
        
        self.tension_history.append(metric)
        self._update_region_metrics(region_id, poi_id, tension_level)

    def record_system_health(
        self,
        total_updates: int,
        conflicts: int,
        revolts: int,
        modifiers_expired: int,
        avg_response_time: float,
        memory_usage: float
    ) -> None:
        """Record system health metrics"""
        health_metric = SystemHealthMetric(
            timestamp=datetime.utcnow(),
            total_tension_updates=total_updates,
            conflicts_triggered=conflicts,
            revolts_triggered=revolts,
            modifiers_expired=modifiers_expired,
            average_response_time_ms=avg_response_time,
            memory_usage_mb=memory_usage
        )
        
        self.system_health_history.append(health_metric)

    def record_performance_metric(self, operation: str, duration_ms: float) -> None:
        """Record performance metrics for operations"""
        if operation == 'tension_calculation':
            self.performance_metrics['calculation_times'].append(duration_ms)
        elif operation == 'api_response':
            self.performance_metrics['api_response_times'].append(duration_ms)

    def record_error(self, error_type: str, error_message: str) -> None:
        """Record system errors"""
        self.performance_metrics['error_count'] += 1
        # Could extend to categorize errors and track error patterns

    def get_tension_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get tension summary for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        recent_metrics = [
            metric for metric in self.tension_history
            if metric.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {
                'period_hours': hours_back,
                'total_measurements': 0,
                'average_tension': 0.0,
                'peak_tension': 0.0,
                'regions_active': 0
            }
        
        tensions = [metric.tension_level for metric in recent_metrics]
        regions = set(metric.region_id for metric in recent_metrics)
        
        return {
            'period_hours': hours_back,
            'total_measurements': len(recent_metrics),
            'average_tension': statistics.mean(tensions),
            'peak_tension': max(tensions),
            'median_tension': statistics.median(tensions),
            'standard_deviation': statistics.stdev(tensions) if len(tensions) > 1 else 0.0,
            'regions_active': len(regions),
            'measurement_frequency': len(recent_metrics) / hours_back
        }

    def get_region_analysis(self, region_id: str, hours_back: int = 24) -> Dict[str, Any]:
        """Get detailed analysis for a specific region"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        region_metrics = [
            metric for metric in self.tension_history
            if metric.region_id == region_id and metric.timestamp >= cutoff_time
        ]
        
        if not region_metrics:
            return {
                'region_id': region_id,
                'period_hours': hours_back,
                'no_data': True
            }
        
        # Analyze POI distribution
        poi_analysis = defaultdict(list)
        for metric in region_metrics:
            poi_analysis[metric.poi_id].append(metric.tension_level)
        
        poi_summaries = {}
        for poi_id, tensions in poi_analysis.items():
            poi_summaries[poi_id] = {
                'measurements': len(tensions),
                'average_tension': statistics.mean(tensions),
                'peak_tension': max(tensions),
                'current_tension': tensions[-1] if tensions else 0.0
            }
        
        # Event analysis
        event_types = [metric.event_type for metric in region_metrics if metric.event_type]
        event_counts = defaultdict(int)
        for event_type in event_types:
            event_counts[event_type] += 1
        
        all_tensions = [metric.tension_level for metric in region_metrics]
        
        return {
            'region_id': region_id,
            'period_hours': hours_back,
            'total_measurements': len(region_metrics),
            'average_tension': statistics.mean(all_tensions),
            'peak_tension': max(all_tensions),
            'pois_analyzed': len(poi_summaries),
            'poi_details': poi_summaries,
            'event_summary': dict(event_counts),
            'tension_trend': self._calculate_trend(all_tensions),
            'risk_assessment': self._assess_region_risk(region_id, all_tensions)
        }

    def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report"""
        if not self.system_health_history:
            return {'status': 'no_data', 'message': 'No health data available'}
        
        latest_health = self.system_health_history[-1]
        
        # Calculate trends over last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_health = [
            h for h in self.system_health_history
            if h.timestamp >= one_hour_ago
        ]
        
        performance_summary = self._get_performance_summary()
        
        return {
            'status': 'healthy',
            'timestamp': latest_health.timestamp.isoformat(),
            'system_stats': {
                'total_tension_updates': latest_health.total_tension_updates,
                'conflicts_triggered': latest_health.conflicts_triggered,
                'revolts_triggered': latest_health.revolts_triggered,
                'modifiers_expired': latest_health.modifiers_expired,
                'uptime_hours': (datetime.utcnow() - self.performance_metrics['uptime_start']).total_seconds() / 3600
            },
            'performance': performance_summary,
            'alerts': self._check_alerts(latest_health, performance_summary),
            'trends': self._calculate_health_trends(recent_health)
        }

    def get_alert_status(self) -> List[Dict[str, Any]]:
        """Get current system alerts"""
        alerts = []
        
        # Check tension alerts
        for region_id, metrics in self.region_metrics.items():
            tension = metrics['current_tension']
            if tension >= self.alert_thresholds['critical_tension']:
                alerts.append({
                    'type': 'critical_tension',
                    'severity': 'critical',
                    'region_id': region_id,
                    'tension_level': tension,
                    'message': f"Critical tension level in {region_id}: {tension:.2f}"
                })
            elif tension >= self.alert_thresholds['high_tension']:
                alerts.append({
                    'type': 'high_tension',
                    'severity': 'warning',
                    'region_id': region_id,
                    'tension_level': tension,
                    'message': f"High tension level in {region_id}: {tension:.2f}"
                })
        
        # Check performance alerts
        if self.performance_metrics['api_response_times']:
            avg_response_time = statistics.mean(self.performance_metrics['api_response_times'])
            if avg_response_time > self.alert_thresholds['response_time_threshold_ms']:
                alerts.append({
                    'type': 'slow_response',
                    'severity': 'warning',
                    'avg_response_time': avg_response_time,
                    'message': f"Slow API response time: {avg_response_time:.1f}ms"
                })
        
        return alerts

    def export_metrics(self, format: str = 'json', hours_back: int = 24) -> str:
        """Export metrics data for external analysis"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        metrics_data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'period_hours': hours_back,
            'tension_metrics': [
                {
                    'timestamp': metric.timestamp.isoformat(),
                    'region_id': metric.region_id,
                    'poi_id': metric.poi_id,
                    'tension_level': metric.tension_level,
                    'event_type': metric.event_type,
                    'metadata': metric.metadata
                }
                for metric in self.tension_history
                if metric.timestamp >= cutoff_time
            ],
            'system_health': [
                {
                    'timestamp': health.timestamp.isoformat(),
                    'total_tension_updates': health.total_tension_updates,
                    'conflicts_triggered': health.conflicts_triggered,
                    'revolts_triggered': health.revolts_triggered,
                    'modifiers_expired': health.modifiers_expired,
                    'average_response_time_ms': health.average_response_time_ms,
                    'memory_usage_mb': health.memory_usage_mb
                }
                for health in self.system_health_history
                if health.timestamp >= cutoff_time
            ]
        }
        
        if format == 'json':
            return json.dumps(metrics_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    # Private helper methods
    def _update_region_metrics(self, region_id: str, poi_id: str, tension_level: float) -> None:
        """Update real-time region metrics"""
        metrics = self.region_metrics[region_id]
        metrics['current_tension'] = max(metrics['current_tension'], tension_level)
        metrics['peak_tension'] = max(metrics['peak_tension'], tension_level)
        metrics['event_count'] += 1
        metrics['last_update'] = datetime.utcnow()
        
        # Update rolling average
        if 'tension_values' not in metrics:
            metrics['tension_values'] = deque(maxlen=100)
        metrics['tension_values'].append(tension_level)
        metrics['average_tension'] = statistics.mean(metrics['tension_values'])

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values"""
        if len(values) < 2:
            return 'insufficient_data'
        
        # Simple trend calculation using first half vs second half
        mid_point = len(values) // 2
        first_half_avg = statistics.mean(values[:mid_point])
        second_half_avg = statistics.mean(values[mid_point:])
        
        diff = second_half_avg - first_half_avg
        if abs(diff) < 0.05:  # Threshold for "stable"
            return 'stable'
        elif diff > 0:
            return 'increasing'
        else:
            return 'decreasing'

    def _assess_region_risk(self, region_id: str, tensions: List[float]) -> Dict[str, Any]:
        """Assess risk level for a region based on tension patterns"""
        if not tensions:
            return {'level': 'unknown', 'reasons': ['no_data']}
        
        avg_tension = statistics.mean(tensions)
        peak_tension = max(tensions)
        volatility = statistics.stdev(tensions) if len(tensions) > 1 else 0.0
        
        risk_factors = []
        risk_level = 'low'
        
        if avg_tension > 0.7:
            risk_factors.append('high_average_tension')
            risk_level = 'medium'
        
        if peak_tension > 0.9:
            risk_factors.append('critical_peak_tension')
            risk_level = 'high'
        
        if volatility > 0.3:
            risk_factors.append('high_volatility')
            if risk_level == 'low':
                risk_level = 'medium'
        
        # Check for sustained high tension
        high_tension_count = sum(1 for t in tensions[-10:] if t > 0.8)
        if high_tension_count >= 7:  # 70% of recent measurements
            risk_factors.append('sustained_high_tension')
            risk_level = 'high'
        
        return {
            'level': risk_level,
            'factors': risk_factors,
            'average_tension': avg_tension,
            'peak_tension': peak_tension,
            'volatility': volatility
        }

    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        calc_times = list(self.performance_metrics['calculation_times'])
        api_times = list(self.performance_metrics['api_response_times'])
        
        summary = {
            'error_count': self.performance_metrics['error_count'],
            'uptime_hours': (datetime.utcnow() - self.performance_metrics['uptime_start']).total_seconds() / 3600
        }
        
        if calc_times:
            summary['calculation_performance'] = {
                'average_ms': statistics.mean(calc_times),
                'median_ms': statistics.median(calc_times),
                'p95_ms': self._percentile(calc_times, 95),
                'sample_count': len(calc_times)
            }
        
        if api_times:
            summary['api_performance'] = {
                'average_ms': statistics.mean(api_times),
                'median_ms': statistics.median(api_times),
                'p95_ms': self._percentile(api_times, 95),
                'sample_count': len(api_times)
            }
        
        return summary

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def _check_alerts(self, health: SystemHealthMetric, performance: Dict[str, Any]) -> List[str]:
        """Check for system health alerts"""
        alerts = []
        
        if health.average_response_time_ms > self.alert_thresholds['response_time_threshold_ms']:
            alerts.append(f"High response time: {health.average_response_time_ms:.1f}ms")
        
        if performance['error_count'] > 0:
            alerts.append(f"Errors detected: {performance['error_count']}")
        
        return alerts

    def _calculate_health_trends(self, recent_health: List[SystemHealthMetric]) -> Dict[str, str]:
        """Calculate trends in system health metrics"""
        if len(recent_health) < 2:
            return {}
        
        trends = {}
        
        # Response time trend
        response_times = [h.average_response_time_ms for h in recent_health]
        trends['response_time'] = self._calculate_trend(response_times)
        
        # Memory usage trend
        memory_usage = [h.memory_usage_mb for h in recent_health]
        trends['memory_usage'] = self._calculate_trend(memory_usage)
        
        return trends 