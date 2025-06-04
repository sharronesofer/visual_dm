"""
Alliance routes module.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from backend.infrastructure.database import get_db_session

from backend.systems.faction.models.alliance import (
    Alliance,
    AllianceMember,
    AllianceProposal,
    AllianceType,
    AllianceStatus,
    MembershipStatus
)
from backend.infrastructure.repositories.faction.alliance_repository import AllianceRepository
from backend.systems.faction.services.alliance_service import AllianceService


router = APIRouter(prefix="/alliances", tags=["alliances"])


def get_alliance_service(db: Session = Depends(get_db_session)) -> AllianceService:
    """Dependency to get alliance service instance"""
    return AllianceService(db)


def get_alliance_repository(db: Session = Depends(get_db_session)) -> AllianceRepository:
    """Dependency to get alliance repository instance"""
    return AllianceRepository(db)


# Alliance Management Endpoints

@router.post("/", response_model=AllianceResponse)
async def create_alliance(
    request: CreateAllianceRequest,
    service: AllianceService = Depends(get_alliance_service)
):
    """
    Create a new faction alliance.
    
    Args:
        request: Alliance creation request
        service: Alliance service instance
        
    Returns:
        Created alliance data
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        alliance = service.create_alliance(request)
        return AllianceResponse.model_validate(alliance.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alliance: {str(e)}")


@router.get("/{alliance_id}", response_model=AllianceResponse)
async def get_alliance(
    alliance_id: UUID = Path(..., description="Alliance ID"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Get alliance details by ID.
    
    Args:
        alliance_id: Alliance ID
        repository: Alliance repository instance
        
    Returns:
        Alliance data
        
    Raises:
        HTTPException: If alliance not found
    """
    alliance = repository.get_alliance_by_id(alliance_id)
    if not alliance:
        raise HTTPException(status_code=404, detail="Alliance not found")
    
    return AllianceResponse.model_validate(alliance.to_dict())


@router.get("/", response_model=AllianceListResponse)
async def list_alliances(
    status: Optional[AllianceStatus] = Query(None, description="Filter by alliance status"),
    alliance_type: Optional[AllianceType] = Query(None, description="Filter by alliance type"),
    faction_id: Optional[UUID] = Query(None, description="Filter by faction involvement"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    List alliances with optional filtering.
    
    Args:
        status: Optional status filter
        alliance_type: Optional type filter
        faction_id: Optional faction filter
        page: Page number
        size: Page size
        repository: Alliance repository instance
        
    Returns:
        Paginated list of alliances
    """
    try:
        # Get alliances based on filters
        if faction_id:
            alliances = repository.get_alliances_by_faction(faction_id)
        elif status:
            alliances = repository.get_alliances_by_status(status)
        elif alliance_type:
            alliances = repository.get_alliances_by_type(alliance_type)
        else:
            alliances = repository.get_active_alliances()
        
        # Apply pagination
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_alliances = alliances[start_idx:end_idx]
        
        # Convert to response models
        alliance_responses = [
            AllianceResponse.model_validate(alliance.to_dict())
            for alliance in paginated_alliances
        ]
        
        return AllianceListResponse(
            items=alliance_responses,
            total=len(alliances),
            page=page,
            size=size,
            has_next=end_idx < len(alliances),
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list alliances: {str(e)}")


@router.put("/{alliance_id}", response_model=AllianceResponse)
async def update_alliance(
    alliance_id: UUID = Path(..., description="Alliance ID"),
    request: UpdateAllianceRequest = ...,
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Update an existing alliance.
    
    Args:
        alliance_id: Alliance ID
        request: Alliance update request
        repository: Alliance repository instance
        
    Returns:
        Updated alliance data
        
    Raises:
        HTTPException: If alliance not found or update fails
    """
    alliance = repository.get_alliance_by_id(alliance_id)
    if not alliance:
        raise HTTPException(status_code=404, detail="Alliance not found")
    
    try:
        # Update fields if provided
        if request.name is not None:
            alliance.name = request.name
        if request.status is not None:
            alliance.status = request.status.value
        if request.description is not None:
            alliance.description = request.description
        if request.terms is not None:
            alliance.terms = request.terms
        if request.mutual_obligations is not None:
            alliance.mutual_obligations = request.mutual_obligations
        if request.shared_enemies is not None:
            alliance.shared_enemies = request.shared_enemies
        if request.shared_goals is not None:
            alliance.shared_goals = request.shared_goals
        if request.end_date is not None:
            alliance.end_date = request.end_date
        if request.auto_renew is not None:
            alliance.auto_renew = request.auto_renew
        
        updated_alliance = repository.update_alliance(alliance)
        return AllianceResponse.model_validate(updated_alliance.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alliance: {str(e)}")


@router.delete("/{alliance_id}")
async def delete_alliance(
    alliance_id: UUID = Path(..., description="Alliance ID"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Delete an alliance.
    
    Args:
        alliance_id: Alliance ID
        repository: Alliance repository instance
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If alliance not found
    """
    success = repository.delete_alliance(alliance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alliance not found")
    
    return {"message": "Alliance deleted successfully"}


# Alliance Formation and Analysis Endpoints

@router.post("/evaluate-opportunity")
async def evaluate_alliance_opportunity(
    faction_a_id: UUID,
    faction_b_id: UUID,
    common_threat_ids: Optional[List[UUID]] = None,
    alliance_type: Optional[AllianceType] = None,
    service: AllianceService = Depends(get_alliance_service)
):
    """
    Evaluate the potential for alliance formation between two factions.
    
    Args:
        faction_a_id: First faction ID
        faction_b_id: Second faction ID
        common_threat_ids: Optional list of common enemy faction IDs
        alliance_type: Optional specific alliance type to evaluate
        service: Alliance service instance
        
    Returns:
        Alliance evaluation results
    """
    try:
        evaluation = service.evaluate_alliance_opportunity(
            faction_a_id=faction_a_id,
            faction_b_id=faction_b_id,
            common_threat_ids=common_threat_ids,
            alliance_type=alliance_type
        )
        return evaluation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate alliance opportunity: {str(e)}")


@router.get("/faction/{faction_id}/potential-partners")
async def get_potential_alliance_partners(
    faction_id: UUID = Path(..., description="Faction ID"),
    shared_enemy_id: Optional[UUID] = Query(None, description="Shared enemy faction ID"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Find potential alliance partners for a faction.
    
    Args:
        faction_id: Faction ID
        shared_enemy_id: Optional shared enemy to find partners against
        repository: Alliance repository instance
        
    Returns:
        List of potential partner faction IDs
    """
    try:
        partners = repository.find_potential_alliance_partners(
            faction_id=faction_id,
            shared_enemy_id=shared_enemy_id
        )
        return {"potential_partners": partners}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find potential partners: {str(e)}")


# Betrayal Analysis and Management Endpoints

@router.post("/betrayal/evaluate")
async def evaluate_betrayal_probability(
    alliance_id: UUID,
    faction_id: UUID,
    external_factors: Optional[Dict[str, Any]] = None,
    service: AllianceService = Depends(get_alliance_service)
):
    """
    Evaluate the probability of a faction betraying an alliance.
    
    Args:
        alliance_id: Alliance ID
        faction_id: Faction ID to evaluate
        external_factors: Optional external circumstances
        service: Alliance service instance
        
    Returns:
        Betrayal probability analysis
    """
    try:
        analysis = service.evaluate_betrayal_probability(
            alliance_id=alliance_id,
            faction_id=faction_id,
            external_factors=external_factors
        )
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate betrayal probability: {str(e)}")


@router.post("/betrayal/execute")
async def execute_betrayal(
    alliance_id: UUID,
    betrayer_faction_id: UUID,
    betrayal_type: str,
    description: str,
    reason: BetrayalReason,
    service: AllianceService = Depends(get_alliance_service)
):
    """
    Execute a betrayal action.
    
    Args:
        alliance_id: Alliance being betrayed
        betrayer_faction_id: Faction committing betrayal
        betrayal_type: Type of betrayal
        description: Description of betrayal
        reason: Primary reason for betrayal
        service: Alliance service instance
        
    Returns:
        Betrayal event data
    """
    try:
        betrayal = service.execute_betrayal(
            alliance_id=alliance_id,
            betrayer_faction_id=betrayer_faction_id,
            betrayal_type=betrayal_type,
            description=description,
            reason=reason
        )
        return BetrayalResponse.model_validate(betrayal.__dict__)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute betrayal: {str(e)}")


@router.get("/betrayal/{betrayal_id}", response_model=BetrayalResponse)
async def get_betrayal(
    betrayal_id: UUID = Path(..., description="Betrayal ID"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Get betrayal event details by ID.
    
    Args:
        betrayal_id: Betrayal ID
        repository: Alliance repository instance
        
    Returns:
        Betrayal event data
        
    Raises:
        HTTPException: If betrayal not found
    """
    betrayal = repository.get_betrayal_by_id(betrayal_id)
    if not betrayal:
        raise HTTPException(status_code=404, detail="Betrayal not found")
    
    return BetrayalResponse.model_validate(betrayal.__dict__)


@router.get("/betrayal/alliance/{alliance_id}")
async def get_alliance_betrayals(
    alliance_id: UUID = Path(..., description="Alliance ID"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Get all betrayal events for a specific alliance.
    
    Args:
        alliance_id: Alliance ID
        repository: Alliance repository instance
        
    Returns:
        List of betrayal events
    """
    try:
        betrayals = repository.get_betrayals_by_alliance(alliance_id)
        betrayal_responses = [
            BetrayalResponse.model_validate(betrayal.__dict__)
            for betrayal in betrayals
        ]
        return {"betrayals": betrayal_responses}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alliance betrayals: {str(e)}")


@router.get("/betrayal/faction/{faction_id}")
async def get_faction_betrayals(
    faction_id: UUID = Path(..., description="Faction ID"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Get all betrayal events involving a specific faction.
    
    Args:
        faction_id: Faction ID
        repository: Alliance repository instance
        
    Returns:
        List of betrayal events
    """
    try:
        betrayals = repository.get_betrayals_by_faction(faction_id)
        betrayal_responses = [
            BetrayalResponse.model_validate(betrayal.__dict__)
            for betrayal in betrayals
        ]
        return {"betrayals": betrayal_responses}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get faction betrayals: {str(e)}")


# Alliance Member Management Endpoints

@router.post("/{alliance_id}/members/{faction_id}")
async def add_faction_to_alliance(
    alliance_id: UUID = Path(..., description="Alliance ID"),
    faction_id: UUID = Path(..., description="Faction ID to add"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Add a faction to an existing alliance.
    
    Args:
        alliance_id: Alliance ID
        faction_id: Faction ID to add
        repository: Alliance repository instance
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If operation fails
    """
    success = repository.add_faction_to_alliance(alliance_id, faction_id)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Failed to add faction to alliance (not found or already a member)"
        )
    
    return {"message": "Faction added to alliance successfully"}


@router.delete("/{alliance_id}/members/{faction_id}")
async def remove_faction_from_alliance(
    alliance_id: UUID = Path(..., description="Alliance ID"),
    faction_id: UUID = Path(..., description="Faction ID to remove"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Remove a faction from an alliance.
    
    Args:
        alliance_id: Alliance ID
        faction_id: Faction ID to remove
        repository: Alliance repository instance
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If operation fails
    """
    success = repository.remove_faction_from_alliance(alliance_id, faction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alliance not found")
    
    return {"message": "Faction removed from alliance successfully"}


# Statistics and Analytics Endpoints

@router.get("/statistics/overview")
async def get_alliance_statistics(
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Get overall alliance system statistics.
    
    Args:
        repository: Alliance repository instance
        
    Returns:
        Alliance system statistics
    """
    try:
        stats = repository.get_alliance_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alliance statistics: {str(e)}")


@router.get("/faction/{faction_id}/statistics")
async def get_faction_alliance_statistics(
    faction_id: UUID = Path(..., description="Faction ID"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Get alliance-related statistics for a specific faction.
    
    Args:
        faction_id: Faction ID
        repository: Alliance repository instance
        
    Returns:
        Faction alliance statistics
    """
    try:
        alliance_count = repository.get_faction_alliance_count(faction_id)
        betrayal_count = repository.get_faction_betrayal_count(faction_id)
        
        return {
            "faction_id": str(faction_id),
            "active_alliance_count": alliance_count,
            "betrayal_count": betrayal_count,
            "trustworthiness_score": max(0.0, 1.0 - (betrayal_count * 0.1))  # Simple trust calculation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get faction statistics: {str(e)}")


@router.get("/betrayal/recent")
async def get_recent_betrayals(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of betrayals to return"),
    repository: AllianceRepository = Depends(get_alliance_repository)
):
    """
    Get the most recent betrayal events.
    
    Args:
        limit: Maximum number of betrayals to return
        repository: Alliance repository instance
        
    Returns:
        List of recent betrayal events
    """
    try:
        betrayals = repository.get_recent_betrayals(limit)
        betrayal_responses = [
            BetrayalResponse.model_validate(betrayal.__dict__)
            for betrayal in betrayals
        ]
        return {"recent_betrayals": betrayal_responses}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent betrayals: {str(e)}") 