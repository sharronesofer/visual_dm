"""
Treaty Router

Specialized router for treaty-related endpoints and operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.systems.diplomacy.services.unified_diplomacy_service import (
    UnifiedDiplomacyService, get_unified_diplomacy_service
)
from backend.systems.diplomacy.models.core_models import (
    TreatyType, TreatyStatus, TreatyViolationType
)

# Create treaty router
treaty_router = APIRouter(
    prefix="/treaties",
    tags=["treaties"],
    responses={404: {"description": "Treaty not found"}}
)

@treaty_router.get("/")
async def list_treaties(
    faction_id: Optional[UUID] = None,
    treaty_type: Optional[TreatyType] = None,
    status: Optional[TreatyStatus] = None,
    active_only: bool = True,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """List treaties with optional filtering"""
    try:
        if faction_id:
            treaties = service.get_faction_treaties(faction_id, active_only=active_only)
        else:
            treaties = service.get_all_treaties(active_only=active_only)
        
        # Apply additional filters
        if treaty_type:
            treaties = [t for t in treaties if t.treaty_type == treaty_type]
        if status:
            treaties = [t for t in treaties if t.status == status]
            
        return [treaty.to_dict() for treaty in treaties]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list treaties: {str(e)}"
        )

@treaty_router.get("/{treaty_id}")
async def get_treaty_details(
    treaty_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Get detailed information about a specific treaty"""
    try:
        treaty = service.get_treaty(treaty_id)
        if not treaty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treaty {treaty_id} not found"
            )
        
        # Get additional details like violations
        violations = service.get_treaty_violations(treaty_id)
        
        result = treaty.to_dict()
        result["violations"] = [v.to_dict() for v in violations]
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get treaty details: {str(e)}"
        )

@treaty_router.post("/")
async def create_new_treaty(
    faction_a_id: UUID,
    faction_b_id: UUID,
    treaty_type: TreatyType,
    terms: Dict[str, Any],
    duration_days: Optional[int] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Create a new treaty between two factions"""
    try:
        treaty = service.create_treaty(
            faction_a_id=faction_a_id,
            faction_b_id=faction_b_id,
            treaty_type=treaty_type,
            terms=terms,
            duration_days=duration_days
        )
        return treaty.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create treaty: {str(e)}"
        )

@treaty_router.put("/{treaty_id}/ratify")
async def ratify_treaty(
    treaty_id: UUID,
    faction_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Ratify a treaty by one of the involved factions"""
    try:
        result = service.ratify_treaty(treaty_id, faction_id)
        return {"success": result, "treaty_id": str(treaty_id)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ratify treaty: {str(e)}"
        )

@treaty_router.put("/{treaty_id}/terminate")
async def terminate_treaty(
    treaty_id: UUID,
    faction_id: UUID,
    reason: str = "No reason provided",
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Terminate a treaty"""
    try:
        result = service.terminate_treaty(treaty_id, faction_id, reason)
        return {"success": result, "treaty_id": str(treaty_id), "reason": reason}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to terminate treaty: {str(e)}"
        )

@treaty_router.post("/{treaty_id}/violations")
async def report_treaty_violation(
    treaty_id: UUID,
    violation_type: TreatyViolationType,
    reporting_faction_id: UUID,
    description: str,
    evidence: Optional[Dict[str, Any]] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Report a treaty violation"""
    try:
        violation = service.report_treaty_violation(
            treaty_id=treaty_id,
            violation_type=violation_type,
            reporting_faction_id=reporting_faction_id,
            description=description,
            evidence=evidence or {}
        )
        return violation.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to report treaty violation: {str(e)}"
        )

@treaty_router.get("/{treaty_id}/violations")
async def get_treaty_violations(
    treaty_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all violations for a specific treaty"""
    try:
        violations = service.get_treaty_violations(treaty_id)
        return [violation.to_dict() for violation in violations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get treaty violations: {str(e)}"
        )

@treaty_router.get("/faction/{faction_id}")
async def get_faction_treaties(
    faction_id: UUID,
    active_only: bool = True,
    treaty_type: Optional[TreatyType] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all treaties involving a specific faction"""
    try:
        treaties = service.get_faction_treaties(faction_id, active_only=active_only)
        
        # Filter by treaty type if specified
        if treaty_type:
            treaties = [t for t in treaties if t.treaty_type == treaty_type]
            
        return [treaty.to_dict() for treaty in treaties]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get faction treaties: {str(e)}"
        ) 