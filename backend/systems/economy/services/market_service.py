"""
Market service for economy system.
Handles pricing, supply/demand, and market operations.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import random
from sqlalchemy.orm import Session

from backend.systems.economy.models import Market, MarketData, Resource
from backend.systems.economy.services.resource_service import ResourceService
from app.core.logging import logger

class MarketService:
    """Service for managing markets and pricing in the economy system."""
    
    def __init__(self, db_session: Session = None, resource_service: Optional[ResourceService] = None):
        """Initialize the market service.
        
        Args:
            db_session: SQLAlchemy session for database operations
            resource_service: Optional resource service
        """
        self.db_session = db_session
        self.resource_service = resource_service or ResourceService(db_session)
        self._market_cache = {}
        
        # Base price modifiers for different market types
        self._market_type_modifiers = {
            "general": 1.0,
            "specialized": 1.2,
            "black_market": 1.5,
            "festival": 0.8,
            "harbor": 0.9,
        }
    
    def get_market(self, market_id: Union[str, int]) -> Optional[Market]:
        """Get a market by ID.
        
        Args:
            market_id: ID of the market
            
        Returns:
            Market object if found, None otherwise
        """
        try:
            if isinstance(market_id, str) and market_id.isdigit():
                market_id = int(market_id)
                
            # Try cache first
            if market_id in self._market_cache:
                return self._market_cache[market_id]
                
            # Get from database
            if self.db_session:
                market = self.db_session.query(Market).filter(Market.id == market_id).first()
                if market:
                    self._market_cache[market_id] = market
                return market
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting market: {str(e)}")
            return None
    
    def get_markets_by_region(self, region_id: int) -> List[Market]:
        """Get all markets in a region.
        
        Args:
            region_id: ID of the region
            
        Returns:
            List of markets in the region
        """
        try:
            if not self.db_session:
                return []
                
            return self.db_session.query(Market).filter(Market.region_id == region_id).all()
            
        except Exception as e:
            logger.error(f"Error getting markets by region: {str(e)}")
            return []
    
    def create_market(self, market_data: Union[Dict[str, Any], MarketData]) -> Optional[Market]:
        """Create a new market.
        
        Args:
            market_data: Market data or dictionary
            
        Returns:
            Created market if successful, None otherwise
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return None
                
            if isinstance(market_data, dict):
                market_data_obj = MarketData(**market_data)
            else:
                market_data_obj = market_data
                
            # Validate market type is valid
            if market_data_obj.market_type not in self._market_type_modifiers:
                logger.warning(f"Invalid market type: {market_data_obj.market_type}, defaulting to 'general'")
                market_data_obj.market_type = "general"
                
            # Create market
            market = Market.from_data_model(market_data_obj)
            self.db_session.add(market)
            self.db_session.commit()
            
            # Update cache
            self._market_cache[market.id] = market
            
            return market
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error creating market: {str(e)}")
            return None
    
    def update_market(self, market_id: int, updates: Dict[str, Any]) -> Optional[Market]:
        """Update an existing market.
        
        Args:
            market_id: ID of the market to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated market if successful, None otherwise
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return None
                
            market = self.get_market(market_id)
            if not market:
                logger.error(f"Market with ID {market_id} not found")
                return None
                
            # Update fields
            for key, value in updates.items():
                if hasattr(market, key):
                    setattr(market, key, value)
            
            market.updated_at = datetime.utcnow()
            self.db_session.commit()
            
            # Update cache
            self._market_cache[market.id] = market
            
            return market
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error updating market: {str(e)}")
            return None
    
    def delete_market(self, market_id: int) -> bool:
        """Delete a market.
        
        Args:
            market_id: ID of the market to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return False
                
            market = self.get_market(market_id)
            if not market:
                logger.error(f"Market with ID {market_id} not found")
                return False
                
            self.db_session.delete(market)
            self.db_session.commit()
            
            # Remove from cache
            if market_id in self._market_cache:
                del self._market_cache[market_id]
                
            return True
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error deleting market: {str(e)}")
            return False
    
    def calculate_price(self, resource_id: int, market_id: int, 
                       quantity: float = 1.0) -> Tuple[float, Dict[str, Any]]:
        """Calculate the price for a resource in a specific market.
        
        Args:
            resource_id: ID of the resource
            market_id: ID of the market
            quantity: Quantity of the resource
            
        Returns:
            Tuple of (price, price_factors)
        """
        try:
            resource = self.resource_service.get_resource(resource_id)
            market = self.get_market(market_id)
            
            if not resource or not market:
                return 0.0, {"error": "Resource or market not found"}
                
            # Start with base price
            base_price = resource.price * quantity
            
            # Apply market type modifier
            market_type_modifier = self._market_type_modifiers.get(market.market_type, 1.0)
            
            # Apply specific resource price modifiers from the market
            resource_modifier = market.price_modifiers.get(str(resource_id), 1.0)
            
            # Apply supply/demand dynamics
            supply_demand_modifier = self._calculate_supply_demand_modifier(resource, market)
            
            # Apply random fluctuation (market volatility)
            volatility = market.volatility or 0.05  # Default 5% volatility
            random_factor = 1.0 + (random.random() * volatility * 2 - volatility)
            
            # Calculate final price
            final_price = base_price * market_type_modifier * resource_modifier * supply_demand_modifier * random_factor
            
            # Record price factors for debugging/explanation
            price_factors = {
                "base_price": base_price,
                "market_type_modifier": market_type_modifier,
                "resource_modifier": resource_modifier,
                "supply_demand_modifier": supply_demand_modifier,
                "random_factor": random_factor,
                "final_price": final_price
            }
            
            return final_price, price_factors
            
        except Exception as e:
            logger.error(f"Error calculating price: {str(e)}")
            return 0.0, {"error": str(e)}
    
    def _calculate_supply_demand_modifier(self, resource: Resource, market: Market) -> float:
        """Calculate supply/demand modifier for a resource in a market.
        
        Args:
            resource: Resource object
            market: Market object
            
        Returns:
            Supply/demand modifier
        """
        try:
            # Get all resources of this type in the region
            region_resources = self.resource_service.get_resources_by_region(market.region_id)
            
            # Filter to this resource type
            type_resources = [r for r in region_resources if r.type == resource.type]
            
            if not type_resources:
                return 1.5  # Scarcity premium if no similar resources
                
            # Calculate total amount of this resource type
            total_amount = sum(r.amount for r in type_resources)
            
            # Get supply threshold from market or use default
            supply_threshold = market.supply_thresholds.get(resource.type, 100)
            
            if total_amount <= 0:
                return 2.0  # High premium for depleted resources
                
            # More supply = lower prices, less supply = higher prices
            # Non-linear relationship with diminishing returns
            import math
            supply_factor = math.exp(-total_amount / supply_threshold) + 0.5
            
            # Clamp to reasonable range
            return max(0.5, min(3.0, supply_factor))
            
        except Exception as e:
            logger.error(f"Error calculating supply/demand modifier: {str(e)}")
            return 1.0  # Neutral modifier on error
    
    def update_market_conditions(self, region_id: int, 
                               event_modifiers: Optional[Dict[str, Any]] = None) -> List[Market]:
        """Update market conditions based on events, time, etc.
        
        Args:
            region_id: ID of the region to update markets for
            event_modifiers: Optional modifiers from events
            
        Returns:
            List of updated markets
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return []
                
            markets = self.get_markets_by_region(region_id)
            updated_markets = []
            
            for market in markets:
                # Apply general market drift (slight randomization over time)
                price_modifiers = market.price_modifiers or {}
                
                for resource_id in price_modifiers:
                    # Small random drift in prices
                    drift = (random.random() * 0.1) - 0.05  # -5% to +5%
                    price_modifiers[resource_id] = max(0.5, min(2.0, price_modifiers[resource_id] + drift))
                
                # Apply event modifiers if any
                if event_modifiers:
                    for resource_id, modifier in event_modifiers.items():
                        if resource_id in price_modifiers:
                            price_modifiers[resource_id] *= modifier
                            # Clamp to reasonable range
                            price_modifiers[resource_id] = max(0.1, min(5.0, price_modifiers[resource_id]))
                
                # Update market with new price modifiers
                market.price_modifiers = price_modifiers
                market.updated_at = datetime.utcnow()
                
                # Commit updates
                self.db_session.commit()
                
                # Update cache
                self._market_cache[market.id] = market
                
                updated_markets.append(market)
            
            return updated_markets
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error updating market conditions: {str(e)}")
            return []
    
    def get_resource_price_trends(self, resource_id: int, 
                                region_id: Optional[int] = None) -> Dict[str, Any]:
        """Get price trends for a resource across markets.
        
        Args:
            resource_id: ID of the resource
            region_id: Optional region ID to filter markets
            
        Returns:
            Dictionary with price trend information
        """
        try:
            resource = self.resource_service.get_resource(resource_id)
            if not resource:
                return {"error": f"Resource with ID {resource_id} not found"}
                
            if region_id:
                markets = self.get_markets_by_region(region_id)
            else:
                # Get all markets (in a real implementation, would need pagination)
                markets = self.db_session.query(Market).limit(20).all()
                
            price_data = []
            
            for market in markets:
                price, _ = self.calculate_price(resource_id, market.id)
                price_data.append({
                    "market_id": market.id,
                    "market_name": market.name,
                    "region_id": market.region_id,
                    "market_type": market.market_type,
                    "price": price
                })
            
            # Calculate stats
            if price_data:
                prices = [item["price"] for item in price_data]
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                price_range = max_price - min_price
            else:
                avg_price = 0
                min_price = 0
                max_price = 0
                price_range = 0
                
            return {
                "resource_id": resource_id,
                "resource_name": resource.name,
                "base_price": resource.price,
                "markets": price_data,
                "stats": {
                    "average_price": avg_price,
                    "min_price": min_price,
                    "max_price": max_price,
                    "price_range": price_range,
                    "market_count": len(price_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting resource price trends: {str(e)}")
            return {"error": str(e)}
    
    def clear_cache(self) -> None:
        """Clear the market cache."""
        self._market_cache = {}

    def set_tax_rate(self, market_id: int, tax_rate: float) -> Optional[Market]:
        """Set tax rate for a market.
        
        Args:
            market_id: ID of the market
            tax_rate: New tax rate (0.0 - 1.0)
            
        Returns:
            Updated market if successful, None otherwise
        """
        try:
            # Validate tax rate
            if tax_rate < 0.0 or tax_rate > 1.0:
                logger.error(f"Invalid tax rate: {tax_rate}. Must be between 0.0 and 1.0")
                return None
            
            market = self.get_market(market_id)
            if not market:
                logger.error(f"Market with ID {market_id} not found")
                return None
            
            market.tax_rate = tax_rate
            market.updated_at = datetime.utcnow()
            
            if self.db_session:
                self.db_session.commit()
            
            # Update cache
            self._market_cache[market.id] = market
            
            return market
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error setting tax rate: {str(e)}")
            return None

    def get_tax_rate(self, market_id: int) -> Optional[float]:
        """Get tax rate for a market.
        
        Args:
            market_id: ID of the market
            
        Returns:
            Tax rate if market found, None otherwise
        """
        market = self.get_market(market_id)
        if not market:
            logger.error(f"Market with ID {market_id} not found")
            return None
        
        return market.tax_rate

    def calculate_tax_revenue(self, market_id: int, time_period: str = "daily") -> Dict[str, Any]:
        """Calculate tax revenue for a market.
        
        Args:
            market_id: ID of the market
            time_period: Time period for calculation ('daily', 'weekly', 'monthly')
            
        Returns:
            Dictionary with tax revenue calculation results
        """
        try:
            market = self.get_market(market_id)
            if not market:
                logger.error(f"Market with ID {market_id} not found")
                return {"error": "Market not found"}
            
            # Get trading volume for the market
            trading_volume = market.trading_volume or {}
            
            # Period multipliers
            period_multipliers = {
                "daily": 1.0,
                "weekly": 7.0,
                "monthly": 30.0
            }
            
            multiplier = period_multipliers.get(time_period, 1.0)
            
            # Calculate tax revenue based on trading volume and tax rate
            total_volume = sum(trading_volume.values()) * multiplier
            tax_revenue = total_volume * market.tax_rate
            
            return {
                "market_id": market_id,
                "market_name": market.name,
                "tax_rate": market.tax_rate,
                "time_period": time_period,
                "total_trading_volume": total_volume,
                "tax_revenue": tax_revenue,
                "revenue_by_resource": {
                    resource_id: volume * multiplier * market.tax_rate
                    for resource_id, volume in trading_volume.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating tax revenue: {str(e)}")
            return {"error": str(e)}

    def calculate_price_index(self, market_id: Optional[int] = None, 
                           region_id: Optional[int] = None) -> Dict[str, Any]:
        """Calculate price index for a market or region.
        
        The price index is a weighted average of prices for all resources
        in a market or region, providing an economic indicator.
        
        Args:
            market_id: Optional ID of a specific market
            region_id: Optional ID of a region (all markets in region are included)
            
        Returns:
            Dictionary with price index calculation results
        """
        try:
            markets = []
            
            if market_id:
                # Single market calculation
                market = self.get_market(market_id)
                if market:
                    markets = [market]
            elif region_id:
                # All markets in a region
                markets = self.get_markets_by_region(region_id)
            else:
                logger.error("Must provide either market_id or region_id for price index calculation")
                return {"error": "Missing market_id or region_id"}
                
            if not markets:
                logger.error(f"No markets found for calculation")
                return {"error": "No markets found"}
                
            # Calculate price index
            total_weight = 0.0
            weighted_prices = 0.0
            resource_prices = {}
            market_indices = {}
            
            for market in markets:
                # Get all resources with price modifiers in this market
                resource_ids = list(market.price_modifiers.keys()) if market.price_modifiers else []
                market_total_weight = 0.0
                market_weighted_prices = 0.0
                
                for resource_id in resource_ids:
                    resource = self.resource_service.get_resource(resource_id)
                    if not resource:
                        continue
                        
                    # Get base price from resource or default to 1.0
                    base_price = getattr(resource, 'base_price', 1.0)
                    
                    # Get price modifier from market
                    modifier = market.get_price_modifier(resource_id)
                    
                    # Calculate final price
                    final_price = base_price * modifier
                    
                    # Get trading volume as weight
                    weight = market.trading_volume.get(resource_id, 1.0) if market.trading_volume else 1.0
                    
                    # Add to weighted average calculation
                    weighted_prices += final_price * weight
                    total_weight += weight
                    
                    # Add to market-specific calculation
                    market_weighted_prices += final_price * weight
                    market_total_weight += weight
                    
                    # Store resource price
                    if resource_id not in resource_prices:
                        resource_prices[resource_id] = []
                    resource_prices[resource_id].append({
                        'market_id': market.id,
                        'price': final_price,
                        'volume': weight
                    })
                    
                # Calculate market-specific price index
                if market_total_weight > 0:
                    market_index = market_weighted_prices / market_total_weight
                else:
                    market_index = 0.0
                    
                market_indices[market.id] = {
                    'name': market.name,
                    'price_index': market_index,
                    'trading_volume': market_total_weight
                }
                
            # Calculate overall price index
            if total_weight > 0:
                price_index = weighted_prices / total_weight
            else:
                price_index = 0.0
                
            # Prepare result
            result = {
                'price_index': price_index,
                'total_trading_volume': total_weight,
                'market_indices': market_indices,
                'resource_count': len(resource_prices),
                'calculation_time': datetime.utcnow().isoformat()
            }
            
            # Add region info if applicable
            if region_id:
                result['region_id'] = region_id
                
            return result
            
        except Exception as e:
            logger.error(f"Error calculating price index: {str(e)}")
            return {"error": str(e)} 