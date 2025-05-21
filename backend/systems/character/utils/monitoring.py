"""
System monitoring and performance metrics for Visual DM backend.

This module provides logging, metrics collection, and monitoring capabilities
for tracking system performance and debugging.
"""
import logging
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
import threading
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/system.log")
    ]
)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Create a central logger instance
integration_logger = logging.getLogger("integration")

class PerformanceMetrics:
    """
    Collects and stores performance metrics for different system components.
    Supports both synchronous and asynchronous code.
    """
    
    def __init__(self):
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
    def start_timer(self, component: str, operation: str) -> int:
        """
        Start a timer for measuring operation duration
        
        Args:
            component: System component (e.g., "inventory", "websocket")
            operation: Specific operation being timed
            
        Returns:
            Timer ID for stopping the timer later
        """
        timer_id = int(time.time() * 1000)
        
        with self._lock:
            if component not in self._metrics:
                self._metrics[component] = {}
                
            self._metrics[component][f"{operation}_{timer_id}"] = {
                "start_time": time.time(),
                "operation": operation,
                "completed": False
            }
            
        return timer_id
    
    def stop_timer(self, component: str, operation: str, timer_id: int, metadata: Optional[Dict[str, Any]] = None) -> float:
        """
        Stop a timer and record the duration
        
        Args:
            component: System component
            operation: Operation being timed
            timer_id: Timer ID from start_timer
            metadata: Additional information about the operation
            
        Returns:
            Duration of the operation in seconds
        """
        end_time = time.time()
        duration = 0.0
        
        with self._lock:
            if component in self._metrics:
                timer_key = f"{operation}_{timer_id}"
                if timer_key in self._metrics[component]:
                    timer_data = self._metrics[component][timer_key]
                    duration = end_time - timer_data["start_time"]
                    timer_data["duration"] = duration
                    timer_data["completed"] = True
                    timer_data["end_time"] = end_time
                    
                    if metadata:
                        timer_data["metadata"] = metadata
        
        # Log slow operations (> 1 second)
        if duration > 1.0:
            integration_logger.warning(
                f"Slow operation detected - Component: {component}, Operation: {operation}, "
                f"Duration: {duration:.3f}s, Metadata: {metadata or {}}"
            )
        
        return duration
    
    async def async_measure(self, component: str, operation: str, coroutine, metadata: Optional[Dict[str, Any]] = None):
        """
        Measure duration of an asynchronous operation
        
        Args:
            component: System component
            operation: Operation being measured
            coroutine: Coroutine to execute and measure
            metadata: Additional information about the operation
            
        Returns:
            Result of the coroutine execution
        """
        timer_id = self.start_timer(component, operation)
        
        try:
            result = await coroutine
            return result
        finally:
            self.stop_timer(component, operation, timer_id, metadata)
    
    def measure(self, component: str, operation: str, func: Callable, *args, **kwargs):
        """
        Measure duration of a synchronous function call
        
        Args:
            component: System component
            operation: Operation being measured
            func: Function to call and measure
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the function call
        """
        timer_id = self.start_timer(component, operation)
        metadata = {"args_count": len(args), "kwargs_keys": list(kwargs.keys())}
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            self.stop_timer(component, operation, timer_id, metadata)
    
    def get_metrics(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Get collected metrics
        
        Args:
            component: Optionally filter by component name
            
        Returns:
            Dictionary of metrics
        """
        with self._lock:
            if component:
                return self._metrics.get(component, {}).copy()
            return self._metrics.copy()
    
    def get_average_duration(self, component: str, operation: str) -> float:
        """
        Get average duration for a specific operation
        
        Args:
            component: System component
            operation: Operation to get average duration for
            
        Returns:
            Average duration in seconds or 0 if no data
        """
        durations = []
        
        with self._lock:
            if component in self._metrics:
                for key, data in self._metrics[component].items():
                    if data["operation"] == operation and data["completed"]:
                        durations.append(data["duration"])
        
        if durations:
            return sum(durations) / len(durations)
        return 0.0
    
    def reset_metrics(self, component: Optional[str] = None):
        """
        Reset collected metrics
        
        Args:
            component: Optionally reset only for specific component
        """
        with self._lock:
            if component:
                self._metrics[component] = {}
            else:
                self._metrics = {}
    
    def export_metrics(self, file_path: Optional[str] = None) -> str:
        """
        Export metrics to a JSON file
        
        Args:
            file_path: Path to save metrics to (default: logs/metrics_{timestamp}.json)
            
        Returns:
            Path to the saved file
        """
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"logs/metrics_{timestamp}.json"
        
        with self._lock:
            with open(file_path, "w") as f:
                json.dump(self._metrics, f, indent=2)
        
        return file_path
    
    def log_metrics_summary(self):
        """Log a summary of collected metrics"""
        summary = {}
        
        with self._lock:
            for component, data in self._metrics.items():
                op_summary = {}
                for timer_key, timer_data in data.items():
                    if not timer_data["completed"]:
                        continue
                        
                    operation = timer_data["operation"]
                    duration = timer_data["duration"]
                    
                    if operation not in op_summary:
                        op_summary[operation] = {
                            "count": 0,
                            "total_duration": 0.0,
                            "min_duration": float("inf"),
                            "max_duration": 0.0
                        }
                    
                    op_summary[operation]["count"] += 1
                    op_summary[operation]["total_duration"] += duration
                    op_summary[operation]["min_duration"] = min(op_summary[operation]["min_duration"], duration)
                    op_summary[operation]["max_duration"] = max(op_summary[operation]["max_duration"], duration)
                
                for op, stats in op_summary.items():
                    stats["avg_duration"] = stats["total_duration"] / stats["count"]
                    
                summary[component] = op_summary
        
        for component, op_summary in summary.items():
            for operation, stats in op_summary.items():
                integration_logger.info(
                    f"Metrics - Component: {component}, Operation: {operation}, "
                    f"Count: {stats['count']}, Avg: {stats['avg_duration']:.3f}s, "
                    f"Min: {stats['min_duration']:.3f}s, Max: {stats['max_duration']:.3f}s"
                )

# Create singleton instance
performance_metrics = PerformanceMetrics()

# Decorator for monitoring function performance
def monitor(component: str, operation: Optional[str] = None):
    """
    Decorator for monitoring function performance
    
    Args:
        component: System component
        operation: Operation name (defaults to function name)
    """
    def decorator(func):
        nonlocal operation
        if operation is None:
            operation = func.__name__
            
        if asyncio.iscoroutinefunction(func):
            async def wrapper(*args, **kwargs):
                return await performance_metrics.async_measure(
                    component, operation, func(*args, **kwargs)
                )
        else:
            def wrapper(*args, **kwargs):
                return performance_metrics.measure(
                    component, operation, func, *args, **kwargs
                )
                
        return wrapper
    return decorator 
