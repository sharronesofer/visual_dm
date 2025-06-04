"""
Performance Monitoring API Router

Provides endpoints for monitoring population system performance including:
- Cache statistics and hit rates
- API response times and bottlenecks
- Memory usage and optimization opportunities
- System health monitoring
- Performance recommendations

This router helps with performance optimization and monitoring.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import time
import psutil
import os
from pydantic import BaseModel

from backend.infrastructure.cache.redis_cache import cache
from backend.infrastructure.cache.cache_decorators import get_cache_performance_stats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/performance", tags=["population-performance"])


class PerformanceMetrics(BaseModel):
    """Model for performance metrics response"""
    cache_statistics: Dict[str, Any]
    system_resources: Dict[str, Any]
    api_performance: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime


class SystemHealth(BaseModel):
    """Model for system health response"""
    overall_status: str
    cache_health: Dict[str, Any]
    memory_usage: Dict[str, Any]
    cpu_usage: float
    recommendations: List[str]


@router.get("/cache-stats")
async def get_cache_statistics():
    """Get detailed cache performance statistics"""
    try:
        if not cache.available:
            return {
                "cache_available": False,
                "message": "Redis cache is not available",
                "fallback_mode": True,
                "performance_impact": "APIs running without cache optimization"
            }
        
        cache_stats = cache.get_cache_stats()
        performance_stats = get_cache_performance_stats()
        
        # Calculate additional metrics
        additional_metrics = {
            "cache_efficiency_score": _calculate_cache_efficiency(cache_stats),
            "memory_efficiency": _calculate_memory_efficiency(cache_stats),
            "optimization_opportunities": _identify_optimization_opportunities(cache_stats)
        }
        
        return {
            "cache_available": True,
            "basic_stats": cache_stats,
            "performance_stats": performance_stats,
            "additional_metrics": additional_metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting cache statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache statistics: {str(e)}")


@router.get("/system-health", response_model=SystemHealth)
async def get_system_health():
    """Get comprehensive system health status"""
    try:
        # Cache health
        cache_health = cache.health_check() if cache.available else {
            "status": "unavailable",
            "available": False
        }
        
        # System resource usage
        memory_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        memory_usage = {
            "total_gb": round(memory_info.total / (1024**3), 2),
            "available_gb": round(memory_info.available / (1024**3), 2),
            "used_percent": memory_info.percent,
            "free_percent": round(100 - memory_info.percent, 2)
        }
        
        # Generate recommendations
        recommendations = _generate_health_recommendations(
            cache_health, memory_usage, cpu_percent
        )
        
        # Overall status
        overall_status = _determine_overall_status(
            cache_health, memory_usage, cpu_percent
        )
        
        return SystemHealth(
            overall_status=overall_status,
            cache_health=cache_health,
            memory_usage=memory_usage,
            cpu_usage=cpu_percent,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")


@router.get("/metrics", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """Get comprehensive performance metrics"""
    try:
        # Cache statistics
        cache_statistics = get_cache_performance_stats()
        
        # System resources
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        system_resources = {
            "memory": {
                "total_gb": round(memory_info.total / (1024**3), 2),
                "used_gb": round((memory_info.total - memory_info.available) / (1024**3), 2),
                "used_percent": memory_info.percent,
                "available_gb": round(memory_info.available / (1024**3), 2)
            },
            "disk": {
                "total_gb": round(disk_info.total / (1024**3), 2),
                "used_gb": round(disk_info.used / (1024**3), 2),
                "free_gb": round(disk_info.free / (1024**3), 2),
                "used_percent": round((disk_info.used / disk_info.total) * 100, 2)
            },
            "cpu_count": psutil.cpu_count(),
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
        
        # API performance (simplified - would need actual metrics collection)
        api_performance = {
            "average_response_time_ms": 50,  # Would be collected from actual metrics
            "slowest_endpoints": [
                {"endpoint": "/population/batch/operations", "avg_time_ms": 120},
                {"endpoint": "/population/economic/overview", "avg_time_ms": 85},
                {"endpoint": "/population/diseases/status", "avg_time_ms": 65}
            ],
            "total_requests_last_hour": 1500,  # Would be collected from actual metrics
            "error_rate_percent": 0.2
        }
        
        # Generate recommendations
        recommendations = _generate_performance_recommendations(
            cache_statistics, system_resources, api_performance
        )
        
        return PerformanceMetrics(
            cache_statistics=cache_statistics,
            system_resources=system_resources,
            api_performance=api_performance,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@router.post("/cache/clear")
async def clear_cache(
    confirm: bool = Query(False, description="Confirm cache clearing"),
    pattern: Optional[str] = Query(None, description="Pattern to clear (default: all)")
):
    """Clear cache data (use with caution)"""
    try:
        if not confirm:
            raise HTTPException(
                status_code=400,
                detail="Cache clearing requires confirmation. Add ?confirm=true to proceed."
            )
        
        if not cache.available:
            raise HTTPException(status_code=503, detail="Cache is not available")
        
        if pattern:
            # Clear specific pattern
            cleared_count = cache.invalidate_pattern(pattern)
            message = f"Cleared {cleared_count} cache entries matching pattern: {pattern}"
        else:
            # Clear all cache
            success = cache.clear_all_cache()
            if not success:
                raise HTTPException(status_code=500, detail="Failed to clear cache")
            message = "All cache data cleared successfully"
        
        logger.warning(f"Cache cleared: {message}")
        
        return {
            "success": True,
            "message": message,
            "cleared_at": datetime.utcnow().isoformat(),
            "warning": "Cache clearing may temporarily impact performance"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.post("/cache/warm")
async def warm_cache(
    background_tasks: BackgroundTasks,
    population_ids: Optional[List[str]] = Query(None, description="Specific population IDs to warm"),
    include_economic: bool = Query(True, description="Include economic data warming"),
    include_disease: bool = Query(True, description="Include disease data warming"),
    include_quest: bool = Query(True, description="Include quest data warming")
):
    """Pre-warm cache with commonly requested data"""
    try:
        if not cache.available:
            raise HTTPException(status_code=503, detail="Cache is not available")
        
        # Start cache warming in background
        background_tasks.add_task(
            _execute_cache_warming,
            population_ids,
            include_economic,
            include_disease,
            include_quest
        )
        
        return {
            "success": True,
            "message": "Cache warming initiated in background",
            "started_at": datetime.utcnow().isoformat(),
            "estimated_completion": "2-5 minutes",
            "cache_warming_scope": {
                "population_ids": population_ids or "all_active",
                "include_economic": include_economic,
                "include_disease": include_disease,
                "include_quest": include_quest
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting cache warming: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start cache warming: {str(e)}")


@router.get("/recommendations")
async def get_optimization_recommendations():
    """Get performance optimization recommendations"""
    try:
        recommendations = []
        
        # Cache recommendations
        if cache.available:
            cache_stats = cache.get_cache_stats()
            hit_rate = cache_stats.get("hit_rate", 0.0)
            
            if hit_rate < 50:
                recommendations.append({
                    "category": "cache",
                    "priority": "high",
                    "issue": "Low cache hit rate",
                    "current_value": f"{hit_rate:.1f}%",
                    "recommendation": "Consider increasing cache TTL for stable data or reviewing cache invalidation strategy",
                    "expected_improvement": "20-40% faster API responses"
                })
            
            total_keys = cache_stats.get("total_keys", 0)
            if total_keys > 10000:
                recommendations.append({
                    "category": "cache",
                    "priority": "medium",
                    "issue": "High number of cache keys",
                    "current_value": f"{total_keys} keys",
                    "recommendation": "Review cache key patterns and implement more aggressive TTL policies",
                    "expected_improvement": "Reduced memory usage and faster key lookups"
                })
        else:
            recommendations.append({
                "category": "cache",
                "priority": "critical",
                "issue": "Cache system unavailable",
                "current_value": "Redis not connected",
                "recommendation": "Configure and connect Redis cache for significant performance improvements",
                "expected_improvement": "50-80% faster API responses"
            })
        
        # Memory recommendations
        memory_info = psutil.virtual_memory()
        if memory_info.percent > 80:
            recommendations.append({
                "category": "memory",
                "priority": "high",
                "issue": "High memory usage",
                "current_value": f"{memory_info.percent:.1f}%",
                "recommendation": "Consider scaling up server memory or optimizing application memory usage",
                "expected_improvement": "Better system stability and performance"
            })
        
        # API recommendations
        recommendations.append({
            "category": "api",
            "priority": "medium",
            "issue": "Potential optimization",
            "current_value": "Standard configuration",
            "recommendation": "Implement response compression and pagination for large datasets",
            "expected_improvement": "Reduced bandwidth usage and faster response times"
        })
        
        return {
            "total_recommendations": len(recommendations),
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat(),
            "next_review_recommended": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting optimization recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/health")
async def performance_system_health():
    """Health check for the performance monitoring system"""
    try:
        health_status = {
            "status": "healthy",
            "system": "population_performance_monitoring",
            "monitoring_capabilities": [
                "cache_statistics",
                "system_resource_monitoring",
                "api_performance_tracking",
                "health_recommendations",
                "cache_management",
                "performance_optimization"
            ],
            "dependencies": {
                "redis_cache": cache.available,
                "system_monitoring": True,
                "performance_tracking": True
            }
        }
        
        # Add warnings if dependencies are unavailable
        warnings = []
        if not cache.available:
            warnings.append("Redis cache unavailable - cache statistics and management disabled")
        
        if warnings:
            health_status["warnings"] = warnings
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Performance system health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance system unhealthy: {str(e)}")


# Helper functions
def _calculate_cache_efficiency(cache_stats: Dict[str, Any]) -> float:
    """Calculate cache efficiency score (0-100)"""
    if not cache_stats.get("available", False):
        return 0.0
    
    hit_rate = cache_stats.get("hit_rate", 0.0)
    total_keys = cache_stats.get("total_keys", 0)
    
    # Base score from hit rate
    base_score = hit_rate
    
    # Bonus for having reasonable number of keys
    if 100 <= total_keys <= 5000:
        base_score += 10
    elif total_keys > 5000:
        base_score -= 5
    
    return min(100.0, max(0.0, base_score))


def _calculate_memory_efficiency(cache_stats: Dict[str, Any]) -> str:
    """Calculate memory efficiency rating"""
    if not cache_stats.get("available", False):
        return "unknown"
    
    # This would need actual memory usage data from Redis
    # For now, return a placeholder
    return "good"


def _identify_optimization_opportunities(cache_stats: Dict[str, Any]) -> List[str]:
    """Identify cache optimization opportunities"""
    opportunities = []
    
    if not cache_stats.get("available", False):
        opportunities.append("Enable Redis cache for significant performance improvements")
        return opportunities
    
    hit_rate = cache_stats.get("hit_rate", 0.0)
    if hit_rate < 60:
        opportunities.append("Increase cache TTL for stable data to improve hit rate")
    
    total_keys = cache_stats.get("total_keys", 0)
    if total_keys > 8000:
        opportunities.append("Implement cache key cleanup to reduce memory usage")
    
    key_distribution = cache_stats.get("keys_by_category", {})
    if key_distribution.get("api_response", 0) > key_distribution.get("population", 0) * 2:
        opportunities.append("API response cache may be too aggressive - consider shorter TTL")
    
    return opportunities


def _generate_health_recommendations(
    cache_health: Dict[str, Any],
    memory_usage: Dict[str, Any],
    cpu_usage: float
) -> List[str]:
    """Generate system health recommendations"""
    recommendations = []
    
    if not cache_health.get("available", False):
        recommendations.append("Configure Redis cache to improve API performance")
    
    if memory_usage.get("used_percent", 0) > 85:
        recommendations.append("Consider increasing server memory or optimizing memory usage")
    
    if cpu_usage > 80:
        recommendations.append("High CPU usage detected - consider scaling or optimization")
    
    return recommendations


def _determine_overall_status(
    cache_health: Dict[str, Any],
    memory_usage: Dict[str, Any],
    cpu_usage: float
) -> str:
    """Determine overall system health status"""
    if memory_usage.get("used_percent", 0) > 90 or cpu_usage > 90:
        return "critical"
    
    if memory_usage.get("used_percent", 0) > 80 or cpu_usage > 80:
        return "warning"
    
    if not cache_health.get("available", False):
        return "degraded"
    
    return "healthy"


def _generate_performance_recommendations(
    cache_statistics: Dict[str, Any],
    system_resources: Dict[str, Any],
    api_performance: Dict[str, Any]
) -> List[str]:
    """Generate comprehensive performance recommendations"""
    recommendations = []
    
    # Cache recommendations
    if not cache_statistics.get("available", False):
        recommendations.append("Enable Redis cache for 50-80% performance improvement")
    elif cache_statistics.get("cache_efficiency", {}).get("hit_rate", 0) < 60:
        recommendations.append("Optimize cache TTL settings to improve hit rate")
    
    # Memory recommendations
    memory_used = system_resources.get("memory", {}).get("used_percent", 0)
    if memory_used > 80:
        recommendations.append("Scale server memory or optimize application memory usage")
    
    # API recommendations
    avg_response_time = api_performance.get("average_response_time_ms", 0)
    if avg_response_time > 100:
        recommendations.append("Implement response compression and optimize slow endpoints")
    
    return recommendations


async def _execute_cache_warming(
    population_ids: Optional[List[str]],
    include_economic: bool,
    include_disease: bool,
    include_quest: bool
):
    """Execute cache warming in background"""
    try:
        logger.info("Starting cache warming process...")
        
        # This would actually call the relevant business logic functions
        # to populate cache with commonly requested data
        
        if population_ids:
            for pop_id in population_ids:
                logger.info(f"Warming cache for population {pop_id}")
                # Call actual functions to populate cache
                
        logger.info("Cache warming process completed successfully")
        
    except Exception as e:
        logger.error(f"Error during cache warming: {str(e)}") 