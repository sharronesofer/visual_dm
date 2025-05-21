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

from app.core.logging import logger
from backend.systems.economy.models import (
    Resource, ResourceData, 
    TradeRoute, TradeRouteData,
    Market, MarketData,
    CommodityFuture, CommodityFutureData
)
from backend.systems.economy.services import (
    ResourceService,
    TradeService,
    MarketService,
    FuturesService
)

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
    
    # World Tick Processing
    
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
            
            # In a real implementation, we would query all distinct regions with markets
            # For now, we'll use the regions from trade events as a sample
            for event in trade_events:
                origin_id = event.get("origin_region_id")
                dest_id = event.get("destination_region_id")
                
                # Process origin region markets if not already processed
                if origin_id and origin_id not in regions_processed:
                    # Create event modifiers based on trade activity
                    modifiers = self._create_market_modifiers_from_trades(origin_id, trade_events)
                    updated = self.update_market_conditions(origin_id, modifiers)
                    markets_updated += len(updated)
                    regions_processed.add(origin_id)
                
                # Process destination region markets if not already processed
                if dest_id and dest_id not in regions_processed:
                    modifiers = self._create_market_modifiers_from_trades(dest_id, trade_events)
                    updated = self.update_market_conditions(dest_id, modifiers)
                    markets_updated += len(updated)
                    regions_processed.add(dest_id)
            
            results["markets_updated"] = markets_updated
            
            # Calculate tax revenue for all processed regions
            for region_id in regions_processed:
                # Get all markets in the region
                markets = self.get_markets_by_region(region_id)
                
                region_tax_revenue = 0.0
                for market in markets:
                    market_revenue = self.calculate_tax_revenue(market.id)
                    region_tax_revenue += market_revenue.get("total_revenue", 0.0)
                    
                    # Append the market's revenue to results
                    results["tax_revenue"][str(market.id)] = market_revenue
                
                # Add the region total
                results["tax_revenue"][f"region_{region_id}_total"] = region_tax_revenue
                
                # Calculate and store price indices for the region
                price_index_data = self.calculate_price_index(region_id=region_id)
                results["price_indices"][str(region_id)] = price_index_data
                
                # Generate economic events based on metrics
                if tick_count % 5 == 0:  # Only generate these events periodically
                    economic_events = self.generate_economic_events(region_id)
                    results["generated_events"].extend(economic_events)
                    
                    # Process these events immediately
                    for event in economic_events:
                        event_type = event.get("event_type")
                        affected_resources = event.get("affected_resources")
                        severity = event.get("severity", 1.0)
                        
                        if event_type:
                            event_results = self.process_economic_event(
                                event_type, region_id, affected_resources, severity
                            )
                            event["results"] = event_results
            
            # Process expiring futures contracts every tick
            futures_results = self.process_expiring_futures()
            if "error" not in futures_results:
                results["futures_processed"] = {
                    "settled": futures_results.get("settled", []),
                    "expired": futures_results.get("expired", []),
                    "error_count": len(futures_results.get("errors", []))
                }
                
                # Add events for significant futures settlements
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
            
            # Generate economy events (like price changes, shortages, etc.)
            legacy_economy_events = self._generate_economy_events(tick_count, regions_processed)
            results["events"].extend(legacy_economy_events)
            
            # Add the generated events to the main events list
            results["events"].extend(results["generated_events"])
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing economy tick: {str(e)}")
            results["error"] = str(e)
            return results
    
    def _create_market_modifiers_from_trades(self, region_id: int, 
                                          trade_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create market modifiers based on trade activity.
        
        Args:
            region_id: Region ID to analyze
            trade_events: List of trade events
            
        Returns:
            Dictionary of resource ID to price modifier
        """
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
                # Create a small modifier based on flow
                modifier = 1.0 - (net_flow * 0.01)
                # Clamp to reasonable range
                modifier = max(0.9, min(1.1, modifier))
                modifiers[str(resource_id)] = modifier
        
        return modifiers
    
    def _generate_economy_events(self, tick_count: int, 
                              regions_processed: set) -> List[Dict[str, Any]]:
        """Generate economy events based on current state.
        
        Args:
            tick_count: Current world tick count
            regions_processed: Set of regions that were processed
            
        Returns:
            List of economy events
        """
        events = []
        
        # Only generate events every few ticks to avoid spam
        if tick_count % 5 != 0:
            return events
            
        # Check for resource shortages in processed regions
        for region_id in regions_processed:
            resources = self.get_resources_by_region(region_id)
            
            for resource in resources:
                # Check for critically low resources
                if resource.amount < resource.minimum_viable_amount:
                    events.append({
                        "type": "resource_shortage",
                        "region_id": region_id,
                        "resource_id": resource.id,
                        "resource_name": resource.name,
                        "current_amount": resource.amount,
                        "severity": "critical" if resource.amount <= 0 else "warning",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        
        # In a real implementation, we could also generate:
        # - Price spike events when prices change dramatically
        # - Market opportunity events when there's a big price difference between regions
        # - Economic boom/bust events based on overall economic activity
        
        return events
    
    # Utility Methods
    
    def clear_cache(self) -> None:
        """Clear all service caches."""
        self.resource_service.clear_cache()
        self.trade_service.clear_cache()
        self.market_service.clear_cache()
        self.futures_service.clear_cache()
        logger.info("Economy Manager caches cleared")

    def simulate_economic_competition(self, region_ids: List[int]) -> Dict[str, Any]:
        """Simulate economic competition between regions.
        
        This method analyzes the economic metrics of multiple regions and simulates
        competition between them, resulting in economic advantages/disadvantages.
        
        Args:
            region_ids: List of region IDs to include in the competition
            
        Returns:
            Dictionary with competition results and events
        """
        if len(region_ids) < 2:
            return {"message": "At least two regions are required for competition simulation"}
        
        results = {
            "competitive_advantages": {},
            "market_shifts": {},
            "events": []
        }
        
        try:
            # Collect economic metrics for each region
            region_metrics = {}
            
            for region_id in region_ids:
                metrics = {
                    "price_index": self.calculate_price_index(region_id=region_id),
                    "markets": self.get_markets_by_region(region_id),
                    "resources": self.get_resources_by_region(region_id),
                    "trade_routes": self.get_trade_routes_by_region(region_id)
                }
                
                # Calculate resource diversity
                resource_types = set(r.resource_type for r in metrics["resources"])
                metrics["resource_diversity"] = len(resource_types)
                
                # Calculate market strength
                markets_count = len(metrics["markets"])
                avg_tax_rate = sum(m.tax_rate for m in metrics["markets"]) / max(markets_count, 1)
                metrics["market_strength"] = markets_count * (1 - avg_tax_rate)
                
                # Calculate trade network reach
                trade_partners = set()
                for route in metrics["trade_routes"]:
                    if route.origin_region_id == region_id:
                        trade_partners.add(route.destination_region_id)
                    else:
                        trade_partners.add(route.origin_region_id)
                metrics["trade_partners"] = len(trade_partners)
                
                region_metrics[region_id] = metrics
            
            # Determine competitive advantages
            for region_id, metrics in region_metrics.items():
                advantages = []
                disadvantages = []
                
                # Compare price index
                region_price_index = metrics["price_index"].get("average_index", 100)
                price_ranks = sorted([(r, m["price_index"].get("average_index", 100)) 
                                  for r, m in region_metrics.items()], key=lambda x: x[1])
                price_rank = next(i for i, (r, _) in enumerate(price_ranks) if r == region_id)
                
                if price_rank == 0:  # Lowest prices
                    advantages.append("lowest_prices")
                    results["events"].append({
                        "type": "economic_advantage",
                        "region_id": region_id,
                        "advantage": "lowest_prices",
                        "description": f"Region {region_id} has established a price advantage over competitors"
                    })
                elif price_rank == len(price_ranks) - 1:  # Highest prices
                    disadvantages.append("highest_prices")
                
                # Compare resource diversity
                diversity_ranks = sorted([(r, m["resource_diversity"]) 
                                      for r, m in region_metrics.items()], key=lambda x: x[1], reverse=True)
                diversity_rank = next(i for i, (r, _) in enumerate(diversity_ranks) if r == region_id)
                
                if diversity_rank == 0:  # Most diverse
                    advantages.append("resource_diverse")
                elif diversity_rank == len(diversity_ranks) - 1:  # Least diverse
                    disadvantages.append("resource_limited")
                
                # Compare trade networks
                trade_ranks = sorted([(r, m["trade_partners"]) 
                                  for r, m in region_metrics.items()], key=lambda x: x[1], reverse=True)
                trade_rank = next(i for i, (r, _) in enumerate(trade_ranks) if r == region_id)
                
                if trade_rank == 0:  # Most connected
                    advantages.append("trade_connected")
                elif trade_rank == len(trade_ranks) - 1:  # Least connected
                    disadvantages.append("trade_isolated")
                
                # Store results
                results["competitive_advantages"][str(region_id)] = {
                    "advantages": advantages,
                    "disadvantages": disadvantages
                }
                
                # Generate market shifts based on advantages/disadvantages
                market_shifts = {}
                for market in metrics["markets"]:
                    # Base price modifier
                    modifier = 1.0
                    
                    # Adjust based on advantages/disadvantages
                    if "lowest_prices" in advantages:
                        modifier *= 0.95  # 5% volume increase
                    if "highest_prices" in disadvantages:
                        modifier *= 0.9  # 10% volume decrease
                    if "trade_connected" in advantages:
                        modifier *= 1.05  # 5% volume increase
                    if "trade_isolated" in disadvantages:
                        modifier *= 0.95  # 5% volume decrease
                    
                    if modifier != 1.0:
                        market_shifts[str(market.id)] = modifier
                        
                        # Generate event for significant shifts
                        if abs(1 - modifier) >= 0.05:
                            direction = "increase" if modifier > 1 else "decrease"
                            results["events"].append({
                                "type": "market_shift",
                                "region_id": region_id,
                                "market_id": market.id,
                                "direction": direction,
                                "magnitude": abs(1 - modifier),
                                "description": f"Market {market.id} in region {region_id} experiences trade volume {direction}"
                            })
                
                results["market_shifts"][str(region_id)] = market_shifts
            
            return results
        except Exception as e:
            logger.error(f"Error simulating economic competition: {str(e)}")
            return {"error": str(e)}

    def process_economic_event(self, event_type: str, region_id: int, 
                               affected_resources: Optional[List[str]] = None,
                               severity: float = 1.0) -> Dict[str, Any]:
        """Process an economic event and apply its effects to resources."""
        return self.resource_service.process_economic_event(
            event_type, region_id, affected_resources, severity
        )

    def simulate_resource_consumption(self, region_id: int, 
                                      population: int, 
                                      consumption_factors: Dict[str, float] = None) -> Dict[str, Any]:
        """Simulate resource consumption by population and activities.
        
        Models how population consumes resources over time, generating
        shortage events when consumption exceeds available resources.
        
        Args:
            region_id: ID of the region
            population: Current population size
            consumption_factors: Optional dictionary of resource type to consumption multiplier
                             (defaults will be used if not provided)
        
        Returns:
            Dictionary with consumption results including shortages and events
        """
        return self.resource_service.simulate_resource_consumption(
            region_id, population, consumption_factors
        )

    def simulate_production_activities(self, region_id: int, 
                                       production_capacity: Dict[str, float] = None) -> Dict[str, Any]:
        """Simulate resource production from various activities.
        
        Models how settlements and natural processes generate resources over time,
        creating new resources when none exist of a particular type.
        
        Args:
            region_id: ID of the region
            production_capacity: Optional dictionary of resource type to production capacity
                               (defaults will be used if not provided)
        
        Returns:
            Dictionary with production results and events
        """
        return self.resource_service.simulate_production_activities(
            region_id, production_capacity
        )

    def generate_economic_events(self, region_id: int) -> List[Dict[str, Any]]:
        """Generate economic events based on current metrics.
        
        Analyzes economy metrics to generate appropriate events
        (booms, busts, etc.) for the region.
        
        Args:
            region_id: ID of the region to analyze
            
        Returns:
            List of economic events generated
        """
        try:
            # Get all relevant metrics
            price_index_data = self.calculate_price_index(region_id=region_id)
            resources = self.get_resources_by_region(region_id)
            markets = self.market_service.get_markets_by_region(region_id)
            
            # Initialize events list
            events = []
            
            # Check for price index anomalies
            price_index = price_index_data.get('price_index', 100)
            if price_index > 150:  # Significant inflation
                events.append({
                    "event_type": "bust",
                    "cause": "price_inflation",
                    "region_id": region_id,
                    "severity": min(1.0 + (price_index - 150) / 100, 3.0),  # Scale severity based on inflation
                    "affected_resources": [str(r.id) for r in resources],
                    "description": f"Economic bust due to extreme inflation in region {region_id}"
                })
            elif price_index < 60:  # Significant deflation
                events.append({
                    "event_type": "boom",
                    "cause": "price_deflation",
                    "region_id": region_id,
                    "severity": min(1.0 + (60 - price_index) / 50, 2.0),  # Scale severity based on deflation
                    "affected_resources": [str(r.id) for r in resources],
                    "description": f"Economic boom due to favorable prices in region {region_id}"
                })
            
            # Check for resource scarcity
            for resource in resources:
                if hasattr(resource, 'minimum_viable_amount') and resource.amount < resource.minimum_viable_amount:
                    resource_type = getattr(resource, 'type', 'general')
                    
                    # Food scarcity is more severe
                    if resource_type == 'food' and resource.amount <= 0:
                        events.append({
                            "event_type": "famine",
                            "cause": "food_scarcity",
                            "region_id": region_id,
                            "severity": min(2.0, resource.minimum_viable_amount / max(resource.amount, 0.1)),
                            "affected_resources": [str(resource.id)],
                            "description": f"Famine due to critical food shortage in region {region_id}"
                        })
                    # Other resource scarcity
                    elif resource.amount <= 0:
                        events.append({
                            "event_type": "bust",
                            "cause": f"{resource_type}_depletion",
                            "region_id": region_id,
                            "severity": 1.0,
                            "affected_resources": [str(resource.id)],
                            "description": f"Economic downturn due to {resource_type} depletion in region {region_id}"
                        })
            
            # Check for resource abundance
            for resource in resources:
                if hasattr(resource, 'minimum_viable_amount') and resource.minimum_viable_amount > 0:
                    # If we have 10x the minimum viable amount, consider it abundant
                    if resource.amount > resource.minimum_viable_amount * 10:
                        resource_type = getattr(resource, 'type', 'general')
                        events.append({
                            "event_type": "harvest" if resource_type == 'food' else "boom",
                            "cause": f"{resource_type}_abundance",
                            "region_id": region_id,
                            "severity": min(1.0 + (resource.amount / (resource.minimum_viable_amount * 10)), 2.0),
                            "affected_resources": [str(resource.id)],
                            "description": f"{'Bountiful harvest' if resource_type == 'food' else 'Economic boom'} due to {resource_type} abundance in region {region_id}"
                        })
            
            # Check market tax rates for potential events
            high_tax_markets = [m for m in markets if m.tax_rate > 0.25]  # 25% tax rate is high
            if high_tax_markets and len(high_tax_markets) > len(markets) / 2:  # More than half markets have high taxes
                # High taxes can cause economic slowdown
                events.append({
                    "event_type": "bust",
                    "cause": "high_taxation",
                    "region_id": region_id,
                    "severity": 1.0,
                    "affected_resources": [],  # Affects all resources
                    "description": f"Economic slowdown due to high taxation in region {region_id}"
                })
                
            # Add randomized events with low probability (10%)
            if len(events) == 0 and random.random() < 0.1:
                # Pick a random event type
                event_types = ["boom", "bust", "discovery", "disaster"]
                event_type = random.choice(event_types)
                
                # Create a random event
                events.append({
                    "event_type": event_type,
                    "cause": "random_fluctuation",
                    "region_id": region_id,
                    "severity": random.uniform(0.5, 1.5),
                    "affected_resources": [],  # Can be populated based on event type
                    "description": f"Random {event_type} event in region {region_id}"
                })
            
            return events
        
        except Exception as e:
            logger.error(f"Error generating economic events: {str(e)}")
            return []

    def process_population_change(self, region_id: int, 
                          previous_population: int, 
                          current_population: int) -> Dict[str, Any]:
        """Process population change effects on economy.
        
        Adjusts resource consumption and production based on population changes.
        
        Args:
            region_id: ID of the region with population change
            previous_population: Previous population count
            current_population: Current population count
            
        Returns:
            Dictionary with results of processing
        """
        try:
            if previous_population == current_population:
                return {"message": "No population change to process"}
            
            # Calculate change percentage
            if previous_population > 0:
                change_percentage = (current_population - previous_population) / previous_population
            else:
                change_percentage = 1.0  # 100% increase if previous was 0
            
            # Process resource impacts
            resource_results = self.resource_service.population_impact_on_resources(
                region_id, previous_population, current_population
            )
            
            # Process market impacts
            market_adjustments = {}
            events = []
            
            # Get markets in the region
            markets = self.get_markets_by_region(region_id)
            
            for market in markets:
                # Adjust trading volume based on population change
                # Population increase -> trading volume increase
                trading_volume = market.trading_volume or {}
                
                for resource_id, volume in trading_volume.items():
                    # Trading volume increases/decreases with population
                    # but not linearly (square root relationship)
                    adjustment_factor = 1.0 + (math.sqrt(abs(change_percentage)) * 
                                            (1 if change_percentage > 0 else -1))
                    
                    # Cap adjustments to reasonable values
                    adjustment_factor = max(0.5, min(adjustment_factor, 2.0))
                    
                    # Apply adjustment
                    new_volume = volume * adjustment_factor
                    trading_volume[resource_id] = new_volume
                    
                    # Record adjustment
                    if str(market.id) not in market_adjustments:
                        market_adjustments[str(market.id)] = {}
                    market_adjustments[str(market.id)][resource_id] = {
                        "previous_volume": volume,
                        "new_volume": new_volume,
                        "adjustment_factor": adjustment_factor
                    }
                
                # Update market with new trading volume
                market.trading_volume = trading_volume
                if self.db_session:
                    self.db_session.add(market)
                
                # Generate events for significant population changes
                if abs(change_percentage) > 0.2:  # More than 20% change
                    events.append({
                        "type": "market_volume_change",
                        "region_id": region_id,
                        "market_id": market.id,
                        "cause": "population_change",
                        "change_direction": "increase" if change_percentage > 0 else "decrease",
                        "change_magnitude": abs(change_percentage),
                        "description": f"Market volume {'increased' if change_percentage > 0 else 'decreased'} due to population change in region {region_id}"
                    })
            
            # Commit changes
            if self.db_session:
                self.db_session.commit()
            
            # Combine results
            result = {
                "region_id": region_id,
                "previous_population": previous_population,
                "current_population": current_population,
                "population_change": current_population - previous_population,
                "change_percentage": change_percentage,
                "resource_results": resource_results,
                "market_adjustments": market_adjustments,
                "events": events + resource_results.get("events", [])
            }
            
            return result
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error processing population change: {str(e)}")
            return {"error": str(e)}

    def generate_economic_forecast(self, region_id: int, forecast_periods: int = 3) -> Dict[str, Any]:
        """Generate an economic forecast for the specified region.
        
        Analyzes current economic trends and projects future economic conditions.
        
        Args:
            region_id: ID of the region to analyze
            forecast_periods: Number of time periods to forecast ahead
            
        Returns:
            Dictionary with economic forecast and confidence levels
        """
        try:
            # Collect current economic data
            price_index = self.calculate_price_index(region_id=region_id)
            resources = self.get_resources_by_region(region_id)
            markets = self.get_markets_by_region(region_id)
            
            # Initialize forecast result
            forecast = {
                "region_id": region_id,
                "base_metrics": {
                    "price_index": price_index.get("price_index", 100),
                    "resource_count": len(resources),
                    "market_count": len(markets),
                    "total_trading_volume": sum(sum(m.trading_volume.values()) if m.trading_volume else 0 for m in markets),
                    "average_tax_rate": sum(m.tax_rate for m in markets) / max(len(markets), 1),
                    "resource_scarcity": sum(1 for r in resources if hasattr(r, "minimum_viable_amount") and 
                                         r.amount < r.minimum_viable_amount)
                },
                "forecast_periods": forecast_periods,
                "forecasts": [],
                "risk_factors": [],
                "growth_factors": [],
                "confidence_level": 0
            }
            
            # Identify risk factors
            if forecast["base_metrics"]["price_index"] > 140:
                forecast["risk_factors"].append({
                    "factor": "high_inflation",
                    "severity": min((forecast["base_metrics"]["price_index"] - 140) / 20, 5),
                    "description": "High inflation could lead to reduced purchasing power and economic instability"
                })
                
            if forecast["base_metrics"]["price_index"] < 70:
                forecast["risk_factors"].append({
                    "factor": "deflation",
                    "severity": min((70 - forecast["base_metrics"]["price_index"]) / 15, 5),
                    "description": "Deflation may lead to reduced economic activity and delayed spending"
                })
                
            resource_scarcity_percentage = forecast["base_metrics"]["resource_scarcity"] / max(len(resources), 1)
            if resource_scarcity_percentage > 0.3:  # More than 30% of resources scarce
                forecast["risk_factors"].append({
                    "factor": "resource_scarcity",
                    "severity": min(resource_scarcity_percentage * 10, 5),
                    "description": "Resource scarcity could constrain economic growth and increase prices"
                })
                
            if forecast["base_metrics"]["average_tax_rate"] > 0.25:  # High tax rates
                forecast["risk_factors"].append({
                    "factor": "high_taxation",
                    "severity": min((forecast["base_metrics"]["average_tax_rate"] - 0.25) * 10, 5),
                    "description": "High tax rates may reduce economic activity and investment"
                })
                
            # Identify growth factors
            if 80 <= forecast["base_metrics"]["price_index"] <= 120:  # Stable prices
                forecast["growth_factors"].append({
                    "factor": "price_stability",
                    "strength": 3,
                    "description": "Stable prices create a favorable environment for trade and investment"
                })
                
            if resource_scarcity_percentage < 0.1:  # Good resource availability
                forecast["growth_factors"].append({
                    "factor": "resource_abundance",
                    "strength": min((1 - resource_scarcity_percentage) * 5, 5),
                    "description": "Abundant resources support economic growth and stability"
                })
                
            if forecast["base_metrics"]["average_tax_rate"] < 0.15:  # Low tax rates
                forecast["growth_factors"].append({
                    "factor": "favorable_taxation",
                    "strength": min((0.15 - forecast["base_metrics"]["average_tax_rate"]) * 20, 5),
                    "description": "Lower tax rates encourage economic activity and investment"
                })
                
            # Calculate confidence level based on data quality
            # Higher confidence with more markets, resources, and stable metrics
            confidence_factors = [
                min(len(markets) / 5, 1),  # More markets = better data
                min(len(resources) / 10, 1),  # More resources = better data
                0.8 if 80 <= forecast["base_metrics"]["price_index"] <= 120 else 0.5,  # Stable prices = more predictable
                0.9 if len(forecast["risk_factors"]) <= 1 else 0.7  # Fewer risks = more confidence
            ]
            forecast["confidence_level"] = sum(confidence_factors) / len(confidence_factors) * 100
            
            # Generate forecasts for each period
            current_price_index = forecast["base_metrics"]["price_index"]
            
            for period in range(1, forecast_periods + 1):
                # Calculate net impact from risk and growth factors
                risk_impact = sum(risk["severity"] / 10 for risk in forecast["risk_factors"])
                growth_impact = sum(growth["strength"] / 10 for growth in forecast["growth_factors"])
                net_impact = growth_impact - risk_impact
                
                # Add some randomness to each period (less certain as we go further)
                randomness = random.uniform(-0.05, 0.05) * period
                
                # Project price index change
                price_index_change = (net_impact + randomness) * 10  # Scale to percentage
                new_price_index = current_price_index * (1 + price_index_change / 100)
                
                # Determine economic direction
                if new_price_index > current_price_index * 1.1:
                    direction = "growth"
                elif new_price_index < current_price_index * 0.9:
                    direction = "contraction"
                else:
                    direction = "stable"
                
                # Generate forecast for this period
                period_forecast = {
                    "period": period,
                    "projected_price_index": new_price_index,
                    "price_index_change": price_index_change,
                    "direction": direction,
                    "confidence": max(20, forecast["confidence_level"] - (period * 15)),  # Confidence decreases with time
                    "description": f"Period {period} forecast: Economic {direction} with price index projected at {new_price_index:.1f}"
                }
                
                forecast["forecasts"].append(period_forecast)
                
                # Update current price index for next period
                current_price_index = new_price_index
                
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating economic forecast: {str(e)}")
            return {"error": str(e)} 