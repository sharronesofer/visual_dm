"""
Futures Service

This module provides service layer functionality for commodity futures contracts
in the economy system.
"""

from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid
import random
import math

import logging
logger = logging.getLogger(__name__)
from backend.systems.economy.models import (
    CommodityFuture, CommodityFutureData,
    Market
)
from backend.systems.economy.services.resource import Resource

class FuturesService:
    """
    Service for managing commodity futures contracts.
    
    This service handles:
    - Creation of futures contracts
    - Matching buyers and sellers
    - Settlement of contracts at expiration
    - Price forecasting based on futures market
    """
    
    def __init__(self, db_session: Optional[Session] = None, 
                resource_service=None, market_service=None):
        """Initialize futures service.
        
        Args:
            db_session: SQLAlchemy session for database operations
            resource_service: ResourceService instance for resource operations
            market_service: MarketService instance for market operations
        """
        self.db_session = db_session
        self.resource_service = resource_service
        self.market_service = market_service
        self._cache = {}
        
    def get_future(self, future_id: Union[str, int]) -> Optional[CommodityFuture]:
        """Get a commodity future by ID.
        
        Args:
            future_id: ID of the future contract
            
        Returns:
            CommodityFuture if found, None otherwise
        """
        if not self.db_session:
            return None
            
        try:
            future = self.db_session.query(CommodityFuture).filter(
                CommodityFuture.id == str(future_id)
            ).first()
            return future
        except Exception as e:
            logger.error(f"Error getting commodity future {future_id}: {str(e)}")
            return None
            
    def get_futures_by_resource(self, resource_id: Union[str, int]) -> List[CommodityFuture]:
        """Get all futures contracts for a resource.
        
        Args:
            resource_id: ID of the resource
            
        Returns:
            List of CommodityFuture objects
        """
        if not self.db_session:
            return []
            
        try:
            futures = self.db_session.query(CommodityFuture).filter(
                CommodityFuture.resource_id == str(resource_id)
            ).all()
            return futures
        except Exception as e:
            logger.error(f"Error getting futures for resource {resource_id}: {str(e)}")
            return []
            
    def get_futures_by_market(self, market_id: Union[str, int]) -> List[CommodityFuture]:
        """Get all futures contracts in a market.
        
        Args:
            market_id: ID of the market
            
        Returns:
            List of CommodityFuture objects
        """
        if not self.db_session:
            return []
            
        try:
            futures = self.db_session.query(CommodityFuture).filter(
                CommodityFuture.market_id == str(market_id)
            ).all()
            return futures
        except Exception as e:
            logger.error(f"Error getting futures for market {market_id}: {str(e)}")
            return []
            
    def get_open_futures(self, market_id: Optional[Union[str, int]] = None) -> List[CommodityFuture]:
        """Get all open (unmatched) futures contracts.
        
        Args:
            market_id: Optional market ID to filter by
            
        Returns:
            List of open CommodityFuture objects
        """
        if not self.db_session:
            return []
            
        try:
            query = self.db_session.query(CommodityFuture).filter(
                CommodityFuture.status == "open"
            )
            
            if market_id:
                query = query.filter(CommodityFuture.market_id == str(market_id))
                
            futures = query.all()
            return futures
        except Exception as e:
            logger.error(f"Error getting open futures: {str(e)}")
            return []
    
    def create_future(self, future_data: Union[Dict[str, Any], CommodityFutureData]) -> Optional[CommodityFuture]:
        """Create a new futures contract.
        
        Args:
            future_data: Data for the new futures contract
            
        Returns:
            New CommodityFuture if successful, None otherwise
        """
        if not self.db_session:
            return None
            
        try:
            # Convert dict to CommodityFutureData if needed
            if isinstance(future_data, dict):
                # Generate ID if not provided
                if "id" not in future_data:
                    future_data["id"] = str(uuid.uuid4())
                
                # Set timestamps if not provided
                now = datetime.utcnow()
                if "created_at" not in future_data:
                    future_data["created_at"] = now
                if "updated_at" not in future_data:
                    future_data["updated_at"] = now
                    
                future_data_obj = CommodityFutureData(**future_data)
            else:
                future_data_obj = future_data
                
            # Validate data
            if not future_data_obj.resource_id or not future_data_obj.market_id:
                logger.error("Future must have resource_id and market_id")
                return None
                
            if future_data_obj.quantity <= 0:
                logger.error(f"Invalid quantity for future: {future_data_obj.quantity}")
                return None
                
            # Verify resource exists if resource service is available
            if self.resource_service:
                resource = self.resource_service.get_resource(future_data_obj.resource_id)
                if not resource:
                    logger.error(f"Resource {future_data_obj.resource_id} not found")
                    return None
                    
            # Verify market exists if market service is available
            if self.market_service:
                market = self.market_service.get_market(future_data_obj.market_id)
                if not market:
                    logger.error(f"Market {future_data_obj.market_id} not found")
                    return None
            
            # Create the future
            future = CommodityFuture.from_data(future_data_obj)
            self.db_session.add(future)
            self.db_session.commit()
            
            logger.info(f"Created future contract {future.id} for resource {future.resource_id}")
            return future
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error creating future: {str(e)}")
            return None
            
    def update_future(self, future_id: Union[str, int], updates: Dict[str, Any]) -> Optional[CommodityFuture]:
        """Update an existing futures contract.
        
        Args:
            future_id: ID of the future to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated CommodityFuture if successful, None otherwise
        """
        if not self.db_session:
            return None
            
        try:
            future = self.get_future(future_id)
            if not future:
                logger.error(f"Future {future_id} not found")
                return None
                
            # Don't update certain fields
            protected_fields = ["id", "resource_id", "market_id", "created_at"]
            for field in protected_fields:
                if field in updates:
                    del updates[field]
                    
            # Don't allow changing settled contracts except for admin purposes
            if future.is_settled and "is_settled" not in updates:
                logger.error(f"Cannot update settled future {future_id}")
                return None
                
            # Update fields
            for key, value in updates.items():
                if hasattr(future, key):
                    setattr(future, key, value)
                    
            # Always update the updated_at timestamp
            future.updated_at = datetime.utcnow()
            
            self.db_session.add(future)
            self.db_session.commit()
            
            logger.info(f"Updated future contract {future_id}")
            return future
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error updating future {future_id}: {str(e)}")
            return None
            
    def match_buyer(self, future_id: Union[str, int], buyer_id: str) -> Optional[CommodityFuture]:
        """Match a buyer to an open futures contract.
        
        Args:
            future_id: ID of the future contract
            buyer_id: ID of the buyer entity
            
        Returns:
            Updated CommodityFuture if successful, None otherwise
        """
        if not self.db_session:
            return None
            
        try:
            future = self.get_future(future_id)
            if not future:
                logger.error(f"Future {future_id} not found")
                return None
                
            if future.status != "open":
                logger.error(f"Future {future_id} is not open for matching")
                return None
                
            if future.buyer_id:
                logger.error(f"Future {future_id} already has a buyer")
                return None
                
            # Update the future with the buyer
            future.buyer_id = buyer_id
            future.status = "matched"
            future.updated_at = datetime.utcnow()
            
            self.db_session.add(future)
            self.db_session.commit()
            
            logger.info(f"Matched buyer {buyer_id} to future {future_id}")
            return future
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error matching buyer for future {future_id}: {str(e)}")
            return None
            
    def settle_future(self, future_id: Union[str, int]) -> Dict[str, Any]:
        """Settle a futures contract (execute the trade).
        
        Args:
            future_id: ID of the future to settle
            
        Returns:
            Dictionary with settlement results
        """
        if not self.db_session:
            return {"error": "No database session available"}
            
        try:
            future = self.get_future(future_id)
            if not future:
                return {"error": f"Future {future_id} not found"}
                
            if future.is_settled:
                return {"error": f"Future {future_id} is already settled"}
                
            if future.status != "matched":
                return {"error": f"Future {future_id} cannot be settled (status: {future.status})"}
                
            # Get current market price for the resource
            current_price = None
            price_info = {}
            
            if self.market_service:
                price, price_info = self.market_service.calculate_price(
                    future.resource_id, future.market_id, future.quantity
                )
                current_price = price
                
            # Calculate profit/loss
            profit_loss = 0.0
            if current_price is not None:
                # Positive means buyer made profit, negative means seller made profit
                profit_loss = (current_price - future.strike_price) * future.quantity
                
            # Mark as settled
            future.is_settled = True
            future.status = "settled"
            future.settlement_date = datetime.utcnow()
            
            self.db_session.add(future)
            self.db_session.commit()
            
            # Create result
            result = {
                "future_id": future.id,
                "resource_id": future.resource_id,
                "market_id": future.market_id,
                "quantity": future.quantity,
                "strike_price": future.strike_price,
                "current_price": current_price,
                "profit_loss": profit_loss,
                "buyer_profit": profit_loss if profit_loss > 0 else 0,
                "seller_profit": -profit_loss if profit_loss < 0 else 0,
                "settlement_date": future.settlement_date.isoformat() if future.settlement_date else None,
                "price_info": price_info
            }
            
            logger.info(f"Settled future {future_id} with profit/loss {profit_loss}")
            return result
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error settling future {future_id}: {str(e)}")
            return {"error": str(e)}
            
    def process_expiring_futures(self) -> Dict[str, Any]:
        """Process all futures contracts that are expiring.
        
        This should be called regularly to settle/expire contracts
        that have reached their expiration date.
        
        Returns:
            Dictionary with processing results
        """
        if not self.db_session:
            return {"error": "No database session available"}
            
        try:
            now = datetime.utcnow()
            
            # Find futures that are expiring now
            expiring_futures = self.db_session.query(CommodityFuture).filter(
                and_(
                    CommodityFuture.expiration_date <= now,
                    CommodityFuture.is_settled == False,
                    or_(
                        CommodityFuture.status == "matched",
                        CommodityFuture.status == "open"
                    )
                )
            ).all()
            
            results = {
                "processed_count": len(expiring_futures),
                "settled": [],
                "expired": [],
                "errors": []
            }
            
            # Process each expiring future
            for future in expiring_futures:
                try:
                    if future.status == "matched":
                        # Settle matched futures
                        settlement = self.settle_future(future.id)
                        if "error" in settlement:
                            results["errors"].append({
                                "future_id": future.id,
                                "error": settlement["error"]
                            })
                        else:
                            results["settled"].append(settlement)
                    else:
                        # Expire open futures
                        future.status = "expired"
                        future.updated_at = now
                        self.db_session.add(future)
                        
                        results["expired"].append({
                            "future_id": future.id,
                            "resource_id": future.resource_id,
                            "market_id": future.market_id,
                            "quantity": future.quantity,
                            "strike_price": future.strike_price
                        })
                except Exception as e:
                    logger.error(f"Error processing future {future.id}: {str(e)}")
                    results["errors"].append({
                        "future_id": future.id,
                        "error": str(e)
                    })
                    
            # Commit all changes
            self.db_session.commit()
            
            logger.info(f"Processed {len(expiring_futures)} expiring futures: "
                      f"{len(results['settled'])} settled, {len(results['expired'])} expired")
            return results
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error processing expiring futures: {str(e)}")
            return {"error": str(e)}
            
    def forecast_future_prices(self, resource_id: Union[str, int], 
                              market_id: Optional[Union[str, int]] = None,
                              time_periods: int = 3) -> Dict[str, Any]:
        """Forecast future prices based on futures contracts.
        
        Args:
            resource_id: ID of the resource
            market_id: Optional market ID to filter by
            time_periods: Number of time periods to forecast
            
        Returns:
            Dictionary with price forecasts
        """
        try:
            # Get all futures for this resource
            futures_query = self.db_session.query(CommodityFuture).filter(
                CommodityFuture.resource_id == str(resource_id),
                or_(
                    CommodityFuture.status == "matched",
                    CommodityFuture.status == "open"
                )
            )
            
            if market_id:
                futures_query = futures_query.filter(CommodityFuture.market_id == str(market_id))
                
            futures = futures_query.all()
            
            if not futures:
                return {
                    "resource_id": resource_id,
                    "market_id": market_id,
                    "message": "No futures data available for forecasting",
                    "forecasts": []
                }
                
            # Get current price
            current_price = None
            if self.market_service:
                if market_id:
                    price, _ = self.market_service.calculate_price(resource_id, market_id)
                    current_price = price
                else:
                    # Use the average price across all markets
                    markets = self.market_service.get_markets_for_resource(resource_id)
                    if markets:
                        prices = []
                        for market in markets:
                            price, _ = self.market_service.calculate_price(resource_id, market.id)
                            prices.append(price)
                        current_price = sum(prices) / len(prices) if prices else None
                    
            # Group futures by expiration time periods
            now = datetime.utcnow()
            period_futures = {}
            
            for future in futures:
                if future.expiration_date < now:
                    continue  # Skip expired futures
                    
                # Calculate which period this future belongs to
                days_until_expiration = (future.expiration_date - now).days
                period = min(days_until_expiration // 30 + 1, time_periods)
                
                if period not in period_futures:
                    period_futures[period] = []
                period_futures[period].append(future)
                
            # Generate forecasts
            forecasts = []
            
            for period in range(1, time_periods + 1):
                period_data = {
                    "period": period,
                    "days_from_now": period * 30,
                    "forecast_date": (now + timedelta(days=period * 30)).isoformat(),
                }
                
                if period in period_futures:
                    # Calculate weighted average price from futures
                    total_quantity = sum(f.quantity for f in period_futures[period])
                    weighted_price = sum(f.strike_price * f.quantity for f in period_futures[period]) / total_quantity
                    
                    period_data.update({
                        "futures_count": len(period_futures[period]),
                        "total_volume": total_quantity,
                        "weighted_price": weighted_price,
                        "price_range": {
                            "min": min(f.strike_price for f in period_futures[period]),
                            "max": max(f.strike_price for f in period_futures[period])
                        },
                        "confidence": min(100, 40 + (len(period_futures[period]) * 5))  # More futures = higher confidence
                    })
                    
                    # Calculate price change from current
                    if current_price:
                        price_change = weighted_price - current_price
                        price_change_pct = (price_change / current_price) * 100
                        
                        period_data.update({
                            "current_price": current_price,
                            "price_change": price_change,
                            "price_change_percent": price_change_pct,
                            "direction": "up" if price_change > 0 else "down" if price_change < 0 else "stable"
                        })
                else:
                    # No futures data for this period
                    period_data.update({
                        "futures_count": 0,
                        "message": "No futures data available for this period",
                        "confidence": 0
                    })
                    
                forecasts.append(period_data)
                
            return {
                "resource_id": resource_id,
                "market_id": market_id,
                "current_price": current_price,
                "total_futures": len(futures),
                "forecast_generated_at": now.isoformat(),
                "forecasts": forecasts
            }
            
        except Exception as e:
            logger.error(f"Error forecasting prices for resource {resource_id}: {str(e)}")
            return {
                "resource_id": resource_id,
                "market_id": market_id,
                "error": str(e)
            }
            
    def clear_cache(self) -> None:
        """Clear service cache."""
        self._cache = {} 