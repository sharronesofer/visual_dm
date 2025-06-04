"""
FastAPI Router for Rumor System

Modern FastAPI implementation with dependency injection that integrates
with the business logic services and follows Development Bible patterns.
Includes comprehensive OpenAPI documentation for all endpoints.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi import status
from sqlalchemy.orm import Session

# Infrastructure imports
from backend.infrastructure.database.session import get_db
from backend.infrastructure.systems.rumor.models.models import (
    CreateRumorRequest,
    UpdateRumorRequest,
    RumorResponse,
    RumorListResponse
)
from backend.infrastructure.systems.rumor.repositories.rumor_repository import (
    SQLAlchemyRumorRepository,
    create_rumor_repository
)
from backend.infrastructure.systems.rumor.services.validation_service import (
    DefaultRumorValidationService,
    create_rumor_validation_service
)

# Business logic imports
from backend.systems.rumor.services.services import (
    RumorBusinessService,
    CreateRumorData,
    UpdateRumorData,
    RumorData
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rumors",
    tags=["rumors"],
    responses={
        400: {"description": "Bad request - invalid input data"},
        404: {"description": "Rumor not found"},
        500: {"description": "Internal server error"},
    },
)


# Dependency injection
def get_rumor_repository(db: Session = Depends(get_db)) -> SQLAlchemyRumorRepository:
    """Get rumor repository dependency"""
    return create_rumor_repository(db)


def get_validation_service() -> DefaultRumorValidationService:
    """Get validation service dependency"""
    return create_rumor_validation_service()


def get_rumor_service(
    repository: SQLAlchemyRumorRepository = Depends(get_rumor_repository),
    validation_service: DefaultRumorValidationService = Depends(get_validation_service)
) -> RumorBusinessService:
    """Get rumor service dependency"""
    return RumorBusinessService(repository, validation_service)


# Basic CRUD Endpoints

@router.post(
    "/", 
    response_model=RumorResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new rumor",
    description="""
    Create a new rumor in the system. The rumor will be created with the specified content
    and originator, and will start with full believability for the originator.
    
    **Business Rules:**
    - Content must be between 10-500 characters
    - Originator ID is required and identifies the entity spreading the rumor
    - Truth value represents how accurate the rumor actually is (0.0 = false, 1.0 = true)
    - Severity affects how the rumor spreads and decays over time
    """,
    response_description="The created rumor with generated ID and metadata"
)
async def create_rumor(
    request: CreateRumorRequest = Body(
        ...,
        example={
            "content": "The merchant's caravan was robbed on the road to Millfield",
            "originator_id": "npc_guard_captain",
            "categories": ["crime", "theft"],
            "severity": "moderate",
            "truth_value": 0.8,
            "properties": {"location": "trade_road", "witnesses": 3}
        }
    ),
    service: RumorBusinessService = Depends(get_rumor_service)
) -> RumorResponse:
    """Create a new rumor in the system."""
    try:
        logger.info(f"Creating rumor for originator: {request.originator_id}")
        
        # Convert to business logic format
        create_data = CreateRumorData(
            content=request.content,
            originator_id=request.originator_id,
            categories=request.categories or [],
            severity=request.severity,
            truth_value=request.truth_value,
            properties=request.properties or {}
        )
        
        # Create rumor using business logic
        rumor_data = service.create_rumor(create_data)
        
        # Convert to response format
        return RumorResponse(
            id=str(rumor_data.id),
            content=rumor_data.content,
            originator_id=rumor_data.originator_id,
            categories=rumor_data.categories,
            severity=rumor_data.severity,
            truth_value=rumor_data.truth_value,
            believability=rumor_data.believability,
            spread_count=rumor_data.spread_count,
            properties=rumor_data.properties,
            status=rumor_data.status,
            created_at=rumor_data.created_at,
            updated_at=getattr(rumor_data, 'updated_at', None)
        )
        
    except ValueError as e:
        logger.error(f"Validation error creating rumor: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating rumor: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/", 
    response_model=RumorListResponse,
    summary="List rumors with filtering and pagination",
    description="""
    Retrieve a paginated list of rumors with optional filtering capabilities.
    
    **Filtering Options:**
    - **Status**: Filter by rumor status (active, inactive, etc.)
    - **Search**: Search in rumor content and originator ID
    - **Originator**: Filter by specific originator ID
    
    **Performance Notes:**
    - Results are cached for better performance
    - Uses database indexes for efficient querying
    - Supports pagination to handle large datasets
    """,
    response_description="Paginated list of rumors matching the criteria"
)
async def list_rumors(
    page: int = Query(1, ge=1, description="Page number (1-based)", example=1),
    size: int = Query(50, ge=1, le=100, description="Items per page (max 100)", example=20),
    status: Optional[str] = Query(None, description="Filter by status", example="active"),
    search: Optional[str] = Query(None, description="Search in content or originator", example="caravan"),
    originator_id: Optional[str] = Query(None, description="Filter by originator", example="npc_guard_captain"),
    service: RumorBusinessService = Depends(get_rumor_service)
) -> RumorListResponse:
    """List rumors with filtering and pagination support."""
    try:
        logger.info(f"Listing rumors: page={page}, size={size}, status={status}")
        
        rumors, total = service.list_rumors(
            page=page,
            size=size,
            status=status,
            search=search
        )
        
        # Convert to response format
        rumor_responses = [
            RumorResponse(
                id=str(rumor.id),
                content=rumor.content,
                originator_id=rumor.originator_id,
                categories=rumor.categories,
                severity=rumor.severity,
                truth_value=rumor.truth_value,
                believability=rumor.believability,
                spread_count=rumor.spread_count,
                properties=rumor.properties,
                status=rumor.status,
                created_at=rumor.created_at,
                updated_at=getattr(rumor, 'updated_at', None)
            )
            for rumor in rumors
        ]
        
        has_next = (page * size) < total
        has_prev = page > 1
        
        return RumorListResponse(
            items=rumor_responses,
            total=total,
            page=page,
            size=size,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Error listing rumors: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/{rumor_id}", 
    response_model=RumorResponse,
    summary="Get a specific rumor by ID",
    description="""
    Retrieve detailed information about a specific rumor by its unique identifier.
    
    **Performance Notes:**
    - Results are cached for frequently accessed rumors
    - Uses database indexes for efficient lookup
    """,
    response_description="Detailed rumor information"
)
async def get_rumor(
    rumor_id: UUID = Path(..., description="The unique ID of the rumor to retrieve"),
    service: RumorBusinessService = Depends(get_rumor_service)
) -> RumorResponse:
    """Get detailed information about a specific rumor."""
    try:
        logger.info(f"Getting rumor: {rumor_id}")
        
        rumor_data = service.get_rumor_by_id(rumor_id)
        
        if not rumor_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rumor not found")
        
        return RumorResponse(
            id=str(rumor_data.id),
            content=rumor_data.content,
            originator_id=rumor_data.originator_id,
            categories=rumor_data.categories,
            severity=rumor_data.severity,
            truth_value=rumor_data.truth_value,
            believability=rumor_data.believability,
            spread_count=rumor_data.spread_count,
            properties=rumor_data.properties,
            status=rumor_data.status,
            created_at=rumor_data.created_at,
            updated_at=getattr(rumor_data, 'updated_at', None)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put(
    "/{rumor_id}", 
    response_model=RumorResponse,
    summary="Update an existing rumor",
    description="""
    Update an existing rumor's properties. Only provided fields will be updated.
    
    **Updatable Fields:**
    - Content, categories, severity, truth value
    - Believability, spread count, status
    - Custom properties
    
    **Note:** Some fields like ID, originator, and timestamps cannot be modified.
    """,
    response_description="The updated rumor data"
)
async def update_rumor(
    rumor_id: UUID = Path(..., description="The unique ID of the rumor to update"),
    request: UpdateRumorRequest = Body(
        ...,
        example={
            "content": "The merchant's caravan was attacked by bandits on the road to Millfield",
            "severity": "major",
            "properties": {"confirmed": True, "casualties": 2}
        }
    ),
    service: RumorBusinessService = Depends(get_rumor_service)
) -> RumorResponse:
    """Update an existing rumor's properties."""
    try:
        logger.info(f"Updating rumor: {rumor_id}")
        
        # Get existing rumor
        existing_rumor = service.get_rumor_by_id(rumor_id)
        if not existing_rumor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rumor not found")
        
        # Apply updates
        update_fields = {}
        if request.content is not None:
            update_fields["content"] = request.content
        if request.categories is not None:
            update_fields["categories"] = request.categories
        if request.severity is not None:
            update_fields["severity"] = request.severity
        if request.truth_value is not None:
            update_fields["truth_value"] = request.truth_value
        if request.believability is not None:
            update_fields["believability"] = request.believability
        if request.spread_count is not None:
            update_fields["spread_count"] = request.spread_count
        if request.status is not None:
            update_fields["status"] = request.status
        if request.properties is not None:
            update_fields["properties"] = request.properties
        
        update_data = UpdateRumorData(**update_fields)
        updated_rumor = service.update_rumor(rumor_id, update_data)
        
        return RumorResponse(
            id=str(updated_rumor.id),
            content=updated_rumor.content,
            originator_id=updated_rumor.originator_id,
            categories=updated_rumor.categories,
            severity=updated_rumor.severity,
            truth_value=updated_rumor.truth_value,
            believability=updated_rumor.believability,
            spread_count=updated_rumor.spread_count,
            properties=updated_rumor.properties,
            status=updated_rumor.status,
            created_at=updated_rumor.created_at,
            updated_at=getattr(updated_rumor, 'updated_at', None)
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete(
    "/{rumor_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a rumor",
    description="""
    Permanently delete a rumor from the system.
    
    **Warning:** This action cannot be undone. The rumor and all associated data will be removed.
    
    **Cache Invalidation:** Related cached data will be automatically cleared.
    """,
    response_description="No content on successful deletion"
)
async def delete_rumor(
    rumor_id: UUID = Path(..., description="The unique ID of the rumor to delete"),
    service: RumorBusinessService = Depends(get_rumor_service)
):
    """Permanently delete a rumor from the system."""
    try:
        logger.info(f"Deleting rumor: {rumor_id}")
        
        success = service.delete_rumor(rumor_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rumor not found")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Statistics Endpoint

@router.get(
    "/statistics/summary", 
    response_model=Dict[str, Any],
    summary="Get rumor system statistics",
    description="""
    Retrieve comprehensive statistics about the rumor system.
    
    **Metrics Included:**
    - Total and active rumor counts
    - Severity distribution
    - Average truth value, believability, and spread count
    
    **Performance Notes:**
    - Statistics are cached for improved performance
    - Uses aggregation functions for efficient calculation
    """,
    response_description="System-wide rumor statistics and metrics"
)
async def get_rumor_statistics(
    service: RumorBusinessService = Depends(get_rumor_service)
) -> Dict[str, Any]:
    """Get comprehensive rumor system statistics."""
    try:
        logger.info("Getting rumor statistics")
        
        stats = service.get_rumor_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting rumor statistics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Advanced Rumor Mechanics Endpoints

@router.post(
    "/{rumor_id}/spread", 
    response_model=Dict[str, Any],
    summary="Spread a rumor between entities",
    description="""
    Simulate the spreading of a rumor from one entity to another using advanced mechanics.
    
    **Advanced Features:**
    - **Probability Calculation**: Based on relationship strength, trust, and social context
    - **Content Mutation**: Rumors may change as they spread (like "Chinese whispers")
    - **Believability Changes**: Rumors become more or less believable as they spread
    - **Environmental Factors**: Time of day, location type, and social settings affect spread
    
    **Parameters:**
    - **Relationship Strength**: How well the entities know each other (0.0-1.0)
    - **Social Context**: Environmental factors like location type, time of day, privacy level
    - **Receiver Personality**: Traits that affect how they receive and potentially mutate rumors
    
    **Business Logic:**
    - Rumors with higher severity spread more easily
    - Strong relationships increase spread probability
    - Taverns and markets boost spread, courts and temples reduce it
    - Evening/night time increases spread probability
    """,
    response_description="Result of the spread operation including success status and any mutations"
)
async def spread_rumor(
    rumor_id: UUID = Path(..., description="The ID of the rumor to spread"),
    from_entity_id: str = Body(..., description="ID of the entity spreading the rumor"),
    to_entity_id: str = Body(..., description="ID of the entity receiving the rumor"),
    relationship_strength: float = Body(0.5, ge=0.0, le=1.0, description="Strength of relationship between entities"),
    allow_mutation: bool = Body(True, description="Whether to allow rumor content to mutate during spread"),
    social_context: Optional[Dict[str, Any]] = Body(
        None, 
        description="Social context affecting spread",
        example={
            "location_type": "tavern",
            "time_of_day": "evening",
            "privacy_level": 0.7,
            "receiver_trust": 0.6,
            "source_credibility": 0.8,
            "supporting_evidence": 0.3
        }
    ),
    receiver_personality: Optional[Dict[str, Any]] = Body(
        None,
        description="Personality traits affecting rumor reception and mutation",
        example={
            "gossipy": True,
            "skepticism": 0.4,
            "dramatic": False,
            "careful": False,
            "honest": True
        }
    ),
    service: RumorBusinessService = Depends(get_rumor_service)
) -> Dict[str, Any]:
    """Spread a rumor between entities using advanced mechanics."""
    try:
        logger.info(f"Spreading rumor {rumor_id} from {from_entity_id} to {to_entity_id}")
        
        success, failure_reason, new_rumor = service.spread_rumor(
            rumor_id=rumor_id,
            from_entity_id=from_entity_id,
            to_entity_id=to_entity_id,
            relationship_strength=relationship_strength,
            allow_mutation=allow_mutation,
            social_context=social_context,
            receiver_personality=receiver_personality
        )
        
        if not success:
            return {
                "success": False,
                "message": failure_reason,
                "spread_data": None
            }
        
        # Convert new rumor to response format if it exists
        new_rumor_data = None
        if new_rumor:
            new_rumor_data = {
                "id": str(new_rumor.id),
                "content": new_rumor.content,
                "originator_id": new_rumor.originator_id,
                "believability": new_rumor.believability,
                "spread_count": new_rumor.spread_count,
                "was_mutated": 'mutation_metadata' in new_rumor.properties
            }
        
        return {
            "success": True,
            "message": "Rumor spread successfully",
            "spread_data": {
                "from_entity": from_entity_id,
                "to_entity": to_entity_id,
                "relationship_strength": relationship_strength,
                "new_rumor": new_rumor_data
            }
        }
        
    except ValueError as e:
        logger.error(f"Validation error spreading rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error spreading rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post(
    "/{rumor_id}/decay", 
    response_model=RumorResponse,
    summary="Apply time-based decay to a rumor",
    description="""
    Apply sophisticated time-based decay to a rumor's believability.
    
    **Decay Mechanics:**
    - **Logarithmic Decay**: Fast initial decay, then slower over time
    - **Severity Impact**: More severe rumors decay slower
    - **Environmental Factors**: Conflict slows decay, peace accelerates it
    - **Minimum Floors**: Critical rumors never completely disappear
    
    **Environmental Factors:**
    - `active_conflict`: Slows decay (people remember war rumors longer)
    - `peaceful_period`: Accelerates decay (rumors fade in peaceful times)
    - `information_abundance`: More info available = faster decay
    - `social_stability`: Stable societies forget rumors faster
    """,
    response_description="The rumor with updated believability after decay"
)
async def apply_time_decay(
    rumor_id: UUID = Path(..., description="The ID of the rumor to apply decay to"),
    days_elapsed: int = Body(..., ge=0, description="Number of days since last reinforcement"),
    environmental_factors: Optional[Dict[str, Any]] = Body(
        None,
        description="Environmental factors affecting decay rate",
        example={
            "active_conflict": False,
            "peaceful_period": True,
            "information_abundance": 0.6,
            "social_stability": 0.7
        }
    ),
    service: RumorBusinessService = Depends(get_rumor_service)
) -> RumorResponse:
    """Apply time-based decay to reduce rumor believability over time."""
    try:
        logger.info(f"Applying time decay to rumor {rumor_id} for {days_elapsed} days")
        
        updated_rumor = service.apply_time_decay(
            rumor_id=rumor_id,
            days_elapsed=days_elapsed,
            environmental_factors=environmental_factors
        )
        
        return RumorResponse(
            id=str(updated_rumor.id),
            content=updated_rumor.content,
            originator_id=updated_rumor.originator_id,
            categories=updated_rumor.categories,
            severity=updated_rumor.severity,
            truth_value=updated_rumor.truth_value,
            believability=updated_rumor.believability,
            spread_count=updated_rumor.spread_count,
            properties=updated_rumor.properties,
            status=updated_rumor.status,
            created_at=updated_rumor.created_at,
            updated_at=getattr(updated_rumor, 'updated_at', None)
        )
        
    except ValueError as e:
        logger.error(f"Validation error applying decay to rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error applying decay to rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post(
    "/{rumor_id}/contradict", 
    response_model=RumorResponse,
    summary="Apply contradiction to reduce rumor believability",
    description="""
    Apply contradiction to reduce a rumor's believability when conflicting information emerges.
    
    **Contradiction Mechanics:**
    - **Strength Impact**: Stronger contradictions cause more believability loss
    - **Source Credibility**: More credible sources have greater contradiction effect
    - **Randomness**: Some variation in how much believability is lost
    
    **Use Cases:**
    - Official announcements contradicting rumors
    - Eyewitness testimony conflicting with rumors
    - Evidence emerging that disproves rumors
    """,
    response_description="The rumor with reduced believability after contradiction"
)
async def contradict_rumor(
    rumor_id: UUID = Path(..., description="The ID of the rumor to contradict"),
    contradiction_strength: float = Body(..., ge=0.0, le=1.0, description="Strength of the contradiction (0.0-1.0)"),
    source_credibility: float = Body(..., ge=0.0, le=1.0, description="Credibility of the contradicting source (0.0-1.0)"),
    service: RumorBusinessService = Depends(get_rumor_service)
) -> RumorResponse:
    """Reduce rumor believability through contradiction."""
    try:
        logger.info(f"Contradicting rumor {rumor_id} with strength {contradiction_strength}")
        
        updated_rumor = service.contradict_rumor(
            rumor_id=rumor_id,
            contradiction_strength=contradiction_strength,
            source_credibility=source_credibility
        )
        
        return RumorResponse(
            id=str(updated_rumor.id),
            content=updated_rumor.content,
            originator_id=updated_rumor.originator_id,
            categories=updated_rumor.categories,
            severity=updated_rumor.severity,
            truth_value=updated_rumor.truth_value,
            believability=updated_rumor.believability,
            spread_count=updated_rumor.spread_count,
            properties=updated_rumor.properties,
            status=updated_rumor.status,
            created_at=updated_rumor.created_at,
            updated_at=getattr(updated_rumor, 'updated_at', None)
        )
        
    except ValueError as e:
        logger.error(f"Validation error contradicting rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error contradicting rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post(
    "/{rumor_id}/reinforce", 
    response_model=RumorResponse,
    summary="Apply reinforcement to boost rumor believability",
    description="""
    Apply reinforcement to boost a rumor's believability when supporting evidence emerges.
    
    **Reinforcement Mechanics:**
    - **Diminishing Returns**: Harder to reinforce already highly believable rumors
    - **Severity Resistance**: More severe rumors are harder to reinforce without strong evidence
    - **Source Credibility**: More credible sources provide better reinforcement
    
    **Use Cases:**
    - Additional witnesses coming forward
    - Supporting evidence being discovered
    - Credible sources confirming the rumor
    """,
    response_description="The rumor with increased believability after reinforcement"
)
async def reinforce_rumor(
    rumor_id: UUID = Path(..., description="The ID of the rumor to reinforce"),
    reinforcement_strength: float = Body(..., ge=0.0, le=1.0, description="Strength of the reinforcement (0.0-1.0)"),
    source_credibility: float = Body(..., ge=0.0, le=1.0, description="Credibility of the reinforcing source (0.0-1.0)"),
    service: RumorBusinessService = Depends(get_rumor_service)
) -> RumorResponse:
    """Boost rumor believability through reinforcement."""
    try:
        logger.info(f"Reinforcing rumor {rumor_id} with strength {reinforcement_strength}")
        
        updated_rumor = service.reinforce_rumor(
            rumor_id=rumor_id,
            reinforcement_strength=reinforcement_strength,
            source_credibility=source_credibility
        )
        
        return RumorResponse(
            id=str(updated_rumor.id),
            content=updated_rumor.content,
            originator_id=updated_rumor.originator_id,
            categories=updated_rumor.categories,
            severity=updated_rumor.severity,
            truth_value=updated_rumor.truth_value,
            believability=updated_rumor.believability,
            spread_count=updated_rumor.spread_count,
            properties=updated_rumor.properties,
            status=updated_rumor.status,
            created_at=updated_rumor.created_at,
            updated_at=getattr(updated_rumor, 'updated_at', None)
        )
        
    except ValueError as e:
        logger.error(f"Validation error reinforcing rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error reinforcing rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/{rumor_id}/impact", 
    response_model=Dict[str, Any],
    summary="Analyze rumor impact and influence",
    description="""
    Get comprehensive impact analysis for a rumor including metrics and historical data.
    
    **Impact Analysis Includes:**
    - **Impact Score**: Overall influence rating (0.0-1.0)
    - **Impact Level**: Categorical assessment (Minimal, Low, Moderate, High, Critical)
    - **Key Metrics**: Believability, spread count, severity, truth value
    - **Historical Data**: Contradictions, reinforcements, decay applications
    - **Variant Count**: Number of mutations created from this rumor
    
    **Impact Score Calculation:**
    - Based on severity, believability, and spread count
    - Higher scores indicate more influential rumors
    - Used for prioritizing rumor management efforts
    """,
    response_description="Comprehensive impact analysis and metrics for the rumor"
)
async def get_rumor_impact(
    rumor_id: UUID = Path(..., description="The ID of the rumor to analyze"),
    service: RumorBusinessService = Depends(get_rumor_service)
) -> Dict[str, Any]:
    """Get comprehensive impact analysis for a rumor."""
    try:
        logger.info(f"Analyzing impact for rumor {rumor_id}")
        
        # Get the rumor first
        rumor = service.get_rumor_by_id(rumor_id)
        if not rumor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rumor not found")
        
        # Calculate impact score
        impact_score = service.calculate_rumor_impact_score(rumor_id)
        
        # Get variants (mutations)
        variants = service.get_rumor_variants(rumor_id)
        
        return {
            "rumor_id": str(rumor_id),
            "impact_score": impact_score,
            "metrics": {
                "believability": rumor.believability,
                "spread_count": rumor.spread_count,
                "severity": rumor.severity,
                "truth_value": rumor.truth_value,
                "variant_count": len(variants)
            },
            "impact_level": (
                "Critical" if impact_score >= 0.8 else
                "High" if impact_score >= 0.6 else
                "Moderate" if impact_score >= 0.4 else
                "Low" if impact_score >= 0.2 else
                "Minimal"
            ),
            "history": {
                "contradictions": rumor.properties.get('contradictions', []),
                "reinforcements": rumor.properties.get('reinforcements', []),
                "decay_applications": rumor.properties.get('decay_applications', 0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing impact for rumor {rumor_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 