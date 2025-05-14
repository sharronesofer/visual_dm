"""
Monitoring and metrics management system.
"""

import time
import json
import logging
import threading
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime, timedelta
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

class Metric:
    """Metric data structure."""
    
    def __init__(
        self,
        name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[float] = None
    ):
        """Initialize metric.
        
        Args:
            name: Metric name
            value: Metric value
            tags: Optional metric tags
            timestamp: Optional timestamp
        """
        self.name = name
        self.value = value
        self.tags = tags or {}
        self.timestamp = timestamp or time.time()

class MonitoringManager:
    """Manages monitoring and metrics collection."""
    
    def __init__(
        self,
        push_interval: int = 60,  # 1 minute
        retention_period: int = 604800  # 7 days
    ):
        """Initialize the monitoring manager.
        
        Args:
            push_interval: Interval for pushing metrics in seconds
            retention_period: Metric retention period in seconds
        """
        try:
            self.push_interval = push_interval
            self.retention_period = retention_period
            
            self.metrics: List[Metric] = []
            self.running = False
            self.push_thread = None
            
            # Create metrics directory
            self.metrics_dir = Path("metrics")
            self.metrics_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("Monitoring manager initialized")
            
        except Exception as e:
            handle_component_error(
                "MonitoringManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def record_metric(
        self,
        name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric.
        
        Args:
            name: Metric name
            value: Metric value
            tags: Optional metric tags
        """
        try:
            metric = Metric(name, value, tags)
            self.metrics.append(metric)
            
            logger.debug(f"Recorded metric: {name} = {value}")
            
        except Exception as e:
            handle_component_error(
                "MonitoringManager",
                "record_metric",
                e,
                ErrorSeverity.ERROR,
                {"name": name, "value": value}
            )
            
    def get_metrics(
        self,
        name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[Metric]:
        """Get metrics with optional filtering.
        
        Args:
            name: Filter by metric name
            tags: Filter by metric tags
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of filtered metrics
        """
        try:
            filtered_metrics = self.metrics
            
            if name:
                filtered_metrics = [m for m in filtered_metrics if m.name == name]
                
            if tags:
                filtered_metrics = [
                    m for m in filtered_metrics
                    if all(m.tags.get(k) == v for k, v in tags.items())
                ]
                
            if start_time:
                filtered_metrics = [
                    m for m in filtered_metrics
                    if m.timestamp >= start_time
                ]
                
            if end_time:
                filtered_metrics = [
                    m for m in filtered_metrics
                    if m.timestamp <= end_time
                ]
                
            return filtered_metrics
            
        except Exception as e:
            handle_component_error(
                "MonitoringManager",
                "get_metrics",
                e,
                ErrorSeverity.ERROR
            )
            return []
            
    def get_metric_statistics(
        self,
        name: str,
        tags: Optional[Dict[str, str]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Dict[str, float]:
        """Get statistics for a metric.
        
        Args:
            name: Metric name
            tags: Optional metric tags
            start_time: Optional start time
            end_time: Optional end time
            
        Returns:
            Dictionary with metric statistics
        """
        try:
            metrics = self.get_metrics(name, tags, start_time, end_time)
            if not metrics:
                return {
                    "min": 0,
                    "max": 0,
                    "avg": 0,
                    "sum": 0,
                    "count": 0
                }
                
            values = [m.value for m in metrics]
            return {
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "sum": sum(values),
                "count": len(values)
            }
            
        except Exception as e:
            handle_component_error(
                "MonitoringManager",
                "get_metric_statistics",
                e,
                ErrorSeverity.ERROR,
                {"name": name}
            )
            return {
                "min": 0,
                "max": 0,
                "avg": 0,
                "sum": 0,
                "count": 0
            }
            
    def _push_metrics(self) -> None:
        """Push metrics to storage."""
        try:
            while self.running:
                # Get metrics to push
                current_time = time.time()
                metrics_to_push = [
                    m for m in self.metrics
                    if current_time - m.timestamp <= self.retention_period
                ]
                
                if metrics_to_push:
                    # Generate filename with timestamp
                    filename = f"metrics_{int(current_time)}.json"
                    filepath = self.metrics_dir / filename
                    
                    # Save metrics
                    with open(filepath, "w") as f:
                        json.dump(
                            [
                                {
                                    "name": m.name,
                                    "value": m.value,
                                    "tags": m.tags,
                                    "timestamp": m.timestamp
                                }
                                for m in metrics_to_push
                            ],
                            f,
                            indent=4
                        )
                        
                    logger.info(f"Pushed {len(metrics_to_push)} metrics")
                    
                    # Clean up old metrics
                    self.metrics = [
                        m for m in self.metrics
                        if current_time - m.timestamp <= self.retention_period
                    ]
                    
                # Sleep until next push
                time.sleep(self.push_interval)
                
        except Exception as e:
            handle_component_error(
                "MonitoringManager",
                "_push_metrics",
                e,
                ErrorSeverity.ERROR
            )
            
    def start(self) -> None:
        """Start the monitoring manager."""
        try:
            if self.running:
                return
                
            self.running = True
            self.push_thread = threading.Thread(
                target=self._push_metrics,
                daemon=True
            )
            self.push_thread.start()
            
            logger.info("Monitoring manager started")
            
        except Exception as e:
            handle_component_error(
                "MonitoringManager",
                "start",
                e,
                ErrorSeverity.ERROR
            )
            
    def stop(self) -> None:
        """Stop the monitoring manager."""
        try:
            self.running = False
            if self.push_thread:
                self.push_thread.join()
                
            logger.info("Monitoring manager stopped")
            
        except Exception as e:
            handle_component_error(
                "MonitoringManager",
                "stop",
                e,
                ErrorSeverity.ERROR
            )
            
    def cleanup(self) -> None:
        """Clean up monitoring resources."""
        try:
            self.stop()
            self.metrics.clear()
            
            logger.info("Monitoring manager cleaned up")
            
        except Exception as e:
            handle_component_error(
                "MonitoringManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 