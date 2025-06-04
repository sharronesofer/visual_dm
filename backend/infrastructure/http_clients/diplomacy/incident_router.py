"""
Incident Router

Specialized router for diplomatic incident management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.systems.diplomacy.services.unified_diplomacy_service import (
    UnifiedDiplomacyService, get_unified_diplomacy_service
)
from backend.systems.diplomacy.models.core_models import (
    DiplomaticIncidentType, DiplomaticIncidentSeverity,
    UltimatumStatus, TreatyViolationType
)

# Create incident router
incident_router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
    responses={404: {"description": "Incident not found"}}
)

@incident_router.get("/")
async def list_diplomatic_incidents(
    faction_id: Optional[UUID] = None,
    incident_type: Optional[DiplomaticIncidentType] = None,
    severity: Optional[DiplomaticIncidentSeverity] = None,
    resolved_only: Optional[bool] = None,
    limit: int = 50,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """List diplomatic incidents with optional filtering"""
    try:
        incidents = service.get_diplomatic_incidents(
            faction_id=faction_id,
            incident_type=incident_type,
            limit=limit
        )
        
        # Apply additional filters
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        if resolved_only is not None:
            incidents = [i for i in incidents if i.resolved == resolved_only]
            
        return [incident.to_dict() for incident in incidents]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list diplomatic incidents: {str(e)}"
        )

@incident_router.get("/{incident_id}")
async def get_incident_details(
    incident_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Get detailed information about a specific diplomatic incident"""
    try:
        incident = service.get_diplomatic_incident(incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diplomatic incident {incident_id} not found"
            )
        return incident.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get incident details: {str(e)}"
        )

@incident_router.post("/")
async def report_diplomatic_incident(
    incident_type: DiplomaticIncidentType,
    faction_a_id: UUID,
    faction_b_id: Optional[UUID] = None,
    severity: DiplomaticIncidentSeverity = DiplomaticIncidentSeverity.MINOR,
    description: str = "",
    location: Optional[str] = None,
    evidence: Optional[Dict[str, Any]] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Report a new diplomatic incident"""
    try:
        incident = service.report_diplomatic_incident(
            incident_type=incident_type,
            faction_a_id=faction_a_id,
            faction_b_id=faction_b_id,
            severity=severity,
            description=description,
            location=location,
            evidence=evidence or {}
        )
        return incident.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to report diplomatic incident: {str(e)}"
        )

@incident_router.put("/{incident_id}/resolve")
async def resolve_incident(
    incident_id: UUID,
    resolution: str,
    resolved_by_faction_id: Optional[UUID] = None,
    compensation: Optional[Dict[str, Any]] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Resolve a diplomatic incident"""
    try:
        result = service.resolve_diplomatic_incident(
            incident_id=incident_id,
            resolution=resolution,
            resolved_by_faction_id=resolved_by_faction_id,
            compensation=compensation or {}
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve incident: {str(e)}"
        )

@incident_router.post("/ultimatums")
async def issue_ultimatum(
    issuing_faction_id: UUID,
    target_faction_id: UUID,
    demands: Dict[str, Any],
    deadline_hours: int = 24,
    consequences: Optional[Dict[str, Any]] = None,
    related_incident_id: Optional[UUID] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Issue an ultimatum to another faction"""
    try:
        ultimatum = service.issue_ultimatum(
            issuing_faction_id=issuing_faction_id,
            target_faction_id=target_faction_id,
            demands=demands,
            deadline_hours=deadline_hours,
            consequences=consequences or {},
            related_incident_id=related_incident_id
        )
        return ultimatum.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to issue ultimatum: {str(e)}"
        )

@incident_router.get("/ultimatums")
async def list_ultimatums(
    faction_id: Optional[UUID] = None,
    status_filter: Optional[UltimatumStatus] = None,
    active_only: bool = True,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """List ultimatums with optional filtering"""
    try:
        ultimatums = service.get_ultimatums(
            faction_id=faction_id,
            status_filter=status_filter,
            active_only=active_only
        )
        return [ultimatum.to_dict() for ultimatum in ultimatums]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list ultimatums: {str(e)}"
        )

@incident_router.put("/ultimatums/{ultimatum_id}/respond")
async def respond_to_ultimatum(
    ultimatum_id: UUID,
    response: str,  # "accept", "reject", "negotiate"
    responding_faction_id: UUID,
    counter_proposal: Optional[Dict[str, Any]] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Respond to an ultimatum"""
    try:
        result = service.respond_to_ultimatum(
            ultimatum_id=ultimatum_id,
            response=response,
            responding_faction_id=responding_faction_id,
            counter_proposal=counter_proposal or {}
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to respond to ultimatum: {str(e)}"
        )

@incident_router.post("/sanctions")
async def impose_sanctions(
    imposing_faction_id: UUID,
    target_faction_id: UUID,
    sanction_type: str,
    restrictions: Dict[str, Any],
    duration_days: Optional[int] = None,
    reason: str = "",
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Impose sanctions on another faction"""
    try:
        sanction = service.impose_sanctions(
            imposing_faction_id=imposing_faction_id,
            target_faction_id=target_faction_id,
            sanction_type=sanction_type,
            restrictions=restrictions,
            duration_days=duration_days,
            reason=reason
        )
        return sanction.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to impose sanctions: {str(e)}"
        )

@incident_router.get("/sanctions")
async def list_sanctions(
    faction_id: Optional[UUID] = None,
    active_only: bool = True,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """List sanctions with optional filtering"""
    try:
        sanctions = service.get_sanctions(
            faction_id=faction_id,
            active_only=active_only
        )
        return [sanction.to_dict() for sanction in sanctions]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sanctions: {str(e)}"
        )

@incident_router.get("/faction/{faction_id}")
async def get_faction_incidents(
    faction_id: UUID,
    incident_type: Optional[DiplomaticIncidentType] = None,
    resolved_only: Optional[bool] = None,
    limit: int = 25,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all incidents involving a specific faction"""
    try:
        incidents = service.get_diplomatic_incidents(
            faction_id=faction_id,
            incident_type=incident_type,
            limit=limit
        )
        
        if resolved_only is not None:
            incidents = [i for i in incidents if i.resolved == resolved_only]
            
        return [incident.to_dict() for incident in incidents]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get faction incidents: {str(e)}"
        ) 