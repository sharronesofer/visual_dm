"""
Faction Expansion API Router

FastAPI router providing endpoints for faction expansion strategies.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.infrastructure.database import get_db_session
from backend.systems.faction.services.expansion_service import (
    FactionExpansionService,
    get_faction_expansion_service,
    ExpansionStrategy,
    ExpansionAttempt
)
from backend.systems.faction.services.services import FactionService
from backend.infrastructure.schemas.faction.expansion_schemas import (
    ExpansionAttemptRequest,
    ExpansionAttemptResponse,
    FactionExpansionProfileRequest,
    FactionExpansionProfileResponse,
    RegionExpansionOpportunitiesRequest,
    RegionExpansionOpportunitiesResponse,
    BulkExpansionSimulationRequest,
    BulkExpansionSimulationResponse,
    ExpansionHistoryRequest,
    ExpansionHistoryResponse,
    ExpansionStrategyType
)
from backend.infrastructure.shared.exceptions import (
    FactionNotFoundError,
    FactionValidationError
)

logger = logging.getLogger(__name__)

expansion_router = APIRouter(prefix="/expansion", tags=["faction-expansion"])


@expansion_router.post("/attempt", response_model=ExpansionAttemptResponse)
async def attempt_expansion(
    request: ExpansionAttemptRequest,
    expansion_service: FactionExpansionService = Depends(get_faction_expansion_service),
    db: Session = Depends(get_db_session)
) -> ExpansionAttemptResponse:
    """
    Attempt faction expansion into a target region
    
    Executes an expansion attempt using the faction's preferred strategy or a specified strategy.
    The expansion can be military conquest, economic influence, or cultural conversion.
    """
    try:
        # Get faction
        faction_service = FactionService(db)
        faction_response = await faction_service.get_faction_by_id(request.faction_id)
        
        if not faction_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faction {request.faction_id} not found"
            )
        
        # Get faction entity for expansion logic
        faction_entity = db.query(FactionEntity).filter(
            FactionEntity.id == request.faction_id,
            FactionEntity.is_active == True
        ).first()
        
        if not faction_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Faction entity {request.faction_id} not found"
            )
        
        # Check if faction should attempt expansion (unless forced)
        if not request.force_attempt and not expansion_service.should_attempt_expansion(faction_entity):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Faction {faction_entity.name} is not currently motivated to expand. Use force_attempt=true to override."
            )
        
        # Convert schema strategy to service strategy
        service_strategy = None
        if request.strategy:
            service_strategy = ExpansionStrategy(request.strategy.value)
        
        # Attempt expansion
        result = await expansion_service.attempt_expansion(
            faction=faction_entity,
            target_region_id=request.target_region_id,
            strategy=service_strategy
        )
        
        # Convert result to response schema
        return ExpansionAttemptResponse(
            success=result.success,
            strategy_used=ExpansionStrategyType(result.strategy_used.value),
            target_region_id=result.target_region_id,
            faction_id=faction_entity.id,
            cost=result.cost,
            effectiveness=result.effectiveness,
            reason=result.reason,
            consequences=result.consequences
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is (they already have proper status codes)
        raise
    except FactionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FactionValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error attempting expansion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during expansion attempt"
        )


@expansion_router.get("/profile/{faction_id}", response_model=FactionExpansionProfileResponse)
async def get_faction_expansion_profile(
    faction_id: UUID,
    expansion_service: FactionExpansionService = Depends(get_faction_expansion_service),
    db: Session = Depends(get_db_session)
) -> FactionExpansionProfileResponse:
    """
    Get a faction's expansion profile and strategy preferences
    
    Returns detailed analysis of the faction's expansion behavior including
    preferred strategy, aggressiveness, and underlying personality attributes.
    """
    try:
        # Get faction entity
        faction_entity = db.query(FactionEntity).filter(
            FactionEntity.id == faction_id,
            FactionEntity.is_active == True
        ).first()
        
        if not faction_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faction {faction_id} not found"
            )
        
        # Analyze expansion behavior
        primary_strategy = expansion_service.determine_expansion_strategy(faction_entity)
        aggressiveness = expansion_service.get_expansion_aggressiveness(faction_entity)
        should_expand = expansion_service.should_attempt_expansion(faction_entity)
        
        # Calculate strategy scores for detailed analysis
        attrs = faction_entity.get_hidden_attributes()
        
        military_score = (
            attrs["hidden_ambition"] * 2 +
            (6 - attrs["hidden_integrity"]) +
            attrs["hidden_impulsivity"]
        ) / 15.0  # Normalize to 0-1
        
        economic_score = (
            attrs["hidden_pragmatism"] * 2 +
            attrs["hidden_discipline"] * 2 +
            attrs["hidden_ambition"]
        ) / 18.0  # Normalize to 0-1
        
        cultural_score = (
            attrs["hidden_integrity"] * 2 +
            (6 - attrs["hidden_impulsivity"]) * 2 +
            attrs["hidden_resilience"]
        ) / 18.0  # Normalize to 0-1
        
        return FactionExpansionProfileResponse(
            faction_id=faction_entity.id,
            faction_name=faction_entity.name,
            primary_strategy=ExpansionStrategyType(primary_strategy.value),
            aggressiveness=aggressiveness,
            should_expand=should_expand,
            strategy_scores={
                "military": military_score,
                "economic": economic_score,
                "cultural": cultural_score
            },
            hidden_attributes=attrs
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is (they already have proper status codes)
        raise
    except Exception as e:
        logger.error(f"Error getting faction expansion profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving expansion profile"
        )


@expansion_router.get("/opportunities/{region_id}", response_model=RegionExpansionOpportunitiesResponse)
async def get_region_expansion_opportunities(
    region_id: UUID,
    max_factions: int = Query(5, ge=1, le=20, description="Maximum factions to analyze"),
    expansion_service: FactionExpansionService = Depends(get_faction_expansion_service),
    db: Session = Depends(get_db_session)
) -> RegionExpansionOpportunitiesResponse:
    """
    Analyze expansion opportunities for a specific region
    
    Returns list of factions likely to attempt expansion into the region,
    ordered by likelihood and effectiveness predictions.
    """
    try:
        # Get all active factions
        factions = db.query(FactionEntity).filter(
            FactionEntity.is_active == True
        ).limit(max_factions * 2).all()  # Get more than needed for filtering
        
        opportunities = []
        
        for faction in factions:
            # Analyze faction expansion potential
            primary_strategy = expansion_service.determine_expansion_strategy(faction)
            aggressiveness = expansion_service.get_expansion_aggressiveness(faction)
            likelihood = aggressiveness * 0.8 + 0.1  # Convert to probability
            
            # Predict effectiveness based on strategy and attributes
            attrs = faction.get_hidden_attributes()
            if primary_strategy == ExpansionStrategy.MILITARY:
                predicted_effectiveness = (
                    attrs["hidden_ambition"] * 0.3 +
                    attrs["hidden_discipline"] * 0.3 +
                    (6 - attrs["hidden_impulsivity"]) * 0.2 +
                    attrs["hidden_resilience"] * 0.2
                ) / 6.0
            elif primary_strategy == ExpansionStrategy.ECONOMIC:
                predicted_effectiveness = (
                    attrs["hidden_pragmatism"] * 0.4 +
                    attrs["hidden_discipline"] * 0.3 +
                    attrs["hidden_ambition"] * 0.2 +
                    (6 - attrs["hidden_impulsivity"]) * 0.1
                ) / 6.0
            else:  # Cultural
                predicted_effectiveness = (
                    attrs["hidden_integrity"] * 0.4 +
                    (6 - attrs["hidden_impulsivity"]) * 0.3 +
                    attrs["hidden_resilience"] * 0.2 +
                    attrs["hidden_discipline"] * 0.1
                ) / 6.0
            
            opportunities.append(RegionExpansionOpportunity(
                faction_id=faction.id,
                faction_name=faction.name,
                expansion_strategy=ExpansionStrategyType(primary_strategy.value),
                likelihood=likelihood,
                predicted_effectiveness=predicted_effectiveness,
                aggressiveness=aggressiveness
            ))
        
        # Sort by likelihood (highest first) and limit results
        opportunities.sort(key=lambda x: x.likelihood, reverse=True)
        opportunities = opportunities[:max_factions]
        
        return RegionExpansionOpportunitiesResponse(
            region_id=region_id,
            opportunities=opportunities,
            total_factions_analyzed=len(factions)
        )
        
    except Exception as e:
        logger.error(f"Error analyzing expansion opportunities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error analyzing expansion opportunities"
        )


@expansion_router.post("/simulate", response_model=BulkExpansionSimulationResponse)
async def simulate_bulk_expansion(
    request: BulkExpansionSimulationRequest,
    expansion_service: FactionExpansionService = Depends(get_faction_expansion_service),
    db: Session = Depends(get_db_session)
) -> BulkExpansionSimulationResponse:
    """
    Simulate expansion attempts for multiple factions
    
    Runs a simulation of faction expansion over multiple steps,
    useful for testing expansion balance and predicting territorial changes.
    """
    try:
        simulation_id = uuid4()
        expansion_results = []
        total_attempts = 0
        successful_attempts = 0
        
        # Get faction entities
        faction_entities = db.query(FactionEntity).filter(
            FactionEntity.id.in_(request.faction_ids),
            FactionEntity.is_active == True
        ).all()
        
        if len(faction_entities) != len(request.faction_ids):
            found_ids = [f.id for f in faction_entities]
            missing_ids = [fid for fid in request.faction_ids if fid not in found_ids]
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factions not found: {missing_ids}"
            )
        
        # Track territorial control
        faction_territories = {str(faction.id): [] for faction in faction_entities}
        
        # Run simulation steps
        for step in range(request.simulation_steps):
            logger.info(f"Running expansion simulation step {step + 1}/{request.simulation_steps}")
            
            for faction in faction_entities:
                # Check if faction should attempt expansion
                if expansion_service.should_attempt_expansion(faction):
                    # For simulation, use a mock region ID
                    # In real implementation, this would integrate with region system
                    mock_region_id = uuid4()
                    
                    try:
                        result = await expansion_service.attempt_expansion(
                            faction=faction,
                            target_region_id=mock_region_id
                        )
                        
                        total_attempts += 1
                        if result.success:
                            successful_attempts += 1
                            faction_territories[str(faction.id)].append(mock_region_id)
                        
                        # Convert to response format
                        expansion_results.append(ExpansionAttemptResponse(
                            success=result.success,
                            strategy_used=ExpansionStrategyType(result.strategy_used.value),
                            target_region_id=result.target_region_id,
                            faction_id=faction.id,
                            cost=result.cost,
                            effectiveness=result.effectiveness,
                            reason=result.reason,
                            consequences=result.consequences
                        ))
                        
                    except Exception as e:
                        logger.warning(f"Expansion attempt failed for faction {faction.name}: {e}")
                        continue
        
        return BulkExpansionSimulationResponse(
            simulation_id=simulation_id,
            steps_completed=request.simulation_steps,
            total_attempts=total_attempts,
            successful_attempts=successful_attempts,
            expansion_results=expansion_results,
            final_faction_territories=faction_territories
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is (they already have proper status codes)
        raise
    except Exception as e:
        logger.error(f"Error running bulk expansion simulation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during expansion simulation"
        )


# Import FactionEntity here to avoid circular import
from backend.infrastructure.models.faction.models import FactionEntity 