from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
from collections import defaultdict
import threading
import json

from flask import request, g, current_app
from prometheus_client import Counter, Histogram, Gauge, generate_latest

@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    path: str
    method: str
    status_code: int
    duration: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
class MetricsCollector:
    """Collector for API metrics."""
    
    def __init__(self, app=None):
        self.app = app
        self._metrics_lock = threading.Lock()
        self._initialize_metrics()
        
        if app is not None:
            self.init_app(app)
            
    def _initialize_metrics(self):
        """Initialize Prometheus metrics."""
        # Request count metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total number of HTTP requests',
            ['method', 'path', 'status']
        )
        
        # Request duration metrics
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'path'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        # Active requests gauge
        self.active_requests = Gauge(
            'http_requests_active',
            'Number of active HTTP requests',
            ['method']
        )
        
        # Error count metrics
        self.error_count = Counter(
            'http_errors_total',
            'Total number of HTTP errors',
            ['method', 'path', 'error_type']
        )
        
        # Response size metrics
        self.response_size = Histogram(
            'http_response_size_bytes',
            'HTTP response size in bytes',
            ['method', 'path'],
            buckets=[100, 1000, 10000, 100000, 1000000]
        )
        
        # Rate limiting metrics
        self.rate_limit_hits = Counter(
            'rate_limit_hits_total',
            'Total number of rate limit hits',
            ['method', 'path']
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total number of cache hits',
            ['path']
        )
        self.cache_misses = Counter(
            'cache_misses_total',
            'Total number of cache misses',
            ['path']
        )
        
        # Authentication metrics
        self.auth_failures = Counter(
            'auth_failures_total',
            'Total number of authentication failures',
            ['method', 'path', 'reason']
        )
        
        # Validation error metrics
        self.validation_errors = Counter(
            'validation_errors_total',
            'Total number of validation errors',
            ['method', 'path', 'field']
        )
        
    def init_app(self, app):
        """Initialize metrics collection for a Flask application."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
        
        # Add metrics endpoint
        @app.route('/metrics')
        def metrics():
            return generate_latest(), 200, {'Content-Type': 'text/plain'}
            
    def before_request(self):
        """Record metrics before processing request."""
        g.start_time = time.time()
        
        # Increment active requests
        self.active_requests.labels(
            method=request.method
        ).inc()
        
    def after_request(self, response):
        """Record metrics after processing request."""
        # Calculate request duration
        duration = time.time() - g.start_time
        
        # Update request count
        self.request_count.labels(
            method=request.method,
            path=request.path,
            status=response.status_code
        ).inc()
        
        # Update duration histogram
        self.request_duration.labels(
            method=request.method,
            path=request.path
        ).observe(duration)
        
        # Update response size histogram
        self.response_size.labels(
            method=request.method,
            path=request.path
        ).observe(len(response.get_data()))
        
        # Decrement active requests
        self.active_requests.labels(
            method=request.method
        ).dec()
        
        # Record cache metrics if available
        if hasattr(g, 'cache_hit'):
            if g.cache_hit:
                self.cache_hits.labels(path=request.path).inc()
            else:
                self.cache_misses.labels(path=request.path).inc()
                
        # Record rate limit metrics if available
        if hasattr(g, 'rate_limited') and g.rate_limited:
            self.rate_limit_hits.labels(
                method=request.method,
                path=request.path
            ).inc()
            
        return response
        
    def teardown_request(self, exception):
        """Record error metrics if an exception occurred."""
        if exception:
            # Update error count
            self.error_count.labels(
                method=request.method,
                path=request.path,
                error_type=type(exception).__name__
            ).inc()
            
            # Record authentication failures
            if hasattr(exception, 'status_code') and exception.status_code == 401:
                self.auth_failures.labels(
                    method=request.method,
                    path=request.path,
                    reason=str(exception)
                ).inc()
                
            # Record validation errors
            if hasattr(exception, 'status_code') and exception.status_code == 400:
                field = getattr(exception, 'field', 'unknown')
                self.validation_errors.labels(
                    method=request.method,
                    path=request.path,
                    field=field
                ).inc()
                
    def record_cache_metrics(self, hit: bool, path: str):
        """Record cache hit/miss metrics."""
        if hit:
            self.cache_hits.labels(path=path).inc()
        else:
            self.cache_misses.labels(path=path).inc()
            
    def record_rate_limit_hit(self, method: str, path: str):
        """Record a rate limit hit."""
        self.rate_limit_hits.labels(
            method=method,
            path=path
        ).inc()
        
    def record_auth_failure(self, method: str, path: str, reason: str):
        """Record an authentication failure."""
        self.auth_failures.labels(
            method=method,
            path=path,
            reason=reason
        ).inc()
        
    def record_validation_error(self, method: str, path: str, field: str):
        """Record a validation error."""
        self.validation_errors.labels(
            method=method,
            path=path,
            field=field
        ).inc() 