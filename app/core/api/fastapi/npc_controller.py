"""NPC controller implementation.

This module provides the API controller for NPC entities, implementing standard CRUD
operations and NPC-specific endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Path, Query, HTTPException
from pydantic import BaseModel

from .base_controller import BaseController
from ...middleware.rate_limit import RateLimiter
from ...middleware.cache import APICache
from ...services.npc import NPCService
from ....search.entities import NPCModel
from ..patterns import BaseResponse, PaginatedResponse

class NPCUpdateLocationRequest(BaseModel):
    """Request model for updating NPC location."""
    location_id: str
    reason: str

class NPCUpdateFactionRequest(BaseModel):
    """Request model for updating NPC faction."""
    faction_id: str
    reason: str

class NPCController(BaseController[NPCModel]):
    """Controller for NPC-related endpoints."""
    
    def __init__(
        self,
        service: NPCService,
        router: APIRouter,
        rate_limiter: RateLimiter,
        cache: APICache
    ):
        """Initialize the NPC controller."""
        super().__init__(service, router, "npc", rate_limiter, cache)
        self._register_npc_routes()
        
    def _register_npc_routes(self) -> None:
        """Register NPC-specific routes."""
        # Update location endpoint
        self.router.add_api_route(
            "/npcs/{id}/location",
            self.update_location,
            methods=["PUT"],
            response_model=BaseResponse[NPCModel],
            summary="Update NPC location",
            description="Move an NPC to a new location"
        )
        
        # Update faction endpoint
        self.router.add_api_route(
            "/npcs/{id}/faction",
            self.update_faction,
            methods=["PUT"],
            response_model=BaseResponse[NPCModel],
            summary="Update NPC faction",
            description="Change an NPC's faction allegiance"
        )
        
        # Get NPCs by location endpoint
        self.router.add_api_route(
            "/npcs/by-location/{location_id}",
            self.get_by_location,
            methods=["GET"],
            response_model=PaginatedResponse[NPCModel],
            summary="Get NPCs by location",
            description="Get all NPCs at a specific location"
        )
        
        # Get NPCs by faction endpoint
        self.router.add_api_route(
            "/npcs/by-faction/{faction_id}",
            self.get_by_faction,
            methods=["GET"],
            response_model=PaginatedResponse[NPCModel],
            summary="Get NPCs by faction",
            description="Get all NPCs belonging to a specific faction"
        )
        
    async def update_location(
        self,
        id: str = Path(..., description="The ID of the NPC"),
        request: NPCUpdateLocationRequest = None
    ) -> BaseResponse[NPCModel]:
        """Update an NPC's location."""
        try:
            npc = await self.service.update_location(id, request.location_id, request.reason)
            if not npc:
                raise HTTPException(status_code=404, detail="NPC not found")
            return BaseResponse[NPCModel](
                data=npc,
                message="NPC location updated successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def update_faction(
        self,
        id: str = Path(..., description="The ID of the NPC"),
        request: NPCUpdateFactionRequest = None
    ) -> BaseResponse[NPCModel]:
        """Update an NPC's faction."""
        try:
            npc = await self.service.update_faction(id, request.faction_id, request.reason)
            if not npc:
                raise HTTPException(status_code=404, detail="NPC not found")
            return BaseResponse[NPCModel](
                data=npc,
                message="NPC faction updated successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_location(
        self,
        location_id: str = Path(..., description="The ID of the location"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[NPCModel]:
        """Get all NPCs at a specific location."""
        try:
            npcs, total = await self.service.get_by_location(location_id, page, per_page)
            return PaginatedResponse[NPCModel](
                data=npcs,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_faction(
        self,
        faction_id: str = Path(..., description="The ID of the faction"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[NPCModel]:
        """Get all NPCs belonging to a specific faction."""
        try:
            npcs, total = await self.service.get_by_faction(faction_id, page, per_page)
            return PaginatedResponse[NPCModel](
                data=npcs,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 