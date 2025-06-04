"""
Faction API router module.

This module provides API routes for faction system access with full hidden attributes support.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from backend.infrastructure.database.database import get_db
from datetime import datetime

from backend.systems.faction.services.services import FactionService
from backend.infrastructure.models.faction.models import (
    CreateFactionRequest,
    UpdateFactionRequest, 
    FactionResponse,
    FactionListResponse
)
from backend.infrastructure.utils.faction.faction_utils import (
    generate_faction_hidden_attributes,
    validate_hidden_attributes,
    calculate_faction_compatibility,
    calculate_faction_behavior_modifiers
)
from backend.infrastructure.shared.exceptions import (
    FactionNotFoundError,
    FactionConflictError
)
# Import diplomacy integration
from backend.systems.faction.services.diplomacy_integration_service import FactionDiplomacyIntegrationService
from backend.systems.diplomacy.services.unified_diplomacy_service import UnifiedDiplomacyService
from backend.infrastructure.config_loaders.faction_config_loader import get_faction_config

# Create router
faction_router = APIRouter(
    prefix="/factions",
    tags=["factions"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get faction service
def get_faction_service(db: Session = Depends(get_db)) -> FactionService:
    return FactionService(db)

# Dependency to get faction diplomacy service
def get_faction_diplomacy_service(db: Session = Depends(get_db)) -> FactionDiplomacyIntegrationService:
    faction_service = FactionService(db)
    diplomacy_service = UnifiedDiplomacyService(db_session=db)
    return FactionDiplomacyIntegrationService(faction_service, diplomacy_service)

@faction_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "faction_system", "features": ["hidden_attributes", "behavior_modifiers"]}

@faction_router.get("/stats", response_model=Dict[str, Any])
async def get_faction_statistics():
    """Get faction system statistics."""
    try:
        # Return basic statistics without database queries for now
        return {
            "total_factions": 0,
            "active_factions": 0,
            "inactive_factions": 0,
            "system_status": "operational",
            "note": "Database statistics temporarily disabled due to model mapping issues",
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving faction statistics: {str(e)}"
        )

@faction_router.post("/generate-hidden-attributes", response_model=Dict[str, int])
async def generate_random_hidden_attributes():
    """Generate a random set of hidden attributes for faction creation."""
    try:
        return generate_faction_hidden_attributes()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating hidden attributes: {str(e)}"
        )

@faction_router.get("/mock-list", response_model=FactionListResponse)
async def mock_list_factions():
    """Mock faction list endpoint for testing while resolving database issues."""
    try:
        # Mock faction data
        mock_faction = FactionResponse(
            id=UUID("12345678-1234-5678-9012-123456789abc"),
            name="Test Faction",
            description="A mock faction for testing purposes",
            status="active",
            properties={"location": "Test Region", "military_strength": 75},
            created_at=datetime.utcnow(),
            updated_at=None,
            is_active=True,
            hidden_ambition=4,
            hidden_integrity=3,
            hidden_discipline=5,
            hidden_impulsivity=2,
            hidden_pragmatism=4,
            hidden_resilience=3
        )
        
        return FactionListResponse(
            items=[mock_faction],
            total=1,
            page=1,
            size=50,
            has_next=False,
            has_prev=False
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating mock faction list: {str(e)}"
        )

@faction_router.get("/mock-behavior-modifiers", response_model=Dict[str, float])
async def mock_faction_behavior_modifiers():
    """Mock behavior modifiers endpoint for testing configuration system."""
    try:
        # Mock hidden attributes
        hidden_attrs = {
            "hidden_ambition": 4,
            "hidden_integrity": 3,
            "hidden_discipline": 5,
            "hidden_impulsivity": 2,
            "hidden_pragmatism": 4,
            "hidden_resilience": 3
        }
        
        modifiers = calculate_faction_behavior_modifiers(hidden_attrs)
        return modifiers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating mock behavior modifiers: {str(e)}"
        )

@faction_router.get("/mock-diplomatic-status", response_model=Dict[str, Any])
async def mock_faction_diplomatic_status():
    """Mock diplomatic status endpoint for testing diplomacy integration."""
    try:
        # Mock diplomatic status data
        return {
            "faction_id": "12345678-1234-5678-9012-123456789abc",
            "faction_name": "Test Faction",
            "diplomatic_stance": "neutral",
            "active_treaties": [
                {
                    "id": "treaty-001",
                    "name": "Trade Agreement with Northern Alliance",
                    "type": "economic",
                    "status": "active",
                    "partner_factions": ["faction-002", "faction-003"]
                }
            ],
            "current_negotiations": [
                {
                    "id": "negotiation-001",
                    "type": "military_alliance",
                    "partner": "faction-004",
                    "status": "in_progress",
                    "progress": 0.6
                }
            ],
            "relationship_summary": {
                "allies": 2,
                "neutral": 5,
                "hostile": 1,
                "at_war": 0
            },
            "trust_levels": {
                "faction-002": 0.8,
                "faction-003": 0.7,
                "faction-004": 0.5,
                "faction-005": -0.3
            },
            "betrayal_risks": {
                "faction-002": 0.1,
                "faction-003": 0.15,
                "faction-004": 0.3
            },
            "recent_events": [
                {
                    "event": "trade_agreement_signed",
                    "partner": "faction-002",
                    "date": datetime.utcnow().isoformat(),
                    "impact": "positive"
                }
            ],
            "diplomatic_priorities": [
                "Expand trade networks",
                "Secure military alliances",
                "Monitor hostile faction movements"
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating mock diplomatic status: {str(e)}"
        )

@faction_router.get("/mock-betrayal-calculations", response_model=Dict[str, Any])
async def mock_betrayal_calculations():
    """Mock betrayal risk calculations to demonstrate JSON configuration system."""
    try:
        # Mock hidden attributes for our test faction
        hidden_attrs = {
            "hidden_ambition": 4,
            "hidden_integrity": 3,
            "hidden_discipline": 5,
            "hidden_impulsivity": 2,
            "hidden_pragmatism": 4,
            "hidden_resilience": 3
        }
        
        config = get_faction_config()
        
        # Calculate betrayal probabilities for different scenarios
        scenarios = ["opportunity", "pressure", "fear", "desperation"]
        betrayal_calculations = {}
        
        for scenario in scenarios:
            probability = config.get_betrayal_probability(scenario, hidden_attrs)
            betrayal_calculations[scenario] = {
                "probability": round(probability, 3),
                "risk_level": "high" if probability > 0.7 else "medium" if probability > 0.4 else "low",
                "description": f"Betrayal probability under {scenario} scenario"
            }
        
        # Get alliance compatibility with different faction types
        alliance_types = config.get_alliance_types()
        alliance_compatibility = {}
        
        for alliance_type, alliance_config in alliance_types.items():
            compatibility = config.calculate_alliance_compatibility(hidden_attrs, alliance_config)
            alliance_compatibility[alliance_type] = {
                "compatibility_score": round(compatibility, 3),
                "suitability": "excellent" if compatibility > 0.8 else "good" if compatibility > 0.6 else "moderate" if compatibility > 0.4 else "poor",
                "description": alliance_config.get("description", f"{alliance_type} alliance")
            }
        
        return {
            "faction_id": "12345678-1234-5678-9012-123456789abc",
            "faction_name": "Test Faction",
            "hidden_attributes": hidden_attrs,
            "behavior_profile": {
                "ambition_level": "high" if hidden_attrs["hidden_ambition"] > 4 else "moderate",
                "integrity_level": "moderate",
                "discipline_level": "high" if hidden_attrs["hidden_discipline"] > 4 else "moderate",
                "decision_style": "calculated" if hidden_attrs["hidden_impulsivity"] < 3 else "reactive"
            },
            "betrayal_risk_analysis": betrayal_calculations,
            "alliance_compatibility": alliance_compatibility,
            "strategic_recommendations": [
                "Strong candidate for military alliances due to high discipline",
                "Moderate betrayal risk - monitor for opportunity scenarios",
                "Good at strategic planning but may be overly ambitious",
                "Reliable in economic partnerships"
            ],
            "configuration_source": "JSON configuration system",
            "calculation_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating mock betrayal analysis: {str(e)}"
        )

@faction_router.get("/", response_model=FactionListResponse)
async def list_factions(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    service: FactionService = Depends(get_faction_service)
):
    """List all factions with pagination and filters."""
    try:
        factions, total = await service.list_factions(
            page=page,
            size=size,
            status=status_filter,
            search=search
        )
        
        return FactionListResponse(
            items=factions,
            total=total,
            page=page,
            size=size,
            has_next=(page * size) < total,
            has_prev=page > 1
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing factions: {str(e)}"
        )

@faction_router.get("/{faction_id}", response_model=FactionResponse)
async def get_faction(
    faction_id: UUID,
    service: FactionService = Depends(get_faction_service)
):
    """Get a specific faction by ID."""
    try:
        faction = await service.get_faction_by_id(faction_id)
        if not faction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faction with ID {faction_id} not found"
            )
        return faction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving faction: {str(e)}"
        )

@faction_router.post("/", response_model=FactionResponse, status_code=status.HTTP_201_CREATED)
async def create_faction(
    request: CreateFactionRequest,
    service: FactionService = Depends(get_faction_service)
):
    """Create a new faction with optional hidden attributes."""
    try:
        return await service.create_faction(request)
    except FactionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating faction: {str(e)}"
        )

@faction_router.put("/{faction_id}", response_model=FactionResponse)
async def update_faction(
    faction_id: UUID,
    request: UpdateFactionRequest,
    service: FactionService = Depends(get_faction_service)
):
    """Update an existing faction, including hidden attributes."""
    try:
        return await service.update_faction(faction_id, request)
    except FactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except FactionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating faction: {str(e)}"
        )

@faction_router.delete("/{faction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faction(
    faction_id: UUID,
    service: FactionService = Depends(get_faction_service)
):
    """Soft delete a faction."""
    try:
        success = await service.delete_faction(faction_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faction with ID {faction_id} not found"
            )
    except HTTPException:
        raise
    except FactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting faction: {str(e)}"
        )

@faction_router.get("/{faction_id}/hidden-attributes", response_model=Dict[str, int])
async def get_faction_hidden_attributes(
    faction_id: UUID,
    service: FactionService = Depends(get_faction_service)
):
    """Get the hidden personality attributes for a faction."""
    try:
        faction = await service.get_faction_by_id(faction_id)
        if not faction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faction with ID {faction_id} not found"
            )
        
        return {
            "hidden_ambition": faction.hidden_ambition,
            "hidden_integrity": faction.hidden_integrity,
            "hidden_discipline": faction.hidden_discipline,
            "hidden_impulsivity": faction.hidden_impulsivity,
            "hidden_pragmatism": faction.hidden_pragmatism,
            "hidden_resilience": faction.hidden_resilience
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving faction hidden attributes: {str(e)}"
        )

@faction_router.get("/{faction_id}/behavior-modifiers", response_model=Dict[str, float])
async def get_faction_behavior_modifiers(
    faction_id: UUID,
    service: FactionService = Depends(get_faction_service)
):
    """Get calculated behavior modifiers based on faction's hidden attributes."""
    try:
        faction = await service.get_faction_by_id(faction_id)
        if not faction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faction with ID {faction_id} not found"
            )
        
        hidden_attrs = {
            "hidden_ambition": faction.hidden_ambition,
            "hidden_integrity": faction.hidden_integrity,
            "hidden_discipline": faction.hidden_discipline,
            "hidden_impulsivity": faction.hidden_impulsivity,
            "hidden_pragmatism": faction.hidden_pragmatism,
            "hidden_resilience": faction.hidden_resilience
        }
        
        modifiers = calculate_faction_behavior_modifiers(hidden_attrs)
        return modifiers
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating faction behavior modifiers: {str(e)}"
        )

