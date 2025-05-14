"""
Code analysis and monitoring schemas for request/response validation and Swagger documentation.
"""

from marshmallow import Schema, fields, validate
from typing import Dict, Any

class CacheStatsSchema(Schema):
    """Schema for cache statistics."""
    hit_rate = fields.Float(metadata={
        "description": "Cache hit rate percentage",
        "example": 85.5
    })
    miss_rate = fields.Float(metadata={
        "description": "Cache miss rate percentage",
        "example": 14.5
    })
    total_requests = fields.Int(metadata={
        "description": "Total number of cache requests",
        "example": 1000
    })

class RouteStatsSchema(Schema):
    """Schema for route performance statistics."""
    count = fields.Int(metadata={
        "description": "Number of requests to this route",
        "example": 500
    })
    avg_time = fields.Float(metadata={
        "description": "Average response time in seconds",
        "example": 0.125
    })
    min_time = fields.Float(metadata={
        "description": "Minimum response time in seconds",
        "example": 0.050
    })
    max_time = fields.Float(metadata={
        "description": "Maximum response time in seconds",
        "example": 0.500
    })
    p95_time = fields.Float(metadata={
        "description": "95th percentile response time in seconds",
        "example": 0.300
    })

class DatabaseStatsSchema(Schema):
    """Schema for database performance statistics."""
    query_count = fields.Int(metadata={
        "description": "Total number of queries executed",
        "example": 10000
    })
    avg_query_time = fields.Float(metadata={
        "description": "Average query execution time in seconds",
        "example": 0.050
    })
    slow_queries = fields.Int(metadata={
        "description": "Number of slow queries (>1s)",
        "example": 5
    })

class ConnectionPoolStatsSchema(Schema):
    """Schema for database connection pool statistics."""
    total_connections = fields.Int(metadata={
        "description": "Total number of connections in the pool",
        "example": 20
    })
    active_connections = fields.Int(metadata={
        "description": "Number of currently active connections",
        "example": 15
    })
    idle_connections = fields.Int(metadata={
        "description": "Number of idle connections",
        "example": 5
    })
    max_connections = fields.Int(metadata={
        "description": "Maximum number of connections allowed",
        "example": 50
    })

class SecurityIssueSchema(Schema):
    """Schema for security issues."""
    id = fields.Str(metadata={
        "description": "Unique identifier for the issue",
        "example": "code-123"
    })
    severity = fields.Str(validate=validate.OneOf(['low', 'medium', 'high', 'critical']), metadata={
        "description": "Severity level of the issue",
        "example": "medium"
    })
    category = fields.Str(metadata={
        "description": "Category of the security issue",
        "example": "code"
    })
    description = fields.Str(metadata={
        "description": "Description of the issue",
        "example": "Potential SQL injection vulnerability detected"
    })
    location = fields.Str(metadata={
        "description": "Location where the issue was found",
        "example": "app/core/models/user.py:123"
    })
    timestamp = fields.DateTime(metadata={
        "description": "When the issue was detected",
        "example": "2024-03-15T12:34:56Z"
    })
    status = fields.Str(validate=validate.OneOf(['open', 'fixed', 'ignored']), metadata={
        "description": "Current status of the issue",
        "example": "open"
    })
    details = fields.Dict(metadata={
        "description": "Additional details about the issue",
        "example": {"output": "Detailed scanner output"}
    })

class CodeQualityMetricsSchema(Schema):
    """Schema for code quality metrics."""
    complexity = fields.Float(metadata={
        "description": "Average cyclomatic complexity",
        "example": 5.2
    })
    maintainability = fields.Float(metadata={
        "description": "Maintainability index (0-100)",
        "example": 85.5
    })
    test_coverage = fields.Float(metadata={
        "description": "Test coverage percentage",
        "example": 78.3
    })
    documentation_coverage = fields.Float(metadata={
        "description": "Documentation coverage percentage",
        "example": 92.1
    })
    code_smells = fields.Int(metadata={
        "description": "Number of code smells detected",
        "example": 15
    })
    duplicate_code = fields.Float(metadata={
        "description": "Percentage of duplicate code",
        "example": 3.5
    })

class PerformanceMetricsSchema(Schema):
    """Schema for overall performance metrics."""
    routes = fields.Dict(fields.Nested(RouteStatsSchema), metadata={
        "description": "Performance statistics for each route"
    })
    cache = fields.Nested(CacheStatsSchema, metadata={
        "description": "Cache performance statistics"
    })
    database = fields.Nested(DatabaseStatsSchema, metadata={
        "description": "Database performance statistics"
    })
    connection_pool = fields.Nested(ConnectionPoolStatsSchema, metadata={
        "description": "Connection pool statistics"
    })

class ErrorResponseSchema(Schema):
    """Schema for error responses."""
    error = fields.Str(required=True, metadata={
        "description": "Error message",
        "example": "Performance monitoring not enabled"
    }) 