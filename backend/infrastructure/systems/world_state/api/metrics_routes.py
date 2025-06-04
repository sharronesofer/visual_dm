"""
Metrics and Monitoring endpoints for World State System

Provides performance metrics, health checks, and monitoring data
for system observability and optimization.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
import asyncio
import time
import psutil
import logging

from backend.systems.world_state.services.services import WorldStateService, create_world_state_service

router = APIRouter(prefix="/api/v1/world-state/metrics", tags=["world-state-metrics"])
logger = logging.getLogger(__name__)

# Performance tracking
class PerformanceTracker:
    """Tracks performance metrics for world state operations"""
    
    def __init__(self):
        self.operation_times: Dict[str, List[float]] = {}
        self.operation_counts: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}
        self.last_reset = datetime.utcnow()
    
    def record_operation(self, operation: str, duration: float, success: bool = True):
        """Record operation performance"""
        if operation not in self.operation_times:
            self.operation_times[operation] = []
            self.operation_counts[operation] = 0
            self.error_counts[operation] = 0
        
        self.operation_times[operation].append(duration)
        self.operation_counts[operation] += 1
        
        if not success:
            self.error_counts[operation] += 1
        
        # Keep only last 1000 measurements per operation
        if len(self.operation_times[operation]) > 1000:
            self.operation_times[operation] = self.operation_times[operation][-1000:]
    
    def get_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for an operation"""
        if operation not in self.operation_times:
            return {"error": "Operation not found"}
        
        times = self.operation_times[operation]
        if not times:
            return {"error": "No data available"}
        
        return {
            "operation": operation,
            "total_calls": self.operation_counts[operation],
            "error_count": self.error_counts[operation],
            "error_rate": self.error_counts[operation] / self.operation_counts[operation],
            "avg_duration_ms": sum(times) / len(times) * 1000,
            "min_duration_ms": min(times) * 1000,
            "max_duration_ms": max(times) * 1000,
            "recent_calls": len(times),
            "last_reset": self.last_reset.isoformat()
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all operations"""
        return {
            op: self.get_stats(op)
            for op in self.operation_times.keys()
        }
    
    def reset(self):
        """Reset all metrics"""
        self.operation_times.clear()
        self.operation_counts.clear()
        self.error_counts.clear()
        self.last_reset = datetime.utcnow()

# Global performance tracker
perf_tracker = PerformanceTracker()

class MetricsResponse(BaseModel):
    """Response model for metrics data"""
    timestamp: datetime
    system_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    world_state_metrics: Dict[str, Any]

async def get_world_state_service() -> WorldStateService:
    """Get world state service for metrics"""
    return await create_world_state_service()

def measure_performance(operation_name: str):
    """Decorator to measure operation performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise e
            finally:
                duration = time.time() - start_time
                perf_tracker.record_operation(operation_name, duration, success)
        return wrapper
    return decorator

@router.get("/health")
async def detailed_health_check():
    """Comprehensive health check with detailed metrics"""
    try:
        service = await get_world_state_service()
        
        # Test basic operations
        start_time = time.time()
        status = await service.get_system_status()
        response_time = time.time() - start_time
        
        # System resource metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_data = {
            "status": "healthy" if status.get("initialized") else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": response_time * 1000,
            "world_state": {
                "initialized": status.get("initialized", False),
                "total_regions": status.get("total_regions", 0),
                "total_state_variables": status.get("total_state_variables", 0),
                "total_active_effects": status.get("total_active_effects", 0),
                "summarization_enabled": status.get("summarization_enabled", False)
            },
            "system_resources": {
                "memory_usage_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_usage_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3)
            },
            "performance": perf_tracker.get_all_stats()
        }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/performance")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": perf_tracker.get_all_stats(),
        "summary": {
            "total_operations": len(perf_tracker.operation_times),
            "total_calls": sum(perf_tracker.operation_counts.values()),
            "total_errors": sum(perf_tracker.error_counts.values()),
            "last_reset": perf_tracker.last_reset.isoformat()
        }
    }

@router.get("/performance/{operation}")
async def get_operation_metrics(operation: str):
    """Get metrics for a specific operation"""
    stats = perf_tracker.get_stats(operation)
    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])
    return stats

