"""
War Impact System API Router (Infrastructure Layer)

Provides REST API endpoints for managing war impact systems affecting population:
- War scenario creation and management
- Siege operations and progression tracking
- Refugee population management and settlement
- Post-war reconstruction project management
- War effects on population dynamics

This router integrates war impact business logic with API infrastructure.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from backend.systems.population.models.war_impact_models import (
    war_engine,
    WarStatus,
    SiegeStage,
    RefugeeStatus,
    ReconstructionPhase
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/war", tags=["population-war"])


# Pydantic models for API requests/responses
class CreateWarScenarioRequest(BaseModel):
    """Request model for creating a war scenario"""
    name: str = Field(..., description="Name of the war scenario")
    war_type: str = Field(..., description="Type of war: territorial, succession, resources, independence")
    aggressor_settlements: List[str] = Field(..., description="Settlement IDs of aggressors")
    defender_settlements: List[str] = Field(..., description="Settlement IDs of defenders")
    intensity_level: float = Field(0.5, ge=0.0, le=1.0, description="War intensity (0.0-1.0)")
    estimated_duration_days: int = Field(180, ge=1, le=3650, description="Estimated war duration in days")


class InitiateSiegeRequest(BaseModel):
    """Request model for initiating a siege"""
    war_scenario_id: str = Field(..., description="ID of the active war scenario")
    besieged_settlement: str = Field(..., description="Settlement under siege")
    besieging_forces: List[str] = Field(..., description="Settlements conducting the siege")
    estimated_duration_days: int = Field(90, ge=1, le=365, description="Estimated siege duration")


class CreateRefugeeRequest(BaseModel):
    """Request model for creating refugee populations"""
    origin_settlement: str = Field(..., description="Settlement where refugees originated")
    population_to_displace: int = Field(..., ge=1, description="Number of people displaced")
    destination_settlement: Optional[str] = Field(None, description="Target settlement for refugees")


class CreateReconstructionProjectRequest(BaseModel):
    """Request model for creating reconstruction projects"""
    settlement_id: str = Field(..., description="Settlement requiring reconstruction")
    project_name: str = Field(..., description="Name of the reconstruction project")
    reconstruction_phase: str = Field(..., description="Phase: immediate_relief, basic_infrastructure, economic_recovery, social_rebuilding, full_restoration")
    resource_requirements: Dict[str, float] = Field(..., description="Required resources")
    funding_required: float = Field(..., ge=0, description="Funding required")
    estimated_completion_days: int = Field(120, ge=1, le=1825, description="Estimated completion time")


class WarEffectsRequest(BaseModel):
    """Request model for calculating war effects"""
    settlement_id: str = Field(..., description="Settlement to calculate effects for")
    current_population: int = Field(..., ge=0, description="Current population count")


@router.post("/scenarios")
async def create_war_scenario(request: CreateWarScenarioRequest):
    """Create a new war scenario affecting multiple settlements"""
    try:
        scenario_id = war_engine.create_war_scenario(
            name=request.name,
            war_type=request.war_type,
            aggressor_settlements=request.aggressor_settlements,
            defender_settlements=request.defender_settlements,
            intensity_level=request.intensity_level,
            estimated_duration_days=request.estimated_duration_days
        )
        
        return {
            "success": True,
            "scenario_id": scenario_id,
            "message": f"War scenario '{request.name}' created successfully",
            "affected_settlements": list(set(request.aggressor_settlements + request.defender_settlements)),
            "intensity_level": request.intensity_level,
            "estimated_duration_days": request.estimated_duration_days,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating war scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create war scenario: {str(e)}")


@router.get("/scenarios")
async def get_active_war_scenarios():
    """Get all active war scenarios"""
    try:
        active_wars = war_engine.get_active_wars()
        
        return {
            "active_wars": active_wars,
            "total_active_wars": len(active_wars),
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting active war scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get war scenarios: {str(e)}")


@router.post("/scenarios/{scenario_id}/siege")
async def initiate_siege(scenario_id: str, request: InitiateSiegeRequest):
    """Initiate a siege as part of an active war scenario"""
    try:
        success = war_engine.initiate_siege(
            war_scenario_id=request.war_scenario_id,
            besieged_settlement=request.besieged_settlement,
            besieging_forces=request.besieging_forces,
            estimated_duration_days=request.estimated_duration_days
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to initiate siege - war scenario not found")
        
        return {
            "success": True,
            "message": f"Siege initiated against {request.besieged_settlement}",
            "besieged_settlement": request.besieged_settlement,
            "besieging_forces": request.besieging_forces,
            "estimated_duration_days": request.estimated_duration_days,
            "initiated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating siege: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate siege: {str(e)}")


@router.post("/scenarios/{scenario_id}/end")
async def end_war_scenario(
    scenario_id: str,
    outcome: str = Query("concluded", description="War outcome: victory, defeat, peace_treaty, stalemate, concluded")
):
    """End an active war scenario"""
    try:
        success = war_engine.end_war_scenario(scenario_id, outcome)
        
        if not success:
            raise HTTPException(status_code=404, detail="War scenario not found")
        
        return {
            "success": True,
            "message": f"War scenario {scenario_id} ended",
            "outcome": outcome,
            "ended_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending war scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to end war scenario: {str(e)}")


@router.post("/refugees")
async def create_refugee_population(request: CreateRefugeeRequest):
    """Create a refugee population from a settlement"""
    try:
        refugee_id = war_engine.generate_refugees(
            origin_settlement=request.origin_settlement,
            population_to_displace=request.population_to_displace,
            destination_settlement=request.destination_settlement
        )
        
        return {
            "success": True,
            "refugee_id": refugee_id,
            "message": f"Refugee population created: {request.population_to_displace} people displaced",
            "origin_settlement": request.origin_settlement,
            "population_count": request.population_to_displace,
            "destination_settlement": request.destination_settlement,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating refugee population: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create refugee population: {str(e)}")


@router.get("/refugees")
async def get_refugee_populations():
    """Get all active refugee populations"""
    try:
        refugee_populations = war_engine.get_refugee_populations()
        
        # Calculate summary statistics
        total_refugees = sum(r["population_count"] for r in refugee_populations)
        origins = list(set(r["origin_settlement"] for r in refugee_populations))
        
        return {
            "refugee_populations": refugee_populations,
            "summary": {
                "total_refugee_populations": len(refugee_populations),
                "total_displaced_people": total_refugees,
                "origin_settlements": origins,
                "displacement_locations": len(origins)
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting refugee populations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get refugee populations: {str(e)}")


@router.post("/reconstruction")
async def create_reconstruction_project(request: CreateReconstructionProjectRequest):
    """Create a post-war reconstruction project"""
    try:
        # Validate reconstruction phase
        try:
            reconstruction_phase = ReconstructionPhase(request.reconstruction_phase)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid reconstruction phase. Must be one of: {[phase.value for phase in ReconstructionPhase]}"
            )
        
        project_id = war_engine.create_reconstruction_project(
            settlement_id=request.settlement_id,
            project_name=request.project_name,
            reconstruction_phase=reconstruction_phase,
            resource_requirements=request.resource_requirements,
            funding_required=request.funding_required,
            estimated_completion_days=request.estimated_completion_days
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "message": f"Reconstruction project '{request.project_name}' created",
            "settlement_id": request.settlement_id,
            "reconstruction_phase": request.reconstruction_phase,
            "funding_required": request.funding_required,
            "estimated_completion_days": request.estimated_completion_days,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating reconstruction project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create reconstruction project: {str(e)}")


@router.get("/reconstruction")
async def get_reconstruction_projects(
    settlement_id: Optional[str] = Query(None, description="Filter by settlement ID")
):
    """Get reconstruction projects, optionally filtered by settlement"""
    try:
        projects = war_engine.get_reconstruction_projects(settlement_id)
        
        # Calculate summary statistics
        total_funding = sum(p.get("funding_required", 0) for p in projects)
        completed_projects = [p for p in projects if p["is_completed"]]
        
        return {
            "reconstruction_projects": projects,
            "summary": {
                "total_projects": len(projects),
                "completed_projects": len(completed_projects),
                "active_projects": len(projects) - len(completed_projects),
                "total_funding_required": total_funding
            },
            "filter": {"settlement_id": settlement_id} if settlement_id else None,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting reconstruction projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get reconstruction projects: {str(e)}")


@router.post("/effects/calculate")
async def calculate_war_effects(request: WarEffectsRequest):
    """Calculate daily war effects on a settlement's population"""
    try:
        effects = war_engine.process_daily_war_effects(
            settlement_id=request.settlement_id,
            current_population=request.current_population
        )
        
        # Add war status information
        war_status = war_engine.get_war_status(request.settlement_id)
        
        return {
            "settlement_id": request.settlement_id,
            "current_population": request.current_population,
            "war_status": war_status.value,
            "daily_effects": effects,
            "calculated_at": datetime.utcnow().isoformat(),
            "summary": {
                "net_population_change": effects["population_change"],
                "morale_impact": effects["morale_change"],
                "economic_impact": effects["economic_impact"],
                "refugees_generated": effects["refugees_generated"],
                "military_recruited": effects["military_recruited"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating war effects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate war effects: {str(e)}")


@router.get("/status/{settlement_id}")
async def get_war_status(settlement_id: str):
    """Get the current war status for a specific settlement"""
    try:
        war_status = war_engine.get_war_status(settlement_id)
        
        # Get additional details if at war
        additional_info = {}
        if war_status != WarStatus.PEACE:
            # Find relevant war scenario
            active_wars = war_engine.get_active_wars()
            relevant_wars = [w for w in active_wars if settlement_id in w["affected_settlements"]]
            
            if relevant_wars:
                additional_info["active_war"] = relevant_wars[0]
            
            # Check for refugee populations from this settlement
            refugees = war_engine.get_refugee_populations()
            refugees_from_settlement = [r for r in refugees if r["origin_settlement"] == settlement_id]
            
            if refugees_from_settlement:
                additional_info["refugees_generated"] = {
                    "total_populations": len(refugees_from_settlement),
                    "total_displaced": sum(r["population_count"] for r in refugees_from_settlement)
                }
            
            # Check for reconstruction projects
            reconstruction_projects = war_engine.get_reconstruction_projects(settlement_id)
            if reconstruction_projects:
                additional_info["reconstruction_projects"] = {
                    "total_projects": len(reconstruction_projects),
                    "active_projects": len([p for p in reconstruction_projects if not p["is_completed"]])
                }
        
        return {
            "settlement_id": settlement_id,
            "war_status": war_status.value,
            "additional_info": additional_info,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting war status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get war status: {str(e)}")


@router.get("/overview")
async def get_war_system_overview():
    """Get comprehensive overview of the war impact system"""
    try:
        active_wars = war_engine.get_active_wars()
        refugee_populations = war_engine.get_refugee_populations()
        reconstruction_projects = war_engine.get_reconstruction_projects()
        
        # Calculate comprehensive statistics
        total_affected_settlements = len(set(
            settlement for war in active_wars 
            for settlement in war["affected_settlements"]
        ))
        
        total_refugees = sum(r["population_count"] for r in refugee_populations)
        total_reconstruction_funding = sum(
            p.get("funding_required", 0) for p in reconstruction_projects
        )
        
        war_types = {}
        for war in active_wars:
            war_type = war.get("war_type", "unknown")
            war_types[war_type] = war_types.get(war_type, 0) + 1
        
        return {
            "system_overview": {
                "active_wars": len(active_wars),
                "total_affected_settlements": total_affected_settlements,
                "refugee_populations": len(refugee_populations),
                "total_displaced_people": total_refugees,
                "reconstruction_projects": len(reconstruction_projects),
                "total_reconstruction_funding": total_reconstruction_funding
            },
            "war_distribution": war_types,
            "reconstruction_phases": {
                phase.value: len([p for p in reconstruction_projects 
                                if p["reconstruction_phase"] == phase.value])
                for phase in ReconstructionPhase
            },
            "refugee_status_distribution": {
                status.value: len([r for r in refugee_populations 
                                 if r["refugee_status"] == status.value])
                for status in RefugeeStatus
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting war system overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system overview: {str(e)}")


@router.get("/health")
async def war_system_health():
    """Health check for the war impact system"""
    try:
        health_status = {
            "status": "healthy",
            "system": "population_war_impact",
            "capabilities": [
                "war_scenario_management",
                "siege_operations",
                "refugee_population_tracking",
                "reconstruction_project_management",
                "war_effects_calculation",
                "settlement_war_status"
            ],
            "features": [
                "multiple_war_types",
                "siege_progression_modeling",
                "refugee_displacement_simulation",
                "reconstruction_phase_management",
                "population_impact_calculation",
                "real_time_war_status"
            ]
        }
        
        # Test basic functionality
        try:
            test_effects = war_engine.process_daily_war_effects("test_settlement", 1000)
            health_status["functionality_test"] = "passed"
        except Exception as e:
            health_status["functionality_test"] = f"failed: {str(e)}"
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"War system health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"War system unhealthy: {str(e)}") 