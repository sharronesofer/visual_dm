"""
Economy API Routes - FastAPI endpoints for the economy system.

Provides RESTful API endpoints for all economy functionality including
resources, markets, analytics, and economic operations.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.systems.economy.services.economy_manager import EconomyManager
from backend.systems.economy.services.resource import ResourceData
from backend.systems.economy.models.market import MarketData

# Set up logging
logger = logging.getLogger(__name__)

# Create API router
economy_router = APIRouter(prefix="/api/v1/economy", tags=["economy"])

# Dependency injection for database session
def get_db():
    """Get database session for dependency injection."""
    return None  # For now, EconomyManager handles None gracefully

# Pydantic models for request/response
class EconomyStatusResponse(BaseModel):
    initialized: bool
    services: Dict[str, bool]
    database_connected: bool
    timestamp: str

class ResourceResponse(BaseModel):
    id: str
    name: str
    type: str
    value: float
    quantity: int
    amount: float
    region_id: str

class MarketResponse(BaseModel):
    id: int
    name: str
    region_id: int
    market_type: str

class PriceCalculationResponse(BaseModel):
    price: float
    details: Dict[str, Any]

class EconomicAnalyticsResponse(BaseModel):
    region_id: int
    timestamp: str
    metrics: Dict[str, Any]
    summary: Dict[str, Any]

class EconomicForecastResponse(BaseModel):
    region_id: int
    periods: int
    predictions: List[Dict[str, Any]]
    confidence: float

class TickProcessingResponse(BaseModel):
    trades_processed: int
    markets_updated: int
    tax_revenue: Dict[str, float]
    price_indices: Dict[str, float]
    generated_events: List[Dict[str, Any]]
    futures_processed: int

# Helper function to get EconomyManager instance
def get_economy_manager(db_session: Session = Depends(get_db)) -> EconomyManager:
    """Get EconomyManager singleton instance."""
    try:
        return EconomyManager.get_instance(db_session)
    except Exception as e:
        logger.error(f"Failed to get EconomyManager instance: {e}")
        raise HTTPException(status_code=500, detail="Economy system unavailable")

@economy_router.get("/status", response_model=EconomyStatusResponse)
async def get_economy_status(
    economy: EconomyManager = Depends(get_economy_manager)
) -> EconomyStatusResponse:
    """
    Get overall economy system status and health information.
    
    Returns:
        EconomyStatusResponse: Current system status
    """
    try:
        status = economy.get_economy_status()
        return EconomyStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error getting economy status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get economy status")

# Resource Management Endpoints

@economy_router.get("/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: str,
    economy: EconomyManager = Depends(get_economy_manager)
) -> ResourceResponse:
    """
    Get a specific resource by ID.
    
    Args:
        resource_id: The resource identifier
        
    Returns:
        ResourceResponse: Resource data
    """
    try:
        resource = economy.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return ResourceResponse(
            id=resource.id,
            name=resource.name,
            type=resource.type,
            value=resource.value,
            quantity=resource.quantity,
            amount=resource.amount,
            region_id=resource.region_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get resource")

@economy_router.get("/regions/{region_id}/resources", response_model=List[ResourceResponse])
async def get_region_resources(
    region_id: int,
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    economy: EconomyManager = Depends(get_economy_manager)
) -> List[ResourceResponse]:
    """
    Get all resources in a specific region.
    
    Args:
        region_id: The region identifier
        resource_type: Optional filter by resource type
        
    Returns:
        List[ResourceResponse]: List of resources in the region
    """
    try:
        if resource_type:
            resources = economy.get_available_resources(region_id=region_id, resource_type=resource_type)
        else:
            resources = economy.get_resources_by_region(region_id)
        
        return [
            ResourceResponse(
                id=resource.id,
                name=resource.name,
                type=resource.type,
                value=resource.value,
                quantity=resource.quantity,
                amount=resource.amount,
                region_id=resource.region_id
            )
            for resource in resources
        ]
    except Exception as e:
        logger.error(f"Error getting resources for region {region_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get region resources")

@economy_router.post("/resources", response_model=ResourceResponse)
async def create_resource(
    resource_data: Dict[str, Any] = Body(...),
    economy: EconomyManager = Depends(get_economy_manager)
) -> ResourceResponse:
    """
    Create a new resource.
    
    Args:
        resource_data: Resource creation data
        
    Returns:
        ResourceResponse: Created resource data
    """
    try:
        resource = economy.create_resource(resource_data)
        if not resource:
            raise HTTPException(status_code=400, detail="Failed to create resource")
        
        return ResourceResponse(
            id=resource.id,
            name=resource.name,
            type=resource.type,
            value=resource.value,
            quantity=resource.quantity,
            amount=resource.amount,
            region_id=resource.region_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating resource: {e}")
        raise HTTPException(status_code=500, detail="Failed to create resource")

@economy_router.put("/resources/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    updates: Dict[str, Any] = Body(...),
    economy: EconomyManager = Depends(get_economy_manager)
) -> ResourceResponse:
    """
    Update an existing resource.
    
    Args:
        resource_id: The resource identifier
        updates: Update data
        
    Returns:
        ResourceResponse: Updated resource data
    """
    try:
        resource = economy.update_resource(resource_id, updates)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return ResourceResponse(
            id=resource.id,
            name=resource.name,
            type=resource.type,
            value=resource.value,
            quantity=resource.quantity,
            amount=resource.amount,
            region_id=resource.region_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update resource")

@economy_router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: str,
    economy: EconomyManager = Depends(get_economy_manager)
) -> Dict[str, bool]:
    """
    Delete a resource.
    
    Args:
        resource_id: The resource identifier
        
    Returns:
        Dict[str, bool]: Success status
    """
    try:
        success = economy.delete_resource(resource_id)
        if not success:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete resource")

@economy_router.post("/resources/{resource_id}/adjust")
async def adjust_resource_amount(
    resource_id: str,
    amount_change: float = Body(..., embed=True),
    economy: EconomyManager = Depends(get_economy_manager)
) -> ResourceResponse:
    """
    Adjust the amount of a resource.
    
    Args:
        resource_id: The resource identifier
        amount_change: Amount to add/subtract (can be negative)
        
    Returns:
        ResourceResponse: Updated resource data
    """
    try:
        resource = economy.adjust_resource_amount(resource_id, amount_change)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return ResourceResponse(
            id=resource.id,
            name=resource.name,
            type=resource.type,
            value=resource.value,
            quantity=resource.quantity,
            amount=resource.amount,
            region_id=resource.region_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adjusting resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to adjust resource amount")

@economy_router.post("/transfer")
async def transfer_resource(
    source_region_id: int = Body(...),
    dest_region_id: int = Body(...),
    resource_id: str = Body(...),
    amount: float = Body(...),
    economy: EconomyManager = Depends(get_economy_manager)
) -> Dict[str, Any]:
    """
    Transfer resources between regions.
    
    Args:
        source_region_id: Source region ID
        dest_region_id: Destination region ID
        resource_id: Resource identifier
        amount: Amount to transfer
        
    Returns:
        Dict[str, Any]: Transfer result
    """
    try:
        success, message = economy.transfer_resource(source_region_id, dest_region_id, resource_id, amount)
        
        return {
            "success": success,
            "message": message,
            "source_region": source_region_id,
            "destination_region": dest_region_id,
            "resource_id": resource_id,
            "amount": amount
        }
    except Exception as e:
        logger.error(f"Error transferring resource: {e}")
        raise HTTPException(status_code=500, detail="Failed to transfer resource")

# Market Management Endpoints

@economy_router.get("/markets/{market_id}", response_model=Optional[MarketResponse])
async def get_market(
    market_id: Union[str, int],
    economy: EconomyManager = Depends(get_economy_manager)
) -> Optional[MarketResponse]:
    """
    Get a specific market by ID.
    
    Args:
        market_id: The market identifier
        
    Returns:
        MarketResponse: Market data or None if not found
    """
    try:
        market = economy.get_market(market_id)
        if not market:
            return None
        
        return MarketResponse(
            id=market.id,
            name=market.name,
            region_id=market.region_id,
            market_type=market.market_type
        )
    except Exception as e:
        logger.error(f"Error getting market {market_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market")

@economy_router.get("/regions/{region_id}/markets", response_model=List[MarketResponse])
async def get_region_markets(
    region_id: int,
    economy: EconomyManager = Depends(get_economy_manager)
) -> List[MarketResponse]:
    """
    Get all markets in a specific region.
    
    Args:
        region_id: The region identifier
        
    Returns:
        List[MarketResponse]: List of markets in the region
    """
    try:
        markets = economy.get_markets_by_region(region_id)
        
        return [
            MarketResponse(
                id=market.id,
                name=market.name,
                region_id=market.region_id,
                market_type=market.market_type
            )
            for market in markets
        ]
    except Exception as e:
        logger.error(f"Error getting markets for region {region_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get region markets")

@economy_router.post("/markets/price", response_model=PriceCalculationResponse)
async def calculate_price(
    resource_id: int = Body(...),
    market_id: int = Body(...),
    quantity: float = Body(1.0),
    economy: EconomyManager = Depends(get_economy_manager)
) -> PriceCalculationResponse:
    """
    Calculate the price for a resource in a market.
    
    Args:
        resource_id: Resource identifier
        market_id: Market identifier  
        quantity: Quantity for price calculation
        
    Returns:
        PriceCalculationResponse: Price and calculation details
    """
    try:
        price, details = economy.calculate_price(resource_id, market_id, quantity)
        
        return PriceCalculationResponse(
            price=price,
            details=details
        )
    except Exception as e:
        logger.error(f"Error calculating price: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate price")

@economy_router.post("/markets/{market_id}/conditions")
async def update_market_conditions(
    market_id: int,
    event_modifiers: Optional[Dict[str, Any]] = Body(None),
    economy: EconomyManager = Depends(get_economy_manager)
) -> List[MarketResponse]:
    """
    Update market conditions based on events.
    
    Args:
        market_id: Market identifier (used as region_id)
        event_modifiers: Optional event modifiers to apply
        
    Returns:
        List[MarketResponse]: Updated markets
    """
    try:
        markets = economy.update_market_conditions(market_id, event_modifiers)
        
        return [
            MarketResponse(
                id=market.id,
                name=market.name,
                region_id=market.region_id,
                market_type=market.market_type
            )
            for market in markets
        ]
    except Exception as e:
        logger.error(f"Error updating market conditions: {e}")
        raise HTTPException(status_code=500, detail="Failed to update market conditions")

# Economic Analytics Endpoints

@economy_router.get("/analytics/{region_id}", response_model=EconomicAnalyticsResponse)
async def get_economic_analytics(
    region_id: int,
    economy: EconomyManager = Depends(get_economy_manager)
) -> EconomicAnalyticsResponse:
    """
    Get economic analytics for a region.
    
    Args:
        region_id: The region identifier
        
    Returns:
        EconomicAnalyticsResponse: Economic analytics data
    """
    try:
        analytics = economy.get_economic_analytics(region_id)
        
        return EconomicAnalyticsResponse(**analytics)
    except Exception as e:
        logger.error(f"Error getting economic analytics for region {region_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get economic analytics")

@economy_router.get("/forecast/{region_id}", response_model=EconomicForecastResponse)
async def get_economic_forecast(
    region_id: int,
    periods: int = Query(3, description="Number of periods to forecast"),
    economy: EconomyManager = Depends(get_economy_manager)
) -> EconomicForecastResponse:
    """
    Generate economic forecast for a region.
    
    Args:
        region_id: The region identifier
        periods: Number of periods to forecast
        
    Returns:
        EconomicForecastResponse: Economic forecast data
    """
    try:
        forecast = economy.generate_economic_forecast(region_id, periods)
        
        return EconomicForecastResponse(**forecast)
    except Exception as e:
        logger.error(f"Error generating economic forecast for region {region_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate economic forecast")

@economy_router.get("/resources/{resource_id}/trends")
async def get_resource_price_trends(
    resource_id: int,
    region_id: Optional[int] = Query(None, description="Filter by region"),
    economy: EconomyManager = Depends(get_economy_manager)
) -> Dict[str, Any]:
    """
    Get price trends for a specific resource.
    
    Args:
        resource_id: Resource identifier
        region_id: Optional region filter
        
    Returns:
        Dict[str, Any]: Price trend data
    """
    try:
        trends = economy.market_service.get_resource_price_trends(resource_id, region_id)
        return trends
    except Exception as e:
        logger.error(f"Error getting price trends for resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get price trends")

# System Operations Endpoints

@economy_router.post("/tick/{region_id}", response_model=TickProcessingResponse)
async def process_economic_tick(
    region_id: int,
    economy: EconomyManager = Depends(get_economy_manager)
) -> TickProcessingResponse:
    """
    Process economic tick for a region.
    
    Args:
        region_id: The region identifier
        
    Returns:
        TickProcessingResponse: Tick processing results
    """
    try:
        results = economy.process_tick(region_id)
        
        return TickProcessingResponse(**results)
    except Exception as e:
        logger.error(f"Error processing economic tick for region {region_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process economic tick")

@economy_router.post("/population-impact/{region_id}")
async def calculate_population_impact(
    region_id: int,
    previous_population: int = Body(...),
    current_population: int = Body(...),
    economy: EconomyManager = Depends(get_economy_manager)
) -> Dict[str, Any]:
    """
    Calculate the impact of population changes on resources.
    
    Args:
        region_id: The region identifier
        previous_population: Previous population count
        current_population: Current population count
        
    Returns:
        Dict[str, Any]: Population impact analysis
    """
    try:
        impact = economy.resource_service.population_impact_on_resources(
            region_id, previous_population, current_population
        )
        return impact
    except Exception as e:
        logger.error(f"Error calculating population impact for region {region_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate population impact")

# Health Check Endpoint

@economy_router.get("/health")
async def health_check(
    economy: EconomyManager = Depends(get_economy_manager)
) -> Dict[str, str]:
    """
    Health check endpoint for monitoring.
    
    Returns:
        Dict[str, str]: Health status
    """
    try:
        status = economy.get_economy_status()
        if status.get('initialized'):
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
        else:
            return {"status": "degraded", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "timestamp": datetime.utcnow().isoformat()} 