"""
Faction succession router module.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from backend.systems.faction.services.succession_service import FactionSuccessionService
from backend.infrastructure.repositories.faction.succession_repository import SuccessionRepository
from backend.systems.faction.models.succession import (
    CreateSuccessionCrisisRequest,
    UpdateSuccessionCrisisRequest,
    AddCandidateRequest,
    SuccessionCrisisResponse,
    SuccessionCrisisListResponse,
    SuccessionType,
    SuccessionCrisisStatus,
    SuccessionTrigger,
    SuccessionCandidate
)
from backend.infrastructure.schemas.faction.succession_schemas import (
    SuccessionAnalysisRequest,
    SuccessionAnalysisResponse,
    TriggerSuccessionCrisisRequest,
    AdvanceSuccessionCrisisRequest,
    ResolveSuccessionCrisisRequest,
    InterferenceRequest,
    CandidateActionRequest,
    SuccessionMetricsResponse,
    FactionStabilityRequest,
    SuccessionSimulationRequest,
    SuccessionSimulationResponse,
    BatchSuccessionAnalysisRequest,
    BatchSuccessionAnalysisResponse,
    SuccessionTriggerRequest,
    SuccessionTriggerResponse,
    SuccessionCandidateRequest,
    SuccessionCandidateResponse,
    SuccessionEventRequest,
    SuccessionEventResponse,
    SuccessionOutcomeRequest,
    SuccessionOutcomeResponse,
    SuccessionHistoryRequest,
    SuccessionHistoryResponse
)
from backend.infrastructure.database import get_db_session

logger = logging.getLogger(__name__)

# Create router
succession_router = APIRouter(
    prefix="/succession",
    tags=["succession"],
    responses={404: {"description": "Not found"}}
)

# Dependency injection
def get_succession_service() -> FactionSuccessionService:
    """Get succession service instance"""
    return FactionSuccessionService()

def get_succession_repository() -> SuccessionRepository:
    """Get succession repository instance"""
    return SuccessionRepository()


@succession_router.post("/analyze", response_model=SuccessionAnalysisResponse)
async def analyze_faction_succession_vulnerability(
    request: SuccessionAnalysisRequest,
    succession_service: FactionSuccessionService = Depends(get_succession_service),
    db: Session = Depends(get_db_session)
) -> SuccessionAnalysisResponse:
    """
    Analyze a faction's vulnerability to succession crises
    """
    try:
        # Get faction
        from backend.infrastructure.models.faction.models import FactionEntity
        faction = db.query(FactionEntity).filter(
            FactionEntity.id == request.faction_id
        ).first()
        
        if not faction:
            raise HTTPException(status_code=404, detail="Faction not found")
        
        # Calculate vulnerability
        vulnerability_score = succession_service.calculate_succession_vulnerability(faction)
        succession_type = succession_service.determine_succession_type(faction)
        
        # Generate potential triggers analysis
        potential_triggers = []
        for trigger in SuccessionTrigger:
            if trigger in request.simulate_triggers or not request.simulate_triggers:
                should_trigger = succession_service.should_trigger_crisis(faction, trigger)
                potential_triggers.append({
                    "trigger": trigger.value,
                    "probability": 0.8 if should_trigger else 0.2,
                    "description": f"Analysis for {trigger.value}"
                })
        
        # Get stability factors
        hidden_attrs = faction.get_hidden_attributes()
        stability_factors = {
            "hidden_ambition": hidden_attrs["hidden_ambition"],
            "hidden_integrity": hidden_attrs["hidden_integrity"],
            "hidden_discipline": hidden_attrs["hidden_discipline"],
            "hidden_impulsivity": hidden_attrs["hidden_impulsivity"],
            "hidden_pragmatism": hidden_attrs["hidden_pragmatism"],
            "hidden_resilience": hidden_attrs["hidden_resilience"]
        }
        
        response = SuccessionAnalysisResponse(
            faction_id=faction.id,
            faction_name=faction.name,
            succession_type=succession_type,
            vulnerability_score=vulnerability_score,
            potential_triggers=potential_triggers,
            potential_candidates=[],  # Would be populated by scanning faction members
            stability_factors=stability_factors,
            succession_rules={"type": succession_type.value},
            leadership_structure={"current_system": "placeholder"}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing succession vulnerability: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@succession_router.post("/trigger", response_model=SuccessionCrisisResponse)
async def trigger_succession_crisis(
    request: TriggerSuccessionCrisisRequest,
    succession_service: FactionSuccessionService = Depends(get_succession_service),
    db: Session = Depends(get_db_session)
) -> SuccessionCrisisResponse:
    """
    Trigger a succession crisis for a faction
    """
    try:
        # Create succession crisis request
        create_request = CreateSuccessionCrisisRequest(
            faction_id=request.faction_id,
            trigger=request.trigger,
            previous_leader_id=request.previous_leader_id,
            metadata=request.trigger_details
        )
        
        # Create the crisis
        crisis = succession_service.create_succession_crisis(db, create_request)
        
        # Convert to response model
        response = SuccessionCrisisResponse(
            id=crisis.id,
            faction_id=crisis.faction_id,
            faction_name=crisis.faction_name,
            succession_type=SuccessionType(crisis.succession_type),
            status=SuccessionCrisisStatus(crisis.status),
            trigger=SuccessionTrigger(crisis.trigger),
            crisis_start=crisis.crisis_start,
            crisis_end=crisis.crisis_end,
            estimated_duration=crisis.estimated_duration,
            previous_leader_id=crisis.previous_leader_id,
            previous_leader_name=crisis.previous_leader_name,
            candidates=[],  # Empty initially
            winner_id=crisis.winner_id,
            faction_stability=crisis.faction_stability,
            instability_effects=crisis.instability_effects or {},
            interfering_factions=crisis.interfering_factions or [],
            interference_details=crisis.interference_details or {},
            resolution_method=crisis.resolution_method,
            faction_split=crisis.faction_split,
            new_factions=crisis.new_factions or [],
            created_at=crisis.created_at,
            updated_at=crisis.updated_at,
            metadata=crisis.metadata or {}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error triggering succession crisis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@succession_router.get("/", response_model=SuccessionCrisisListResponse)
async def list_succession_crises(
    status: Optional[str] = Query(None, description="Filter by status"),
    faction_id: Optional[UUID] = Query(None, description="Filter by faction ID"),
    active_only: bool = Query(False, description="Show only active crises"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    succession_repository: SuccessionRepository = Depends(get_succession_repository),
    db: Session = Depends(get_db_session)
) -> SuccessionCrisisListResponse:
    """
    List succession crises with optional filtering
    """
    try:
        # Get crises based on filters
        if active_only:
            crises = succession_repository.get_all_active_crises(db, limit=size)
        elif faction_id:
            crises = succession_repository.get_active_crises_for_faction(db, faction_id)
        elif status:
            status_enum = SuccessionCrisisStatus(status)
            crises = succession_repository.get_crises_by_status(db, status_enum, limit=size)
        else:
            # Get all crises (would need pagination in real implementation)
            crises = succession_repository.get_all_active_crises(db, limit=size)
        
        # Convert to response models
        crisis_responses = []
        for crisis in crises:
            crisis_response = SuccessionCrisisResponse(
                id=crisis.id,
                faction_id=crisis.faction_id,
                faction_name=crisis.faction_name,
                succession_type=SuccessionType(crisis.succession_type),
                status=SuccessionCrisisStatus(crisis.status),
                trigger=SuccessionTrigger(crisis.trigger),
                crisis_start=crisis.crisis_start,
                crisis_end=crisis.crisis_end,
                estimated_duration=crisis.estimated_duration,
                previous_leader_id=crisis.previous_leader_id,
                previous_leader_name=crisis.previous_leader_name,
                candidates=crisis.candidates or [],
                winner_id=crisis.winner_id,
                faction_stability=crisis.faction_stability,
                instability_effects=crisis.instability_effects or {},
                interfering_factions=crisis.interfering_factions or [],
                interference_details=crisis.interference_details or {},
                resolution_method=crisis.resolution_method,
                faction_split=crisis.faction_split,
                new_factions=crisis.new_factions or [],
                created_at=crisis.created_at,
                updated_at=crisis.updated_at,
                metadata=crisis.metadata or {}
            )
            crisis_responses.append(crisis_response)
        
        # Simple pagination (would be more sophisticated in production)
        total = len(crisis_responses)
        has_next = len(crises) == size  # Approximation
        has_prev = page > 1
        
        return SuccessionCrisisListResponse(
            items=crisis_responses,
            total=total,
            page=page,
            size=size,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Error listing succession crises: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@succession_router.get("/{crisis_id}", response_model=SuccessionCrisisResponse)
async def get_succession_crisis(
    crisis_id: UUID = Path(..., description="Succession crisis ID"),
    succession_repository: SuccessionRepository = Depends(get_succession_repository),
    db: Session = Depends(get_db_session)
) -> SuccessionCrisisResponse:
    """
    Get detailed information about a specific succession crisis
    """
    try:
        crisis = succession_repository.get_crisis_by_id(db, crisis_id)
        
        if not crisis:
            raise HTTPException(status_code=404, detail="Succession crisis not found")
        
        response = SuccessionCrisisResponse(
            id=crisis.id,
            faction_id=crisis.faction_id,
            faction_name=crisis.faction_name,
            succession_type=SuccessionType(crisis.succession_type),
            status=SuccessionCrisisStatus(crisis.status),
            trigger=SuccessionTrigger(crisis.trigger),
            crisis_start=crisis.crisis_start,
            crisis_end=crisis.crisis_end,
            estimated_duration=crisis.estimated_duration,
            previous_leader_id=crisis.previous_leader_id,
            previous_leader_name=crisis.previous_leader_name,
            candidates=crisis.candidates or [],
            winner_id=crisis.winner_id,
            faction_stability=crisis.faction_stability,
            instability_effects=crisis.instability_effects or {},
            interfering_factions=crisis.interfering_factions or [],
            interference_details=crisis.interference_details or {},
            resolution_method=crisis.resolution_method,
            faction_split=crisis.faction_split,
            new_factions=crisis.new_factions or [],
            created_at=crisis.created_at,
            updated_at=crisis.updated_at,
            metadata=crisis.metadata or {}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting succession crisis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@succession_router.post("/{crisis_id}/candidates", response_model=SuccessionCrisisResponse)
async def add_succession_candidate(
    crisis_id: UUID = Path(..., description="Succession crisis ID"),
    request: AddCandidateRequest = ...,
    succession_service: FactionSuccessionService = Depends(get_succession_service),
    db: Session = Depends(get_db_session)
) -> SuccessionCrisisResponse:
    """
    Add a candidate to an ongoing succession crisis
    """
    try:
        crisis = succession_service.add_succession_candidate(db, crisis_id, request)
        
        response = SuccessionCrisisResponse(
            id=crisis.id,
            faction_id=crisis.faction_id,
            faction_name=crisis.faction_name,
            succession_type=SuccessionType(crisis.succession_type),
            status=SuccessionCrisisStatus(crisis.status),
            trigger=SuccessionTrigger(crisis.trigger),
            crisis_start=crisis.crisis_start,
            crisis_end=crisis.crisis_end,
            estimated_duration=crisis.estimated_duration,
            previous_leader_id=crisis.previous_leader_id,
            previous_leader_name=crisis.previous_leader_name,
            candidates=crisis.candidates or [],
            winner_id=crisis.winner_id,
            faction_stability=crisis.faction_stability,
            instability_effects=crisis.instability_effects or {},
            interfering_factions=crisis.interfering_factions or [],
            interference_details=crisis.interference_details or {},
            resolution_method=crisis.resolution_method,
            faction_split=crisis.faction_split,
            new_factions=crisis.new_factions or [],
            created_at=crisis.created_at,
            updated_at=crisis.updated_at,
            metadata=crisis.metadata or {}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error adding succession candidate: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@succession_router.post("/{crisis_id}/advance", response_model=SuccessionCrisisResponse)
async def advance_succession_crisis(
    crisis_id: UUID = Path(..., description="Succession crisis ID"),
    request: AdvanceSuccessionCrisisRequest = ...,
    succession_service: FactionSuccessionService = Depends(get_succession_service),
    db: Session = Depends(get_db_session)
) -> SuccessionCrisisResponse:
    """
    Advance succession crisis by specified time period
    """
    try:
        crisis = succession_service.advance_succession_crisis(
            db, crisis_id, request.time_days
        )
        
        response = SuccessionCrisisResponse(
            id=crisis.id,
            faction_id=crisis.faction_id,
            faction_name=crisis.faction_name,
            succession_type=SuccessionType(crisis.succession_type),
            status=SuccessionCrisisStatus(crisis.status),
            trigger=SuccessionTrigger(crisis.trigger),
            crisis_start=crisis.crisis_start,
            crisis_end=crisis.crisis_end,
            estimated_duration=crisis.estimated_duration,
            previous_leader_id=crisis.previous_leader_id,
            previous_leader_name=crisis.previous_leader_name,
            candidates=crisis.candidates or [],
            winner_id=crisis.winner_id,
            faction_stability=crisis.faction_stability,
            instability_effects=crisis.instability_effects or {},
            interfering_factions=crisis.interfering_factions or [],
            interference_details=crisis.interference_details or {},
            resolution_method=crisis.resolution_method,
            faction_split=crisis.faction_split,
            new_factions=crisis.new_factions or [],
            created_at=crisis.created_at,
            updated_at=crisis.updated_at,
            metadata=crisis.metadata or {}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error advancing succession crisis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@succession_router.post("/{crisis_id}/resolve", response_model=SuccessionCrisisResponse)
async def resolve_succession_crisis(
    crisis_id: UUID = Path(..., description="Succession crisis ID"),
    request: ResolveSuccessionCrisisRequest = ...,
    succession_service: FactionSuccessionService = Depends(get_succession_service),
    db: Session = Depends(get_db_session)
) -> SuccessionCrisisResponse:
    """
    Manually resolve succession crisis with specified winner
    """
    try:
        crisis = succession_service.resolve_succession_crisis(
            db, crisis_id, request.winner_id, request.resolution_method
        )
        
        response = SuccessionCrisisResponse(
            id=crisis.id,
            faction_id=crisis.faction_id,
            faction_name=crisis.faction_name,
            succession_type=SuccessionType(crisis.succession_type),
            status=SuccessionCrisisStatus(crisis.status),
            trigger=SuccessionTrigger(crisis.trigger),
            crisis_start=crisis.crisis_start,
            crisis_end=crisis.crisis_end,
            estimated_duration=crisis.estimated_duration,
            previous_leader_id=crisis.previous_leader_id,
            previous_leader_name=crisis.previous_leader_name,
            candidates=crisis.candidates or [],
            winner_id=crisis.winner_id,
            faction_stability=crisis.faction_stability,
            instability_effects=crisis.instability_effects or {},
            interfering_factions=crisis.interfering_factions or [],
            interference_details=crisis.interference_details or {},
            resolution_method=crisis.resolution_method,
            faction_split=crisis.faction_split,
            new_factions=crisis.new_factions or [],
            created_at=crisis.created_at,
            updated_at=crisis.updated_at,
            metadata=crisis.metadata or {}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error resolving succession crisis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@succession_router.post("/{crisis_id}/interference", response_model=SuccessionCrisisResponse)
async def add_external_interference(
    crisis_id: UUID = Path(..., description="Succession crisis ID"),
    request: InterferenceRequest = ...,
    succession_service: FactionSuccessionService = Depends(get_succession_service),
    db: Session = Depends(get_db_session)
) -> SuccessionCrisisResponse:
    """
    Add external faction interference to succession crisis
    """
    try:
        crisis = succession_service.add_external_interference(
            db=db,
            crisis_id=crisis_id,
            interfering_faction_id=request.interfering_faction_id,
            interference_type=request.interference_type,
            candidate_id=request.candidate_id,
            resources=request.resources_committed
        )
        
        response = SuccessionCrisisResponse(
            id=crisis.id,
            faction_id=crisis.faction_id,
            faction_name=crisis.faction_name,
            succession_type=SuccessionType(crisis.succession_type),
            status=SuccessionCrisisStatus(crisis.status),
            trigger=SuccessionTrigger(crisis.trigger),
            crisis_start=crisis.crisis_start,
            crisis_end=crisis.crisis_end,
            estimated_duration=crisis.estimated_duration,
            previous_leader_id=crisis.previous_leader_id,
            previous_leader_name=crisis.previous_leader_name,
            candidates=crisis.candidates or [],
            winner_id=crisis.winner_id,
            faction_stability=crisis.faction_stability,
            instability_effects=crisis.instability_effects or {},
            interfering_factions=crisis.interfering_factions or [],
            interference_details=crisis.interference_details or {},
            resolution_method=crisis.resolution_method,
            faction_split=crisis.faction_split,
            new_factions=crisis.new_factions or [],
            created_at=crisis.created_at,
            updated_at=crisis.updated_at,
            metadata=crisis.metadata or {}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error adding external interference: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@succession_router.get("/metrics/overview", response_model=SuccessionMetricsResponse)
async def get_succession_metrics(
    succession_repository: SuccessionRepository = Depends(get_succession_repository),
    db: Session = Depends(get_db_session)
) -> SuccessionMetricsResponse:
    """
    Get comprehensive succession crisis metrics
    """
    try:
        metrics = succession_repository.get_succession_metrics(db)
        
        response = SuccessionMetricsResponse(
            total_crises=metrics["total_crises"],
            active_crises=metrics["active_crises"],
            resolved_crises=metrics["resolved_crises"],
            failed_crises=metrics["failed_crises"],
            faction_splits=metrics["faction_splits"],
            crisis_by_faction_type={},  # Would be populated with real data
            crisis_by_trigger={},  # Would be populated with real data
            crisis_by_succession_type={},  # Would be populated with real data
            average_duration_days=metrics["average_duration_days"],
            average_candidates=metrics["average_candidates"],
            average_stability_impact=metrics["average_stability_impact"]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting succession metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 