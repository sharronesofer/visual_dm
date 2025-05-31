"""
Database utility functions.
Provides optimized database operations with caching and error handling.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging
from datetime import datetime, timedelta
from functools import wraps
from backend.infrastructure.database import get_db
from backend.infrastructure.shared.utils.cache import RedisCache
from backend.infrastructure.shared.utils.monitoring import monitor
from backend.infrastructure.shared.utils.db_pool import pool_manager
import json
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Provides database optimization utilities."""
    
    def __init__(self, app=None):
        self.app = app
        self.cache = RedisCache()
        self._query_stats = defaultdict(lambda: {
            'count': 0,
            'cache_hits': 0,
            'avg_time': 0.0
        })
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask application."""
        self.app = app
        self.cache_enabled = app.config.get('DB_CACHE_ENABLED', True)
        self.cache_timeout = app.config.get('DB_CACHE_TIMEOUT', 300)  # 5 minutes default
        self.bulk_size = app.config.get('DB_BULK_INSERT_SIZE', 1000)
    
    def cached_query(self, timeout: Optional[int] = None):
        """Decorator for caching database queries."""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if not self.cache_enabled:
                    return f(*args, **kwargs)
                
                # Generate cache key
                key = f"{f.__name__}:{hash(str(args))}-{hash(str(kwargs))}"
                result = self.cache.get(key)
                
                if result is not None:
                    self._query_stats[f.__name__]['cache_hits'] += 1
                    return json.loads(result)
                
                result = f(*args, **kwargs)
                if result is not None:
                    self.cache.set(
                        key,
                        json.dumps(result),
                        timeout or self.cache_timeout
                    )
                
                return result
            return wrapper
        return decorator
    
    def bulk_insert(self, model: Any, items: List[Dict[str, Any]]) -> None:
        """Efficiently insert multiple items in batches."""
        session = next(get_db())
        try:
            for i in range(0, len(items), self.bulk_size):
                batch = items[i:i + self.bulk_size]
                session.bulk_insert_mappings(model, batch)
                session.flush()
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Bulk insert failed: {str(e)}")
            raise
    
    def bulk_update(self, model: Any, items: List[Dict[str, Any]], key_field: str) -> None:
        """Efficiently update multiple items in batches."""
        session = next(get_db())
        try:
            for i in range(0, len(items), self.bulk_size):
                batch = items[i:i + self.bulk_size]
                session.bulk_update_mappings(model, batch)
                session.flush()
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Bulk update failed: {str(e)}")
            raise
    
    def execute_with_retry(self, query: Union[str, text], params: Optional[Dict[str, Any]] = None,
                          max_retries: int = 3, initial_delay: float = 0.1) -> Any:
        """Execute a query with automatic retry on failure."""
        last_error = None
        delay = initial_delay
        
        for attempt in range(max_retries):
            try:
                with pool_manager.monitored_session() as session:
                    if isinstance(query, str):
                        query = text(query)
                    result = session.execute(query, params)
                    return result
                    
            except SQLAlchemyError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Query failed on attempt {attempt + 1}, retrying in {delay:.1f}s: {str(e)}"
                    )
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                continue
                
        logger.error(f"Query failed after {max_retries} attempts: {str(last_error)}")
        raise last_error
    
    def analyze_table(self, table_name: str) -> Dict[str, Any]:
        """Analyze a database table and suggest optimizations."""
        try:
            with pool_manager.monitored_session() as session:
                # Get basic table statistics
                stats = session.execute(text(f"""
                    SELECT 
                        (SELECT reltuples::bigint FROM pg_class WHERE relname = :table) as row_count,
                        pg_size_pretty(pg_total_relation_size(:table)) as total_size,
                        pg_size_pretty(pg_table_size(:table)) as table_size,
                        pg_size_pretty(pg_indexes_size(:table)) as index_size
                """), {'table': table_name}).fetchone()
                
                # Get index information
                indexes = session.execute(text(f"""
                    SELECT
                        indexname,
                        indexdef
                    FROM pg_indexes
                    WHERE tablename = :table
                """), {'table': table_name}).fetchall()
                
                # Get column statistics
                columns = session.execute(text(f"""
                    SELECT
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_name = :table
                """), {'table': table_name}).fetchall()
                
                # Analyze table
                session.execute(f"ANALYZE {table_name}")
                
                return {
                    'statistics': {
                        'row_count': stats[0],
                        'total_size': stats[1],
                        'table_size': stats[2],
                        'index_size': stats[3]
                    },
                    'indexes': [{'name': idx[0], 'definition': idx[1]} for idx in indexes],
                    'columns': [
                        {
                            'name': col[0],
                            'type': col[1],
                            'nullable': col[2],
                            'default': col[3]
                        }
                        for col in columns
                    ]
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to analyze table {table_name}: {str(e)}")
            raise
    
    def optimize_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[str, List[str]]:
        """Analyze and optimize a SQL query."""
        try:
            with pool_manager.monitored_session() as session:
                # Get query plan
                plan = session.execute(
                    text(f"EXPLAIN ANALYZE {query}"),
                    params
                ).fetchall()
                
                plan_text = '\n'.join(row[0] for row in plan)
                suggestions = []
                
                # Analyze execution plan
                if 'Seq Scan' in plan_text:
                    suggestions.append(
                        "Consider adding an index to avoid sequential scans"
                    )
                
                if 'Hash Join' in plan_text and 'Parallel' not in plan_text:
                    suggestions.append(
                        "Query might benefit from parallel execution"
                    )
                
                if 'Materialize' in plan_text:
                    suggestions.append(
                        "Consider adding indexes to avoid materialization"
                    )
                
                # Suggest query improvements
                if 'GROUP BY' in query and 'WHERE' not in query:
                    suggestions.append(
                        "Consider adding WHERE clause before GROUP BY for better performance"
                    )
                
                if 'DISTINCT' in query and 'ORDER BY' in query:
                    suggestions.append(
                        "DISTINCT with ORDER BY can be slow. Consider using GROUP BY"
                    )
                
                return query, suggestions
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to optimize query: {str(e)}")
            raise
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get database optimization statistics."""
        stats = {
            'query_stats': dict(self._query_stats),
            'cache_stats': None,
            'pool_stats': None,
            'slow_queries': None
        }
        # Cache stats (robust)
        try:
            if hasattr(self.cache, 'get_stats'):
                stats['cache_stats'] = self.cache.get_stats()
        except Exception as e:
            stats['cache_stats'] = {'error': str(e)}
        # Pool stats (robust)
        try:
            stats['pool_stats'] = pool_manager.get_metrics()
        except Exception as e:
            stats['pool_stats'] = {'error': str(e)}
        # Slow queries (robust)
        try:
            stats['slow_queries'] = monitor.get_query_stats()
        except Exception as e:
            stats['slow_queries'] = {'error': str(e)}
        return stats
    
    def get_query_cache_stats(self) -> Dict[str, Any]:
        """Return query cache hit/miss rates and average query times."""
        stats = {}
        for name, data in self._query_stats.items():
            count = data['count']
            hits = data['cache_hits']
            avg_time = data['avg_time']
            stats[name] = {
                'calls': count,
                'cache_hits': hits,
                'cache_hit_rate': hits / count if count else 0,
                'avg_time': avg_time
            }
        return stats
    
    def get_slow_queries(self) -> list:
        """Return details of slow queries for performance analysis."""
        try:
            stats = monitor.get_query_stats()
            return stats.get('slow_queries', []) if isinstance(stats, dict) else stats
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_table_stats(self, table_name: str) -> dict:
        """Return statistics for a specific table (row count, size, indexes)."""
        try:
            return self.analyze_table(table_name)
        except Exception as e:
            return {'error': str(e)}
    
    def get_index_usage(self, table_name: str) -> list:
        """Return index usage statistics for a specific table."""
        try:
            stats = self.analyze_table(table_name)
            return stats.get('indexes', []) if isinstance(stats, dict) else stats
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_query_optimization_suggestions(self, query: str, params: Optional[dict] = None) -> list:
        """Return optimization suggestions for a given query."""
        try:
            _, suggestions = self.optimize_query(query, params)
            return suggestions
        except Exception as e:
            return [str(e)]

# Initialize database optimizer
optimizer = DatabaseOptimizer() 