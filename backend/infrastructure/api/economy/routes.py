"""
Economy API Routes - Complete FastAPI router implementation for economy system.

This module provides comprehensive REST API endpoints for economy operations
including resources, markets, trade routes, futures, and economic analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Dict, Any, List, Optional, Union
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.systems.economy.services.economy_manager import EconomyManager
# from backend.infrastructure.database.economy import get_db_session  # Not implemented yet
from backend.systems.economy.services.resource import ResourceData
from backend.systems.economy.models.market import MarketData
from backend.systems.economy.models.trade_route import TradeRouteData
from backend.systems.economy.models.commodity_future import CommodityFutureData

# Simple dependency for now
def get_db_session():
    """Simple database session dependency - to be implemented"""
    return None

# Create router
economy_router = APIRouter(prefix="/economy", tags=["economy"])

# Request/Response Models
class EconomyStatusResponse(BaseModel):
    """Economy system status response."""
    status: str
    total_resources: int
    total_markets: int
    total_trade_routes: int
    total_futures: int
    economic_health: Dict[str, Any]
    last_tick: Optional[str]

class ProcessTickRequest(BaseModel):
    """Request model for processing economic ticks."""
    tick_count: int = Field(default=1, ge=1, le=100)

class ProcessTickResponse(BaseModel):
    """Response model for tick processing."""
    ticks_processed: int
    resources_processed: int
    markets_updated: int
    trade_routes_processed: int
    futures_settled: int
    events_generated: List[Dict[str, Any]]

class EconomicMetricsResponse(BaseModel):
    """Economic metrics response."""
    region_id: Optional[int]
    price_index: Dict[str, Any]
    trade_volume: float
    market_activity: Dict[str, Any]
    resource_availability: Dict[str, Any]
    economic_trends: Dict[str, Any]

class ResourceCreateRequest(BaseModel):
    """Request model for creating resources."""
    region_id: int
    resource_type: str
    amount: float = Field(ge=0)
    quality: str = Field(default="standard")
    availability: str = Field(default="available")

class ResourceUpdateRequest(BaseModel):
    """Request model for updating resources."""
    amount: Optional[float] = Field(None, ge=0)
    quality: Optional[str] = None
    availability: Optional[str] = None

class ResourceTransferRequest(BaseModel):
    """Request model for transferring resources."""
    source_region_id: int
    dest_region_id: int
    amount: float = Field(gt=0)

class MarketCreateRequest(BaseModel):
    """Request model for creating markets."""
    region_id: int
    market_type: str
    name: str
    description: Optional[str] = None

class MarketUpdateRequest(BaseModel):
    """Request model for updating markets."""
    name: Optional[str] = None
    description: Optional[str] = None
    market_type: Optional[str] = None
    is_active: Optional[bool] = None

class TradeRouteCreateRequest(BaseModel):
    """Request model for creating trade routes."""
    origin_region_id: int
    destination_region_id: int
    resource_ids: List[int]
    route_type: str = Field(default="standard")
    frequency: int = Field(default=7, ge=1)

class TradeRouteUpdateRequest(BaseModel):
    """Request model for updating trade routes."""
    resource_ids: Optional[List[int]] = None
    route_type: Optional[str] = None
    frequency: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None

class FutureCreateRequest(BaseModel):
    """Request model for creating futures contracts."""
    resource_id: int
    market_id: int
    quantity: float = Field(gt=0)
    strike_price: float = Field(gt=0)
    expiration_days: int = Field(ge=1, le=365)
    contract_type: str = Field(default="buy")

class FutureUpdateRequest(BaseModel):
    """Request model for updating futures contracts."""
    strike_price: Optional[float] = Field(None, gt=0)
    expiration_date: Optional[str] = None
    status: Optional[str] = None

# Dependency injection
def get_economy_manager(db_session: Session = Depends(get_db_session)) -> EconomyManager:
    """Get economy manager instance with database session."""
    return EconomyManager.get_instance(db_session)

# Core Economy Operations
@economy_router.get("/status", response_model=EconomyStatusResponse)
async def get_economy_status(economy_manager: EconomyManager = Depends(get_economy_manager)):
    """Get overall economic system status."""
    try:
        status_data = economy_manager.get_economy_status()
        return EconomyStatusResponse(**status_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get economy status: {str(e)}")

@economy_router.post("/process-tick", response_model=ProcessTickResponse)
async def process_economic_tick(
    request: ProcessTickRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Process economic simulation tick."""
    try:
        result = economy_manager.process_tick(request.tick_count)
        return ProcessTickResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process tick: {str(e)}")

