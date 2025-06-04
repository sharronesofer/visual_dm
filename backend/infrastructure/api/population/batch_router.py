"""
Population System Batch Operations API Router

Provides endpoints for bulk operations including:
- Batch population updates for large-scale events
- Mass disease introduction for pandemic scenarios
- Bulk migration processing
- Enhanced search and filtering capabilities
- Administrative dashboard operations
- Developer tools and testing utilities
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import logging
from pydantic import BaseModel, Field
import asyncio

from backend.systems.population.utils.disease_models import (
    DiseaseType,
    DiseaseStage,
    DISEASE_ENGINE,
    apply_disease_effects_to_population
)

# Import WebSocket integration
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

# Import quest integration
try:
    from backend.infrastructure.api.quest.population_integration import (
        population_quest_generator
    )
    QUEST_INTEGRATION_AVAILABLE = True
except ImportError:
    population_quest_generator = None
    QUEST_INTEGRATION_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/batch", tags=["population-batch-operations"])


# Pydantic models for request validation
class BatchPopulationUpdate(BaseModel):
    """Model for batch population update requests"""
    population_id: str
    new_population: int = Field(..., ge=0, description="New population count")
    change_reason: str = Field(..., description="Reason for population change")
    apply_effects: bool = Field(True, description="Whether to apply population effects")


class BatchDiseaseIntroduction(BaseModel):
    """Model for batch disease introduction requests"""
    population_id: str
    disease_type: DiseaseType
    initial_infected: int = Field(1, ge=1, le=1000, description="Initial infected count")
    environmental_factors: Optional[Dict[str, float]] = None


class PandemicScenario(BaseModel):
    """Model for pandemic scenario requests"""
    scenario_name: str = Field(..., description="Name of the pandemic scenario")
    affected_populations: List[str] = Field(..., description="List of population IDs to affect")
    primary_disease: DiseaseType = Field(..., description="Primary disease for the pandemic")
    spread_pattern: str = Field("random", description="Spread pattern: random, sequential, radial")
    spread_delay_hours: int = Field(24, ge=1, le=168, description="Hours between spread to new populations")
    initial_infected_range: List[int] = Field([1, 10], description="Range for initial infected [min, max]")
    environmental_factors: Optional[Dict[str, float]] = None


class PopulationSearchFilters(BaseModel):
    """Model for population search and filtering"""
    population_ids: Optional[List[str]] = None
    min_population: Optional[int] = Field(None, ge=0)
    max_population: Optional[int] = Field(None, ge=0)
    has_diseases: Optional[bool] = None
    disease_types: Optional[List[DiseaseType]] = None
    disease_stages: Optional[List[DiseaseStage]] = None
    outbreak_severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    has_active_quests: Optional[bool] = None
    settlement_types: Optional[List[str]] = None
    last_updated_hours: Optional[int] = Field(None, ge=1, le=8760)  # Within last X hours


class BatchOperationResult(BaseModel):
    """Model for batch operation results"""
    operation_id: str
    operation_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = Field("running", pattern="^(running|completed|failed|cancelled)$")
    total_operations: int
    completed_operations: int
    failed_operations: int
    results: List[Dict[str, Any]] = []
    errors: List[str] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Global storage for batch operations (in production, use Redis or database)
active_batch_operations: Dict[str, BatchOperationResult] = {}


@router.post("/populations/update", response_model=BatchOperationResult)
async def batch_update_populations(
    updates: List[BatchPopulationUpdate],
    background_tasks: BackgroundTasks,
    send_notifications: bool = Query(True, description="Send WebSocket notifications"),
    validate_only: bool = Query(False, description="Only validate without applying changes")
):
    """
    Perform batch population updates for multiple populations
    
    Useful for:
    - Large-scale events affecting multiple settlements
    - Disaster aftermath population changes
    - Migration wave processing
    - Administrative corrections
    """
    try:
        operation_id = str(uuid4())
        
        # Create batch operation record
        batch_result = BatchOperationResult(
            operation_id=operation_id,
            operation_type="batch_population_update",
            started_at=datetime.utcnow(),
            total_operations=len(updates),
            completed_operations=0,
            failed_operations=0
        )
        
        if validate_only:
            # Validation mode - check all updates without applying
            validation_results = []
            for update in updates:
                try:
                    # Validate population update
                    if update.new_population < 0:
                        raise ValueError("Population cannot be negative")
                    
                    validation_results.append({
                        "population_id": update.population_id,
                        "valid": True,
                        "new_population": update.new_population,
                        "change_reason": update.change_reason
                    })
                except Exception as e:
                    validation_results.append({
                        "population_id": update.population_id,
                        "valid": False,
                        "error": str(e)
                    })
                    batch_result.failed_operations += 1
            
            batch_result.status = "completed"
            batch_result.completed_at = datetime.utcnow()
            batch_result.results = validation_results
            batch_result.completed_operations = len(updates) - batch_result.failed_operations
            
            return batch_result
        
        # Store operation for tracking
        active_batch_operations[operation_id] = batch_result
        
        # Run batch update in background
        background_tasks.add_task(
            _execute_batch_population_updates,
            operation_id,
            updates,
            send_notifications
        )
        
        return batch_result
        
    except Exception as e:
        logger.error(f"Error starting batch population update: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start batch update: {str(e)}")


@router.post("/diseases/introduce", response_model=BatchOperationResult)
async def batch_introduce_diseases(
    introductions: List[BatchDiseaseIntroduction],
    background_tasks: BackgroundTasks,
    send_notifications: bool = Query(True, description="Send WebSocket notifications"),
    delay_between_seconds: int = Query(0, ge=0, le=300, description="Delay between introductions (seconds)")
):
    """
    Introduce diseases to multiple populations simultaneously
    
    Useful for:
    - Pandemic scenario testing
    - Multi-settlement outbreak events
    - Disease spread simulation
    - Load testing disease systems
    """
    try:
        operation_id = str(uuid4())
        
        batch_result = BatchOperationResult(
            operation_id=operation_id,
            operation_type="batch_disease_introduction",
            started_at=datetime.utcnow(),
            total_operations=len(introductions),
            completed_operations=0,
            failed_operations=0
        )
        
        # Store operation for tracking
        active_batch_operations[operation_id] = batch_result
        
        # Run batch disease introduction in background
        background_tasks.add_task(
            _execute_batch_disease_introductions,
            operation_id,
            introductions,
            send_notifications,
            delay_between_seconds
        )
        
        return batch_result
        
    except Exception as e:
        logger.error(f"Error starting batch disease introduction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start batch disease introduction: {str(e)}")


@router.post("/pandemic/scenario", response_model=BatchOperationResult)
async def create_pandemic_scenario(
    scenario: PandemicScenario,
    background_tasks: BackgroundTasks,
    send_notifications: bool = Query(True, description="Send WebSocket notifications")
):
    """
    Create a pandemic scenario affecting multiple populations with realistic spread patterns
    
    Spread patterns:
    - random: Random order of population infection
    - sequential: Infect populations in the order provided
    - radial: Simulate spread from first population outward (simulated)
    """
    try:
        operation_id = str(uuid4())
        
        batch_result = BatchOperationResult(
            operation_id=operation_id,
            operation_type=f"pandemic_scenario_{scenario.scenario_name}",
            started_at=datetime.utcnow(),
            total_operations=len(scenario.affected_populations),
            completed_operations=0,
            failed_operations=0
        )
        
        # Store operation for tracking
        active_batch_operations[operation_id] = batch_result
        
        # Run pandemic scenario in background
        background_tasks.add_task(
            _execute_pandemic_scenario,
            operation_id,
            scenario,
            send_notifications
        )
        
        return batch_result
        
    except Exception as e:
        logger.error(f"Error starting pandemic scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start pandemic scenario: {str(e)}")


@router.post("/populations/search")
async def search_populations(
    filters: PopulationSearchFilters,
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Advanced population search and filtering for admin/developer tools
    
    Supports filtering by:
    - Population size ranges
    - Disease status and types
    - Quest availability
    - Settlement types
    - Recent update activity
    """
    try:
        # This is a simplified implementation - in production, you'd query your actual database
        # For now, we'll simulate search results based on known disease engine data
        
        search_results = []
        total_found = 0
        
        # Get all populations with disease data
        all_populations = DISEASE_ENGINE.active_outbreaks.keys()
        
        for pop_id in all_populations:
            population_data = {
                "population_id": pop_id,
                "current_population": 1000,  # Would come from actual population data
                "disease_status": DISEASE_ENGINE.get_disease_status(pop_id),
                "quest_count": 0,
                "settlement_type": "unknown",
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Apply filters
            if filters.population_ids and pop_id not in filters.population_ids:
                continue
            
            disease_status = population_data["disease_status"]
            
            if filters.has_diseases is not None:
                if filters.has_diseases != disease_status.get("has_diseases", False):
                    continue
            
            if filters.disease_types:
                outbreak_diseases = [outbreak["disease_type"] for outbreak in disease_status.get("outbreaks", [])]
                if not any(dt.value in outbreak_diseases for dt in filters.disease_types):
                    continue
            
            if filters.outbreak_severity:
                # Calculate outbreak severity based on infected counts
                max_infected = max([outbreak.get("infected_count", 0) for outbreak in disease_status.get("outbreaks", [])], default=0)
                if max_infected > 100:
                    severity = "critical"
                elif max_infected > 50:
                    severity = "high"
                elif max_infected > 10:
                    severity = "medium"
                else:
                    severity = "low"
                
                if severity != filters.outbreak_severity:
                    continue
            
            # Get quest data if available
            if QUEST_INTEGRATION_AVAILABLE and population_quest_generator:
                active_quests = population_quest_generator.get_active_quests_for_population(pop_id)
                population_data["quest_count"] = len(active_quests)
                population_data["quests"] = [
                    {
                        "quest_id": quest.quest_id,
                        "title": quest.title,
                        "type": quest.quest_type.value,
                        "priority": quest.priority.value
                    }
                    for quest in active_quests
                ]
            
            if filters.has_active_quests is not None:
                if filters.has_active_quests != (population_data["quest_count"] > 0):
                    continue
            
            total_found += 1
            
            # Apply pagination
            if total_found > offset and len(search_results) < limit:
                search_results.append(population_data)
        
        return {
            "search_filters": filters.dict(),
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total_found": total_found,
                "returned_count": len(search_results)
            },
            "populations": search_results,
            "search_performed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching populations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search populations: {str(e)}")


