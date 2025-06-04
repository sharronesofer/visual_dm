"""
Quest System API Router with Population Integration

Provides endpoints for quest management including:
- Population-generated quest retrieval
- Quest completion and management
- Quest statistics and monitoring
- Integration with population events
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Import quest integration components
try:
    from backend.infrastructure.api.quest.population_integration import (
        population_quest_generator,
        PopulationQuest,
        QuestPriority,
        QuestType,
        handle_disease_outbreak_quest_generation,
        handle_population_change_quest_generation
    )
    QUEST_INTEGRATION_AVAILABLE = True
except ImportError:
    population_quest_generator = None
    QUEST_INTEGRATION_AVAILABLE = False
    logging.warning("Quest integration not available")

# Import population disease models for testing
try:
    from backend.systems.population.utils.disease_models import DiseaseType, DiseaseStage
    DISEASE_MODELS_AVAILABLE = True
except ImportError:
    DISEASE_MODELS_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quests", tags=["population-quests"])


@router.get("/health")
async def quest_system_health():
    """
    Health check for the quest system
    
    Returns:
        System health status and capabilities
    """
    try:
        stats = {}
        if QUEST_INTEGRATION_AVAILABLE and population_quest_generator:
            stats = population_quest_generator.get_quest_statistics()
        
        return {
            "status": "healthy",
            "system": "population_quest_integration",
            "quest_integration_available": QUEST_INTEGRATION_AVAILABLE,
            "disease_models_available": DISEASE_MODELS_AVAILABLE,
            "current_quest_statistics": stats,
            "capabilities": [
                "population_event_quest_generation",
                "disease_outbreak_quests",
                "population_change_quests",
                "quest_lifecycle_management",
                "quest_statistics_tracking"
            ] if QUEST_INTEGRATION_AVAILABLE else ["health_check_only"],
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Quest system health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quest system unhealthy: {str(e)}")


@router.get("/population/{population_id}")
async def get_population_quests(
    population_id: str,
    active_only: bool = Query(True, description="Return only active quests"),
    priority_filter: Optional[str] = Query(None, description="Filter by priority (low/medium/high/critical)"),
    type_filter: Optional[str] = Query(None, description="Filter by quest type")
):
    """
    Get all quests for a specific population
    
    Args:
        population_id: ID of the population
        active_only: Whether to return only active quests
        priority_filter: Optional priority filter
        type_filter: Optional quest type filter
        
    Returns:
        List of quests for the population
    """
    try:
        if not QUEST_INTEGRATION_AVAILABLE:
            raise HTTPException(status_code=503, detail="Quest integration not available")
        
        # Get quests for population
        quests = population_quest_generator.get_active_quests_for_population(population_id)
        
        # Apply filters
        filtered_quests = []
        for quest in quests:
            # Active filter
            if active_only and not quest.is_active:
                continue
                
            # Priority filter
            if priority_filter and quest.priority.value != priority_filter:
                continue
                
            # Type filter
            if type_filter and quest.quest_type.value != type_filter:
                continue
                
            filtered_quests.append(quest)
        
        # Convert to dict format
        quest_dicts = []
        for quest in filtered_quests:
            quest_dicts.append({
                "quest_id": quest.quest_id,
                "title": quest.title,
                "description": quest.description,
                "type": quest.quest_type.value,
                "priority": quest.priority.value,
                "population_id": quest.population_id,
                "event_source": quest.event_source,
                "rewards": quest.rewards,
                "requirements": quest.requirements,
                "estimated_duration_hours": quest.estimated_duration_hours,
                "max_participants": quest.max_participants,
                "location_hint": quest.location_hint,
                "expiry_date": quest.expiry_date.isoformat() if quest.expiry_date else None,
                "created_at": quest.created_at.isoformat(),
                "is_active": quest.is_active,
                "source_event_data": quest.source_event_data
            })
        
        return {
            "population_id": population_id,
            "quest_count": len(quest_dicts),
            "filters_applied": {
                "active_only": active_only,
                "priority_filter": priority_filter,
                "type_filter": type_filter
            },
            "quests": quest_dicts
        }
        
    except Exception as e:
        logger.error(f"Error getting quests for population {population_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get population quests: {str(e)}")


@router.get("/priority/{priority}")
async def get_quests_by_priority(
    priority: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of quests to return")
):
    """
    Get quests by priority level
    
    Args:
        priority: Priority level (low/medium/high/critical)
        limit: Maximum number of quests to return
        
    Returns:
        List of quests with the specified priority
    """
    try:
        if not QUEST_INTEGRATION_AVAILABLE:
            raise HTTPException(status_code=503, detail="Quest integration not available")
        
        # Validate priority
        try:
            quest_priority = QuestPriority(priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")
        
        # Get quests by priority
        quests = population_quest_generator.get_quests_by_priority(quest_priority)
        
        # Limit results
        limited_quests = quests[:limit]
        
        # Convert to dict format
        quest_dicts = []
        for quest in limited_quests:
            quest_dicts.append({
                "quest_id": quest.quest_id,
                "title": quest.title,
                "description": quest.description,
                "type": quest.quest_type.value,
                "priority": quest.priority.value,
                "population_id": quest.population_id,
                "event_source": quest.event_source,
                "location_hint": quest.location_hint,
                "estimated_duration_hours": quest.estimated_duration_hours,
                "max_participants": quest.max_participants,
                "created_at": quest.created_at.isoformat(),
                "expiry_date": quest.expiry_date.isoformat() if quest.expiry_date else None
            })
        
        return {
            "priority": priority,
            "total_quests_with_priority": len(quests),
            "returned_quest_count": len(quest_dicts),
            "limit_applied": limit,
            "quests": quest_dicts
        }
        
    except Exception as e:
        logger.error(f"Error getting quests by priority {priority}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quests by priority: {str(e)}")


@router.post("/{quest_id}/complete")
async def complete_quest(quest_id: str):
    """
    Mark a quest as completed
    
    Args:
        quest_id: ID of the quest to complete
        
    Returns:
        Completion status
    """
    try:
        if not QUEST_INTEGRATION_AVAILABLE:
            raise HTTPException(status_code=503, detail="Quest integration not available")
        
        # Complete the quest
        success = population_quest_generator.complete_quest(quest_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Quest not found: {quest_id}")
        
        return {
            "success": True,
            "quest_id": quest_id,
            "message": "Quest completed successfully",
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing quest {quest_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete quest: {str(e)}")


@router.post("/maintenance/expire-old")
async def expire_old_quests():
    """
    Expire quests that have passed their expiry date
    
    Returns:
        List of expired quest IDs
    """
    try:
        if not QUEST_INTEGRATION_AVAILABLE:
            raise HTTPException(status_code=503, detail="Quest integration not available")
        
        # Expire old quests
        expired_quest_ids = population_quest_generator.expire_old_quests()
        
        return {
            "success": True,
            "expired_quest_count": len(expired_quest_ids),
            "expired_quest_ids": expired_quest_ids,
            "expired_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error expiring old quests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to expire old quests: {str(e)}")


@router.get("/statistics")
async def get_quest_statistics():
    """
    Get comprehensive quest statistics
    
    Returns:
        Quest system statistics
    """
    try:
        if not QUEST_INTEGRATION_AVAILABLE:
            raise HTTPException(status_code=503, detail="Quest integration not available")
        
        stats = population_quest_generator.get_quest_statistics()
        
        return {
            "quest_integration_available": QUEST_INTEGRATION_AVAILABLE,
            "statistics": stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting quest statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quest statistics: {str(e)}")


@router.post("/test/disease-outbreak")
async def test_disease_outbreak_quest_generation(
    population_id: str,
    disease_type: str = Query(..., description="Disease type"),
    disease_stage: str = Query(..., description="Disease stage"),
    location_name: Optional[str] = Query(None, description="Optional location name")
):
    """
    Test endpoint for generating disease outbreak quests
    
    Args:
        population_id: Population ID for testing
        disease_type: Type of disease
        disease_stage: Stage of disease outbreak
        location_name: Optional location name
        
    Returns:
        Generated quest opportunities
    """
    try:
        if not QUEST_INTEGRATION_AVAILABLE:
            raise HTTPException(status_code=503, detail="Quest integration not available")
        
        if not DISEASE_MODELS_AVAILABLE:
            raise HTTPException(status_code=503, detail="Disease models not available")
        
        # Validate disease type and stage
        try:
            dt = DiseaseType(disease_type)
            ds = DiseaseStage(disease_stage)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid disease type or stage: {str(e)}")
        
        # Generate test outbreak data
        outbreak_data = {
            "disease_name": disease_type.replace("_", " ").title(),
            "stage": disease_stage,
            "infected_count": 10,
            "mortality_rate": 0.1,
            "transmission_rate": 0.15
        }
        
        # Generate quests
        quest_opportunities = await handle_disease_outbreak_quest_generation(
            population_id=population_id,
            disease_type=dt,
            disease_stage=ds,
            outbreak_data=outbreak_data,
            location_name=location_name or f"Test Settlement {population_id}"
        )
        
        return {
            "test_parameters": {
                "population_id": population_id,
                "disease_type": disease_type,
                "disease_stage": disease_stage,
                "location_name": location_name
            },
            "quest_opportunities": quest_opportunities,
            "quest_count": len(quest_opportunities),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing disease outbreak quest generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test quest generation: {str(e)}")


@router.post("/test/population-change")
async def test_population_change_quest_generation(
    population_id: str,
    old_count: int = Query(..., ge=0, description="Old population count"),
    new_count: int = Query(..., ge=0, description="New population count"),
    change_reason: str = Query(..., description="Reason for population change"),
    location_name: Optional[str] = Query(None, description="Optional location name")
):
    """
    Test endpoint for generating population change quests
    
    Args:
        population_id: Population ID for testing
        old_count: Previous population count
        new_count: New population count
        change_reason: Reason for the change
        location_name: Optional location name
        
    Returns:
        Generated quest opportunities
    """
    try:
        if not QUEST_INTEGRATION_AVAILABLE:
            raise HTTPException(status_code=503, detail="Quest integration not available")
        
        # Generate quests
        quest_opportunities = await handle_population_change_quest_generation(
            population_id=population_id,
            old_count=old_count,
            new_count=new_count,
            change_reason=change_reason,
            location_name=location_name or f"Test Settlement {population_id}"
        )
        
        return {
            "test_parameters": {
                "population_id": population_id,
                "old_count": old_count,
                "new_count": new_count,
                "change_reason": change_reason,
                "location_name": location_name
            },
            "quest_opportunities": quest_opportunities,
            "quest_count": len(quest_opportunities),
            "change_percentage": ((new_count - old_count) / old_count * 100) if old_count > 0 else 0,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing population change quest generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test population change quest generation: {str(e)}")


@router.get("/types")
async def get_quest_types():
    """
    Get available quest types and priorities
    
    Returns:
        Quest type and priority information
    """
    try:
        if not QUEST_INTEGRATION_AVAILABLE:
            return {
                "quest_integration_available": False,
                "message": "Quest integration not available"
            }
        
        return {
            "quest_integration_available": True,
            "quest_types": [qt.value for qt in QuestType],
            "quest_priorities": [qp.value for qp in QuestPriority],
            "quest_type_descriptions": {
                "investigation": "Investigate sources or gather information",
                "gathering": "Collect resources or materials", 
                "delivery": "Transport items or messages",
                "protection": "Defend or guard locations/people",
                "evacuation": "Help people escape dangerous areas",
                "extermination": "Eliminate threats or sources of problems",
                "rebuilding": "Reconstruct damaged areas or communities",
                "memorial": "Honor the dead or commemorate events",
                "escort": "Guide people to safety",
                "rescue": "Save people from danger"
            },
            "priority_descriptions": {
                "low": "Non-urgent tasks, can be completed when convenient",
                "medium": "Standard priority, should be addressed reasonably soon",
                "high": "Important tasks that need prompt attention",
                "critical": "Urgent tasks requiring immediate action"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting quest types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quest types: {str(e)}") 