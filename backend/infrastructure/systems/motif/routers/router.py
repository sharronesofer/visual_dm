"""
Motif system - Router.
FastAPI router for motif system endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime

from backend.infrastructure.systems.motif.models import (
    Motif, MotifCreate, MotifUpdate, MotifFilter, MotifResponse,
    MotifScope, MotifLifecycle, MotifCategory, MotifEvolutionTrigger,
    PlayerCharacterMotif, MotifSynthesis, MotifConflict
)
from backend.infrastructure.systems.motif.repositories import MotifRepository
from backend.systems.motif.services.service import MotifService

# Create router instance
router = APIRouter(prefix="/motif", tags=["motif"])

# Security
security = HTTPBearer(auto_error=False)

logger = logging.getLogger(__name__)


def get_motif_repository():
    """Dependency to get motif repository instance."""
    return MotifRepository()


def get_motif_service(repository: MotifRepository = Depends(get_motif_repository)):
    """Dependency to get motif service instance."""
    return MotifService(repository=repository)


async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Basic auth verification placeholder."""
    # TODO: Implement proper authentication
    # For now, just pass through
    return credentials


# Health & Info Endpoints

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "motif", "timestamp": datetime.utcnow()}


@router.get("/info")
async def system_info():
    """Get system information."""
    return {
        "system": "motif",
        "version": "1.0.0",
        "available_categories": [cat.value for cat in MotifCategory],
        "available_scopes": [scope.value for scope in MotifScope],
        "available_lifecycles": [lifecycle.value for lifecycle in MotifLifecycle]
    }


# Core CRUD Operations

@router.post("/", response_model=MotifResponse, status_code=status.HTTP_201_CREATED)
async def create_motif(
    motif_data: MotifCreate,
    service: MotifService = Depends(get_motif_service),
    _auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
):
    """Create a new motif."""
    try:
        motif = await service.create_motif(motif_data)
        logger.info(f"Created motif: {motif.id}")
        return MotifResponse(
            success=True,
            message="Motif created successfully",
            data=motif
        )
    except Exception as e:
        logger.error(f"Error creating motif: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create motif: {str(e)}"
        )