@router.get("/operations/{operation_id}", response_model=BatchOperationResult)
async def get_batch_operation_status(operation_id: str):
    """Get the status of a batch operation"""
    if operation_id not in active_batch_operations:
        raise HTTPException(status_code=404, detail=f"Batch operation not found: {operation_id}")
    
    return active_batch_operations[operation_id]


@router.get("/operations", response_model=List[BatchOperationResult])
async def list_batch_operations(
    status_filter: Optional[str] = Query(None, description="Filter by status: running, completed, failed, cancelled"),
    limit: int = Query(50, ge=1, le=200)
):
    """List batch operations with optional status filtering"""
    operations = list(active_batch_operations.values())
    
    if status_filter:
        # Validate status filter
        valid_statuses = ["running", "completed", "failed", "cancelled"]
        if status_filter not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status filter. Must be one of: {valid_statuses}")
        operations = [op for op in operations if op.status == status_filter]
    
    # Sort by start time (most recent first)
    operations.sort(key=lambda op: op.started_at, reverse=True)
    
    return operations[:limit]


@router.delete("/operations/{operation_id}")
async def cancel_batch_operation(operation_id: str):
    """Cancel a running batch operation"""
    if operation_id not in active_batch_operations:
        raise HTTPException(status_code=404, detail=f"Batch operation not found: {operation_id}")
    
    operation = active_batch_operations[operation_id]
    
    if operation.status != "running":
        raise HTTPException(status_code=400, detail=f"Cannot cancel operation with status: {operation.status}")
    
    operation.status = "cancelled"
    operation.completed_at = datetime.utcnow()
    
    return {
        "success": True,
        "operation_id": operation_id,
        "message": "Batch operation cancelled",
        "cancelled_at": operation.completed_at.isoformat()
    }


