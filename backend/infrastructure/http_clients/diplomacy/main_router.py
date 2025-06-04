"""
Main Diplomacy Router

This router serves as the main entry point for all diplomacy-related
API endpoints, organizing them by functional area.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.systems.diplomacy.services.unified_diplomacy_service import (
    UnifiedDiplomacyService, get_unified_diplomacy_service
)
from backend.systems.diplomacy.models.core_models import (
    DiplomaticStatus, TreatyType, NegotiationStatus,
    DiplomaticEventType, DiplomaticIncidentType
)

# Create main diplomacy router
diplomacy_router = APIRouter(
    prefix="/api/diplomacy",
    tags=["diplomacy"],
    responses={404: {"description": "Not found"}}
)

# =========================================================================
# FACTION RELATIONSHIP ENDPOINTS
# =========================================================================

@diplomacy_router.get("/relationships")
async def get_all_relationships(
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all faction relationships"""
    try:
        relationships = service.get_all_relationships()
        return [rel.to_dict() for rel in relationships]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve relationships: {str(e)}"
        )

@diplomacy_router.get("/relationships/{faction_a_id}/{faction_b_id}")
async def get_relationship(
    faction_a_id: UUID,
    faction_b_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Get relationship between two specific factions"""
    try:
        relationship = service.get_relationship(faction_a_id, faction_b_id)
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relationship not found"
            )
        return relationship.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve relationship: {str(e)}"
        )

@diplomacy_router.post("/relationships/{faction_a_id}/{faction_b_id}/update")
async def update_relationship(
    faction_a_id: UUID,
    faction_b_id: UUID,
    status: DiplomaticStatus,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Update relationship status between two factions"""
    try:
        relationship = service.update_relationship_status(
            faction_a_id, faction_b_id, status
        )
        return relationship.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update relationship: {str(e)}"
        )

# =========================================================================
# TREATY ENDPOINTS
# =========================================================================

@diplomacy_router.get("/treaties")
async def get_all_treaties(
    active_only: Optional[bool] = True,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all treaties, optionally filtered by active status"""
    try:
        treaties = service.get_all_treaties(active_only=active_only)
        return [treaty.to_dict() for treaty in treaties]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve treaties: {str(e)}"
        )

@diplomacy_router.get("/treaties/{treaty_id}")
async def get_treaty(
    treaty_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Get a specific treaty by ID"""
    try:
        treaty = service.get_treaty(treaty_id)
        if not treaty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treaty not found"
            )
        return treaty.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve treaty: {str(e)}"
        )

@diplomacy_router.post("/treaties")
async def create_treaty(
    faction_a_id: UUID,
    faction_b_id: UUID,
    treaty_type: TreatyType,
    terms: Dict[str, Any],
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Create a new treaty between two factions"""
    try:
        treaty = service.create_treaty(
            faction_a_id=faction_a_id,
            faction_b_id=faction_b_id,
            treaty_type=treaty_type,
            terms=terms
        )
        return treaty.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create treaty: {str(e)}"
        )

# =========================================================================
# NEGOTIATION ENDPOINTS
# =========================================================================

@diplomacy_router.get("/negotiations")
async def get_all_negotiations(
    status_filter: Optional[NegotiationStatus] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all negotiations, optionally filtered by status"""
    try:
        negotiations = service.get_all_negotiations(status_filter=status_filter)
        return [negotiation.to_dict() for negotiation in negotiations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve negotiations: {str(e)}"
        )

@diplomacy_router.post("/negotiations")
async def start_negotiation(
    initiator_faction_id: UUID,
    target_faction_id: UUID,
    topic: str,
    initial_offer: Dict[str, Any],
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Start a new negotiation between two factions"""
    try:
        negotiation = service.start_negotiation(
            initiator_faction_id=initiator_faction_id,
            target_faction_id=target_faction_id,
            topic=topic,
            initial_offer=initial_offer
        )
        return negotiation.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start negotiation: {str(e)}"
        )

# =========================================================================
# DIPLOMATIC EVENT ENDPOINTS
# =========================================================================

@diplomacy_router.get("/events")
async def get_diplomatic_events(
    faction_id: Optional[UUID] = None,
    event_type: Optional[DiplomaticEventType] = None,
    limit: Optional[int] = 50,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get diplomatic events, optionally filtered"""
    try:
        events = service.get_diplomatic_events(
            faction_id=faction_id,
            event_type=event_type,
            limit=limit
        )
        return [event.to_dict() for event in events]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve diplomatic events: {str(e)}"
        )

@diplomacy_router.post("/events")
async def record_diplomatic_event(
    event_type: DiplomaticEventType,
    faction_a_id: UUID,
    faction_b_id: Optional[UUID] = None,
    description: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Record a new diplomatic event"""
    try:
        event = service.record_diplomatic_event(
            event_type=event_type,
            faction_a_id=faction_a_id,
            faction_b_id=faction_b_id,
            description=description,
            metadata=metadata or {}
        )
        return event.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record diplomatic event: {str(e)}"
        )

# =========================================================================
# UTILITY ENDPOINTS
# =========================================================================

@diplomacy_router.get("/summary/{faction_id}")
async def get_faction_diplomatic_summary(
    faction_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Get a comprehensive diplomatic summary for a faction"""
    try:
        summary = service.get_faction_diplomatic_summary(faction_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get diplomatic summary: {str(e)}"
        )

@diplomacy_router.get("/health")
async def diplomacy_health_check(
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, str]:
    """Health check endpoint for diplomacy system"""
    try:
        # Perform a simple operation to verify system health
        relationships_count = len(service.get_all_relationships())
        return {
            "status": "healthy",
            "system": "diplomacy",
            "relationships_count": str(relationships_count)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Diplomacy system unhealthy: {str(e)}"
        ) 