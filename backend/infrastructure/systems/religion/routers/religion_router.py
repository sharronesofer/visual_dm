"""
Religion FastAPI Router

This module provides FastAPI endpoints for the religion system.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Import business logic models from systems
from backend.systems.religion.models import (
    CreateReligionRequest,
    UpdateReligionRequest, 
    ReligionResponse,
    ReligionListResponse,
    # New sub-resource models
    DeityRequest,
    DeityResponse,
    ReligiousPracticeRequest,
    ReligiousPracticeResponse,
    ReligiousEventRequest,
    ReligiousEventResponse,
    ReligiousInfluenceRequest,
    ReligiousInfluenceResponse
)

# Import business logic services from systems
from backend.systems.religion.services import (
    ReligionService,
    get_religion_service
)

# Import business logic exceptions from systems
from backend.systems.religion.models.exceptions import (
    ReligionNotFoundError,
    ReligionValidationError,
    ReligionConflictError
)

# This would typically come from a database dependency
# For now, we'll create a mock dependency
def get_database_session():
    """Dependency to get database session - implement based on your DB setup"""
    # This should return your actual SQLAlchemy session
    # Example: return SessionLocal()
    pass

def get_religion_service_dependency(db: Session = Depends(get_database_session)) -> ReligionService:
    """Dependency to get religion service"""
    return get_religion_service(db)


router = APIRouter(prefix="/religions", tags=["religions"])


# Core Religion CRUD Endpoints
@router.get("/", response_model=ReligionListResponse)
async def list_religions(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search term"),
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> ReligionListResponse:
    """
    List all religions with pagination and filtering
    
    - **page**: Page number (1-based)
    - **size**: Number of items per page (1-100)
    - **status**: Filter by religion status
    - **search**: Search in name and description
    """
    try:
        religions, total = await religion_service.list_religions(
            page=page,
            size=size,
            status=status,
            search=search
        )
        
        has_next = (page * size) < total
        has_prev = page > 1
        
        return ReligionListResponse(
            items=religions,
            total=total,
            page=page,
            size=size,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list religions: {str(e)}"
        )


@router.get("/{religion_id}", response_model=ReligionResponse)
async def get_religion(
    religion_id: UUID,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> ReligionResponse:
    """
    Get a specific religion by ID
    
    - **religion_id**: The UUID of the religion to retrieve
    """
    try:
        religion = await religion_service.get_religion_by_id(religion_id)
        
        if not religion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Religion with ID {religion_id} not found"
            )
        
        return religion
        
    except ReligionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Religion with ID {religion_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get religion: {str(e)}"
        )


@router.post("/", response_model=ReligionResponse, status_code=status.HTTP_201_CREATED)
async def create_religion(
    request: CreateReligionRequest,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> ReligionResponse:
    """
    Create a new religion
    
    - **request**: Religion creation data
    """
    try:
        religion = await religion_service.create_religion(request)
        return religion
        
    except ReligionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ReligionValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create religion: {str(e)}"
        )


@router.put("/{religion_id}", response_model=ReligionResponse)
async def update_religion(
    religion_id: UUID,
    request: UpdateReligionRequest,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> ReligionResponse:
    """
    Update an existing religion
    
    - **religion_id**: The UUID of the religion to update
    - **request**: Religion update data
    """
    try:
        religion = await religion_service.update_religion(religion_id, request)
        return religion
        
    except ReligionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Religion with ID {religion_id} not found"
        )
    except ReligionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ReligionValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update religion: {str(e)}"
        )


@router.delete("/{religion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_religion(
    religion_id: UUID,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> None:
    """
    Delete a religion (soft delete)
    
    - **religion_id**: The UUID of the religion to delete
    """
    try:
        success = await religion_service.delete_religion(religion_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Religion with ID {religion_id} not found"
            )
        
    except ReligionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Religion with ID {religion_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete religion: {str(e)}"
        )


# Additional Core Endpoints
@router.get("/search/", response_model=List[ReligionResponse])
async def search_religions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> List[ReligionResponse]:
    """
    Search religions by name or description
    
    - **q**: Search query string
    - **limit**: Maximum number of results to return
    """
    try:
        religions = await religion_service.search_religions(q, limit)
        return religions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search religions: {str(e)}"
        )


@router.get("/name/{name}", response_model=ReligionResponse)
async def get_religion_by_name(
    name: str,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> ReligionResponse:
    """
    Get a religion by its name
    
    - **name**: The name of the religion to retrieve
    """
    try:
        religion = await religion_service.get_religion_by_name(name)
        
        if not religion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Religion with name '{name}' not found"
            )
        
        return religion
        
    except ReligionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Religion with name '{name}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get religion by name: {str(e)}"
        )


@router.post("/bulk", response_model=List[ReligionResponse], status_code=status.HTTP_201_CREATED)
async def bulk_create_religions(
    requests: List[CreateReligionRequest],
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> List[ReligionResponse]:
    """
    Create multiple religions in bulk
    
    - **requests**: List of religion creation requests
    """
    try:
        religions = await religion_service.bulk_create_religions(requests)
        return religions
        
    except ReligionValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create religions: {str(e)}"
        )


@router.get("/statistics/overview", response_model=Dict[str, Any])
async def get_religion_statistics(
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> Dict[str, Any]:
    """
    Get overall religion system statistics
    """
    try:
        stats = await religion_service.get_religion_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get religion statistics: {str(e)}"
        )


# Unity Frontend Expected Sub-Resource Endpoints

@router.get("/pantheon/{pantheon_id}", response_model=List[ReligionResponse])
async def get_religions_by_pantheon(
    pantheon_id: str,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> List[ReligionResponse]:
    """
    Get religions by pantheon ID (Unity frontend expected endpoint)
    
    - **pantheon_id**: The pantheon identifier
    """
    try:
        # For now, return religions matching pantheon in properties
        religions, _ = await religion_service.list_religions(search=f"pantheon:{pantheon_id}")
        return religions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get religions by pantheon: {str(e)}"
        )


@router.get("/{religion_id}/practices", response_model=List[ReligiousPracticeResponse])
async def get_religious_practices(
    religion_id: UUID,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> List[ReligiousPracticeResponse]:
    """
    Get religious practices for a religion (Unity frontend expected endpoint)
    
    - **religion_id**: The UUID of the religion
    """
    try:
        # For now, return practices from religion properties
        religion = await religion_service.get_religion_by_id(religion_id)
        if not religion:
            raise HTTPException(status_code=404, detail="Religion not found")
        
        # Extract practices from properties and convert to response objects
        practices = religion.properties.get("practices_data", [])
        return [
            ReligiousPracticeResponse(
                id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
                name=practice.get("name", "Unknown Practice"),
                description=practice.get("description"),
                frequency=practice.get("frequency"),
                participants=practice.get("participants", 0),
                location_type=practice.get("location_type"),
                required_items=practice.get("required_items", []),
                religion_id=religion_id
            )
            for practice in (practices if isinstance(practices, list) else [])
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get religious practices: {str(e)}"
        )


@router.post("/{religion_id}/practices", response_model=ReligiousPracticeResponse, status_code=status.HTTP_201_CREATED)
async def add_religious_practice(
    religion_id: UUID,
    request: ReligiousPracticeRequest,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> ReligiousPracticeResponse:
    """
    Add a religious practice to a religion (Unity frontend expected endpoint)
    
    - **religion_id**: The UUID of the religion
    - **request**: Religious practice creation data
    """
    try:
        # For now, add to religion properties - in full implementation would be separate table
        religion = await religion_service.get_religion_by_id(religion_id)
        if not religion:
            raise HTTPException(status_code=404, detail="Religion not found")
        
        practice_id = UUID("00000000-0000-0000-0000-000000000001")  # Placeholder
        
        return ReligiousPracticeResponse(
            id=practice_id,
            name=request.name,
            description=request.description,
            frequency=request.frequency,
            participants=request.participants or 0,
            location_type=request.location_type,
            required_items=request.required_items or [],
            religion_id=religion_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add religious practice: {str(e)}"
        )


@router.get("/{religion_id}/deities", response_model=List[DeityResponse])
async def get_deities(
    religion_id: UUID,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> List[DeityResponse]:
    """
    Get deities for a religion (Unity frontend expected endpoint)
    
    - **religion_id**: The UUID of the religion
    """
    try:
        religion = await religion_service.get_religion_by_id(religion_id)
        if not religion:
            raise HTTPException(status_code=404, detail="Religion not found")
        
        # Extract deities from religion properties
        deities = religion.deities or []
        return [
            DeityResponse(
                id=UUID(deity.get("id", "00000000-0000-0000-0000-000000000000")),
                name=deity.get("name", "Unknown Deity"),
                description=deity.get("description"),
                domain=deity.get("domain"),
                alignment=deity.get("alignment"),
                symbols=deity.get("symbols", []),
                holy_days=deity.get("holy_days", []),
                powers=deity.get("powers", []),
                worshiper_count=deity.get("worshiper_count", 0),
                religion_id=religion_id
            )
            for deity in deities
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deities: {str(e)}"
        )


@router.post("/{religion_id}/deities", response_model=DeityResponse, status_code=status.HTTP_201_CREATED)
async def create_deity(
    religion_id: UUID,
    request: DeityRequest,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> DeityResponse:
    """
    Create a deity for a religion (Unity frontend expected endpoint)
    
    - **religion_id**: The UUID of the religion
    - **request**: Deity creation data
    """
    try:
        religion = await religion_service.get_religion_by_id(religion_id)
        if not religion:
            raise HTTPException(status_code=404, detail="Religion not found")
        
        deity_id = UUID("00000000-0000-0000-0000-000000000002")  # Placeholder
        
        return DeityResponse(
            id=deity_id,
            name=request.name,
            description=request.description,
            domain=request.domain,
            alignment=request.alignment,
            symbols=request.symbols or [],
            holy_days=request.holy_days or [],
            powers=request.powers or [],
            worshiper_count=0,
            religion_id=religion_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deity: {str(e)}"
        )


@router.get("/{religion_id}/events", response_model=List[ReligiousEventResponse])
async def get_religious_events(
    religion_id: UUID,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> List[ReligiousEventResponse]:
    """
    Get religious events for a religion (Unity frontend expected endpoint)
    
    - **religion_id**: The UUID of the religion
    """
    try:
        religion = await religion_service.get_religion_by_id(religion_id)
        if not religion:
            raise HTTPException(status_code=404, detail="Religion not found")
        
        # Return empty list for now - in full implementation would query events table
        return []
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get religious events: {str(e)}"
        )


@router.post("/{religion_id}/events", response_model=ReligiousEventResponse, status_code=status.HTTP_201_CREATED)
async def create_religious_event(
    religion_id: UUID,
    request: ReligiousEventRequest,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> ReligiousEventResponse:
    """
    Create a religious event for a religion (Unity frontend expected endpoint)
    
    - **religion_id**: The UUID of the religion
    - **request**: Religious event creation data
    """
    try:
        religion = await religion_service.get_religion_by_id(religion_id)
        if not religion:
            raise HTTPException(status_code=404, detail="Religion not found")
        
        from datetime import datetime
        event_id = UUID("00000000-0000-0000-0000-000000000003")  # Placeholder
        
        return ReligiousEventResponse(
            id=event_id,
            name=request.name,
            description=request.description,
            event_type=request.event_type,
            date=request.date or datetime.utcnow(),
            duration=request.duration or 1,
            location=request.location,
            participants=request.participants or [],
            religion_id=religion_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create religious event: {str(e)}"
        )


@router.get("/{religion_id}/influence/{region_id}", response_model=ReligiousInfluenceResponse)
async def get_religious_influence(
    religion_id: UUID,
    region_id: str,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> ReligiousInfluenceResponse:
    """
    Get religious influence for a religion in a specific region (Unity frontend expected endpoint)
    
    - **religion_id**: The UUID of the religion
    - **region_id**: The region identifier
    """
    try:
        religion = await religion_service.get_religion_by_id(religion_id)
        if not religion:
            raise HTTPException(status_code=404, detail="Religion not found")
        
        from datetime import datetime
        influence_id = UUID("00000000-0000-0000-0000-000000000004")  # Placeholder
        
        return ReligiousInfluenceResponse(
            id=influence_id,
            religion_id=religion_id,
            region_id=region_id,
            influence_level=0.5,  # Default value
            follower_count=religion.followers_count,
            temples_count=0,
            clergy_count=0,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get religious influence: {str(e)}"
        )


@router.put("/{religion_id}/influence/{region_id}", response_model=ReligiousInfluenceResponse)
async def update_religious_influence(
    religion_id: UUID,
    region_id: str,
    request: ReligiousInfluenceRequest,
    religion_service: ReligionService = Depends(get_religion_service_dependency)
) -> ReligiousInfluenceResponse:
    """
    Update religious influence for a religion in a specific region (Unity frontend expected endpoint)
    
    - **religion_id**: The UUID of the religion
    - **region_id**: The region identifier
    - **request**: Religious influence update data
    """
    try:
        religion = await religion_service.get_religion_by_id(religion_id)
        if not religion:
            raise HTTPException(status_code=404, detail="Religion not found")
        
        from datetime import datetime
        influence_id = UUID("00000000-0000-0000-0000-000000000004")  # Placeholder
        
        return ReligiousInfluenceResponse(
            id=influence_id,
            religion_id=religion_id,
            region_id=region_id,
            influence_level=request.influence_level or 0.0,
            follower_count=request.follower_count or 0,
            temples_count=request.temples_count or 0,
            clergy_count=request.clergy_count or 0,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update religious influence: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "religion",
        "version": "1.0.0"
    }


# Export the router
__all__ = ["router"] 