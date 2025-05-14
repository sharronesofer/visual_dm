"""Location controller implementation.

This module provides the API controller for Location entities, implementing standard CRUD
operations and location-specific endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Path, Query, HTTPException
from pydantic import BaseModel

from .base_controller import BaseController
from ...middleware.rate_limit import RateLimiter
from ...middleware.cache import APICache
from ...services.location import LocationService
from ....search.entities import LocationModel, NPCModel, ItemModel
from ..patterns import BaseResponse, PaginatedResponse

class LocationUpdateStatusRequest(BaseModel):
    """Request model for updating location status."""
    status: str  # e.g., 'open', 'closed', 'restricted'
    reason: str

class LocationController(BaseController[LocationModel]):
    """Controller for Location-related endpoints."""
    
    def __init__(
        self,
        service: LocationService,
        router: APIRouter,
        rate_limiter: RateLimiter,
        cache: APICache
    ):
        """Initialize the Location controller."""
        super().__init__(service, router, "location", rate_limiter, cache)
        self._register_location_routes()
        
    def _register_location_routes(self) -> None:
        """Register Location-specific routes."""
        # Update status endpoint
        self.router.add_api_route(
            "/locations/{id}/status",
            self.update_status,
            methods=["PUT"],
            response_model=BaseResponse[LocationModel],
            summary="Update location status",
            description="Update a location's status (open, closed, restricted)"
        )
        
        # Get connected locations endpoint
        self.router.add_api_route(
            "/locations/{id}/connected",
            self.get_connected_locations,
            methods=["GET"],
            response_model=PaginatedResponse[LocationModel],
            summary="Get connected locations",
            description="Get all locations connected to this one"
        )
        
        # Get location contents endpoint
        self.router.add_api_route(
            "/locations/{id}/contents",
            self.get_location_contents,
            methods=["GET"],
            response_model=BaseResponse[Dict[str, Any]],
            summary="Get location contents",
            description="Get all NPCs and items at this location"
        )
        
        # Get locations by region endpoint
        self.router.add_api_route(
            "/locations/by-region/{region}",
            self.get_by_region,
            methods=["GET"],
            response_model=PaginatedResponse[LocationModel],
            summary="Get locations by region",
            description="Get all locations in a specific region"
        )
        
        # Get locations by type endpoint
        self.router.add_api_route(
            "/locations/by-type/{location_type}",
            self.get_by_type,
            methods=["GET"],
            response_model=PaginatedResponse[LocationModel],
            summary="Get locations by type",
            description="Get all locations of a specific type"
        )
        
    async def update_status(
        self,
        id: str = Path(..., description="The ID of the location"),
        request: LocationUpdateStatusRequest = None
    ) -> BaseResponse[LocationModel]:
        """Update a location's status."""
        try:
            location = await self.service.update_status(id, request.status, request.reason)
            if not location:
                raise HTTPException(status_code=404, detail="Location not found")
            return BaseResponse[LocationModel](
                data=location,
                message="Location status updated successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_connected_locations(
        self,
        id: str = Path(..., description="The ID of the location"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[LocationModel]:
        """Get all locations connected to this one."""
        try:
            locations, total = await self.service.get_connected_locations(id, page, per_page)
            return PaginatedResponse[LocationModel](
                data=locations,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_location_contents(
        self,
        id: str = Path(..., description="The ID of the location")
    ) -> BaseResponse[Dict[str, Any]]:
        """Get all NPCs and items at this location."""
        try:
            npcs, items = await self.service.get_location_contents(id)
            return BaseResponse[Dict[str, Any]](
                data={
                    "npcs": npcs,
                    "items": items
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_region(
        self,
        region: str = Path(..., description="The region to get locations from"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[LocationModel]:
        """Get all locations in a specific region."""
        try:
            locations, total = await self.service.get_by_region(region, page, per_page)
            return PaginatedResponse[LocationModel](
                data=locations,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_type(
        self,
        location_type: str = Path(..., description="The type of locations to get"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[LocationModel]:
        """Get all locations of a specific type."""
        try:
            locations, total = await self.service.get_by_type(location_type, page, per_page)
            return PaginatedResponse[LocationModel](
                data=locations,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 