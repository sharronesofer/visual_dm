"""
Pagination utilities for API responses.
"""

from typing import Any, Dict, Generic, List, Optional, Sequence, TypeVar, Union
from fastapi import Query
from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-based)"
    )
    per_page: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page"
    )
    
    @validator('page')
    def validate_page(cls, v: int) -> int:
        """Ensure page number is positive."""
        if v < 1:
            raise ValueError("Page number must be positive")
        return v
    
    @validator('per_page')
    def validate_per_page(cls, v: int) -> int:
        """Ensure items per page is within bounds."""
        if v < 1:
            raise ValueError("Items per page must be positive")
        if v > 100:
            raise ValueError("Items per page cannot exceed 100")
        return v

class PageInfo(BaseModel):
    """Information about the current page."""
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    next_page: Optional[int] = Field(None, description="Next page number if available")
    prev_page: Optional[int] = Field(None, description="Previous page number if available")

class Page(GenericModel, Generic[T]):
    """Generic paginated result."""
    items: List[T] = Field(..., description="Items in the current page")
    page_info: PageInfo = Field(..., description="Pagination information")

def paginate(
    items: Sequence[T],
    params: PaginationParams,
    total_items: Optional[int] = None
) -> Page[T]:
    """
    Create a paginated result from a sequence of items.
    
    Args:
        items: Sequence of items to paginate
        params: Pagination parameters
        total_items: Total number of items (if different from len(items))
        
    Returns:
        Paginated result with items and page information
    """
    total = total_items if total_items is not None else len(items)
    total_pages = (total + params.per_page - 1) // params.per_page
    
    # Adjust page number if out of bounds
    page = min(params.page, total_pages) if total_pages > 0 else 1
    
    # Calculate slice indices
    start = (page - 1) * params.per_page
    end = start + params.per_page
    
    # Get items for current page
    page_items = items[start:end]
    
    # Create page info
    page_info = PageInfo(
        page=page,
        per_page=params.per_page,
        total_items=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
        next_page=page + 1 if page < total_pages else None,
        prev_page=page - 1 if page > 1 else None
    )
    
    return Page(items=page_items, page_info=page_info)

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(20, ge=1, le=100, description="Number of items per page")
) -> PaginationParams:
    """
    FastAPI dependency for pagination parameters.
    
    Args:
        page: Page number (1-based)
        per_page: Number of items per page
        
    Returns:
        PaginationParams instance
    """
    return PaginationParams(page=page, per_page=per_page)

async def paginate_query(
    query: Any,
    params: PaginationParams,
    count_query: Optional[Any] = None
) -> Page[T]:
    """
    Create a paginated result from a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query to paginate
        params: Pagination parameters
        count_query: Optional separate query for counting total items
        
    Returns:
        Paginated result with items and page information
    """
    # Get total count
    total = await count_query.scalar() if count_query is not None else await query.count()
    
    # Apply pagination to query
    items = await query.offset((params.page - 1) * params.per_page).limit(params.per_page).all()
    
    return paginate(items, params, total) 