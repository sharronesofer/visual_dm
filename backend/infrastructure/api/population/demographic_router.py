"""
Population System - Demographic Analysis API Router

This router provides REST API endpoints for the demographic mathematical models
and analysis capabilities implemented for Task 74.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.systems.population.services.demographic_service import (
    DemographicAnalysisService
)
from backend.infrastructure.database import get_db_session
from backend.infrastructure.shared.exceptions import (
    PopulationNotFoundError,
    PopulationValidationError
)

# Pydantic models for request/response
class RegionalFactorsRequest(BaseModel):
    """Request model for regional factors affecting demographics"""
    healthcare_quality: Optional[float] = Field(None, ge=0.0, le=1.0, description="Healthcare quality (0.0-1.0)")
    safety_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Safety level (0.0-1.0)")
    economic_prosperity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Economic prosperity (0.0-1.0)")
    environmental_quality: Optional[float] = Field(None, ge=0.0, le=1.0, description="Environmental quality (0.0-1.0)")
    infrastructure_quality: Optional[float] = Field(None, ge=0.0, le=1.0, description="Infrastructure quality (0.0-1.0)")


class MigrationAnalysisRequest(BaseModel):
    """Request model for migration flow analysis"""
    origin_population_id: UUID = Field(..., description="ID of origin population")
    destination_population_ids: List[UUID] = Field(..., description="List of destination population IDs")
    migration_type: str = Field("economic", description="Type of migration (economic, safety, family, seasonal, forced, return)")


class PopulationProjectionRequest(BaseModel):
    """Request model for population projection"""
    population_id: UUID = Field(..., description="ID of population to project")
    months_ahead: int = Field(12, ge=1, le=120, description="Number of months to project (1-120)")
    scenario_factors: Optional[Dict[str, Any]] = Field(None, description="External factors affecting population")


class DemographicAnalysisResponse(BaseModel):
    """Response model for comprehensive demographic analysis"""
    population_id: str
    analysis_timestamp: str
    demographic_profile: Dict[str, Any]
    age_specific_rates: Dict[str, Any]
    settlement_analysis: Dict[str, Any]
    regional_factors: Dict[str, float]
    recommendations: List[str]


class MigrationFlowResponse(BaseModel):
    """Response model for migration flow analysis"""
    origin_population_id: str
    origin_name: str
    migration_type: str
    push_factors: Dict[str, float]
    migration_flows: List[Dict[str, Any]]
    total_estimated_emigration: int
    analysis_timestamp: str


class PopulationProjectionResponse(BaseModel):
    """Response model for population projections"""
    population_id: str
    projection_months: int
    scenario_factors: Dict[str, Any]
    initial_population: int
    final_population: int
    population_change: int
    percentage_change: float
    projections: List[Dict[str, Any]]
    projection_timestamp: str


# Create the router
router = APIRouter(prefix="/population/demographics", tags=["Population Demographics"])


def create_demographic_analysis_service(db_session: Session = Depends(get_db_session)) -> DemographicAnalysisService:
    """Factory function to create demographic analysis service with proper dependency injection"""
    return DemographicAnalysisService(db_session)


@router.post("/analyze/{population_id}", response_model=DemographicAnalysisResponse)
async def analyze_population_demographics(
    population_id: UUID,
    regional_factors: Optional[RegionalFactorsRequest] = None,
    service: DemographicAnalysisService = Depends(create_demographic_analysis_service)
):
    """
    Perform comprehensive demographic analysis for a population
    
    This endpoint applies the mathematical models from Task 74 to analyze:
    - Age-based birth/death rates and fertility curves
    - Life expectancy calculations based on regional factors
    - Population pyramids and age distributions
    - Settlement growth dynamics and carrying capacity
    - Demographic recommendations based on analysis
    
    Args:
        population_id: UUID of the population to analyze
        regional_factors: Optional regional factors affecting demographics
        
    Returns:
        Complete demographic analysis with mathematical model results
    """
    try:
        # Convert regional factors to dict if provided
        region_factors_dict = None
        if regional_factors:
            region_factors_dict = regional_factors.dict(exclude_unset=True)
        
        result = await service.analyze_population_demographics(
            population_id, region_factors_dict
        )
        
        return DemographicAnalysisResponse(**result)
        
    except PopulationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/migration-flows", response_model=MigrationFlowResponse)
async def calculate_migration_flows(
    request: MigrationAnalysisRequest,
    service: DemographicAnalysisService = Depends(create_demographic_analysis_service)
):
    """
    Calculate migration probabilities and flows between populations
    
    This endpoint uses the migration mathematical models from Task 74 to calculate:
    - Economic, safety, family, and seasonal migration patterns
    - Push/pull factors affecting migration decisions
    - Distance decay effects on migration probability
    - Estimated number of migrants for each destination
    
    Args:
        request: Migration analysis request with origin and destinations
        
    Returns:
        Migration flow analysis with probabilities and estimates
    """
    try:
        result = await service.calculate_migration_flows(
            request.origin_population_id,
            request.destination_population_ids,
            request.migration_type
        )
        
        return MigrationFlowResponse(**result)
        
    except PopulationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration analysis failed: {str(e)}")


@router.post("/projections", response_model=PopulationProjectionResponse)
async def project_population_future(
    request: PopulationProjectionRequest,
    service: DemographicAnalysisService = Depends(create_demographic_analysis_service)
):
    """
    Project population changes over time using demographic models
    
    This endpoint uses the population projection models from Task 74 to simulate:
    - Natural population growth from birth/death rates
    - Age distribution changes over time
    - Impact of external factors (wars, economic changes, disasters)
    - Monthly population projections with demographic details
    
    Args:
        request: Population projection request with timeframe and scenarios
        
    Returns:
        Population projections with demographic changes over time
    """
    try:
        result = await service.project_population_future(
            request.population_id,
            request.months_ahead,
            request.scenario_factors
        )
        
        return PopulationProjectionResponse(**result)
        
    except PopulationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Population projection failed: {str(e)}")


@router.get("/models/mortality-rates")
async def get_age_mortality_rates(
    healthcare_quality: float = Query(0.5, ge=0.0, le=1.0, description="Healthcare quality (0.0-1.0)"),
    safety_level: float = Query(0.5, ge=0.0, le=1.0, description="Safety level (0.0-1.0)")
):
    """
    Get age-based mortality rates using the mathematical models
    
    This endpoint demonstrates the age-based mortality curve calculations
    from the demographic mathematical models in Task 74.
    
    Args:
        healthcare_quality: Quality of healthcare affecting mortality
        safety_level: Regional safety level affecting mortality
        
    Returns:
        Dictionary of mortality rates by age group
    """
    try:
        from backend.systems.population.utils.demographic_models import DemographicModels, AgeGroup
        
        mortality_rates = {}
        base_mortality = 0.008  # Base annual mortality rate
        
        for age_group in AgeGroup:
            rate = DemographicModels.calculate_age_based_mortality(
                age_group, base_mortality, healthcare_quality, safety_level
            )
            mortality_rates[age_group.value] = {
                "annual_mortality_rate": rate,
                "percentage": round(rate * 100, 2),
                "description": f"Annual mortality rate for {age_group.value} age group"
            }
        
        return {
            "mortality_rates_by_age": mortality_rates,
            "parameters": {
                "base_mortality": base_mortality,
                "healthcare_quality": healthcare_quality,
                "safety_level": safety_level
            },
            "timestamp": "2024-12-19T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mortality calculation failed: {str(e)}")


@router.get("/models/fertility-rates")
async def get_age_fertility_rates(
    economic_prosperity: float = Query(0.5, ge=0.0, le=1.0, description="Economic prosperity (0.0-1.0)"),
    cultural_factors: float = Query(0.5, ge=0.0, le=1.0, description="Cultural fertility preferences (0.0-1.0)")
):
    """
    Get age-based fertility rates using the mathematical models
    
    This endpoint demonstrates the age-based fertility curve calculations
    from the demographic mathematical models in Task 74.
    
    Args:
        economic_prosperity: Economic conditions affecting fertility
        cultural_factors: Cultural preferences affecting fertility
        
    Returns:
        Dictionary of fertility rates by age group
    """
    try:
        from backend.systems.population.utils.demographic_models import DemographicModels, AgeGroup
        
        fertility_rates = {}
        base_fertility = 0.12  # Base annual fertility rate
        
        for age_group in AgeGroup:
            rate = DemographicModels.calculate_fertility_rate(
                age_group, base_fertility, economic_prosperity, cultural_factors
            )
            fertility_rates[age_group.value] = {
                "annual_fertility_rate": rate,
                "children_per_woman_per_year": round(rate, 3),
                "description": f"Annual fertility rate for {age_group.value} age group"
            }
        
        return {
            "fertility_rates_by_age": fertility_rates,
            "parameters": {
                "base_fertility": base_fertility,
                "economic_prosperity": economic_prosperity,
                "cultural_factors": cultural_factors
            },
            "timestamp": "2024-12-19T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fertility calculation failed: {str(e)}")


@router.get("/models/life-expectancy")
async def calculate_life_expectancy(
    healthcare_quality: float = Query(0.5, ge=0.0, le=1.0, description="Healthcare quality (0.0-1.0)"),
    safety_level: float = Query(0.5, ge=0.0, le=1.0, description="Safety level (0.0-1.0)"),
    economic_level: float = Query(0.5, ge=0.0, le=1.0, description="Economic prosperity (0.0-1.0)"),
    environmental_quality: float = Query(0.5, ge=0.0, le=1.0, description="Environmental quality (0.0-1.0)")
):
    """
    Calculate life expectancy using the mathematical models
    
    This endpoint demonstrates the life expectancy calculation
    from the demographic mathematical models in Task 74.
    
    Args:
        healthcare_quality: Quality of medical care
        safety_level: Regional safety from violence/war
        economic_level: Economic prosperity
        environmental_quality: Environmental conditions
        
    Returns:
        Life expectancy calculation with factor breakdown
    """
    try:
        from backend.systems.population.utils.demographic_models import DemographicModels
        
        life_expectancy = DemographicModels.calculate_life_expectancy(
            healthcare_quality, safety_level, economic_level, environmental_quality
        )
        
        # Calculate individual factor contributions
        base_expectancy = 45.0
        healthcare_bonus = healthcare_quality * 25.0
        safety_bonus = safety_level * 15.0 - 7.5
        economic_bonus = economic_level * 10.0
        environmental_bonus = environmental_quality * 8.0
        
        return {
            "life_expectancy_years": round(life_expectancy, 1),
            "factor_breakdown": {
                "base_expectancy": base_expectancy,
                "healthcare_bonus": round(healthcare_bonus, 1),
                "safety_bonus": round(safety_bonus, 1),
                "economic_bonus": round(economic_bonus, 1),
                "environmental_bonus": round(environmental_bonus, 1)
            },
            "parameters": {
                "healthcare_quality": healthcare_quality,
                "safety_level": safety_level,
                "economic_level": economic_level,
                "environmental_quality": environmental_quality
            },
            "timestamp": "2024-12-19T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Life expectancy calculation failed: {str(e)}")


@router.get("/models/settlement-growth")
async def calculate_settlement_growth(
    current_population: int = Query(..., ge=1, description="Current population size"),
    settlement_type: str = Query(..., description="Settlement type (village, town, city, large_city, metropolis)"),
    economic_activity: float = Query(0.5, ge=0.0, le=1.0, description="Economic activity level (0.0-1.0)"),
    resource_capacity: int = Query(10000, ge=1, description="Maximum sustainable population"),
    infrastructure_level: float = Query(0.5, ge=0.0, le=1.0, description="Infrastructure quality (0.0-1.0)")
):
    """
    Calculate settlement growth dynamics using the mathematical models
    
    This endpoint demonstrates the settlement growth calculations
    from the demographic mathematical models in Task 74.
    
    Args:
        current_population: Current population size
        settlement_type: Type of settlement
        economic_activity: Level of economic activity
        resource_capacity: Maximum sustainable population
        infrastructure_level: Quality of infrastructure
        
    Returns:
        Settlement growth analysis and projections
    """
    try:
        from backend.systems.population.utils.demographic_models import DemographicModels, SettlementType
        
        # Convert string to enum
        settlement_enum = SettlementType(settlement_type.lower())
        
        growth_dynamics = DemographicModels.calculate_settlement_growth_dynamics(
            current_population, settlement_enum, economic_activity, 
            resource_capacity, infrastructure_level
        )
        
        return growth_dynamics
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid settlement type: {settlement_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settlement growth calculation failed: {str(e)}") 