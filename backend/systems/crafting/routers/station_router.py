"""
Station Router

FastAPI router for crafting station management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime

from backend.systems.crafting.schemas import (
    StationResponseSchema,
    StationListResponseSchema,
    StationSearchSchema,
    StationUseSchema,
    StationUseResponseSchema,
    StationStatusSchema,
    StationUpgradeSchema,
    StationUpgradeResponseSchema,
    StationCreateSchema,
    StationUpdateSchema,
    StationMaintenanceSchema,
    StationMaintenanceResponseSchema
)
from backend.systems.crafting.repositories import StationRepository
from backend.systems.crafting.services import StationService

router = APIRouter(prefix="/stations", tags=["stations"])

# Dependency to get station repository
def get_station_repository() -> StationRepository:
    """Get station repository instance."""
    return StationRepository()

# Dependency to get station service
def get_station_service() -> StationService:
    """Get station service instance."""
    return StationService()

@router.get("/", response_model=StationListResponseSchema)
async def list_stations(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    station_type: Optional[str] = Query(None, description="Filter by station type"),
    location_id: Optional[str] = Query(None, description="Filter by location"),
    character_id: Optional[str] = Query(None, description="Character ID for availability check"),
    is_public_only: bool = Query(False, description="Show only public stations"),
    is_available_only: bool = Query(False, description="Show only available stations"),
    repository: StationRepository = Depends(get_station_repository)
):
    """
    List all crafting stations with optional filtering and pagination.
    
    Returns a paginated list of stations that can be filtered by various criteria.
    """
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get stations based on filters
        if character_id and not is_public_only:
            stations = repository.get_available_stations(character_id, location_id)
        elif station_type:
            stations = repository.get_by_type(station_type)
        elif location_id:
            stations = repository.get_by_location(location_id)
        elif is_public_only:
            stations = repository.get_public_stations(location_id)
        else:
            stations = repository.get_all(limit=per_page, offset=offset)
        
        # Filter by availability if requested
        if is_available_only:
            stations = [s for s in stations if s.is_available(character_id)]
        
        # Apply pagination to filtered results
        total = len(stations)
        paginated_stations = stations[offset:offset + per_page]
        
        # Convert to response schemas with computed fields
        station_responses = []
        for station in paginated_stations:
            response = StationResponseSchema.from_orm(station)
            # Add computed fields
            response.efficiency_multiplier = station.get_efficiency_multiplier()
            response.total_quality_bonus = station.get_quality_bonus()
            response.is_available = station.is_available(character_id)
            station_responses.append(response)
        
        return StationListResponseSchema(
            stations=station_responses,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stations: {str(e)}"
        )

@router.get("/{station_id}", response_model=StationResponseSchema)
async def get_station(
    station_id: uuid.UUID,
    character_id: Optional[str] = Query(None, description="Character ID for availability check"),
    repository: StationRepository = Depends(get_station_repository)
):
    """
    Get detailed information about a specific crafting station.
    
    Returns complete station details including current status and availability.
    """
    try:
        station = repository.get_by_id(str(station_id))
        
        if not station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Station with ID {station_id} not found"
            )
        
        response = StationResponseSchema.from_orm(station)
        # Add computed fields
        response.efficiency_multiplier = station.get_efficiency_multiplier()
        response.total_quality_bonus = station.get_quality_bonus()
        response.is_available = station.is_available(character_id)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve station: {str(e)}"
        )

@router.post("/{station_id}/use", response_model=StationUseResponseSchema)
async def use_station(
    station_id: uuid.UUID,
    use_request: StationUseSchema,
    service: StationService = Depends(get_station_service),
    repository: StationRepository = Depends(get_station_repository)
):
    """
    Start using a crafting station for a specific operation.
    
    This reserves the station for the character and returns session information.
    """
    try:
        # Check if station exists and is available
        station = repository.get_by_id(str(station_id))
        if not station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Station with ID {station_id} not found"
            )
        
        if not station.is_available(use_request.character_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Station is not available for use"
            )
        
        # TODO: Implement station usage logic in StationService
        # For now, create a mock session
        session_id = f"session_{station_id}_{use_request.character_id}_{int(datetime.now().timestamp())}"
        
        return StationUseResponseSchema(
            station_id=station_id,
            character_id=use_request.character_id,
            session_id=session_id,
            start_time=datetime.now(),
            estimated_end_time=datetime.now() if not use_request.duration else None,
            efficiency_multiplier=station.get_efficiency_multiplier(),
            quality_bonus=station.get_quality_bonus(),
            is_active=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to use station: {str(e)}"
        )

@router.get("/{station_id}/status", response_model=StationStatusSchema)
async def get_station_status(
    station_id: uuid.UUID,
    repository: StationRepository = Depends(get_station_repository)
):
    """
    Get the current status and availability of a crafting station.
    
    Returns information about current usage, queue, and availability.
    """
    try:
        station = repository.get_by_id(str(station_id))
        
        if not station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Station with ID {station_id} not found"
            )
        
        # TODO: Implement real-time status tracking
        # For now, return basic status
        return StationStatusSchema(
            station_id=station_id,
            is_active=station.is_active,
            is_available=station.is_available(),
            current_users=0,  # TODO: Get from session tracking
            max_capacity=station.capacity,
            active_sessions=[],  # TODO: Get active sessions
            queue_length=0,  # TODO: Get queue length
            estimated_wait_time=0  # TODO: Calculate wait time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get station status: {str(e)}"
        )

@router.post("/{station_id}/upgrade", response_model=StationUpgradeResponseSchema)
async def upgrade_station(
    station_id: uuid.UUID,
    upgrade_request: StationUpgradeSchema,
    repository: StationRepository = Depends(get_station_repository)
):
    """
    Upgrade a crafting station.
    
    Supports upgrading level, efficiency, quality bonus, or capacity.
    """
    try:
        station = repository.get_by_id(str(station_id))
        
        if not station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Station with ID {station_id} not found"
            )
        
        # Check ownership or permissions
        if station.owner_id and station.owner_id != upgrade_request.character_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to upgrade this station"
            )
        
        # Perform the upgrade
        upgrade_result = station.upgrade(upgrade_request.upgrade_type)
        
        if upgrade_result["success"]:
            # Update in database
            repository.update(str(station_id), **{
                upgrade_request.upgrade_type: upgrade_result["new_value"]
            })
        
        return StationUpgradeResponseSchema(
            station_id=station_id,
            upgrade_type=upgrade_request.upgrade_type,
            success=upgrade_result["success"],
            old_value=upgrade_result.get("old_value"),
            new_value=upgrade_result.get("new_value"),
            materials_consumed=upgrade_request.materials,
            cost=upgrade_request.materials,  # TODO: Calculate actual cost
            message=upgrade_result.get("error", "Upgrade successful")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade station: {str(e)}"
        )

@router.post("/{station_id}/maintenance", response_model=StationMaintenanceResponseSchema)
async def maintain_station(
    station_id: uuid.UUID,
    maintenance_request: StationMaintenanceSchema,
    repository: StationRepository = Depends(get_station_repository)
):
    """
    Perform maintenance on a crafting station.
    
    Maintenance can restore efficiency, durability, and other properties.
    """
    try:
        station = repository.get_by_id(str(station_id))
        
        if not station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Station with ID {station_id} not found"
            )
        
        # Check ownership or permissions
        if station.owner_id and station.owner_id != maintenance_request.character_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to maintain this station"
            )
        
        # TODO: Implement maintenance logic
        # For now, return success response
        return StationMaintenanceResponseSchema(
            station_id=station_id,
            maintenance_performed=True,
            materials_consumed=maintenance_request.materials,
            efficiency_restored=0.1,  # 10% efficiency restored
            durability_restored=0.2,  # 20% durability restored
            next_maintenance_due=None,  # TODO: Calculate next maintenance
            message="Maintenance completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to maintain station: {str(e)}"
        )

@router.post("/", response_model=StationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_station(
    station_data: StationCreateSchema,
    repository: StationRepository = Depends(get_station_repository)
):
    """
    Create a new crafting station.
    
    This endpoint is typically used by administrators or for station construction.
    """
    try:
        # Convert schema to dict for repository
        station_dict = station_data.dict()
        
        # Create the station
        station = repository.create(**station_dict)
        
        response = StationResponseSchema.from_orm(station)
        # Add computed fields
        response.efficiency_multiplier = station.get_efficiency_multiplier()
        response.total_quality_bonus = station.get_quality_bonus()
        response.is_available = station.is_available()
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create station: {str(e)}"
        )

@router.put("/{station_id}", response_model=StationResponseSchema)
async def update_station(
    station_id: uuid.UUID,
    station_data: StationUpdateSchema,
    repository: StationRepository = Depends(get_station_repository)
):
    """
    Update an existing crafting station.
    
    Only provided fields will be updated, others remain unchanged.
    """
    try:
        # Check if station exists
        existing_station = repository.get_by_id(str(station_id))
        if not existing_station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Station with ID {station_id} not found"
            )
        
        # Update only provided fields
        update_data = station_data.dict(exclude_unset=True)
        updated_station = repository.update(str(station_id), **update_data)
        
        response = StationResponseSchema.from_orm(updated_station)
        # Add computed fields
        response.efficiency_multiplier = updated_station.get_efficiency_multiplier()
        response.total_quality_bonus = updated_station.get_quality_bonus()
        response.is_available = updated_station.is_available()
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update station: {str(e)}"
        )

@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_station(
    station_id: uuid.UUID,
    repository: StationRepository = Depends(get_station_repository)
):
    """
    Delete a crafting station.
    
    This will permanently remove the station from the system.
    """
    try:
        success = repository.delete(str(station_id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Station with ID {station_id} not found"
            )
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete station: {str(e)}"
        ) 