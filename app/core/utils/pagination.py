"""
Pagination utility for API endpoints.
Provides consistent pagination handling across the application.
"""

from typing import TypeVar, Generic, List, Dict, Any, Optional
from sqlalchemy.orm import Query
from flask import request, url_for
from math import ceil

T = TypeVar('T')

class PaginatedResponse(Generic[T]):
    """
    Generic paginated response wrapper that includes metadata about the pagination.
    """
    def __init__(
        self,
        items: List[T],
        total: int,
        page: int,
        per_page: int,
        endpoint: str,
        **kwargs
    ):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.total_pages = ceil(total / per_page) if per_page > 0 else 0
        self.has_next = page < self.total_pages
        self.has_prev = page > 1
        self.endpoint = endpoint
        self.kwargs = kwargs

    def get_metadata(self) -> Dict[str, Any]:
        """Get pagination metadata including navigation links."""
        metadata = {
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev
        }

        # Add navigation links
        links = {}
        if self.has_prev:
            links["prev"] = url_for(
                self.endpoint,
                page=self.page - 1,
                per_page=self.per_page,
                _external=True,
                **self.kwargs
            )
        if self.has_next:
            links["next"] = url_for(
                self.endpoint,
                page=self.page + 1,
                per_page=self.per_page,
                _external=True,
                **self.kwargs
            )
        
        metadata["links"] = links
        return metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert paginated response to dictionary format."""
        return {
            "items": self.items,
            "metadata": self.get_metadata()
        }

class Paginator:
    """
    Utility class for handling pagination in SQLAlchemy queries.
    """
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 25
    MAX_PER_PAGE = 100

    @staticmethod
    def get_page_params() -> tuple[int, int]:
        """Get page and per_page parameters from request."""
        try:
            page = int(request.args.get('page', Paginator.DEFAULT_PAGE))
            per_page = min(
                int(request.args.get('per_page', Paginator.DEFAULT_PER_PAGE)),
                Paginator.MAX_PER_PAGE
            )
            return max(page, 1), max(per_page, 1)
        except (TypeError, ValueError):
            return Paginator.DEFAULT_PAGE, Paginator.DEFAULT_PER_PAGE

    @staticmethod
    def paginate(
        query: Query,
        endpoint: str,
        schema: Any = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        Paginate a SQLAlchemy query and return a PaginatedResponse.
        
        Args:
            query: The SQLAlchemy query to paginate
            endpoint: The endpoint name for generating navigation links
            schema: Optional Marshmallow schema for serializing items
            **kwargs: Additional arguments to pass to url_for()
        
        Returns:
            PaginatedResponse containing the paginated items and metadata
        """
        page, per_page = Paginator.get_page_params()
        
        # Get total count efficiently
        total = query.count()
        
        # Apply pagination to query
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Serialize items if schema provided
        if schema:
            items = schema.dump(items, many=True)
            
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            endpoint=endpoint,
            **kwargs
        ) 