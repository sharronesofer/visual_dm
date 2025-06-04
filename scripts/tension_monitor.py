#!/usr/bin/env python3
"""
Tension System Monitoring CLI

A comprehensive command-line monitoring dashboard for the tension system that provides:
- Real-time tension metrics across all regions
- System health monitoring for all integrations
- Performance profiling and bottleneck identification
- Historical trend analysis
- Alert management and notification system
- Configuration hot-reloading

Usage:
    python tools/tension_monitor.py --mode dashboard
    python tools/tension_monitor.py --mode alerts --region region_1
    python tools/tension_monitor.py --mode performance --duration 1h
"""

import asyncio
import argparse
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

# Set up monitoring-specific logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MonitoringMode(Enum):
    """Monitoring operation modes"""
    DASHBOARD = "dashboard"
    ALERTS = "alerts"
    PERFORMANCE = "performance"
    HEALTH = "health"
    TRENDS = "trends"
    CONFIG = "config"


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    response_time_ms: float
    active_calculations: int
    cache_hit_rate: float
    error_rate: float
    integration_statuses: Dict[str, str]


@dataclass
class TensionAlert:
    """Tension system alert"""
    alert_id: str
    severity: str  # low, medium, high, critical
    region_id: str
    poi_id: Optional[str]
    message: str
    timestamp: datetime
    acknowledged: bool
    auto_resolve: bool


