"""
Relationship Router

Specialized router for faction relationship management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.systems.diplomacy.services.unified_diplomacy_service import (
    UnifiedDiplomacyService, get_unified_diplomacy_service
)
from backend.systems.diplomacy.models.core_models import DiplomaticStatus

# Create relationship router
relationship_router = APIRouter(
    prefix="/relationships",
    tags=["relationships"],
    responses={404: {"description": "Relationship not found"}}
)

@relationship_router.get("/")
async def list_all_relationships(
    status_filter: Optional[DiplomaticStatus] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """List all faction relationships"""
    try:
        relationships = service.get_all_relationships()
        
        # Filter by status if specified
        if status_filter:
            relationships = [r for r in relationships if r.status == status_filter]
            
        return [relationship.to_dict() for relationship in relationships]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list relationships: {str(e)}"
        )

@relationship_router.get("/{faction_a_id}/{faction_b_id}")
async def get_specific_relationship(
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
                detail=f"Relationship between {faction_a_id} and {faction_b_id} not found"
            )
        return relationship.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get relationship: {str(e)}"
        )

@relationship_router.post("/{faction_a_id}/{faction_b_id}")
async def establish_relationship(
    faction_a_id: UUID,
    faction_b_id: UUID,
    initial_status: DiplomaticStatus = DiplomaticStatus.NEUTRAL,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Establish a new relationship between two factions"""
    try:
        relationship = service.establish_relationship(
            faction_a_id, faction_b_id, initial_status
        )
        return relationship.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to establish relationship: {str(e)}"
        )

@relationship_router.put("/{faction_a_id}/{faction_b_id}/status")
async def update_relationship_status(
    faction_a_id: UUID,
    faction_b_id: UUID,
    new_status: DiplomaticStatus,
    reason: Optional[str] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Update the status of a relationship between two factions"""
    try:
        relationship = service.update_relationship_status(
            faction_a_id, faction_b_id, new_status, reason
        )
        return relationship.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update relationship status: {str(e)}"
        )

@relationship_router.get("/faction/{faction_id}")
async def get_faction_relationships(
    faction_id: UUID,
    status_filter: Optional[DiplomaticStatus] = None,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all relationships for a specific faction"""
    try:
        relationships = service.get_faction_relationships(faction_id)
        
        # Filter by status if specified
        if status_filter:
            relationships = [r for r in relationships if r.status == status_filter]
            
        return [relationship.to_dict() for relationship in relationships]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get faction relationships: {str(e)}"
        )

@relationship_router.get("/faction/{faction_id}/allies")
async def get_faction_allies(
    faction_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all allied factions for a specific faction"""
    try:
        relationships = service.get_faction_relationships(faction_id)
        allies = [
            r for r in relationships 
            if r.status == DiplomaticStatus.ALLIED
        ]
        return [relationship.to_dict() for relationship in allies]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get faction allies: {str(e)}"
        )

@relationship_router.get("/faction/{faction_id}/enemies")
async def get_faction_enemies(
    faction_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> List[Dict[str, Any]]:
    """Get all hostile factions for a specific faction"""
    try:
        relationships = service.get_faction_relationships(faction_id)
        enemies = [
            r for r in relationships 
            if r.status == DiplomaticStatus.HOSTILE
        ]
        return [relationship.to_dict() for relationship in enemies]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get faction enemies: {str(e)}"
        )

@relationship_router.get("/faction/{faction_id}/summary")
async def get_faction_relationship_summary(
    faction_id: UUID,
    service: UnifiedDiplomacyService = Depends(get_unified_diplomacy_service)
) -> Dict[str, Any]:
    """Get a summary of all relationships for a faction"""
    try:
        relationships = service.get_faction_relationships(faction_id)
        
        summary = {
            "faction_id": str(faction_id),
            "total_relationships": len(relationships),
            "by_status": {}
        }
        
        # Count relationships by status
        for relationship in relationships:
            status = relationship.status.value
            if status not in summary["by_status"]:
                summary["by_status"][status] = 0
            summary["by_status"][status] += 1
        
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get faction relationship summary: {str(e)}"
        ) 