@router.get("/statistics/overview")
async def get_batch_statistics():
    """Get overview statistics for batch operations"""
    try:
        total_operations = len(active_batch_operations)
        status_counts = {}
        operation_type_counts = {}
        
        for operation in active_batch_operations.values():
            # Count by status
            status = operation.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by operation type
            op_type = operation.operation_type
            operation_type_counts[op_type] = operation_type_counts.get(op_type, 0) + 1
        
        # Calculate success rate
        completed_ops = status_counts.get("completed", 0)
        failed_ops = status_counts.get("failed", 0)
        success_rate = (completed_ops / (completed_ops + failed_ops) * 100) if (completed_ops + failed_ops) > 0 else 0
        
        return {
            "total_batch_operations": total_operations,
            "status_distribution": status_counts,
            "operation_type_distribution": operation_type_counts,
            "success_rate": round(success_rate, 2),
            "system_capabilities": {
                "websocket_integration": WEBSOCKET_INTEGRATION_AVAILABLE,
                "quest_integration": QUEST_INTEGRATION_AVAILABLE,
                "max_concurrent_operations": 10,  # Could be configurable
                "supported_operation_types": [
                    "batch_population_update",
                    "batch_disease_introduction", 
                    "pandemic_scenario"
                ]
            },
            "statistics_generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting batch statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get batch statistics: {str(e)}")


