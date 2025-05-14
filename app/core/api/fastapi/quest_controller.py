"""Quest controller implementation.

This module provides the API controller for Quest entities, implementing standard CRUD
operations and quest-specific endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Path, Query, HTTPException
from pydantic import BaseModel

from .base_controller import BaseController
from ...middleware.rate_limit import RateLimiter
from ...middleware.cache import APICache
from ...services.quest import QuestService
from ....search.entities import QuestModel
from ..patterns import BaseResponse, PaginatedResponse

class QuestUpdateStatusRequest(BaseModel):
    """Request model for updating quest status."""
    status: str  # e.g., 'available', 'in_progress', 'completed', 'failed'
    reason: str

class QuestUpdateProgressRequest(BaseModel):
    """Request model for updating quest progress."""
    progress: Dict[str, Any]  # Flexible structure for different quest types
    completion_percentage: float
    notes: str = None

class QuestController(BaseController[QuestModel]):
    """Controller for Quest-related endpoints."""
    
    def __init__(
        self,
        service: QuestService,
        router: APIRouter,
        rate_limiter: RateLimiter,
        cache: APICache
    ):
        """Initialize the Quest controller."""
        super().__init__(service, router, "quest", rate_limiter, cache)
        self._register_quest_routes()
        
    def _register_quest_routes(self) -> None:
        """Register Quest-specific routes."""
        # Update status endpoint
        self.router.add_api_route(
            "/quests/{id}/status",
            self.update_status,
            methods=["PUT"],
            response_model=BaseResponse[QuestModel],
            summary="Update quest status",
            description="Update a quest's status (available, in_progress, completed, failed)"
        )
        
        # Update progress endpoint
        self.router.add_api_route(
            "/quests/{id}/progress",
            self.update_progress,
            methods=["PUT"],
            response_model=BaseResponse[QuestModel],
            summary="Update quest progress",
            description="Update the progress of a quest"
        )
        
        # Get available quests endpoint
        self.router.add_api_route(
            "/quests/available",
            self.get_available_quests,
            methods=["GET"],
            response_model=PaginatedResponse[QuestModel],
            summary="Get available quests",
            description="Get all quests that are currently available"
        )
        
        # Get quests by NPC endpoint
        self.router.add_api_route(
            "/quests/by-npc/{npc_id}",
            self.get_by_npc,
            methods=["GET"],
            response_model=PaginatedResponse[QuestModel],
            summary="Get quests by NPC",
            description="Get all quests associated with a specific NPC"
        )
        
        # Get quests by location endpoint
        self.router.add_api_route(
            "/quests/by-location/{location_id}",
            self.get_by_location,
            methods=["GET"],
            response_model=PaginatedResponse[QuestModel],
            summary="Get quests by location",
            description="Get all quests associated with a specific location"
        )
        
        # Get quests by type endpoint
        self.router.add_api_route(
            "/quests/by-type/{quest_type}",
            self.get_by_type,
            methods=["GET"],
            response_model=PaginatedResponse[QuestModel],
            summary="Get quests by type",
            description="Get all quests of a specific type"
        )
        
    async def update_status(
        self,
        id: str = Path(..., description="The ID of the quest"),
        request: QuestUpdateStatusRequest = None
    ) -> BaseResponse[QuestModel]:
        """Update a quest's status."""
        try:
            quest = await self.service.update_status(id, request.status, request.reason)
            if not quest:
                raise HTTPException(status_code=404, detail="Quest not found")
            return BaseResponse[QuestModel](
                data=quest,
                message="Quest status updated successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def update_progress(
        self,
        id: str = Path(..., description="The ID of the quest"),
        request: QuestUpdateProgressRequest = None
    ) -> BaseResponse[QuestModel]:
        """Update a quest's progress."""
        try:
            quest = await self.service.update_progress(
                id,
                request.progress,
                request.completion_percentage,
                request.notes
            )
            if not quest:
                raise HTTPException(status_code=404, detail="Quest not found")
            return BaseResponse[QuestModel](
                data=quest,
                message="Quest progress updated successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_available_quests(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page"),
        min_level: int = Query(None, description="Minimum level requirement"),
        max_level: int = Query(None, description="Maximum level requirement")
    ) -> PaginatedResponse[QuestModel]:
        """Get all quests that are currently available."""
        try:
            quests, total = await self.service.get_available_quests(
                page,
                per_page,
                min_level,
                max_level
            )
            return PaginatedResponse[QuestModel](
                data=quests,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_npc(
        self,
        npc_id: str = Path(..., description="The ID of the NPC"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[QuestModel]:
        """Get all quests associated with a specific NPC."""
        try:
            quests, total = await self.service.get_by_npc(npc_id, page, per_page)
            return PaginatedResponse[QuestModel](
                data=quests,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_by_location(
        self,
        location_id: str = Path(..., description="The ID of the location"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[QuestModel]:
        """Get all quests associated with a specific location."""
        try:
            quests, total = await self.service.get_by_location(location_id, page, per_page)
            return PaginatedResponse[QuestModel](
                data=quests,
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
        quest_type: str = Path(..., description="The type of quests to get"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ) -> PaginatedResponse[QuestModel]:
        """Get all quests of a specific type."""
        try:
            quests, total = await self.service.get_by_type(quest_type, page, per_page)
            return PaginatedResponse[QuestModel](
                data=quests,
                meta={
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 