"""
Unified Economy Service - Central coordination for all economy subsystems

This service provides a unified interface for coordinating between different
economy subsystems like resources, markets, trade routes, and futures.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session

from backend.systems.economy.services.economy_manager import EconomyManager
from backend.systems.economy.services.resource_service import ResourceService
from backend.systems.economy.services.market_service import MarketService
from backend.systems.economy.services.trade_service import TradeService
from backend.systems.economy.services.futures_service import FuturesService

logger = logging.getLogger(__name__)


class UnifiedEconomyService:
    """
    Unified service for coordinating all economy operations.
    
    This service acts as a facade pattern, providing a simplified interface
    for complex economy operations that span multiple subsystems.
    """
    
    def __init__(self, db_session: Session):
        """Initialize the unified economy service."""
        self.db_session = db_session
        self.economy_manager = EconomyManager.get_instance(db_session)
        
        # Direct service references for fine-grained control
        self.resource_service = ResourceService(db_session)
        self.market_service = MarketService(db_session)
        self.trade_service = TradeService(db_session)
        self.futures_service = FuturesService(db_session)
        
        logger.info("Unified Economy Service initialized")
    
    def get_economy_overview(self, region_id: Optional[int] = None) -> Dict[str, Any]:
        """Get a comprehensive overview of the economy state."""
        try:
            overview = {
                'timestamp': datetime.utcnow().isoformat(),
                'region_id': region_id,
                'system_status': self.economy_manager.get_economy_status(),
                'economic_analytics': self.economy_manager.get_economic_analytics(region_id),
                'price_indices': self.economy_manager.calculate_price_index(region_id),
            }
            
            # Add region-specific data if region specified
            if region_id:
                overview['resources'] = [
                    r.dict() if hasattr(r, 'dict') else str(r) 
                    for r in self.economy_manager.get_resources_by_region(region_id)
                ]
                overview['markets'] = [
                    m.dict() if hasattr(m, 'dict') else str(m)
                    for m in self.economy_manager.get_markets_by_region(region_id)
                ]
                overview['trade_routes'] = [
                    tr.dict() if hasattr(tr, 'dict') else str(tr)
                    for tr in self.economy_manager.get_trade_routes_by_region(region_id)
                ]
            
            return overview
            
        except Exception as e:
            logger.error(f"Error getting economy overview: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'region_id': region_id
            }
    
    def process_economic_tick(self, regions: Optional[List[int]] = None) -> Dict[str, Any]:
        """Process economic updates for specified regions or all regions."""
        try:
            results = {
                'timestamp': datetime.utcnow().isoformat(),
                'processed_regions': [],
                'total_trades': 0,
                'total_market_updates': 0,
                'generated_events': [],
                'errors': []
            }
            
            if regions:
                # Process specific regions
                for region_id in regions:
                    try:
                        tick_result = self.economy_manager.process_tick(region_id)
                        results['processed_regions'].append(region_id)
                        results['total_trades'] += tick_result.get('trades_processed', 0)
                        results['total_market_updates'] += tick_result.get('markets_updated', 0)
                        results['generated_events'].extend(tick_result.get('generated_events', []))
                    except Exception as e:
                        logger.warning(f"Error processing tick for region {region_id}: {e}")
                        results['errors'].append({
                            'region_id': region_id,
                            'error': str(e)
                        })
            else:
                # Process global tick
                tick_result = self.economy_manager.process_tick()
                results['total_trades'] = tick_result.get('trades_processed', 0)
                results['total_market_updates'] = tick_result.get('markets_updated', 0)
                results['generated_events'] = tick_result.get('generated_events', [])
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing economic tick: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def execute_transaction(
        self, 
        transaction_type: str,
        source_region: int,
        target_region: Optional[int] = None,
        resource_id: Optional[int] = None,
        amount: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute an economy transaction across subsystems."""
        try:
            transaction_id = f"txn_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            result = {
                'transaction_id': transaction_id,
                'type': transaction_type,
                'timestamp': datetime.utcnow().isoformat(),
                'success': False,
                'details': {}
            }
            
            if transaction_type == 'transfer_resource':
                if not all([target_region, resource_id, amount]):
                    raise ValueError("Resource transfer requires target_region, resource_id, and amount")
                
                success, message = self.economy_manager.transfer_resource(
                    source_region, target_region, resource_id, amount
                )
                result['success'] = success
                result['details']['message'] = message
                
            elif transaction_type == 'market_trade':
                if not all([resource_id, amount]):
                    raise ValueError("Market trade requires resource_id and amount")
                
                market_id = kwargs.get('market_id', 1)
                price, details = self.economy_manager.calculate_price(resource_id, market_id, amount)
                
                result['success'] = True
                result['details']['price'] = price
                result['details']['calculation_details'] = details
                
            elif transaction_type == 'create_future':
                if not all([resource_id, amount]):
                    raise ValueError("Future creation requires resource_id and amount")
                
                future_data = {
                    'resource_id': str(resource_id),
                    'market_id': str(kwargs.get('market_id', 1)),
                    'quantity': amount,
                    'strike_price': kwargs.get('strike_price', 100.0),
                    'seller_id': kwargs.get('seller_id', 'system')
                }
                
                future = self.economy_manager.create_future(future_data)
                result['success'] = future is not None
                result['details']['future'] = future.dict() if future and hasattr(future, 'dict') else str(future)
                
            else:
                raise ValueError(f"Unknown transaction type: {transaction_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing transaction: {e}")
            return {
                'transaction_id': transaction_id if 'transaction_id' in locals() else 'unknown',
                'type': transaction_type,
                'timestamp': datetime.utcnow().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        try:
            status = self.economy_manager.get_economy_status()
            
            health = {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': 'healthy' if status.get('initialized') else 'unhealthy',
                'services': status.get('services', {}),
                'database_status': 'connected' if self.db_session else 'disconnected',
                'subsystem_health': {
                    'resource_service': 'operational',
                    'market_service': 'operational', 
                    'trade_service': 'operational',
                    'futures_service': 'operational'
                }
            }
            
            # Additional health checks
            try:
                # Test basic operations
                self.economy_manager.get_resource('1')
                health['basic_operations'] = 'functional'
            except Exception:
                health['basic_operations'] = 'impaired'
                health['overall_status'] = 'degraded'
            
            return health
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': 'critical',
                'error': str(e)
            }


def create_unified_economy_service(db_session: Session) -> UnifiedEconomyService:
    """Factory function to create a unified economy service instance."""
    return UnifiedEconomyService(db_session) 