"""
Region System API Router

Comprehensive API endpoints for region system including:
- World metadata and continent management
- Region CRUD operations and generation
- Biome adjacency validation
- Real-time updates and WebSocket integration
- Performance monitoring and optimization
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import random

from backend.infrastructure.database import get_db_session
from backend.infrastructure.shared.exceptions import (
    RegionNotFoundError,
    RegionValidationError,
    RegionConflictError,
    RepositoryError
)

# Import dependency injection system
from backend.infrastructure.systems.region.dependencies import (
    RegionService, ContinentService, EventService,
    ValidationService, WorldGenService
)

# Import schemas for API validation (using strings per Bible)
from backend.infrastructure.systems.region.schemas import (
    RegionCreateSchema, RegionUpdateSchema, RegionResponseSchema,
    ContinentCreateSchema, ContinentResponseSchema,
    HexCoordinateSchema, ResourceNodeSchema
)

# Import performance monitoring router
from .performance_router import router as performance_router

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/regions", tags=["regions"])

# Include performance monitoring sub-router
router.include_router(
    performance_router,
    prefix="/performance",
    tags=["region-performance"]
)

# WebSocket connection manager for real-time updates
class RegionWebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast_region_update(self, region_data: dict):
        """Broadcast region updates to all connected clients"""
        if not self.active_connections:
            return
        
        message = {
            "type": "region_update",
            "data": region_data
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

# Global WebSocket manager instance
ws_manager = RegionWebSocketManager()

# ============================================================================
# WORLD METADATA ENDPOINTS
# ============================================================================

@router.get("/world/metadata", response_model=Dict[str, Any])
async def get_world_metadata(
    continent_service: ContinentService,
    region_service: RegionService
):
    """Get comprehensive world metadata including continents and statistics"""
    try:
        # Use business services instead of repositories (wrapped in async)
        continents = await asyncio.to_thread(continent_service.get_all_continents)
        
        # Calculate world-level statistics
        total_area = sum(c.total_area_square_km for c in continents)
        continent_count = len(continents)
        
        # Get region count (simplified for now)
        all_regions = await asyncio.to_thread(region_service.get_regions)
        total_regions = len(all_regions)
        total_population = sum(r.population for r in all_regions)
        avg_population = total_population / total_regions if total_regions > 0 else 0
        
        # Calculate biome distribution using strings per Bible
        biome_distribution = {}
        for region in all_regions:
            biome = region.profile.dominant_biome if region.profile else "unknown"
            biome_distribution[biome] = biome_distribution.get(biome, 0) + 1
        
        world_metadata = {
            "world_info": {
                "total_continents": continent_count,
                "total_area_square_km": total_area,
                "total_regions": total_regions,
                "total_population": total_population,
                "average_population_per_region": avg_population
            },
            "continents": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "description": c.description,
                    "area_square_km": c.total_area_square_km,
                    "political_situation": c.political_situation
                }
                for c in continents
            ],
            "biome_distribution": biome_distribution,
            "generation_info": {
                "supports_procedural_generation": True,
                "available_biomes": [
                    "temperate_forest", "deciduous_forest", "coniferous_forest", "tropical_rainforest",
                    "grassland", "prairie", "savanna", "desert", "arctic", "tundra",
                    "mountains", "hills", "swamp", "marsh", "coastal", "island",
                    "volcanic", "magical_forest", "shadowlands", "feywild"
                ],
                "available_climates": [
                    "tropical", "subtropical", "temperate", "continental", "polar",
                    "arid", "semi_arid", "mediterranean", "monsoon", "oceanic", "magical"
                ],
                "danger_levels": list(range(1, 11))  # 1-10 per Bible
            }
        }
        
        return world_metadata
        
    except Exception as e:
        logger.error(f"Error getting world metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get world metadata: {str(e)}")

@router.get("/world/continents", response_model=List[ContinentResponseSchema])
async def list_continents(continent_service: ContinentService):
    """Get list of all continents"""
    try:
        continents = await asyncio.to_thread(continent_service.get_all_continents)
        
        return [
            ContinentResponseSchema(
                id=c.id,
                name=c.name,
                description=c.description or "",
                total_area_square_km=c.total_area_square_km,
                political_situation=c.political_situation,
                climate_zones=[str(zone.value) if hasattr(zone, 'value') else str(zone) for zone in c.climate_zones],
                major_biomes=[str(biome.value) if hasattr(biome, 'value') else str(biome) for biome in c.major_biomes],
                region_count=0,  # TODO: Calculate from relationships
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in continents
        ]
        
    except Exception as e:
        logger.error(f"Error listing continents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list continents: {str(e)}")

# ============================================================================
# CONTINENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/continents", response_model=ContinentResponseSchema, status_code=201)
async def create_continent(
    continent_data: ContinentCreateSchema,
    continent_service: ContinentService
):
    """Create a new continent"""
    try:
        continent = await asyncio.to_thread(
            continent_service.create_continent,
            name=continent_data.name,
            description=continent_data.description
        )
        
        response = ContinentResponseSchema(
            id=continent.id,
            name=continent.name,
            description=continent.description or "",
            total_area_square_km=continent.total_area_square_km,
            political_situation=continent.political_situation,
            climate_zones=[],
            major_biomes=[],
            region_count=0,
            created_at=continent.created_at,
            updated_at=continent.updated_at
        )
        
        # Broadcast update
        await ws_manager.broadcast_region_update({
            "action": "continent_created",
            "continent": response.dict()
        })
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating continent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create continent: {str(e)}")

@router.get("/continents/{continent_id}", response_model=ContinentResponseSchema)
async def get_continent(
    continent_id: UUID,
    continent_service: ContinentService
):
    """Get continent by ID"""
    try:
        continent = await asyncio.to_thread(continent_service.get_continent_by_id, continent_id)
        
        return ContinentResponseSchema(
            id=continent.id,
            name=continent.name,
            description=continent.description or "",
            total_area_square_km=continent.total_area_square_km,
            political_situation=continent.political_situation,
            climate_zones=[str(zone.value) if hasattr(zone, 'value') else str(zone) for zone in continent.climate_zones],
            major_biomes=[str(biome.value) if hasattr(biome, 'value') else str(biome) for biome in continent.major_biomes],
            region_count=0,  # TODO: Calculate from relationships
            created_at=continent.created_at,
            updated_at=continent.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting continent {continent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get continent: {str(e)}")

@router.get("/continents/{continent_id}/regions", response_model=List[RegionResponseSchema])
async def get_regions_by_continent(
    continent_id: UUID,
    region_service: RegionService
):
    """Get all regions in a continent"""
    try:
        regions = await asyncio.to_thread(region_service.get_regions_by_continent, continent_id)
        
        return [
            RegionResponseSchema(
                id=r.id,
                name=r.name,
                description=r.description or "",
                region_type=r.region_type,  # String per Bible
                dominant_biome=r.profile.dominant_biome if r.profile else "unknown",  # String per Bible
                climate=r.profile.climate.value if r.profile and r.profile.climate else "unknown",  # String per Bible
                population=r.population,
                area_square_km=r.area_square_km,
                danger_level=r.danger_level.value if r.danger_level else 2,
                exploration_status=0.0,  # TODO: Add to model
                continent_id=r.continent_id,
                center_coordinate=HexCoordinateSchema(
                    q=r.center_coordinate.q, 
                    r=r.center_coordinate.r, 
                    s=r.center_coordinate.s
                ) if r.center_coordinate else None,
                hex_coordinates=[
                    HexCoordinateSchema(q=coord.q, r=coord.r, s=coord.s) 
                    for coord in r.hex_coordinates
                ],
                resource_nodes=[
                    ResourceNodeSchema(
                        resource_type=node.resource_type,
                        abundance=node.abundance,
                        quality=node.quality,
                        accessibility=node.accessibility,
                        depletion_rate=node.depletion_rate,
                        current_reserves=node.current_reserves,
                        location=HexCoordinateSchema(
                            q=node.location.q, 
                            r=node.location.r, 
                            s=node.location.s
                        ) if node.location else None
                    )
                    for node in (r.resource_nodes or [])
                ],
                created_at=r.created_at,
                updated_at=r.updated_at
            )
            for r in regions
        ]
        
    except Exception as e:
        logger.error(f"Error getting regions for continent {continent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get regions: {str(e)}")

# ============================================================================
# REGION CRUD ENDPOINTS
# ============================================================================

@router.post("/", response_model=RegionResponseSchema, status_code=201)
async def create_region(
    region_data: RegionCreateSchema,
    region_service: RegionService,
    event_service: EventService
):
    """Create a new region"""
    try:
        # Convert schema to dict for business service (using strings per Bible)
        create_data = {
            "name": region_data.name,
            "description": region_data.description,
            "region_type": region_data.region_type.value if hasattr(region_data.region_type, 'value') else str(region_data.region_type),
            "dominant_biome": region_data.dominant_biome.value if hasattr(region_data.dominant_biome, 'value') else str(region_data.dominant_biome),
            "climate": region_data.climate.value if hasattr(region_data.climate, 'value') else str(region_data.climate),
            "continent_id": str(region_data.continent_id) if region_data.continent_id else None,
            "population": region_data.population
        }
        
        region = await asyncio.to_thread(region_service.create_region, create_data)
        
        response = RegionResponseSchema(
            id=region.id,
            name=region.name,
            description=region.description or "",
            region_type=region.region_type,
            dominant_biome=region.profile.dominant_biome if region.profile else "unknown",
            climate=region.profile.climate.value if region.profile and region.profile.climate else "unknown",
            population=region.population,
            area_square_km=region.area_square_km,
            danger_level=region.danger_level.value if region.danger_level else 2,
            exploration_status=0.0,
            continent_id=region.continent_id,
            center_coordinate=HexCoordinateSchema(
                q=region.center_coordinate.q, 
                r=region.center_coordinate.r, 
                s=region.center_coordinate.s
            ) if region.center_coordinate else None,
            hex_coordinates=[
                HexCoordinateSchema(q=coord.q, r=coord.r, s=coord.s) 
                for coord in region.hex_coordinates
            ],
            resource_nodes=[
                ResourceNodeSchema(
                    resource_type=node.resource_type,
                    abundance=node.abundance,
                    quality=node.quality,
                    accessibility=node.accessibility,
                    depletion_rate=node.depletion_rate,
                    current_reserves=node.current_reserves,
                    location=HexCoordinateSchema(
                        q=node.location.q, 
                        r=node.location.r, 
                        s=node.location.s
                    ) if node.location else None
                )
                for node in (region.resource_nodes or [])
            ],
            created_at=region.created_at,
            updated_at=region.updated_at
        )
        
        # Create business event
        try:
            event_data = event_service.create_region_created_event(
                region_id=region.id,
                region_name=region.name,
                region_type=region.region_type,
                continent_id=region.continent_id,
                created_by="api"
            )
            # TODO: Dispatch event via infrastructure layer
        except Exception as e:
            logger.warning(f"Failed to create region event: {e}")
        
        # Broadcast WebSocket update
        await ws_manager.broadcast_region_update({
            "action": "region_created",
            "region": response.dict()
        })
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating region: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create region: {str(e)}")

@router.get("/", response_model=List[RegionResponseSchema])
async def list_regions(
    region_service: RegionService,
    continent_id: Optional[UUID] = Query(None, description="Filter by continent ID"),
    biome_type: Optional[str] = Query(None, description="Filter by biome type (string per Bible)"),
    region_type: Optional[str] = Query(None, description="Filter by region type (string per Bible)"),
    name_filter: Optional[str] = Query(None, description="Filter by name (partial match)"),
    min_population: Optional[int] = Query(None, description="Minimum population"),
    max_population: Optional[int] = Query(None, description="Maximum population"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size")
):
    """List regions with optional filtering and pagination"""
    try:
        # Build filters using strings per Bible
        filters = {}
        if continent_id:
            filters["continent_id"] = continent_id
        if biome_type:
            filters["dominant_biome"] = biome_type  # String per Bible
        if region_type:
            filters["region_type"] = region_type  # String per Bible
        if name_filter:
            filters["name_filter"] = name_filter
        if min_population is not None:
            filters["min_population"] = min_population
        if max_population is not None:
            filters["max_population"] = max_population
        
        # Get regions using business service
        regions = await asyncio.to_thread(region_service.get_regions, filters)
        
        # Apply pagination (simplified for now)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_regions = regions[start_idx:end_idx]
        
        response_data = [
            RegionResponseSchema(
                id=r.id,
                name=r.name,
                description=r.description or "",
                region_type=r.region_type,
                dominant_biome=r.profile.dominant_biome if r.profile else "unknown",
                climate=r.profile.climate.value if r.profile and r.profile.climate else "unknown",
                population=r.population,
                area_square_km=r.area_square_km,
                danger_level=r.danger_level.value if r.danger_level else 2,
                exploration_status=0.0,
                continent_id=r.continent_id,
                center_coordinate=HexCoordinateSchema(
                    q=r.center_coordinate.q, 
                    r=r.center_coordinate.r, 
                    s=r.center_coordinate.s
                ) if r.center_coordinate else None,
                hex_coordinates=[
                    HexCoordinateSchema(q=coord.q, r=coord.r, s=coord.s) 
                    for coord in r.hex_coordinates
                ],
                resource_nodes=[
                    ResourceNodeSchema(
                        resource_type=node.resource_type,
                        abundance=node.abundance,
                        quality=node.quality,
                        accessibility=node.accessibility,
                        depletion_rate=node.depletion_rate,
                        current_reserves=node.current_reserves,
                        location=HexCoordinateSchema(
                            q=node.location.q, 
                            r=node.location.r, 
                            s=node.location.s
                        ) if node.location else None
                    )
                    for node in (r.resource_nodes or [])
                ],
                created_at=r.created_at,
                updated_at=r.updated_at
            )
            for r in paginated_regions
        ]
        
        # Add pagination metadata to headers
        return JSONResponse(
            content=[region.dict() for region in response_data],
            headers={
                "X-Total-Count": str(len(regions)),
                "X-Page": str(page),
                "X-Page-Size": str(size),
                "X-Total-Pages": str((len(regions) + size - 1) // size)
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing regions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list regions: {str(e)}")

@router.get("/{region_id}", response_model=RegionResponseSchema)
async def get_region(
    region_id: UUID,
    region_service: RegionService
):
    """Get region by ID"""
    try:
        region = await asyncio.to_thread(region_service.get_region_by_id, region_id)
        
        return RegionResponseSchema(
            id=region.id,
            name=region.name,
            description=region.description or "",
            region_type=region.region_type,
            dominant_biome=region.profile.dominant_biome if region.profile else "unknown",
            climate=region.profile.climate.value if region.profile and region.profile.climate else "unknown",
            population=region.population,
            area_square_km=region.area_square_km,
            danger_level=region.danger_level.value if region.danger_level else 2,
            exploration_status=0.0,
            continent_id=region.continent_id,
            center_coordinate=HexCoordinateSchema(
                q=region.center_coordinate.q, 
                r=region.center_coordinate.r, 
                s=region.center_coordinate.s
            ) if region.center_coordinate else None,
            hex_coordinates=[
                HexCoordinateSchema(q=coord.q, r=coord.r, s=coord.s) 
                for coord in region.hex_coordinates
            ],
            resource_nodes=[
                ResourceNodeSchema(
                    resource_type=node.resource_type,
                    abundance=node.abundance,
                    quality=node.quality,
                    accessibility=node.accessibility,
                    depletion_rate=node.depletion_rate,
                    current_reserves=node.current_reserves,
                    location=HexCoordinateSchema(
                        q=node.location.q, 
                        r=node.location.r, 
                        s=node.location.s
                    ) if node.location else None
                )
                for node in (region.resource_nodes or [])
            ],
            created_at=region.created_at,
            updated_at=region.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get region: {str(e)}")

@router.put("/{region_id}", response_model=RegionResponseSchema)
async def update_region(
    region_id: UUID,
    update_data: RegionUpdateSchema,
    region_service: RegionService,
    event_service: EventService
):
    """Update an existing region"""
    try:
        # Convert update schema to dict (using strings per Bible)
        updates = {}
        if update_data.name is not None:
            updates["name"] = update_data.name
        if update_data.description is not None:
            updates["description"] = update_data.description
        if update_data.region_type is not None:
            updates["region_type"] = update_data.region_type.value if hasattr(update_data.region_type, 'value') else str(update_data.region_type)
        if update_data.population is not None:
            updates["population"] = update_data.population
        
        updated_region = await asyncio.to_thread(region_service.update_region, region_id, updates)
        
        # Create business event for infrastructure to dispatch
        try:
            event = event_service.create_region_updated_event(updated_region)
            logger.info(f"Region updated event created: {event}")
        except Exception as e:
            logger.warning(f"Failed to create region updated event: {e}")
        
        return RegionResponseSchema(
            id=updated_region.id,
            name=updated_region.name,
            description=updated_region.description,
            region_type=updated_region.region_type,
            dominant_biome=updated_region.profile.dominant_biome,
            climate=updated_region.profile.climate.value,
            population=updated_region.population,
            danger_level=updated_region.danger_level.value,
            continent_id=updated_region.continent_id,
            hex_coordinates=updated_region.hex_coordinates,
            resource_nodes=updated_region.resource_nodes or []
        )
    except Exception as e:
        logger.error(f"Error updating region {region_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{region_id}")
async def delete_region(
    region_id: UUID,
    region_service: RegionService,
    event_service: EventService
):
    """Delete a region"""
    try:
        success = await asyncio.to_thread(region_service.delete_region, region_id)
        
        if success:
            # Create business event for infrastructure to dispatch
            try:
                event = event_service.create_region_deleted_event(region_id)
                logger.info(f"Region deleted event created: {event}")
            except Exception as e:
                logger.warning(f"Failed to create region deleted event: {e}")
            
            return JSONResponse(status_code=204, content={"message": "Region deleted successfully"})
        else:
            raise HTTPException(status_code=404, detail="Region not found")
    except Exception as e:
        logger.error(f"Error deleting region {region_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search/name", response_model=List[RegionResponseSchema])
async def search_regions_by_name(
    region_service: RegionService,
    q: str = Query(..., description="Search term for region name"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results")
):
    """Search regions by name"""
    try:
        regions = await asyncio.to_thread(region_service.search_regions_by_name, q)
        
        # Apply limit
        limited_regions = regions[:limit]
        
        return [
            RegionResponseSchema(
                id=region.id,
                name=region.name,
                description=region.description,
                region_type=region.region_type,
                dominant_biome=region.profile.dominant_biome,
                climate=region.profile.climate.value,
                population=region.population,
                danger_level=region.danger_level.value,
                continent_id=region.continent_id,
                hex_coordinates=region.hex_coordinates,
                resource_nodes=region.resource_nodes or []
            )
            for region in limited_regions
        ]
    except Exception as e:
        logger.error(f"Error searching regions by name '{q}': {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/population", response_model=Dict[str, Any])
async def get_population_analytics(
    region_service: RegionService,
    continent_id: Optional[UUID] = Query(None, description="Filter by continent")
):
    """Get population analytics across regions"""
    try:
        # Get regions (optionally filtered by continent)
        if continent_id:
            regions = await asyncio.to_thread(region_service.get_regions_by_continent, continent_id)
        else:
            regions = await asyncio.to_thread(region_service.get_regions)
        
        if not regions:
            return {
                "total_population": 0,
                "average_population": 0,
                "population_by_region_type": {},
                "population_by_biome": {},
                "most_populated_region": None,
                "least_populated_region": None,
                "total_regions": 0
            }
        
        # Calculate analytics
        total_population = sum(r.population for r in regions)
        avg_population = total_population / len(regions)
        
        # Group by region type (strings per Bible)
        by_region_type = {}
        for region in regions:
            region_type = region.region_type
            if region_type not in by_region_type:
                by_region_type[region_type] = {"count": 0, "total_population": 0}
            by_region_type[region_type]["count"] += 1
            by_region_type[region_type]["total_population"] += region.population
        
        # Group by biome (strings per Bible)
        by_biome = {}
        for region in regions:
            biome = region.profile.dominant_biome
            if biome not in by_biome:
                by_biome[biome] = {"count": 0, "total_population": 0}
            by_biome[biome]["count"] += 1
            by_biome[biome]["total_population"] += region.population
        
        # Find extremes
        most_populated = max(regions, key=lambda r: r.population)
        least_populated = min(regions, key=lambda r: r.population)
        
        return {
            "total_population": total_population,
            "average_population": round(avg_population, 2),
            "population_by_region_type": by_region_type,
            "population_by_biome": by_biome,
            "most_populated_region": {
                "id": str(most_populated.id),
                "name": most_populated.name,
                "population": most_populated.population
            },
            "least_populated_region": {
                "id": str(least_populated.id),
                "name": least_populated.name,
                "population": least_populated.population
            },
            "total_regions": len(regions)
        }
    except Exception as e:
        logger.error(f"Error getting population analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get population analytics")

# ============================================================================
# PROCEDURAL GENERATION ENDPOINTS
# ============================================================================

@router.post("/generate/world", response_model=Dict[str, Any])
async def generate_world(
    num_continents: int = Query(3, ge=1, le=10, description="Number of continents to generate"),
    seed: Optional[int] = Query(None, description="Generation seed for reproducible results"),
    db: Session = Depends(get_db_session)
):
    """Generate a complete world with multiple continents"""
    try:
        # Import here to avoid circular imports
        from backend.systems.world_generation import WorldGenerator, WorldGenerationConfig
        
        generator = WorldGenerator(seed=seed)
        
        # Generate world using the new single-continent approach
        config = WorldGenerationConfig()
        world_result = generator.generate_world(config=config, world_name="Generated World")
        
        # Store the main continent and islands in database
        continent_repo = get_continent_repository(db)
        region_repo = get_region_repository(db)
        
        created_continents = []
        
        # Store main continent
        main_continent_entity = continent_repo.create_continent(
            name=world_result.main_continent.name,
            description=world_result.main_continent.description,
            generation_seed=world_result.seed_used
        )
        created_continents.append(main_continent_entity)
        
        # Store islands
        for island in world_result.islands:
            island_entity = continent_repo.create_continent(
                name=island.name,
                description=island.description,
                generation_seed=world_result.seed_used
            )
            created_continents.append(island_entity)
        
        # Store regions
        created_regions = []
        for region_metadata in world_result.all_regions:
            # Find the appropriate continent for this region
            continent_id = main_continent_entity.id  # Default to main continent
            
            region_entity = region_repo.create_region(
                name=region_metadata.name,
                description=region_metadata.description,
                continent_id=str(continent_id),
                biome_type=region_metadata.profile.dominant_biome,
                hex_q=region_metadata.center_coordinate.q,
                hex_r=region_metadata.center_coordinate.r,
                hex_s=region_metadata.center_coordinate.s,
                total_population=region_metadata.population
            )
            created_regions.append(region_entity)
        
        # Broadcast update
        await ws_manager.broadcast_region_update({
            "action": "world_generated",
            "continents_count": len(created_continents),
            "regions_count": len(created_regions),
            "seed": world_result.seed_used
        })
        
        return {
            "success": True,
            "continents_created": len(created_continents),
            "regions_created": len(created_regions),
            "generation_time": world_result.generation_time,
            "seed_used": world_result.seed_used,
            "generation_stats": world_result.generation_stats
        }
        
    except Exception as e:
        logger.error(f"Error generating world: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate world: {str(e)}")

@router.post("/generate/continent", response_model=Dict[str, Any])
async def generate_continent(
    name: str = Query(..., description="Name for the new continent"),
    size_min: int = Query(50, ge=10, le=500, description="Minimum number of regions"),
    size_max: int = Query(150, ge=10, le=500, description="Maximum number of regions"),
    seed: Optional[int] = Query(None, description="Generation seed"),
    db: Session = Depends(get_db_session)
):
    """Generate a single continent with regions"""
    try:
        # Import here to avoid circular imports
        from backend.systems.world_generation import WorldGenerator, WorldGenerationConfig
        
        generator = WorldGenerator(seed=seed)
        
        # Create config for continent generation
        config = WorldGenerationConfig()
        config.main_continent_size = (size_min, size_max)
        config.island_count = 0  # Just generate the main continent
        
        # Generate the continent
        continent_size = random.randint(size_min, size_max)
        continent_metadata = generator._generate_continent(
            name=name,
            size=continent_size,
            config=config,
            is_main_landmass=True
        )
        
        # Store in database
        continent_repo = get_continent_repository(db)
        region_repo = get_region_repository(db)
        
        continent_entity = continent_repo.create_continent(
            name=continent_metadata.name,
            description=continent_metadata.description,
            generation_seed=generator.seed
        )
        
        # Store regions
        created_regions = []
        for region_metadata in continent_metadata.regions:
            region_entity = region_repo.create_region(
                name=region_metadata.name,
                description=region_metadata.description,
                continent_id=str(continent_entity.id),
                biome_type=region_metadata.profile.dominant_biome,
                hex_q=region_metadata.center_coordinate.q,
                hex_r=region_metadata.center_coordinate.r,
                hex_s=region_metadata.center_coordinate.s,
                total_population=region_metadata.population
            )
            created_regions.append(region_entity)
        
        # Broadcast update
        await ws_manager.broadcast_region_update({
            "action": "continent_generated",
            "continent_id": str(continent_entity.id),
            "regions_count": len(created_regions)
        })
        
        return {
            "success": True,
            "continent_id": str(continent_entity.id),
            "continent_name": continent_entity.name,
            "regions_created": len(created_regions),
            "seed_used": generator.seed
        }
        
    except Exception as e:
        logger.error(f"Error generating continent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate continent: {str(e)}")

# ============================================================================
# BIOME ADJACENCY VALIDATION ENDPOINTS
# ============================================================================

@router.post("/validate/biome-adjacency", response_model=Dict[str, Any])
async def validate_biome_adjacency_endpoint(
    region1_id: UUID = Query(..., description="First region ID"),
    region2_id: UUID = Query(..., description="Second region ID"),
    db: Session = Depends(get_db_session)
):
    """Validate if two regions can be adjacent based on their biomes"""
    try:
        region_repo = get_region_repository(db)
        
        region1 = region_repo.get_by_id(region1_id)
        region2 = region_repo.get_by_id(region2_id)
        
        if not region1:
            raise HTTPException(status_code=404, detail=f"Region {region1_id} not found")
        if not region2:
            raise HTTPException(status_code=404, detail=f"Region {region2_id} not found")
        
        # Use biome placement engine for validation
        from backend.infrastructure.world_generation_config import BiomeConfigManager
        from backend.systems.world_generation.algorithms.biome_placement import BiomePlacementEngine
        
        biome_config = BiomeConfigManager()
        biome_engine = BiomePlacementEngine(biome_config)
        
        is_valid = biome_engine._is_valid_biome_transition(
            region1.biome_type, 
            region2.biome_type
        )
        
        return {
            "valid": is_valid,
            "region1": {
                "id": str(region1.id),
                "name": region1.name,
                "biome": region1.biome_type.value
            },
            "region2": {
                "id": str(region2.id),
                "name": region2.name,
                "biome": region2.biome_type.value
            },
            "reason": "Biomes are compatible" if is_valid else "Biomes are not compatible for adjacency"
        }
        
    except Exception as e:
        logger.error(f"Error validating biome adjacency: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate biome adjacency: {str(e)}")

@router.get("/biomes/adjacency-rules", response_model=Dict[str, List[str]])
async def get_biome_adjacency_rules():
    """Get all biome adjacency rules"""
    try:
        from backend.infrastructure.world_generation_config import BiomeConfigManager
        
        biome_config = BiomeConfigManager()
        adjacency_rules = {}
        
        # Get adjacency rules for each biome
        for biome_type in BiomeType:
            adjacent_biomes = biome_config.get_adjacent_biomes(biome_type)
            adjacency_rules[biome_type.value] = [b.value for b in adjacent_biomes]
        
        return adjacency_rules
        
    except Exception as e:
        logger.error(f"Error getting biome adjacency rules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get biome adjacency rules: {str(e)}")

# ============================================================================
# WEBSOCKET ENDPOINT FOR REAL-TIME UPDATES
# ============================================================================

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time region updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            
            # Echo back for connection testing
            await websocket.send_json({
                "type": "echo",
                "message": f"Received: {data}"
            })
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "region-api",
        "version": "1.0.0"
    }

@router.get("/stats", response_model=Dict[str, Any])
async def get_region_statistics(
    db: Session = Depends(get_db_session)
):
    """Get comprehensive region system statistics"""
    try:
        region_repo = get_region_repository(db)
        continent_repo = get_continent_repository(db)
        
        region_stats = region_repo.get_statistics()
        continents = continent_repo.get_all()
        
        return {
            "regions": region_stats,
            "continents": {
                "total_continents": len(continents),
                "total_area": sum(c.total_area_square_km for c in continents),
                "average_area": sum(c.total_area_square_km for c in continents) / len(continents) if continents else 0
            },
            "websocket_connections": len(ws_manager.active_connections)
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# ============================================================================
# REGION POPULATION ENDPOINTS (from API contracts)
# ============================================================================

@router.get("/{region_id}/population", response_model=Dict[str, Any])
async def get_region_population(
    region_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Get detailed population data for a region per API contracts"""
    try:
        region_repo = get_region_repository(db)
        region = region_repo.get_by_id(region_id)
        
        if not region:
            raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        
        # Calculate detailed population metrics
        population_data = {
            "region_id": str(region_id),
            "total_population": region.population,
            "population_density": region.population_density if hasattr(region, 'population_density') else 0.0,
            "growth_rate": 0.02,  # Default 2% growth rate
            "demographics": {
                "age_distribution": {
                    "children": 0.25,
                    "adults": 0.65,
                    "elderly": 0.10
                },
                "occupations": {
                    "agriculture": 0.40,
                    "crafts": 0.25,
                    "trade": 0.15,
                    "military": 0.10,
                    "nobility": 0.05,
                    "clergy": 0.05
                }
            },
            "settlements": region.major_settlements if hasattr(region, 'major_settlements') else [],
            "urbanization_level": min(region.population / 10000, 1.0) if region.population > 0 else 0.0,
            "last_updated": region.updated_at.isoformat() if region.updated_at else None
        }
        
        return population_data
        
    except Exception as e:
        logger.error(f"Error getting region population {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get population data: {str(e)}")


