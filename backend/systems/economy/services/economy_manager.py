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

import logging
logger = logging.getLogger(__name__)
from backend.systems.economy.services.resource import (
    Resource, ResourceData
)
from backend.systems.economy.models.trade_route import (
    TradeRoute, TradeRouteData
)
from backend.systems.economy.models.market import (
    Market, MarketData
)
from backend.systems.economy.models.commodity_future import (
    CommodityFuture, CommodityFutureData
)
from backend.systems.economy.services.resource_service import ResourceService
from backend.systems.economy.services.trade_service import TradeService
from backend.systems.economy.services.market_service import MarketService
from backend.systems.economy.services.futures_service import FuturesService

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
        """Initialize the economy manager.
        
        Args:
            db_session: SQLAlchemy session for database operations
        """
        if EconomyManager._instance is not None:
            raise Exception("EconomyManager is a singleton, use get_instance()")
            
        self.db_session = db_session
        
        # Initialize services
        self.resource_service = ResourceService(db_session)
        self.trade_service = TradeService(db_session, self.resource_service)
        self.market_service = MarketService(db_session, self.resource_service)
        self.futures_service = FuturesService(db_session, self.resource_service, self.market_service)
        
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
        return self.resource_service.create_resource(resource_data)
    
    def update_resource(self, resource_id: int, updates: Dict[str, Any]) -> Optional[Resource]:
        """Update an existing resource."""
        return self.resource_service.update_resource(resource_id, updates)
    
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
        return self.resource_service.transfer_resource(source_region_id, dest_region_id, resource_id, amount)
    
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
        return self.trade_service.create_trade_route(route_data)
    
    def update_trade_route(self, route_id: int, updates: Dict[str, Any]) -> Optional[TradeRoute]:
        """Update an existing trade route."""
        return self.trade_service.update_trade_route(route_id, updates)
    
    def delete_trade_route(self, route_id: int) -> bool:
        """Delete a trade route."""
        return self.trade_service.delete_trade_route(route_id)
    
    def process_trade_routes(self, tick_count: int = 1) -> Tuple[int, List[Dict[str, Any]]]:
        """Process all active trade routes for resource transfers."""
        return self.trade_service.process_trade_routes(tick_count)
    
    # Market API
    
    def get_market(self, market_id: Union[str, int]) -> Optional[Market]:
        """Get a market by ID."""
        return self.market_service.get_market(market_id)
    
    def get_markets_by_region(self, region_id: int) -> List[Market]:
        """Get all markets in a region."""
        return self.market_service.get_markets_by_region(region_id)
    
    def create_market(self, market_data: Union[Dict[str, Any], MarketData]) -> Optional[Market]:
        """Create a new market."""
        return self.market_service.create_market(market_data)
    
    def update_market(self, market_id: int, updates: Dict[str, Any]) -> Optional[Market]:
        """Update an existing market."""
        return self.market_service.update_market(market_id, updates)
    
    def delete_market(self, market_id: int) -> bool:
        """Delete a market."""
        return self.market_service.delete_market(market_id)
    
    def calculate_price(self, resource_id: int, market_id: int,
                       quantity: float = 1.0) -> Tuple[float, Dict[str, Any]]:
        """Calculate the price for a resource in a market."""
        return self.market_service.calculate_price(resource_id, market_id, quantity)
    
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
        """Process economy for a world tick.
        
        This method integrates all economy subsystems and processes them for a world tick.
        
        Args:
            tick_count: Current world tick count
            
        Returns:
            Dictionary with results and events from processing
        """
        logger.info(f"Processing economy tick {tick_count}")
        results = {
            "trades_processed": 0,
            "markets_updated": 0,
            "tax_revenue": {},
            "price_indices": {},
            "generated_events": [],
            "futures_processed": {"settled": [], "expired": []},
            "events": []
        }
        
        try:
            # Process trade routes
            trades_count, trade_events = self.process_trade_routes(tick_count)
            results["trades_processed"] = trades_count
            results["events"].extend(trade_events)
            
            # Process market changes for each region with markets
            regions_processed = set()
            markets_updated = 0
            
            # Process trade event regions
            for event in trade_events:
                origin_id = event.get("origin_region_id")
                dest_id = event.get("destination_region_id")
                
                # Process origin region markets
                if origin_id and origin_id not in regions_processed:
                    modifiers = self._create_market_modifiers_from_trades(origin_id, trade_events)
                    updated = self.update_market_conditions(origin_id, modifiers)
                    markets_updated += len(updated)
                    regions_processed.add(origin_id)
                
                # Process destination region markets
                if dest_id and dest_id not in regions_processed:
                    modifiers = self._create_market_modifiers_from_trades(dest_id, trade_events)
                    updated = self.update_market_conditions(dest_id, modifiers)
                    markets_updated += len(updated)
                    regions_processed.add(dest_id)
            
            results["markets_updated"] = markets_updated
            
            # Calculate economic metrics for processed regions
            for region_id in regions_processed:
                # Tax revenue calculation
                markets = self.get_markets_by_region(region_id)
                region_tax_revenue = 0.0
                
                for market in markets:
                    market_revenue = self.calculate_tax_revenue(market.id)
                    region_tax_revenue += market_revenue.get("total_revenue", 0.0)
                    results["tax_revenue"][str(market.id)] = market_revenue
                
                results["tax_revenue"][f"region_{region_id}_total"] = region_tax_revenue
                
                # Price indices
                price_index_data = self.calculate_price_index(region_id=region_id)
                results["price_indices"][str(region_id)] = price_index_data
                
                # Economic events generation
                if tick_count % 5 == 0:
                    economic_events = self.generate_economic_events(region_id)
                    results["generated_events"].extend(economic_events)
                    
                    # Process economic events
                    for event in economic_events:
                        event_type = event.get("event_type")
                        affected_resources = event.get("affected_resources")
                        severity = event.get("severity", 1.0)
                        
                        if event_type:
                            event_results = self.process_economic_event(
                                event_type, region_id, affected_resources, severity
                            )
                            event["results"] = event_results
            
            # Process futures contracts
            futures_results = self.process_expiring_futures()
            if "error" not in futures_results:
                results["futures_processed"] = {
                    "settled": futures_results.get("settled", []),
                    "expired": futures_results.get("expired", []),
                    "error_count": len(futures_results.get("errors", []))
                }
                
                # Add futures settlement events
                for settlement in futures_results.get("settled", []):
                    if abs(settlement.get("profit_loss", 0)) > 0:
                        results["events"].append({
                            "type": "future_settlement",
                            "future_id": settlement.get("future_id"),
                            "resource_id": settlement.get("resource_id"),
                            "market_id": settlement.get("market_id"),
                            "profit_loss": settlement.get("profit_loss"),
                            "winner": "buyer" if settlement.get("profit_loss", 0) > 0 else "seller",
                            "timestamp": datetime.utcnow().isoformat()
                        })
            
            # Generate additional economy events
            legacy_economy_events = self._generate_economy_events(tick_count, regions_processed)
            results["events"].extend(legacy_economy_events)
            results["events"].extend(results["generated_events"])
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing economy tick: {str(e)}")
            results["error"] = str(e)
            return results
    
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