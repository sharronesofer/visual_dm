"""
Tension System API Router

Provides comprehensive REST endpoints for the tension system following
FastAPI and Development Bible standards with complete OpenAPI documentation.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Body, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
import json

from backend.systems.tension import UnifiedTensionManager
from backend.systems.tension.models.tension_events import TensionEventType
from backend.systems.tension.monitoring import TensionMetrics, TensionDashboard, TensionAnalytics, TensionAlerts

# Initialize the tension system and monitoring
tension_manager = UnifiedTensionManager()
metrics = TensionMetrics()
analytics = TensionAnalytics()
alerts = TensionAlerts()
dashboard = TensionDashboard(metrics, analytics, alerts)

# Create router with enhanced documentation
router = APIRouter(
    prefix="/api/tension",
    tags=["tension"],
    responses={
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"},
        422: {"description": "Validation error"}
    },
)


# Enhanced Pydantic models for API requests/responses with examples
class TensionResponse(BaseModel):
    """Response model for tension data"""
    region_id: str = Field(..., description="Region identifier", example="westlands")
    poi_id: str = Field(..., description="Point of Interest identifier", example="rusty_anchor_tavern")
    tension_level: float = Field(..., description="Current tension level (0.0-1.0)", example=0.65, ge=0.0, le=1.0)
    last_updated: datetime = Field(..., description="Timestamp of last update", example="2024-01-15T14:30:00Z")
    modifiers: List[Dict[str, Any]] = Field(default_factory=list, description="Active tension modifiers", example=[
        {"source": "recent_combat", "impact": 0.15, "expires_at": "2024-01-15T15:30:00Z"}
    ])

    class Config:
        schema_extra = {
            "example": {
                "region_id": "westlands",
                "poi_id": "rusty_anchor_tavern", 
                "tension_level": 0.65,
                "last_updated": "2024-01-15T14:30:00Z",
                "modifiers": [
                    {
                        "source": "recent_combat",
                        "impact": 0.15,
                        "expires_at": "2024-01-15T15:30:00Z"
                    }
                ]
            }
        }


class TensionEventRequest(BaseModel):
    """Request model for creating tension events"""
    event_type: str = Field(..., description="Type of tension event", example="player_combat")
    data: Dict[str, Any] = Field(..., description="Event-specific data", example={
        "lethal": True, "enemies_defeated": 3, "difficulty": "normal"
    })
    severity: Optional[float] = Field(1.0, description="Event severity multiplier", example=1.5, ge=0.1, le=5.0)
    description: Optional[str] = Field(None, description="Human-readable event description", example="Tavern brawl turned deadly")

    class Config:
        schema_extra = {
            "example": {
                "event_type": "player_combat",
                "data": {
                    "lethal": True,
                    "enemies_defeated": 3,
                    "difficulty": "normal"
                },
                "severity": 1.5,
                "description": "Tavern brawl turned deadly"
            }
        }


class TensionModifierRequest(BaseModel):
    """Request model for adding tension modifiers"""
    source: str = Field(..., description="Source of the modifier", example="festival")
    impact: float = Field(..., description="Impact on tension (-1.0 to 1.0)", example=-0.2, ge=-1.0, le=1.0)
    duration_hours: float = Field(..., description="Duration in hours", example=24.0, gt=0)
    description: Optional[str] = Field(None, description="Description of modifier", example="Harvest festival reduces tension")

    class Config:
        schema_extra = {
            "example": {
                "source": "festival",
                "impact": -0.2,
                "duration_hours": 24.0,
                "description": "Harvest festival reduces tension"
            }
        }


class ConflictTriggerResponse(BaseModel):
    """Response model for conflict triggers"""
    name: str = Field(..., description="Conflict name", example="civil_unrest")
    triggered: bool = Field(..., description="Whether conflict is active", example=True)
    tension_threshold: float = Field(..., description="Tension threshold for trigger", example=0.8)
    probability: float = Field(..., description="Probability of occurrence", example=0.65)
    details: Dict[str, Any] = Field(..., description="Additional conflict details", example={
        "faction": "peasants", "cause": "taxation"
    })


class RegionSummaryResponse(BaseModel):
    """Response model for region tension summary"""
    region_id: str = Field(..., description="Region identifier", example="westlands")
    poi_count: int = Field(..., description="Number of POIs in region", example=15)
    average_tension: float = Field(..., description="Average tension across POIs", example=0.45)
    max_tension: float = Field(..., description="Highest tension in region", example=0.78)
    high_tension_pois: List[str] = Field(..., description="POIs with high tension", example=["tavern", "barracks"])
    conflicts: List[ConflictTriggerResponse] = Field(default_factory=list, description="Active conflicts")


class DashboardResponse(BaseModel):
    """Response model for dashboard data"""
    dashboard_type: str = Field(..., description="Type of dashboard", example="overview")
    timestamp: datetime = Field(..., description="Data timestamp", example="2024-01-15T14:30:00Z")
    data: Dict[str, Any] = Field(..., description="Dashboard data")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Active alerts")


class EventTypesResponse(BaseModel):
    """Response model for available event types"""
    event_types: List[str] = Field(..., description="Available event types")
    total_count: int = Field(..., description="Total number of event types")
    categories: Dict[str, List[str]] = Field(..., description="Event types by category")


class BulkEventRequest(BaseModel):
    """Request model for bulk event processing"""
    events: List[Dict[str, Any]] = Field(..., description="List of events to process", min_items=1, max_items=50)

    class Config:
        schema_extra = {
            "example": {
                "events": [
                    {
                        "region_id": "westlands",
                        "poi_id": "tavern",
                        "event_type": "player_combat",
                        "data": {"lethal": True},
                        "severity": 1.0
                    },
                    {
                        "region_id": "eastlands", 
                        "poi_id": "market",
                        "event_type": "festival",
                        "data": {"attendance": "high"},
                        "severity": 1.2
                    }
                ]
            }
        }


# Core Tension Endpoints with enhanced documentation
@router.get(
    "/regions/{region_id}/pois/{poi_id}/tension", 
    response_model=TensionResponse,
    summary="Get Current Tension Level",
    description="""
    Retrieve the current tension level for a specific Point of Interest (POI) within a region.
    
    Returns comprehensive tension data including:
    - Current tension level (0.0 = peaceful, 1.0 = maximum tension)
    - Active modifiers affecting tension
    - Last update timestamp
    
    This endpoint automatically records the query as a metric for monitoring purposes.
    """,
    responses={
        200: {
            "description": "Tension data retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "region_id": "westlands",
                        "poi_id": "rusty_anchor_tavern",
                        "tension_level": 0.65,
                        "last_updated": "2024-01-15T14:30:00Z",
                        "modifiers": [
                            {
                                "source": "recent_combat",
                                "impact": 0.15,
                                "expires_at": "2024-01-15T15:30:00Z"
                            }
                        ]
                    }
                }
            }
        },
        404: {"description": "Region or POI not found"},
        500: {"description": "Error calculating tension"}
    }
)
async def get_tension(
    region_id: str = Path(..., description="Region identifier (e.g., 'westlands', 'eastlands')", example="westlands"),
    poi_id: str = Path(..., description="POI identifier (e.g., 'tavern', 'market', 'castle')", example="rusty_anchor_tavern")
):
    """Get current tension level for a specific location"""
    try:
        tension_level = tension_manager.calculate_tension(region_id, poi_id)
        modifiers = tension_manager.get_active_modifiers(region_id, poi_id)
        
        # Record metric
        metrics.record_tension_metric(region_id, poi_id, tension_level)
        
        return TensionResponse(
            region_id=region_id,
            poi_id=poi_id,
            tension_level=tension_level,
            last_updated=datetime.utcnow(),
            modifiers=modifiers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating tension: {str(e)}")


@router.post(
    "/regions/{region_id}/pois/{poi_id}/events",
    summary="Create Tension Event",
    description="""
    Create a new tension event that affects the tension level of a specific location.
    
    Events can include:
    - Combat events (player_combat, faction_warfare, assassination)
    - Environmental events (plague_outbreak, natural_disaster)
    - Political events (rebellion, regime_change)
    - Social events (festival, riot, protest)
    
    The system will automatically:
    - Calculate tension impact based on event type and data
    - Apply configured modifiers for time of day, weather, etc.
    - Record metrics for monitoring
    - Update the location's tension level
    """,
    responses={
        200: {
            "description": "Event processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Event processed successfully",
                        "new_tension_level": 0.78,
                        "event_type": "player_combat",
                        "timestamp": "2024-01-15T14:30:00Z"
                    }
                }
            }
        },
        400: {"description": "Invalid event type or data"},
        500: {"description": "Error processing event"}
    }
)
async def create_tension_event(
    region_id: str = Path(..., description="Region identifier", example="westlands"),
    poi_id: str = Path(..., description="POI identifier", example="rusty_anchor_tavern"),
    event: TensionEventRequest = Body(..., description="Event data")
):
    """Create a new tension event"""
    try:
        # Validate event type
        if not hasattr(TensionEventType, event.event_type.upper()):
            available_types = [e.value for e in TensionEventType][:10]  # Show first 10
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid event type: {event.event_type}. Available types include: {', '.join(available_types)}..."
            )
        
        event_type = TensionEventType(event.event_type)
        
        # Update tension from event
        tension_manager.update_tension_from_event(
            region_id, poi_id, event_type, event.data
        )
        
        # Get updated tension
        new_tension = tension_manager.calculate_tension(region_id, poi_id)
        
        # Record metrics
        metrics.record_tension_metric(
            region_id, poi_id, new_tension, event.event_type, event.data
        )
        
        return {
            "message": "Event processed successfully",
            "new_tension_level": new_tension,
            "event_type": event.event_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing event: {str(e)}")


@router.post("/regions/{region_id}/pois/{poi_id}/modifiers")
async def add_tension_modifier(
    region_id: str = Path(..., description="Region identifier"),
    poi_id: str = Path(..., description="POI identifier"),
    modifier: TensionModifierRequest = Body(..., description="Modifier data")
):
    """Add a temporary tension modifier"""
    try:
        tension_manager.add_tension_modifier(
            region_id, poi_id, modifier.source, modifier.impact, 
            modifier.duration_hours, modifier.description
        )
        
        new_tension = tension_manager.calculate_tension(region_id, poi_id)
        
        return {
            "message": "Modifier added successfully",
            "new_tension_level": new_tension,
            "modifier_expires_in_hours": modifier.duration_hours,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding modifier: {str(e)}")


@router.get("/regions/{region_id}/pois/{poi_id}/modifiers")
async def get_active_modifiers(
    region_id: str = Path(..., description="Region identifier"),
    poi_id: str = Path(..., description="POI identifier")
):
    """Get all active modifiers for a location"""
    try:
        modifiers = tension_manager.get_active_modifiers(region_id, poi_id)
        return {
            "region_id": region_id,
            "poi_id": poi_id,
            "active_modifiers": modifiers,
            "count": len(modifiers),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting modifiers: {str(e)}")


# Conflict and Analysis Endpoints
@router.get("/regions/{region_id}/conflicts", response_model=List[ConflictTriggerResponse])
async def check_conflicts(
    region_id: str = Path(..., description="Region identifier"),
    include_details: bool = Query(False, description="Include detailed conflict information")
):
    """Check for potential conflicts in a region"""
    try:
        conflicts = tension_manager.check_conflicts(region_id)
        
        response = []
        for conflict in conflicts:
            response.append(ConflictTriggerResponse(
                name=conflict.get('name', 'unknown'),
                triggered=conflict.get('triggered', False),
                tension_threshold=conflict.get('tension_threshold', 0.0),
                probability=conflict.get('probability', 0.0),
                details=conflict if include_details else {}
            ))
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking conflicts: {str(e)}")


@router.get("/regions/{region_id}/summary")
async def get_region_summary(
    region_id: str = Path(..., description="Region identifier"),
    hours_back: int = Query(24, description="Hours of data to analyze", ge=1, le=168)
):
    """Get comprehensive summary for a region"""
    try:
        # Get tension summary from manager
        summary = tension_manager.get_region_summary(region_id)
        
        # Get metrics analysis
        analysis = metrics.get_region_analysis(region_id, hours_back)
        
        # Combine data
        combined_summary = {
            **summary,
            "analysis_period_hours": hours_back,
            "detailed_analysis": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return combined_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting region summary: {str(e)}")


# Monitoring and Analytics Endpoints
@router.get("/dashboard/overview")
async def get_dashboard_overview():
    """Get the main tension system dashboard overview"""
    try:
        return dashboard.get_overview_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard: {str(e)}")


@router.get("/dashboard/regions/{region_id}")
async def get_region_dashboard(
    region_id: str = Path(..., description="Region identifier"),
    hours_back: int = Query(24, description="Hours of data to analyze", ge=1, le=168)
):
    """Get detailed dashboard for a specific region"""
    try:
        return dashboard.get_region_dashboard(region_id, hours_back)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting region dashboard: {str(e)}")


@router.get("/dashboard/health")
async def get_system_health():
    """Get system health dashboard"""
    try:
        return dashboard.get_system_health_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting health dashboard: {str(e)}")


@router.get("/dashboard/analytics")
async def get_analytics_dashboard(
    time_window_hours: int = Query(168, description="Analysis time window in hours", ge=1, le=720)
):
    """Get comprehensive analytics dashboard"""
    try:
        return dashboard.get_analytics_dashboard(time_window_hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics dashboard: {str(e)}")


@router.get("/dashboard/alerts")
async def get_alerts_dashboard():
    """Get alerts and monitoring dashboard"""
    try:
        return dashboard.get_alerts_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alerts dashboard: {str(e)}")


@router.get("/dashboard/live")
async def get_live_data():
    """Get real-time data stream for live updates"""
    try:
        return dashboard.get_live_data_stream()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting live data: {str(e)}")


# Statistics and Reporting Endpoints
@router.get("/statistics/summary")
async def get_statistics_summary(
    hours_back: int = Query(24, description="Hours of data to analyze", ge=1, le=168)
):
    """Get system-wide statistics summary"""
    try:
        return metrics.get_tension_summary(hours_back)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")


@router.get("/statistics/alerts")
async def get_alert_status():
    """Get current alert status"""
    try:
        return {
            "alerts": metrics.get_alert_status(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alerts: {str(e)}")


@router.get("/export/metrics")
async def export_metrics(
    format: str = Query("json", description="Export format"),
    hours_back: int = Query(24, description="Hours of data to export", ge=1, le=168)
):
    """Export metrics data for external analysis"""
    try:
        if format not in ["json"]:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
        exported_data = metrics.export_metrics(format, hours_back)
        
        return {
            "format": format,
            "hours_back": hours_back,
            "data": json.loads(exported_data) if format == "json" else exported_data,
            "export_timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting metrics: {str(e)}")


# Administrative Endpoints
@router.post("/admin/clear-cache")
async def clear_dashboard_cache():
    """Clear dashboard cache (admin only)"""
    try:
        dashboard.clear_cache()
        return {
            "message": "Dashboard cache cleared successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@router.get("/admin/configuration")
async def get_system_configuration():
    """Get tension system configuration"""
    try:
        # This would return actual configuration in production
        return {
            "monitoring_enabled": True,
            "real_time_updates": True,
            "cache_ttl_seconds": 30,
            "max_history_size": 10000,
            "alert_thresholds": {
                "high_tension": 0.8,
                "critical_tension": 0.9
            },
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting configuration: {str(e)}")


# WebSocket endpoint for real-time updates
@router.websocket("/ws/live-updates")
async def websocket_live_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time tension updates"""
    await websocket.accept()
    try:
        while True:
            # Get live data
            live_data = dashboard.get_live_data_stream()
            
            # Send to client
            await websocket.send_json(live_data)
            
            # Wait for update interval
            import asyncio
            await asyncio.sleep(30)  # Update every 30 seconds
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close(code=1000, reason=f"Error in live updates: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Basic health check for the tension system"""
    try:
        # Perform basic system checks
        health_report = metrics.get_system_health_report()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": health_report.get("status", "unknown"),
            "active_regions": len(metrics.region_metrics),
            "uptime_hours": health_report.get("system_stats", {}).get("uptime_hours", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"System unhealthy: {str(e)}")


@router.get(
    "/event-types",
    response_model=EventTypesResponse,
    summary="Get Available Event Types",
    description="""
    Retrieve all available tension event types organized by category.
    
    Returns:
    - Complete list of event types
    - Total count
    - Events organized by category (Combat, Environmental, Political, etc.)
    
    Use this endpoint to discover what event types are available for creating tension events.
    """,
    responses={
        200: {
            "description": "Event types retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "event_types": ["player_combat", "plague_outbreak", "festival"],
                        "total_count": 87,
                        "categories": {
                            "Combat": ["player_combat", "faction_warfare"],
                            "Environmental": ["plague_outbreak", "earthquake"],
                            "Social": ["festival", "riot"]
                        }
                    }
                }
            }
        }
    }
)
async def get_event_types():
    """Get all available event types organized by category"""
    try:
        # Get all event types
        all_events = [event.value for event in TensionEventType]
        
        # Organize by category (first word of event name)
        categories = {}
        for event in all_events:
            category = event.split('_')[0].title()
            if category not in categories:
                categories[category] = []
            categories[category].append(event)
        
        return EventTypesResponse(
            event_types=all_events,
            total_count=len(all_events),
            categories=categories
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving event types: {str(e)}")


# Bulk operations endpoint
@router.post("/bulk/events")
async def create_bulk_events(
    events: List[Dict[str, Any]] = Body(..., description="List of events to process")
):
    """Process multiple tension events in bulk"""
    try:
        results = []
        
        for event_data in events:
            try:
                region_id = event_data.get("region_id")
                poi_id = event_data.get("poi_id")
                event_type = TensionEventType(event_data.get("event_type"))
                data = event_data.get("data", {})
                
                # Process event
                tension_manager.update_tension_from_event(region_id, poi_id, event_type, data)
                new_tension = tension_manager.calculate_tension(region_id, poi_id)
                
                # Record metrics
                metrics.record_tension_metric(region_id, poi_id, new_tension, event_type.value, data)
                
                results.append({
                    "success": True,
                    "region_id": region_id,
                    "poi_id": poi_id,
                    "new_tension": new_tension
                })
                
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "event_data": event_data
                })
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        return {
            "total_processed": len(results),
            "successful": successful,
            "failed": failed,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing bulk events: {str(e)}")


# Faction Relationship Endpoints (Development Bible: -100 to +100 scale)

@router.get("/faction-relationships/{faction_a_id}/{faction_b_id}")
async def get_faction_relationship(
    faction_a_id: str,
    faction_b_id: str,
    service: TensionService = Depends(get_tension_service)
):
    """Get relationship between two factions"""
    relationship = service.get_faction_relationship(faction_a_id, faction_b_id)
    if not relationship:
        return {
            "faction_a_id": faction_a_id,
            "faction_b_id": faction_b_id,
            "tension_level": 0,
            "relationship_type": "neutral",
            "exists": False
        }
    
    return {
        "faction_a_id": relationship.faction_a_id,
        "faction_b_id": relationship.faction_b_id,
        "tension_level": relationship.tension_level,
        "relationship_type": relationship.relationship_type,
        "last_updated": relationship.last_updated.isoformat(),
        "recent_events": relationship.recent_events,
        "war_threshold": relationship.war_threshold,
        "alliance_threshold": relationship.alliance_threshold,
        "exists": True
    }


@router.post("/faction-relationships/{faction_a_id}/{faction_b_id}/update-tension")
async def update_faction_tension(
    faction_a_id: str,
    faction_b_id: str,
    tension_change: int,
    source: str = "api_call",
    service: TensionService = Depends(get_tension_service)
):
    """Update tension between two factions (Development Bible: -100 to +100 scale)"""
    relationship = service.update_faction_tension(faction_a_id, faction_b_id, tension_change, source)
    
    return {
        "faction_a_id": relationship.faction_a_id,
        "faction_b_id": relationship.faction_b_id,
        "tension_level": relationship.tension_level,
        "relationship_type": relationship.relationship_type,
        "tension_change_applied": tension_change,
        "last_updated": relationship.last_updated.isoformat(),
        "at_war": relationship.tension_level >= relationship.war_threshold,
        "in_alliance": relationship.tension_level <= relationship.alliance_threshold
    }


@router.get("/faction-relationships/wars")
async def get_active_wars(
    service: TensionService = Depends(get_tension_service)
):
    """Get all faction relationships currently at war"""
    wars = service.get_faction_wars()
    
    return {
        "active_wars": [
            {
                "faction_a_id": war.faction_a_id,
                "faction_b_id": war.faction_b_id,
                "tension_level": war.tension_level,
                "relationship_type": war.relationship_type,
                "last_updated": war.last_updated.isoformat(),
                "recent_events": war.recent_events[-3:] if war.recent_events else []
            }
            for war in wars
        ],
        "total_wars": len(wars)
    }


@router.get("/faction-relationships/alliances")
async def get_active_alliances(
    service: TensionService = Depends(get_tension_service)
):
    """Get all faction relationships that are alliances"""
    alliances = service.get_faction_alliances()
    
    return {
        "active_alliances": [
            {
                "faction_a_id": alliance.faction_a_id,
                "faction_b_id": alliance.faction_b_id,
                "tension_level": alliance.tension_level,
                "relationship_type": alliance.relationship_type,
                "last_updated": alliance.last_updated.isoformat(),
                "recent_events": alliance.recent_events[-3:] if alliance.recent_events else []
            }
            for alliance in alliances
        ],
        "total_alliances": len(alliances)
    }


@router.post("/faction-relationships/decay")
async def decay_faction_tensions(
    service: TensionService = Depends(get_tension_service)
):
    """Apply natural decay to all faction relationships"""
    result = service.decay_all_faction_tension()
    
    return {
        "message": "Faction tension decay applied",
        "relationships_processed": result['processed'],
        "relationships_decayed": result['decayed'],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/faction-relationships/{faction_id}/status")
async def get_faction_diplomatic_status(
    faction_id: str,
    service: TensionService = Depends(get_tension_service)
):
    """Get diplomatic status for a specific faction"""
    relationships = service.get_faction_relationships_for_faction(faction_id)
    
    wars = []
    alliances = []
    neutral = []
    hostile = []
    
    for rel in relationships:
        other_faction = rel.faction_b_id if rel.faction_a_id == faction_id else rel.faction_a_id
        
        rel_info = {
            "faction_id": other_faction,
            "tension_level": rel.tension_level,
            "relationship_type": rel.relationship_type,
            "last_updated": rel.last_updated.isoformat()
        }
        
        if rel.tension_level >= 70:
            wars.append(rel_info)
        elif rel.tension_level <= -50:
            alliances.append(rel_info)
        elif rel.tension_level >= 30:
            hostile.append(rel_info)
        else:
            neutral.append(rel_info)
    
    return {
        "faction_id": faction_id,
        "diplomatic_status": {
            "wars": wars,
            "alliances": alliances,
            "hostile": hostile,
            "neutral": neutral
        },
        "summary": {
            "total_relationships": len(relationships),
            "active_wars": len(wars),
            "active_alliances": len(alliances),
            "hostile_relationships": len(hostile),
            "neutral_relationships": len(neutral)
        }
    } 