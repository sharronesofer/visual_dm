"""
Negotiation Router

Specialized router for negotiation-related endpoints and operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.systems.diplomacy.services.unified_diplomacy_service import (
    UnifiedDiplomacyService, get_unified_diplomacy_service
)
from backend.systems.diplomacy.models.core_models import NegotiationStatus

# Create negotiation router
negotiation_router = APIRouter(
    prefix="/negotiations",
    tags=["negotiations"],
    responses={404: {"description": "Negotiation not found"}}
)

@negotiation_router.get("/")
async def list_negotiations(
    faction_id: Optional[UUID] = None,
    status_filter: Optional[NegotiationStatus] = None,
    active_only: bool = True,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """List negotiations with optional filtering"""
    try:
        negotiations = service.get_all_negotiations(status_filter=status_filter)
        
        # Filter by faction if specified
        if faction_id:
            negotiations = [
                n for n in negotiations 
                if n.initiator_faction_id == faction_id or n.target_faction_id == faction_id
            ]
        
        # Filter by active status
        if active_only:
            active_statuses = [NegotiationStatus.INITIATED, NegotiationStatus.IN_PROGRESS]
            negotiations = [n for n in negotiations if n.status in active_statuses]
            
        return [negotiation.to_dict() for negotiation in negotiations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list negotiations: {str(e)}"
        )

@negotiation_router.get("/{negotiation_id}")
async def get_negotiation_details(
    negotiation_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Get detailed information about a specific negotiation"""
    try:
        negotiation = service.get_negotiation(negotiation_id)
        if not negotiation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Negotiation {negotiation_id} not found"
            )
        
        # Get negotiation offers
        offers = service.get_negotiation_offers(negotiation_id)
        
        result = negotiation.to_dict()
        result["offers"] = [offer.to_dict() for offer in offers]
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get negotiation details: {str(e)}"
        )

@negotiation_router.post("/")
async def start_new_negotiation(
    initiator_faction_id: UUID,
    target_faction_id: UUID,
    topic: str,
    initial_offer: Dict[str, Any],
    deadline_days: Optional[int] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Start a new negotiation between two factions"""
    try:
        negotiation = service.start_negotiation(
            initiator_faction_id=initiator_faction_id,
            target_faction_id=target_faction_id,
            topic=topic,
            initial_offer=initial_offer,
            deadline_days=deadline_days
        )
        return negotiation.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start negotiation: {str(e)}"
        )

@negotiation_router.post("/{negotiation_id}/offers")
async def submit_negotiation_offer(
    negotiation_id: UUID,
    offering_faction_id: UUID,
    terms: Dict[str, Any],
    message: Optional[str] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Submit a new offer in an ongoing negotiation"""
    try:
        offer = service.submit_negotiation_offer(
            negotiation_id=negotiation_id,
            offering_faction_id=offering_faction_id,
            terms=terms,
            message=message or ""
        )
        return offer.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit negotiation offer: {str(e)}"
        )

@negotiation_router.put("/{negotiation_id}/respond")
async def respond_to_negotiation(
    negotiation_id: UUID,
    responding_faction_id: UUID,
    response: str,  # "accept", "reject", "counter"
    counter_offer: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Respond to a negotiation (accept, reject, or counter)"""
    try:
        result = service.respond_to_negotiation(
            negotiation_id=negotiation_id,
            responding_faction_id=responding_faction_id,
            response=response,
            counter_offer=counter_offer,
            message=message or ""
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to respond to negotiation: {str(e)}"
        )

@negotiation_router.put("/{negotiation_id}/conclude")
async def conclude_negotiation(
    negotiation_id: UUID,
    concluding_faction_id: UUID,
    outcome: str,  # "success", "failure", "timeout"
    final_terms: Optional[Dict[str, Any]] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Conclude a negotiation with a final outcome"""
    try:
        result = service.conclude_negotiation(
            negotiation_id=negotiation_id,
            concluding_faction_id=concluding_faction_id,
            outcome=outcome,
            final_terms=final_terms or {}
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to conclude negotiation: {str(e)}"
        )

@negotiation_router.get("/{negotiation_id}/offers")
async def get_negotiation_offers(
    negotiation_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all offers for a specific negotiation"""
    try:
        offers = service.get_negotiation_offers(negotiation_id)
        return [offer.to_dict() for offer in offers]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get negotiation offers: {str(e)}"
        )

@negotiation_router.get("/faction/{faction_id}")
async def get_faction_negotiations(
    faction_id: UUID,
    active_only: bool = True,
    status_filter: Optional[NegotiationStatus] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all negotiations involving a specific faction"""
    try:
        negotiations = service.get_faction_negotiations(
            faction_id, 
            active_only=active_only,
            status_filter=status_filter
        )
        return [negotiation.to_dict() for negotiation in negotiations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get faction negotiations: {str(e)}"
        ) 