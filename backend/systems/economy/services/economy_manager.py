"""
Economy Manager - Main API for the economy system.

This module provides a centralized manager for all economy-related
functionality including resources, trade routes, and markets.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from sqlalchemy.orm import Session
import random
import math

# Database session import
from backend.infrastructure.database.session import SessionLocal

import logging
logger = logging.getLogger(__name__)
from backend.systems.economy.services.resource import (
    Resource, ResourceData
)
from backend.systems.economy.models.trade_route import (
    TradeRouteData
)
from backend.infrastructure.database.economy.trade_route_models import TradeRoute
from backend.systems.economy.models.market import (
    MarketData
)
from backend.infrastructure.database.economy.market_models import Market
from backend.systems.economy.models.commodity_future import (
    CommodityFutureData
)
from backend.infrastructure.database.economy.commodity_future_models import CommodityFuture
from backend.systems.economy.services.resource_service import ResourceService
from backend.systems.economy.services.trade_service import TradeService
from backend.systems.economy.services.market_service import MarketService
from backend.systems.economy.services.futures_service import FuturesService
from backend.systems.economy.services.tournament_economy_service import TournamentEconomyService
from backend.systems.economy.services.central_bank_service import CentralBankService
from backend.infrastructure.config_loaders.economy_config_loader import get_economy_config
from backend.systems.economy.events.events import (
    EconomyEventBus, EconomyEvent, EconomyEventType,
    ResourceEvent, MarketEvent, PriceEvent, TradeEvent, TransactionEvent,
    publish_resource_event, publish_market_event, publish_price_event,
    publish_trade_event, publish_transaction_event, publish_system_event,
    get_event_bus
)
from backend.systems.economy.services.guild_ai_service import GuildAIService

class EconomyManager:
    """
    Manager for the economy system providing a unified API for economy operations.
    
    This class integrates resources, trade routes, and markets into a cohesive
    economy system. It is designed to be used as a singleton with a single instance
    managing all economy-related operations.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls, db_session: Session = None) -> 'EconomyManager':
        """Get the singleton instance of the economy manager.
        
        Args:
            db_session: SQLAlchemy session for database operations
            
        Returns:
            Singleton instance of EconomyManager
        """
        if not cls._instance:
            cls._instance = cls(db_session)
        return cls._instance
    
    def __init__(self, db_session: Session = None):
        """
        Initialize the economy manager.
        
        Args:
            db_session: Database session for persistence
        """
        self.db_session = db_session or SessionLocal()
        self.resource_service = ResourceService(self.db_session)
        self.trade_service = TradeService(self.db_session)
        self.market_service = MarketService(self.db_session)
        self.futures_service = FuturesService(self.db_session)
        self.tournament_service = TournamentEconomyService(self.db_session)
        self.central_bank_service = CentralBankService(self.db_session)
        self.guild_ai_service = GuildAIService(self.db_session)
        self.event_bus = get_event_bus()
        self._initialized = False
        
        # Load configuration
        self.config = get_economy_config()
        
        logger.info("Economy Manager initialized")
    
    # Resource Management API
    
    def get_resource(self, resource_id: Union[str, int]) -> Optional[Resource]:
        """Get a resource by ID."""
        return self.resource_service.get_resource(resource_id)
    
    def get_resources_by_region(self, region_id: int) -> List[Resource]:
        """Get all resources in a region."""
        return self.resource_service.get_resources_by_region(region_id)
    
    def create_resource(self, resource_data: Union[Dict[str, Any], ResourceData]) -> Optional[Resource]:
        """Create a new resource."""
        resource = self.resource_service.create_resource(resource_data)
        
        # Publish resource creation event
        if resource:
            try:
                publish_resource_event(
                    event_type=EconomyEventType.RESOURCE_CREATED,
                    resource_id=str(resource.id),
                    region_id=resource.region_id,
                    resource_type=resource.resource_type,
                    amount=resource.amount,
                    base_value=resource.base_value,
                    rarity=resource.rarity,
                    is_tradeable=resource.is_tradeable
                )
            except Exception as e:
                logger.warning(f"Failed to publish resource creation event: {e}")
        
        return resource
    
    def update_resource(self, resource_id: int, updates: Dict[str, Any]) -> Optional[Resource]:
        """Update an existing resource."""
        # Get the old resource for comparison
        old_resource = self.resource_service.get_resource(resource_id)
        
        # Update the resource
        updated_resource = self.resource_service.update_resource(resource_id, updates)
        
        # Publish resource update event
        if updated_resource:
            try:
                event_data = {
                    "resource_type": updated_resource.resource_type,
                    "amount": updated_resource.amount,
                    "updates": updates
                }
                
                # Add old values for comparison if available
                if old_resource:
                    event_data["old_amount"] = old_resource.amount
                    event_data["amount_change"] = updated_resource.amount - old_resource.amount
                
                publish_resource_event(
                    event_type=EconomyEventType.RESOURCE_UPDATED,
                    resource_id=str(resource_id),
                    region_id=updated_resource.region_id,
                    **event_data
                )
            except Exception as e:
                logger.warning(f"Failed to publish resource update event: {e}")
        
        return updated_resource
    
    def delete_resource(self, resource_id: int) -> bool:
        """Delete a resource."""
        return self.resource_service.delete_resource(resource_id)
    
    def adjust_resource_amount(self, resource_id: int, amount_change: float) -> Optional[Resource]:
        """Adjust the amount of a resource."""
        return self.resource_service.adjust_resource_amount(resource_id, amount_change)
    
    def get_available_resources(self, region_id: Optional[int] = None,
                              resource_type: Optional[str] = None) -> List[Resource]:
        """Get available resources, optionally filtered."""
        return self.resource_service.get_available_resources(region_id, resource_type)
    
    def transfer_resource(self, source_region_id: int, dest_region_id: int,
                         resource_id: int, amount: float) -> Tuple[bool, str]:
        """Transfer resources between regions."""
        result = self.resource_service.transfer_resource(source_region_id, dest_region_id, resource_id, amount)
        
        # Publish resource transfer event
        if result[0]:  # If transfer was successful
            try:
                # Get resource info for better event data
                resource = self.resource_service.get_resource(resource_id)
                
                publish_resource_event(
                    event_type=EconomyEventType.RESOURCE_TRANSFERRED,
                    resource_id=str(resource_id),
                    region_id=source_region_id,  # Source region as primary
                    resource_type=resource.resource_type if resource else "unknown",
                    amount=amount,
                    from_region_id=source_region_id,
                    to_region_id=dest_region_id,
                    transfer_successful=True
                )
            except Exception as e:
                logger.warning(f"Failed to publish resource transfer event: {e}")
        
        return result
    
    # Trade Route API
    
    def get_trade_route(self, route_id: Union[str, int]) -> Optional[TradeRoute]:
        """Get a trade route by ID."""
        return self.trade_service.get_trade_route(route_id)
    
    def get_trade_routes_by_region(self, region_id: int, as_origin: bool = True,
                                 as_destination: bool = True) -> List[TradeRoute]:
        """Get all trade routes for a region."""
        return self.trade_service.get_trade_routes_by_region(region_id, as_origin, as_destination)
    
    def create_trade_route(self, route_data: Union[Dict[str, Any], TradeRouteData]) -> Optional[TradeRoute]:
        """Create a new trade route."""
        route = self.trade_service.create_trade_route(route_data)
        
        # Publish trade route creation event
        if route:
            try:
                publish_trade_event(
                    event_type=EconomyEventType.TRADE_ROUTE_CREATED,
                    trade_route_id=route.id,
                    origin_region_id=route.origin_region_id,
                    destination_region_id=route.destination_region_id,
                    route_name=route.name,
                    is_active=route.is_active,
                    frequency_ticks=route.frequency_ticks,
                    efficiency=route.efficiency,
                    danger_level=route.danger_level
                )
            except Exception as e:
                logger.warning(f"Failed to publish trade route creation event: {e}")
        
        return route
    
    def update_trade_route(self, route_id: int, updates: Dict[str, Any]) -> Optional[TradeRoute]:
        """Update an existing trade route."""
        return self.trade_service.update_trade_route(route_id, updates)
    
    def delete_trade_route(self, route_id: int) -> bool:
        """Delete a trade route."""
        return self.trade_service.delete_trade_route(route_id)
    
    def process_trade_routes(self, tick_count: int = 1) -> Tuple[int, List[Dict[str, Any]]]:
        """Process all active trade routes for resource transfers."""
        success_count, trade_events = self.trade_service.process_trade_routes(tick_count)
        
        # Publish trade execution events for cross-system integration
        for trade_event in trade_events:
            try:
                publish_trade_event(
                    event_type=EconomyEventType.TRADE_EXECUTED,
                    trade_route_id=trade_event.get("trade_route_id"),
                    origin_region_id=trade_event.get("origin_region_id"),
                    destination_region_id=trade_event.get("destination_region_id"),
                    resource_id=trade_event.get("resource_id"),
                    amount=trade_event.get("amount"),
                    timestamp=trade_event.get("timestamp"),
                    trade_type="route_execution"
                )
            except Exception as e:
                logger.warning(f"Failed to publish trade execution event: {e}")
        
        return success_count, trade_events
    
    # Market API
    
    def get_market(self, market_id: Union[str, int]) -> Optional[Market]:
        """Get a market by ID."""
        return self.market_service.get_market(market_id)
    
    def get_markets_by_region(self, region_id: int) -> List[Market]:
        """Get all markets in a region."""
        return self.market_service.get_markets_by_region(region_id)
    
    def create_market(self, market_data: Union[Dict[str, Any], MarketData]) -> Optional[Market]:
        """Create a new market."""
        market = self.market_service.create_market(market_data)
        
        # Publish market creation event
        if market:
            try:
                publish_market_event(
                    event_type=EconomyEventType.MARKET_CREATED,
                    market_id=market.id,
                    region_id=market.region_id,
                    market_type=market.market_type,
                    market_name=market.name,
                    is_active=market.is_active,
                    base_demand=market.base_demand,
                    base_supply=market.base_supply
                )
            except Exception as e:
                logger.warning(f"Failed to publish market creation event: {e}")
        
        return market
    
    def update_market(self, market_id: int, updates: Dict[str, Any]) -> Optional[Market]:
        """Update an existing market."""
        return self.market_service.update_market(market_id, updates)
    
    def delete_market(self, market_id: int) -> bool:
        """Delete a market."""
        return self.market_service.delete_market(market_id)
    
    def calculate_price(self, resource_id: int, market_id: int,
                       quantity: float = 1.0) -> Tuple[float, Dict[str, Any]]:
        """Calculate the price for a resource in a market."""
        # Get current price first for comparison
        try:
            current_price, details = self.market_service.calculate_price(resource_id, market_id, quantity)
            
            # Publish price update event if price calculation includes changes
            if details.get("price_changed", False):
                try:
                    publish_price_event(
                        resource_id=str(resource_id),
                        market_id=market_id,
                        old_price=details.get("old_price", current_price),
                        new_price=current_price,
                        quantity=quantity,
                        modifiers=details.get("modifiers", {}),
                        calculation_method=details.get("method", "standard")
                    )
                except Exception as e:
                    logger.warning(f"Failed to publish price update event: {e}")
            
            return current_price, details
            
        except Exception as e:
            logger.error(f"Failed to calculate price: {e}")
            return 0.0, {"error": str(e)}
    
    def update_market_conditions(self, region_id: int,
                               event_modifiers: Optional[Dict[str, Any]] = None) -> List[Market]:
        """Update market conditions based on events, time, etc."""
        return self.market_service.update_market_conditions(region_id, event_modifiers)
    
    def get_resource_price_trends(self, resource_id: int,
                                region_id: Optional[int] = None) -> Dict[str, Any]:
        """Get price trends for a resource across markets."""
        return self.market_service.get_resource_price_trends(resource_id, region_id)
    
    # Futures API
    
    def get_future(self, future_id: Union[str, int]) -> Optional[CommodityFuture]:
        """Get a futures contract by ID."""
        return self.futures_service.get_future(future_id)
    
    def get_futures_by_resource(self, resource_id: Union[str, int]) -> List[CommodityFuture]:
        """Get all futures contracts for a resource."""
        return self.futures_service.get_futures_by_resource(resource_id)
    
    def get_futures_by_market(self, market_id: Union[str, int]) -> List[CommodityFuture]:
        """Get all futures contracts in a market."""
        return self.futures_service.get_futures_by_market(market_id)
    
    def get_open_futures(self, market_id: Optional[Union[str, int]] = None) -> List[CommodityFuture]:
        """Get all open futures contracts, optionally filtered by market."""
        return self.futures_service.get_open_futures(market_id)
    
    def create_future(self, future_data: Union[Dict[str, Any], CommodityFutureData]) -> Optional[CommodityFuture]:
        """Create a new futures contract."""
        return self.futures_service.create_future(future_data)
    
    def update_future(self, future_id: Union[str, int], updates: Dict[str, Any]) -> Optional[CommodityFuture]:
        """Update an existing futures contract."""
        return self.futures_service.update_future(future_id, updates)
    
    def match_buyer(self, future_id: Union[str, int], buyer_id: str) -> Optional[CommodityFuture]:
        """Match a buyer to an open futures contract."""
        return self.futures_service.match_buyer(future_id, buyer_id)
    
    def settle_future(self, future_id: Union[str, int]) -> Dict[str, Any]:
        """Settle a futures contract (execute the trade)."""
        return self.futures_service.settle_future(future_id)
    
    def process_expiring_futures(self) -> Dict[str, Any]:
        """Process all futures contracts that are expiring."""
        return self.futures_service.process_expiring_futures()
    
    def forecast_future_prices(self, resource_id: Union[str, int], 
                              market_id: Optional[Union[str, int]] = None,
                              time_periods: int = 3) -> Dict[str, Any]:
        """Forecast future prices based on futures contracts."""
        return self.futures_service.forecast_future_prices(resource_id, market_id, time_periods)
    
    # Economic Analytics and Processing
    
    def process_tick(self, tick_count: int = 1) -> Dict[str, Any]:
        """
        Process economic tick operations.
        
        This method coordinates all economic activities that should happen
        during a game tick, including trade route processing, market updates,
        and futures contract management.
        
        Args:
            tick_count: Number of ticks to process
            
        Returns:
            Dictionary with processing results
        """
        try:
            start_time = datetime.utcnow()
            results = {
                "tick_count": tick_count,
                "start_time": start_time.isoformat(),
                "trade_routes": {"processed": 0, "events": []},
                "markets": {"updated": 0, "regions": []},
                "futures": {"processed": 0, "settled": 0, "expired": 0},
                "events": {"published": 0, "errors": 0},
                "errors": []
            }
            
            # Process trade routes
            try:
                trade_success, trade_events = self.process_trade_routes(tick_count)
                results["trade_routes"]["processed"] = trade_success
                results["trade_routes"]["events"] = trade_events
            except Exception as e:
                error_msg = f"Trade route processing failed: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
            
            # Process futures contracts
            try:
                futures_result = self.process_expiring_futures()
                results["futures"]["processed"] = futures_result.get("processed_count", 0)
                results["futures"]["settled"] = len(futures_result.get("settled", []))
                results["futures"]["expired"] = len(futures_result.get("expired", []))
            except Exception as e:
                error_msg = f"Futures processing failed: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
            
            # Update market conditions for regions that had trade activity
            regions_processed = set()
            for trade_event in results["trade_routes"]["events"]:
                origin_id = trade_event.get("origin_region_id")
                dest_id = trade_event.get("destination_region_id")
                
                if origin_id and origin_id not in regions_processed:
                    try:
                        modifiers = self._create_market_modifiers_from_trades(origin_id, trade_events)
                        updated_markets = self.update_market_conditions(origin_id, modifiers)
                        results["markets"]["updated"] += len(updated_markets)
                        results["markets"]["regions"].append(origin_id)
                        regions_processed.add(origin_id)
                    except Exception as e:
                        error_msg = f"Market update failed for region {origin_id}: {str(e)}"
                        results["errors"].append(error_msg)
                        logger.error(error_msg)
                
                if dest_id and dest_id not in regions_processed:
                    try:
                        modifiers = self._create_market_modifiers_from_trades(dest_id, trade_events)
                        updated_markets = self.update_market_conditions(dest_id, modifiers)
                        results["markets"]["updated"] += len(updated_markets)
                        results["markets"]["regions"].append(dest_id)
                        regions_processed.add(dest_id)
                    except Exception as e:
                        error_msg = f"Market update failed for region {dest_id}: {str(e)}"
                        results["errors"].append(error_msg)
                        logger.error(error_msg)
            
            # Generate economic events for regions
            try:
                economy_events = self._generate_economy_events(tick_count, regions_processed)
                results["economy_events"] = economy_events
            except Exception as e:
                error_msg = f"Economy event generation failed: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
            
            # Process guild AI decisions
            try:
                guild_ai_results = self.process_all_guild_ai_ticks()
                results["guild_ai"] = {
                    "processed_guilds": guild_ai_results.get("processed_guilds", 0),
                    "total_actions": guild_ai_results.get("total_actions", 0),
                    "system_events": guild_ai_results.get("system_events", [])
                }
            except Exception as e:
                error_msg = f"Guild AI processing failed: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
            
            # Calculate completion time
            end_time = datetime.utcnow()
            results["end_time"] = end_time.isoformat()
            results["duration_seconds"] = (end_time - start_time).total_seconds()
            results["success"] = len(results["errors"]) == 0
            
            # Publish economic tick processed event
            try:
                publish_system_event(
                    event_type=EconomyEventType.ECONOMIC_TICK_PROCESSED,
                    tick_count=tick_count,
                    duration_seconds=results["duration_seconds"],
                    trade_routes_processed=results["trade_routes"]["processed"],
                    markets_updated=results["markets"]["updated"],
                    futures_processed=results["futures"]["processed"],
                    regions_affected=list(regions_processed),
                    success=results["success"],
                    error_count=len(results["errors"])
                )
                results["events"]["published"] += 1
            except Exception as e:
                results["events"]["errors"] += 1
                logger.warning(f"Failed to publish economic tick event: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Critical error in economic tick processing: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tick_count": tick_count
            }
    
    def calculate_price_index(self, region_id: Optional[int] = None) -> Dict[str, Any]:
        """Calculate economic price index for a region or globally."""
        try:
            if region_id:
                markets = self.get_markets_by_region(region_id)
            else:
                # Would need to get all markets - simplified for now
                markets = []
            
            if not markets:
                return {"index": 100.0, "status": "no_data", "markets_count": 0}
            
            total_price_weighted = 0.0
            total_weight = 0.0
            
            for market in markets:
                # Get market price data - simplified calculation
                market_weight = getattr(market, 'volume', 1.0)
                market_price = getattr(market, 'base_price', 100.0)
                
                total_price_weighted += market_price * market_weight
                total_weight += market_weight
            
            if total_weight > 0:
                price_index = (total_price_weighted / total_weight)
            else:
                price_index = 100.0
            
            return {
                "index": price_index,
                "status": "calculated",
                "markets_count": len(markets),
                "region_id": region_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating price index: {str(e)}")
            return {"index": 100.0, "status": "error", "error": str(e)}
    
    def calculate_tax_revenue(self, market_id: int) -> Dict[str, Any]:
        """Calculate tax revenue for a market."""
        try:
            market = self.get_market(market_id)
            if not market:
                return {"total_revenue": 0.0, "status": "market_not_found"}
            
            # Simplified tax calculation based on market activity
            base_revenue = getattr(market, 'volume', 0.0) * 0.05  # 5% tax rate
            
            return {
                "total_revenue": base_revenue,
                "tax_rate": 0.05,
                "market_id": market_id,
                "status": "calculated",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating tax revenue for market {market_id}: {str(e)}")
            return {"total_revenue": 0.0, "status": "error", "error": str(e)}
    
    def generate_economic_events(self, region_id: int) -> List[Dict[str, Any]]:
        """Generate economic events for a region."""
        events = []
        
        try:
            # Get region data
            markets = self.get_markets_by_region(region_id)
            resources = self.get_resources_by_region(region_id)
            
            # Generate supply/demand events
            for resource in resources:
                if hasattr(resource, 'amount') and resource.amount < 10:
                    events.append({
                        "event_type": "resource_shortage",
                        "region_id": region_id,
                        "resource_id": resource.id,
                        "severity": 0.8,
                        "affected_resources": [resource.id],
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Generate market events
            for market in markets:
                if random.random() < 0.1:  # 10% chance of market event
                    events.append({
                        "event_type": "market_fluctuation",
                        "region_id": region_id,
                        "market_id": market.id,
                        "severity": random.uniform(0.5, 1.5),
                        "affected_resources": [],
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Error generating economic events for region {region_id}: {str(e)}")
        
        return events
    
    def process_economic_event(self, event_type: str, region_id: int, 
                             affected_resources: List[int], severity: float) -> Dict[str, Any]:
        """Process an economic event and return results."""
        try:
            results = {"processed": True, "effects": []}
            
            if event_type == "resource_shortage":
                # Increase prices for affected resources
                for resource_id in affected_resources:
                    markets = self.get_markets_by_region(region_id)
                    for market in markets:
                        # Apply price increase based on severity
                        price_modifier = 1.0 + (severity * 0.5)
                        results["effects"].append({
                            "type": "price_increase",
                            "resource_id": resource_id,
                            "market_id": market.id,
                            "modifier": price_modifier
                        })
            
            elif event_type == "market_fluctuation":
                # Random market effects
                effect_type = random.choice(["price_increase", "price_decrease", "volume_change"])
                results["effects"].append({
                    "type": effect_type,
                    "region_id": region_id,
                    "severity": severity
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing economic event {event_type}: {str(e)}")
            return {"processed": False, "error": str(e)}
    
    def generate_economic_forecast(self, region_id: Optional[int] = None, 
                                 time_periods: int = 5) -> Dict[str, Any]:
        """Generate economic forecast for a region."""
        try:
            forecast = {
                "region_id": region_id,
                "periods": time_periods,
                "predictions": [],
                "confidence": 0.7,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Generate simple forecast based on current trends
            current_index = self.calculate_price_index(region_id)
            base_index = current_index.get("index", 100.0)
            
            for period in range(1, time_periods + 1):
                # Simple trend prediction with some randomness
                trend_factor = 1.0 + random.uniform(-0.05, 0.05)
                predicted_index = base_index * (trend_factor ** period)
                
                forecast["predictions"].append({
                    "period": period,
                    "price_index": predicted_index,
                    "trend": "stable" if abs(trend_factor - 1.0) < 0.02 else 
                            "increasing" if trend_factor > 1.0 else "decreasing"
                })
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating economic forecast: {str(e)}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    def get_economic_analytics(self, region_id: Optional[int] = None) -> Dict[str, Any]:
        """Get comprehensive economic analytics."""
        try:
            analytics = {
                "region_id": region_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {},
                "trends": {},
                "summary": {}
            }
            
            # Price index
            price_index = self.calculate_price_index(region_id)
            analytics["metrics"]["price_index"] = price_index
            
            # Resource counts
            if region_id:
                resources = self.get_resources_by_region(region_id)
                markets = self.get_markets_by_region(region_id)
            else:
                resources = []
                markets = []
            
            analytics["metrics"]["resource_count"] = len(resources)
            analytics["metrics"]["market_count"] = len(markets)
            
            # Economic health indicators
            analytics["summary"]["economic_health"] = "stable"  # Simplified
            analytics["summary"]["total_resources"] = len(resources)
            analytics["summary"]["total_markets"] = len(markets)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting economic analytics: {str(e)}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    def get_economy_status(self) -> Dict[str, Any]:
        """Get overall economy system status."""
        try:
            status = {
                "initialized": True,
                "services": {
                    "resource_service": self.resource_service is not None,
                    "trade_service": self.trade_service is not None,
                    "market_service": self.market_service is not None,
                    "futures_service": self.futures_service is not None
                },
                "database_connected": self.db_session is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting economy status: {str(e)}")
            return {"initialized": False, "error": str(e)}
    
    def initialize_economy(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize the economy system with optional configuration."""
        try:
            logger.info("Initializing economy system")
            
            # Apply configuration if provided
            if config:
                logger.info(f"Applying economy configuration: {config}")
            
            # Verify services are available
            services_status = {
                "resource_service": self.resource_service is not None,
                "trade_service": self.trade_service is not None,
                "market_service": self.market_service is not None,
                "futures_service": self.futures_service is not None
            }
            
            all_services_ready = all(services_status.values())
            
            result = {
                "initialized": all_services_ready,
                "services": services_status,
                "config_applied": config is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if all_services_ready:
                logger.info("Economy system successfully initialized")
            else:
                logger.warning(f"Economy system initialization incomplete: {services_status}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error initializing economy system: {str(e)}")
            return {"initialized": False, "error": str(e)}
    
    def shutdown_economy(self) -> Dict[str, Any]:
        """Shutdown the economy system gracefully."""
        try:
            logger.info("Shutting down economy system")
            
            # Clear singleton instance
            EconomyManager._instance = None
            
            return {
                "shutdown": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error shutting down economy system: {str(e)}")
            return {"shutdown": False, "error": str(e)}
    
    # Helper methods
    
    def _create_market_modifiers_from_trades(self, region_id: int, 
                                          trade_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create market modifiers based on trade activity."""
        modifiers = {}
        
        # Filter events for this region
        region_events = [e for e in trade_events if 
                       e.get("origin_region_id") == region_id or 
                       e.get("destination_region_id") == region_id]
        
        # Group by resource ID
        resource_volumes = {}
        for event in region_events:
            resource_id = event.get("resource_id")
            if not resource_id:
                continue
                
            amount = event.get("amount", 0)
            is_export = event.get("origin_region_id") == region_id
            
            if resource_id not in resource_volumes:
                resource_volumes[resource_id] = {"export": 0, "import": 0}
                
            if is_export:
                resource_volumes[resource_id]["export"] += amount
            else:
                resource_volumes[resource_id]["import"] += amount
        
        # Create price modifiers based on import/export balance
        for resource_id, volumes in resource_volumes.items():
            net_flow = volumes["import"] - volumes["export"]
            
            # Positive net flow (more imports) decreases prices
            # Negative net flow (more exports) increases prices
            if abs(net_flow) > 0:
                modifier = 1.0 - (net_flow * 0.01)
                modifier = max(0.9, min(1.1, modifier))  # Clamp to reasonable range
                modifiers[str(resource_id)] = modifier
        
        return modifiers
    
    def _generate_economy_events(self, tick_count: int, 
                               regions_processed: set) -> List[Dict[str, Any]]:
        """Generate legacy economy events."""
        events = []
        
        try:
            # Generate periodic economic events
            if tick_count % 10 == 0:  # Every 10 ticks
                for region_id in regions_processed:
                    if random.random() < 0.3:  # 30% chance
                        events.append({
                            "type": "economic_cycle",
                            "region_id": region_id,
                            "cycle_phase": random.choice(["growth", "recession", "recovery"]),
                            "timestamp": datetime.utcnow().isoformat()
                        })
            
            # Resource discovery events
            if tick_count % 50 == 0:  # Every 50 ticks
                for region_id in regions_processed:
                    if random.random() < 0.1:  # 10% chance
                        events.append({
                            "type": "resource_discovery",
                            "region_id": region_id,
                            "resource_type": random.choice(["minerals", "food", "energy"]),
                            "amount": random.randint(100, 1000),
                            "timestamp": datetime.utcnow().isoformat()
                        })
        
        except Exception as e:
            logger.error(f"Error generating legacy economy events: {str(e)}")
        
        return events
    
    # Shop Pricing API (Unified interface)
    
    def calculate_shop_buy_price(self, item: Dict[str, Any], player_level: int, 
                                character_attributes: Optional[Dict[str, Any]] = None,
                                faction_reputation: Optional[Dict[str, Any]] = None,
                                region_id: Optional[str] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate how much a shop will pay to buy an item from a player.
        
        Args:
            item: Item data dictionary
            player_level: Player's level
            character_attributes: Optional character stats for pricing modifiers
            faction_reputation: Optional faction relationships for pricing
            region_id: Optional region for market-based pricing
            
        Returns:
            Tuple of (price, calculation_details)
        """
        try:
            calculation_details = {
                "pricing_method": "unknown",
                "base_price": 0.0,
                "modifiers": {},
                "final_price": 0.0
            }
            
            # Try market-based pricing first if we have resource and market info
            if ('resource_id' in item and 'market_id' in item and 
                item['resource_id'] and item['market_id']):
                
                market_price, market_details = self.calculate_price(
                    item['resource_id'], 
                    item['market_id'], 
                    quantity=1.0
                )
                
                # Apply shop buy ratio from config
                shop_config = self.config.get_shop_pricing_config()
                buy_ratio = shop_config.get('buy_from_player_ratio', 0.6)
                
                base_price = market_price * buy_ratio
                calculation_details.update({
                    "pricing_method": "market_based",
                    "base_price": market_price,
                    "shop_buy_ratio": buy_ratio,
                    "market_details": market_details
                })
                
            else:
                # Fallback to level-based pricing
                base_price = self._calculate_level_based_item_price(item, player_level)
                shop_config = self.config.get_shop_pricing_config()
                buy_ratio = shop_config.get('level_based_buy_ratio', 0.25)
                
                base_price = base_price * buy_ratio
                calculation_details.update({
                    "pricing_method": "level_based",
                    "base_price": base_price,
                    "shop_buy_ratio": buy_ratio
                })
            
            # Apply character and faction modifiers
            modified_price, modifiers = self._apply_character_pricing_modifiers(
                base_price, character_attributes, faction_reputation
            )
            
            calculation_details["modifiers"] = modifiers
            calculation_details["final_price"] = modified_price
            
            return modified_price, calculation_details
            
        except Exception as e:
            logger.error(f"Error calculating shop buy price: {str(e)}")
            return 0.0, {"error": str(e)}
    
    def calculate_shop_sell_price(self, item: Dict[str, Any], player_level: int,
                                 character_attributes: Optional[Dict[str, Any]] = None,
                                 faction_reputation: Optional[Dict[str, Any]] = None,
                                 region_id: Optional[str] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate how much a shop will charge to sell an item to a player.
        
        Args:
            item: Item data dictionary
            player_level: Player's level
            character_attributes: Optional character stats for pricing modifiers
            faction_reputation: Optional faction relationships for pricing
            region_id: Optional region for market-based pricing
            
        Returns:
            Tuple of (price, calculation_details)
        """
        try:
            calculation_details = {
                "pricing_method": "unknown",
                "base_price": 0.0,
                "modifiers": {},
                "final_price": 0.0
            }
            
            # Try market-based pricing first
            if ('resource_id' in item and 'market_id' in item and 
                item['resource_id'] and item['market_id']):
                
                market_price, market_details = self.calculate_price(
                    item['resource_id'], 
                    item['market_id'], 
                    quantity=1.0
                )
                
                # Shop sells at market price (or with markup from config)
                shop_config = self.config.get_shop_pricing_config()
                sell_markup = shop_config.get('sell_to_player_markup', 1.0)
                
                base_price = market_price * sell_markup
                calculation_details.update({
                    "pricing_method": "market_based",
                    "base_price": market_price,
                    "shop_sell_markup": sell_markup,
                    "market_details": market_details
                })
                
            else:
                # Fallback to level-based pricing
                item_price = self._calculate_level_based_item_price(item, player_level)
                
                # Use configured markup for level-based pricing
                shop_config = self.config.get_shop_pricing_config()
                sell_markup = shop_config.get('level_based_sell_markup', 1.5)
                
                base_price = item_price * sell_markup
                calculation_details.update({
                    "pricing_method": "level_based",
                    "base_price": item_price,
                    "shop_sell_markup": sell_markup
                })
            
            # Apply character and faction modifiers
            modified_price, modifiers = self._apply_character_pricing_modifiers(
                base_price, character_attributes, faction_reputation
            )
            
            calculation_details["modifiers"] = modifiers
            calculation_details["final_price"] = modified_price
            
            return modified_price, calculation_details
            
        except Exception as e:
            logger.error(f"Error calculating shop sell price: {str(e)}")
            return 0.0, {"error": str(e)}
    
    def get_expected_gold_at_level(self, level: int) -> int:
        """
        Get expected daily gold income for a player level using configuration.
        
        Args:
            level: Player level
            
        Returns:
            Expected daily gold income
        """
        try:
            gold_rates = self.config.get_gold_earning_rates()
            base_rates = gold_rates.get('daily_gold_by_level', {})
            
            # Find the appropriate rate for this level
            level_str = str(level)
            if level_str in base_rates:
                return base_rates[level_str]
            
            # Fallback to level-based calculation if not in config
            level = max(1, min(level, 20))  # Clamp to valid range
            return gold_rates.get('base_daily_gold', 50) + (level - 1) * gold_rates.get('per_level_increase', 5)
            
        except Exception as e:
            logger.error(f"Error getting expected gold for level {level}: {str(e)}")
            return 50  # Safe fallback
    
    def _calculate_level_based_item_price(self, item: Dict[str, Any], player_level: int) -> float:
        """
        Calculate item price based on player level and item rarity.
        
        Args:
            item: Item data
            player_level: Player level
            
        Returns:
            Calculated price
        """
        try:
            # Get base gold expectation for level
            base_gold = self.get_expected_gold_at_level(player_level)
            
            # Get rarity multiplier from config
            item_scaling = self.config.get_item_cost_scaling()
            rarity = item.get("rarity", "normal")
            rarity_multipliers = item_scaling.get('rarity_multipliers', {})
            multiplier = rarity_multipliers.get(rarity, rarity_multipliers.get('normal', 0.25))
            
            return base_gold * multiplier
            
        except Exception as e:
            logger.error(f"Error calculating level-based price: {str(e)}")
            return 10.0  # Safe fallback
    
    def _apply_character_pricing_modifiers(self, base_price: float,
                                          character_attributes: Optional[Dict[str, Any]] = None,
                                          faction_reputation: Optional[Dict[str, Any]] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Apply character attributes and faction reputation modifiers to pricing.
        
        Args:
            base_price: Base price before modifiers
            character_attributes: Character stats that might affect pricing
            faction_reputation: Faction relationships that affect pricing
            
        Returns:
            Tuple of (modified_price, modifiers_applied)
        """
        modifiers = {}
        final_multiplier = 1.0
        
        try:
            # Character attribute modifiers (e.g., Charisma for better prices)
            if character_attributes:
                charisma = character_attributes.get('charisma', 10)
                if charisma != 10:  # 10 is baseline
                    charisma_modifier = 1.0 + (charisma - 10) * 0.02  # 2% per point above/below 10
                    final_multiplier *= charisma_modifier
                    modifiers['charisma_modifier'] = charisma_modifier
            
            # Faction reputation modifiers
            if faction_reputation:
                # Calculate average reputation with trading factions
                trading_rep = faction_reputation.get('merchants_guild', 0)
                local_rep = faction_reputation.get('local_faction', 0)
                
                avg_rep = (trading_rep + local_rep) / 2 if trading_rep or local_rep else 0
                
                if avg_rep != 0:
                    rep_modifier = 1.0 + (avg_rep * 0.001)  # 0.1% per reputation point
                    final_multiplier *= rep_modifier
                    modifiers['reputation_modifier'] = rep_modifier
            
            final_price = base_price * final_multiplier
            modifiers['total_multiplier'] = final_multiplier
            
            return final_price, modifiers
            
        except Exception as e:
            logger.error(f"Error applying pricing modifiers: {str(e)}")
            return base_price, {"error": str(e)}
    
    # Shop Management API
    
    def process_shop_transaction(self, transaction_type: str, character_id: str, 
                               npc_id: str, item: Dict[str, Any], 
                               player_level: int, character_attributes: Optional[Dict[str, Any]] = None,
                               faction_reputation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a shop transaction between a character and NPC.
        
        Args:
            transaction_type: "buy" or "sell"
            character_id: ID of the character
            npc_id: ID of the NPC shop owner
            item: Item being transacted
            player_level: Character level for pricing
            character_attributes: Character stats affecting pricing
            faction_reputation: Faction relationships affecting pricing
            
        Returns:
            Transaction result with details
        """
        try:
            result = {
                "transaction_id": f"tx_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{character_id}_{npc_id}",
                "transaction_type": transaction_type,
                "character_id": character_id,
                "npc_id": npc_id,
                "item": item,
                "player_level": player_level,
                "success": False,
                "message": "",
                "price": 0.0,
                "modifiers": {}
            }
            
            if transaction_type == "buy":
                price, modifiers = self.calculate_shop_buy_price(
                    item, player_level, character_attributes, faction_reputation
                )
                result["price"] = price
                result["modifiers"] = modifiers
                result["success"] = True
                result["message"] = f"Purchase completed for {price}g"
                
            elif transaction_type == "sell":
                price, modifiers = self.calculate_shop_sell_price(
                    item, player_level, character_attributes, faction_reputation
                )
                result["price"] = price
                result["modifiers"] = modifiers
                result["success"] = True
                result["message"] = f"Sale completed for {price}g"
                
            else:
                result["message"] = f"Unknown transaction type: {transaction_type}"
                return result
            
            # Publish transaction event
            try:
                publish_transaction_event(
                    event_type=EconomyEventType.TRANSACTION_COMPLETED,
                    transaction_id=result["transaction_id"],
                    buyer_id=character_id if transaction_type == "buy" else npc_id,
                    seller_id=npc_id if transaction_type == "buy" else character_id,
                    item_id=item.get("id", "unknown"),
                    item_name=item.get("name", "unknown"),
                    quantity=1.0,
                    unit_price=price,
                    total_value=price,
                    transaction_type=transaction_type,
                    character_level=player_level,
                    modifiers_applied=modifiers
                )
            except Exception as e:
                logger.warning(f"Failed to publish shop transaction event: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing shop transaction: {str(e)}")
            return {
                "success": False,
                "message": f"Transaction failed: {str(e)}",
                "error": str(e)
            }
    
    def generate_shop_inventory(self, npc_id: str, shop_type: str = "general",
                               item_count: int = 10, average_player_level: int = 10,
                               region_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate shop inventory with unified pricing.
        
        Args:
            npc_id: Shop owner NPC ID
            shop_type: Type of shop (affects item categories)
            item_count: Number of items to generate
            average_player_level: Average level of expected customers (affects pricing)
            region_id: Region for market-based pricing
            
        Returns:
            List of shop inventory items with unified pricing
        """
        try:
            # Determine shop categories based on type
            shop_categories = {
                "general": ["gear", "consumables", "tools"],
                "armorer": ["armor", "shields", "helmets"],
                "weaponsmith": ["weapons", "ammunition"],
                "alchemist": ["potions", "reagents", "scrolls"],
                "trader": ["goods", "crafting", "materials"]
            }
            
            categories = shop_categories.get(shop_type, ["gear", "consumables"])
            
            inventory = []
            for i in range(item_count):
                # Generate basic item
                category = random.choice(categories)
                rarity = random.choices(
                    ["normal", "rare", "epic", "legendary"],
                    weights=[70, 20, 8, 2]
                )[0]
                
                item = {
                    "id": f"shop_{npc_id}_{i}",
                    "display_name": f"{rarity.title()} {category.title()}",
                    "category": category,
                    "rarity": rarity,
                    "weight_lbs": random.randint(1, 10),
                    "region_id": region_id
                }
                
                # Apply unified pricing
                sell_price, pricing_details = self.calculate_shop_sell_price(
                    item, average_player_level, region_id=region_id
                )
                
                item.update({
                    "resale_price": round(sell_price),
                    "pricing_method": pricing_details.get("pricing_method", "unified"),
                    "added_at": datetime.utcnow().isoformat()
                })
                
                inventory.append(item)
            
            return inventory
            
        except Exception as e:
            logger.error(f"Error generating shop inventory: {str(e)}")
            return []
    
    # Tournament Economy API
    
    def calculate_tournament_entry_fee(self, tournament_type: str, player_level: int,
                                     region_id: Optional[str] = None,
                                     currency: str = "gold") -> Tuple[int, Dict[str, Any]]:
        """
        Calculate tournament entry fee based on player level and tournament type.
        
        Args:
            tournament_type: Type of tournament (e.g., "standard", "premium", "elite")
            player_level: Player's current level
            region_id: Optional region for regional pricing adjustments
            currency: Currency type ("gold" or "tokens")
            
        Returns:
            Tuple of (entry_fee, calculation_details)
        """
        result = self.tournament_service.calculate_entry_fee(
            tournament_type, player_level, region_id, currency
        )
        
        # Publish tournament entry fee calculation event
        try:
            publish_system_event(
                event_type=EconomyEventType.TOURNAMENT_ENTRY_FEE_CALCULATED,
                tournament_type=tournament_type,
                player_level=player_level,
                region_id=region_id,
                currency=currency,
                entry_fee=result[0],
                calculation_details=result[1]
            )
        except Exception as e:
            logger.warning(f"Failed to publish tournament entry fee event: {e}")
        
        return result
    
    def create_tournament_prize_pool(self, participants: List[Dict[str, Any]],
                                   tournament_type: str) -> Dict[str, Any]:
        """
        Create tournament prize pool from participant entry fees.
        
        Args:
            participants: List of participant data with entry fees
            tournament_type: Type of tournament
            
        Returns:
            Prize pool information
        """
        return self.tournament_service.create_tournament_prize_pool(
            participants, tournament_type
        )
    
    def distribute_tournament_prizes(self, winners: List[Dict[str, Any]],
                                   prize_pool: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Distribute tournament prizes to winners.
        
        Args:
            winners: List of winner data with rankings
            prize_pool: Prize pool information
            
        Returns:
            List of prize distribution results
        """
        result = self.tournament_service.distribute_tournament_prizes(winners, prize_pool)
        
        # Publish tournament prize distribution event
        try:
            publish_system_event(
                event_type=EconomyEventType.TOURNAMENT_PRIZE_DISTRIBUTED,
                winners_count=len(winners),
                prize_pool_total=prize_pool.get("total_value", 0),
                prize_pool_currency=prize_pool.get("currency", "mixed"),
                distribution_results=result
            )
        except Exception as e:
            logger.warning(f"Failed to publish tournament prize distribution event: {e}")
        
        return result
    
    def validate_tournament_entry(self, player_data: Dict[str, Any],
                                tournament_type: str,
                                entry_currency: str) -> Tuple[bool, str]:
        """
        Validate if a player can enter a tournament.
        
        Args:
            player_data: Player information including currency balances
            tournament_type: Type of tournament
            entry_currency: Currency player wants to use for entry
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return self.tournament_service.validate_tournament_entry(
            player_data, tournament_type, entry_currency
        )
    
    def calculate_tournament_economic_impact(self, tournament_result: Dict[str, Any],
                                           region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate the economic impact of a tournament on the regional economy.
        
        Args:
            tournament_result: Complete tournament result data
            region_id: Region where tournament was held
            
        Returns:
            Economic impact analysis
        """
        return self.tournament_service.calculate_economic_impact(
            tournament_result, region_id
        )

    # Central Bank API
    
    def calculate_interest_rate(self, region_id: Optional[str] = None,
                              loan_type: str = "personal_loan") -> float:
        """
        Calculate current interest rate for a region and loan type.
        
        Args:
            region_id: Region for rate calculation
            loan_type: Type of loan (personal_loan, business_loan, emergency_loan)
            
        Returns:
            Current interest rate as decimal (0.05 = 5%)
        """
        return self.central_bank_service.calculate_interest_rate(region_id, loan_type)
    
    def calculate_tax_rate(self, region_id: Optional[str] = None,
                          tax_type: str = "default") -> float:
        """
        Calculate current tax rate for a region and tax type.
        
        Args:
            region_id: Region for tax calculation
            tax_type: Type of tax (default, transaction_tax, luxury_tax, etc.)
            
        Returns:
            Current tax rate as decimal (0.1 = 10%)
        """
        return self.central_bank_service.calculate_tax_rate(region_id, tax_type)
    
    def create_loan_offer(self, borrower_data: Dict[str, Any],
                         loan_amount: int, loan_type: str = "personal_loan",
                         region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a loan offer for a borrower.
        
        Args:
            borrower_data: Borrower information (wealth, credit history, etc.)
            loan_amount: Requested loan amount
            loan_type: Type of loan
            region_id: Region for loan terms
            
        Returns:
            Loan offer details or rejection
        """
        return self.central_bank_service.create_loan_offer(
            borrower_data, loan_amount, loan_type, region_id
        )
    
    def trigger_economic_event(self, event_type: str,
                             region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger an economic event through the central bank.
        
        Args:
            event_type: Type of economic event to trigger
            region_id: Optional region to target
            
        Returns:
            Event trigger results
        """
        result = self.central_bank_service.trigger_economic_event(event_type, region_id)
        
        # Publish economic event triggered event
        try:
            publish_system_event(
                event_type=EconomyEventType.ECONOMIC_EVENT_TRIGGERED,
                triggered_event_type=event_type,
                region_id=region_id,
                event_results=result
            )
        except Exception as e:
            logger.warning(f"Failed to publish economic event trigger event: {e}")
        
        return result
    
    def manage_money_supply(self, target_inflation: float = 0.02) -> Dict[str, Any]:
        """
        Manage money supply to target inflation rate.
        
        Args:
            target_inflation: Target inflation rate
            
        Returns:
            Money supply management actions taken
        """
        return self.central_bank_service.manage_money_supply(target_inflation)
    
    def get_economic_state(self) -> Dict[str, Any]:
        """Get current economic state information."""
        return self.central_bank_service.get_economic_state()

    # =========================================================================
    # GUILD AI SYSTEM
    # =========================================================================
    
    def evaluate_guild_expansion_opportunities(self, guild_id: str) -> List[Dict[str, Any]]:
        """
        Evaluate expansion opportunities for a guild using AI analysis.
        
        Args:
            guild_id: ID of the guild to evaluate
            
        Returns:
            List of expansion opportunities with AI recommendations
        """
        try:
            from uuid import UUID
            guild_uuid = UUID(guild_id)
            expansion_options = self.guild_ai_service.evaluate_expansion_opportunities(guild_uuid)
            
            # Convert to dictionaries for API response
            return [
                {
                    "region_id": option.region_id,
                    "priority_score": option.priority_score,
                    "expansion_cost": option.expansion_cost,
                    "expected_profit": option.expected_profit,
                    "risk_level": option.risk_level,
                    "competition_level": option.competition_level,
                    "strategic_value": option.strategic_value,
                    "reasoning": option.reasoning
                }
                for option in expansion_options
            ]
            
        except Exception as e:
            logger.error(f"Error evaluating guild expansion opportunities: {e}")
            return []
    
    def plan_guild_pricing_strategy(self, guild_id: str) -> Dict[str, Any]:
        """
        Plan intelligent pricing strategy for a guild.
        
        Args:
            guild_id: ID of the guild
            
        Returns:
            Pricing strategy plan with AI recommendations
        """
        try:
            from uuid import UUID
            guild_uuid = UUID(guild_id)
            return self.guild_ai_service.plan_pricing_strategy(guild_uuid)
            
        except Exception as e:
            logger.error(f"Error planning guild pricing strategy: {e}")
            return {"error": str(e)}
    
    def assess_guild_competition_threats(self, guild_id: str) -> List[Dict[str, Any]]:
        """
        Assess competitive threats facing a guild using AI analysis.
        
        Args:
            guild_id: ID of the guild
            
        Returns:
            List of identified threats with AI recommendations
        """
        try:
            from uuid import UUID
            guild_uuid = UUID(guild_id)
            threats = self.guild_ai_service.assess_competition_threats(guild_uuid)
            
            # Convert to dictionaries for API response
            return [
                {
                    "threat_id": threat.threat_id,
                    "threat_type": threat.threat_type,
                    "severity": threat.severity,
                    "source_guild_id": str(threat.source_guild_id) if threat.source_guild_id else None,
                    "affected_regions": threat.affected_regions,
                    "recommended_response": threat.recommended_response,
                    "urgency": threat.urgency
                }
                for threat in threats
            ]
            
        except Exception as e:
            logger.error(f"Error assessing guild competition threats: {e}")
            return []
    
    def propose_guild_alliances(self, guild_id: str) -> List[Dict[str, Any]]:
        """
        Propose potential alliances for a guild using AI analysis.
        
        Args:
            guild_id: ID of the guild
            
        Returns:
            List of alliance proposals with AI recommendations
        """
        try:
            from uuid import UUID
            guild_uuid = UUID(guild_id)
            proposals = self.guild_ai_service.propose_alliances(guild_uuid)
            
            # Convert to dictionaries for API response
            return [
                {
                    "target_guild_id": str(proposal.target_guild_id),
                    "alliance_type": proposal.alliance_type,
                    "mutual_benefit_score": proposal.mutual_benefit_score,
                    "trust_level": proposal.trust_level,
                    "strategic_alignment": proposal.strategic_alignment,
                    "proposed_terms": proposal.proposed_terms,
                    "success_probability": proposal.success_probability
                }
                for proposal in proposals
            ]
            
        except Exception as e:
            logger.error(f"Error proposing guild alliances: {e}")
            return []
    
    def execute_guild_market_manipulation(self, guild_id: str) -> Dict[str, Any]:
        """
        Plan and execute market manipulation strategies for a guild.
        
        Args:
            guild_id: ID of the guild
            
        Returns:
            Market manipulation plan with AI recommendations
        """
        try:
            from uuid import UUID
            guild_uuid = UUID(guild_id)
            manipulation_plan = self.guild_ai_service.execute_market_manipulation(guild_uuid)
            
            # Convert to dictionary for API response
            return {
                "manipulation_type": manipulation_plan.manipulation_type,
                "target_markets": manipulation_plan.target_markets,
                "target_resources": manipulation_plan.target_resources,
                "expected_impact": manipulation_plan.expected_impact,
                "execution_cost": manipulation_plan.execution_cost,
                "risk_level": manipulation_plan.risk_level,
                "timeline": manipulation_plan.timeline,
                "success_probability": manipulation_plan.success_probability
            }
            
        except Exception as e:
            logger.error(f"Error executing guild market manipulation: {e}")
            return {"error": str(e)}
    
    def process_guild_ai_tick(self, guild_id: str) -> Dict[str, Any]:
        """
        Process AI decision-making for a guild during a game tick.
        
        Args:
            guild_id: ID of the guild to process
            
        Returns:
            Results of AI processing including actions taken and decisions made
        """
        try:
            from uuid import UUID
            guild_uuid = UUID(guild_id)
            return self.guild_ai_service.process_guild_ai_tick(guild_uuid)
            
        except Exception as e:
            logger.error(f"Error processing guild AI tick: {e}")
            return {"error": str(e)}
    
    def process_all_guild_ai_ticks(self) -> Dict[str, Any]:
        """
        Process AI decision-making for all active guilds during a game tick.
        
        Returns:
            Aggregated results of AI processing for all guilds
        """
        try:
            # Get all active guilds
            from backend.infrastructure.database.economy.advanced_models import MerchantGuildEntity
            active_guilds = self.db_session.query(MerchantGuildEntity).filter(
                MerchantGuildEntity.is_active == True
            ).all()
            
            results = {
                "processed_guilds": 0,
                "total_actions": 0,
                "guild_results": {},
                "system_events": []
            }
            
            for guild in active_guilds:
                try:
                    guild_result = self.guild_ai_service.process_guild_ai_tick(guild.id)
                    
                    if "error" not in guild_result:
                        results["processed_guilds"] += 1
                        results["total_actions"] += len(guild_result.get("actions_taken", []))
                        results["guild_results"][str(guild.id)] = guild_result
                        
                        # Generate system events for significant guild actions
                        if guild_result.get("actions_taken"):
                            results["system_events"].append({
                                "type": "guild_ai_actions",
                                "guild_id": str(guild.id),
                                "guild_name": guild.name,
                                "actions": guild_result["actions_taken"],
                                "timestamp": datetime.utcnow().isoformat()
                            })
                    
                except Exception as e:
                    logger.error(f"Error processing AI tick for guild {guild.id}: {e}")
                    results["guild_results"][str(guild.id)] = {"error": str(e)}
            
            # Publish system-wide guild AI processing event
            try:
                publish_system_event(
                    event_type=EconomyEventType.ECONOMIC_ANALYTICS_UPDATED,
                    guilds_processed=results["processed_guilds"],
                    total_actions=results["total_actions"],
                    processing_type="guild_ai_tick"
                )
            except Exception as e:
                logger.warning(f"Failed to publish guild AI processing event: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing all guild AI ticks: {e}")
            return {"error": str(e)}
    
    def get_guild_personality_analysis(self, guild_id: str) -> Dict[str, Any]:
        """
        Get AI personality analysis for a guild.
        
        Args:
            guild_id: ID of the guild
            
        Returns:
            Guild personality analysis and behavioral predictions
        """
        try:
            from uuid import UUID
            from backend.infrastructure.database.economy.advanced_models import MerchantGuildEntity
            
            guild_uuid = UUID(guild_id)
            guild = self.db_session.query(MerchantGuildEntity).filter(
                MerchantGuildEntity.id == guild_uuid
            ).first()
            
            if not guild:
                return {"error": "Guild not found"}
            
            personality = self.guild_ai_service.get_guild_personality(guild)
            personality_config = self.guild_ai_service.guild_ai_config["personality_traits"][personality.value]
            
            return {
                "guild_id": guild_id,
                "guild_name": guild.name,
                "personality_type": personality.value,
                "personality_traits": personality_config,
                "behavioral_predictions": {
                    "expansion_likelihood": personality_config["expansion_rate"],
                    "cooperation_tendency": personality_config["cooperation_willingness"],
                    "competition_aggression": personality_config["competition_aggression"],
                    "risk_tolerance": personality_config["risk_tolerance"],
                    "market_manipulation_tendency": personality_config.get("market_manipulation_tendency", 0.0)
                },
                "current_status": {
                    "total_wealth": guild.total_wealth,
                    "territory_count": len(guild.territory_control or []),
                    "market_share": guild.market_share,
                    "pricing_influence": guild.pricing_influence,
                    "coordination_level": guild.coordination_level,
                    "alliance_count": len(guild.allied_guilds or []),
                    "rival_count": len(guild.rival_guilds or [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting guild personality analysis: {e}")
            return {"error": str(e)} 