"""
Chaos API

FastAPI router for chaos system endpoints.
Provides REST API access to chaos system functionality.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

from backend.systems.chaos.core.chaos_engine import get_chaos_engine
from backend.infrastructure.systems.chaos.models.chaos_events import ChaosEventType, EventSeverity

logger = logging.getLogger(__name__)


# Pydantic models for API responses
class ChaosStatusResponse(BaseModel):
    """Response model for chaos system status"""
    chaos_score: float
    chaos_level: str
    is_running: bool
    is_paused: bool
    system_health: float
    pressure_stability: float
    last_update: str
    active_events_count: int
    connected_systems: List[str]


class PressureSummaryResponse(BaseModel):
    """Response model for pressure summary"""
    overall_pressure: float
    source_breakdown: Dict[str, float]
    regional_pressure: Dict[str, float]
    last_calculation: str


class EventSummaryResponse(BaseModel):
    """Response model for event summary"""
    event_id: str
    event_type: str
    severity: str
    title: str
    description: str
    affected_regions: List[str]
    global_event: bool
    triggered_at: Optional[str]
    remaining_hours: float
    chaos_score_at_trigger: float


class SystemHealthResponse(BaseModel):
    """Response model for system health"""
    overall_health: str
    connected_systems: int
    failed_systems: int
    system_status: Dict[str, Any]
    integration_metrics: Dict[str, Any]
    last_check: str


class ChaosAPI:
    """
    API controller for chaos system endpoints
    """
    
    def __init__(self):
        self.chaos_engine = get_chaos_engine()
        
    async def get_chaos_status(self) -> ChaosStatusResponse:
        """Get current chaos system status"""
        try:
            chaos_state = self.chaos_engine.get_current_chaos_state()
            metrics = self.chaos_engine.get_system_metrics()
            
            return ChaosStatusResponse(
                chaos_score=chaos_state.get('current_chaos_score', 0.0),
                chaos_level=chaos_state.get('current_chaos_level', 'dormant'),
                is_running=metrics.get('is_running', False),
                is_paused=metrics.get('is_paused', False),
                system_health=metrics.get('system_health', 0.0),
                pressure_stability=metrics.get('pressure_stability', 0.0),
                last_update=chaos_state.get('calculation_timestamp', datetime.now().isoformat()),
                active_events_count=len(self.chaos_engine.get_active_events()),
                connected_systems=metrics.get('connected_systems', [])
            )
            
        except Exception as e:
            logger.error(f"Error getting chaos status: {e}")
            raise HTTPException(status_code=500, detail="Failed to get chaos status")
    
    async def get_pressure_summary(self) -> PressureSummaryResponse:
        """Get current pressure summary"""
        try:
            pressure_summary = self.chaos_engine.get_pressure_summary()
            
            return PressureSummaryResponse(
                overall_pressure=pressure_summary.get('overall_pressure', 0.0),
                source_breakdown=pressure_summary.get('source_breakdown', {}),
                regional_pressure=pressure_summary.get('regional_pressure', {}),
                last_calculation=pressure_summary.get('last_calculation', datetime.now().isoformat())
            )
            
        except Exception as e:
            logger.error(f"Error getting pressure summary: {e}")
            raise HTTPException(status_code=500, detail="Failed to get pressure summary")
    
    async def get_active_events(self) -> List[EventSummaryResponse]:
        """Get all currently active chaos events"""
        try:
            events = self.chaos_engine.get_active_events()
            
            return [
                EventSummaryResponse(
                    event_id=event.event_id,
                    event_type=event.event_type.value,
                    severity=event.severity.value,
                    title=event.title,
                    description=event.description,
                    affected_regions=[str(r) for r in event.affected_regions],
                    global_event=event.global_event,
                    triggered_at=event.triggered_at.isoformat() if event.triggered_at else None,
                    remaining_hours=event.get_remaining_duration(),
                    chaos_score_at_trigger=event.chaos_score_at_trigger
                )
                for event in events
            ]
            
        except Exception as e:
            logger.error(f"Error getting active events: {e}")
            raise HTTPException(status_code=500, detail="Failed to get active events")
    
    async def get_event_statistics(self) -> Dict[str, Any]:
        """Get event system statistics"""
        try:
            return self.chaos_engine.get_event_statistics()
            
        except Exception as e:
            logger.error(f"Error getting event statistics: {e}")
            raise HTTPException(status_code=500, detail="Failed to get event statistics")
    
    async def get_system_health(self) -> SystemHealthResponse:
        """Get system health status"""
        try:
            health = await self.chaos_engine.get_system_health()
            
            return SystemHealthResponse(
                overall_health=health.get('overall_health', 'unknown'),
                connected_systems=health.get('connected_systems', 0),
                failed_systems=health.get('failed_systems', 0),
                system_status=health.get('system_status', {}),
                integration_metrics=health.get('integration_metrics', {}),
                last_check=health.get('last_check', datetime.now().isoformat())
            )
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            raise HTTPException(status_code=500, detail="Failed to get system health")
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            return self.chaos_engine.get_system_metrics()
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            raise HTTPException(status_code=500, detail="Failed to get system metrics")
    
    async def pause_chaos_engine(self) -> Dict[str, str]:
        """Pause the chaos engine"""
        try:
            self.chaos_engine.pause()
            return {"status": "paused", "message": "Chaos engine paused"}
            
        except Exception as e:
            logger.error(f"Error pausing chaos engine: {e}")
            raise HTTPException(status_code=500, detail="Failed to pause chaos engine")
    
    async def resume_chaos_engine(self) -> Dict[str, str]:
        """Resume the chaos engine"""
        try:
            self.chaos_engine.resume()
            return {"status": "resumed", "message": "Chaos engine resumed"}
            
        except Exception as e:
            logger.error(f"Error resuming chaos engine: {e}")
            raise HTTPException(status_code=500, detail="Failed to resume chaos engine")
    
    async def apply_mitigation(self, mitigation_type: str, effectiveness: float, 
                             duration_hours: float, source_id: str, source_type: str,
                             description: str = "", affected_regions: List[str] = None,
                             affected_sources: List[str] = None) -> Dict[str, Any]:
        """Apply a mitigation factor (for testing/admin purposes)"""
        try:
            success = await self.chaos_engine.apply_mitigation(
                mitigation_type=mitigation_type,
                effectiveness=effectiveness,
                duration_hours=duration_hours,
                source_id=source_id,
                source_type=source_type,
                description=description,
                affected_regions=affected_regions or [],
                affected_sources=affected_sources or []
            )
            
            if success:
                return {
                    "status": "success",
                    "message": f"Applied mitigation: {mitigation_type}",
                    "mitigation_type": mitigation_type,
                    "effectiveness": effectiveness,
                    "duration_hours": duration_hours
                }
            else:
                raise HTTPException(status_code=400, detail="Failed to apply mitigation")
                
        except Exception as e:
            logger.error(f"Error applying mitigation: {e}")
            raise HTTPException(status_code=500, detail="Failed to apply mitigation")
    
    async def force_trigger_event(self, event_type: str, severity: str = "moderate",
                                regions: List[str] = None) -> Dict[str, Any]:
        """Force trigger a chaos event (for testing/admin purposes)"""
        try:
            success = await self.chaos_engine.force_trigger_event(
                event_type=event_type,
                severity=severity,
                regions=regions or []
            )
            
            if success:
                return {
                    "status": "success",
                    "message": f"Force triggered event: {event_type}",
                    "event_type": event_type,
                    "severity": severity,
                    "regions": regions or []
                }
            else:
                raise HTTPException(status_code=400, detail="Failed to trigger event")
                
        except Exception as e:
            logger.error(f"Error force triggering event: {e}")
            raise HTTPException(status_code=500, detail="Failed to trigger event")


def create_chaos_api_routes() -> APIRouter:
    """Create and configure the chaos API router"""
    
    router = APIRouter(prefix="/api/v1/chaos", tags=["chaos"])
    chaos_api = ChaosAPI()
    
    @router.get("/status", response_model=ChaosStatusResponse)
    async def get_chaos_status():
        """Get current chaos system status"""
        return await chaos_api.get_chaos_status()
    
    @router.get("/pressure", response_model=PressureSummaryResponse)
    async def get_pressure_summary():
        """Get current pressure summary"""
        return await chaos_api.get_pressure_summary()
    
    @router.get("/events", response_model=List[EventSummaryResponse])
    async def get_active_events():
        """Get all currently active chaos events"""
        return await chaos_api.get_active_events()
    
    @router.get("/events/statistics")
    async def get_event_statistics():
        """Get event system statistics"""
        return await chaos_api.get_event_statistics()
    
    @router.get("/health", response_model=SystemHealthResponse)
    async def get_system_health():
        """Get system health status"""
        return await chaos_api.get_system_health()
    
    @router.get("/metrics")
    async def get_system_metrics():
        """Get comprehensive system metrics"""
        return await chaos_api.get_system_metrics()
    
    @router.post("/pause")
    async def pause_chaos_engine():
        """Pause the chaos engine"""
        return await chaos_api.pause_chaos_engine()
    
    @router.post("/resume")
    async def resume_chaos_engine():
        """Resume the chaos engine"""
        return await chaos_api.resume_chaos_engine()
    
    @router.post("/mitigation")
    async def apply_mitigation(
        mitigation_type: str = Query(..., description="Type of mitigation to apply"),
        effectiveness: float = Query(..., description="Effectiveness (0.0-1.0)"),
        duration_hours: float = Query(..., description="Duration in hours"),
        source_id: str = Query(..., description="Source ID"),
        source_type: str = Query(..., description="Source type"),
        description: str = Query("", description="Optional description"),
        affected_regions: Optional[List[str]] = Query(None, description="Affected regions"),
        affected_sources: Optional[List[str]] = Query(None, description="Affected pressure sources")
    ):
        """Apply a mitigation factor (testing/admin only)"""
        return await chaos_api.apply_mitigation(
            mitigation_type, effectiveness, duration_hours, source_id, source_type,
            description, affected_regions, affected_sources
        )
    
    @router.post("/events/trigger")
    async def force_trigger_event(
        event_type: str = Query(..., description="Event type to trigger"),
        severity: str = Query("moderate", description="Event severity"),
        regions: Optional[List[str]] = Query(None, description="Affected regions")
    ):
        """Force trigger a chaos event (testing/admin only)"""
        return await chaos_api.force_trigger_event(event_type, severity, regions)
    
    return router 