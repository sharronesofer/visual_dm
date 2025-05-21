from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from typing import List, Dict, Any, Optional

from backend.systems.population.models import (
    POIPopulation,
    POIType,
    POIState,
    PopulationConfig,
    PopulationChangedEvent,
    PopulationChangeRequest,
    GlobalMultiplierRequest,
    BaseRateRequest
)
from backend.systems.population.service import population_service

router = APIRouter(prefix="/api/population", tags=["population"])

@router.get("/config", response_model=PopulationConfig)
async def get_population_config():
    """Get the global configuration for the population control system"""
    return population_service.config

@router.put("/config/global-multiplier", response_model=float)
async def set_global_multiplier(request: GlobalMultiplierRequest):
    """Set the global population multiplier"""
    return await population_service.set_global_multiplier(request.value)

@router.put("/config/base-rate", response_model=Dict[POIType, float])
async def set_base_rate(request: BaseRateRequest):
    """Set the base rate for a POI type"""
    return await population_service.set_base_rate(request.poi_type, request.value)

@router.get("/", response_model=List[POIPopulation])
async def get_all_populations():
    """Get all POI populations"""
    return await population_service.get_all_populations()

@router.get("/{poi_id}", response_model=POIPopulation)
async def get_population(poi_id: str):
    """Get population data for a specific POI"""
    population = await population_service.get_population(poi_id)
    if not population:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"POI population with id {poi_id} not found")
    return population

@router.post("/", response_model=POIPopulation, status_code=status.HTTP_201_CREATED)
async def create_population(population: POIPopulation):
    """Create population data for a POI"""
    # Check if population with this ID already exists
    existing = await population_service.get_population(population.poi_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"POI population with id {population.poi_id} already exists"
        )
    return await population_service.create_population(population)

@router.put("/{poi_id}", response_model=POIPopulation)
async def update_population(poi_id: str, population: POIPopulation):
    """Update population data for a POI"""
    # Ensure the path parameter matches the POI ID in the request body
    if poi_id != population.poi_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Path parameter poi_id '{poi_id}' does not match request body poi_id '{population.poi_id}'"
        )
    
    updated = await population_service.update_population(poi_id, population)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"POI population with id {poi_id} not found"
        )
    return updated

@router.patch("/{poi_id}/population", response_model=POIPopulation)
async def change_population(poi_id: str, request: PopulationChangeRequest, background_tasks: BackgroundTasks):
    """Manually change the population of a POI"""
    population = await population_service.get_population(poi_id)
    if not population:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"POI population with id {poi_id} not found"
        )
    
    old_population = population.current_population
    population.current_population = request.new_population
    
    # Update record in background to prevent blocking
    background_tasks.add_task(population_service.update_population, poi_id, population)
    
    return population

@router.delete("/{poi_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_population(poi_id: str):
    """Delete population data for a POI"""
    deleted = await population_service.delete_population(poi_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"POI population with id {poi_id} not found"
        )
    return None

@router.post("/monthly-update", status_code=status.HTTP_202_ACCEPTED)
async def process_monthly_update(background_tasks: BackgroundTasks):
    """Process monthly population updates for all POIs"""
    # Always use a background task for long-running operations
    background_tasks.add_task(population_service.monthly_update)
    return {"message": "Monthly population update started in background"}

@router.get("/events", response_model=List[PopulationChangedEvent])
async def get_population_events(limit: int = 100):
    """Get recent population change events"""
    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be greater than 0"
        )
    return population_service.events[-limit:] if population_service.events else []

@router.get("/by-state/{state}", response_model=List[POIPopulation])
async def get_populations_by_state(state: POIState):
    """Get all POIs with a specific state"""
    all_pois = await population_service.get_all_populations()
    return [poi for poi in all_pois if poi.state == state]

@router.get("/by-type/{poi_type}", response_model=List[POIPopulation])
async def get_populations_by_type(poi_type: POIType):
    """Get all POIs of a specific type"""
    all_pois = await population_service.get_all_populations()
    return [poi for poi in all_pois if poi.poi_type == poi_type] 