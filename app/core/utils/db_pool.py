"""
Database connection pool management utilities.
Provides optimized connection pooling with monitoring and health checks.
"""

from typing import Optional, Dict, Any
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import time
import logging
from contextlib import contextmanager
from flask import current_app
from app.core.database import db
import threading

logger = logging.getLogger(__name__)

class ConnectionPoolManager:
    """Manages database connection pooling with monitoring and health checks."""
    
    def __init__(self, app=None):
        """Initialize the connection pool manager."""
        self.app = app
        self.pool_metrics: Dict[str, Any] = {
            'total_connections': 0,
            'active_connections': 0,
            'idle_connections': 0,
            'connection_timeouts': 0,
            'connection_errors': 0,
            'avg_checkout_time': 0.0,
            'total_checkouts': 0,
            'failed_checkouts': 0,
            'connection_resets': 0,
            'peak_connections': 0,
            'total_wait_time': 0.0,
            'avg_wait_time': 0.0
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask application."""
        self.app = app
        
        # Get database configuration with optimized defaults
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        pool_size = app.config.get('SQLALCHEMY_POOL_SIZE', 10)  # Increased default pool size
        max_overflow = app.config.get('SQLALCHEMY_MAX_OVERFLOW', 20)  # Increased max overflow
        pool_timeout = app.config.get('SQLALCHEMY_POOL_TIMEOUT', 30)
        pool_recycle = app.config.get('SQLALCHEMY_POOL_RECYCLE', 1800)  # Reduced to 30 minutes
        pool_pre_ping = app.config.get('SQLALCHEMY_POOL_PRE_PING', True)  # Enable connection testing
        
        # Create engine with optimized pool settings
        engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
            echo_pool=app.config.get('SQLALCHEMY_ECHO_POOL', False),
            connect_args={
                'connect_timeout': 10,  # 10 second connection timeout
                'keepalives': 1,        # Enable TCP keepalive
                'keepalives_idle': 30,  # Idle time before sending keepalive
                'keepalives_interval': 10,  # Interval between keepalives
                'keepalives_count': 5   # Number of keepalive retries
            }
        )
        
        # Set up event listeners for monitoring
        self._setup_engine_events(engine)
        
        # Replace SQLAlchemy engine
        db.get_engine = lambda *args, **kwargs: engine
    
    def _setup_engine_events(self, engine: Engine):
        """Set up SQLAlchemy engine event listeners for monitoring."""
        
        @event.listens_for(engine, 'checkout')
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Track connection checkout time and validate connection."""
            connection_record.info['checkout_time'] = time.time()
            connection_record.info['checkout_thread'] = threading.get_ident()
            
            # Update peak connections metric
            current_active = self.pool_metrics['active_connections']
            self.pool_metrics['peak_connections'] = max(
                current_active + 1,
                self.pool_metrics['peak_connections']
            )
            
            # Validate connection is still alive
            try:
                cursor = dbapi_connection.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
            except Exception as e:
                self.pool_metrics['connection_errors'] += 1
                self.pool_metrics['failed_checkouts'] += 1
                logger.error(f"Connection validation failed: {str(e)}")
                
                # Invalidate connection and retry
                connection_record.invalidate()
                raise SQLAlchemyError("Connection validation failed - retrying")
        
        @event.listens_for(engine, 'checkin')
        def receive_checkin(dbapi_connection, connection_record):
            """Track connection usage metrics on checkin."""
            checkout_time = connection_record.info.get('checkout_time')
            if checkout_time:
                usage_time = time.time() - checkout_time
                self.pool_metrics['total_checkouts'] += 1
                self.pool_metrics['avg_checkout_time'] = (
                    (self.pool_metrics['avg_checkout_time'] * (self.pool_metrics['total_checkouts'] - 1) + usage_time) /
                    self.pool_metrics['total_checkouts']
                )
                
                # Track wait time if connection was queued
                if 'queue_start' in connection_record.info:
                    wait_time = connection_record.info['checkout_time'] - connection_record.info['queue_start']
                    self.pool_metrics['total_wait_time'] += wait_time
                    self.pool_metrics['avg_wait_time'] = (
                        self.pool_metrics['total_wait_time'] / self.pool_metrics['total_checkouts']
                    )
        
        @event.listens_for(engine, 'connect')
        def receive_connect(dbapi_connection, connection_record):
            """Track total connections and set up connection-level settings."""
            self.pool_metrics['total_connections'] += 1
            
            # Set session-level settings for better performance
            cursor = dbapi_connection.cursor()
            cursor.execute("SET SESSION statement_timeout = '30s'")  # 30 second query timeout
            cursor.execute("SET SESSION idle_in_transaction_session_timeout = '60s'")  # 1 minute idle timeout
            cursor.close()
        
        @event.listens_for(engine, 'reset')
        def receive_reset(dbapi_connection, connection_record):
            """Handle connection resets with validation."""
            self.pool_metrics['connection_resets'] += 1
            try:
                # Verify connection is still valid
                cursor = dbapi_connection.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
            except Exception:
                # If validation fails, don't return connection to pool
                self.pool_metrics['connection_errors'] += 1
                connection_record.invalidate()
        
        @event.listens_for(engine, 'invalidate')
        def receive_invalidate(dbapi_connection, connection_record):
            """Track connection invalidations."""
            self.pool_metrics['connection_errors'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current connection pool metrics."""
        if not self.app:
            return self.pool_metrics
            
        engine = db.get_engine(self.app)
        pool = engine.pool
        
        # Update real-time metrics
        self.pool_metrics.update({
            'active_connections': pool.checkedout(),
            'idle_connections': pool.size() - pool.checkedout(),
            'total_size': pool.size() + pool.overflow()
        })
        
        return self.pool_metrics
    
    @contextmanager
    def monitored_session(self):
        """Context manager for monitored database sessions with automatic retry."""
        session_start = time.time()
        retry_count = 0
        max_retries = 3
        
        while True:
            try:
                yield db.session
                duration = time.time() - session_start
                logger.debug(f"Database session completed in {duration:.3f}s")
                break
                
            except SQLAlchemyError as e:
                retry_count += 1
                duration = time.time() - session_start
                
                if retry_count >= max_retries:
                    logger.error(f"Database session failed after {duration:.3f}s and {retry_count} retries: {str(e)}")
                    raise
                
                logger.warning(f"Database error on attempt {retry_count}, retrying: {str(e)}")
                time.sleep(0.1 * retry_count)  # Exponential backoff
                continue
                
            finally:
                db.session.close()

# Initialize connection pool manager
pool_manager = ConnectionPoolManager()

def init_db_pool(app):
    """Initialize database connection pool for the application."""
    pool_manager.init_app(app) 