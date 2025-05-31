"""
Chaos Analytics

Comprehensive analytics and monitoring system for chaos operations.
Tracks performance, events, patterns, and system health.
"""

import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pathlib import Path

from backend.systems.chaos.core.config import ChaosConfig
from backend.systems.chaos.models.chaos_events import ChaosEvent
from backend.systems.chaos.models.chaos_state import ChaosState
from backend.systems.chaos.models.pressure_data import PressureData

from .event_tracker import EventTracker
from .performance_monitor import PerformanceMonitor
from .configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class ChaosAnalytics:
    """
    Main analytics coordinator for the chaos system
    
    Integrates event tracking, performance monitoring, and configuration
    management to provide comprehensive insights and optimization capabilities.
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        
        # Initialize analytics components
        self.event_tracker = EventTracker(config)
        self.performance_monitor = PerformanceMonitor(config)
        self.configuration_manager = ConfigurationManager(config)
        
        # Analytics state
        self.is_initialized = False
        self.is_running = False
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        
        logger.info("Chaos Analytics initialized")
    
    async def initialize(self) -> None:
        """Initialize all analytics components"""
        try:
            logger.info("Initializing Chaos Analytics...")
            
            # Initialize components in order
            await self.event_tracker.initialize()
            await self.performance_monitor.initialize()
            await self.configuration_manager.initialize()
            
            # Start background analytics tasks
            await self._start_background_tasks()
            
            self.is_initialized = True
            self.is_running = True
            
            logger.info("Chaos Analytics initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chaos Analytics: {e}")
            raise
    
    async def _start_background_tasks(self) -> None:
        """Start background analytics tasks"""
        try:
            # Register configuration change listeners
            self._register_configuration_listeners()
            
            # Start periodic analytics snapshot task
            snapshot_task = asyncio.create_task(self._periodic_analytics_snapshot())
            self.background_tasks.append(snapshot_task)
            
            # Start periodic optimization analysis
            optimization_task = asyncio.create_task(self._periodic_optimization_analysis())
            self.background_tasks.append(optimization_task)
            
            logger.debug("Background analytics tasks started")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    def _register_configuration_listeners(self) -> None:
        """Register listeners for configuration changes"""
        try:
            # Listen for pressure weight changes
            self.configuration_manager.register_change_listener(
                'pressure_weights',
                self._on_pressure_weight_change
            )
            
            # Listen for performance setting changes
            self.configuration_manager.register_change_listener(
                'performance',
                self._on_performance_setting_change
            )
            
            # Listen for chaos threshold changes
            self.configuration_manager.register_change_listener(
                'chaos_thresholds',
                self._on_chaos_threshold_change
            )
            
            logger.debug("Configuration listeners registered")
            
        except Exception as e:
            logger.error(f"Error registering configuration listeners: {e}")
    
    async def _on_pressure_weight_change(self, path: str, new_value: Any, old_value: Any) -> None:
        """Handle pressure weight configuration changes"""
        logger.info(f"Pressure weight changed: {path} = {new_value} (was {old_value})")
        
        # Track configuration impact
        context_id = self.performance_monitor.start_operation("config_change_impact")
        try:
            # The change will naturally affect future pressure calculations
            # No immediate action needed, but we could trigger a recalculation
            pass
        finally:
            self.performance_monitor.end_operation(context_id, True, "config_change_impact")
    
    async def _on_performance_setting_change(self, path: str, new_value: Any, old_value: Any) -> None:
        """Handle performance setting configuration changes"""
        logger.info(f"Performance setting changed: {path} = {new_value} (was {old_value})")
        
        # Certain performance changes might require system adjustments
        if 'interval' in path:
            # Interval changes might affect background task timing
            logger.debug(f"Interval setting changed, may affect task scheduling")
    
    async def _on_chaos_threshold_change(self, path: str, new_value: Any, old_value: Any) -> None:
        """Handle chaos threshold configuration changes"""
        logger.info(f"Chaos threshold changed: {path} = {new_value} (was {old_value})")
        
        # Threshold changes affect event triggering logic
        # The chaos engine will pick up these changes automatically
    
    async def _periodic_analytics_snapshot(self) -> None:
        """Periodic task to take comprehensive analytics snapshots"""
        try:
            while self.is_running:
                # Take snapshots every 5 minutes
                await asyncio.sleep(300)
                
                if self.is_running:
                    context_id = self.performance_monitor.start_operation("analytics_snapshot")
                    try:
                        # Performance snapshot is taken automatically by the monitor
                        # Event tracker snapshots are taken when events occur
                        # This task could coordinate additional analytics activities
                        
                        logger.debug("Periodic analytics snapshot completed")
                    except Exception as e:
                        logger.error(f"Error in periodic analytics snapshot: {e}")
                    finally:
                        self.performance_monitor.end_operation(context_id, True, "analytics_snapshot")
                        
        except asyncio.CancelledError:
            logger.info("Periodic analytics snapshot task cancelled")
        except Exception as e:
            logger.error(f"Error in periodic analytics snapshot: {e}")
    
    async def _periodic_optimization_analysis(self) -> None:
        """Periodic task to analyze system performance and suggest optimizations"""
        try:
            while self.is_running:
                # Run optimization analysis every 30 minutes
                await asyncio.sleep(1800)
                
                if self.is_running:
                    context_id = self.performance_monitor.start_operation("optimization_analysis")
                    try:
                        await self._run_optimization_analysis()
                    except Exception as e:
                        logger.error(f"Error in optimization analysis: {e}")
                    finally:
                        self.performance_monitor.end_operation(context_id, True, "optimization_analysis")
                        
        except asyncio.CancelledError:
            logger.info("Periodic optimization analysis task cancelled")
        except Exception as e:
            logger.error(f"Error in periodic optimization analysis: {e}")
    
    async def _run_optimization_analysis(self) -> None:
        """Run comprehensive optimization analysis"""
        try:
            # Get performance trends
            performance_analysis = self.performance_monitor.analyze_performance_trends()
            
            # Get event patterns
            event_analysis = self.event_tracker.analyze_event_patterns()
            
            # Determine if optimization is needed
            if isinstance(performance_analysis, dict) and 'system_health_score' in performance_analysis:
                health_score = performance_analysis['system_health_score']
                
                if health_score < 0.7:  # Poor health
                    logger.info(f"System health score low ({health_score:.2f}), triggering optimization")
                    await self.configuration_manager.optimize_configuration("stability")
                    
                elif health_score < 0.8:  # Moderate health
                    # Check for specific performance issues
                    suggestions = performance_analysis.get('optimization_suggestions', [])
                    high_priority_issues = [s for s in suggestions if s.get('priority') == 'high']
                    
                    if high_priority_issues:
                        logger.info(f"Found {len(high_priority_issues)} high-priority performance issues")
                        await self.configuration_manager.optimize_configuration("performance")
            
            logger.debug("Optimization analysis completed")
            
        except Exception as e:
            logger.error(f"Error in optimization analysis: {e}")
    
    # Event tracking interface
    def track_event_created(self, chaos_event: ChaosEvent) -> None:
        """Track when a chaos event is created"""
        self.event_tracker.track_event_created(chaos_event)
    
    def track_event_triggered(self, chaos_event: ChaosEvent, 
                            chaos_state: ChaosState, pressure_data: PressureData) -> None:
        """Track when a chaos event is triggered"""
        self.event_tracker.track_event_triggered(chaos_event, chaos_state, pressure_data)
        self.event_tracker.take_analytics_snapshot(chaos_state, pressure_data)
    
    def track_event_resolved(self, event_id: str, resolution_type: str = "auto",
                           resolution_quality: float = 1.0, mitigation_applied: bool = False,
                           mitigation_effectiveness: float = 0.0) -> None:
        """Track when a chaos event is resolved"""
        self.event_tracker.track_event_resolved(
            event_id, resolution_type, resolution_quality, 
            mitigation_applied, mitigation_effectiveness
        )
    
    def track_cascade_event(self, parent_event_id: str, cascade_event_id: str) -> None:
        """Track cascade relationship between events"""
        self.event_tracker.track_cascade_event(parent_event_id, cascade_event_id)
    
    # Performance monitoring interface
    def start_operation(self, operation_name: str) -> str:
        """Start timing an operation"""
        return self.performance_monitor.start_operation(operation_name)
    
    def end_operation(self, context_id: str, success: bool = True, 
                     operation_name: Optional[str] = None) -> float:
        """End timing an operation"""
        return self.performance_monitor.end_operation(context_id, success, operation_name)
    
    def record_metric(self, metric_type, value: float, operation_name: Optional[str] = None) -> None:
        """Record a performance metric"""
        self.performance_monitor.record_metric(metric_type, value, operation_name)
    
    # Configuration management interface
    async def get_configuration(self, path: Optional[str] = None) -> Any:
        """Get configuration value(s)"""
        return self.configuration_manager.get_configuration(path)
    
    async def set_configuration(self, path: str, value: Any, changed_by: str = "system",
                              reason: str = "") -> bool:
        """Set a configuration value"""
        return await self.configuration_manager.set_configuration(path, value, changed_by, reason)
    
    # Analytics and reporting interface
    async def get_comprehensive_report(self, time_period_hours: int = 24) -> Dict[str, Any]:
        """Get a comprehensive analytics report"""
        try:
            context_id = self.performance_monitor.start_operation("comprehensive_report")
            
            try:
                # Get component reports
                event_summary = self.event_tracker.get_event_summary(time_period_hours)
                event_patterns = self.event_tracker.analyze_event_patterns()
                performance_summary = self.performance_monitor.get_performance_summary()
                performance_trends = self.performance_monitor.analyze_performance_trends()
                config_metrics = self.configuration_manager.get_configuration_metrics()
                config_history = self.configuration_manager.get_configuration_history(20)
                
                # Compile comprehensive report
                report = {
                    'timestamp': datetime.now().isoformat(),
                    'time_period_hours': time_period_hours,
                    'summary': {
                        'events': event_summary,
                        'performance': performance_summary,
                        'configuration': config_metrics
                    },
                    'analysis': {
                        'event_patterns': event_patterns,
                        'performance_trends': performance_trends
                    },
                    'recent_changes': {
                        'configuration_history': config_history,
                        'performance_alerts': self.performance_monitor.get_recent_alerts(10)
                    },
                    'system_health': {
                        'overall_score': performance_trends.get('system_health_score', 0.5) if isinstance(performance_trends, dict) else 0.5,
                        'is_running': self.is_running,
                        'components_initialized': self.is_initialized
                    }
                }
                
                return report
                
            finally:
                self.performance_monitor.end_operation(context_id, True, "comprehensive_report")
                
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {"error": str(e)}
    
    async def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get optimization recommendations based on current analytics"""
        try:
            # Get performance analysis
            performance_analysis = self.performance_monitor.analyze_performance_trends()
            
            # Get event patterns
            event_patterns = self.event_tracker.analyze_event_patterns()
            
            # Compile recommendations
            recommendations = {
                'timestamp': datetime.now().isoformat(),
                'performance_recommendations': [],
                'configuration_recommendations': [],
                'system_recommendations': []
            }
            
            # Performance-based recommendations
            if isinstance(performance_analysis, dict):
                suggestions = performance_analysis.get('optimization_suggestions', [])
                recommendations['performance_recommendations'] = suggestions
                
                # System health recommendations
                health_score = performance_analysis.get('system_health_score', 0.5)
                if health_score < 0.6:
                    recommendations['system_recommendations'].append({
                        'priority': 'critical',
                        'type': 'system_health',
                        'issue': f'Low system health score: {health_score:.2f}',
                        'recommendation': 'Consider reducing system load or optimizing configuration'
                    })
                
                elif health_score < 0.8:
                    recommendations['system_recommendations'].append({
                        'priority': 'medium',
                        'type': 'system_health',
                        'issue': f'Moderate system health score: {health_score:.2f}',
                        'recommendation': 'Monitor system closely and consider performance tuning'
                    })
            
            # Event-based recommendations
            if isinstance(event_patterns, dict) and 'cascade_patterns' in event_patterns:
                cascade_rate = event_patterns['cascade_patterns'].get('cascade_rate', 0.0)
                if cascade_rate > 0.3:  # High cascade rate
                    recommendations['configuration_recommendations'].append({
                        'priority': 'high',
                        'type': 'event_cascading',
                        'issue': f'High event cascade rate: {cascade_rate:.1%}',
                        'recommendation': 'Consider adjusting chaos thresholds or event probabilities'
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
            return {"error": str(e)}
    
    async def export_analytics_data(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Export all analytics data to files"""
        try:
            if not output_dir:
                output_dir = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            export_dir = Path(output_dir)
            export_dir.mkdir(exist_ok=True)
            
            exported_files = {}
            
            # Export event tracker data
            await self.event_tracker.save_analytics_data()
            exported_files['event_data'] = str(export_dir / "event_analytics.json")
            
            # Export performance data
            performance_summary = self.performance_monitor.get_performance_summary()
            performance_file = export_dir / "performance_analytics.json"
            with open(performance_file, 'w') as f:
                import json
                json.dump(performance_summary, f, indent=2)
            exported_files['performance_data'] = str(performance_file)
            
            # Export configuration data
            config_export = self.configuration_manager.export_configuration(include_history=True)
            config_file = export_dir / "configuration_analytics.json"
            with open(config_file, 'w') as f:
                import json
                json.dump(config_export, f, indent=2)
            exported_files['configuration_data'] = str(config_file)
            
            # Export comprehensive report
            comprehensive_report = await self.get_comprehensive_report(168)  # 1 week
            report_file = export_dir / "comprehensive_report.json"
            with open(report_file, 'w') as f:
                import json
                json.dump(comprehensive_report, f, indent=2)
            exported_files['comprehensive_report'] = str(report_file)
            
            logger.info(f"Analytics data exported to {export_dir}")
            return exported_files
            
        except Exception as e:
            logger.error(f"Error exporting analytics data: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_data(self, max_age_days: int = 30) -> None:
        """Clean up old analytics data"""
        try:
            await self.event_tracker.cleanup_old_data(max_age_days)
            logger.info(f"Cleaned up analytics data older than {max_age_days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown analytics system gracefully"""
        try:
            logger.info("Shutting down Chaos Analytics...")
            
            self.is_running = False
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Save final analytics data
            await self.event_tracker.save_analytics_data()
            
            # Stop performance monitoring
            self.performance_monitor.stop_monitoring()
            
            logger.info("Chaos Analytics shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during analytics shutdown: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current analytics system status"""
        return {
            'is_initialized': self.is_initialized,
            'is_running': self.is_running,
            'components': {
                'event_tracker': {
                    'initialized': self.event_tracker.is_initialized,
                    'active_events': len(self.event_tracker.active_event_records),
                    'total_events': len(self.event_tracker.event_records)
                },
                'performance_monitor': {
                    'monitoring_enabled': self.performance_monitor.monitoring_enabled,
                    'snapshots_taken': len(self.performance_monitor.snapshots),
                    'operations_tracked': len(self.performance_monitor.operation_metrics)
                },
                'configuration_manager': {
                    'validation_enabled': self.configuration_manager.validation_enabled,
                    'changes_applied': self.configuration_manager.configuration_metrics['changes_applied'],
                    'active_listeners': sum(len(listeners) for listeners in self.configuration_manager.change_listeners.values())
                }
            },
            'background_tasks': {
                'total_tasks': len(self.background_tasks),
                'running_tasks': sum(1 for task in self.background_tasks if not task.done())
            }
        } 