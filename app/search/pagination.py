"""Pagination models and utilities for search functionality.

This module provides standardized pagination support for search endpoints,
including both offset-based and cursor-based pagination, response models,
and link header generation.
"""

from typing import List, Generic, TypeVar, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from urllib.parse import urlencode
import base64
import json

T = TypeVar('T')

class OffsetPaginationParams(BaseModel):
    """Parameters for offset-based pagination.
    
    Attributes:
        page: Page number (1-based indexing)
        limit: Number of items per page
    """
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate the offset for database queries."""
        return (self.page - 1) * self.limit

class CursorPaginationParams(BaseModel):
    """Parameters for cursor-based pagination.
    
    Attributes:
        cursor: Opaque cursor for the next page
        limit: Number of items per page
    """
    cursor: Optional[str] = Field(default=None, description="Opaque cursor for pagination")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")

    @classmethod
    def encode_cursor(cls, sort_values: Dict[str, Any]) -> str:
        """Encode sort values into an opaque cursor.
        
        Args:
            sort_values: Dictionary of sort field values from the last item
            
        Returns:
            Base64 encoded cursor string
        """
        cursor_data = json.dumps(sort_values)
        return base64.b64encode(cursor_data.encode()).decode()

    @classmethod
    def decode_cursor(cls, cursor: str) -> Dict[str, Any]:
        """Decode an opaque cursor into sort values.
        
        Args:
            cursor: Base64 encoded cursor string
            
        Returns:
            Dictionary of sort field values
        """
        try:
            cursor_data = base64.b64decode(cursor.encode()).decode()
            return json.loads(cursor_data)
        except (ValueError, json.JSONDecodeError):
            raise ValueError("Invalid cursor format")

PaginationParams = Union[OffsetPaginationParams, CursorPaginationParams]

class PaginatedResponse(Generic[T], BaseModel):
    """Generic paginated response container.
    
    Attributes:
        items: List of items for the current page
        total: Total number of items across all pages
        limit: Items per page
        next_cursor: Cursor for the next page (cursor-based pagination)
        prev_cursor: Cursor for the previous page (cursor-based pagination)
        page: Current page number (offset-based pagination)
        total_pages: Total number of pages (offset-based pagination)
        has_next: Whether there is a next page
        has_prev: Whether there is a previous page
    """
    items: List[T]
    total: int
    limit: int
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    page: Optional[int] = None
    total_pages: Optional[int] = None
    has_next: bool
    has_prev: bool

    @classmethod
    def create_offset_based(cls, 
                          items: List[T], 
                          total: int, 
                          params: OffsetPaginationParams) -> 'PaginatedResponse[T]':
        """Create an offset-based paginated response.
        
        Args:
            items: List of items for the current page
            total: Total number of items across all pages
            params: Offset pagination parameters
            
        Returns:
            A configured PaginatedResponse instance
        """
        total_pages = (total + params.limit - 1) // params.limit
        return cls(
            items=items,
            total=total,
            limit=params.limit,
            page=params.page,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_prev=params.page > 1
        )

    @classmethod
    def create_cursor_based(cls,
                          items: List[T],
                          total: int,
                          params: CursorPaginationParams,
                          sort_fields: List[Dict[str, str]],
                          prev_cursor: Optional[str] = None) -> 'PaginatedResponse[T]':
        """Create a cursor-based paginated response.
        
        Args:
            items: List of items for the current page
            total: Total number of items across all pages
            params: Cursor pagination parameters
            sort_fields: List of sort fields used for cursor generation
            prev_cursor: Cursor for the previous page
            
        Returns:
            A configured PaginatedResponse instance
        """
        # Generate next cursor from last item if we have a full page
        next_cursor = None
        if len(items) == params.limit:
            last_item = items[-1]
            sort_values = {
                field["field"]: getattr(last_item, field["field"])
                for field in sort_fields
            }
            next_cursor = CursorPaginationParams.encode_cursor(sort_values)

        return cls(
            items=items,
            total=total,
            limit=params.limit,
            next_cursor=next_cursor,
            prev_cursor=prev_cursor,
            has_next=bool(next_cursor),
            has_prev=bool(prev_cursor)
        )

def generate_link_header(base_url: str, 
                        params: PaginationParams, 
                        response: PaginatedResponse) -> Optional[str]:
    """Generate a Link header for pagination navigation.
    
    Supports both offset-based and cursor-based pagination.
    Follows RFC 5988 standard for Web Linking.
    
    Args:
        base_url: Base URL for the endpoint
        params: Current pagination parameters
        response: Paginated response containing navigation info
        
    Returns:
        Formatted Link header string or None if not needed
    """
    links = []
    
    if isinstance(params, OffsetPaginationParams):
        # Offset-based pagination links
        if response.total_pages <= 1:
            return None
            
        # First page
        query = urlencode({'page': 1, 'limit': params.limit})
        links.append(f'<{base_url}?{query}>; rel="first"')
        
        # Previous page
        if response.has_prev:
            query = urlencode({'page': params.page - 1, 'limit': params.limit})
            links.append(f'<{base_url}?{query}>; rel="prev"')
        
        # Next page
        if response.has_next:
            query = urlencode({'page': params.page + 1, 'limit': params.limit})
            links.append(f'<{base_url}?{query}>; rel="next"')
        
        # Last page
        query = urlencode({'page': response.total_pages, 'limit': params.limit})
        links.append(f'<{base_url}?{query}>; rel="last"')
    
    else:
        # Cursor-based pagination links
        if response.prev_cursor:
            query = urlencode({'cursor': response.prev_cursor, 'limit': params.limit})
            links.append(f'<{base_url}?{query}>; rel="prev"')
        
        if response.next_cursor:
            query = urlencode({'cursor': response.next_cursor, 'limit': params.limit})
            links.append(f'<{base_url}?{query}>; rel="next"')
    
    return ', '.join(links) if links else None 