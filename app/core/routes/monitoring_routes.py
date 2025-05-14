"""
Monitoring and analytics routes.
"""

from flask import Blueprint, jsonify, render_template
from app.core.utils.monitoring import PerformanceMonitor
from app.core.utils.cache import RedisCache
from app.core.utils.http_cache import HTTPCache
from app.core.utils.cache_warmer import cache_warmer
from datetime import datetime, timedelta
import json

bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')

@bp.route('/cache-analytics')
def cache_analytics():
    """Get cache analytics data."""
    redis_cache = RedisCache()
    http_cache = HTTPCache()
    
    # Get Redis cache stats
    redis_stats = {
        'hit_count': redis_cache.get_hit_count(),
        'miss_count': redis_cache.get_miss_count(),
        'hit_rate': redis_cache.get_hit_rate(),
        'memory_usage': redis_cache.get_memory_usage(),
        'key_count': redis_cache.get_key_count(),
        'expired_keys': redis_cache.get_expired_keys(),
        'evicted_keys': redis_cache.get_evicted_keys()
    }
    
    # Get HTTP cache stats
    http_stats = {
        'etag_hits': http_cache.get_etag_hits(),
        'last_modified_hits': http_cache.get_last_modified_hits(),
        'total_requests': http_cache.get_total_requests(),
        'cached_responses': http_cache.get_cached_responses(),
        'compression_savings': http_cache.get_compression_savings()
    }
    
    # Get cache warmer stats
    warmer_stats = {
        'last_warm_cycle': cache_warmer.last_warm_time if hasattr(cache_warmer, 'last_warm_time') else None,
        'endpoints_warmed': len(cache_warmer.critical_endpoints),
        'warm_interval': cache_warmer.warm_interval.total_seconds() // 60,  # Convert to minutes
        'is_active': cache_warmer.warming_thread is not None and cache_warmer.warming_thread.is_alive()
    }
    
    # Get performance impact
    perf_monitor = PerformanceMonitor()
    performance_stats = {
        'avg_response_time': perf_monitor.get_avg_response_time(),
        'cache_impact': perf_monitor.get_cache_performance_impact(),
        'bandwidth_saved': perf_monitor.get_bandwidth_savings()
    }
    
    analytics_data = {
        'redis_stats': redis_stats,
        'http_stats': http_stats,
        'warmer_stats': warmer_stats,
        'performance_stats': performance_stats,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify(analytics_data)

@bp.route('/dashboard')
def dashboard():
    """Render the monitoring dashboard."""
    return render_template('monitoring/dashboard.html') 