@router.post("/performance/reset")
async def reset_performance_metrics():
    """Reset all performance metrics"""
    perf_tracker.reset()
    return {
        "message": "Performance metrics reset",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/system")
async def get_system_metrics():
    """Get system resource metrics"""
    try:
        # CPU and memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Process metrics
        process = psutil.Process()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count()
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent": disk.percent
            },
            "process": {
                "memory_mb": process.memory_info().rss / (1024**2),
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")

@router.get("/world-state")
@measure_performance("get_world_state_metrics")
async def get_world_state_metrics():
    """Get world state specific metrics"""
    try:
        service = await get_world_state_service()
        status = await service.get_system_status()
        
        # Calculate additional metrics
        regions_count = status.get("total_regions", 0)
        state_vars_count = status.get("total_state_variables", 0)
        effects_count = status.get("total_active_effects", 0)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "world_state": {
                "initialized": status.get("initialized", False),
                "current_time": status.get("current_time"),
                "game_day": status.get("game_day", 0),
                "season": status.get("season"),
                "year": status.get("year", 0)
            },
            "data_counts": {
                "regions": regions_count,
                "state_variables": state_vars_count,
                "active_effects": effects_count,
                "change_history": status.get("change_history_count", 0)
            },
            "summarization": {
                "enabled": status.get("summarization_enabled", False),
                "last_summarization": status.get("last_summarization", {})
            },
            "repository": status.get("repository_info", {}),
            "density_metrics": {
                "avg_state_vars_per_region": state_vars_count / max(regions_count, 1),
                "avg_effects_per_region": effects_count / max(regions_count, 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get world state metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get world state metrics: {str(e)}")

@router.get("/trends")
async def get_trend_analysis(
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze")
):
    """Get trend analysis for the specified time period"""
    try:
        # This is a simplified implementation
        # In production, you'd store historical metrics in a time series database
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Mock trend data - replace with actual historical data collection
        trend_data = {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            },
            "trends": {
                "state_changes_per_hour": [
                    {"hour": i, "count": 50 + (i % 10) * 5}
                    for i in range(hours)
                ],
                "average_response_time_ms": [
                    {"hour": i, "avg_ms": 150 + (i % 20) * 2}
                    for i in range(hours)
                ],
                "error_rate_percent": [
                    {"hour": i, "rate": 0.1 + (i % 5) * 0.02}
                    for i in range(hours)
                ]
            },
            "summary": {
                "total_state_changes": hours * 55,  # Mock data
                "avg_response_time_ms": 160,
                "peak_activity_hour": 14,
                "overall_error_rate": 0.15
            }
        }
        
        return trend_data
        
    except Exception as e:
        logger.error(f"Failed to get trend analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trend analysis: {str(e)}")

@router.get("/alerts")
async def get_system_alerts():
    """Get system alerts and warnings"""
    try:
        alerts = []
        
        # Check system resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        if memory.percent > 85:
            alerts.append({
                "type": "WARNING",
                "category": "MEMORY",
                "message": f"High memory usage: {memory.percent:.1f}%",
                "threshold": 85,
                "current": memory.percent,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if disk.percent > 90:
            alerts.append({
                "type": "CRITICAL",
                "category": "DISK",
                "message": f"Low disk space: {disk.percent:.1f}% used",
                "threshold": 90,
                "current": disk.percent,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Check performance metrics
        all_stats = perf_tracker.get_all_stats()
        for operation, stats in all_stats.items():
            if isinstance(stats, dict) and stats.get("error_rate", 0) > 0.1:
                alerts.append({
                    "type": "WARNING",
                    "category": "PERFORMANCE",
                    "message": f"High error rate for {operation}: {stats['error_rate']:.2%}",
                    "threshold": 0.1,
                    "current": stats["error_rate"],
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Check world state service
        try:
            service = await get_world_state_service()
            status = await service.get_system_status()
            
            if not status.get("initialized", False):
                alerts.append({
                    "type": "CRITICAL",
                    "category": "WORLD_STATE",
                    "message": "World state service not initialized",
                    "timestamp": datetime.utcnow().isoformat()
                })
        except Exception:
            alerts.append({
                "type": "CRITICAL",
                "category": "WORLD_STATE",
                "message": "World state service unavailable",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "alert_count": len(alerts),
            "alerts": alerts,
            "status": "OK" if not alerts else "WARNINGS" if not any(a["type"] == "CRITICAL" for a in alerts) else "CRITICAL"
        }
        
    except Exception as e:
        logger.error(f"Failed to get system alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system alerts: {str(e)}")

# Export the performance tracker for use by other modules
__all__ = ["router", "perf_tracker", "measure_performance"] 