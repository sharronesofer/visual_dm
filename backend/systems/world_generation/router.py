"""
World Generation API Router

FastAPI router for world generation endpoints.
Follows the established architectural pattern with facade service integration.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.systems.world_generation.services.world_generation_service import (
    WorldGenerationService, create_world_generation_service
)


# Request/Response Models
class GenerateWorldRequest(BaseModel):
    world_name: str
    template_name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class CreateRegionRequest(BaseModel):
    name: str
    biome_type: Optional[str] = None
    climate_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class WorldGenerationResponse(BaseModel):
    world_id: str
    world_name: str
    main_continent: Dict[str, Any]
    islands: List[Dict[str, Any]]
    regions: List[Dict[str, Any]]
    npcs: List[Dict[str, Any]]
    factions: List[Dict[str, Any]]
    trade_routes: List[Dict[str, Any]]
    generation_stats: Dict[str, Any]
    generation_time: float
    seed_used: int


class RegionResponse(BaseModel):
    id: str
    name: str
    description: str
    biome: str
    climate: str
    danger_level: str
    population: int
    area_km2: float
    coordinates: List[Dict[str, int]]
    resources: List[Dict[str, Any]]


class WorldListResponse(BaseModel):
    id: str
    world_name: str
    region_count: int
    created_at: str
    simulation_active: bool


class WorldDetailResponse(BaseModel):
    id: str
    world_name: str
    world_seed: int
    template_used: Optional[str]
    region_count: int
    npc_count: int
    faction_count: int
    trade_route_count: int
    generation_time: float
    created_at: str
    simulation_active: bool


# Create router
router = APIRouter(prefix="/world-generation", tags=["world-generation"])


def get_world_generation_service() -> WorldGenerationService:
    """Dependency to get world generation service instance"""
    return create_world_generation_service()


@router.post(
    "/generate",
    response_model=WorldGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new world",
    description="Generate a complete world with continents, regions, NPCs, factions, and trade routes."
)
async def generate_world(
    request: GenerateWorldRequest,
    service: WorldGenerationService = Depends(get_world_generation_service)
) -> WorldGenerationResponse:
    """Generate a new world"""
    try:
        result = await service.generate_world(
            world_name=request.world_name,
            template_name=request.template_name,
            config_dict=request.config
        )
        
        return WorldGenerationResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"World generation failed: {str(e)}"
        )


@router.post(
    "/regions",
    response_model=RegionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a single region",
    description="Create an individual region with specified biome and climate."
)
async def create_region(
    request: CreateRegionRequest,
    service: WorldGenerationService = Depends(get_world_generation_service)
) -> RegionResponse:
    """Create a single region"""
    try:
        result = await service.create_single_region(
            name=request.name,
            biome_type=request.biome_type,
            climate_type=request.climate_type,
            config_dict=request.config
        )
        
        return RegionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Region creation failed: {str(e)}"
        )


@router.get(
    "/worlds",
    response_model=List[WorldListResponse],
    summary="List all worlds",
    description="Get a list of all generated worlds with basic information."
)
async def list_worlds(
    active_only: bool = False,
    service: WorldGenerationService = Depends(get_world_generation_service)
) -> List[WorldListResponse]:
    """List all generated worlds"""
    try:
        worlds = await service.list_worlds(active_only=active_only)
        return [WorldListResponse(**world) for world in worlds]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list worlds: {str(e)}"
        )


@router.get(
    "/worlds/{world_id}",
    response_model=WorldDetailResponse,
    summary="Get world details",
    description="Get detailed information about a specific world."
)
async def get_world_details(
    world_id: UUID,
    service: WorldGenerationService = Depends(get_world_generation_service)
) -> WorldDetailResponse:
    """Get detailed information about a world"""
    try:
        world = await service.get_world_by_id(world_id)
        
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"World with ID {world_id} not found"
            )
        
        return WorldDetailResponse(**world)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get world details: {str(e)}"
        )


@router.get(
    "/worlds/{world_id}/content",
    summary="Get world content",
    description="Get complete world content including all regions, NPCs, factions, and trade routes."
)
async def get_world_content(
    world_id: UUID,
    service: WorldGenerationService = Depends(get_world_generation_service)
) -> Dict[str, Any]:
    """Get complete world content"""
    try:
        content = await service.get_world_content(world_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"World content for ID {world_id} not found"
            )
        
        return content
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get world content: {str(e)}"
        )


@router.get(
    "/templates",
    summary="Get available templates",
    description="Get a list of available world generation templates."
)
async def get_templates(
    service: WorldGenerationService = Depends(get_world_generation_service)
) -> List[Dict[str, Any]]:
    """Get available world generation templates"""
    try:
        templates = await service.get_available_templates()
        return templates
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}"
        )


@router.get(
    "/statistics",
    summary="Get generation statistics",
    description="Get overall statistics about world generation usage and performance."
)
async def get_statistics(
    service: WorldGenerationService = Depends(get_world_generation_service)
) -> Dict[str, Any]:
    """Get generation statistics"""
    try:
        stats = await service.get_generation_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        ) 