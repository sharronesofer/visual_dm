"""
Arc System API Router

This module provides FastAPI routes for arc management operations.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.database import get_async_db
from backend.systems.arc.services.arc import ArcManager
from backend.infrastructure.repositories.arc.arc_repository import ArcRepository
from backend.infrastructure.repositories.arc.arc_step_repository import ArcStepRepository
from backend.infrastructure.repositories.arc.arc_progression_repository import ArcProgressionRepository
from backend.infrastructure.repositories.arc.arc_completion_record_repository import ArcCompletionRecordRepository

# Import models from the correct location
from backend.systems.arc.models.arc import (
    CreateArcRequest, UpdateArcRequest, ArcResponse, ArcListResponse,
    ArcType, ArcStatus, ArcPriority
)
from backend.systems.arc.models.arc_step import (
    CreateArcStepRequest, UpdateArcStepRequest, ArcStepResponse
)
from backend.systems.arc.models.arc_progression import (
    CreateArcProgressionRequest, ArcProgressionResponse
)
from backend.systems.arc.models.arc_completion_record import (
    CreateArcCompletionRecordRequest, ArcCompletionRecordResponse, ArcCompletionRecordListResponse
)

from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/arcs", tags=["arcs"])


# Response models for operations
class SuccessResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str


class ArcOperationResponse(BaseModel):
    success: bool
    message: str
    arc_id: Optional[UUID] = None


# Request models for operations
class ArcActivationRequest(BaseModel):
    force: bool = False


class ArcStepAdvanceRequest(BaseModel):
    step_id: Optional[UUID] = None
    completion_data: Optional[Dict[str, Any]] = None


class ArcCompletionRequest(BaseModel):
    outcome: str
    completion_notes: Optional[str] = None


class ArcSearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None


class BatchArcStatusUpdate(BaseModel):
    arc_ids: List[UUID]
    status: ArcStatus


class BatchArcStepUpdate(BaseModel):
    step_ids: List[UUID]
    updates: Dict[str, Any]


# Dependency to get database session
async def get_db() -> AsyncSession:
    """Get database session."""
    async with get_async_db() as session:
        yield session


# Dependency to get Arc Manager service
async def get_arc_manager(db: AsyncSession = Depends(get_db)) -> ArcManager:
    """Get Arc Manager service with dependencies."""
    arc_repo = ArcRepository(db)
    step_repo = ArcStepRepository(db)
    progression_repo = ArcProgressionRepository(db)
    completion_repo = ArcCompletionRecordRepository(db)
    
    return ArcManager(arc_repo, step_repo, progression_repo, completion_repo)


# Arc CRUD Endpoints
@router.post("/arcs", response_model=ArcResponse, status_code=status.HTTP_201_CREATED)
async def create_arc(
    arc_data: CreateArcRequest,
    manager: ArcManager = Depends(get_arc_manager)
) -> ArcResponse:
    """Create a new narrative arc."""
    try:
        arc = await manager.create_arc(
            title=arc_data.title,
            description=arc_data.description,
            arc_type=arc_data.arc_type,
            priority=arc_data.priority,
            region_id=arc_data.region_id,
            character_id=arc_data.character_id,
            npc_id=arc_data.npc_id,
            faction_ids=arc_data.faction_ids,
            narrative_summary=arc_data.narrative_summary,
            objectives=arc_data.objectives,
            themes=arc_data.themes,
            estimated_duration_hours=arc_data.estimated_duration_hours,
            tags=arc_data.tags,
            difficulty_level=arc_data.difficulty_level,
            player_impact=arc_data.player_impact,
            world_impact=arc_data.world_impact
        )
        
        if not arc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create arc. Check if type limits are exceeded."
            )
        
        return ArcResponse.from_orm(arc)
        
    except Exception as e:
        logger.error(f"Error creating arc: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/arcs", response_model=ArcListResponse)
async def list_arcs(
    skip: int = Query(0, ge=0, description="Number of arcs to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of arcs to return"),
    arc_type: Optional[ArcType] = Query(None, description="Filter by arc type"),
    status: Optional[ArcStatus] = Query(None, description="Filter by status"),
    priority: Optional[ArcPriority] = Query(None, description="Filter by priority"),
    manager: ArcManager = Depends(get_arc_manager)
) -> ArcListResponse:
    """Get list of arcs with optional filtering."""
    try:
        # Apply filters based on query parameters
        if arc_type and status:
            arcs = await manager.get_arcs_by_type(arc_type, status)
        elif arc_type:
            arcs = await manager.get_arcs_by_type(arc_type)
        elif status:
            arcs = await manager.get_arcs_by_status(status)
        else:
            # Get all arcs - in a real implementation, you'd want pagination here
            arcs = []  # This would need to be implemented in the manager
        
        # Apply pagination
        total = len(arcs)
        paged_arcs = arcs[skip:skip + limit]
        
        return ArcListResponse(
            items=[ArcResponse.from_orm(arc) for arc in paged_arcs],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
        
    except Exception as e:
        logger.error(f"Error listing arcs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/arcs/{arc_id}", response_model=ArcResponse)
async def get_arc(
    arc_id: UUID,
    manager: ArcManager = Depends(get_arc_manager)
) -> ArcResponse:
    """Get a specific arc by ID."""
    try:
        arc = await manager.get_arc(arc_id)
        if not arc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arc with ID {arc_id} not found"
            )
        
        return ArcResponse.from_orm(arc)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting arc {arc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/arcs/{arc_id}", response_model=ArcResponse)
async def update_arc(
    arc_id: UUID,
    arc_data: UpdateArcRequest,
    manager: ArcManager = Depends(get_arc_manager)
) -> ArcResponse:
    """Update an existing arc."""
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = arc_data.dict(exclude_unset=True)
        
        updated_arc = await manager.update_arc(arc_id, update_data)
        if not updated_arc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arc with ID {arc_id} not found"
            )
        
        return ArcResponse.from_orm(updated_arc)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating arc {arc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/arcs/{arc_id}", response_model=SuccessResponse)
async def delete_arc(
    arc_id: UUID,
    manager: ArcManager = Depends(get_arc_manager)
) -> SuccessResponse:
    """Delete an arc."""
    try:
        success = await manager.delete_arc(arc_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arc with ID {arc_id} not found"
            )
        
        return SuccessResponse(message=f"Arc {arc_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting arc {arc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Arc Management Endpoints
@router.post("/arcs/{arc_id}/activate", response_model=ArcOperationResponse)
async def activate_arc(
    arc_id: UUID,
    manager: ArcManager = Depends(get_arc_manager)
) -> ArcOperationResponse:
    """Activate an arc to begin progression."""
    try:
        success = await manager.activate_arc(arc_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arc with ID {arc_id} not found or cannot be activated"
            )
        
        return ArcOperationResponse(
            success=True,
            message=f"Arc {arc_id} activated successfully",
            arc_id=arc_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating arc {arc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/arcs/{arc_id}/advance", response_model=ArcOperationResponse)
async def advance_arc_step(
    arc_id: UUID,
    request: ArcStepAdvanceRequest,
    manager: ArcManager = Depends(get_arc_manager)
) -> ArcOperationResponse:
    """Advance to the next step in an arc."""
    try:
        success = await manager.advance_arc_step(
            arc_id, 
            step_id=request.step_id,
            completion_data=request.completion_data
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot advance arc {arc_id}. Check arc status and step requirements."
            )
        
        return ArcOperationResponse(
            success=True,
            message=f"Arc {arc_id} advanced to next step",
            arc_id=arc_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error advancing arc {arc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/arcs/{arc_id}/complete", response_model=ArcOperationResponse)
async def complete_arc(
    arc_id: UUID,
    request: ArcCompletionRequest,
    manager: ArcManager = Depends(get_arc_manager)
) -> ArcOperationResponse:
    """Complete an arc with specified outcome."""
    try:
        success = await manager.complete_arc(
            arc_id,
            outcome=request.outcome,
            completion_notes=request.completion_notes
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete arc {arc_id}. Check arc status."
            )
        
        return ArcOperationResponse(
            success=True,
            message=f"Arc {arc_id} completed with outcome: {request.outcome}",
            arc_id=arc_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing arc {arc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/arcs/active", response_model=List[ArcResponse])
async def get_active_arcs(
    manager: ArcManager = Depends(get_arc_manager)
) -> List[ArcResponse]:
    """Get all currently active arcs."""
    try:
        arcs = await manager.get_arcs_by_status(ArcStatus.ACTIVE)
        return [ArcResponse.from_orm(arc) for arc in arcs]
        
    except Exception as e:
        logger.error(f"Error getting active arcs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/arcs/stalled", response_model=List[ArcResponse])
async def get_stalled_arcs(
    hours_threshold: int = Query(24, ge=1, description="Hours of inactivity threshold"),
    manager: ArcManager = Depends(get_arc_manager)
) -> List[ArcResponse]:
    """Get arcs that have been inactive for specified hours."""
    try:
        arcs = await manager.get_stalled_arcs(hours_threshold)
        return [ArcResponse.from_orm(arc) for arc in arcs]
        
    except Exception as e:
        logger.error(f"Error getting stalled arcs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/arcs/search", response_model=List[ArcResponse])
async def search_arcs(
    request: ArcSearchRequest,
    manager: ArcManager = Depends(get_arc_manager)
) -> List[ArcResponse]:
    """Search arcs by query and filters."""
    try:
        arcs = await manager.search_arcs(
            query=request.query,
            filters=request.filters
        )
        return [ArcResponse.from_orm(arc) for arc in arcs]
        
    except Exception as e:
        logger.error(f"Error searching arcs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/statistics", response_model=Dict[str, Any])
async def get_arc_statistics(
    manager: ArcManager = Depends(get_arc_manager)
) -> Dict[str, Any]:
    """Get comprehensive arc system statistics."""
    try:
        stats = await manager.get_arc_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting arc statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/arcs/batch/status", response_model=SuccessResponse)
async def batch_update_arc_status(
    request: BatchArcStatusUpdate,
    manager: ArcManager = Depends(get_arc_manager)
) -> SuccessResponse:
    """Update status for multiple arcs."""
    try:
        success_count = await manager.batch_update_status(
            arc_ids=request.arc_ids,
            status=request.status
        )
        
        return SuccessResponse(
            message=f"Successfully updated {success_count} of {len(request.arc_ids)} arcs"
        )
        
    except Exception as e:
        logger.error(f"Error batch updating arc status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        ) 