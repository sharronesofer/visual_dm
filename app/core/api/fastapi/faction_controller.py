"""Faction controller implementation.

This module provides the API controller for Faction entities, implementing standard CRUD
operations and faction-specific endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Path, Query, HTTPException
from pydantic import BaseModel

from .base_controller import BaseController
from ...middleware.rate_limit import RateLimiter
from ...middleware.cache import APICache
from ...services.faction import FactionService
from ....search.entities import FactionModel, NPCModel
from ..patterns import BaseResponse, PaginatedResponse

class FactionRelationshipRequest(BaseModel):
    """Request model for updating faction relationships."""
    target_faction_id: str
    relationship_type: str  # e.g., 'allied', 'neutral', 'hostile'
    relationship_value: int  # -100 to 100
    reason: str

class FactionMembershipRequest(BaseModel):
    """Request model for managing faction membership."""
    npc_id: str
    role: str  # e.g., 'leader', 'member', 'recruit'
    rank: int  # Numerical rank within the faction
    notes: str = None

class FactionController(BaseController[FactionModel]):
    """Controller for Faction-related endpoints."""
    
    def __init__(
        self,
        service: FactionService,
        router: APIRouter,
        rate_limiter: RateLimiter,
        cache: APICache
    ):
        """Initialize the Faction controller."""
        super().__init__(service, router, "faction", rate_limiter, cache)
        self._register_faction_routes()
        
    def _register_faction_routes(self) -> None:
        """Register Faction-specific routes."""
        # Update relationship endpoint
        self.router.add_api_route(
            "/factions/{id}/relationships/{target_id}",
            self.update_relationship,
            methods=["PUT"],
            response_model=BaseResponse[FactionModel],
            summary="Update faction relationship",
            description="Update the relationship between two factions"
        )
        
        # Add member endpoint
        self.router.add_api_route(
            "/factions/{id}/members",
            self.add_member,
            methods=["POST"],
            response_model=BaseResponse[FactionModel],
            summary="Add faction member",
            description="Add a new member to the faction"
        )
        
        # Remove member endpoint
        self.router.add_api_route(
            "/factions/{id}/members/{npc_id}",
            self.remove_member,
            methods=["DELETE"],
            response_model=BaseResponse[FactionModel],
            summary="Remove faction member",
            description="Remove a member from the faction"
        )
        
        # Get members endpoint
        self.router.add_api_route(
            "/factions/{id}/members",
            self.get_members,
            methods=["GET"],
            response_model=PaginatedResponse[NPCModel],
            summary="Get faction members",
            description="Get all members of the faction"
        )
        
        # Get relationships endpoint
        self.router.add_api_route(
            "/factions/{id}/relationships",
            self.get_relationships,
            methods=["GET"],
            response_model=BaseResponse[Dict[str, Any]],
            summary="Get faction relationships",
            description="Get all relationships with other factions"
        )
        
        # Get factions by influence endpoint
        self.router.add_api_route(
            "/factions/by-influence",
            self.get_by_influence,
            methods=["GET"],
            response_model=PaginatedResponse[FactionModel],
            summary="Get factions by influence",
            description="Get factions sorted by their influence score"
        )
        
    async def update_relationship(
        self,
        id: str = Path(..., description="The ID of the faction"),
        target_id: str = Path(..., description="The ID of the target faction"),
        request: FactionRelationshipRequest = None
    ) -> BaseResponse[FactionModel]:
        """Update the relationship between two factions."""
        try:
            faction = await self.service.update_relationship(
                id,
                target_id,
                request.relationship_type,
                request.relationship_value,
                request.reason
            )
            if not faction:
                raise HTTPException(status_code=404, detail="Faction not found")
            return BaseResponse[FactionModel](
                data=faction,
                message="Faction relationship updated successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def add_member(
        self,
        id: str = Path(..., description="The ID of the faction"),
        request: FactionMembershipRequest = None
    ) -> BaseResponse[FactionModel]:
        """Add a new member to the faction."""
        try:
            faction = await self.service.add_member(
                id,
                request.npc_id,
                request.role,
                request.rank,
                request.notes
            )
            if not faction:
                raise HTTPException(status_code=404, detail="Faction not found")
            return BaseResponse[FactionModel](
                data=faction,
                message="Member added to faction successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def remove_member(
        self,
        id: str = Path(..., description="The ID of the faction"),
        npc_id: str = Path(..., description="The ID of the NPC to remove")
    ) -> BaseResponse[FactionModel]:
        """Remove a member from the faction."""
        try:
            faction = await self.service.remove_member(id, npc_id)
            if not faction:
                raise HTTPException(status_code=404, detail="Faction not found")
            return BaseResponse[FactionModel](
                data=faction,
                message="Member removed from faction successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_members(
        self,
        id: str = Path(..., description="The ID of the faction"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page"),
        role: str = Query(None, description="Filter by member role")
    ) -> PaginatedResponse[NPCModel]:
        """Get all members of the faction."""
        try:
            members, total = await self.service.get_members(id, page, per_page, role)
            return PaginatedResponse[NPCModel](
                data=members,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_relationships(
        self,
        id: str = Path(..., description="The ID of the faction")
    ) -> BaseResponse[Dict[str, Any]]:
        """Get all relationships with other factions."""
        try:
            relationships = await self.service.get_relationships(id)
            return BaseResponse[Dict[str, Any]](
                data=relationships
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_influence(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page"),
        min_influence: int = Query(None, description="Minimum influence score"),
        max_influence: int = Query(None, description="Maximum influence score")
    ) -> PaginatedResponse[FactionModel]:
        """Get factions sorted by their influence score."""
        try:
            factions, total = await self.service.get_by_influence(
                page,
                per_page,
                min_influence,
                max_influence
            )
            return PaginatedResponse[FactionModel](
                data=factions,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 