# Background task functions
async def _execute_batch_population_updates(
    operation_id: str,
    updates: List[BatchPopulationUpdate],
    send_notifications: bool
):
    """Execute batch population updates in background"""
    operation = active_batch_operations[operation_id]
    
    try:
        for update in updates:
            try:
                # Apply population update (simulated - would integrate with actual population service)
                logger.info(f"Updating population {update.population_id}: {update.new_population}")
                
                # Send WebSocket notification if enabled
                if send_notifications and WEBSOCKET_INTEGRATION_AVAILABLE:
                    await event_integrator.notify_population_change(
                        update.population_id,
                        1000,  # Would be actual old population
                        update.new_population,
                        update.change_reason
                    )
                
                operation.results.append({
                    "population_id": update.population_id,
                    "success": True,
                    "new_population": update.new_population,
                    "change_reason": update.change_reason,
                    "processed_at": datetime.utcnow().isoformat()
                })
                operation.completed_operations += 1
                
            except Exception as e:
                logger.error(f"Failed to update population {update.population_id}: {str(e)}")
                operation.errors.append(f"Population {update.population_id}: {str(e)}")
                operation.failed_operations += 1
        
        operation.status = "completed"
        operation.completed_at = datetime.utcnow()
        
    except Exception as e:
        logger.error(f"Batch population update operation {operation_id} failed: {str(e)}")
        operation.status = "failed"
        operation.completed_at = datetime.utcnow()
        operation.errors.append(f"Operation failed: {str(e)}")


async def _execute_batch_disease_introductions(
    operation_id: str,
    introductions: List[BatchDiseaseIntroduction],
    send_notifications: bool,
    delay_between_seconds: int
):
    """Execute batch disease introductions in background"""
    operation = active_batch_operations[operation_id]
    
    try:
        for i, introduction in enumerate(introductions):
            try:
                # Apply delay if specified
                if delay_between_seconds > 0 and i > 0:
                    await asyncio.sleep(delay_between_seconds)
                
                # Introduce disease
                if send_notifications and WEBSOCKET_INTEGRATION_AVAILABLE:
                    outbreak = await enhanced_disease_engine.introduce_disease_with_notification(
                        introduction.population_id,
                        introduction.disease_type,
                        introduction.initial_infected,
                        introduction.environmental_factors
                    )
                else:
                    outbreak = DISEASE_ENGINE.introduce_disease(
                        introduction.population_id,
                        introduction.disease_type,
                        introduction.initial_infected,
                        introduction.environmental_factors
                    )
                
                operation.results.append({
                    "population_id": introduction.population_id,
                    "success": True,
                    "disease_type": introduction.disease_type.value,
                    "initial_infected": introduction.initial_infected,
                    "outbreak_id": f"{introduction.population_id}_{introduction.disease_type.value}",
                    "processed_at": datetime.utcnow().isoformat()
                })
                operation.completed_operations += 1
                
            except Exception as e:
                logger.error(f"Failed to introduce disease to {introduction.population_id}: {str(e)}")
                operation.errors.append(f"Population {introduction.population_id}: {str(e)}")
                operation.failed_operations += 1
        
        operation.status = "completed"
        operation.completed_at = datetime.utcnow()
        
    except Exception as e:
        logger.error(f"Batch disease introduction operation {operation_id} failed: {str(e)}")
        operation.status = "failed"
        operation.completed_at = datetime.utcnow()
        operation.errors.append(f"Operation failed: {str(e)}")