# ===========================
# Diplomacy Integration Endpoints
# ===========================

@faction_router.get("/{faction_id}/diplomatic-status", response_model=Dict[str, Any])
async def get_faction_diplomatic_status(
    faction_id: UUID,
    service: FactionDiplomacyIntegrationService = Depends(get_faction_diplomacy_service)
):
    """Get comprehensive diplomatic status for a faction."""
    try:
        status_data = await service.get_faction_diplomatic_status(faction_id)
        if "error" in status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=status_data["error"]
            )
        return status_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving diplomatic status: {str(e)}"
        )

@faction_router.post("/{faction_id}/evaluate-alliance", response_model=Dict[str, Any])
async def evaluate_alliance_proposal(
    faction_id: UUID,
    target_faction_id: UUID = Query(..., description="Target faction for the alliance"),
    alliance_type: str = Query("military", description="Type of alliance (military, economic, etc.)"),
    service: FactionDiplomacyIntegrationService = Depends(get_faction_diplomacy_service)
):
    """Evaluate whether a faction would accept an alliance proposal."""
    try:
        evaluation = await service.evaluate_alliance_proposal(faction_id, target_faction_id, alliance_type)
        if "error" in evaluation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=evaluation["error"]
            )
        return evaluation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating alliance proposal: {str(e)}"
        )

