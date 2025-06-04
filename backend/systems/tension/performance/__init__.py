"""
Tension System Performance Optimizations

Provides performance optimization utilities including:
- Intelligent caching strategies
- Database query optimization
- Batch processing for events
- Connection pooling
- Query result caching

This module follows the performance patterns established in the NPC system
and equipment system for consistency.
"""

from .cache_manager import TensionCacheManager
from .query_optimizer import TensionQueryOptimizer
from .batch_processor import TensionBatchProcessor
from .performance_monitor import TensionPerformanceMonitor

__all__ = [
    'TensionCacheManager',
    'TensionQueryOptimizer', 
    'TensionBatchProcessor',
    'TensionPerformanceMonitor'
] 