async def _execute_pandemic_scenario(
    operation_id: str,
    scenario: PandemicScenario,
    send_notifications: bool
):
    """Execute pandemic scenario in background"""
    operation = active_batch_operations[operation_id]
    
    try:
        import random
        
        # Determine infection order based on spread pattern
        if scenario.spread_pattern == "random":
            infection_order = scenario.affected_populations.copy()
            random.shuffle(infection_order)
        elif scenario.spread_pattern == "sequential":
            infection_order = scenario.affected_populations.copy()
        elif scenario.spread_pattern == "radial":
            # Simulate radial spread (simplified - in reality would use geographic data)
            infection_order = scenario.affected_populations.copy()
            random.shuffle(infection_order[1:])  # Keep first as origin, randomize rest
        else:
            infection_order = scenario.affected_populations.copy()
        
        # Execute infections with delays
        for i, population_id in enumerate(infection_order):
            try:
                # Apply spread delay (except for first population)
                if i > 0:
                    await asyncio.sleep(scenario.spread_delay_hours * 3600)  # Convert hours to seconds
                
                # Determine initial infected count
                min_infected, max_infected = scenario.initial_infected_range
                initial_infected = random.randint(min_infected, max_infected)
                
                # Introduce disease
                if send_notifications and WEBSOCKET_INTEGRATION_AVAILABLE:
                    outbreak = await enhanced_disease_engine.introduce_disease_with_notification(
                        population_id,
                        scenario.primary_disease,
                        initial_infected,
                        scenario.environmental_factors
                    )
                else:
                    outbreak = DISEASE_ENGINE.introduce_disease(
                        population_id,
                        scenario.primary_disease,
                        initial_infected,
                        scenario.environmental_factors
                    )
                
                operation.results.append({
                    "population_id": population_id,
                    "success": True,
                    "infection_order": i + 1,
                    "disease_type": scenario.primary_disease.value,
                    "initial_infected": initial_infected,
                    "processed_at": datetime.utcnow().isoformat()
                })
                operation.completed_operations += 1
                
            except Exception as e:
                logger.error(f"Failed to infect population {population_id} in pandemic scenario: {str(e)}")
                operation.errors.append(f"Population {population_id}: {str(e)}")
                operation.failed_operations += 1
        
        operation.status = "completed"
        operation.completed_at = datetime.utcnow()
        
    except Exception as e:
        logger.error(f"Pandemic scenario operation {operation_id} failed: {str(e)}")
        operation.status = "failed"
        operation.completed_at = datetime.utcnow()
        operation.errors.append(f"Operation failed: {str(e)}")


@router.get("/health")
async def batch_operations_health():
    """Health check for batch operations system"""
    try:
        active_count = len([op for op in active_batch_operations.values() if op.status == "running"])
        
        return {
            "status": "healthy",
            "system": "population_batch_operations",
            "active_operations": active_count,
            "total_operations_tracked": len(active_batch_operations),
            "websocket_integration_available": WEBSOCKET_INTEGRATION_AVAILABLE,
            "quest_integration_available": QUEST_INTEGRATION_AVAILABLE,
            "capabilities": [
                "batch_population_updates",
                "mass_disease_introduction",
                "pandemic_scenario_simulation",
                "advanced_population_search",
                "admin_filtering_tools",
                "background_processing",
                "operation_tracking"
            ],
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Batch operations health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch operations system unhealthy: {str(e)}") 