@faction_router.post("/{faction_id}/propose-alliance", response_model=Dict[str, Any])
async def propose_alliance(
    faction_id: UUID,
    target_faction_id: UUID = Query(..., description="Target faction for the alliance"),
    alliance_type: str = Query("military", description="Type of alliance (military, economic, etc.)"),
    service: FactionDiplomacyIntegrationService = Depends(get_faction_diplomacy_service)
):
    """Propose an alliance between two factions."""
    try:
        proposal = await service.propose_alliance(faction_id, target_faction_id, alliance_type)
        if "error" in proposal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=proposal["error"]
            )
        return proposal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error proposing alliance: {str(e)}"
        )

@faction_router.get("/{faction_id}/betrayal-risk/{ally_id}", response_model=Dict[str, Any])
async def calculate_betrayal_risk(
    faction_id: UUID,
    ally_id: UUID,
    scenario: str = Query("opportunity", description="Betrayal scenario (opportunity, pressure, fear, desperation)"),
    service: FactionDiplomacyIntegrationService = Depends(get_faction_diplomacy_service)
):
    """Calculate the risk of a faction betraying an ally."""
    try:
        risk_data = await service.calculate_betrayal_risk(faction_id, ally_id, scenario)
        if "error" in risk_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=risk_data["error"]
            )
        return risk_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating betrayal risk: {str(e)}"
        )