@router.get("/{region_id}/economy", response_model=Dict[str, Any])
async def get_region_economy(
    region_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Get economic data for a region per API contracts"""
    try:
        region_repo = get_region_repository(db)
        region = region_repo.get_by_id(region_id)
        
        if not region:
            raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        
        # Calculate total resource value
        total_resource_value = 0.0
        resource_breakdown = {}
        if region.resource_nodes:
            for resource in region.resource_nodes:
                value = resource.calculate_value()
                total_resource_value += value
                resource_breakdown[resource.resource_type] = {
                    "abundance": resource.abundance,
                    "quality": resource.quality,
                    "accessibility": resource.accessibility,
                    "estimated_value": value
                }
        
        # Calculate economic metrics
        wealth_level = getattr(region, 'wealth_level', 0.5)
        base_gdp = region.population * wealth_level * 100  # Simple GDP calculation
        
        economy_data = {
            "region_id": str(region_id),
            "wealth_level": wealth_level,
            "estimated_gdp": base_gdp,
            "gdp_per_capita": base_gdp / max(region.population, 1),
            "primary_industries": getattr(region, 'primary_industries', ["agriculture"]),
            "resources": {
                "total_value": total_resource_value,
                "breakdown": resource_breakdown
            },
            "trade": {
                "trade_routes": getattr(region, 'trade_routes', []),
                "trade_volume": wealth_level * region.population * 0.1,
                "import_export_balance": 0.0  # Placeholder
            },
            "infrastructure": {
                "development_level": wealth_level,
                "transportation": "basic" if wealth_level < 0.5 else "developed",
                "communication": "limited" if wealth_level < 0.7 else "good"
            },
            "market_data": {
                "stability": getattr(region, 'political_stability', 0.5),
                "inflation_rate": 0.03,  # Default 3%
                "unemployment_rate": max(0.1 - wealth_level * 0.1, 0.01)
            },
            "last_updated": region.updated_at.isoformat() if region.updated_at else None
        }
        
        return economy_data
        
    except Exception as e:
        logger.error(f"Error getting region economy {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get economic data: {str(e)}")


# ============================================================================
# ADDITIONAL ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/{region_id}/analytics", response_model=Dict[str, Any])
async def get_region_analytics(
    region_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Get comprehensive analytics for a region"""
    try:
        region_repo = get_region_repository(db)
        region = region_repo.get_by_id(region_id)
        
        if not region:
            raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        
        # Combine population and economic data with additional analytics
        analytics_data = {
            "region_overview": {
                "id": str(region_id),
                "name": region.name,
                "type": region.region_type,
                "biome": region.profile.dominant_biome if region.profile else "unknown",
                "climate": region.profile.climate.value if region.profile and region.profile.climate else "unknown",
                "danger_level": region.danger_level.value if region.danger_level else 2,
                "area_km2": region.area_square_km
            },
            "habitability": {
                "score": region.profile.calculate_habitability() if region.profile else 0.5,
                "factors": {
                    "soil_fertility": region.profile.soil_fertility if region.profile else 0.5,
                    "water_availability": region.profile.water_availability if region.profile else 0.5,
                    "climate_suitability": 0.8 if region.profile and region.profile.climate.value == "temperate" else 0.6
                }
            },
            "strategic_value": {
                "military": min(region.area_square_km / 1000, 1.0),
                "economic": getattr(region, 'wealth_level', 0.5),
                "political": getattr(region, 'political_stability', 0.5),
                "resource": min(len(region.resource_nodes) * 0.2, 1.0) if region.resource_nodes else 0.0
            },
            "development_potential": {
                "infrastructure": getattr(region, 'wealth_level', 0.5),
                "population_growth": min(region.population / 50000, 1.0) if region.population > 0 else 0.1,
                "resource_exploitation": 0.7 if region.resource_nodes else 0.2,
                "connectivity": len(getattr(region, 'neighboring_region_ids', [])) * 0.1
            }
        }
        
        return analytics_data
        
    except Exception as e:
        logger.error(f"Error getting region analytics {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}") 