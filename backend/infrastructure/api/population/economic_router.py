"""
Economic System API Router (Infrastructure Layer)

Provides REST API endpoints for managing economic systems that affect population:
- Economic state management and monitoring
- Trade route creation and management
- Resource availability updates
- Economic event triggering and tracking
- Economic effects on population dynamics

This router integrates economic business logic with API infrastructure.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from backend.systems.population.models.economic_models import (
    economic_engine,
    EconomicStatus,
    ResourceType,
    TradeRouteStatus,
    ResourceAvailability,
    TradeRoute,
    EconomicEvent,
    EconomicState
)

# Import WebSocket integration for notifications
try:
    from backend.infrastructure.api.population.websocket_integration import (
        event_integrator
    )
    WEBSOCKET_INTEGRATION_AVAILABLE = True
except ImportError:
    event_integrator = None
    WEBSOCKET_INTEGRATION_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/economic", tags=["population-economic"])


# Pydantic models for request/response validation
class EconomicStateResponse(BaseModel):
    """Response model for economic state"""
    settlement_id: str
    prosperity_level: float
    economic_status: str
    wealth_per_capita: float
    trade_volume: float
    active_trade_routes: int
    trade_partners: List[str]
    prosperity_trend: float
    last_updated: datetime
    active_events: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ResourceUpdate(BaseModel):
    """Model for resource availability updates"""
    resource_type: ResourceType
    scarcity_change: float = Field(..., ge=-1.0, le=1.0, description="Change in scarcity level (-1.0 to 1.0)")
    quality_change: float = Field(0.0, ge=-1.0, le=1.0, description="Change in quality modifier")


class TradeRouteCreate(BaseModel):
    """Model for creating trade routes"""
    origin_settlement: str
    destination_settlement: str
    primary_goods: List[ResourceType]
    distance: float = Field(100.0, gt=0, description="Distance in arbitrary units")
    safety_level: TradeRouteStatus = TradeRouteStatus.SAFE


class TradeRouteResponse(BaseModel):
    """Response model for trade routes"""
    route_id: str
    origin_settlement: str
    destination_settlement: str
    distance: float
    safety_level: str
    primary_goods: List[str]
    trade_volume_modifier: float
    travel_time_days: int
    prosperity_bonus: float
    migration_influence: float
    is_active: bool
    effective_trade_bonus: float
    last_updated: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EconomicEventCreate(BaseModel):
    """Model for creating economic events"""
    event_type: str = Field(..., description="Type of economic event")
    name: str = Field(..., description="Name of the event")
    description: str = Field(..., description="Description of the event")
    affected_settlements: List[str] = Field(..., description="Settlements affected by this event")
    duration_days: int = Field(30, ge=1, le=365, description="Duration of the event in days")
    
    # Optional population effects
    population_growth_modifier: Optional[float] = Field(None, ge=0.1, le=3.0)
    migration_pressure_modifier: Optional[float] = Field(None, ge=0.1, le=3.0)
    disease_resistance_modifier: Optional[float] = Field(None, ge=0.1, le=3.0)
    
    # Optional economic effects
    prosperity_change: Optional[float] = Field(None, ge=-1.0, le=1.0)
    resource_effects: Optional[Dict[str, float]] = None
    completion_effects: Optional[Dict[str, Any]] = None


class EconomicEventResponse(BaseModel):
    """Response model for economic events"""
    event_id: str
    event_type: str
    name: str
    description: str
    start_date: datetime
    duration_days: int
    affected_settlements: List[str]
    is_active: bool
    population_effects: Dict[str, float]
    economic_effects: Dict[str, Any]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@router.get("/state/{settlement_id}", response_model=EconomicStateResponse)
async def get_economic_state(settlement_id: str):
    """Get the economic state of a specific settlement"""
    try:
        state = economic_engine.get_economic_state(settlement_id)
        
        return EconomicStateResponse(
            settlement_id=state.settlement_id,
            prosperity_level=state.prosperity_level,
            economic_status=state.get_economic_status().value,
            wealth_per_capita=state.wealth_per_capita,
            trade_volume=state.trade_volume,
            active_trade_routes=len(state.active_trade_routes),
            trade_partners=state.trade_partners,
            prosperity_trend=state.prosperity_trend,
            last_updated=state.last_updated,
            active_events=len(state.active_events)
        )
        
    except Exception as e:
        logger.error(f"Error getting economic state for {settlement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get economic state: {str(e)}")


@router.get("/effects/{settlement_id}")
async def get_population_effects(settlement_id: str):
    """Get economic effects on population for a settlement"""
    try:
        effects = economic_engine.get_population_effects(settlement_id)
        
        return {
            "settlement_id": settlement_id,
            "economic_effects": effects,
            "explanation": {
                "population_growth_modifier": "Multiplier for population growth rate (1.0 = normal)",
                "disease_resistance_modifier": "Multiplier for disease resistance (1.0 = normal)",
                "migration_attractiveness": "Attractiveness for migration (-1.0 to 1.0)",
                "economic_status": "Overall economic condition",
                "prosperity_level": "Prosperity level (-1.0 to 1.0)",
                "trade_route_count": "Number of active trade routes"
            },
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting population effects for {settlement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get population effects: {str(e)}")


@router.post("/resources/{settlement_id}/update")
async def update_resource_availability(
    settlement_id: str,
    resource_update: ResourceUpdate,
    send_notifications: bool = Query(True, description="Send WebSocket notifications")
):
    """Update resource availability for a settlement"""
    try:
        # Update the resource
        economic_engine.update_resource_availability(
            settlement_id,
            resource_update.resource_type,
            resource_update.scarcity_change,
            resource_update.quality_change
        )
        
        # Get updated state
        state = economic_engine.get_economic_state(settlement_id)
        resource = state.resources.get(resource_update.resource_type)
        
        # Send WebSocket notification if enabled
        if send_notifications and WEBSOCKET_INTEGRATION_AVAILABLE and event_integrator:
            await event_integrator.notify_economic_change(
                settlement_id,
                "resource_update",
                {
                    "resource_type": resource_update.resource_type.value,
                    "new_scarcity": resource.scarcity_level if resource else None,
                    "abundance_category": resource.get_abundance_category() if resource else None
                }
            )
        
        return {
            "success": True,
            "settlement_id": settlement_id,
            "resource_type": resource_update.resource_type.value,
            "updated_resource": {
                "scarcity_level": resource.scarcity_level if resource else None,
                "abundance_category": resource.get_abundance_category() if resource else None,
                "quality_modifier": resource.quality_modifier if resource else None,
                "price_modifier": resource.current_price_modifier if resource else None
            },
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating resource {resource_update.resource_type.value} for {settlement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update resource: {str(e)}")


@router.get("/resources/{settlement_id}")
async def get_resource_availability(settlement_id: str):
    """Get all resource availability for a settlement"""
    try:
        state = economic_engine.get_economic_state(settlement_id)
        
        resources_data = {}
        for resource_type, resource in state.resources.items():
            resources_data[resource_type.value] = {
                "scarcity_level": resource.scarcity_level,
                "abundance_category": resource.get_abundance_category(),
                "quality_modifier": resource.quality_modifier,
                "price_modifier": resource.current_price_modifier,
                "population_effects": {
                    "growth_modifier": resource.population_growth_modifier,
                    "disease_resistance_modifier": resource.disease_resistance_modifier,
                    "migration_attractiveness_modifier": resource.migration_attractiveness_modifier
                }
            }
        
        return {
            "settlement_id": settlement_id,
            "resources": resources_data,
            "total_resources": len(resources_data),
            "critical_shortages": [
                resource_type for resource_type, data in resources_data.items()
                if data["abundance_category"] == "critical_shortage"
            ],
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting resources for {settlement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get resources: {str(e)}")


@router.post("/trade-routes", response_model=TradeRouteResponse)
async def create_trade_route(
    trade_route: TradeRouteCreate,
    send_notifications: bool = Query(True, description="Send WebSocket notifications")
):
    """Create a new trade route between settlements"""
    try:
        # Create the trade route
        route_id = economic_engine.create_trade_route(
            trade_route.origin_settlement,
            trade_route.destination_settlement,
            trade_route.primary_goods,
            trade_route.distance,
            trade_route.safety_level
        )
        
        # Get the created route
        route = economic_engine.trade_routes[route_id]
        
        # Send WebSocket notifications if enabled
        if send_notifications and WEBSOCKET_INTEGRATION_AVAILABLE and event_integrator:
            for settlement_id in [trade_route.origin_settlement, trade_route.destination_settlement]:
                await event_integrator.notify_economic_change(
                    settlement_id,
                    "trade_route_created",
                    {
                        "route_id": route_id,
                        "partner_settlement": (
                            trade_route.destination_settlement 
                            if settlement_id == trade_route.origin_settlement 
                            else trade_route.origin_settlement
                        ),
                        "primary_goods": [good.value for good in trade_route.primary_goods]
                    }
                )
        
        return TradeRouteResponse(
            route_id=route.route_id,
            origin_settlement=route.origin_settlement,
            destination_settlement=route.destination_settlement,
            distance=route.distance,
            safety_level=route.safety_level.value,
            primary_goods=[good.value for good in route.primary_goods],
            trade_volume_modifier=route.trade_volume_modifier,
            travel_time_days=route.travel_time_days,
            prosperity_bonus=route.prosperity_bonus,
            migration_influence=route.migration_influence,
            is_active=route.is_active,
            effective_trade_bonus=route.get_effective_trade_bonus(),
            last_updated=route.last_updated
        )
        
    except Exception as e:
        logger.error(f"Error creating trade route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create trade route: {str(e)}")


@router.get("/trade-routes", response_model=List[TradeRouteResponse])
async def list_trade_routes(
    settlement_id: Optional[str] = Query(None, description="Filter by settlement ID"),
    active_only: bool = Query(True, description="Only show active routes")
):
    """List trade routes, optionally filtered by settlement"""
    try:
        routes = []
        
        for route in economic_engine.trade_routes.values():
            # Apply filters
            if active_only and not route.is_active:
                continue
            
            if settlement_id and settlement_id not in [route.origin_settlement, route.destination_settlement]:
                continue
            
            routes.append(TradeRouteResponse(
                route_id=route.route_id,
                origin_settlement=route.origin_settlement,
                destination_settlement=route.destination_settlement,
                distance=route.distance,
                safety_level=route.safety_level.value,
                primary_goods=[good.value for good in route.primary_goods],
                trade_volume_modifier=route.trade_volume_modifier,
                travel_time_days=route.travel_time_days,
                prosperity_bonus=route.prosperity_bonus,
                migration_influence=route.migration_influence,
                is_active=route.is_active,
                effective_trade_bonus=route.get_effective_trade_bonus(),
                last_updated=route.last_updated
            ))
        
        return routes
        
    except Exception as e:
        logger.error(f"Error listing trade routes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list trade routes: {str(e)}")


@router.put("/trade-routes/{route_id}/safety")
async def update_trade_route_safety(
    route_id: str,
    new_safety: TradeRouteStatus,
    send_notifications: bool = Query(True, description="Send WebSocket notifications")
):
    """Update the safety level of a trade route"""
    try:
        if route_id not in economic_engine.trade_routes:
            raise HTTPException(status_code=404, detail=f"Trade route not found: {route_id}")
        
        old_route = economic_engine.trade_routes[route_id]
        old_safety = old_route.safety_level
        
        # Update the safety level
        economic_engine.update_trade_route_safety(route_id, new_safety)
        
        # Send WebSocket notifications if enabled
        if send_notifications and WEBSOCKET_INTEGRATION_AVAILABLE and event_integrator:
            for settlement_id in [old_route.origin_settlement, old_route.destination_settlement]:
                await event_integrator.notify_economic_change(
                    settlement_id,
                    "trade_route_safety_changed",
                    {
                        "route_id": route_id,
                        "old_safety": old_safety.value,
                        "new_safety": new_safety.value,
                        "effective_bonus_change": (
                            economic_engine.trade_routes[route_id].get_effective_trade_bonus() - 
                            old_route.get_effective_trade_bonus()
                        )
                    }
                )
        
        updated_route = economic_engine.trade_routes[route_id]
        
        return {
            "success": True,
            "route_id": route_id,
            "old_safety": old_safety.value,
            "new_safety": new_safety.value,
            "effective_trade_bonus": updated_route.get_effective_trade_bonus(),
            "updated_at": updated_route.last_updated.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trade route safety: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update trade route safety: {str(e)}")


@router.post("/events", response_model=EconomicEventResponse)
async def create_economic_event(
    event: EconomicEventCreate,
    send_notifications: bool = Query(True, description="Send WebSocket notifications")
):
    """Create a new economic event affecting one or more settlements"""
    try:
        # Prepare effects dictionary
        effects = {}
        if event.population_growth_modifier is not None:
            effects['population_growth_modifier'] = event.population_growth_modifier
        if event.migration_pressure_modifier is not None:
            effects['migration_pressure_modifier'] = event.migration_pressure_modifier
        if event.disease_resistance_modifier is not None:
            effects['disease_resistance_modifier'] = event.disease_resistance_modifier
        if event.prosperity_change is not None:
            effects['prosperity_change'] = event.prosperity_change
        if event.resource_effects is not None:
            effects['resource_effects'] = event.resource_effects
        if event.completion_effects is not None:
            effects['completion_effects'] = event.completion_effects
        
        # Create the event
        event_id = economic_engine.create_economic_event(
            event.event_type,
            event.name,
            event.description,
            event.affected_settlements,
            event.duration_days,
            **effects
        )
        
        # Get the created event
        created_event = economic_engine.active_events[event_id]
        
        # Send WebSocket notifications if enabled
        if send_notifications and WEBSOCKET_INTEGRATION_AVAILABLE and event_integrator:
            for settlement_id in event.affected_settlements:
                await event_integrator.notify_economic_change(
                    settlement_id,
                    "economic_event_started",
                    {
                        "event_id": event_id,
                        "event_name": event.name,
                        "event_type": event.event_type,
                        "duration_days": event.duration_days,
                        "effects": effects
                    }
                )
        
        return EconomicEventResponse(
            event_id=created_event.event_id,
            event_type=created_event.event_type,
            name=created_event.name,
            description=created_event.description,
            start_date=created_event.start_date,
            duration_days=created_event.duration_days,
            affected_settlements=created_event.affected_settlements,
            is_active=created_event.is_active,
            population_effects={
                "population_growth_modifier": created_event.population_growth_modifier,
                "migration_pressure_modifier": created_event.migration_pressure_modifier,
                "disease_resistance_modifier": created_event.disease_resistance_modifier,
                "fertility_modifier": created_event.fertility_modifier,
                "mortality_modifier": created_event.mortality_modifier
            },
            economic_effects={
                "prosperity_change": created_event.prosperity_change,
                "resource_effects": created_event.resource_effects,
                "trade_route_effects": created_event.trade_route_effects
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating economic event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create economic event: {str(e)}")


@router.get("/events", response_model=List[EconomicEventResponse])
async def list_economic_events(
    settlement_id: Optional[str] = Query(None, description="Filter by settlement ID"),
    active_only: bool = Query(True, description="Only show active events")
):
    """List economic events, optionally filtered by settlement"""
    try:
        events = []
        
        for event in economic_engine.active_events.values():
            # Apply filters
            if active_only and not event.is_active:
                continue
            
            if settlement_id and settlement_id not in event.affected_settlements:
                continue
            
            events.append(EconomicEventResponse(
                event_id=event.event_id,
                event_type=event.event_type,
                name=event.name,
                description=event.description,
                start_date=event.start_date,
                duration_days=event.duration_days,
                affected_settlements=event.affected_settlements,
                is_active=event.is_active,
                population_effects={
                    "population_growth_modifier": event.population_growth_modifier,
                    "migration_pressure_modifier": event.migration_pressure_modifier,
                    "disease_resistance_modifier": event.disease_resistance_modifier,
                    "fertility_modifier": event.fertility_modifier,
                    "mortality_modifier": event.mortality_modifier
                },
                economic_effects={
                    "prosperity_change": event.prosperity_change,
                    "resource_effects": event.resource_effects,
                    "trade_route_effects": event.trade_route_effects
                }
            ))
        
        return events
        
    except Exception as e:
        logger.error(f"Error listing economic events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list economic events: {str(e)}")


@router.post("/simulate-day/{settlement_id}")
async def simulate_economic_day(
    settlement_id: str,
    send_notifications: bool = Query(True, description="Send WebSocket notifications")
):
    """Simulate one day of economic progression for a settlement"""
    try:
        # Progress one economic day
        day_result = economic_engine.progress_economic_day(settlement_id)
        
        # Get updated population effects
        population_effects = economic_engine.get_population_effects(settlement_id)
        
        # Send WebSocket notification if enabled and there were significant changes
        if (send_notifications and WEBSOCKET_INTEGRATION_AVAILABLE and event_integrator and 
            abs(day_result["prosperity_change"]) > 0.001):  # Only notify for meaningful changes
            
            await event_integrator.notify_economic_change(
                settlement_id,
                "daily_economic_update",
                {
                    "prosperity_change": day_result["prosperity_change"],
                    "new_prosperity_level": day_result["prosperity_level"],
                    "economic_status": day_result["economic_status"],
                    "population_effects": population_effects
                }
            )
        
        return {
            "simulation_result": day_result,
            "population_effects": population_effects,
            "simulated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error simulating economic day for {settlement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate economic day: {str(e)}")


@router.get("/overview")
async def economic_system_overview():
    """Get an overview of the entire economic system"""
    try:
        total_settlements = len(economic_engine.economic_states)
        total_routes = len(economic_engine.trade_routes)
        active_routes = len([r for r in economic_engine.trade_routes.values() if r.is_active])
        total_events = len(economic_engine.active_events)
        active_events = len([e for e in economic_engine.active_events.values() if e.is_active])
        
        # Economic status distribution
        status_distribution = {}
        prosperity_levels = []
        
        for state in economic_engine.economic_states.values():
            status = state.get_economic_status().value
            status_distribution[status] = status_distribution.get(status, 0) + 1
            prosperity_levels.append(state.prosperity_level)
        
        avg_prosperity = sum(prosperity_levels) / len(prosperity_levels) if prosperity_levels else 0.0
        
        return {
            "system_overview": {
                "total_settlements": total_settlements,
                "average_prosperity": round(avg_prosperity, 3),
                "economic_status_distribution": status_distribution
            },
            "trade_network": {
                "total_routes": total_routes,
                "active_routes": active_routes,
                "route_utilization": round(active_routes / total_routes * 100, 1) if total_routes > 0 else 0.0
            },
            "economic_events": {
                "total_events": total_events,
                "active_events": active_events
            },
            "system_capabilities": {
                "websocket_integration": WEBSOCKET_INTEGRATION_AVAILABLE,
                "real_time_notifications": WEBSOCKET_INTEGRATION_AVAILABLE,
                "resource_management": True,
                "trade_route_management": True,
                "economic_event_system": True,
                "population_integration": True
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting economic system overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system overview: {str(e)}")


@router.get("/health")
async def economic_system_health():
    """Health check for the economic system"""
    try:
        return {
            "status": "healthy",
            "system": "population_economic",
            "components": {
                "economic_engine": "operational",
                "websocket_integration": "available" if WEBSOCKET_INTEGRATION_AVAILABLE else "unavailable",
                "trade_routes": f"{len(economic_engine.trade_routes)} active",
                "economic_events": f"{len(economic_engine.active_events)} tracked",
                "settlements": f"{len(economic_engine.economic_states)} monitored"
            },
            "capabilities": [
                "economic_state_management",
                "resource_availability_tracking",
                "trade_route_management",
                "economic_event_processing",
                "population_effect_calculation",
                "real_time_notifications",
                "economic_simulation"
            ],
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Economic system health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Economic system unhealthy: {str(e)}") 