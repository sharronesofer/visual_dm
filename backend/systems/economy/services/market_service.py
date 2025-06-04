"""
Market Service - Functionality for managing markets and pricing.

This service manages market operations, pricing calculations, and market dynamics.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from sqlalchemy.orm import Session

# Infrastructure layer - SQLAlchemy models for database operations
from backend.infrastructure.database.economy.market_models import Market
# Business layer - Pydantic models for business logic
from backend.systems.economy.models.market import MarketData

logger = logging.getLogger(__name__)

class MarketService:
    """Service for managing markets and pricing operations."""
    
    def __init__(self, db_session: Session = None, resource_service=None):
        """Initialize the market service.
        
        Args:
            db_session: SQLAlchemy session for database operations
            resource_service: ResourceService instance for resource operations
        """
        self.db_session = db_session
        self.resource_service = resource_service
        logger.info("MarketService initialized")
    
    def get_market(self, market_id: Union[str, int]) -> Optional[Market]:
        """Get a market by ID.
        
        Args:
            market_id: Market ID to retrieve
            
        Returns:
            Market instance or None if not found
        """
        try:
            if self.db_session:
                return self.db_session.query(Market).filter(Market.id == market_id).first()
            else:
                # Mock implementation for testing
                return Market(
                    id=int(market_id) if str(market_id).isdigit() else 1,
                    name=f"Market {market_id}",
                    region_id=1,
                    market_type="general"
                )
        except Exception as e:
            logger.error(f"Error getting market {market_id}: {str(e)}")
            return None
    
    def get_markets_by_region(self, region_id: int) -> List[Market]:
        """Get all markets in a region.
        
        Args:
            region_id: Region ID to search
            
        Returns:
            List of Market instances
        """
        try:
            if self.db_session:
                return self.db_session.query(Market).filter(Market.region_id == region_id).all()
            else:
                # Mock implementation for testing
                return [
                    Market(
                        id=1,
                        name=f"Market in Region {region_id}",
                        region_id=region_id,
                        market_type="general"
                    )
                ]
        except Exception as e:
            logger.error(f"Error getting markets for region {region_id}: {str(e)}")
            return []
    
    def create_market(self, market_data: Union[Dict[str, Any], MarketData]) -> Optional[Market]:
        """Create a new market.
        
        Args:
            market_data: Market data to create
            
        Returns:
            Created Market instance or None if failed
        """
        try:
            if isinstance(market_data, dict):
                market_data = MarketData(**market_data)
            
            if self.db_session:
                # Create market directly from the business data
                market = Market(
                    name=market_data.name,
                    region_id=int(market_data.region_id) if market_data.region_id else None,
                    market_type=market_data.market_type,
                    price_modifiers=market_data.price_modifiers,
                    supply_demand=market_data.supply_demand,
                    trading_volume=market_data.trading_volume,
                    tax_rate=market_data.tax_rate,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    market_metadata=market_data.metadata
                )
                self.db_session.add(market)
                self.db_session.commit()
                return market
            else:
                # Mock implementation for testing
                return Market(
                    id=1,
                    name=market_data.name,
                    region_id=int(market_data.region_id) if market_data.region_id else 1,
                    market_type=market_data.market_type
                )
        except Exception as e:
            logger.error(f"Error creating market: {str(e)}")
            return None
    
    def update_market(self, market_id: int, updates: Dict[str, Any]) -> Optional[Market]:
        """Update an existing market.
        
        Args:
            market_id: Market ID to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated Market instance or None if failed
        """
        try:
            market = self.get_market(market_id)
            if market:
                for key, value in updates.items():
                    if hasattr(market, key):
                        setattr(market, key, value)
                
                if self.db_session:
                    self.db_session.commit()
                
                return market
            return None
        except Exception as e:
            logger.error(f"Error updating market {market_id}: {str(e)}")
            return None
    
    def delete_market(self, market_id: int) -> bool:
        """Delete a market.
        
        Args:
            market_id: Market ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.db_session:
                market = self.get_market(market_id)
                if market:
                    self.db_session.delete(market)
                    self.db_session.commit()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting market {market_id}: {str(e)}")
            return False
    
    def calculate_price(self, resource_id: int, market_id: int, quantity: float = 1.0) -> Tuple[float, Dict[str, Any]]:
        """Calculate the price for a resource in a market.
        
        Args:
            resource_id: Resource ID
            market_id: Market ID
            quantity: Quantity to price
            
        Returns:
            Tuple of (price, calculation_details)
        """
        try:
            market = self.get_market(market_id)
            if not market:
                return 0.0, {"error": "Market not found"}
            
            # Get base price from resource
            base_price = 10.0  # Default base price
            if self.resource_service:
                resource = self.resource_service.get_resource(resource_id)
                if resource and hasattr(resource, 'base_price'):
                    base_price = resource.base_price
            
            # Apply market modifiers
            price_modifier = market.get_price_modifier(str(resource_id))
            final_price = base_price * price_modifier * quantity
            
            calculation_details = {
                "base_price": base_price,
                "price_modifier": price_modifier,
                "quantity": quantity,
                "final_price": final_price,
                "market_id": market_id,
                "resource_id": resource_id
            }
            
            return final_price, calculation_details
            
        except Exception as e:
            logger.error(f"Error calculating price for resource {resource_id} in market {market_id}: {str(e)}")
            return 0.0, {"error": str(e)}
    
    def update_market_conditions(self, region_id: int, event_modifiers: Optional[Dict[str, Any]] = None) -> List[Market]:
        """Update market conditions based on events, time, etc.
        
        Args:
            region_id: Region ID to update
            event_modifiers: Optional event-based modifiers
            
        Returns:
            List of updated Market instances
        """
        try:
            markets = self.get_markets_by_region(region_id)
            updated_markets = []
            
            for market in markets:
                if event_modifiers:
                    # Apply event modifiers
                    for resource_id, modifier in event_modifiers.items():
                        market.set_price_modifier(resource_id, modifier)
                
                # Apply time-based changes (simplified)
                # In a real implementation, this would be more sophisticated
                
                if self.db_session:
                    self.db_session.commit()
                
                updated_markets.append(market)
            
            return updated_markets
            
        except Exception as e:
            logger.error(f"Error updating market conditions for region {region_id}: {str(e)}")
            return []
    
    def get_resource_price_trends(self, resource_id: int, region_id: Optional[int] = None) -> Dict[str, Any]:
        """Get price trends for a resource across markets.
        
        Args:
            resource_id: Resource ID
            region_id: Optional region ID to filter
            
        Returns:
            Dictionary with price trend data
        """
        try:
            if region_id:
                markets = self.get_markets_by_region(region_id)
            else:
                # Would need to get all markets - simplified for now
                markets = []
            
            trends = {
                "resource_id": resource_id,
                "region_id": region_id,
                "markets": [],
                "average_price": 0.0,
                "price_range": {"min": 0.0, "max": 0.0},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            prices = []
            for market in markets:
                price, details = self.calculate_price(resource_id, market.id)
                prices.append(price)
                trends["markets"].append({
                    "market_id": market.id,
                    "market_name": market.name,
                    "price": price,
                    "modifier": market.get_price_modifier(str(resource_id))
                })
            
            if prices:
                trends["average_price"] = sum(prices) / len(prices)
                trends["price_range"]["min"] = min(prices)
                trends["price_range"]["max"] = max(prices)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting price trends for resource {resource_id}: {str(e)}")
            return {"error": str(e), "resource_id": resource_id}
