"""
Revolutionary NPC Tier System API Router

Provides REST API endpoints for managing the tier system, monitoring performance,
and handling player interactions with the revolutionary MMO-scale NPC system.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.infrastructure.database import get_db
from backend.infrastructure.shared.database.manager import DatabaseManager
from backend.infrastructure.events.dispatcher import EventDispatcher
from backend.systems.npc.services.tier_manager import NPCTierManager, NPCTier
from backend.systems.npc.services.npc_service import NPCService
from backend.systems.world_generation.config.population_config import POPULATION_CONFIG


# =========================================================================
# Pydantic Models for Tier System API
# =========================================================================

class PlayerEntersPOIRequest(BaseModel):
    player_id: UUID = Field(..., description="UUID of the player entering the POI")
    poi_id: UUID = Field(..., description="UUID of the POI being entered")

class PlayerInteractsRequest(BaseModel):
    player_id: UUID = Field(..., description="UUID of the player interacting")
    npc_id: UUID = Field(..., description="UUID of the NPC being interacted with")

class RegisterPOINPCsRequest(BaseModel):
    poi_id: UUID = Field(..., description="UUID of the POI")
    npc_count: int = Field(..., gt=0, description="Number of NPCs to register")
    poi_type: str = Field(default="settlement", description="Type of POI")

class TierFilterRequest(BaseModel):
    poi_id: UUID = Field(..., description="UUID of the POI")
    tier_filter: Optional[List[str]] = Field(None, description="List of tier names to filter by")
    include_details: bool = Field(default=False, description="Whether to include full NPC details")

class SystemParticipantsRequest(BaseModel):
    system_name: str = Field(..., description="Name of the system (economy, diplomacy, etc.)")
    poi_ids: Optional[List[UUID]] = Field(None, description="Optional list of POI IDs to filter by")


# =========================================================================
# Router Setup
# =========================================================================

router = APIRouter(
    prefix="/api/v1/npc-tier-system",
    tags=["Revolutionary NPC Tier System"],
    responses={
        404: {"description": "Resource not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


# =========================================================================
# Dependency Injection
# =========================================================================

def get_tier_manager(db: Session = Depends(get_db)) -> NPCTierManager:
    """Get tier manager instance with database and event dispatcher"""
    db_manager = DatabaseManager(db)
    event_dispatcher = EventDispatcher()
    return NPCTierManager(db_manager, event_dispatcher)

def get_npc_service_with_tier_manager(
    db: Session = Depends(get_db),
    tier_manager: NPCTierManager = Depends(get_tier_manager)
) -> NPCService:
    """Get NPC service with tier manager integration"""
    return NPCService(db, tier_manager)


# =========================================================================
# Player Interaction Endpoints
# =========================================================================

@router.post("/player/enters-poi", status_code=status.HTTP_200_OK)
async def player_enters_poi(
    request: PlayerEntersPOIRequest,
    tier_manager: NPCTierManager = Depends(get_tier_manager)
) -> Dict[str, Any]:
    """
    Handle player entering a POI - promotes NPCs from Tier 4 to Tier 2 (visible).
    
    This is the core "Chuck-E-Cheese" activation system that makes NPCs visible
    when players enter their POI.
    """
    try:
        result = await tier_manager.player_enters_poi(request.player_id, request.poi_id)
        
        return {
            "success": True,
            "promoted_npc_ids": [str(npc_id) for npc_id in result],
            "promotion_count": len(result),
            "poi_id": str(request.poi_id),
            "player_id": str(request.player_id),
            "message": f"Promoted {len(result)} NPCs to visible tier"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle player POI entry: {str(e)}"
        )

@router.post("/player/interacts-with-npc", status_code=status.HTTP_200_OK)
async def player_interacts_with_npc(
    request: PlayerInteractsRequest,
    tier_manager: NPCTierManager = Depends(get_tier_manager)
) -> Dict[str, Any]:
    """
    Handle player interaction with NPC - promotes to Tier 1 (full AI activation).
    
    This promotes an NPC to the highest tier with full AI processing, memory,
    and conversation capabilities.
    """
    try:
        was_promoted = await tier_manager.player_interacts_with_npc(
            request.player_id, request.npc_id
        )
        
        return {
            "success": True,
            "promoted": was_promoted,
            "npc_id": str(request.npc_id),
            "player_id": str(request.player_id),
            "current_tier": NPCTier.TIER_1_ACTIVE.value,
            "message": "NPC promoted to active tier" if was_promoted else "NPC already active"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle player-NPC interaction: {str(e)}"
        )


# =========================================================================
# POI and NPC Management Endpoints
# =========================================================================

@router.post("/poi/register-npcs", status_code=status.HTTP_201_CREATED)
async def register_poi_npcs(
    request: RegisterPOINPCsRequest,
    tier_manager: NPCTierManager = Depends(get_tier_manager)
) -> Dict[str, Any]:
    """
    Register NPCs for a POI in the tier system.
    
    Creates NPCs at appropriate initial tiers based on POI type and
    registers them for tier management.
    """
    try:
        created_npc_ids = await tier_manager.register_poi_npcs(
            request.poi_id, request.npc_count, request.poi_type
        )
        
        return {
            "success": True,
            "poi_id": str(request.poi_id),
            "created_npc_count": len(created_npc_ids),
            "created_npc_ids": [str(npc_id) for npc_id in created_npc_ids],
            "poi_type": request.poi_type,
            "message": f"Registered {len(created_npc_ids)} NPCs for POI"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register POI NPCs: {str(e)}"
        )

@router.post("/poi/npcs-by-tier", status_code=status.HTTP_200_OK)
async def get_poi_npcs_by_tier(
    request: TierFilterRequest,
    tier_manager: NPCTierManager = Depends(get_tier_manager)
) -> Dict[str, Any]:
    """
    Get NPCs in a POI organized by their current tier.
    
    Returns NPCs grouped by tier with optional filtering and detailed information.
    """
    try:
        # Convert string tier names to NPCTier enum if provided
        tier_filter = None
        if request.tier_filter:
            tier_filter = []
            for tier_name in request.tier_filter:
                try:
                    tier_filter.append(NPCTier(tier_name))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Invalid tier name: {tier_name}"
                    )
        
        poi_npcs = await tier_manager.get_poi_npcs(request.poi_id, tier_filter)
        
        # Organize by tier
        npcs_by_tier = {
            NPCTier.TIER_1_ACTIVE.value: [],
            NPCTier.TIER_2_BACKGROUND.value: [],
            NPCTier.TIER_3_DORMANT.value: [],
            NPCTier.TIER_3_5_COMPRESSED.value: []
        }
        
        for npc_instance in poi_npcs:
            tier_key = npc_instance.current_tier.value
            
            npc_data = {
                "npc_id": str(npc_instance.npc_id),
                "name": npc_instance.name,
                "current_tier": tier_key,
                "last_interaction": npc_instance.last_interaction.isoformat() if npc_instance.last_interaction else None,
                "interaction_count": len(npc_instance.player_interactions),
                "personality_hash": npc_instance.personality_hash,
                "memory_summary": npc_instance.memory_summary
            }
            
            npcs_by_tier[tier_key].append(npc_data)
        
        # Calculate summary
        total_npcs = sum(len(npcs) for npcs in npcs_by_tier.values())
        visible_npcs = total_npcs  # All returned NPCs are visible (Tiers 1-3.5)
        
        return {
            "success": True,
            "poi_id": str(request.poi_id),
            "npcs_by_tier": npcs_by_tier,
            "summary": {
                "total_npcs": total_npcs,
                "visible_npcs": visible_npcs,
                "tier_distribution": {tier: len(npcs) for tier, npcs in npcs_by_tier.items()}
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get POI NPCs by tier: {str(e)}"
        )


# =========================================================================
# System Integration Endpoints
# =========================================================================

@router.post("/systems/participants", status_code=status.HTTP_200_OK)
async def get_system_participants(
    request: SystemParticipantsRequest,
    tier_manager: NPCTierManager = Depends(get_tier_manager)
) -> List[Dict[str, Any]]:
    """
    Get NPCs that participate in a specific system (economy, diplomacy, etc.).
    
    Returns NPCs that can actively participate in the specified system
    based on their tier and POI type.
    """
    try:
        participants = await tier_manager.get_system_participants(
            request.system_name, request.poi_ids
        )
        
        result = []
        for npc_instance in participants:
            participant_data = {
                "npc_id": str(npc_instance.npc_id),
                "name": npc_instance.name,
                "current_tier": npc_instance.current_tier.value,
                "poi_id": str(npc_instance.poi_id),
                "system": request.system_name,
                "participation_level": "active" if npc_instance.current_tier in [
                    NPCTier.TIER_1_ACTIVE, NPCTier.TIER_2_BACKGROUND
                ] else "statistical",
                "system_flags": {
                    "economy": npc_instance.participates_in_economy,
                    "diplomacy": npc_instance.participates_in_diplomacy,
                    "tension": npc_instance.participates_in_tension,
                    "religion": npc_instance.participates_in_religion,
                    "espionage": npc_instance.participates_in_espionage
                }
            }
            result.append(participant_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system participants: {str(e)}"
        )


# =========================================================================
# Performance and Monitoring Endpoints
# =========================================================================

@router.get("/status", status_code=status.HTTP_200_OK)
async def get_tier_system_status(
    tier_manager: NPCTierManager = Depends(get_tier_manager)
) -> Dict[str, Any]:
    """
    Get comprehensive status and performance metrics of the tier system.
    
    Returns real-time metrics, computational budget status, and
    scaling recommendations.
    """
    try:
        budget_status = tier_manager.get_computational_budget_status()
        
        return {
            "success": True,
            "status": "operational",
            "metrics": {
                "tier_1_count": budget_status['metrics'].tier_1_count,
                "tier_2_count": budget_status['metrics'].tier_2_count,
                "tier_3_count": budget_status['metrics'].tier_3_count,
                "tier_3_5_count": budget_status['metrics'].tier_3_5_count,
                "tier_4_count": budget_status['metrics'].tier_4_count,
                "total_npcs": budget_status['metrics'].total_npcs,
                "visible_npcs": budget_status['metrics'].visible_npcs,
                "computational_load": budget_status['metrics'].computational_load,
                "memory_usage_mb": budget_status['metrics'].memory_usage_mb
            },
            "budget_status": budget_status['budget_status'],
            "recommendations": budget_status['recommendations'],
            "performance": {
                "cpu_efficiency": f"{budget_status['budget_status']['efficiency_ratio']*100:.1f}%",
                "memory_optimization": f"{budget_status['metrics'].memory_usage_mb:.1f} MB total",
                "computational_load": f"{budget_status['metrics'].computational_load:.1f} CPU units/hour"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tier system status: {str(e)}"
        )

@router.post("/management/run-cycle", status_code=status.HTTP_200_OK)
async def run_tier_management_cycle(
    tier_manager: NPCTierManager = Depends(get_tier_manager)
) -> Dict[str, Any]:
    """
    Manually trigger a tier management cycle for testing/admin purposes.
    
    Processes tier promotions/demotions based on interaction timers and
    returns cycle statistics.
    """
    try:
        cycle_results = await tier_manager.run_tier_management_cycle()
        
        return {
            "success": True,
            "cycle_results": cycle_results,
            "timestamp": tier_manager.metrics.tier_1_count  # Use current time from manager
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run tier management cycle: {str(e)}"
        )


# =========================================================================
# Configuration and Admin Endpoints  
# =========================================================================

@router.get("/config", status_code=status.HTTP_200_OK)
async def get_tier_system_config() -> Dict[str, Any]:
    """
    Get current tier system configuration and population targets.
    
    Returns configuration that can be used by frontend for planning
    and optimization.
    """
    return {
        "success": True,
        "world_population_targets": POPULATION_CONFIG.WORLD_VISIBLE_NPC_TARGETS,
        "computational_costs": POPULATION_CONFIG.NPC_COMPUTATIONAL_COSTS,
        "memory_costs": POPULATION_CONFIG.NPC_MEMORY_COSTS,
        "region_population_ranges": {
            "standard": POPULATION_CONFIG.REGION_TOTAL_POPULATION_RANGE,
            "visible": POPULATION_CONFIG.REGION_VISIBLE_POPULATION_RANGE,
            "metropolis": POPULATION_CONFIG.METROPOLIS_TOTAL_POPULATION_RANGE
        },
        "settlement_hierarchy": POPULATION_CONFIG.SETTLEMENT_POPULATION_RANGES,
        "poi_distribution": {
            "settlements_per_region": POPULATION_CONFIG.SETTLEMENTS_PER_REGION,
            "non_settlements_per_region": POPULATION_CONFIG.NON_SETTLEMENT_POIS_PER_REGION,
            "total_pois_per_region": POPULATION_CONFIG.TOTAL_POIS_PER_REGION
        }
    }


# =========================================================================
# Health Check Endpoints
# =========================================================================

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """Simple health check for the tier system API"""
    return {
        "status": "healthy",
        "service": "Revolutionary NPC Tier System",
        "version": "1.0.0"
    } 