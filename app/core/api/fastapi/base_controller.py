"""Base controller class for FastAPI endpoints.

This module provides a base controller class that implements common CRUD operations
and shared functionality for all entity types.
"""

from typing import Generic, TypeVar, List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from pydantic import BaseModel

from ..patterns import (
    PaginationParams,
    FilterParams,
    SortParams,
    BaseResponse,
    PaginatedResponse,
    ErrorResponse
)
from ...middleware.rate_limit import RateLimiter
from ...middleware.cache import APICache
from ...services.base import BaseService

T = TypeVar('T', bound=BaseModel)

class BaseController(Generic[T]):
    """Base controller implementing common CRUD operations."""
    
    def __init__(
        self,
        service: BaseService[T],
        router: APIRouter,
        entity_name: str,
        rate_limiter: RateLimiter,
        cache: APICache
    ):
        """Initialize the controller.
        
        Args:
            service: Service instance for entity operations
            router: FastAPI router instance
            entity_name: Name of the entity type
            rate_limiter: Rate limiter instance
            cache: Cache instance
        """
        self.service = service
        self.router = router
        self.entity_name = entity_name
        self.rate_limiter = rate_limiter
        self.cache = cache
        
        # Register routes
        self._register_routes()
        
    def _register_routes(self) -> None:
        """Register all routes for the entity."""
        # List endpoint
        self.router.add_api_route(
            f"/{self.entity_name}s",
            self.get_all,
            methods=["GET"],
            response_model=PaginatedResponse[T],
            summary=f"Get all {self.entity_name}s",
            description=f"Get a paginated list of {self.entity_name}s with optional filtering and sorting"
        )
        
        # Create endpoint
        self.router.add_api_route(
            f"/{self.entity_name}s",
            self.create,
            methods=["POST"],
            response_model=BaseResponse[T],
            summary=f"Create a new {self.entity_name}",
            description=f"Create a new {self.entity_name} with the provided data"
        )
        
        # Get by ID endpoint
        self.router.add_api_route(
            f"/{self.entity_name}s/{{id}}",
            self.get_by_id,
            methods=["GET"],
            response_model=BaseResponse[T],
            summary=f"Get a {self.entity_name} by ID",
            description=f"Get detailed information about a specific {self.entity_name}"
        )
        
        # Update endpoint
        self.router.add_api_route(
            f"/{self.entity_name}s/{{id}}",
            self.update,
            methods=["PUT"],
            response_model=BaseResponse[T],
            summary=f"Update a {self.entity_name}",
            description=f"Update an existing {self.entity_name} with new data"
        )
        
        # Delete endpoint
        self.router.add_api_route(
            f"/{self.entity_name}s/{{id}}",
            self.delete,
            methods=["DELETE"],
            response_model=BaseResponse[Dict[str, Any]],
            summary=f"Delete a {self.entity_name}",
            description=f"Delete an existing {self.entity_name} by ID"
        )
        
        # Search endpoint
        self.router.add_api_route(
            f"/{self.entity_name}s/search",
            self.search,
            methods=["GET"],
            response_model=PaginatedResponse[T],
            summary=f"Search {self.entity_name}s",
            description=f"Search for {self.entity_name}s using advanced query parameters"
        )
        
    async def get_all(
        self,
        pagination: PaginationParams = Depends(),
        filters: FilterParams = Depends(),
        sort: SortParams = Depends()
    ) -> PaginatedResponse[T]:
        """Get a paginated list of entities."""
        try:
            items, total = await self.service.get_all(
                page=pagination.page,
                per_page=pagination.per_page,
                filters=filters.dict(exclude_none=True),
                sort_by=sort.sort_by,
                order=sort.order
            )
            
            return PaginatedResponse[T](
                data=items,
                meta={
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total_items": total,
                    "total_pages": (total + pagination.per_page - 1) // pagination.per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_id(self, id: str = Path(..., description=f"The ID of the {self.entity_name}")) -> BaseResponse[T]:
        """Get an entity by ID."""
        try:
            item = await self.service.get_by_id(id)
            if not item:
                raise HTTPException(status_code=404, detail=f"{self.entity_name} not found")
            return BaseResponse[T](data=item)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def create(self, item: T) -> BaseResponse[T]:
        """Create a new entity."""
        try:
            created_item = await self.service.create(item)
            return BaseResponse[T](
                data=created_item,
                message=f"{self.entity_name} created successfully"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def update(
        self,
        id: str = Path(..., description=f"The ID of the {self.entity_name}"),
        item: T = None
    ) -> BaseResponse[T]:
        """Update an existing entity."""
        try:
            updated_item = await self.service.update(id, item)
            if not updated_item:
                raise HTTPException(status_code=404, detail=f"{self.entity_name} not found")
            return BaseResponse[T](
                data=updated_item,
                message=f"{self.entity_name} updated successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def delete(self, id: str = Path(..., description=f"The ID of the {self.entity_name}")) -> BaseResponse[Dict[str, Any]]:
        """Delete an entity."""
        try:
            success = await self.service.delete(id)
            if not success:
                raise HTTPException(status_code=404, detail=f"{self.entity_name} not found")
            return BaseResponse[Dict[str, Any]](
                data={"id": id},
                message=f"{self.entity_name} deleted successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def search(
        self,
        q: str = Query(None, description="Search query string"),
        fields: List[str] = Query(None, description="Fields to search in"),
        pagination: PaginationParams = Depends(),
        filters: FilterParams = Depends(),
        sort: SortParams = Depends()
    ) -> PaginatedResponse[T]:
        """Search for entities."""
        try:
            items, total = await self.service.search(
                query=q,
                fields=fields,
                page=pagination.page,
                per_page=pagination.per_page,
                filters=filters.dict(exclude_none=True),
                sort_by=sort.sort_by,
                order=sort.order
            )
            
            return PaginatedResponse[T](
                data=items,
                meta={
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total_items": total,
                    "total_pages": (total + pagination.per_page - 1) // pagination.per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 