@faction_router.get("/{faction_id}/stability-assessment", response_model=Dict[str, Any])
async def get_faction_stability_assessment(
    faction_id: UUID,
    service: FactionService = Depends(get_faction_service)
):
    """Get comprehensive stability assessment for a faction."""
    try:
        faction = await service.get_faction_by_id(faction_id)
        if not faction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faction with ID {faction_id} not found"
            )
        
        hidden_attrs = {
            "hidden_ambition": faction.hidden_ambition,
            "hidden_integrity": faction.hidden_integrity,
            "hidden_discipline": faction.hidden_discipline,
            "hidden_impulsivity": faction.hidden_impulsivity,
            "hidden_pragmatism": faction.hidden_pragmatism,
            "hidden_resilience": faction.hidden_resilience
        }
        
        # Core stability factors
        discipline_stability = faction.hidden_discipline / 10.0
        integrity_consistency = faction.hidden_integrity / 10.0
        resilience_factor = faction.hidden_resilience / 10.0
        
        # Risk factors
        impulsivity_risk = faction.hidden_impulsivity / 10.0
        ambition_overreach = max(0, (faction.hidden_ambition - 7)) / 3.0
        
        # Calculate overall stability (0.0-1.0)
        stability_score = (
            discipline_stability * 0.30 +
            integrity_consistency * 0.25 +
            resilience_factor * 0.25 +
            (1.0 - impulsivity_risk) * 0.10 +
            (1.0 - ambition_overreach) * 0.10
        )
        
        # Determine stability category
        if stability_score >= 0.8:
            category = "Highly Stable"
            description = "Well-organized, predictable faction with consistent policies"
        elif stability_score >= 0.6:
            category = "Stable"
            description = "Reliable faction with occasional internal tensions"
        elif stability_score >= 0.4:
            category = "Unstable"
            description = "Prone to internal conflicts and policy shifts"
        elif stability_score >= 0.2:
            category = "Volatile"
            description = "Frequent leadership changes and direction shifts"
        else:
            category = "Chaotic"
            description = "Barely functional with constant internal strife"
        
        return {
            "faction_id": str(faction_id),
            "stability_score": round(stability_score, 3),
            "stability_category": category,
            "description": description,
            "risk_factors": {
                "impulsivity_risk": round(impulsivity_risk, 3),
                "ambition_overreach": round(ambition_overreach, 3),
                "discipline_weakness": round(1.0 - discipline_stability, 3),
                "integrity_inconsistency": round(1.0 - integrity_consistency, 3)
            },
            "stability_factors": {
                "discipline": round(discipline_stability, 3),
                "integrity": round(integrity_consistency, 3),
                "resilience": round(resilience_factor, 3)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating stability assessment: {str(e)}"
        )

@faction_router.get("/{faction_id}/power-score", response_model=Dict[str, Any])
async def get_faction_power_score(
    faction_id: UUID,
    service: FactionService = Depends(get_faction_service)
):
    """Get comprehensive power score calculation for a faction."""
    try:
        faction = await service.get_faction_by_id(faction_id)
        if not faction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faction with ID {faction_id} not found"
            )
        
        # Calculate power score using the documented algorithm
        base_power = (
            faction.hidden_ambition * 0.25 +      # Drive for power (25%)
            faction.hidden_discipline * 0.20 +    # Organizational strength (20%)
            faction.hidden_pragmatism * 0.15 +    # Strategic effectiveness (15%)
            faction.hidden_resilience * 0.15 +    # Sustainability (15%)
            faction.hidden_integrity * 0.10 +     # Trustworthiness factor (10%)
            (10 - faction.hidden_impulsivity) * 0.15  # Strategic patience (15%)
        )
        
        # Normalize to 0-100 scale
        power_score = min(100.0, max(0.0, base_power * 10))
        
        # Determine power category
        if power_score >= 80:
            category = "Dominant"
            description = "Regional superpower with extensive influence"
        elif power_score >= 60:
            category = "Major"
            description = "Significant political player with substantial resources"
        elif power_score >= 40:
            category = "Moderate"
            description = "Established faction with regional influence"
        elif power_score >= 20:
            category = "Minor"
            description = "Local organization with limited reach"
        else:
            category = "Negligible"
            description = "Weak or declining faction with minimal impact"
        
        return {
            "faction_id": str(faction_id),
            "power_score": round(power_score, 2),
            "power_category": category,
            "description": description,
            "power_components": {
                "ambition_drive": round(faction.hidden_ambition * 0.25 * 10, 2),
                "organizational_strength": round(faction.hidden_discipline * 0.20 * 10, 2),
                "strategic_effectiveness": round(faction.hidden_pragmatism * 0.15 * 10, 2),
                "sustainability": round(faction.hidden_resilience * 0.15 * 10, 2),
                "trustworthiness": round(faction.hidden_integrity * 0.10 * 10, 2),
                "strategic_patience": round((10 - faction.hidden_impulsivity) * 0.15 * 10, 2)
            },
            "raw_attributes": {
                "hidden_ambition": faction.hidden_ambition,
                "hidden_discipline": faction.hidden_discipline,
                "hidden_pragmatism": faction.hidden_pragmatism,
                "hidden_resilience": faction.hidden_resilience,
                "hidden_integrity": faction.hidden_integrity,
                "hidden_impulsivity": faction.hidden_impulsivity
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating faction power score: {str(e)}"
        )
