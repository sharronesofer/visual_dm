"""
Trade service for economy system.
Handles trade routes, transactions, and resource flow between regions.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import random
from sqlalchemy.orm import Session

from backend.systems.economy.models import TradeRoute, TradeRouteData, Resource
from backend.systems.economy.services.resource_service import ResourceService
from app.core.logging import logger

class TradeService:
    """Service for managing trade routes and transactions in the economy system."""
    
    def __init__(self, db_session: Session = None, resource_service: Optional[ResourceService] = None):
        """Initialize the trade service.
        
        Args:
            db_session: SQLAlchemy session for database operations
            resource_service: Optional resource service
        """
        self.db_session = db_session
        self.resource_service = resource_service or ResourceService(db_session)
        self._trade_route_cache = {}
    
    def get_trade_route(self, route_id: Union[str, int]) -> Optional[TradeRoute]:
        """Get a trade route by ID.
        
        Args:
            route_id: ID of the trade route
            
        Returns:
            TradeRoute object if found, None otherwise
        """
        try:
            if isinstance(route_id, str) and route_id.isdigit():
                route_id = int(route_id)
                
            # Try cache first
            if route_id in self._trade_route_cache:
                return self._trade_route_cache[route_id]
                
            # Get from database
            if self.db_session:
                route = self.db_session.query(TradeRoute).filter(TradeRoute.id == route_id).first()
                if route:
                    self._trade_route_cache[route_id] = route
                return route
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting trade route: {str(e)}")
            return None
    
    def get_trade_routes_by_region(self, region_id: int, as_origin: bool = True, 
                                  as_destination: bool = True) -> List[TradeRoute]:
        """Get all trade routes for a region.
        
        Args:
            region_id: ID of the region
            as_origin: Include routes where region is the origin
            as_destination: Include routes where region is the destination
            
        Returns:
            List of trade routes for the region
        """
        try:
            if not self.db_session:
                return []
                
            routes = []
            
            if as_origin:
                origin_routes = (self.db_session.query(TradeRoute)
                                .filter(TradeRoute.origin_region_id == region_id)
                                .all())
                routes.extend(origin_routes)
                
            if as_destination:
                dest_routes = (self.db_session.query(TradeRoute)
                              .filter(TradeRoute.destination_region_id == region_id)
                              .all())
                routes.extend(dest_routes)
                
            # Remove duplicates
            unique_routes = {route.id: route for route in routes}
            
            return list(unique_routes.values())
            
        except Exception as e:
            logger.error(f"Error getting trade routes by region: {str(e)}")
            return []
    
    def create_trade_route(self, route_data: Union[Dict[str, Any], TradeRouteData]) -> Optional[TradeRoute]:
        """Create a new trade route.
        
        Args:
            route_data: Trade route data or dictionary
            
        Returns:
            Created trade route if successful, None otherwise
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return None
                
            if isinstance(route_data, dict):
                route_data_obj = TradeRouteData(**route_data)
            else:
                route_data_obj = route_data
                
            # Validate regions exist (in a real implementation)
            # For now we just check they're not the same
            if route_data_obj.origin_region_id == route_data_obj.destination_region_id:
                logger.error("Origin and destination regions cannot be the same")
                return None
                
            # Create route
            route = TradeRoute.from_data_model(route_data_obj)
            self.db_session.add(route)
            self.db_session.commit()
            
            # Update cache
            self._trade_route_cache[route.id] = route
            
            return route
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error creating trade route: {str(e)}")
            return None
    
    def update_trade_route(self, route_id: int, updates: Dict[str, Any]) -> Optional[TradeRoute]:
        """Update an existing trade route.
        
        Args:
            route_id: ID of the trade route to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated trade route if successful, None otherwise
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return None
                
            route = self.get_trade_route(route_id)
            if not route:
                logger.error(f"Trade route with ID {route_id} not found")
                return None
                
            # Update fields
            for key, value in updates.items():
                if hasattr(route, key):
                    setattr(route, key, value)
            
            route.updated_at = datetime.utcnow()
            self.db_session.commit()
            
            # Update cache
            self._trade_route_cache[route.id] = route
            
            return route
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error updating trade route: {str(e)}")
            return None
    
    def delete_trade_route(self, route_id: int) -> bool:
        """Delete a trade route.
        
        Args:
            route_id: ID of the trade route to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return False
                
            route = self.get_trade_route(route_id)
            if not route:
                logger.error(f"Trade route with ID {route_id} not found")
                return False
                
            self.db_session.delete(route)
            self.db_session.commit()
            
            # Remove from cache
            if route_id in self._trade_route_cache:
                del self._trade_route_cache[route_id]
                
            return True
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error deleting trade route: {str(e)}")
            return False
    
    def process_trade_routes(self, tick_count: int = 1) -> Tuple[int, List[Dict[str, Any]]]:
        """Process all active trade routes for resource transfers.
        
        This is typically called during a world tick to simulate trade activity.
        
        Args:
            tick_count: Number of ticks to process
            
        Returns:
            Tuple of (success_count, trade_events)
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return 0, []
                
            # Get all active trade routes
            active_routes = (self.db_session.query(TradeRoute)
                           .filter(TradeRoute.is_active == True)
                           .all())
            
            if not active_routes:
                return 0, []
                
            success_count = 0
            trade_events = []
            
            for route in active_routes:
                # Only process if it meets frequency requirements
                if tick_count % route.frequency_ticks != 0:
                    continue
                    
                # Determine resources to trade based on trade configuration
                resources_to_trade = self._determine_trade_resources(route)
                
                for resource_id, amount in resources_to_trade.items():
                    # Adjust for stability factor (prevents identical trades every time)
                    adjusted_amount = amount * (0.8 + (random.random() * 0.4))
                    
                    # Execute the transfer
                    success, message = self.resource_service.transfer_resource(
                        source_region_id=route.origin_region_id,
                        dest_region_id=route.destination_region_id,
                        resource_id=resource_id,
                        amount=adjusted_amount
                    )
                    
                    if success:
                        success_count += 1
                        
                        # Record the event for history/events system
                        trade_events.append({
                            "type": "trade",
                            "trade_route_id": route.id,
                            "origin_region_id": route.origin_region_id,
                            "destination_region_id": route.destination_region_id,
                            "resource_id": resource_id,
                            "amount": adjusted_amount,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    else:
                        logger.warning(f"Trade failed on route {route.id}: {message}")
                        
            return success_count, trade_events
            
        except Exception as e:
            logger.error(f"Error processing trade routes: {str(e)}")
            return 0, []
    
    def _determine_trade_resources(self, route: TradeRoute) -> Dict[int, float]:
        """Determine which resources to trade and in what quantities.
        
        Args:
            route: Trade route to analyze
            
        Returns:
            Dictionary mapping resource IDs to amounts
        """
        resources_to_trade = {}
        
        # If explicit resource mapping is defined in route, use that
        if route.resource_mapping and isinstance(route.resource_mapping, dict):
            return route.resource_mapping
            
        # Otherwise use a more dynamic approach based on available resources
        origin_resources = self.resource_service.get_resources_by_region(route.origin_region_id)
        
        # Filter for tradeable resources with sufficient quantity
        for resource in origin_resources:
            # Skip resources with insufficient quantity
            if resource.amount <= route.min_resource_threshold:
                continue
                
            # Determine an appropriate amount to trade
            base_amount = min(
                resource.amount * route.max_resource_percent,
                route.max_resource_amount
            )
            
            if base_amount <= 0:
                continue
                
            resources_to_trade[resource.id] = base_amount
            
        return resources_to_trade
    
    def clear_cache(self) -> None:
        """Clear the trade route cache."""
        self._trade_route_cache = {} 