@router.get("/", response_model=MotifResponse)
async def list_motifs(
    category: Optional[MotifCategory] = Query(None, description="Filter by category"),
    scope: Optional[MotifScope] = Query(None, description="Filter by scope"),
    lifecycle: Optional[MotifLifecycle] = Query(None, description="Filter by lifecycle"),
    min_intensity: Optional[int] = Query(None, ge=1, le=10, description="Minimum intensity"),
    max_intensity: Optional[int] = Query(None, ge=1, le=10, description="Maximum intensity"),
    region_id: Optional[str] = Query(None, description="Filter by region ID"),
    active_only: bool = Query(True, description="Include only active motifs"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    service: MotifService = Depends(get_motif_service)
):
    """List motifs with optional filtering."""
    try:
        # Build filter
        filter_params = MotifFilter(
            category=category,
            scope=scope,
            lifecycle=lifecycle,
            min_intensity=min_intensity,
            max_intensity=max_intensity,
            region_id=region_id,
            active_only=active_only
        )
        
        motifs = await service.list_motifs(filter_params, limit=limit, offset=offset)
        total_count = await service.count_motifs(filter_params)
        
        return MotifResponse(
            success=True,
            message=f"Retrieved {len(motifs)} motifs",
            data={
                "motifs": motifs,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        logger.error(f"Error listing motifs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list motifs: {str(e)}"
        )


@router.get("/{motif_id}", response_model=MotifResponse)
async def get_motif(
    motif_id: str = Path(..., description="Motif ID"),
    service: MotifService = Depends(get_motif_service)
):
    """Get a specific motif by ID."""
    try:
        motif = await service.get_motif(motif_id)
        if not motif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Motif with ID {motif_id} not found"
            )
        
        return MotifResponse(
            success=True,
            message="Motif retrieved successfully",
            data=motif
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting motif {motif_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get motif: {str(e)}"
        )


@router.put("/{motif_id}", response_model=MotifResponse)
async def update_motif(
    motif_id: str = Path(..., description="Motif ID"),
    motif_data: MotifUpdate = ...,
    service: MotifService = Depends(get_motif_service),
    _auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
):
    """Update a motif."""
    try:
        motif = await service.update_motif(motif_id, motif_data)
        if not motif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Motif with ID {motif_id} not found"
            )
        
        logger.info(f"Updated motif: {motif_id}")
        return MotifResponse(
            success=True,
            message="Motif updated successfully",
            data=motif
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating motif {motif_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update motif: {str(e)}"
        )


@router.delete("/{motif_id}", response_model=MotifResponse)
async def delete_motif(
    motif_id: str = Path(..., description="Motif ID"),
    service: MotifService = Depends(get_motif_service),
    _auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
):
    """Delete a motif."""
    try:
        success = await service.delete_motif(motif_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Motif with ID {motif_id} not found"
            )
        
        logger.info(f"Deleted motif: {motif_id}")
        return MotifResponse(
            success=True,
            message="Motif deleted successfully",
            data={"deleted_id": motif_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting motif {motif_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete motif: {str(e)}"
        )


# Lifecycle Management

@router.post("/{motif_id}/lifecycle", response_model=MotifResponse)
async def update_motif_lifecycle(
    motif_id: str = Path(..., description="Motif ID"),
    new_lifecycle: MotifLifecycle = Query(..., description="New lifecycle state"),
    service: MotifService = Depends(get_motif_service),
    _auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
):
    """Update a motif's lifecycle state."""
    try:
        motif = await service.update_motif_lifecycle(motif_id, new_lifecycle)
        if not motif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Motif with ID {motif_id} not found"
            )
        
        logger.info(f"Updated lifecycle for motif {motif_id} to {new_lifecycle}")
        return MotifResponse(
            success=True,
            message=f"Motif lifecycle updated to {new_lifecycle}",
            data=motif
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lifecycle for motif {motif_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update motif lifecycle: {str(e)}"
        )


@router.post("/lifecycle/advance", response_model=MotifResponse)
async def advance_all_lifecycles(
    service: MotifService = Depends(get_motif_service),
    _auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
):
    """Advance all eligible motif lifecycles."""
    try:
        advanced_count = await service.advance_motif_lifecycles()
        logger.info(f"Advanced {advanced_count} motif lifecycles")
        return MotifResponse(
            success=True,
            message=f"Advanced {advanced_count} motif lifecycles",
            data={"advanced_count": advanced_count}
        )
    except Exception as e:
        logger.error(f"Error advancing lifecycles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to advance lifecycles: {str(e)}"
        )


# Spatial Queries

@router.get("/spatial/position", response_model=MotifResponse)
async def get_motifs_at_position(
    x: float = Query(..., description="X coordinate"),
    y: float = Query(..., description="Y coordinate"),
    radius: float = Query(50.0, ge=0, description="Search radius"),
    service: MotifService = Depends(get_motif_service)
):
    """Get motifs at a specific position within a radius."""
    try:
        motifs = await service.get_motifs_at_position(x=x, y=y, radius=radius)
        return MotifResponse(
            success=True,
            message=f"Found {len(motifs)} motifs at position ({x}, {y})",
            data={"motifs": motifs, "position": {"x": x, "y": y}, "radius": radius}
        )
    except Exception as e:
        logger.error(f"Error getting motifs at position ({x}, {y}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get motifs at position: {str(e)}"
        )


@router.get("/spatial/region/{region_id}", response_model=MotifResponse)
async def get_regional_motifs(
    region_id: str = Path(..., description="Region ID"),
    service: MotifService = Depends(get_motif_service)
):
    """Get all motifs affecting a specific region."""
    try:
        motifs = await service.get_regional_motifs(region_id)
        return MotifResponse(
            success=True,
            message=f"Found {len(motifs)} motifs for region {region_id}",
            data={"motifs": motifs, "region_id": region_id}
        )
    except Exception as e:
        logger.error(f"Error getting regional motifs for {region_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get regional motifs: {str(e)}"
        )


@router.get("/spatial/global", response_model=MotifResponse)
async def get_global_motifs(
    service: MotifService = Depends(get_motif_service)
):
    """Get all global motifs."""
    try:
        motifs = await service.get_global_motifs()
        return MotifResponse(
            success=True,
            message=f"Found {len(motifs)} global motifs",
            data={"motifs": motifs}
        )
    except Exception as e:
        logger.error(f"Error getting global motifs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get global motifs: {str(e)}"
        )


# Narrative Context

@router.get("/context/position", response_model=MotifResponse)
async def get_narrative_context_at_position(
    x: float = Query(..., description="X coordinate"),
    y: float = Query(..., description="Y coordinate"),
    context_size: str = Query("medium", regex="^(small|medium|large)$", description="Context size"),
    service: MotifService = Depends(get_motif_service)
):
    """Get narrative context for AI systems at a specific position."""
    try:
        context = await service.get_motif_context(x=x, y=y)
        enhanced_context = await service.get_enhanced_narrative_context(context_size=context_size)
        
        return MotifResponse(
            success=True,
            message="Narrative context retrieved successfully",
            data={
                "position": {"x": x, "y": y},
                "basic_context": context,
                "enhanced_context": enhanced_context,
                "context_size": context_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting narrative context at ({x}, {y}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get narrative context: {str(e)}"
        )


@router.get("/context/global", response_model=MotifResponse)
async def get_global_narrative_context(
    context_size: str = Query("medium", regex="^(small|medium|large)$", description="Context size"),
    service: MotifService = Depends(get_motif_service)
):
    """Get global narrative context for AI systems."""
    try:
        enhanced_context = await service.get_enhanced_narrative_context(context_size=context_size)
        
        return MotifResponse(
            success=True,
            message="Global narrative context retrieved successfully",
            data={
                "enhanced_context": enhanced_context,
                "context_size": context_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting global narrative context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get global narrative context: {str(e)}"
        )


# Player Character Motifs

@router.get("/player/{player_id}", response_model=MotifResponse)
async def get_player_motifs(
    player_id: str = Path(..., description="Player ID"),
    service: MotifService = Depends(get_motif_service)
):
    """Get all motifs associated with a specific player character."""
    try:
        # Use filter to get PC motifs
        filter_params = MotifFilter(
            scope=MotifScope.PLAYER_CHARACTER,
            player_id=player_id,
            active_only=True
        )
        motifs = await service.list_motifs(filter_params)
        
        return MotifResponse(
            success=True,
            message=f"Found {len(motifs)} motifs for player {player_id}",
            data={"motifs": motifs, "player_id": player_id}
        )
    except Exception as e:
        logger.error(f"Error getting player motifs for {player_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get player motifs: {str(e)}"
        )


# Evolution & Events

@router.post("/{motif_id}/evolve", response_model=MotifResponse)
async def trigger_motif_evolution(
    motif_id: str = Path(..., description="Motif ID"),
    trigger_type: MotifEvolutionTrigger = Query(..., description="Evolution trigger type"),
    trigger_description: str = Query(..., description="Description of the trigger event"),
    service: MotifService = Depends(get_motif_service),
    _auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
):
    """Manually trigger motif evolution."""
    try:
        result = await service.trigger_motif_evolution(
            motif_id=motif_id,
            trigger_type=trigger_type,
            trigger_description=trigger_description
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Motif with ID {motif_id} not found or evolution failed"
            )
        
        logger.info(f"Triggered evolution for motif {motif_id}")
        return MotifResponse(
            success=True,
            message="Motif evolution triggered successfully",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering evolution for motif {motif_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger motif evolution: {str(e)}"
        )


# Statistics & Analytics

@router.get("/stats/summary", response_model=MotifResponse)
async def get_motif_statistics(
    service: MotifService = Depends(get_motif_service)
):
    """Get overall motif system statistics."""
    try:
        stats = await service.get_motif_statistics()
        return MotifResponse(
            success=True,
            message="Motif statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting motif statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get motif statistics: {str(e)}"
        )


# Conflict Resolution (answering user's question about what this means)

@router.get("/conflicts", response_model=MotifResponse)
async def get_motif_conflicts(
    service: MotifService = Depends(get_motif_service)
):
    """Get all current motif conflicts (opposing themes creating narrative tension)."""
    try:
        conflicts = await service.get_active_conflicts()
        return MotifResponse(
            success=True,
            message=f"Found {len(conflicts)} active motif conflicts",
            data={"conflicts": conflicts}
        )
    except Exception as e:
        logger.error(f"Error getting motif conflicts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get motif conflicts: {str(e)}"
        )


@router.post("/conflicts/resolve", response_model=MotifResponse)
async def resolve_motif_conflicts(
    auto_resolve: bool = Query(True, description="Automatically resolve conflicts"),
    service: MotifService = Depends(get_motif_service),
    _auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
):
    """
    Resolve motif conflicts. 
    
    Motif conflicts occur when opposing themes (like hope vs despair) 
    exist simultaneously and create narrative tension. This should be 
    interpreted by the LLM as dramatic tension rather than errors.
    """
    try:
        resolved_count = await service.resolve_conflicts(auto_resolve=auto_resolve)
        logger.info(f"Resolved {resolved_count} motif conflicts")
        return MotifResponse(
            success=True,
            message=f"Resolved {resolved_count} motif conflicts",
            data={"resolved_count": resolved_count, "auto_resolve": auto_resolve}
        )
    except Exception as e:
        logger.error(f"Error resolving conflicts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve conflicts: {str(e)}"
        )


# Advanced System Management

@router.post("/canonical/generate", response_model=MotifResponse)
async def generate_canonical_motifs(
    force_regenerate: bool = Query(False, description="Force regeneration of existing canonical motifs"),
    service: MotifService = Depends(get_motif_service),
    _auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
):
    """
    Generate the 50 canonical motifs as specified in the Development Bible.
    These are permanent motifs that represent core narrative themes.
    """
    try:
        result = await service.generate_canonical_motifs(force_regenerate=force_regenerate)
        
        return MotifResponse(
            success=True,
            message=result["message"],
            data=result
        )
    except Exception as e:
        logger.error(f"Error generating canonical motifs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate canonical motifs: {str(e)}"
        )


@router.post("/evolution/process", response_model=MotifResponse)
async def process_evolution_triggers(
    service: MotifService = Depends(get_motif_service),
    _auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
):
    """Process all pending motif evolution triggers based on system analysis."""
    try:
        result = await service.process_evolution_triggers()
        
        return MotifResponse(
            success=True,
            message=f"Evolution processing complete: {result.get('evolved', 0)} motifs evolved",
            data=result
        )
    except Exception as e:
        logger.error(f"Error processing evolution triggers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process evolution triggers: {str(e)}"
        )


@router.get("/analysis/interactions", response_model=MotifResponse)
async def analyze_motif_interactions(
    region_id: Optional[str] = Query(None, description="Region ID for analysis (None for global)"),
    service: MotifService = Depends(get_motif_service)
):
    """Analyze interactions, synergies, and conflicts between motifs."""
    try:
        result = await service.analyze_motif_interactions(region_id=region_id)
        
        return MotifResponse(
            success=True,
            message=result.get("summary", "Interaction analysis complete"),
            data=result
        )
    except Exception as e:
        logger.error(f"Error analyzing motif interactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze motif interactions: {str(e)}"
        )


@router.get("/analysis/distribution", response_model=MotifResponse)
async def analyze_motif_distribution(
    service: MotifService = Depends(get_motif_service)
):
    """Analyze and optimize motif distribution across scopes and regions."""
    try:
        result = await service.optimize_motif_distribution()
        
        return MotifResponse(
            success=True,
            message="Distribution analysis complete",
            data=result
        )
    except Exception as e:
        logger.error(f"Error analyzing motif distribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze motif distribution: {str(e)}"
        )


@router.post("/maintenance/cleanup", response_model=MotifResponse)
async def cleanup_expired_motifs(
    service: MotifService = Depends(get_motif_service),
    _auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
):
    """Clean up expired motifs that have reached CONCLUDED lifecycle."""
    try:
        cleanup_count = await service.cleanup_expired_motifs()
        
        return MotifResponse(
            success=True,
            message=f"Cleaned up {cleanup_count} expired motifs",
            data={"cleanup_count": cleanup_count}
        )
    except Exception as e:
        logger.error(f"Error cleaning up expired motifs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup expired motifs: {str(e)}"
        )
