"""
REST API Router for Diplomacy System

This module defines the API endpoints for interacting with the diplomacy system.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body

from backend.systems.diplomacy.models import (
    DiplomaticEventType, 
    DiplomaticIncidentType,
    DiplomaticStatus, 
    SanctionStatus,
    SanctionType,
    TreatyType,
    TreatyViolationType,
    UltimatumStatus
)
from backend.systems.diplomacy.schemas import (
    DiplomaticEventCreate,
    DiplomaticEventSchema,
    DiplomaticIncidentCreate,
    DiplomaticIncidentSchema,
    DiplomaticIncidentUpdate,
    FactionRelationshipSchema,
    NegotiationCreate,
    NegotiationOfferCreate,
    NegotiationSchema,
    NegotiationUpdate,
    SanctionCreate,
    SanctionSchema,
    SanctionUpdate,
    SanctionViolationRecord,
    TreatyCreate,
    TreatySchema,
    TreatyUpdate,
    TreatyViolationCreate,
    TreatyViolationSchema,
    UltimatumCreate,
    UltimatumSchema,
    UltimatumUpdate
)
from backend.systems.diplomacy.services import DiplomacyService, TensionService


# Create a router
router = APIRouter(
    prefix="/diplomacy",
    tags=["diplomacy"],
    responses={404: {"description": "Not found"}}
)

# Dependency to get diplomacy service
@router.get("/get_diplomacy_service")
def get_diplomacy_service():
    return DiplomacyService()

# Dependency to get tension service
@router.get("/get_tension_service")
def get_tension_service():
    return TensionService()


# Treaty endpoints

@router.post("/treaties", response_model=TreatySchema)
async def create_treaty(
    treaty: TreatyCreate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Create a new treaty between factions."""
    return diplomacy_service.create_treaty(
        name=treaty.name,
        treaty_type=treaty.type,
        parties=treaty.parties,
        terms=treaty.terms,
        end_date=treaty.end_date,
        is_public=treaty.is_public,
        negotiation_id=treaty.negotiation_id
    )


