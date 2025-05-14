"""
RESTful API endpoint design patterns for game systems.

This module defines standardized patterns for API endpoints across the game system,
ensuring consistency in URL structure, request/response formats, and error handling.
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Generic type for data models
T = TypeVar('T')

class PaginationParams(BaseModel):
    """Standard pagination parameters."""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    
class FilterParams(BaseModel):
    """Standard filtering parameters."""
    search: Optional[str] = Field(None, description="Search term")
    status: Optional[str] = Field(None, description="Status filter")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")

class SortParams(BaseModel):
    """Standard sorting parameters."""
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Sort order")

class BaseResponse(BaseModel, Generic[T]):
    """Standard API response format."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field("Operation successful", description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    meta: Optional[Dict[str, Any]] = Field(None, description="Metadata")

class PaginatedResponse(BaseResponse[List[T]]):
    """Standard paginated response format."""
    meta: Dict[str, Any] = Field(
        default_factory=lambda: {
            "page": 1,
            "per_page": 20,
            "total_pages": 1,
            "total_items": 0
        },
        description="Pagination metadata"
    )

class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = Field(False, description="Operation success status")
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")

# URL Pattern Constants
URL_PATTERNS = {
    # Entity patterns (NPC, Item, Location, Quest, Faction)
    'list': '/api/v1/{entity}s',  # GET, POST
    'detail': '/api/v1/{entity}s/{id}',  # GET, PUT, DELETE
    'batch': '/api/v1/{entity}s/batch',  # POST, PUT, DELETE
    'search': '/api/v1/{entity}s/search',  # GET
    
    # Relationship patterns
    'relationships': '/api/v1/{entity}s/{id}/relationships/{related_entity}s',  # GET, POST, DELETE
    'nested': '/api/v1/{entity}s/{id}/{related_entity}s',  # GET, POST
    
    # Version control patterns
    'versions': '/api/v1/{entity}s/{id}/versions',  # GET, POST
    'version_detail': '/api/v1/{entity}s/{id}/versions/{version_id}',  # GET
    
    # Action patterns
    'actions': '/api/v1/{entity}s/{id}/actions/{action_name}',  # POST
    'batch_actions': '/api/v1/{entity}s/actions/{action_name}',  # POST
}

# Standard HTTP Methods and Their Usage
HTTP_METHODS = {
    'GET': {
        'list': 'Retrieve a list of entities with pagination, filtering, and sorting',
        'detail': 'Retrieve a single entity by ID',
        'search': 'Search entities with advanced query parameters',
        'relationships': 'List related entities',
        'versions': 'List entity versions',
    },
    'POST': {
        'list': 'Create a new entity',
        'batch': 'Create multiple entities',
        'relationships': 'Add relationships between entities',
        'versions': 'Create a new version',
        'actions': 'Perform custom actions on entities',
    },
    'PUT': {
        'detail': 'Update an existing entity',
        'batch': 'Update multiple entities',
    },
    'DELETE': {
        'detail': 'Delete a single entity',
        'batch': 'Delete multiple entities',
        'relationships': 'Remove relationships between entities',
    }
}

# Standard Query Parameters
QUERY_PARAMS = {
    'list': {
        'page': 'Page number for pagination',
        'per_page': 'Number of items per page',
        'sort_by': 'Field to sort by',
        'order': 'Sort order (asc/desc)',
        'search': 'Search term',
        'status': 'Filter by status',
        'created_after': 'Filter by creation date',
        'created_before': 'Filter by creation date',
        'tags': 'Filter by tags',
        'include': 'Include related resources',
    },
    'search': {
        'q': 'Search query string',
        'fields': 'Fields to search in',
        'type': 'Entity type filter',
        'category': 'Category filter',
        'location': 'Location filter',
        'faction': 'Faction filter',
        'min_level': 'Minimum level filter',
        'max_level': 'Maximum level filter',
    }
}

# Standard Response Status Codes
STATUS_CODES = {
    200: 'OK - Request successful',
    201: 'Created - Resource created successfully',
    204: 'No Content - Request successful, no content to return',
    400: 'Bad Request - Invalid parameters or request format',
    401: 'Unauthorized - Authentication required',
    403: 'Forbidden - Insufficient permissions',
    404: 'Not Found - Resource not found',
    409: 'Conflict - Resource state conflict',
    422: 'Unprocessable Entity - Validation error',
    429: 'Too Many Requests - Rate limit exceeded',
    500: 'Internal Server Error - Server error occurred',
}

# Rate Limiting Configuration
RATE_LIMITS = {
    'default': {
        'requests': 100,
        'period': 3600,  # 1 hour
    },
    'search': {
        'requests': 30,
        'period': 60,  # 1 minute
    },
    'batch': {
        'requests': 10,
        'period': 3600,  # 1 hour
    }
}

# Cache Configuration
CACHE_CONFIG = {
    'list': 300,  # 5 minutes
    'detail': 600,  # 10 minutes
    'search': 60,  # 1 minute
    'relationships': 300,  # 5 minutes
    'versions': 3600,  # 1 hour
}

def get_endpoint_pattern(entity: str, pattern_type: str) -> str:
    """Get the endpoint URL pattern for a specific entity and pattern type."""
    return URL_PATTERNS[pattern_type].format(entity=entity)

def get_rate_limit(endpoint_type: str) -> Dict[str, int]:
    """Get rate limit configuration for a specific endpoint type."""
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS['default'])

def get_cache_timeout(endpoint_type: str) -> int:
    """Get cache timeout for a specific endpoint type."""
    return CACHE_CONFIG.get(endpoint_type, CACHE_CONFIG['list']) 