class TensionMonitor:
    """CLI-based tension system monitoring dashboard"""
    
    def __init__(self):
        self.running = True
        self.refresh_interval = 5  # seconds
        self.alerts: List[TensionAlert] = []
        self.metrics_history: List[SystemMetrics] = []
        self.max_history = 1000  # Keep last 1000 metrics
        
        # Monitoring configuration
        self.config = {
            'alert_thresholds': {
                'high_tension': 0.8,
                'critical_tension': 0.9,
                'performance_degradation': 1000,  # ms
                'error_rate_threshold': 0.05
            },
            'regions_to_monitor': ['all'],
            'auto_refresh': True,
            'notification_enabled': True
        }
        
    async def start_monitoring(self, mode: MonitoringMode, **kwargs) -> None:
        """Start monitoring in specified mode"""
        logger.info(f"Starting tension monitoring in {mode.value} mode")
        
        try:
            if mode == MonitoringMode.DASHBOARD:
                await self._run_dashboard()
            elif mode == MonitoringMode.ALERTS:
                await self._run_alert_monitoring(kwargs.get('region'))
            elif mode == MonitoringMode.PERFORMANCE:
                await self._run_performance_monitoring(kwargs.get('duration', '30m'))
            elif mode == MonitoringMode.HEALTH:
                await self._run_health_monitoring()
            elif mode == MonitoringMode.TRENDS:
                await self._run_trend_analysis(kwargs.get('timeframe', '24h'))
            elif mode == MonitoringMode.CONFIG:
                await self._run_config_management()
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
    
    async def _run_dashboard(self) -> None:
        """Run the main monitoring dashboard"""
        print("\n" + "="*80)
        print("TENSION SYSTEM MONITORING DASHBOARD")
        print("="*80)
        print("Press 'q' to quit, 'r' to refresh, 'a' for alerts, 'h' for help")
        
        while self.running:
            try:
                # Clear screen (simple version)
                print("\033[H\033[J", end="")
                
                # Header
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Tension System Dashboard - {current_time}")
                print("-" * 80)
                
                # System overview
                await self._display_system_overview()
                
                # Region tension summary
                await self._display_region_summary()
                
                # Integration health
                await self._display_integration_health()
                
                # Recent alerts
                await self._display_recent_alerts()
                
                # Performance metrics
                await self._display_performance_metrics()
                
                # Wait for next refresh or user input
                await asyncio.sleep(self.refresh_interval)
                
            except Exception as e:
                logger.error(f"Dashboard error: {e}")
                await asyncio.sleep(1)
    
    async def _run_alert_monitoring(self, region: Optional[str] = None) -> None:
        """Run alert-focused monitoring"""
        print(f"\nTENSION ALERT MONITORING" + (f" - Region: {region}" if region else ""))
        print("-" * 60)
        
        while self.running:
            # Check for new alerts
            new_alerts = await self._check_for_alerts(region)
            
            for alert in new_alerts:
                self._process_alert(alert)
            
            # Display active alerts
            self._display_alert_summary()
            
            await asyncio.sleep(2)  # More frequent for alerts
    
    async def _run_performance_monitoring(self, duration: str) -> None:
        """Run performance-focused monitoring"""
        print(f"\nTENSION PERFORMANCE MONITORING - Duration: {duration}")
        print("-" * 60)
        
        start_time = datetime.now()
        duration_delta = self._parse_duration(duration)
        
        while self.running and datetime.now() - start_time < duration_delta:
            metrics = await self._collect_performance_metrics()
            self._analyze_performance_metrics(metrics)
            
            # Display performance dashboard
            self._display_performance_dashboard(metrics)
            
            await asyncio.sleep(1)  # High frequency for performance monitoring
        
        # Generate performance report
        await self._generate_performance_report()
    
    async def _run_health_monitoring(self) -> None:
        """Run health-focused monitoring"""
        print("\nTENSION SYSTEM HEALTH MONITORING")
        print("-" * 60)
        
        while self.running:
            health_status = await self._collect_health_metrics()
            self._display_health_dashboard(health_status)
            
            # Check for health issues
            issues = self._detect_health_issues(health_status)
            if issues:
                print("\n⚠️  HEALTH ISSUES DETECTED:")
                for issue in issues:
                    print(f"   • {issue}")
            
            await asyncio.sleep(10)  # Health checks every 10 seconds
    
    async def _run_trend_analysis(self, timeframe: str) -> None:
        """Run trend analysis monitoring"""
        print(f"\nTENSION TREND ANALYSIS - Timeframe: {timeframe}")
        print("-" * 60)
        
        # Load historical data
        historical_data = await self._load_historical_data(timeframe)
        
        # Analyze trends
        trends = self._analyze_trends(historical_data)
        
        # Display trend analysis
        self._display_trend_analysis(trends)
        
        # Keep updating with new data
        while self.running:
            new_data = await self._collect_current_metrics()
            trends = self._update_trends(trends, new_data)
            self._display_trend_updates(trends)
            
            await asyncio.sleep(30)  # Update trends every 30 seconds
    
    async def _run_config_management(self) -> None:
        """Run configuration management interface"""
        print("\nTENSION SYSTEM CONFIGURATION MANAGEMENT")
        print("-" * 60)
        
        while self.running:
            print("\nConfiguration Options:")
            print("1. View current configuration")
            print("2. Update alert thresholds")
            print("3. Modify monitoring regions")
            print("4. Toggle auto-refresh")
            print("5. Export configuration")
            print("6. Import configuration")
            print("q. Quit")
            
            choice = input("\nEnter choice: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '1':
                self._display_current_config()
            elif choice == '2':
                await self._update_alert_thresholds()
            elif choice == '3':
                await self._modify_monitoring_regions()
            elif choice == '4':
                self._toggle_auto_refresh()
            elif choice == '5':
                self._export_configuration()
            elif choice == '6':
                await self._import_configuration()
    
    # Core monitoring methods
    async def _display_system_overview(self) -> None:
        """Display system overview section"""
        print("\n📊 SYSTEM OVERVIEW")
        print("-" * 40)
        
        # Mock data - would integrate with actual tension manager
        total_regions = 25
        high_tension_regions = 3
        active_conflicts = 1
        system_load = 78.5
        
        print(f"Total Regions: {total_regions}")
        print(f"High Tension Regions: {high_tension_regions}")
        print(f"Active Conflicts: {active_conflicts}")
        print(f"System Load: {system_load:.1f}%")
        
        # Health indicator
        health_status = "🟢 HEALTHY" if system_load < 85 else "🟡 DEGRADED" if system_load < 95 else "🔴 CRITICAL"
        print(f"Status: {health_status}")
    
    async def _display_region_summary(self) -> None:
        """Display region tension summary"""
        print("\n🗺️  REGION TENSION SUMMARY")
        print("-" * 40)
        
        # Mock region data - would integrate with actual data
        regions = [
            ("Region_Alpha", 0.85, "Critical"),
            ("Region_Beta", 0.62, "High"),
            ("Region_Gamma", 0.34, "Medium"),
            ("Region_Delta", 0.15, "Low"),
            ("Region_Epsilon", 0.08, "Peaceful")
        ]
        
        for region, tension, status in regions:
            indicator = "🔴" if tension > 0.8 else "🟡" if tension > 0.5 else "🟢"
            print(f"{indicator} {region:<15} {tension:.2f} ({status})")
    
    async def _display_integration_health(self) -> None:
        """Display integration health status"""
        print("\n🔧 INTEGRATION HEALTH")
        print("-" * 40)
        
        # Mock integration data
        integrations = [
            ("NPC Integration", "🟢", "Operational", 245),
            ("Quest Integration", "🟢", "Operational", 156),
            ("Combat Integration", "🟡", "Degraded", 89),
            ("Economy Integration", "🟢", "Operational", 334),
            ("Faction Integration", "🟢", "Operational", 167),
            ("ML Prediction", "🟢", "Operational", 78),
            ("Pattern Analysis", "🟢", "Operational", 92)
        ]
        
        for name, status, description, ops_count in integrations:
            print(f"{status} {name:<18} {description:<12} (Ops: {ops_count})")
    
    async def _display_recent_alerts(self) -> None:
        """Display recent alerts"""
        print("\n🚨 RECENT ALERTS")
        print("-" * 40)
        
        if not self.alerts:
            print("No active alerts")
            return
        
        recent_alerts = sorted(self.alerts, key=lambda x: x.timestamp, reverse=True)[:5]
        
        for alert in recent_alerts:
            severity_icon = {
                'low': '🟢',
                'medium': '🟡', 
                'high': '🟠',
                'critical': '🔴'
            }.get(alert.severity, '⚪')
            
            timestamp = alert.timestamp.strftime("%H:%M:%S")
            ack_status = "✓" if alert.acknowledged else "⏳"
            print(f"{severity_icon} {timestamp} {ack_status} {alert.message[:50]}...")
    
    async def _display_performance_metrics(self) -> None:
        """Display performance metrics"""
        print("\n⚡ PERFORMANCE METRICS")
        print("-" * 40)
        
        # Mock performance data
        metrics = {
            "Avg Response Time": "145ms",
            "Cache Hit Rate": "94.2%",
            "Memory Usage": "67.8%",
            "CPU Usage": "23.1%",
            "Active Calculations": "156",
            "Error Rate": "0.02%"
        }
        
        for metric, value in metrics.items():
            print(f"{metric:<20} {value}")
    
    async def _check_for_alerts(self, region: Optional[str] = None) -> List[TensionAlert]:
        """Check for new alerts"""
        new_alerts = []
        
        # Mock alert detection - would integrate with actual monitoring
        import random
        if random.random() < 0.1:  # 10% chance of new alert
            alert = TensionAlert(
                alert_id=f"alert_{len(self.alerts)}",
                severity=random.choice(['low', 'medium', 'high', 'critical']),
                region_id=region or f"region_{random.randint(1, 5)}",
                poi_id=f"poi_{random.randint(1, 10)}",
                message=f"Tension spike detected in {region or 'region'}",
                timestamp=datetime.now(),
                acknowledged=False,
                auto_resolve=False
            )
            new_alerts.append(alert)
        
        return new_alerts
    
    def _process_alert(self, alert: TensionAlert) -> None:
        """Process and store new alert"""
        self.alerts.append(alert)
        
        # Auto-notification
        if self.config['notification_enabled']:
            severity_color = {
                'low': '\033[92m',     # Green
                'medium': '\033[93m',  # Yellow
                'high': '\033[91m',    # Red
                'critical': '\033[95m' # Magenta
            }.get(alert.severity, '\033[0m')
            
            print(f"\n{severity_color}🚨 NEW ALERT: {alert.message}\033[0m")
    
    def _display_alert_summary(self) -> None:
        """Display alert summary"""
        if not self.alerts:
            print("No active alerts")
            return
        
        by_severity = {}
        for alert in self.alerts:
            if not alert.acknowledged:
                by_severity[alert.severity] = by_severity.get(alert.severity, 0) + 1
        
        print(f"Active Alerts: {sum(by_severity.values())}")
        for severity, count in by_severity.items():
            print(f"  {severity.title()}: {count}")
    
    async def _collect_performance_metrics(self) -> SystemMetrics:
        """Collect current performance metrics"""
        # Mock metrics collection - would integrate with actual monitoring
        import random
        import psutil
        
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent,
            response_time_ms=random.uniform(50, 300),
            active_calculations=random.randint(50, 200),
            cache_hit_rate=random.uniform(0.85, 0.98),
            error_rate=random.uniform(0.001, 0.05),
            integration_statuses={
                'npc': 'healthy',
                'quest': 'healthy', 
                'combat': 'degraded',
                'economy': 'healthy',
                'faction': 'healthy'
            }
        )
        
        # Store in history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)
        
        return metrics
    
    def _analyze_performance_metrics(self, metrics: SystemMetrics) -> None:
        """Analyze performance metrics for issues"""
        issues = []
        
        if metrics.response_time_ms > self.config['alert_thresholds']['performance_degradation']:
            issues.append(f"High response time: {metrics.response_time_ms:.1f}ms")
        
        if metrics.error_rate > self.config['alert_thresholds']['error_rate_threshold']:
            issues.append(f"High error rate: {metrics.error_rate:.3f}")
        
        if metrics.cpu_usage > 90:
            issues.append(f"High CPU usage: {metrics.cpu_usage:.1f}%")
        
        if metrics.memory_usage > 90:
            issues.append(f"High memory usage: {metrics.memory_usage:.1f}%")
        
        for issue in issues:
            logger.warning(f"Performance issue detected: {issue}")
    
    def _display_performance_dashboard(self, metrics: SystemMetrics) -> None:
        """Display performance monitoring dashboard"""
        print(f"\n⚡ PERFORMANCE DASHBOARD - {metrics.timestamp.strftime('%H:%M:%S')}")
        print("-" * 60)
        
        print(f"Response Time: {metrics.response_time_ms:.1f}ms")
        print(f"CPU Usage: {metrics.cpu_usage:.1f}%")
        print(f"Memory Usage: {metrics.memory_usage:.1f}%")
        print(f"Cache Hit Rate: {metrics.cache_hit_rate:.1%}")
        print(f"Error Rate: {metrics.error_rate:.3%}")
        print(f"Active Calculations: {metrics.active_calculations}")
        
        # Performance trend
        if len(self.metrics_history) > 1:
            prev_metrics = self.metrics_history[-2]
            response_trend = metrics.response_time_ms - prev_metrics.response_time_ms
            trend_indicator = "↗️" if response_trend > 10 else "↘️" if response_trend < -10 else "➡️"
            print(f"Response Trend: {trend_indicator} {response_trend:+.1f}ms")
    
    # Utility methods
    def _parse_duration(self, duration_str: str) -> timedelta:
        """Parse duration string into timedelta"""
        duration_str = duration_str.lower()
        
        if duration_str.endswith('s'):
            return timedelta(seconds=int(duration_str[:-1]))
        elif duration_str.endswith('m'):
            return timedelta(minutes=int(duration_str[:-1]))
        elif duration_str.endswith('h'):
            return timedelta(hours=int(duration_str[:-1]))
        elif duration_str.endswith('d'):
            return timedelta(days=int(duration_str[:-1]))
        else:
            return timedelta(minutes=30)  # Default
    
    async def _generate_performance_report(self) -> None:
        """Generate performance monitoring report"""
        if not self.metrics_history:
            print("No performance data to report")
            return
        
        print("\n📈 PERFORMANCE REPORT")
        print("=" * 60)
        
        # Calculate statistics
        response_times = [m.response_time_ms for m in self.metrics_history]
        cpu_usages = [m.cpu_usage for m in self.metrics_history]
        error_rates = [m.error_rate for m in self.metrics_history]
        
        print(f"Data Points: {len(self.metrics_history)}")
        print(f"Time Range: {self.metrics_history[0].timestamp} - {self.metrics_history[-1].timestamp}")
        print()
        print(f"Response Time - Avg: {sum(response_times)/len(response_times):.1f}ms, "
              f"Min: {min(response_times):.1f}ms, Max: {max(response_times):.1f}ms")
        print(f"CPU Usage - Avg: {sum(cpu_usages)/len(cpu_usages):.1f}%, "
              f"Min: {min(cpu_usages):.1f}%, Max: {max(cpu_usages):.1f}%")
        print(f"Error Rate - Avg: {sum(error_rates)/len(error_rates):.3%}, "
              f"Min: {min(error_rates):.3%}, Max: {max(error_rates):.3%}")
        
        # Export to file
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            'report_generated': datetime.now().isoformat(),
            'metrics_count': len(self.metrics_history),
            'summary': {
                'avg_response_time_ms': sum(response_times)/len(response_times),
                'avg_cpu_usage': sum(cpu_usages)/len(cpu_usages),
                'avg_error_rate': sum(error_rates)/len(error_rates)
            },
            'raw_metrics': [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'response_time_ms': m.response_time_ms,
                    'cpu_usage': m.cpu_usage,
                    'memory_usage': m.memory_usage,
                    'error_rate': m.error_rate
                } for m in self.metrics_history
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📁 Report saved to: {report_file}")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Tension System Monitoring CLI")
    parser.add_argument('--mode', choices=[m.value for m in MonitoringMode], 
                       default='dashboard', help='Monitoring mode')
    parser.add_argument('--region', help='Specific region to monitor')
    parser.add_argument('--duration', default='30m', help='Monitoring duration')
    parser.add_argument('--timeframe', default='24h', help='Analysis timeframe')
    parser.add_argument('--config-file', help='Configuration file path')
    parser.add_argument('--export-logs', action='store_true', help='Export logs to file')
    
    args = parser.parse_args()
    
    monitor = TensionMonitor()
    
    # Load configuration if provided
    if args.config_file:
        try:
            with open(args.config_file, 'r') as f:
                monitor.config.update(json.load(f))
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    
    # Start monitoring
    mode = MonitoringMode(args.mode)
    await monitor.start_monitoring(
        mode,
        region=args.region,
        duration=args.duration,
        timeframe=args.timeframe
    )


if __name__ == "__main__":
    try:
        import psutil  # For system metrics
    except ImportError:
        print("Installing required dependency: psutil")
        import subprocess
        subprocess.check_call(['pip', 'install', 'psutil'])
        import psutil
    
    asyncio.run(main()) 