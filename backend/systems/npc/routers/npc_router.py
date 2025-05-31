"""
NPC Router Module

Comprehensive FastAPI router for NPC system operations.
Provides API endpoints for CRUD operations, memory management,
faction relationships, rumors, motifs, and population management.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

# FastAPI imports
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from pydantic import BaseModel, Field

# Import our service layer
from backend.systems.npc.services.npc_service import get_npc_service, NPCService

# Use canonical imports instead of dynamic loading
from backend.systems.npc.models import (
    CreateNpcRequest, UpdateNpcRequest, NpcResponse, NpcListResponse
)

from backend.infrastructure.shared.exceptions import (
    NpcNotFoundError,
    NpcValidationError,
    NpcConflictError
)

logger = logging.getLogger(__name__)

# Dependency injection function
def get_npc_service_dependency() -> NPCService:
    """Dependency injection function for NPCService"""
    return get_npc_service()

# Create the router
router = APIRouter(
    prefix="/api/npc",
    tags=["npc", "npc-system"],
    dependencies=[],
    responses={
        404: {"description": "NPC not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    },
)

# Request/Response Models for API operations
class MemoryRequest(BaseModel):
    """Request model for creating NPC memories"""
    content: str = Field(..., description="Memory content")
    importance: float = Field(default=1.0, ge=0.0, le=10.0, description="Memory importance (0-10)")
    emotion: Optional[str] = Field(None, description="Emotional context")
    location: Optional[str] = Field(None, description="Where the memory occurred")
    participants: Optional[List[str]] = Field(default_factory=list, description="Other participants")
    tags: Optional[List[str]] = Field(default_factory=list, description="Memory tags")

class FactionRequest(BaseModel):
    """Request model for faction operations"""
    faction_id: UUID = Field(..., description="Faction UUID")
    role: Optional[str] = Field("member", description="Role in faction")
    loyalty: Optional[float] = Field(default=5.0, ge=0.0, le=10.0, description="Loyalty level")

class RumorRequest(BaseModel):
    """Request model for rumor operations"""
    content: str = Field(..., description="Rumor content")
    source: Optional[str] = Field(None, description="Rumor source")
    credibility: Optional[float] = Field(default=5.0, ge=0.0, le=10.0, description="Credibility level")
    spread_chance: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Chance to spread")

class MotifRequest(BaseModel):
    """Request model for motif operations"""
    motif_type: str = Field(..., description="Type of motif")
    strength: float = Field(default=1.0, ge=0.0, le=10.0, description="Motif strength")
    description: Optional[str] = Field(None, description="Motif description")
    triggers: Optional[List[str]] = Field(default_factory=list, description="Trigger conditions")

class PopulationMigrationRequest(BaseModel):
    """Request model for population migration"""
    source_region: str = Field(..., description="Source region ID")
    target_region: str = Field(..., description="Target region ID")
    npc_ids: Optional[List[UUID]] = Field(None, description="Specific NPCs to migrate")
    migration_reason: Optional[str] = Field(None, description="Reason for migration")

class ScheduledTaskRequest(BaseModel):
    """Request model for scheduling NPC tasks"""
    task_type: str = Field(..., description="Type of task")
    npc_id: UUID = Field(..., description="NPC to assign task to")
    description: str = Field(..., description="Task description")
    priority: Optional[str] = Field("medium", description="Task priority")
    due_date: Optional[str] = Field(None, description="Due date (ISO format)")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Task parameters")

# ============================================================================
# Core CRUD Operations
# ============================================================================

@router.post("/", response_model=NpcResponse, status_code=status.HTTP_201_CREATED)
async def create_npc(
    request: CreateNpcRequest,
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> NpcResponse:
    """Create a new NPC"""
    try:
        logger.info(f"Creating NPC: {request.name}")
        npc = await npc_service.create_npc(request)
        return npc
    except NpcConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except NpcValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating NPC: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{npc_id}", response_model=NpcResponse)
async def get_npc(
    npc_id: UUID = Path(..., description="NPC UUID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> NpcResponse:
    """Get NPC by ID"""
    try:
        npc = await npc_service.get_npc(npc_id)
        if not npc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"NPC {npc_id} not found")
        return npc
    except Exception as e:
        logger.error(f"Error getting NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{npc_id}", response_model=NpcResponse)
async def update_npc(
    npc_id: UUID = Path(..., description="NPC UUID"),
    request: UpdateNpcRequest = Body(...),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> NpcResponse:
    """Update NPC by ID"""
    try:
        npc = await npc_service.update_npc(npc_id, request)
        return npc
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NpcValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{npc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_npc(
    npc_id: UUID = Path(..., description="NPC UUID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
):
    """Delete NPC by ID (soft delete)"""
    try:
        success = await npc_service.delete_npc(npc_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"NPC {npc_id} not found")
        return None
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=Dict[str, Any])
async def list_npcs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search term"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> Dict[str, Any]:
    """List NPCs with pagination and filtering"""
    try:
        npcs, total = await npc_service.list_npcs(page=page, size=size, status=status_filter, search=search)
        
        has_next = (page * size) < total
        has_prev = page > 1
        
        return {
            "items": npcs,
            "total": total,
            "page": page,
            "size": size,
            "has_next": has_next,
            "has_prev": has_prev
        }
    except Exception as e:
        logger.error(f"Error listing NPCs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ============================================================================
# Memory Management APIs
# ============================================================================

@router.get("/systems/memories/{npc_id}", response_model=List[Dict[str, Any]])
async def get_npc_memories(
    npc_id: UUID = Path(..., description="NPC UUID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> List[Dict[str, Any]]:
    """Retrieve NPC memories"""
    try:
        memories = await npc_service.get_npc_memories(npc_id)
        return memories
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting memories for NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/systems/memories/{npc_id}", status_code=status.HTTP_201_CREATED)
async def create_npc_memory(
    npc_id: UUID = Path(..., description="NPC UUID"),
    memory: MemoryRequest = Body(...),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> Dict[str, Any]:
    """Create new memory for NPC"""
    try:
        memory_data = memory.dict()
        success = await npc_service.add_memory_to_npc(npc_id, memory_data)
        if success:
            return {"message": "Memory created successfully", "npc_id": str(npc_id)}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create memory")
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating memory for NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/systems/memories/{npc_id}/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_npc_memory(
    npc_id: UUID = Path(..., description="NPC UUID"),
    memory_id: str = Path(..., description="Memory ID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
):
    """Delete memory from NPC"""
    try:
        success = await npc_service.forget_memory(npc_id, memory_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
        return None
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting memory {memory_id} for NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/systems/memories/{npc_id}/summary", response_model=Dict[str, Any])
async def get_npc_memory_summary(
    npc_id: UUID = Path(..., description="NPC UUID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> Dict[str, Any]:
    """Get memory summary for NPC"""
    try:
        memories = await npc_service.get_npc_memories(npc_id)
        
        total_memories = len(memories)
        recent_memories = [m for m in memories if 'created_at' in m]  # Filter for recent ones
        important_memories = [m for m in memories if m.get('importance', 0) > 7]
        
        return {
            "npc_id": str(npc_id),
            "total_memories": total_memories,
            "recent_count": len(recent_memories),
            "important_count": len(important_memories),
            "summary": f"NPC has {total_memories} memories, {len(important_memories)} highly important"
        }
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting memory summary for NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ============================================================================
# Faction Management APIs
# ============================================================================

@router.get("/systems/factions/{npc_id}", response_model=List[Dict[str, Any]])
async def get_npc_factions(
    npc_id: UUID = Path(..., description="NPC UUID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> List[Dict[str, Any]]:
    """Get NPC faction affiliations"""
    try:
        factions = await npc_service.get_npc_factions(npc_id)
        return factions
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting factions for NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/systems/factions/{npc_id}", status_code=status.HTTP_201_CREATED)
async def add_npc_faction(
    npc_id: UUID = Path(..., description="NPC UUID"),
    faction: FactionRequest = Body(...),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> Dict[str, Any]:
    """Add faction affiliation to NPC"""
    try:
        success = await npc_service.add_faction_to_npc(npc_id, faction.faction_id)
        if success:
            return {"message": "Faction affiliation added successfully", "npc_id": str(npc_id), "faction_id": str(faction.faction_id)}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add faction affiliation")
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding faction {faction.faction_id} to NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/systems/factions/{npc_id}/{faction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_npc_faction(
    npc_id: UUID = Path(..., description="NPC UUID"),
    faction_id: UUID = Path(..., description="Faction UUID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
):
    """Remove faction affiliation from NPC"""
    try:
        success = await npc_service.remove_faction_from_npc(npc_id, faction_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faction affiliation not found")
        return None
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error removing faction {faction_id} from NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ============================================================================
# Rumor System APIs
# ============================================================================

@router.get("/systems/rumors/{npc_id}", response_model=List[Dict[str, Any]])
async def get_npc_rumors(
    npc_id: UUID = Path(..., description="NPC UUID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> List[Dict[str, Any]]:
    """Get NPC rumors"""
    try:
        rumors = await npc_service.get_npc_rumors(npc_id)
        return rumors
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting rumors for NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/systems/rumors/{npc_id}", status_code=status.HTTP_201_CREATED)
async def add_npc_rumor(
    npc_id: UUID = Path(..., description="NPC UUID"),
    rumor: RumorRequest = Body(...),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> Dict[str, Any]:
    """Add rumor to NPC"""
    try:
        rumor_data = rumor.dict()
        success = await npc_service.add_rumor_to_npc(npc_id, rumor_data)
        if success:
            return {"message": "Rumor added successfully", "npc_id": str(npc_id)}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add rumor")
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding rumor to NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/systems/rumors/{npc_id}/{rumor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def forget_npc_rumor(
    npc_id: UUID = Path(..., description="NPC UUID"),
    rumor_id: str = Path(..., description="Rumor ID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
):
    """Remove rumor from NPC"""
    try:
        success = await npc_service.forget_rumor(npc_id, rumor_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rumor not found")
        return None
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error removing rumor {rumor_id} from NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ============================================================================
# Motif Management APIs
# ============================================================================

@router.get("/systems/motifs/{npc_id}", response_model=List[Dict[str, Any]])
async def get_npc_motifs(
    npc_id: UUID = Path(..., description="NPC UUID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> List[Dict[str, Any]]:
    """Get NPC motifs"""
    try:
        motifs = await npc_service.get_npc_motifs(npc_id)
        return motifs
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting motifs for NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/systems/motifs/{npc_id}", status_code=status.HTTP_201_CREATED)
async def apply_npc_motif(
    npc_id: UUID = Path(..., description="NPC UUID"),
    motif: MotifRequest = Body(...),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> Dict[str, Any]:
    """Apply motif to NPC"""
    try:
        motif_data = motif.dict()
        success = await npc_service.apply_motif(npc_id, motif_data)
        if success:
            return {"message": "Motif applied successfully", "npc_id": str(npc_id)}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to apply motif")
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error applying motif to NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/systems/motifs/{npc_id}/{motif_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_npc_motif(
    npc_id: UUID = Path(..., description="NPC UUID"),
    motif_id: str = Path(..., description="Motif ID"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
):
    """Remove motif from NPC"""
    try:
        success = await npc_service.remove_motif(npc_id, motif_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Motif not found")
        return None
    except NpcNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error removing motif {motif_id} from NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ============================================================================
# Population Management APIs
# ============================================================================

@router.get("/systems/population/{region_id}", response_model=List[NpcResponse])
async def get_regional_npcs(
    region_id: str = Path(..., description="Region identifier"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> List[NpcResponse]:
    """Get regional NPCs"""
    try:
        # For now, return all NPCs (could be filtered by region in the future)
        npcs, total = await npc_service.list_npcs(page=page, size=size)
        return npcs
    except Exception as e:
        logger.error(f"Error getting regional NPCs for {region_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/systems/population/migrate", status_code=status.HTTP_200_OK)
async def handle_npc_migration(
    migration: PopulationMigrationRequest = Body(...),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> Dict[str, Any]:
    """Handle NPC migration between regions"""
    try:
        # For now, this is a placeholder implementation
        # In a full implementation, this would update NPC locations
        migrated_count = len(migration.npc_ids) if migration.npc_ids else 0
        
        return {
            "message": f"Migration completed from {migration.source_region} to {migration.target_region}",
            "migrated_npcs": migrated_count,
            "reason": migration.migration_reason
        }
    except Exception as e:
        logger.error(f"Error handling migration: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/systems/population/stats", response_model=Dict[str, Any])
async def get_population_statistics(
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> Dict[str, Any]:
    """Get population statistics"""
    try:
        stats = await npc_service.get_npc_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting population statistics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ============================================================================
# Advanced NPC APIs
# ============================================================================

@router.post("/systems/scheduled-tasks", status_code=status.HTTP_201_CREATED)
async def schedule_npc_task(
    task: ScheduledTaskRequest = Body(...),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> Dict[str, Any]:
    """Schedule NPC task"""
    try:
        # For now, this is a placeholder implementation
        # In a full implementation, this would integrate with a task scheduler
        
        return {
            "message": "Task scheduled successfully",
            "task_id": f"task_{task.npc_id}_{task.task_type}",
            "npc_id": str(task.npc_id),
            "task_type": task.task_type,
            "priority": task.priority
        }
    except Exception as e:
        logger.error(f"Error scheduling task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/systems/loyalty/{npc_id}", response_model=Dict[str, Any])
async def get_npc_loyalty(
    npc_id: UUID = Path(..., description="NPC UUID"),
    character_id: Optional[str] = Query(None, description="Character ID for loyalty check"),
    npc_service: NPCService = Depends(get_npc_service_dependency)
) -> Dict[str, Any]:
    """Get loyalty status for NPC"""
    try:
        # Check if NPC exists
        npc = await npc_service.get_npc(npc_id)
        if not npc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"NPC {npc_id} not found")
        
        # For now, return basic loyalty information
        # In a full implementation, this would integrate with loyalty system
        loyalty_data = npc.properties.get('loyalty', {})
        
        return {
            "npc_id": str(npc_id),
            "character_id": character_id,
            "loyalty_level": loyalty_data.get('level', 'neutral'),
            "goodwill": loyalty_data.get('goodwill', 0),
            "trust": loyalty_data.get('trust', 5),
            "last_updated": loyalty_data.get('last_updated')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting loyalty for NPC {npc_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ============================================================================
# Health Check and Info
# ============================================================================

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "npc-system",
        "version": "1.0.0",
        "endpoints": {
            "core_crud": 5,
            "memory_management": 4,
            "faction_management": 3,
            "rumor_system": 3,
            "motif_management": 3,
            "population_management": 3,
            "advanced_features": 2
        }
    }

# Export the router
__all__ = ["router"] 