"""
Autonomous NPC API Endpoints

REST API endpoints for external access to autonomous NPC systems including:
- Emotional state management
- Personality evolution tracking
- Crisis response monitoring
- Real-world economic integration
- System health monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from dataclasses import asdict

from backend.infrastructure.database import get_db_session
from backend.systems.npc.services.emotional_state_service import EmotionalStateService
from backend.systems.npc.services.personality_evolution_service import PersonalityEvolutionService
from backend.systems.npc.services.crisis_response_service import CrisisResponseService
from backend.systems.economy.services.real_world_economy_service import RealWorldEconomyService
from backend.systems.npc.services.autonomous_coordinator_service import AutonomousNpcCoordinator
from backend.systems.npc.services.autonomous_monitoring_service import AutonomousNpcMonitoringService
from backend.systems.npc.services.autonomous_scheduler_service import autonomous_scheduler

router = APIRouter(prefix="/api/npc/autonomous", tags=["autonomous-npc"])


# === REQUEST/RESPONSE MODELS ===

class EmotionalStateResponse(BaseModel):
    npc_id: str
    current_emotion: str
    emotion_intensity: float
    happiness_level: float
    energy_level: float
    stress_level: float
    confidence_level: float
    sociability_level: float
    optimism_level: float
    baseline_emotion: str
    days_in_current_state: int
    last_updated: datetime

class PersonalityEvolutionResponse(BaseModel):
    npc_id: str
    recent_personality_changes: List[Dict[str, Any]]
    personality_snapshots: List[Dict[str, Any]]
    significant_memories: List[Dict[str, Any]]

class CrisisResponseRequest(BaseModel):
    crisis_type: str = Field(..., description="Type of crisis (war, plague, famine, etc.)")
    crisis_description: str = Field(..., description="Description of the crisis event")
    crisis_severity: float = Field(..., ge=1.0, le=10.0, description="Crisis severity (1-10)")
    crisis_context: Optional[Dict[str, Any]] = Field(None, description="Additional crisis context")

class SystemHealthResponse(BaseModel):
    timestamp: datetime
    total_npcs: int
    active_emotional_states: int
    ongoing_personality_evolutions: int
    active_crisis_responses: int
    economic_cycles_status: Dict[str, Any]
    system_performance: Dict[str, Any]


# === EMOTIONAL STATE ENDPOINTS ===

@router.get("/emotional-state/{npc_id}", response_model=EmotionalStateResponse)
async def get_emotional_state(
    npc_id: UUID,
    db_session = Depends(get_db_session)
):
    """Get current emotional state of an NPC"""
    try:
        emotional_service = EmotionalStateService(db_session)
        emotional_state = emotional_service.get_or_create_emotional_state(npc_id)
        
        return EmotionalStateResponse(
            npc_id=str(npc_id),
            current_emotion=emotional_state.current_emotion,
            emotion_intensity=emotional_state.emotion_intensity,
            happiness_level=emotional_state.happiness_level,
            energy_level=emotional_state.energy_level,
            stress_level=emotional_state.stress_level,
            confidence_level=emotional_state.confidence_level,
            sociability_level=emotional_state.sociability_level,
            optimism_level=emotional_state.optimism_level,
            baseline_emotion=emotional_state.baseline_emotion,
            days_in_current_state=emotional_state.days_in_current_state,
            last_updated=emotional_state.last_updated
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving emotional state: {str(e)}")

@router.post("/emotional-state/{npc_id}/trigger")
async def trigger_emotional_event(
    npc_id: UUID,
    trigger_type: str,
    description: str,
    intensity: float = Field(ge=1.0, le=10.0),
    location: Optional[str] = None,
    related_entity_id: Optional[str] = None,
    related_entity_type: Optional[str] = None,
    db_session = Depends(get_db_session)
):
    """Trigger an emotional event for an NPC"""
    try:
        emotional_service = EmotionalStateService(db_session)
        result = emotional_service.process_emotional_trigger(
            npc_id, trigger_type, description, intensity,
            location, related_entity_id, related_entity_type
        )
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering emotional event: {str(e)}")

@router.post("/emotional-state/{npc_id}/process-daily-decay")
async def process_daily_emotional_decay(
    npc_id: UUID,
    db_session = Depends(get_db_session)
):
    """Process daily emotional decay for an NPC"""
    try:
        emotional_service = EmotionalStateService(db_session)
        result = emotional_service.process_daily_emotional_decay(npc_id)
        return {"success": True, "changes": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing emotional decay: {str(e)}")


# === PERSONALITY EVOLUTION ENDPOINTS ===

@router.get("/personality-evolution/{npc_id}", response_model=PersonalityEvolutionResponse)
async def get_personality_evolution(
    npc_id: UUID,
    db_session = Depends(get_db_session)
):
    """Get personality evolution summary for an NPC"""
    try:
        personality_service = PersonalityEvolutionService(db_session)
        summary = personality_service.get_personality_evolution_summary(npc_id)
        
        return PersonalityEvolutionResponse(
            npc_id=str(npc_id),
            recent_personality_changes=summary["recent_personality_changes"],
            personality_snapshots=summary["personality_snapshots"],
            significant_memories=summary["significant_memories"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving personality evolution: {str(e)}")

@router.post("/personality-evolution/{npc_id}/evaluate-change")
async def evaluate_personality_change(
    npc_id: UUID,
    event_type: str,
    event_description: str,
    event_severity: float = Field(ge=1.0, le=10.0),
    event_context: Optional[Dict[str, Any]] = None,
    db_session = Depends(get_db_session)
):
    """Evaluate if an event should trigger personality changes"""
    try:
        personality_service = PersonalityEvolutionService(db_session)
        result = personality_service.evaluate_personality_change(
            npc_id, event_type, event_description, event_severity, event_context
        )
        return {"success": True, "evaluation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating personality change: {str(e)}")

@router.post("/personality-evolution/{npc_id}/process-daily")
async def process_daily_personality_evolution(
    npc_id: UUID,
    db_session = Depends(get_db_session)
):
    """Process daily personality evolution for an NPC"""
    try:
        personality_service = PersonalityEvolutionService(db_session)
        result = personality_service.process_daily_personality_evolution(npc_id)
        return {"success": True, "evolution_progress": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing personality evolution: {str(e)}")


# === CRISIS RESPONSE ENDPOINTS ===

@router.post("/crisis-response/{npc_id}/trigger", response_model=Dict[str, Any])
async def trigger_crisis_response(
    npc_id: UUID,
    crisis_request: CrisisResponseRequest,
    db_session = Depends(get_db_session)
):
    """Trigger a crisis response for an NPC"""
    try:
        crisis_service = CrisisResponseService(db_session)
        result = crisis_service.trigger_crisis_response(
            npc_id, 
            crisis_request.crisis_type,
            crisis_request.crisis_description,
            crisis_request.crisis_severity,
            crisis_request.crisis_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering crisis response: {str(e)}")

@router.get("/crisis-response/{npc_id}/active")
async def get_active_crisis_responses(
    npc_id: UUID,
    db_session = Depends(get_db_session)
):
    """Get active crisis responses for an NPC"""
    try:
        from backend.infrastructure.systems.npc.models.personality_evolution_models import NpcCrisisResponse
        
        active_responses = db_session.query(NpcCrisisResponse).filter(
            NpcCrisisResponse.npc_id == npc_id,
            NpcCrisisResponse.response_completed == False
        ).all()
        
        return {
            "npc_id": str(npc_id),
            "active_crisis_responses": [
                {
                    "id": str(response.id),
                    "crisis_type": response.crisis_type,
                    "response_type": response.response_type,
                    "crisis_severity": response.crisis_severity,
                    "days_elapsed": (datetime.utcnow() - response.crisis_start_date).days,
                    "estimated_duration": response.crisis_duration_days
                }
                for response in active_responses
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving crisis responses: {str(e)}")


# === REAL-WORLD ECONOMY ENDPOINTS ===

@router.get("/economy/real-world-summary")
async def get_real_world_economic_summary(
    db_session = Depends(get_db_session)
):
    """Get comprehensive real-world economic conditions"""
    try:
        economy_service = RealWorldEconomyService(db_session)
        summary = economy_service.get_real_world_economic_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving economic summary: {str(e)}")

@router.post("/economy/update-cycles")
async def update_economic_cycles(
    region_ids: Optional[List[str]] = Query(None),
    db_session = Depends(get_db_session)
):
    """Update game economic cycles based on real-world data"""
    try:
        economy_service = RealWorldEconomyService(db_session)
        result = economy_service.update_game_economic_cycles(region_ids)
        return {"success": True, "update_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating economic cycles: {str(e)}")

@router.get("/economy/crisis-detection")
async def detect_economic_crisis(
    market_crash_threshold: float = Query(-8.0, description="Market crash threshold percentage"),
    db_session = Depends(get_db_session)
):
    """Detect potential economic crises from real-world data"""
    try:
        economy_service = RealWorldEconomyService(db_session)
        crisis_event = economy_service.create_crisis_from_real_world_event(market_crash_threshold)
        
        if crisis_event:
            return {"crisis_detected": True, "crisis_event": crisis_event}
        else:
            return {"crisis_detected": False, "message": "No crisis detected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting crisis: {str(e)}")


# === SYSTEM HEALTH & MONITORING ENDPOINTS ===

@router.get("/system/health", response_model=SystemHealthResponse)
async def get_system_health(
    db_session = Depends(get_db_session)
):
    """Get comprehensive autonomous NPC system health status"""
    try:
        coordinator = AutonomousNpcCoordinator(db_session)
        health_data = coordinator.get_system_health_status()
        
        return SystemHealthResponse(
            timestamp=datetime.utcnow(),
            total_npcs=health_data["total_npcs"],
            active_emotional_states=health_data["active_emotional_states"],
            ongoing_personality_evolutions=health_data["ongoing_personality_evolutions"],
            active_crisis_responses=health_data["active_crisis_responses"],
            economic_cycles_status=health_data["economic_cycles_status"],
            system_performance=health_data["system_performance"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system health: {str(e)}")

@router.get("/system/statistics")
async def get_system_statistics(
    time_range_days: int = Query(30, description="Time range for statistics in days"),
    db_session = Depends(get_db_session)
):
    """Get comprehensive system statistics and metrics"""
    try:
        coordinator = AutonomousNpcCoordinator(db_session)
        stats = coordinator.get_comprehensive_statistics(time_range_days)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@router.post("/system/process-daily-updates")
async def process_daily_system_updates(
    npc_batch_size: int = Query(100, description="Number of NPCs to process per batch"),
    db_session = Depends(get_db_session)
):
    """Process daily updates for all autonomous NPC systems"""
    try:
        coordinator = AutonomousNpcCoordinator(db_session)
        result = await coordinator.process_daily_updates(npc_batch_size)
        return {"success": True, "processing_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing daily updates: {str(e)}")

@router.post("/system/bulk-operations/emotional-decay")
async def bulk_process_emotional_decay(
    npc_ids: Optional[List[UUID]] = None,
    db_session = Depends(get_db_session)
):
    """Process emotional decay for multiple NPCs"""
    try:
        coordinator = AutonomousNpcCoordinator(db_session)
        result = await coordinator.bulk_process_emotional_decay(npc_ids)
        return {"success": True, "processed_count": result["processed_count"], "errors": result["errors"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing bulk emotional decay: {str(e)}")

@router.post("/system/bulk-operations/personality-evolution")
async def bulk_process_personality_evolution(
    npc_ids: Optional[List[UUID]] = None,
    db_session = Depends(get_db_session)
):
    """Process personality evolution for multiple NPCs"""
    try:
        coordinator = AutonomousNpcCoordinator(db_session)
        result = await coordinator.bulk_process_personality_evolution(npc_ids)
        return {"success": True, "processed_count": result["processed_count"], "errors": result["errors"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing bulk personality evolution: {str(e)}")


# === MONITORING & ADMIN DASHBOARD ENDPOINTS ===

@router.get("/admin/dashboard", response_model=Dict[str, Any])
async def get_admin_dashboard_data(
    db_session = Depends(get_db_session)
):
    """Get comprehensive real-time dashboard data for admin monitoring"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        dashboard_data = monitoring_service.get_real_time_dashboard_data()
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard data: {str(e)}")