@economy_router.get("/metrics", response_model=EconomicMetricsResponse)
async def get_economic_metrics(
    region_id: Optional[int] = Query(None, description="Filter by region"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get economic metrics and analytics."""
    try:
        analytics = economy_manager.get_economic_analytics(region_id)
        price_index = economy_manager.calculate_price_index(region_id)
        
        return EconomicMetricsResponse(
            region_id=region_id,
            price_index=price_index,
            trade_volume=analytics.get("trade_volume", 0.0),
            market_activity=analytics.get("market_activity", {}),
            resource_availability=analytics.get("resource_availability", {}),
            economic_trends=analytics.get("trends", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@economy_router.get("/forecast")
async def get_economic_forecast(
    region_id: Optional[int] = Query(None, description="Filter by region"),
    periods: int = Query(5, ge=1, le=20, description="Number of periods to forecast"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get economic forecasting data."""
    try:
        forecast = economy_manager.generate_economic_forecast(region_id, periods)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast: {str(e)}")

@economy_router.post("/initialize")
async def initialize_economy(
    config: Optional[Dict[str, Any]] = None,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Initialize economic system with optional configuration."""
    try:
        result = economy_manager.initialize_economy(config)
        return {"message": "Economy initialized successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize economy: {str(e)}")

# Resource Management Endpoints
@economy_router.get("/resources")
async def get_resources(
    region_id: Optional[int] = Query(None, description="Filter by region"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get resources, optionally filtered by region and type."""
    try:
        if region_id:
            resources = economy_manager.get_resources_by_region(region_id)
        else:
            resources = economy_manager.get_available_resources(region_id, resource_type)
        
        return {"resources": [r.to_dict() if hasattr(r, 'to_dict') else r for r in resources]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resources: {str(e)}")

@economy_router.get("/resources/{resource_id}")
async def get_resource(
    resource_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get specific resource by ID."""
    try:
        resource = economy_manager.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return {"resource": resource.to_dict() if hasattr(resource, 'to_dict') else resource}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resource: {str(e)}")

@economy_router.post("/resources")
async def create_resource(
    request: ResourceCreateRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Create a new resource."""
    try:
        resource_data = ResourceData(
            region_id=request.region_id,
            resource_type=request.resource_type,
            amount=request.amount,
            quality=request.quality,
            availability=request.availability
        )
        
        resource = economy_manager.create_resource(resource_data)
        if not resource:
            raise HTTPException(status_code=400, detail="Failed to create resource")
        
        return {"message": "Resource created successfully", "resource": resource.to_dict() if hasattr(resource, 'to_dict') else resource}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create resource: {str(e)}")

@economy_router.put("/resources/{resource_id}")
async def update_resource(
    resource_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager),
    request: ResourceUpdateRequest = None
):
    """Update an existing resource."""
    try:
        updates = {}
        if request:
            if request.amount is not None:
                updates['amount'] = request.amount
            if request.quality is not None:
                updates['quality'] = request.quality
            if request.availability is not None:
                updates['availability'] = request.availability
        
        resource = economy_manager.update_resource(resource_id, updates)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return {"message": "Resource updated successfully", "resource": resource.to_dict() if hasattr(resource, 'to_dict') else resource}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update resource: {str(e)}")

@economy_router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Delete a resource."""
    try:
        success = economy_manager.delete_resource(resource_id)
        if not success:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return {"message": "Resource deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete resource: {str(e)}")

@economy_router.put("/resources/{resource_id}/adjust")
async def adjust_resource_amount(
    resource_id: int,
    amount_change: float = Query(..., description="Amount to add/subtract"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Adjust the amount of a resource."""
    try:
        resource = economy_manager.adjust_resource_amount(resource_id, amount_change)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return {"message": "Resource amount adjusted", "resource": resource.to_dict() if hasattr(resource, 'to_dict') else resource}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to adjust resource: {str(e)}")

@economy_router.post("/resources/{resource_id}/transfer")
async def transfer_resource(
    resource_id: int,
    request: ResourceTransferRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Transfer resources between regions."""
    try:
        success, message = economy_manager.transfer_resource(
            request.source_region_id,
            request.dest_region_id,
            resource_id,
            request.amount
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"message": "Resource transferred successfully", "details": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transfer resource: {str(e)}")

# Market Endpoints
@economy_router.get("/markets")
async def get_markets(
    region_id: Optional[int] = Query(None, description="Filter by region"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get markets, optionally filtered by region."""
    try:
        if region_id:
            markets = economy_manager.get_markets_by_region(region_id)
        else:
            # Get all markets - this might need to be implemented in the manager
            markets = []
            for region in range(1, 11):  # Assuming regions 1-10 for now
                markets.extend(economy_manager.get_markets_by_region(region))
        
        return {"markets": [m.to_dict() if hasattr(m, 'to_dict') else m for m in markets]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get markets: {str(e)}")

@economy_router.get("/markets/{market_id}")
async def get_market(
    market_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get specific market by ID."""
    try:
        market = economy_manager.get_market(market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")
        
        return {"market": market.to_dict() if hasattr(market, 'to_dict') else market}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market: {str(e)}")

@economy_router.post("/markets")
async def create_market(
    request: MarketCreateRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Create a new market."""
    try:
        market_data = MarketData(
            region_id=request.region_id,
            market_type=request.market_type,
            name=request.name,
            description=request.description or ""
        )
        
        market = economy_manager.create_market(market_data)
        if not market:
            raise HTTPException(status_code=400, detail="Failed to create market")
        
        return {"message": "Market created successfully", "market": market.to_dict() if hasattr(market, 'to_dict') else market}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create market: {str(e)}")

@economy_router.put("/markets/{market_id}")
async def update_market(
    market_id: int,
    request: MarketUpdateRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Update an existing market."""
    try:
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.description is not None:
            updates['description'] = request.description
        if request.market_type is not None:
            updates['market_type'] = request.market_type
        if request.is_active is not None:
            updates['is_active'] = request.is_active
        
        market = economy_manager.update_market(market_id, updates)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")
        
        return {"message": "Market updated successfully", "market": market.to_dict() if hasattr(market, 'to_dict') else market}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update market: {str(e)}")

@economy_router.delete("/markets/{market_id}")
async def delete_market(
    market_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Delete a market."""
    try:
        success = economy_manager.delete_market(market_id)
        if not success:
            raise HTTPException(status_code=404, detail="Market not found")
        
        return {"message": "Market deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete market: {str(e)}")

@economy_router.get("/markets/{market_id}/prices")
async def get_market_prices(
    market_id: int,
    resource_id: Optional[int] = Query(None, description="Filter by resource"),
    quantity: float = Query(1.0, ge=0.1, description="Quantity for price calculation"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get market prices for resources."""
    try:
        if resource_id:
            price, details = economy_manager.calculate_price(resource_id, market_id, quantity)
            return {"resource_id": resource_id, "price": price, "details": details}
        else:
            # Get prices for all resources in market - this might need enhancement
            return {"message": "Bulk price query not implemented yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prices: {str(e)}")

@economy_router.get("/markets/{market_id}/trends")
async def get_market_trends(
    market_id: int,
    resource_id: Optional[int] = Query(None, description="Filter by resource"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get market trends and historical data."""
    try:
        if resource_id:
            trends = economy_manager.get_resource_price_trends(resource_id)
            return {"resource_id": resource_id, "trends": trends}
        else:
            # Get trends for all resources in market
            return {"message": "Bulk trend query not implemented yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")

# Trade Route Endpoints
@economy_router.get("/trade-routes")
async def get_trade_routes(
    region_id: Optional[int] = Query(None, description="Filter by region"),
    as_origin: bool = Query(True, description="Include routes with region as origin"),
    as_destination: bool = Query(True, description="Include routes with region as destination"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get trade routes, optionally filtered by region."""
    try:
        if region_id:
            routes = economy_manager.get_trade_routes_by_region(region_id, as_origin, as_destination)
        else:
            # Get all trade routes - this might need implementation in manager
            routes = []
            for region in range(1, 11):  # Assuming regions 1-10 for now
                routes.extend(economy_manager.get_trade_routes_by_region(region, True, True))
        
        return {"trade_routes": [r.to_dict() if hasattr(r, 'to_dict') else r for r in routes]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trade routes: {str(e)}")

@economy_router.get("/trade-routes/{route_id}")
async def get_trade_route(
    route_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get specific trade route by ID."""
    try:
        route = economy_manager.get_trade_route(route_id)
        if not route:
            raise HTTPException(status_code=404, detail="Trade route not found")
        
        return {"trade_route": route.to_dict() if hasattr(route, 'to_dict') else route}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trade route: {str(e)}")

@economy_router.post("/trade-routes")
async def create_trade_route(
    request: TradeRouteCreateRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Create a new trade route."""
    try:
        route_data = TradeRouteData(
            origin_region_id=request.origin_region_id,
            destination_region_id=request.destination_region_id,
            resource_ids=request.resource_ids,
            route_type=request.route_type,
            frequency=request.frequency
        )
        
        route = economy_manager.create_trade_route(route_data)
        if not route:
            raise HTTPException(status_code=400, detail="Failed to create trade route")
        
        return {"message": "Trade route created successfully", "trade_route": route.to_dict() if hasattr(route, 'to_dict') else route}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create trade route: {str(e)}")

@economy_router.put("/trade-routes/{route_id}")
async def update_trade_route(
    route_id: int,
    request: TradeRouteUpdateRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Update an existing trade route."""
    try:
        updates = {}
        if request.resource_ids is not None:
            updates['resource_ids'] = request.resource_ids
        if request.route_type is not None:
            updates['route_type'] = request.route_type
        if request.frequency is not None:
            updates['frequency'] = request.frequency
        if request.is_active is not None:
            updates['is_active'] = request.is_active
        
        route = economy_manager.update_trade_route(route_id, updates)
        if not route:
            raise HTTPException(status_code=404, detail="Trade route not found")
        
        return {"message": "Trade route updated successfully", "trade_route": route.to_dict() if hasattr(route, 'to_dict') else route}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update trade route: {str(e)}")

@economy_router.delete("/trade-routes/{route_id}")
async def delete_trade_route(
    route_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Delete a trade route."""
    try:
        success = economy_manager.delete_trade_route(route_id)
        if not success:
            raise HTTPException(status_code=404, detail="Trade route not found")
        
        return {"message": "Trade route deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete trade route: {str(e)}")

@economy_router.post("/trade-routes/process")
async def process_trade_routes(
    tick_count: int = Query(1, ge=1, le=100, description="Number of ticks to process"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Process all trade routes for resource transfers."""
    try:
        routes_processed, events = economy_manager.process_trade_routes(tick_count)
        return {
            "message": "Trade routes processed successfully",
            "routes_processed": routes_processed,
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process trade routes: {str(e)}")

# Futures Endpoints
@economy_router.get("/futures")
async def get_futures(
    resource_id: Optional[int] = Query(None, description="Filter by resource"),
    market_id: Optional[int] = Query(None, description="Filter by market"),
    open_only: bool = Query(False, description="Only return open contracts"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get futures contracts, optionally filtered."""
    try:
        if open_only:
            futures = economy_manager.get_open_futures(market_id)
        elif resource_id:
            futures = economy_manager.get_futures_by_resource(resource_id)
        elif market_id:
            futures = economy_manager.get_futures_by_market(market_id)
        else:
            futures = economy_manager.get_open_futures()
        
        return {"futures": [f.to_dict() if hasattr(f, 'to_dict') else f for f in futures]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get futures: {str(e)}")

@economy_router.get("/futures/{future_id}")
async def get_future(
    future_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get specific futures contract by ID."""
    try:
        future = economy_manager.get_future(future_id)
        if not future:
            raise HTTPException(status_code=404, detail="Future contract not found")
        
        return {"future": future.to_dict() if hasattr(future, 'to_dict') else future}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get future: {str(e)}")

@economy_router.post("/futures")
async def create_future(
    request: FutureCreateRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Create a new futures contract."""
    try:
        future_data = CommodityFutureData(
            resource_id=request.resource_id,
            market_id=request.market_id,
            quantity=request.quantity,
            strike_price=request.strike_price,
            expiration_days=request.expiration_days,
            contract_type=request.contract_type
        )
        
        future = economy_manager.create_future(future_data)
        if not future:
            raise HTTPException(status_code=400, detail="Failed to create future contract")
        
        return {"message": "Future contract created successfully", "future": future.to_dict() if hasattr(future, 'to_dict') else future}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create future: {str(e)}")

@economy_router.put("/futures/{future_id}")
async def update_future(
    future_id: int,
    request: FutureUpdateRequest,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Update an existing futures contract."""
    try:
        updates = {}
        if request.strike_price is not None:
            updates['strike_price'] = request.strike_price
        if request.expiration_date is not None:
            updates['expiration_date'] = request.expiration_date
        if request.status is not None:
            updates['status'] = request.status
        
        future = economy_manager.update_future(future_id, updates)
        if not future:
            raise HTTPException(status_code=404, detail="Future contract not found")
        
        return {"message": "Future contract updated successfully", "future": future.to_dict() if hasattr(future, 'to_dict') else future}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update future: {str(e)}")

@economy_router.post("/futures/{future_id}/settle")
async def settle_future(
    future_id: int,
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Settle a futures contract."""
    try:
        result = economy_manager.settle_future(future_id)
        return {"message": "Future contract settled", "settlement": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to settle future: {str(e)}")

@economy_router.get("/futures/prices")
async def get_futures_prices(
    resource_id: Optional[int] = Query(None, description="Filter by resource"),
    market_id: Optional[int] = Query(None, description="Filter by market"),
    periods: int = Query(3, ge=1, le=20, description="Number of periods to forecast"),
    economy_manager: EconomyManager = Depends(get_economy_manager)
):
    """Get futures price forecasts."""
    try:
        if resource_id:
            forecast = economy_manager.forecast_future_prices(resource_id, market_id, periods)
            return {"resource_id": resource_id, "market_id": market_id, "forecast": forecast}
        else:
            return {"message": "Resource ID required for price forecasting"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get futures prices: {str(e)}")

# Export router
__all__ = ['economy_router']

# Include shop routes in the main economy router
from .shop_routes import shop_bp
economy_router.include_router(shop_bp, prefix="", tags=["economy"]) 