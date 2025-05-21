"""
API endpoints for rumor system.

This module provides FastAPI endpoints for interacting with
the rumor system.
"""
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse

from backend.systems.rumor.models.rumor import RumorCategory, RumorSeverity
from backend.systems.rumor.services.rumor_service import RumorService
from backend.systems.rumor.schemas import (
    CreateRumorRequest, SpreadRumorRequest, EntityRumorsRequest, DecayRumorsRequest,
    RumorResponse, RumorListResponse, EntityRumorsResponse, RumorOperationResponse
)

router = APIRouter(prefix="/rumors", tags=["rumors"])

# Use the singleton pattern to get RumorService
async def get_rumor_service():
    """Dependency to get the RumorService singleton."""
    return await RumorService.get_instance_async()

@router.post("/", response_model=RumorResponse, status_code=201)
async def create_rumor(
    request: CreateRumorRequest,
    service: RumorService = Depends(get_rumor_service)
):
    """
    Create a new rumor.
    
    Args:
        request: The rumor creation details
        service: The rumor service (injected)
    
    Returns:
        The created rumor
    """
    try:
        rumor_id = await service.create_rumor(
            originator_id=request.originator_id,
            content=request.content,
            categories=request.categories,
            severity=request.severity,
            truth_value=request.truth_value
        )
        rumor = await service.get_rumor_details(rumor_id)
        if not rumor:
            raise HTTPException(status_code=500, detail="Rumor was created but could not be retrieved")
        return RumorResponse.model_validate(rumor.model_dump())
    except Exception as e:
        logger.error(f"Error creating rumor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{rumor_id}", response_model=RumorResponse)
async def get_rumor(
    rumor_id: str = Path(..., description="The ID of the rumor to retrieve"),
    service: RumorService = Depends(get_rumor_service)
):
    """
    Get a specific rumor by ID.
    
    Args:
        rumor_id: The ID of the rumor to retrieve
        service: The rumor service (injected)
    
    Returns:
        The rumor details
    """
    try:
        rumor = await service.get_rumor_details(rumor_id)
        if not rumor:
            raise HTTPException(status_code=404, detail=f"Rumor {rumor_id} not found")
        return RumorResponse.model_validate(rumor.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving rumor {rumor_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=RumorListResponse)
async def list_rumors(
    entity_id: Optional[str] = Query(None, description="Filter rumors by entity who has heard them"),
    category: Optional[str] = Query(None, description="Filter rumors by category"),
    min_believability: Optional[float] = Query(None, description="Filter rumors by minimum believability"),
    limit: int = Query(10, description="Limit the number of results"),
    service: RumorService = Depends(get_rumor_service)
):
    """
    List rumors with optional filtering.
    
    Args:
        entity_id: Optional filter by entity who has heard the rumor
        category: Optional filter by rumor category
        min_believability: Optional filter by minimum believability
        limit: Maximum number of rumors to return
        service: The rumor service (injected)
    
    Returns:
        List of rumors matching the criteria
    """
    try:
        if entity_id:
            # Get rumors for specific entity
            rumor_data = await service.get_rumor_context(
                entity_id=entity_id,
                num_rumors=limit,
                min_believability=min_believability if min_believability is not None else 0.0,
                categories=[RumorCategory(category)] if category else None
            )
            rumors = [item["rumor"] for item in rumor_data if "rumor" in item]
        else:
            # Get all rumors from repository and filter manually
            repository = service.repository
            all_rumors = await repository.get_all_rumors()
            
            # Apply filters
            filtered_rumors = all_rumors
            if category:
                try:
                    category_enum = RumorCategory(category)
                    filtered_rumors = [r for r in filtered_rumors if category_enum in r.categories]
                except ValueError:
                    logger.warning(f"Invalid category: {category}")
            
            rumors = filtered_rumors[:limit]
            
        return RumorListResponse(
            rumors=[RumorResponse.model_validate(r.model_dump()) for r in rumors],
            count=len(rumors),
            total=len(rumors)  # This should ideally be the total count before limit
        )
    except Exception as e:
        logger.error(f"Error listing rumors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/spread", response_model=RumorOperationResponse)
async def spread_rumor(
    request: SpreadRumorRequest,
    service: RumorService = Depends(get_rumor_service)
):
    """
    Spread a rumor from one entity to another.
    
    Args:
        request: The rumor spread details
        service: The rumor service (injected)
    
    Returns:
        Operation result
    """
    try:
        success = await service.spread_rumor(
            rumor_id=request.rumor_id,
            from_entity_id=request.from_entity_id,
            to_entity_id=request.to_entity_id,
            mutation_probability=request.mutation_probability,
            relationship_factor=request.relationship_factor,
            receiver_bias_factor=request.receiver_bias_factor
        )
        return RumorOperationResponse(
            success=success,
            message="Rumor spread successfully" if success else "Failed to spread rumor"
        )
    except Exception as e:
        logger.error(f"Error spreading rumor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entity/{entity_id}", response_model=EntityRumorsResponse)
async def get_entity_rumors(
    entity_id: str = Path(..., description="ID of the entity"),
    service: RumorService = Depends(get_rumor_service)
):
    """
    Get all rumors known to an entity.
    
    Args:
        entity_id: ID of the entity
        service: The rumor service
        
    Returns:
        List of rumors the entity has heard
    """
    rumors = service.get_rumors_by_entity(entity_id)
    
    # Convert to response format
    entity_rumors = []
    for rumor in rumors:
        content = rumor.get_current_content_for_entity(entity_id)
        believability = rumor.get_believability_for_entity(entity_id)
        
        if content and believability is not None:
            entity_rumors.append({
                "rumor_id": rumor.id,
                "content": content,
                "believability": believability,
                "categories": [cat.value for cat in rumor.categories],
                "severity": rumor.severity.value
            })
    
    response = EntityRumorsResponse(
        entity_id=entity_id,
        rumors=entity_rumors,
        count=len(entity_rumors)
    )
    
    return response

@router.post("/decay", response_model=RumorOperationResponse)
async def decay_rumors(
    days: int = Query(7, description="Days since last reinforcement to consider for decay"),
    service: RumorService = Depends(get_rumor_service)
):
    """
    Decay all rumors that haven't been reinforced recently.
    
    Args:
        days: Days since last reinforcement to apply decay
        service: The rumor service (injected)
    
    Returns:
        Operation result
    """
    try:
        await service.decay_all_rumors()
        return RumorOperationResponse(
            success=True,
            message=f"Rumor decay process completed"
        )
    except Exception as e:
        logger.error(f"Error decaying rumors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{rumor_id}", response_model=RumorOperationResponse)
async def delete_rumor(
    rumor_id: str = Path(..., description="The ID of the rumor to delete"),
    service: RumorService = Depends(get_rumor_service)
):
    """
    Delete a rumor.
    
    Args:
        rumor_id: The ID of the rumor to delete
        service: The rumor service (injected)
    
    Returns:
        Operation result
    """
    try:
        success = await service.repository.delete_rumor(rumor_id)
        return RumorOperationResponse(
            success=success,
            message=f"Rumor {rumor_id} deleted successfully" if success else f"Failed to delete rumor {rumor_id}"
        )
    except Exception as e:
        logger.error(f"Error deleting rumor {rumor_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 