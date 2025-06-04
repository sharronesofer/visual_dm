"""
Tension System Dashboard

Provides a comprehensive dashboard interface for monitoring tension system
performance, analytics, and real-time status following Development Bible patterns.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

from .metrics import TensionMetrics
from .analytics import TensionAnalytics
from .alerts import TensionAlerts


@dataclass
class DashboardConfig:
    """Configuration for dashboard display and behavior"""
    refresh_interval_seconds: int = 30
    default_time_window_hours: int = 24
    max_regions_displayed: int = 20
    alert_retention_hours: int = 168  # 1 week
    enable_real_time_updates: bool = True
    show_detailed_metrics: bool = True


class TensionDashboard:
    """
    Comprehensive dashboard for tension system monitoring.
    
    Provides real-time status, historical analytics, alerting,
    and system health monitoring in a unified interface.
    """
    
    def __init__(
        self,
        metrics: TensionMetrics,
        analytics: TensionAnalytics,
        alerts: TensionAlerts,
        config: Optional[DashboardConfig] = None
    ):
        self.metrics = metrics
        self.analytics = analytics
        self.alerts = alerts
        self.config = config or DashboardConfig()
        
        # Dashboard state
        self._last_update = datetime.utcnow()
        self._cached_data = {}
        self._cache_ttl_seconds = 30

    def get_overview_dashboard(self) -> Dict[str, Any]:
        """Get the main overview dashboard data"""
        current_time = datetime.utcnow()
        
        # Check cache
        if self._is_cache_valid('overview'):
            return self._cached_data['overview']
        
        # Generate fresh overview
        overview = {
            'timestamp': current_time.isoformat(),
            'system_status': self._get_system_status(),
            'tension_summary': self.metrics.get_tension_summary(
                self.config.default_time_window_hours
            ),
            'active_alerts': self.alerts.get_active_alerts(),
            'regional_overview': self._get_regional_overview(),
            'recent_events': self._get_recent_events(),
            'performance_metrics': self._get_performance_overview(),
            'config': asdict(self.config)
        }
        
        # Cache the result
        self._cached_data['overview'] = overview
        self._cached_data['overview_timestamp'] = current_time
        
        return overview

    def get_region_dashboard(self, region_id: str, hours_back: int = 24) -> Dict[str, Any]:
        """Get detailed dashboard for a specific region"""
        current_time = datetime.utcnow()
        cache_key = f'region_{region_id}_{hours_back}'
        
        if self._is_cache_valid(cache_key):
            return self._cached_data[cache_key]
        
        # Generate region dashboard
        region_analysis = self.metrics.get_region_analysis(region_id, hours_back)
        tension_timeline = self.analytics.get_tension_timeline(region_id, hours_back)
        event_analysis = self.analytics.get_event_impact_analysis(region_id, hours_back)
        predictions = self.analytics.predict_tension_trends(region_id)
        
        dashboard = {
            'timestamp': current_time.isoformat(),
            'region_id': region_id,
            'time_window_hours': hours_back,
            'analysis': region_analysis,
            'timeline': tension_timeline,
            'event_analysis': event_analysis,
            'predictions': predictions,
            'alerts': self.alerts.get_region_alerts(region_id),
            'recommendations': self._generate_region_recommendations(region_analysis),
            'poi_details': self._get_poi_details(region_id, hours_back)
        }
        
        # Cache the result
        self._cached_data[cache_key] = dashboard
        self._cached_data[f'{cache_key}_timestamp'] = current_time
        
        return dashboard

    def get_system_health_dashboard(self) -> Dict[str, Any]:
        """Get system health and performance dashboard"""
        current_time = datetime.utcnow()
        
        if self._is_cache_valid('health'):
            return self._cached_data['health']
        
        health_report = self.metrics.get_system_health_report()
        performance_trends = self.analytics.get_performance_trends()
        
        dashboard = {
            'timestamp': current_time.isoformat(),
            'health_status': health_report,
            'performance_trends': performance_trends,
            'error_analysis': self._get_error_analysis(),
            'capacity_metrics': self._get_capacity_metrics(),
            'uptime_statistics': self._get_uptime_statistics(),
            'configuration_status': self._get_configuration_status()
        }
        
        # Cache the result
        self._cached_data['health'] = dashboard
        self._cached_data['health_timestamp'] = current_time
        
        return dashboard

    def get_analytics_dashboard(self, time_window_hours: int = 168) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard (default: 1 week)"""
        current_time = datetime.utcnow()
        cache_key = f'analytics_{time_window_hours}'
        
        if self._is_cache_valid(cache_key):
            return self._cached_data[cache_key]
        
        # Generate analytics
        tension_patterns = self.analytics.analyze_tension_patterns(time_window_hours)
        event_correlations = self.analytics.analyze_event_correlations(time_window_hours)
        regional_comparisons = self.analytics.compare_regional_tension(time_window_hours)
        trend_analysis = self.analytics.analyze_long_term_trends(time_window_hours)
        
        dashboard = {
            'timestamp': current_time.isoformat(),
            'time_window_hours': time_window_hours,
            'tension_patterns': tension_patterns,
            'event_correlations': event_correlations,
            'regional_comparisons': regional_comparisons,
            'trend_analysis': trend_analysis,
            'insights': self._generate_analytical_insights(
                tension_patterns, event_correlations, trend_analysis
            ),
            'forecasts': self.analytics.generate_tension_forecasts()
        }
        
        # Cache the result
        self._cached_data[cache_key] = dashboard
        self._cached_data[f'{cache_key}_timestamp'] = current_time
        
        return dashboard

    def get_alerts_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive alerts and monitoring dashboard"""
        current_time = datetime.utcnow()
        
        if self._is_cache_valid('alerts'):
            return self._cached_data['alerts']
        
        dashboard = {
            'timestamp': current_time.isoformat(),
            'active_alerts': self.alerts.get_active_alerts(),
            'alert_history': self.alerts.get_alert_history(
                self.config.alert_retention_hours
            ),
            'alert_statistics': self.alerts.get_alert_statistics(),
            'escalation_status': self.alerts.get_escalation_status(),
            'notification_log': self.alerts.get_notification_log(),
            'alert_trends': self._get_alert_trends(),
            'muted_alerts': self.alerts.get_muted_alerts()
        }
        
        # Cache the result
        self._cached_data['alerts'] = dashboard
        self._cached_data['alerts_timestamp'] = current_time
        
        return dashboard

    def get_live_data_stream(self) -> Dict[str, Any]:
        """Get real-time streaming data for live updates"""
        if not self.config.enable_real_time_updates:
            return {'status': 'disabled', 'message': 'Real-time updates are disabled'}
        
        # Never cache live data
        current_time = datetime.utcnow()
        
        return {
            'timestamp': current_time.isoformat(),
            'current_tensions': self._get_current_tensions(),
            'recent_events': self._get_recent_events(limit=10),
            'active_alerts': self.alerts.get_active_alerts()[:5],  # Top 5 alerts
            'system_vitals': self._get_system_vitals(),
            'update_frequency': self.config.refresh_interval_seconds
        }

    def export_dashboard_data(
        self,
        dashboard_type: str = 'overview',
        format: str = 'json',
        **kwargs
    ) -> str:
        """Export dashboard data for external use"""
        
        dashboard_methods = {
            'overview': self.get_overview_dashboard,
            'region': lambda: self.get_region_dashboard(
                kwargs.get('region_id', 'default'),
                kwargs.get('hours_back', 24)
            ),
            'health': self.get_system_health_dashboard,
            'analytics': lambda: self.get_analytics_dashboard(
                kwargs.get('time_window_hours', 168)
            ),
            'alerts': self.get_alerts_dashboard
        }
        
        if dashboard_type not in dashboard_methods:
            raise ValueError(f"Unknown dashboard type: {dashboard_type}")
        
        data = dashboard_methods[dashboard_type]()
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def clear_cache(self, cache_key: Optional[str] = None) -> None:
        """Clear dashboard cache"""
        if cache_key:
            self._cached_data.pop(cache_key, None)
            self._cached_data.pop(f'{cache_key}_timestamp', None)
        else:
            self._cached_data.clear()

    # Private helper methods
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cached_data:
            return False
        
        timestamp_key = f'{cache_key}_timestamp'
        if timestamp_key not in self._cached_data:
            return False
        
        cache_age = (datetime.utcnow() - self._cached_data[timestamp_key]).total_seconds()
        return cache_age < self._cache_ttl_seconds

    def _get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        health = self.metrics.get_system_health_report()
        alerts = self.alerts.get_active_alerts()
        
        # Determine overall status
        if any(alert['severity'] == 'critical' for alert in alerts):
            status = 'critical'
        elif any(alert['severity'] == 'warning' for alert in alerts):
            status = 'warning'
        elif health.get('status') == 'healthy':
            status = 'healthy'
        else:
            status = 'unknown'
        
        return {
            'status': status,
            'health_score': self._calculate_health_score(health, alerts),
            'active_alerts_count': len(alerts),
            'critical_alerts_count': sum(1 for a in alerts if a['severity'] == 'critical'),
            'last_health_check': health.get('timestamp', datetime.utcnow().isoformat())
        }

    def _get_regional_overview(self) -> List[Dict[str, Any]]:
        """Get overview of all regions"""
        regions_data = []
        
        for region_id, metrics in self.metrics.region_metrics.items():
            if len(regions_data) >= self.config.max_regions_displayed:
                break
            
            analysis = self.metrics.get_region_analysis(region_id, 24)
            alerts = self.alerts.get_region_alerts(region_id)
            
            regions_data.append({
                'region_id': region_id,
                'current_tension': metrics['current_tension'],
                'average_tension': metrics['average_tension'],
                'peak_tension': metrics['peak_tension'],
                'event_count': metrics['event_count'],
                'alert_count': len(alerts),
                'risk_level': analysis.get('risk_assessment', {}).get('level', 'unknown'),
                'last_update': metrics['last_update'].isoformat() if metrics['last_update'] else None
            })
        
        # Sort by current tension (highest first)
        regions_data.sort(key=lambda x: x['current_tension'], reverse=True)
        return regions_data

    def _get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent tension events"""
        recent_events = []
        cutoff_time = datetime.utcnow() - timedelta(hours=6)  # Last 6 hours
        
        for metric in list(self.metrics.tension_history)[-limit*2:]:  # Get more to filter
            if metric.timestamp >= cutoff_time and metric.event_type:
                recent_events.append({
                    'timestamp': metric.timestamp.isoformat(),
                    'region_id': metric.region_id,
                    'poi_id': metric.poi_id,
                    'event_type': metric.event_type,
                    'tension_level': metric.tension_level,
                    'metadata': metric.metadata
                })
        
        # Sort by timestamp (newest first) and limit
        recent_events.sort(key=lambda x: x['timestamp'], reverse=True)
        return recent_events[:limit]

    def _get_performance_overview(self) -> Dict[str, Any]:
        """Get performance metrics overview"""
        performance = self.metrics._get_performance_summary()
        
        return {
            'uptime_hours': performance.get('uptime_hours', 0),
            'error_count': performance.get('error_count', 0),
            'avg_calculation_time_ms': performance.get('calculation_performance', {}).get('average_ms', 0),
            'avg_api_response_time_ms': performance.get('api_performance', {}).get('average_ms', 0),
            'p95_response_time_ms': performance.get('api_performance', {}).get('p95_ms', 0)
        }

    def _generate_region_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for a region based on analysis"""
        recommendations = []
        
        risk_assessment = analysis.get('risk_assessment', {})
        risk_level = risk_assessment.get('level', 'unknown')
        risk_factors = risk_assessment.get('factors', [])
        
        if risk_level == 'high':
            recommendations.append("Consider implementing immediate tension reduction measures")
            if 'sustained_high_tension' in risk_factors:
                recommendations.append("Deploy additional peacekeeping forces or festivals")
        
        if risk_level == 'medium':
            recommendations.append("Monitor closely for escalation patterns")
            if 'high_volatility' in risk_factors:
                recommendations.append("Investigate sources of tension volatility")
        
        tension_trend = analysis.get('tension_trend', 'stable')
        if tension_trend == 'increasing':
            recommendations.append("Trend analysis shows increasing tension - proactive intervention recommended")
        
        if not recommendations:
            recommendations.append("Region appears stable - maintain current monitoring")
        
        return recommendations

    def _get_poi_details(self, region_id: str, hours_back: int) -> Dict[str, Any]:
        """Get detailed POI analysis for a region"""
        analysis = self.metrics.get_region_analysis(region_id, hours_back)
        return analysis.get('poi_details', {})

    def _get_error_analysis(self) -> Dict[str, Any]:
        """Get error analysis and trends"""
        # This would be implemented with more detailed error tracking
        return {
            'total_errors': self.metrics.performance_metrics['error_count'],
            'error_rate': 0.0,  # Would calculate based on total operations
            'common_error_types': [],  # Would categorize errors
            'error_trend': 'stable'  # Would analyze error patterns
        }

    def _get_capacity_metrics(self) -> Dict[str, Any]:
        """Get system capacity and resource utilization"""
        return {
            'memory_usage_percent': 0.0,  # Would get from system monitoring
            'cpu_usage_percent': 0.0,
            'storage_usage_percent': 0.0,
            'concurrent_connections': 0,
            'throughput_per_second': 0.0
        }

    def _get_uptime_statistics(self) -> Dict[str, Any]:
        """Get system uptime statistics"""
        uptime_hours = (datetime.utcnow() - self.metrics.performance_metrics['uptime_start']).total_seconds() / 3600
        
        return {
            'current_uptime_hours': uptime_hours,
            'uptime_percentage_7d': 99.9,  # Would calculate from actual data
            'uptime_percentage_30d': 99.8,
            'last_restart': self.metrics.performance_metrics['uptime_start'].isoformat(),
            'planned_downtime_upcoming': False
        }

    def _get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration and environment status"""
        return {
            'environment': 'production',  # Would get from environment
            'version': '1.0.0',  # Would get from package info
            'config_last_updated': datetime.utcnow().isoformat(),
            'feature_flags': {
                'real_time_updates': self.config.enable_real_time_updates,
                'detailed_metrics': self.config.show_detailed_metrics
            }
        }

    def _generate_analytical_insights(
        self,
        patterns: Dict[str, Any],
        correlations: Dict[str, Any],
        trends: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from analytical data"""
        insights = []
        
        # Example insights - would be more sophisticated in practice
        insights.append("System is operating within normal parameters")
        insights.append("No significant correlation patterns detected")
        insights.append("Tension levels showing seasonal variation")
        
        return insights

    def _get_alert_trends(self) -> Dict[str, Any]:
        """Get alert frequency and trend analysis"""
        return {
            'alerts_last_24h': 0,
            'alerts_last_week': 0,
            'trend': 'stable',
            'most_common_alert_type': 'high_tension',
            'average_resolution_time_minutes': 30
        }

    def _get_current_tensions(self) -> Dict[str, float]:
        """Get current tension levels for all regions"""
        return {
            region_id: metrics['current_tension']
            for region_id, metrics in self.metrics.region_metrics.items()
        }

    def _get_system_vitals(self) -> Dict[str, Any]:
        """Get real-time system vital signs"""
        return {
            'active_regions': len(self.metrics.region_metrics),
            'events_per_minute': 0.0,  # Would calculate from recent events
            'response_time_ms': 0.0,  # Would get latest response time
            'memory_usage_mb': 0.0,  # Would get from system monitoring
            'connections_active': 0
        }

    def _calculate_health_score(self, health: Dict[str, Any], alerts: List[Dict[str, Any]]) -> float:
        """Calculate overall system health score (0-100)"""
        base_score = 100.0
        
        # Deduct points for alerts
        for alert in alerts:
            if alert['severity'] == 'critical':
                base_score -= 20
            elif alert['severity'] == 'warning':
                base_score -= 5
        
        # Deduct points for performance issues
        performance = health.get('performance', {})
        if 'api_performance' in performance:
            avg_response = performance['api_performance'].get('average_ms', 0)
            if avg_response > 1000:  # Slow responses
                base_score -= 10
        
        return max(0.0, min(100.0, base_score)) 