@router.get("/treaties/{treaty_id}", response_model=TreatySchema)
async def get_treaty(
    treaty_id: UUID,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Get a treaty by ID."""
    treaty = diplomacy_service.get_treaty(treaty_id)
    if not treaty:
        raise HTTPException(status_code=404, detail="Treaty not found")
    return treaty


@router.get("/treaties", response_model=List[TreatySchema])
async def list_treaties(
    faction_id: Optional[UUID] = None,
    active_only: bool = False,
    treaty_type: Optional[TreatyType] = None,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """List treaties, optionally filtered."""
    return diplomacy_service.list_treaties(faction_id, active_only, treaty_type)


@router.patch("/treaties/{treaty_id}", response_model=TreatySchema)
async def update_treaty(
    treaty_id: UUID,
    treaty_update: TreatyUpdate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Update a treaty."""
    treaty = diplomacy_service.repository.update_treaty(treaty_id, treaty_update.dict(exclude_unset=True))
    if not treaty:
        raise HTTPException(status_code=404, detail="Treaty not found")
    return treaty


@router.post("/treaties/{treaty_id}/expire", response_model=TreatySchema)
async def expire_treaty(
    treaty_id: UUID,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Mark a treaty as expired."""
    treaty = diplomacy_service.expire_treaty(treaty_id)
    if not treaty:
        raise HTTPException(status_code=404, detail="Treaty not found or already expired")
    return treaty


# Negotiation endpoints

@router.post("/negotiations", response_model=NegotiationSchema)
async def start_negotiation(
    negotiation: NegotiationCreate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Start a new negotiation."""
    initial_offer = None
    if negotiation.initial_offer:
        initial_offer = negotiation.initial_offer.terms
    
    return diplomacy_service.start_negotiation(
        parties=negotiation.parties,
        initiator_id=negotiation.initiator_id,
        treaty_type=negotiation.treaty_type,
        initial_offer=initial_offer,
        metadata=negotiation.metadata
    )


@router.get("/negotiations/{negotiation_id}", response_model=NegotiationSchema)
async def get_negotiation(
    negotiation_id: UUID,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Get a negotiation by ID."""
    negotiation = diplomacy_service.get_negotiation(negotiation_id)
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    return negotiation


@router.post("/negotiations/{negotiation_id}/offers", response_model=NegotiationSchema)
async def make_offer(
    negotiation_id: UUID,
    offer: NegotiationOfferCreate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Make an offer in a negotiation."""
    result = diplomacy_service.make_offer(
        negotiation_id=negotiation_id,
        faction_id=offer.faction_id,
        terms=offer.terms,
        counter_to=offer.counter_offer_id
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="Could not make offer")
    
    negotiation, _ = result
    return negotiation


@router.post("/negotiations/{negotiation_id}/accept", response_model=TreatySchema)
async def accept_offer(
    negotiation_id: UUID,
    faction_id: UUID,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Accept the current offer in a negotiation."""
    result = diplomacy_service.accept_offer(
        negotiation_id=negotiation_id,
        faction_id=faction_id
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="Could not accept offer")
    
    _, treaty = result
    return treaty


@router.post("/negotiations/{negotiation_id}/reject", response_model=NegotiationSchema)
async def reject_offer(
    negotiation_id: UUID,
    faction_id: UUID,
    final: bool = False,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Reject the current offer in a negotiation."""
    negotiation = diplomacy_service.reject_offer(
        negotiation_id=negotiation_id,
        faction_id=faction_id,
        final=final
    )
    
    if not negotiation:
        raise HTTPException(status_code=400, detail="Could not reject offer")
    
    return negotiation


# Diplomatic Event endpoints

@router.post("/events", response_model=DiplomaticEventSchema)
async def create_event(
    event: DiplomaticEventCreate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Create a new diplomatic event."""
    return diplomacy_service.create_diplomatic_event(
        event_type=event.event_type,
        factions=event.factions,
        description=event.description,
        severity=event.severity,
        public=event.public,
        related_treaty_id=event.related_treaty_id,
        related_negotiation_id=event.related_negotiation_id,
        metadata=event.metadata,
        tension_changes=event.tension_change
    )


@router.get("/events", response_model=List[DiplomaticEventSchema])
async def list_events(
    faction_id: Optional[UUID] = None,
    event_type: Optional[DiplomaticEventType] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    public_only: bool = False,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """List diplomatic events, optionally filtered."""
    return diplomacy_service.repository.list_events(
        faction_id=faction_id,
        event_type=event_type,
        start_time=start_time,
        end_time=end_time,
        public_only=public_only
    )


# Faction Relationship endpoints

@router.get("/relations/{faction_id}", response_model=List[FactionRelationshipSchema])
async def get_faction_relationships(
    faction_id: UUID,
    tension_service: TensionService = Depends(get_tension_service)
):
    """Get all relationships for a faction."""
    return tension_service.get_faction_relationships(faction_id)


@router.get("/relations/{faction_a_id}/{faction_b_id}", response_model=FactionRelationshipSchema)
async def get_relationship(
    faction_a_id: UUID,
    faction_b_id: UUID,
    tension_service: TensionService = Depends(get_tension_service)
):
    """Get the relationship between two factions."""
    return tension_service.get_faction_relationship(faction_a_id, faction_b_id)


@router.post("/relations/{faction_a_id}/{faction_b_id}/tension", response_model=FactionRelationshipSchema)
async def update_tension(
    faction_a_id: UUID,
    faction_b_id: UUID,
    tension_change: int,
    reason: Optional[str] = None,
    tension_service: TensionService = Depends(get_tension_service)
):
    """Update tension between two factions."""
    return tension_service.update_faction_tension(
        faction_a_id=faction_a_id,
        faction_b_id=faction_b_id,
        tension_change=tension_change,
        reason=reason
    )


@router.post("/relations/{faction_a_id}/{faction_b_id}/status", response_model=FactionRelationshipSchema)
async def set_status(
    faction_a_id: UUID,
    faction_b_id: UUID,
    status: DiplomaticStatus,
    tension_service: TensionService = Depends(get_tension_service)
):
    """Set diplomatic status between two factions."""
    return tension_service.set_diplomatic_status(
        faction_a_id=faction_a_id,
        faction_b_id=faction_b_id,
        status=status
    )


# Include routes from tension/war module
# These endpoints are provided for backward compatibility

@router.get("/tension/{faction_a_id}/{faction_b_id}", response_model=FactionRelationshipSchema)
async def get_tension(
    faction_a_id: UUID,
    faction_b_id: UUID,
    tension_service: TensionService = Depends(get_tension_service)
):
    """Get tension between two factions (backward compatibility)."""
    return tension_service.get_faction_relationship(faction_a_id, faction_b_id)


@router.post("/war/check/{faction_a_id}/{faction_b_id}")
async def check_war_status(
    faction_a_id: UUID,
    faction_b_id: UUID,
    tension_service: TensionService = Depends(get_tension_service)
):
    """Check if two factions are at war (backward compatibility)."""
    is_at_war = tension_service.are_at_war(faction_a_id, faction_b_id)
    return {"at_war": is_at_war}


# Treaty Violation endpoints

@router.post("/violations", response_model=TreatyViolationSchema)
async def report_treaty_violation(
    violation: TreatyViolationCreate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Report a treaty violation."""
    try:
        return diplomacy_service.report_treaty_violation(
            treaty_id=violation.treaty_id,
            violator_id=violation.violator_id,
            violation_type=violation.violation_type,
            description=violation.description,
            evidence=violation.evidence,
            reported_by=violation.reported_by,
            severity=violation.severity
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/violations", response_model=List[TreatyViolationSchema])
async def get_treaty_violations(
    treaty_id: Optional[UUID] = None,
    faction_id: Optional[UUID] = None,
    violation_type: Optional[TreatyViolationType] = None,
    resolved: Optional[bool] = None,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Get treaty violations, optionally filtered."""
    return diplomacy_service.get_treaty_violations(
        treaty_id=treaty_id,
        faction_id=faction_id,
        violation_type=violation_type,
        resolved=resolved
    )


@router.post("/violations/{violation_id}/acknowledge", response_model=TreatyViolationSchema)
async def acknowledge_violation(
    violation_id: UUID,
    faction_id: UUID,
    resolution_details: Optional[str] = None,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Acknowledge a treaty violation as the violator."""
    try:
        violation = diplomacy_service.acknowledge_violation(
            violation_id=violation_id,
            acknowledging_faction_id=faction_id,
            resolution_details=resolution_details
        )
        if not violation:
            raise HTTPException(status_code=404, detail="Violation not found")
        return violation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/violations/{violation_id}/resolve", response_model=TreatyViolationSchema)
async def resolve_violation(
    violation_id: UUID,
    resolution_details: str,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Mark a treaty violation as resolved."""
    violation = diplomacy_service.resolve_violation(
        violation_id=violation_id,
        resolution_details=resolution_details
    )
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    return violation


@router.get("/compliance/{faction_id}")
async def check_treaty_compliance(
    faction_id: UUID,
    violation_types: Optional[List[TreatyViolationType]] = Query(None),
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Check if a faction is compliant with all its treaties."""
    compliance = diplomacy_service.check_treaty_compliance(
        faction_id=faction_id,
        violation_types=violation_types
    )
    
    # Convert UUID keys to strings for JSON serialization
    result = {}
    for treaty_id, violations in compliance.items():
        result[str(treaty_id)] = [v.dict() for v in violations]
    
    return result


@router.post("/enforce-treaties")
async def enforce_treaties(
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Automatically enforce treaties by detecting violations."""
    violations = diplomacy_service.enforce_treaties_automatically()
    return {
        "success": True,
        "violations_detected": len(violations),
        "violations": [v.dict() for v in violations]
    }


# Diplomatic Incident endpoints

@router.post("/incidents", response_model=DiplomaticIncidentSchema)
async def create_diplomatic_incident(
    incident: DiplomaticIncidentCreate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Create a new diplomatic incident."""
    try:
        return diplomacy_service.create_diplomatic_incident(
            incident_type=incident.incident_type,
            perpetrator_id=incident.perpetrator_id,
            victim_id=incident.victim_id,
            description=incident.description,
            evidence=incident.evidence,
            severity=incident.severity,
            tension_impact=incident.tension_impact,
            public=incident.public,
            witnessed_by=incident.witnessed_by,
            related_event_id=incident.related_event_id,
            related_treaty_id=incident.related_treaty_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/incidents/{incident_id}", response_model=DiplomaticIncidentSchema)
async def get_diplomatic_incident(
    incident_id: UUID,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Get a diplomatic incident by ID."""
    incident = diplomacy_service.get_diplomatic_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Diplomatic incident not found")
    return incident

@router.get("/incidents", response_model=List[DiplomaticIncidentSchema])
async def list_diplomatic_incidents(
    faction_id: Optional[UUID] = None,
    as_perpetrator: bool = True,
    as_victim: bool = True,
    resolved: Optional[bool] = None,
    incident_type: Optional[DiplomaticIncidentType] = None,
    limit: int = 100,
    offset: int = 0,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """List diplomatic incidents with optional filtering."""
    return diplomacy_service.list_diplomatic_incidents(
        faction_id=faction_id,
        as_perpetrator=as_perpetrator,
        as_victim=as_victim,
        resolved=resolved,
        incident_type=incident_type,
        limit=limit,
        offset=offset
    )

@router.patch("/incidents/{incident_id}", response_model=DiplomaticIncidentSchema)
async def update_diplomatic_incident(
    incident_id: UUID,
    incident_update: DiplomaticIncidentUpdate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Update a diplomatic incident."""
    updated_incident = diplomacy_service.update_diplomatic_incident(
        incident_id=incident_id,
        severity=incident_update.severity,
        resolved=incident_update.resolved,
        resolution_details=incident_update.resolution_details
    )
    
    if not updated_incident:
        raise HTTPException(status_code=404, detail="Diplomatic incident not found")
        
    return updated_incident

@router.post("/incidents/{incident_id}/resolve", response_model=DiplomaticIncidentSchema)
async def resolve_diplomatic_incident(
    incident_id: UUID,
    resolution: dict = Body(..., example={"resolution_details": "The issue was resolved through negotiation."}),
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Mark a diplomatic incident as resolved."""
    resolution_details = resolution.get("resolution_details", "")
    resolved_incident = diplomacy_service.resolve_diplomatic_incident(
        incident_id=incident_id,
        resolution_details=resolution_details
    )
    
    if not resolved_incident:
        raise HTTPException(status_code=404, detail="Diplomatic incident not found")
        
    return resolved_incident

# Ultimatum endpoints

@router.post("/ultimatums", response_model=UltimatumSchema)
async def create_ultimatum(
    ultimatum: UltimatumCreate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Create a new ultimatum."""
    try:
        return diplomacy_service.create_ultimatum(
            issuer_id=ultimatum.issuer_id,
            recipient_id=ultimatum.recipient_id,
            demands=ultimatum.demands,
            consequences=ultimatum.consequences,
            deadline=ultimatum.deadline,
            justification=ultimatum.justification,
            public=ultimatum.public,
            witnessed_by=ultimatum.witnessed_by,
            related_incident_id=ultimatum.related_incident_id,
            related_treaty_id=ultimatum.related_treaty_id,
            related_event_id=ultimatum.related_event_id,
            tension_change_on_issue=ultimatum.tension_change_on_issue,
            tension_change_on_accept=ultimatum.tension_change_on_accept,
            tension_change_on_reject=ultimatum.tension_change_on_reject
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ultimatums/{ultimatum_id}", response_model=UltimatumSchema)
async def get_ultimatum(
    ultimatum_id: UUID,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Get an ultimatum by ID."""
    ultimatum = diplomacy_service.get_ultimatum(ultimatum_id)
    if not ultimatum:
        raise HTTPException(status_code=404, detail="Ultimatum not found")
    return ultimatum

@router.get("/ultimatums", response_model=List[UltimatumSchema])
async def list_ultimatums(
    faction_id: Optional[UUID] = None,
    as_issuer: bool = True,
    as_recipient: bool = True,
    status: Optional[UltimatumStatus] = None,
    active_only: bool = False,
    limit: int = 100,
    offset: int = 0,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """List ultimatums with optional filtering."""
    return diplomacy_service.list_ultimatums(
        faction_id=faction_id,
        as_issuer=as_issuer,
        as_recipient=as_recipient,
        status=status,
        active_only=active_only,
        limit=limit,
        offset=offset
    )

@router.patch("/ultimatums/{ultimatum_id}", response_model=UltimatumSchema)
async def update_ultimatum(
    ultimatum_id: UUID,
    ultimatum_update: UltimatumUpdate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Update an ultimatum."""
    updated_ultimatum = diplomacy_service.update_ultimatum(
        ultimatum_id=ultimatum_id,
        status=ultimatum_update.status,
        deadline=ultimatum_update.deadline,
        demands=ultimatum_update.demands,
        consequences=ultimatum_update.consequences
    )
    
    if not updated_ultimatum:
        raise HTTPException(status_code=404, detail="Ultimatum not found")
        
    return updated_ultimatum

@router.post("/ultimatums/{ultimatum_id}/respond", response_model=UltimatumSchema)
async def respond_to_ultimatum(
    ultimatum_id: UUID,
    response: dict = Body(..., example={"accept": True, "justification": "We accept your terms to maintain peace."}),
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Respond to an ultimatum (accept or reject)."""
    accept = response.get("accept", False)
    justification = response.get("justification")
    
    try:
        ultimatum = diplomacy_service.respond_to_ultimatum(
            ultimatum_id=ultimatum_id,
            accept=accept,
            response_justification=justification
        )
        
        if not ultimatum:
            raise HTTPException(status_code=404, detail="Ultimatum not found")
            
        return ultimatum
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ultimatums/check-expired", response_model=List[UltimatumSchema])
async def check_expired_ultimatums(
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Check for and process expired ultimatums."""
    return diplomacy_service.check_expired_ultimatums()


# Sanction endpoints

@router.post("/sanctions", response_model=SanctionSchema)
async def create_sanction(
    sanction: SanctionCreate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Create a new diplomatic sanction against a faction."""
    return diplomacy_service.create_sanction(
        imposer_id=sanction.imposer_id,
        target_id=sanction.target_id,
        sanction_type=sanction.sanction_type,
        description=sanction.description,
        justification=sanction.justification,
        end_date=sanction.end_date,
        conditions_for_lifting=sanction.conditions_for_lifting,
        severity=sanction.severity,
        economic_impact=sanction.economic_impact,
        diplomatic_impact=sanction.diplomatic_impact,
        enforcement_measures=sanction.enforcement_measures,
        supporting_factions=sanction.supporting_factions,
        opposing_factions=sanction.opposing_factions,
        is_public=sanction.is_public
    )


@router.get("/sanctions/{sanction_id}", response_model=SanctionSchema)
async def get_sanction(
    sanction_id: UUID,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Get a sanction by ID."""
    sanction = diplomacy_service.get_sanction(sanction_id)
    if not sanction:
        raise HTTPException(status_code=404, detail="Sanction not found")
    return sanction


@router.get("/sanctions", response_model=List[SanctionSchema])
async def list_sanctions(
    imposer_id: Optional[UUID] = None,
    target_id: Optional[UUID] = None,
    sanction_type: Optional[SanctionType] = None,
    status: Optional[SanctionStatus] = None,
    active_only: bool = False,
    limit: int = 100,
    offset: int = 0,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """List sanctions, optionally filtered by various parameters."""
    return diplomacy_service.list_sanctions(
        imposer_id=imposer_id,
        target_id=target_id,
        sanction_type=sanction_type,
        status=status,
        active_only=active_only,
        limit=limit,
        offset=offset
    )


@router.patch("/sanctions/{sanction_id}", response_model=SanctionSchema)
async def update_sanction(
    sanction_id: UUID,
    sanction_update: SanctionUpdate,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Update an existing sanction."""
    sanction = diplomacy_service.update_sanction(
        sanction_id=sanction_id,
        **sanction_update.dict(exclude_unset=True)
    )
    if not sanction:
        raise HTTPException(status_code=404, detail="Sanction not found")
    return sanction


@router.post("/sanctions/{sanction_id}/lift", response_model=SanctionSchema)
async def lift_sanction(
    sanction_id: UUID,
    reason: dict = Body(..., example={"reason": "Conditions for lifting have been met"}),
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Lift a diplomatic sanction."""
    sanction = diplomacy_service.lift_sanction(
        sanction_id=sanction_id,
        reason=reason.get("reason", "Sanction conditions met")
    )
    if not sanction:
        raise HTTPException(status_code=404, detail="Sanction not found or already lifted")
    return sanction


@router.post("/sanctions/{sanction_id}/violations", response_model=SanctionSchema)
async def record_sanction_violation(
    sanction_id: UUID,
    violation: SanctionViolationRecord,
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Record a violation of a sanction."""
    sanction = diplomacy_service.record_sanction_violation(
        sanction_id=sanction_id,
        description=violation.description,
        evidence=violation.evidence,
        reported_by=violation.reported_by,
        severity=violation.severity
    )
    if not sanction:
        raise HTTPException(status_code=404, detail="Sanction not found")
    return sanction


@router.post("/sanctions/check-expired", response_model=List[SanctionSchema])
async def check_expired_sanctions(
    diplomacy_service: DiplomacyService = Depends(get_diplomacy_service)
):
    """Check for and process expired sanctions."""
    return diplomacy_service.check_expired_sanctions()


# Cross-System Integration Endpoints

@router.get("/integration/status")
async def get_integration_status():
    """Get the status of all cross-system integrations."""
    from backend.systems.diplomacy.integration_services import DiplomacyIntegrationManager
    
    try:
        integration_manager = DiplomacyIntegrationManager()
        return integration_manager.get_integration_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting integration status: {str(e)}")

@router.post("/integration/initialize")
async def initialize_integrations():
    """Initialize all cross-system integrations."""
    from backend.systems.diplomacy.integration_services import DiplomacyIntegrationManager
    
    try:
        integration_manager = DiplomacyIntegrationManager()
        results = integration_manager.initialize_all_integrations()
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
        
        return {"message": "All integrations initialized successfully", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing integrations: {str(e)}")

@router.post("/integration/faction/{faction_id}/sync")
async def sync_faction_relationships(faction_id: UUID):
    """Synchronize diplomatic relationships with faction system data."""
    from backend.systems.diplomacy.integration_services import FactionDiplomacyIntegration
    
    try:
        faction_integration = FactionDiplomacyIntegration()
        results = faction_integration.sync_faction_relationships(faction_id)
        
        if not results.get("synced", False):
            reason = results.get("reason", "Unknown error")
            raise HTTPException(status_code=400, detail=f"Sync failed: {reason}")
        
        return {"message": "Faction relationships synchronized successfully", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing faction relationships: {str(e)}")

@router.get("/integration/regional/{region_id}/status")
async def get_regional_diplomatic_status(region_id: str):
    """Get diplomatic status summary for a specific region."""
    from backend.systems.diplomacy.integration_services import WorldStateDiplomacyIntegration
    
    try:
        world_state_integration = WorldStateDiplomacyIntegration()
        status = world_state_integration.get_regional_diplomatic_status(region_id)
        
        if not status.get("available", False):
            error = status.get("error", "Regional diplomatic status not available")
            raise HTTPException(status_code=503, detail=error)
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting regional diplomatic status: {str(e)}")

@router.post("/integration/events/test")
async def test_integration_events(
    event_type: str,
    event_data: dict = Body(..., example={
        "faction_id": "550e8400-e29b-41d4-a716-446655440000",
        "faction_name": "Test Faction"
    })
):
    """Test cross-system integration events (for development/testing)."""
    from backend.systems.diplomacy.integration_services import DiplomacyIntegrationManager
    
    try:
        integration_manager = DiplomacyIntegrationManager()
        
        # Test different event types
        if event_type == "faction_created":
            await integration_manager.faction_integration._handle_faction_created(event_data)
        elif event_type == "faction_dissolved":
            await integration_manager.faction_integration._handle_faction_dissolved(event_data)
        elif event_type == "diplomatic_action":
            await integration_manager.character_integration._handle_diplomatic_action(event_data)
        elif event_type == "quest_completed":
            await integration_manager.quest_integration._handle_quest_completed(event_data)
        elif event_type == "economic_crisis":
            await integration_manager.world_state_integration._handle_economic_crisis(event_data)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown event type: {event_type}")
        
        return {"message": f"Test event '{event_type}' processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing integration event: {str(e)}")

@router.get("/integration/health")
async def check_integration_health():
    """Comprehensive health check for all integration systems."""
    from backend.systems.diplomacy.integration_services import DiplomacyIntegrationManager
    
    try:
        integration_manager = DiplomacyIntegrationManager()
        status = integration_manager.get_integration_status()
        
        # Add more detailed health information
        health_status = {
            "overall_status": "healthy" if status.get("integrations_active", False) else "unhealthy",
            "services": {
                "faction_service": "available" if status.get("faction_service_available", False) else "unavailable",
                "character_service": "available" if status.get("character_service_available", False) else "unavailable", 
                "quest_service": "available" if status.get("quest_service_available", False) else "unavailable",
                "world_state_service": "available" if status.get("world_state_service_available", False) else "unavailable"
            },
            "integration_managers": {
                "faction_integration": "active",
                "character_integration": "active",
                "quest_integration": "active",
                "world_state_integration": "active"
            },
            "last_check": status.get("last_check"),
            "recommendations": []
        }
        
        # Add recommendations based on missing services
        if not status.get("faction_service_available", False):
            health_status["recommendations"].append("Consider implementing faction service for full integration")
        if not status.get("character_service_available", False):
            health_status["recommendations"].append("Consider implementing character service for full integration")
        if not status.get("quest_service_available", False):
            health_status["recommendations"].append("Consider implementing quest service for full integration")
        if not status.get("world_state_service_available", False):
            health_status["recommendations"].append("Consider implementing world state service for full integration")
        
        if not health_status["recommendations"]:
            health_status["recommendations"].append("All integrations are functioning optimally")
        
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking integration health: {str(e)}") 