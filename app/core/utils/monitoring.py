"""
Performance monitoring utilities.
Provides tools for tracking and analyzing system performance metrics.
"""

from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
import time
import logging
from functools import wraps
from flask import request, current_app
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.core.database import db
from app.core.utils.cache import RedisCache
from app.core.utils.db_pool import ConnectionPoolManager
import json
import threading
from collections import defaultdict
import statistics
import re

logger = logging.getLogger(__name__)

class QueryAnalyzer:
    """Analyzes SQL queries for potential optimizations."""
    
    def __init__(self):
        """Initialize query analyzer."""
        self.query_patterns = {
            'missing_index': re.compile(r'seq scan.*on\s+(\w+)', re.I),
            'cartesian_join': re.compile(r'cross join', re.I),
            'full_table_scan': re.compile(r'full.*scan.*on\s+(\w+)', re.I),
            'implicit_conversion': re.compile(r'::(\w+)', re.I)
        }
        
    def analyze_query(self, query: str, execution_plan: Optional[str] = None) -> List[str]:
        """Analyze a query for potential optimizations."""
        suggestions = []
        
        # Check for basic query patterns
        if 'SELECT *' in query.upper():
            suggestions.append("Consider selecting specific columns instead of '*'")
            
        if 'DISTINCT' in query.upper() and 'GROUP BY' not in query.upper():
            suggestions.append("Consider using GROUP BY instead of DISTINCT where possible")
            
        if execution_plan:
            # Analyze execution plan
            if self.query_patterns['missing_index'].search(execution_plan):
                suggestions.append("Consider adding an index to improve query performance")
                
            if self.query_patterns['cartesian_join'].search(execution_plan):
                suggestions.append("Avoid cartesian joins - specify join conditions")
                
            if self.query_patterns['full_table_scan'].search(execution_plan):
                suggestions.append("Query requires full table scan - consider adding appropriate indexes")
                
            if self.query_patterns['implicit_conversion'].search(execution_plan):
                suggestions.append("Implicit type conversion detected - ensure column types match conditions")
        
        return suggestions

