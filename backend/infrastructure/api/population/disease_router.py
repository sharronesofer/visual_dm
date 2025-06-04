"""
Population Disease System API Router

Provides endpoints for disease management within populations including:
- Disease introduction and management
- Disease status monitoring
- Quest generation from disease outbreaks
- Disease simulation and testing
- Real-time WebSocket notifications for Unity integration
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from uuid import UUID
import logging

from backend.systems.population.utils.disease_models import (
    DiseaseType,
    DiseaseStage,
    DISEASE_ENGINE,
    DISEASE_PROFILES,
    apply_disease_effects_to_population,
    introduce_random_disease_outbreak
)
from backend.systems.population.services.services import (
    PopulationBusinessService,
    create_population_business_service
)

# Import WebSocket integration from infrastructure layer
try:
    from backend.infrastructure.api.population.websocket_integration import (
        enhanced_disease_engine,
        event_integrator
    )
    WEBSOCKET_INTEGRATION_AVAILABLE = True
except ImportError:
    enhanced_disease_engine = None
    event_integrator = None
    WEBSOCKET_INTEGRATION_AVAILABLE = False
    logging.warning("WebSocket integration not available - using basic disease engine")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diseases", tags=["population-diseases"])


@router.post("/{population_id}/introduce")
async def introduce_disease_outbreak(
    population_id: str,
    disease_type: DiseaseType,
    initial_infected: int = Query(1, ge=1, le=1000, description="Initial number of infected individuals"),
    crowding_factor: float = Query(1.0, ge=0.1, le=5.0, description="Crowding conditions multiplier"),
    hygiene_factor: float = Query(1.0, ge=0.1, le=5.0, description="Hygiene conditions multiplier"),
    healthcare_factor: float = Query(1.0, ge=0.1, le=5.0, description="Healthcare quality multiplier"),
    season: Optional[str] = Query(None, description="Current season (winter/spring/summer/autumn)"),
    enable_notifications: bool = Query(True, description="Enable WebSocket notifications for Unity")
):
    """
    Manually introduce a disease outbreak to a population
    
    Args:
        population_id: ID of the population to affect
        disease_type: Type of disease to introduce
        initial_infected: Number of initially infected individuals
        crowding_factor: Environmental crowding factor
        hygiene_factor: Environmental hygiene factor
        healthcare_factor: Healthcare quality factor
        season: Current season for seasonal disease effects
        enable_notifications: Whether to send WebSocket notifications
        
    Returns:
        Disease outbreak details and initial status
    """
    try:
        environmental_factors = {
            'crowding': crowding_factor,
            'hygiene': hygiene_factor,
            'healthcare': healthcare_factor,
            'season': season
        }
        
        # Use enhanced engine with notifications if available and requested
        if WEBSOCKET_INTEGRATION_AVAILABLE and enable_notifications:
            outbreak = await enhanced_disease_engine.introduce_disease_with_notification(
                population_id=population_id,
                disease_type=disease_type,
                initial_infected=initial_infected,
                environmental_factors=environmental_factors
            )
        else:
            # Fallback to basic engine
            outbreak = DISEASE_ENGINE.introduce_disease(
                population_id=population_id,
                disease_type=disease_type,
                initial_infected=initial_infected,
                environmental_factors=environmental_factors
            )
        
        profile = outbreak.get_profile()
        
        return {
            "success": True,
            "message": f"Successfully introduced {profile.name} to population {population_id}",
            "outbreak": {
                "disease_type": outbreak.disease_type.value,
                "disease_name": profile.name,
                "stage": outbreak.stage.value,
                "infected_count": outbreak.infected_count,
                "total_deaths": outbreak.total_deaths,
                "days_active": outbreak.days_active,
                "mortality_rate": profile.mortality_rate,
                "transmission_rate": profile.transmission_rate
            },
            "environmental_factors": environmental_factors,
            "quest_opportunities": DISEASE_ENGINE.generate_quest_opportunities(population_id),
            "websocket_notifications_sent": WEBSOCKET_INTEGRATION_AVAILABLE and enable_notifications
        }
        
    except Exception as e:
        logger.error(f"Error introducing disease to population {population_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to introduce disease: {str(e)}")


@router.get("/{population_id}/status")
async def get_disease_status(population_id: str):
    """
    Get current disease status for a population
    
    Args:
        population_id: ID of the population
        
    Returns:
        Current disease status including active outbreaks
    """
    try:
        disease_status = DISEASE_ENGINE.get_disease_status(population_id)
        quest_opportunities = DISEASE_ENGINE.generate_quest_opportunities(population_id)
        
        return {
            "population_id": population_id,
            "disease_status": disease_status,
            "quest_opportunities": quest_opportunities,
            "total_quests_available": len(quest_opportunities),
            "websocket_integration_available": WEBSOCKET_INTEGRATION_AVAILABLE
        }
        
    except Exception as e:
        logger.error(f"Error getting disease status for population {population_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get disease status: {str(e)}")


@router.post("/{population_id}/progress-time")
async def progress_time_simulation(
    population_id: str,
    days: int = Query(1, ge=1, le=365, description="Number of days to simulate"),
    total_population: int = Query(..., ge=1, description="Current total population"),
    crowding_factor: float = Query(1.0, ge=0.1, le=5.0),
    hygiene_factor: float = Query(1.0, ge=0.1, le=5.0),
    healthcare_factor: float = Query(1.0, ge=0.1, le=5.0),
    season: Optional[str] = Query(None, description="Current season"),
    enable_notifications: bool = Query(True, description="Enable WebSocket notifications")
):
    """
    Simulate time progression for disease outbreaks
    
    Args:
        population_id: ID of the population
        days: Number of days to simulate
        total_population: Current population count
        Environmental factors for disease progression
        enable_notifications: Whether to send WebSocket notifications
        
    Returns:
        Disease progression results over the simulated time period
    """
    try:
        environmental_factors = {
            'crowding': crowding_factor,
            'hygiene': hygiene_factor,
            'healthcare': healthcare_factor,
            'season': season
        }
        
        daily_results = []
        current_population = total_population
        total_notifications_sent = 0
        
        for day in range(days):
            # Use enhanced engine with notifications if available and requested
            if WEBSOCKET_INTEGRATION_AVAILABLE and enable_notifications:
                day_result = await enhanced_disease_engine.progress_disease_day_with_notification(
                    population_id, current_population, environmental_factors
                )
                total_notifications_sent += 1
            else:
                # Fallback to basic engine
                day_result = DISEASE_ENGINE.progress_disease_day(
                    population_id, current_population, environmental_factors
                )
            
            # Apply deaths to population
            current_population = max(0, current_population - day_result['new_deaths'])
            
            daily_results.append({
                "day": day + 1,
                "population": current_population,
                "new_deaths": day_result['new_deaths'],
                "total_infected": day_result['total_infected'],
                "active_outbreaks": day_result['active_outbreaks'],
                "outbreaks": day_result['outbreaks']
            })
        
        # Get final status
        final_disease_status = DISEASE_ENGINE.get_disease_status(population_id)
        population_effects = DISEASE_ENGINE.calculate_population_effects(population_id, current_population)
        quest_opportunities = DISEASE_ENGINE.generate_quest_opportunities(population_id)
        
        return {
            "population_id": population_id,
            "simulation_days": days,
            "starting_population": total_population,
            "ending_population": current_population,
            "population_change": current_population - total_population,
            "total_deaths": sum(day["new_deaths"] for day in daily_results),
            "daily_progression": daily_results,
            "final_disease_status": final_disease_status,
            "population_effects": population_effects,
            "quest_opportunities": quest_opportunities,
            "websocket_notifications_sent": total_notifications_sent if WEBSOCKET_INTEGRATION_AVAILABLE and enable_notifications else 0
        }
        
    except Exception as e:
        logger.error(f"Error simulating time progression for population {population_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate time progression: {str(e)}")


@router.get("/{population_id}/quest-opportunities")
async def get_quest_opportunities(population_id: str):
    """
    Get quest opportunities generated by disease outbreaks
    
    Args:
        population_id: ID of the population
        
    Returns:
        List of available quest opportunities based on current disease outbreaks
    """
    try:
        quest_opportunities = DISEASE_ENGINE.generate_quest_opportunities(population_id)
        disease_status = DISEASE_ENGINE.get_disease_status(population_id)
        
        return {
            "population_id": population_id,
            "has_diseases": disease_status.get("has_diseases", False),
            "outbreak_count": disease_status.get("outbreak_count", 0),
            "quest_opportunities": quest_opportunities,
            "quests_by_urgency": {
                "critical": [q for q in quest_opportunities if q.get("urgency") == "critical"],
                "high": [q for q in quest_opportunities if q.get("urgency") == "high"],
                "medium": [q for q in quest_opportunities if q.get("urgency") == "medium"],
                "low": [q for q in quest_opportunities if q.get("urgency") == "low"]
            },
            "quests_by_type": {}
        }
        
    except Exception as e:
        logger.error(f"Error getting quest opportunities for population {population_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quest opportunities: {str(e)}")


@router.get("/types")
async def get_disease_types():
    """
    Get information about all available disease types
    
    Returns:
        List of disease types with their characteristics
    """
    try:
        disease_info = []
        
        for disease_type, profile in DISEASE_PROFILES.items():
            disease_info.append({
                "disease_type": disease_type.value,
                "name": profile.name,
                "mortality_rate": profile.mortality_rate,
                "transmission_rate": profile.transmission_rate,
                "incubation_days": profile.incubation_days,
                "recovery_days": profile.recovery_days,
                "immunity_duration_days": profile.immunity_duration_days,
                "seasonal_preference": profile.seasonal_preference,
                "targets_young": profile.targets_young,
                "targets_old": profile.targets_old,
                "targets_weak": profile.targets_weak,
                "environmental_factors": {
                    "crowding_factor": profile.crowding_factor,
                    "hygiene_factor": profile.hygiene_factor,
                    "healthcare_factor": profile.healthcare_factor
                }
            })
        
        return {
            "available_diseases": disease_info,
            "total_disease_types": len(disease_info),
            "disease_stages": [stage.value for stage in DiseaseStage],
            "websocket_integration_available": WEBSOCKET_INTEGRATION_AVAILABLE
        }
        
    except Exception as e:
        logger.error(f"Error getting disease types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get disease types: {str(e)}")


@router.post("/simulate-outbreak")
async def simulate_outbreak_scenario(
    population_size: int = Query(..., ge=10, le=100000, description="Population size for simulation"),
    disease_type: DiseaseType = Query(..., description="Type of disease to simulate"),
    simulation_days: int = Query(30, ge=1, le=365, description="Days to simulate"),
    initial_infected: int = Query(1, ge=1, le=100, description="Initial infected count"),
    crowding_factor: float = Query(1.0, ge=0.1, le=5.0),
    hygiene_factor: float = Query(1.0, ge=0.1, le=5.0),
    healthcare_factor: float = Query(1.0, ge=0.1, le=5.0),
    season: Optional[str] = Query(None, description="Season for simulation")
):
    """
    Simulate a disease outbreak scenario for testing and analysis
    
    This endpoint creates a temporary simulation without affecting actual populations.
    Useful for testing disease parameters and understanding outbreak dynamics.
    """
    try:
        # Use a temporary population ID for simulation
        simulation_id = f"simulation_{disease_type.value}_{population_size}"
        
        environmental_factors = {
            'crowding': crowding_factor,
            'hygiene': hygiene_factor,
            'healthcare': healthcare_factor,
            'season': season
        }
        
        # Run the simulation using the disease effects function
        simulation_result = apply_disease_effects_to_population(
            population_id=simulation_id,
            base_population=population_size,
            time_days=simulation_days,
            environmental_factors=environmental_factors
        )
        
        # Also introduce the specific disease to see its effects
        DISEASE_ENGINE.introduce_disease(
            population_id=simulation_id,
            disease_type=disease_type,
            initial_infected=initial_infected,
            environmental_factors=environmental_factors
        )
        
        # Generate additional insights
        profile = DISEASE_PROFILES[disease_type]
        
        return {
            "simulation_parameters": {
                "population_size": population_size,
                "disease_type": disease_type.value,
                "disease_name": profile.name,
                "simulation_days": simulation_days,
                "initial_infected": initial_infected,
                "environmental_factors": environmental_factors
            },
            "simulation_results": simulation_result,
            "disease_profile": {
                "mortality_rate": profile.mortality_rate,
                "transmission_rate": profile.transmission_rate,
                "seasonal_preference": profile.seasonal_preference,
                "targets": {
                    "young": profile.targets_young,
                    "old": profile.targets_old,
                    "weak": profile.targets_weak
                }
            },
            "analysis": {
                "infection_rate": simulation_result["total_deaths"] / population_size if population_size > 0 else 0,
                "survival_rate": simulation_result["ending_population"] / population_size if population_size > 0 else 0,
                "outbreak_severity": "critical" if simulation_result["total_deaths"] > (population_size * 0.1) else 
                                   "high" if simulation_result["total_deaths"] > (population_size * 0.05) else
                                   "medium" if simulation_result["total_deaths"] > (population_size * 0.01) else "low"
            },
            "websocket_integration_available": WEBSOCKET_INTEGRATION_AVAILABLE
        }
        
    except Exception as e:
        logger.error(f"Error simulating outbreak scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate outbreak: {str(e)}")


@router.get("/{population_id}/effects")
async def get_population_disease_effects(
    population_id: str,
    current_population: int = Query(..., ge=0, description="Current population count")
):
    """
    Get the current effects of diseases on population metrics
    
    Args:
        population_id: ID of the population
        current_population: Current population count
        
    Returns:
        Disease effects on productivity, morale, growth, and migration
    """
    try:
        population_effects = DISEASE_ENGINE.calculate_population_effects(population_id, current_population)
        disease_status = DISEASE_ENGINE.get_disease_status(population_id)
        
        return {
            "population_id": population_id,
            "current_population": current_population,
            "disease_status": disease_status,
            "population_effects": population_effects,
            "effect_analysis": {
                "productivity_impact": 1.0 - population_effects["productivity_multiplier"],
                "morale_impact": 1.0 - population_effects["morale_multiplier"],
                "growth_impact": 1.0 - population_effects["growth_rate_multiplier"],
                "migration_risk": population_effects["migration_pressure"],
                "overall_severity": max(
                    1.0 - population_effects["productivity_multiplier"],
                    1.0 - population_effects["morale_multiplier"],
                    population_effects["migration_pressure"]
                )
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting disease effects for population {population_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get disease effects: {str(e)}")


@router.get("/websocket/events")
async def get_recent_websocket_events(
    limit: int = Query(50, ge=1, le=1000, description="Number of recent events to retrieve")
):
    """
    Get recent WebSocket events for debugging and monitoring
    
    Returns:
        Recent WebSocket events and integration statistics
    """
    try:
        if not WEBSOCKET_INTEGRATION_AVAILABLE:
            return {
                "websocket_integration_available": False,
                "message": "WebSocket integration not available"
            }
        
        recent_events = event_integrator.get_recent_events(limit)
        stats = event_integrator.get_stats()
        
        return {
            "websocket_integration_available": True,
            "recent_events": recent_events,
            "integration_stats": stats,
            "events_retrieved": len(recent_events)
        }
        
    except Exception as e:
        logger.error(f"Error getting WebSocket events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get WebSocket events: {str(e)}")


# Health check endpoint
@router.get("/health")
async def disease_system_health():
    """
    Health check for the disease system
    
    Returns:
        System health status and capabilities
    """
    try:
        websocket_stats = None
        if WEBSOCKET_INTEGRATION_AVAILABLE:
            websocket_stats = event_integrator.get_stats()
        
        return {
            "status": "healthy",
            "system": "population_disease_system",
            "disease_engine_active": True,
            "available_diseases": len(DISEASE_PROFILES),
            "disease_types": [dt.value for dt in DiseaseType],
            "disease_stages": [ds.value for ds in DiseaseStage],
            "websocket_integration_available": WEBSOCKET_INTEGRATION_AVAILABLE,
            "websocket_integration_stats": websocket_stats,
            "capabilities": [
                "disease_introduction",
                "outbreak_simulation",
                "time_progression",
                "quest_generation",
                "population_effects_calculation",
                "environmental_factors_modeling"
            ] + (["real_time_websocket_notifications", "unity_client_integration"] if WEBSOCKET_INTEGRATION_AVAILABLE else []),
            "version": "1.1.0"
        }
        
    except Exception as e:
        logger.error(f"Disease system health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Disease system unhealthy: {str(e)}") 