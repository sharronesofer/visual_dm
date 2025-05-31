"""
Region System API Router

Comprehensive API endpoints for region system including:
- World metadata and continent management
- Region CRUD operations and generation
- Biome adjacency validation
- Real-time updates and WebSocket integration
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.infrastructure.shared.database import get_db_session
from backend.infrastructure.shared.exceptions import (
    RegionNotFoundError,
    RegionValidationError,
    RegionConflictError,
    RepositoryError
)
# Import models module directly to avoid circular import issues
import backend.systems.region.models as region_models
RegionMetadata = region_models.RegionMetadata
ContinentMetadata = region_models.ContinentMetadata
RegionCreateSchema = region_models.RegionCreateSchema
RegionUpdateSchema = region_models.RegionUpdateSchema
RegionResponseSchema = region_models.RegionResponseSchema
ContinentCreateSchema = region_models.ContinentCreateSchema
ContinentResponseSchema = region_models.ContinentResponseSchema
HexCoordinateSchema = region_models.HexCoordinateSchema
BiomeType = region_models.BiomeType
RegionType = region_models.RegionType
ClimateType = region_models.ClimateType
DangerLevel = region_models.DangerLevel
from backend.systems.region.repositories.region_repository import (
    get_region_repository,
    get_continent_repository
)
# Import the new event service for cross-system integration
from backend.systems.region.services.event_service import get_region_event_service
from backend.systems.region.utils.worldgen import (
    EnhancedWorldGenerator,
    validate_biome_adjacency,
    generate_continent_with_validation,
    ContinentGenerationConfig,
    WorldGenerationResult
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/regions", tags=["regions"])

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
    db: Session = Depends(get_db_session)
):
    """Get comprehensive world metadata including continents and statistics"""
    try:
        continent_repo = get_continent_repository(db)
        region_repo = get_region_repository(db)
        
        # Get all continents
        continents = continent_repo.get_all()
        
        # Get region statistics
        region_stats = region_repo.get_statistics()
        
        # Calculate world-level statistics
        total_area = sum(c.total_area_square_km for c in continents)
        continent_count = len(continents)
        
        world_metadata = {
            "world_info": {
                "total_continents": continent_count,
                "total_area_square_km": total_area,
                "total_regions": region_stats.get("total_regions", 0),
                "total_population": region_stats.get("total_population", 0),
                "average_population_per_region": region_stats.get("average_population", 0)
            },
            "continents": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "description": c.description,
                    "area_square_km": c.total_area_square_km,
                    "political_situation": c.political_situation,
                    "region_count": len(c.region_ids) if hasattr(c, 'region_ids') else 0
                }
                for c in continents
            ],
            "biome_distribution": region_stats.get("biome_distribution", {}),
            "generation_info": {
                "supports_procedural_generation": True,
                "available_biomes": [biome.value for biome in BiomeType],
                "available_climates": [climate.value for climate in ClimateType],
                "danger_levels": [level.value for level in DangerLevel]
            }
        }
        
        return world_metadata
        
    except Exception as e:
        logger.error(f"Error getting world metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get world metadata: {str(e)}")

@router.get("/world/continents", response_model=List[ContinentResponseSchema])
async def list_continents(
    db: Session = Depends(get_db_session)
):
    """Get list of all continents"""
    try:
        continent_repo = get_continent_repository(db)
        continents = continent_repo.get_all()
        
        return [
            ContinentResponseSchema(
                id=c.id,
                name=c.name,
                description=c.description or "",
                total_area_square_km=c.total_area_square_km,
                political_situation=c.political_situation,
                region_count=len(c.region_ids) if hasattr(c, 'region_ids') else 0,
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
    db: Session = Depends(get_db_session)
):
    """Create a new continent"""
    try:
        continent_repo = get_continent_repository(db)
        
        continent = continent_repo.create_continent(
            name=continent_data.name,
            description=continent_data.description,
            generation_seed=continent_data.generation_seed
        )
        
        response = ContinentResponseSchema(
            id=continent.id,
            name=continent.name,
            description=continent.description or "",
            total_area_square_km=continent.total_area_square_km,
            political_situation=continent.political_situation,
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
        
    except RegionConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating continent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create continent: {str(e)}")

@router.get("/continents/{continent_id}", response_model=ContinentResponseSchema)
async def get_continent(
    continent_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Get continent by ID"""
    try:
        continent_repo = get_continent_repository(db)
        continent = continent_repo.get_by_id(continent_id)
        
        if not continent:
            raise HTTPException(status_code=404, detail=f"Continent {continent_id} not found")
        
        return ContinentResponseSchema(
            id=continent.id,
            name=continent.name,
            description=continent.description or "",
            total_area_square_km=continent.total_area_square_km,
            political_situation=continent.political_situation,
            region_count=len(continent.region_ids) if hasattr(continent, 'region_ids') else 0,
            created_at=continent.created_at,
            updated_at=continent.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting continent {continent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get continent: {str(e)}")

@router.get("/continents/{continent_id}/regions", response_model=List[RegionResponseSchema])
async def get_regions_by_continent(
    continent_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Get all regions in a continent"""
    try:
        region_repo = get_region_repository(db)
        regions = region_repo.get_by_continent(str(continent_id))
        
        return [
            RegionResponseSchema(
                id=r.id,
                name=r.name,
                description=r.description or "",
                region_type=RegionType(r.region_type),
                dominant_biome=BiomeType(r.dominant_biome),
                climate=ClimateType(r.climate),
                population=r.population,
                area_square_km=r.area_square_km,
                danger_level=DangerLevel(r.danger_level),
                exploration_status=r.exploration_status,
                continent_id=r.continent_id,
                center_coordinate=HexCoordinateSchema(q=r.center_hex_q or 0, r=r.center_hex_r or 0, s=0) if r.center_hex_q is not None else None,
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
    db: Session = Depends(get_db_session)
):
    """Create a new region"""
    try:
        region_repo = get_region_repository(db)
        event_service = get_region_event_service()
        
        region = region_repo.create_region(
            name=region_data.name,
            biome_type=region_data.dominant_biome.value,
            description=region_data.description,
            region_type=region_data.region_type.value,
            continent_id=str(region_data.continent_id) if region_data.continent_id else None,
            climate=region_data.climate.value,
            government_type=region_data.government_type,
            danger_level=region_data.danger_level.value
        )
        
        response = RegionResponseSchema(
            id=region.id,
            name=region.name,
            description=region.description or "",
            region_type=RegionType(region.region_type),
            dominant_biome=BiomeType(region.dominant_biome),
            climate=ClimateType(region.climate),
            population=region.population,
            area_square_km=region.area_square_km,
            danger_level=DangerLevel(region.danger_level),
            exploration_status=region.exploration_status,
            continent_id=region.continent_id,
            center_coordinate=HexCoordinateSchema(q=region.center_hex_q or 0, r=region.center_hex_r or 0, s=0) if region.center_hex_q is not None else None,
            created_at=region.created_at,
            updated_at=region.updated_at
        )
        
        # Dispatch region created event for cross-system integration
        try:
            region_metadata = region.to_metadata()
            await event_service.publish_region_created(region_metadata, created_by="api")
        except Exception as e:
            logger.warning(f"Failed to dispatch region created event: {e}")
        
        # Broadcast WebSocket update
        await ws_manager.broadcast_region_update({
            "action": "region_created",
            "region": response.dict()
        })
        
        return response
        
    except RegionConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating region: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create region: {str(e)}")

@router.get("/", response_model=List[RegionResponseSchema])
async def list_regions(
    continent_id: Optional[UUID] = Query(None, description="Filter by continent ID"),
    biome_type: Optional[BiomeType] = Query(None, description="Filter by biome type"),
    region_type: Optional[RegionType] = Query(None, description="Filter by region type"),
    name_filter: Optional[str] = Query(None, description="Filter by name (partial match)"),
    min_population: Optional[int] = Query(None, description="Minimum population"),
    max_population: Optional[int] = Query(None, description="Maximum population"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db_session)
):
    """List regions with optional filtering and pagination"""
    try:
        region_repo = get_region_repository(db)
        
        # Build filter parameters
        biome_types = [biome_type.value] if biome_type else None
        continent_id_str = str(continent_id) if continent_id else None
        
        regions, total = region_repo.search_regions(
            name_filter=name_filter,
            biome_types=biome_types,
            continent_id=continent_id_str,
            min_population=min_population,
            max_population=max_population,
            page=page,
            size=size
        )
        
        response_data = [
            RegionResponseSchema(
                id=r.id,
                name=r.name,
                description=r.description or "",
                region_type=RegionType(r.region_type),
                dominant_biome=BiomeType(r.dominant_biome),
                climate=ClimateType(r.climate),
                population=r.population,
                area_square_km=r.area_square_km,
                danger_level=DangerLevel(r.danger_level),
                exploration_status=r.exploration_status,
                continent_id=r.continent_id,
                center_coordinate=HexCoordinateSchema(q=r.center_hex_q or 0, r=r.center_hex_r or 0, s=0) if r.center_hex_q is not None else None,
                created_at=r.created_at,
                updated_at=r.updated_at
            )
            for r in regions
        ]
        
        # Add pagination metadata to headers
        return JSONResponse(
            content=[region.dict() for region in response_data],
            headers={
                "X-Total-Count": str(total),
                "X-Page": str(page),
                "X-Page-Size": str(size),
                "X-Total-Pages": str((total + size - 1) // size)
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing regions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list regions: {str(e)}")

@router.get("/{region_id}", response_model=RegionResponseSchema)
async def get_region(
    region_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Get region by ID"""
    try:
        region_repo = get_region_repository(db)
        region = region_repo.get_by_id(region_id)
        
        if not region:
            raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        
        return RegionResponseSchema(
            id=region.id,
            name=region.name,
            description=region.description or "",
            region_type=RegionType(region.region_type),
            dominant_biome=BiomeType(region.dominant_biome),
            climate=ClimateType(region.climate),
            population=region.population,
            area_square_km=region.area_square_km,
            danger_level=DangerLevel(region.danger_level),
            exploration_status=region.exploration_status,
            continent_id=region.continent_id,
            center_coordinate=HexCoordinateSchema(q=region.center_hex_q or 0, r=region.center_hex_r or 0, s=0) if region.center_hex_q is not None else None,
            created_at=region.created_at,
            updated_at=region.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get region: {str(e)}")

@router.put("/{region_id}", response_model=RegionResponseSchema)
async def update_region(
    region_id: UUID,
    region_data: RegionUpdateSchema,
    db: Session = Depends(get_db_session)
):
    """Update region by ID"""
    try:
        region_repo = get_region_repository(db)
        event_service = get_region_event_service()
        region = region_repo.get_by_id(region_id)
        
        if not region:
            raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        
        # Track changes for event dispatching
        update_data = region_data.dict(exclude_unset=True)
        old_values = {}
        new_values = {}
        changed_fields = list(update_data.keys())
        
        # Capture old values
        for field in changed_fields:
            if hasattr(region, field):
                old_values[field] = getattr(region, field)
        
        # Update fields
        for field, value in update_data.items():
            if hasattr(region, field):
                setattr(region, field, value)
                new_values[field] = value
        
        updated_region = region_repo.update(region)
        
        response = RegionResponseSchema(
            id=updated_region.id,
            name=updated_region.name,
            description=updated_region.description or "",
            region_type=RegionType(updated_region.region_type),
            dominant_biome=BiomeType(updated_region.dominant_biome),
            climate=ClimateType(updated_region.climate),
            population=updated_region.population,
            area_square_km=updated_region.area_square_km,
            danger_level=DangerLevel(updated_region.danger_level),
            exploration_status=updated_region.exploration_status,
            continent_id=updated_region.continent_id,
            center_coordinate=HexCoordinateSchema(q=updated_region.center_hex_q or 0, r=updated_region.center_hex_r or 0, s=0) if updated_region.center_hex_q is not None else None,
            created_at=updated_region.created_at,
            updated_at=updated_region.updated_at
        )
        
        # Dispatch region updated event for cross-system integration
        try:
            await event_service.publish_region_updated(
                region_id=updated_region.id,
                region_name=updated_region.name,
                changed_fields=changed_fields,
                old_values=old_values,
                new_values=new_values,
                continent_id=updated_region.continent_id,
                updated_by="api"
            )
        except Exception as e:
            logger.warning(f"Failed to dispatch region updated event: {e}")
        
        # Broadcast WebSocket update
        await ws_manager.broadcast_region_update({
            "action": "region_updated",
            "region": response.dict()
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update region: {str(e)}")

@router.delete("/{region_id}", status_code=204)
async def delete_region(
    region_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Delete region by ID"""
    try:
        region_repo = get_region_repository(db)
        event_service = get_region_event_service()
        region = region_repo.get_by_id(region_id)
        
        if not region:
            raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        
        # Capture region data for event before deletion
        region_name = region.name
        continent_id = region.continent_id
        backup_data = {
            "id": str(region.id),
            "name": region.name,
            "description": region.description,
            "region_type": region.region_type,
            "dominant_biome": region.dominant_biome,
            "continent_id": str(region.continent_id) if region.continent_id else None,
            "population": region.population,
            "area_square_km": region.area_square_km
        }
        
        # Delete the region
        region_repo.delete(region_id)
        
        # Dispatch region deleted event for cross-system integration
        try:
            await event_service.publish_region_deleted(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                deleted_by="api",
                backup_data=backup_data
            )
        except Exception as e:
            logger.warning(f"Failed to dispatch region deleted event: {e}")
        
        # Broadcast WebSocket update
        await ws_manager.broadcast_region_update({
            "action": "region_deleted",
            "region_id": str(region_id)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting region {region_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete region: {str(e)}")

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
        generator = EnhancedWorldGenerator(seed=seed)
        
        # Generate world
        world_result = generator.generate_world(num_continents=num_continents)
        
        # Save to database
        continent_repo = get_continent_repository(db)
        region_repo = get_region_repository(db)
        
        saved_continents = []
        saved_regions = []
        
        for continent_metadata in world_result.continents:
            # Create continent in database
            continent = continent_repo.create_continent(
                name=continent_metadata.name,
                description=continent_metadata.description,
                total_area_square_km=continent_metadata.total_area_square_km,
                political_situation=continent_metadata.political_situation,
                generation_seed=continent_metadata.generation_seed
            )
            saved_continents.append(continent)
            
            # Create regions for this continent
            continent_regions = [r for r in world_result.regions if r.continent_id == continent_metadata.id]
            for region_metadata in continent_regions:
                region = region_repo.create_region(
                    name=region_metadata.name,
                    biome_type=region_metadata.profile.dominant_biome.value,
                    description=region_metadata.description,
                    region_type=region_metadata.region_type.value,
                    continent_id=str(continent.id),
                    climate=region_metadata.profile.climate.value,
                    population=region_metadata.population,
                    area_square_km=region_metadata.area_square_km,
                    danger_level=region_metadata.danger_level.value
                )
                saved_regions.append(region)
        
        result = {
            "generation_info": {
                "seed_used": world_result.seed_used,
                "generation_time_seconds": world_result.generation_time,
                "continents_generated": len(saved_continents),
                "regions_generated": len(saved_regions)
            },
            "statistics": world_result.generation_stats,
            "continents": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "area_square_km": c.total_area_square_km
                }
                for c in saved_continents
            ]
        }
        
        # Broadcast update
        await ws_manager.broadcast_region_update({
            "action": "world_generated",
            "generation_info": result["generation_info"]
        })
        
        return result
        
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
        continent_result = generate_continent_with_validation(
            continent_name=name,
            size_range=(size_min, size_max),
            seed=seed
        )
        
        # Save to database
        continent_repo = get_continent_repository(db)
        region_repo = get_region_repository(db)
        
        # Create continent
        continent = continent_repo.create_continent(
            name=continent_result.continent.name,
            description=continent_result.continent.description,
            total_area_square_km=continent_result.continent.total_area_square_km,
            political_situation=continent_result.continent.political_situation,
            generation_seed=continent_result.continent.generation_seed
        )
        
        # Create regions
        saved_regions = []
        for region_metadata in continent_result.regions:
            region = region_repo.create_region(
                name=region_metadata.name,
                biome_type=region_metadata.profile.dominant_biome.value,
                description=region_metadata.description,
                region_type=region_metadata.region_type.value,
                continent_id=str(continent.id),
                climate=region_metadata.profile.climate.value,
                population=region_metadata.population,
                area_square_km=region_metadata.area_square_km,
                danger_level=region_metadata.danger_level.value
            )
            saved_regions.append(region)
        
        result = {
            "continent": {
                "id": str(continent.id),
                "name": continent.name,
                "description": continent.description,
                "area_square_km": continent.total_area_square_km,
                "regions_generated": len(saved_regions)
            },
            "generation_info": {
                "seed_used": continent_result.continent.generation_seed,
                "regions_count": len(saved_regions)
            }
        }
        
        # Broadcast update
        await ws_manager.broadcast_region_update({
            "action": "continent_generated",
            "continent": result["continent"]
        })
        
        return result
        
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
    """Validate if two regions have compatible biomes for adjacency"""
    try:
        region_repo = get_region_repository(db)
        
        region1 = region_repo.get_by_id(region1_id)
        region2 = region_repo.get_by_id(region2_id)
        
        if not region1:
            raise HTTPException(status_code=404, detail=f"Region {region1_id} not found")
        if not region2:
            raise HTTPException(status_code=404, detail=f"Region {region2_id} not found")
        
        # Convert to metadata for validation
        region1_metadata = region1.to_metadata()
        region2_metadata = region2.to_metadata()
        
        is_valid = validate_biome_adjacency(region1_metadata, region2_metadata)
        
        return {
            "valid": is_valid,
            "region1": {
                "id": str(region1.id),
                "name": region1.name,
                "biome": region1.dominant_biome
            },
            "region2": {
                "id": str(region2.id),
                "name": region2.name,
                "biome": region2.dominant_biome
            },
            "validation_details": {
                "biome1": region1.dominant_biome,
                "biome2": region2.dominant_biome,
                "adjacency_allowed": is_valid
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating biome adjacency: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate biome adjacency: {str(e)}")

@router.get("/biomes/adjacency-rules", response_model=Dict[str, List[str]])
async def get_biome_adjacency_rules():
    """Get all biome adjacency rules"""
    try:
        generator = EnhancedWorldGenerator()
        adjacency_rules = {}
        
        for biome_type, adjacent_biomes in generator.biome_adjacency_rules.items():
            adjacency_rules[biome_type.value] = [b.value for b in adjacent_biomes]
        
        return adjacency_rules
        
    except Exception as e:
        logger.error(f"Error getting biome adjacency rules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get adjacency rules: {str(e)}")

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