class PerformanceMonitor:
    """Monitors and tracks system performance metrics."""
    
    def __init__(self, app=None):
        """Initialize the performance monitor."""
        self.app = app
        self.metrics: Dict[str, Any] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'min_time': float('inf'),
            'max_time': 0,
            'times': [],
            'patterns': defaultdict(int)
        })
        self.slow_query_threshold = 1.0  # seconds
        self.cache_metrics: Dict[str, Any] = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0
        }
        self._lock = threading.Lock()
        self.query_analyzer = QueryAnalyzer()
        self.query_cache: Dict[str, Any] = {}
        self.slow_queries: List[Dict[str, Any]] = []
        self.query_patterns: Set[str] = set()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask application."""
        self.app = app
        self.slow_query_threshold = app.config.get('SLOW_QUERY_THRESHOLD', 1.0)
        
        # Set up SQLAlchemy query monitoring
        if app.config.get('ENABLE_QUERY_MONITORING', False):
            event.listen(db.engine, 'before_cursor_execute', self._before_cursor_execute)
            event.listen(db.engine, 'after_cursor_execute', self._after_cursor_execute)
            
            # Enable query execution plan capture if in development
            if app.config.get('FLASK_ENV') == 'development':
                event.listen(Engine, 'before_cursor_execute', self._capture_execution_plan)
    
    def _before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """Record query start time and analyze query."""
        context._query_start_time = time.time()
        
        # Store query for analysis
        query_key = self._get_query_key(statement)
        if query_key not in self.query_cache:
            self.query_cache[query_key] = {
                'count': 0,
                'total_time': 0.0,
                'parameters': set(),
                'suggestions': self.query_analyzer.analyze_query(statement)
            }
        
        self.query_cache[query_key]['count'] += 1
        if parameters:
            self.query_cache[query_key]['parameters'].add(str(parameters))
    
    def _after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """Record query execution time and update metrics."""
        duration = time.time() - context._query_start_time
        query_key = self._get_query_key(statement)
        
        # Update query cache
        self.query_cache[query_key]['total_time'] += duration
        
        # Track slow queries
        if duration > self.slow_query_threshold:
            self.slow_queries.append({
                'query': statement,
                'duration': duration,
                'timestamp': datetime.utcnow(),
                'parameters': parameters
            })
            
            # Log slow query
            logger.warning(
                f"Slow query detected ({duration:.2f}s): {statement[:100]}..."
                f"\nParameters: {parameters}"
            )
        
        # Update pattern detection
        self._update_query_patterns(statement)
    
    def _capture_execution_plan(self, conn, cursor, statement, parameters, context, executemany):
        """Capture query execution plan in development."""
        if statement.strip().upper().startswith('SELECT'):
            try:
                explain_cursor = conn.connection.cursor()
                explain_cursor.execute(f"EXPLAIN {statement}", parameters)
                execution_plan = '\n'.join(row[0] for row in explain_cursor.fetchall())
                explain_cursor.close()
                
                # Analyze execution plan
                suggestions = self.query_analyzer.analyze_query(statement, execution_plan)
                if suggestions:
                    logger.info(f"Query optimization suggestions for: {statement[:100]}...")
                    for suggestion in suggestions:
                        logger.info(f"- {suggestion}")
                
            except Exception as e:
                logger.warning(f"Failed to capture execution plan: {str(e)}")
    
    def _get_query_key(self, statement: str) -> str:
        """Generate normalized query key for caching."""
        # Remove literal values but keep the query structure
        normalized = re.sub(r"'[^']*'", "'?'", statement)
        normalized = re.sub(r"\d+", "?", normalized)
        return normalized.strip()
    
    def _update_query_patterns(self, statement: str):
        """Detect and store query patterns for analysis."""
        # Extract basic query pattern
        pattern = re.sub(r'(WHERE|AND)\s+\w+\s*[=<>]\s*[^AND\s]+', r'\1 ? ? ?', statement)
        pattern = re.sub(r'VALUES\s*\([^)]+\)', 'VALUES (?)', pattern)
        self.query_patterns.add(pattern)
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics."""
        stats = {
            'total_queries': sum(q['count'] for q in self.query_cache.values()),
            'unique_queries': len(self.query_cache),
            'slow_queries': len(self.slow_queries),
            'query_patterns': len(self.query_patterns),
            'top_queries': sorted(
                [
                    {
                        'query': k,
                        'count': v['count'],
                        'avg_time': v['total_time'] / v['count'],
                        'parameter_variations': len(v['parameters']),
                        'suggestions': v['suggestions']
                    }
                    for k, v in self.query_cache.items()
                ],
                key=lambda x: x['count'],
                reverse=True
            )[:10]
        }
        
        if self.slow_queries:
            stats['slow_query_analysis'] = {
                'avg_duration': statistics.mean(q['duration'] for q in self.slow_queries),
                'max_duration': max(q['duration'] for q in self.slow_queries),
                'common_patterns': self._analyze_slow_query_patterns()
            }
        
        return stats
    
    def _analyze_slow_query_patterns(self) -> List[Dict[str, Any]]:
        """Analyze patterns in slow queries."""
        pattern_counts = defaultdict(int)
        pattern_durations = defaultdict(list)
        
        for query in self.slow_queries:
            pattern = self._get_query_key(query['query'])
            pattern_counts[pattern] += 1
            pattern_durations[pattern].append(query['duration'])
        
        return [
            {
                'pattern': pattern,
                'count': count,
                'avg_duration': statistics.mean(pattern_durations[pattern]),
                'max_duration': max(pattern_durations[pattern])
            }
            for pattern, count in sorted(
                pattern_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ][:5]  # Top 5 patterns

    def track_cache_operation(self, hit: bool):
        """Track cache hit/miss metrics."""
        with self._lock:
            self.cache_metrics['total_requests'] += 1
            if hit:
                self.cache_metrics['hits'] += 1
            else:
                self.cache_metrics['misses'] += 1
    
    def track_request_time(self, route: str, response_time: float):
        """Track API request timing."""
        with self._lock:
            metrics = self.metrics[f'route:{route}']
            metrics['count'] += 1
            metrics['total_time'] += response_time
            metrics['min_time'] = min(metrics['min_time'], response_time)
            metrics['max_time'] = max(metrics['max_time'], response_time)
            metrics['times'].append(response_time)
    
    def get_route_stats(self, route: str) -> Dict[str, Any]:
        """Get statistics for a specific route."""
        with self._lock:
            metrics = self.metrics[f'route:{route}']
            if metrics['count'] == 0:
                return {
                    'count': 0,
                    'avg_time': 0,
                    'min_time': 0,
                    'max_time': 0,
                    'p95_time': 0
                }
            
            times = metrics['times']
            return {
                'count': metrics['count'],
                'avg_time': metrics['total_time'] / metrics['count'],
                'min_time': metrics['min_time'],
                'max_time': metrics['max_time'],
                'p95_time': statistics.quantiles(times, n=20)[18]  # 95th percentile
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        with self._lock:
            total = self.cache_metrics['total_requests']
            if total == 0:
                return {
                    'hit_rate': 0,
                    'miss_rate': 0,
                    'total_requests': 0
                }
            
            return {
                'hit_rate': self.cache_metrics['hits'] / total * 100,
                'miss_rate': self.cache_metrics['misses'] / total * 100,
                'total_requests': total
            }
    
    def get_db_stats(self) -> Dict[str, Any]:
        """Get database performance statistics."""
        with self._lock:
            metrics = self.metrics['database_queries']
            if metrics['count'] == 0:
                return {
                    'total_queries': 0,
                    'avg_query_time': 0,
                    'min_query_time': 0,
                    'max_query_time': 0,
                    'p95_query_time': 0
                }
            
            times = metrics['times']
            return {
                'total_queries': metrics['count'],
                'avg_query_time': metrics['total_time'] / metrics['count'],
                'min_query_time': metrics['min_time'],
                'max_query_time': metrics['max_time'],
                'p95_query_time': statistics.quantiles(times, n=20)[18]  # 95th percentile
            }
    
    def reset_metrics(self):
        """Reset all performance metrics."""
        with self._lock:
            self.metrics.clear()
            self.cache_metrics = {
                'hits': 0,
                'misses': 0,
                'total_requests': 0
            }

def track_performance(f):
    """Decorator to track route performance."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        
        monitor = current_app.extensions.get('performance_monitor')
        if monitor:
            monitor.track_request_time(
                request.endpoint,
                end_time - start_time
            )
        
        return result
    return wrapper 