@router.get("/admin/system-health")
async def get_system_health_overview(
    db_session = Depends(get_db_session)
):
    """Get detailed system health overview"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        health_overview = monitoring_service.get_system_health_overview()
        return health_overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system health: {str(e)}")

@router.get("/admin/population-statistics")
async def get_population_statistics(
    db_session = Depends(get_db_session)
):
    """Get detailed NPC population statistics and demographics"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        population_stats = monitoring_service.get_population_statistics()
        return asdict(population_stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving population statistics: {str(e)}")

@router.get("/admin/economic-status")
async def get_economic_cycle_status(
    db_session = Depends(get_db_session)
):
    """Get economic cycle status and trends"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        economic_status = monitoring_service.get_economic_cycle_status()
        return economic_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving economic status: {str(e)}")

@router.get("/admin/crisis-monitoring")
async def get_crisis_monitoring_data(
    db_session = Depends(get_db_session)
):
    """Get comprehensive crisis monitoring and alert data"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        crisis_data = monitoring_service.get_crisis_monitoring_data()
        return crisis_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving crisis monitoring data: {str(e)}")

@router.get("/admin/performance-metrics")
async def get_performance_metrics(
    db_session = Depends(get_db_session)
):
    """Get current performance metrics and KPIs"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        performance_metrics = monitoring_service.get_performance_metrics()
        return performance_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving performance metrics: {str(e)}")

@router.get("/admin/alerts")
async def get_system_alerts(
    limit: int = Query(20, description="Maximum number of alerts to return"),
    include_resolved: bool = Query(False, description="Include resolved alerts"),
    db_session = Depends(get_db_session)
):
    """Get system alerts for monitoring dashboard"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        alerts = monitoring_service.get_recent_alerts(limit=limit)
        
        if not include_resolved:
            alerts = [alert for alert in alerts if not alert.get("resolved", False)]
        
        return {"alerts": alerts, "total_alerts": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")

@router.post("/admin/alerts/{alert_id}/resolve")
async def resolve_system_alert(
    alert_id: str,
    db_session = Depends(get_db_session)
):
    """Mark a system alert as resolved"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        success = monitoring_service.resolve_alert(alert_id)
        
        if success:
            return {"success": True, "message": f"Alert {alert_id} resolved"}
        else:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving alert: {str(e)}")

@router.post("/admin/health-check")
async def trigger_health_check_and_alerts(
    db_session = Depends(get_db_session)
):
    """Trigger a manual system health check and alert generation"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        new_alerts = monitoring_service.check_system_health_and_generate_alerts()
        
        return {
            "health_check_completed": True,
            "new_alerts_generated": len(new_alerts),
            "new_alerts": [asdict(alert) for alert in new_alerts]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing health check: {str(e)}")

@router.get("/admin/analytics")
async def get_detailed_analytics(
    time_range_days: int = Query(7, description="Time range for analytics in days"),
    db_session = Depends(get_db_session)
):
    """Get detailed analytics for the specified time range"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        analytics = monitoring_service.get_detailed_analytics(time_range_days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")

@router.get("/admin/activity-summary")
async def get_activity_summary(
    db_session = Depends(get_db_session)
):
    """Get recent activity summary for the dashboard"""
    try:
        monitoring_service = AutonomousNpcMonitoringService(db_session)
        activity_summary = monitoring_service.get_activity_summary()
        return activity_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving activity summary: {str(e)}")


# === SCHEDULER MANAGEMENT ENDPOINTS ===

@router.get("/admin/scheduler/status")
async def get_scheduler_status():
    """Get current scheduler status and task statistics"""
    try:
        status = autonomous_scheduler.get_scheduler_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving scheduler status: {str(e)}")

@router.post("/admin/scheduler/start")
async def start_scheduler():
    """Start the autonomous NPC scheduler"""
    try:
        autonomous_scheduler.start_scheduler()
        return {"success": True, "message": "Scheduler started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scheduler: {str(e)}")

@router.post("/admin/scheduler/stop")
async def stop_scheduler():
    """Stop the autonomous NPC scheduler"""
    try:
        autonomous_scheduler.stop_scheduler()
        return {"success": True, "message": "Scheduler stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping scheduler: {str(e)}")

@router.post("/admin/scheduler/tasks/{task_name}/enable")
async def enable_scheduled_task(task_name: str):
    """Enable a specific scheduled task"""
    try:
        success = autonomous_scheduler.enable_task(task_name)
        if success:
            return {"success": True, "message": f"Task {task_name} enabled"}
        else:
            raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enabling task: {str(e)}")

@router.post("/admin/scheduler/tasks/{task_name}/disable")
async def disable_scheduled_task(task_name: str):
    """Disable a specific scheduled task"""
    try:
        success = autonomous_scheduler.disable_task(task_name)
        if success:
            return {"success": True, "message": f"Task {task_name} disabled"}
        else:
            raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disabling task: {str(e)}")

@router.post("/admin/scheduler/tasks/{task_name}/trigger")
async def trigger_scheduled_task_manually(task_name: str):
    """Manually trigger a scheduled task"""
    try:
        result = autonomous_scheduler.trigger_task_manually(task_name)
        if result:
            return {
                "success": True,
                "message": f"Task {task_name} triggered manually",
                "execution_result": asdict(result)
            }
        else:
            raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering task: {str(e)}")


# === MASS OPERATIONS ENDPOINTS ===

@router.post("/admin/operations/mass-crisis-event")
async def trigger_mass_crisis_event(
    crisis_type: str,
    crisis_description: str,
    crisis_severity: float = Field(ge=1.0, le=10.0),
    affected_regions: Optional[List[str]] = None,
    npc_selection_criteria: Optional[Dict[str, Any]] = None,
    db_session = Depends(get_db_session)
):
    """Trigger a crisis event affecting multiple NPCs"""
    try:
        coordinator = AutonomousNpcCoordinator(db_session)
        result = await coordinator.trigger_mass_crisis_event(
            crisis_type, crisis_description, crisis_severity,
            affected_regions, npc_selection_criteria
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering mass crisis event: {str(e)}")

@router.post("/admin/operations/batch-emotional-decay")
async def trigger_batch_emotional_decay(
    npc_ids: Optional[List[UUID]] = None,
    db_session = Depends(get_db_session)
):
    """Process emotional decay for multiple NPCs in batch"""
    try:
        coordinator = AutonomousNpcCoordinator(db_session)
        result = await coordinator.bulk_process_emotional_decay(npc_ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch emotional decay: {str(e)}")

@router.post("/admin/operations/batch-personality-evolution")
async def trigger_batch_personality_evolution(
    npc_ids: Optional[List[UUID]] = None,
    db_session = Depends(get_db_session)
):
    """Process personality evolution for multiple NPCs in batch"""
    try:
        coordinator = AutonomousNpcCoordinator(db_session)
        result = await coordinator.bulk_process_personality_evolution(npc_ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch personality evolution: {str(e)}") 