"""
Economy Integration for World State System

This module provides integration between the world state system and economy system,
allowing world state to track economic events, trade routes, and resource prices.
"""

from typing import Optional, List, Dict, Any, Protocol
from uuid import UUID
from datetime import datetime
import logging

from backend.systems.world_state.world_types import StateCategory
from backend.systems.world_state.services.services import WorldStateService

logger = logging.getLogger(__name__)


class EconomyServiceProtocol(Protocol):
    """Protocol for economy service integration"""
    
    async def get_trade_route_by_id(self, route_id: UUID) -> Optional[Any]:
        """Get trade route by ID"""
        ...
    
    async def list_trade_routes(self, **kwargs) -> Any:
        """List trade routes"""
        ...
    
    async def get_resource_price(self, resource_type: str, region_id: str) -> Optional[float]:
        """Get current resource price in a region"""
        ...
    
    async def get_market_data(self, region_id: str) -> Optional[Dict[str, Any]]:
        """Get market data for a region"""
        ...


class EconomyWorldStateIntegration:
    """Integration service for economy and world state systems"""
    
    def __init__(self, 
                 world_state_service: WorldStateService,
                 economy_service: Optional[EconomyServiceProtocol] = None):
        self.world_state_service = world_state_service
        self.economy_service = economy_service
    
    # ===== TRADE ROUTES =====
    
    async def create_trade_route(
        self,
        route_id: UUID,
        origin_region: str,
        destination_region: str,
        resource_type: str,
        trade_volume: float,
        route_security: float = 1.0,
        reason: str = "Trade route established"
    ) -> bool:
        """Create a trade route between regions"""
        try:
            # Store trade route in world state
            route_key = f"trade_routes.{route_id}"
            route_data = {
                'origin_region': origin_region,
                'destination_region': destination_region,
                'resource_type': resource_type,
                'trade_volume': trade_volume,
                'route_security': route_security,
                'status': 'active',
                'created_at': datetime.utcnow().isoformat()
            }
            
            await self.world_state_service.set_state_variable(
                route_key,
                route_data,
                category=StateCategory.ECONOMIC,
                reason=reason
            )
            
            # Update region trade connections
            await self._update_region_trade_connections(origin_region, destination_region, resource_type, True)
            
            # Record trade route event
            await self.record_trade_event(
                route_id,
                "route_created",
                f"Trade route created: {origin_region} → {destination_region} ({resource_type})",
                [origin_region, destination_region]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create trade route: {e}")
            return False
    
    async def update_trade_route_security(
        self,
        route_id: UUID,
        security_level: float,
        reason: str = "Security level update"
    ) -> bool:
        """Update trade route security level (0.0 = dangerous, 1.0 = safe)"""
        try:
            route_key = f"trade_routes.{route_id}"
            current_route = await self.world_state_service.get_state_variable(route_key)
            
            if not current_route:
                logger.warning(f"Trade route {route_id} not found")
                return False
            
            # Update security level
            current_route['route_security'] = max(0.0, min(1.0, security_level))
            current_route['last_updated'] = datetime.utcnow().isoformat()
            
            await self.world_state_service.set_state_variable(
                route_key,
                current_route,
                category=StateCategory.ECONOMIC,
                reason=reason
            )
            
            # Record security event
            await self.record_trade_event(
                route_id,
                "security_update",
                f"Trade route security updated to {security_level:.2f}",
                [current_route['origin_region'], current_route['destination_region']]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update trade route security: {e}")
            return False
    
    async def disable_trade_route(
        self,
        route_id: UUID,
        reason: str = "Trade route disabled"
    ) -> bool:
        """Disable a trade route"""
        try:
            route_key = f"trade_routes.{route_id}"
            current_route = await self.world_state_service.get_state_variable(route_key)
            
            if not current_route:
                logger.warning(f"Trade route {route_id} not found")
                return False
            
            # Update status
            current_route['status'] = 'disabled'
            current_route['disabled_at'] = datetime.utcnow().isoformat()
            
            await self.world_state_service.set_state_variable(
                route_key,
                current_route,
                category=StateCategory.ECONOMIC,
                reason=reason
            )
            
            # Update region connections
            await self._update_region_trade_connections(
                current_route['origin_region'],
                current_route['destination_region'],
                current_route['resource_type'],
                False
            )
            
            # Record event
            await self.record_trade_event(
                route_id,
                "route_disabled",
                f"Trade route disabled: {reason}",
                [current_route['origin_region'], current_route['destination_region']]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable trade route: {e}")
            return False
    
    # ===== RESOURCE PRICES =====
    
    async def set_resource_price(
        self,
        region_id: str,
        resource_type: str,
        price: float,
        reason: str = "Price update"
    ) -> bool:
        """Set resource price in a region"""
        try:
            price_key = f"regions.{region_id}.resource_prices.{resource_type}"
            
            # Get current price for comparison
            old_price = await self.world_state_service.get_state_variable(price_key, region_id=region_id)
            
            # Update price
            await self.world_state_service.set_state_variable(
                price_key,
                price,
                region_id=region_id,
                category=StateCategory.ECONOMIC,
                reason=reason
            )
            
            # Calculate price change if we had a previous price
            if old_price is not None:
                price_change = (price - old_price) / old_price * 100
                
                # Record significant price changes
                if abs(price_change) > 10:  # More than 10% change
                    await self.record_economic_event(
                        "price_change",
                        f"{resource_type} price in {region_id}: {old_price:.2f} → {price:.2f} ({price_change:+.1f}%)",
                        [region_id],
                        {
                            'resource_type': resource_type,
                            'old_price': old_price,
                            'new_price': price,
                            'change_percent': price_change
                        }
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set resource price: {e}")
            return False
    
    async def get_resource_price(self, region_id: str, resource_type: str) -> Optional[float]:
        """Get current resource price in a region"""
        try:
            price_key = f"regions.{region_id}.resource_prices.{resource_type}"
            return await self.world_state_service.get_state_variable(price_key, region_id=region_id)
        except Exception as e:
            logger.error(f"Failed to get resource price: {e}")
            return None
    
    async def get_regional_market_data(self, region_id: str) -> Dict[str, Any]:
        """Get all market data for a region"""
        try:
            # Get all resource prices for the region
            query_result = await self.world_state_service.query_state(
                category=StateCategory.ECONOMIC,
                region_id=region_id,
                key_pattern=f"regions.{region_id}.resource_prices.*"
            )
            
            prices = {}
            for key, value in query_result.items():
                # Extract resource type from key
                parts = key.split('.')
                if len(parts) >= 4:
                    resource_type = parts[3]
                    prices[resource_type] = float(value)
            
            # Get trade connections
            trade_connections = await self._get_region_trade_connections(region_id)
            
            return {
                'region_id': region_id,
                'resource_prices': prices,
                'trade_connections': trade_connections,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get regional market data: {e}")
            return {'error': str(e)}
    
    # ===== ECONOMIC EVENTS =====
    
    async def record_trade_event(
        self,
        route_id: UUID,
        event_type: str,
        description: str,
        affected_regions: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record a trade-related event"""
        try:
            event_metadata = {
                'route_id': str(route_id),
                'event_subtype': event_type,
                **(metadata or {})
            }
            
            return await self.world_state_service.record_world_event(
                event_type=f"trade_{event_type}",
                description=description,
                affected_regions=affected_regions,
                category=StateCategory.ECONOMIC,
                metadata=event_metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to record trade event: {e}")
            return ""
    
    async def record_economic_event(
        self,
        event_type: str,
        description: str,
        affected_regions: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record an economic event"""
        try:
            return await self.world_state_service.record_world_event(
                event_type=f"economic_{event_type}",
                description=description,
                affected_regions=affected_regions,
                category=StateCategory.ECONOMIC,
                metadata=metadata or {}
            )
            
        except Exception as e:
            logger.error(f"Failed to record economic event: {e}")
            return ""
    
    # ===== MARKET ANALYSIS =====
    
    async def analyze_regional_economy(self, region_id: str) -> Dict[str, Any]:
        """Analyze the economic state of a region"""
        try:
            market_data = await self.get_regional_market_data(region_id)
            
            if 'error' in market_data:
                return market_data
            
            prices = market_data.get('resource_prices', {})
            trade_connections = market_data.get('trade_connections', {})
            
            # Calculate economic metrics
            analysis = {
                'region_id': region_id,
                'economic_health': self._calculate_economic_health(prices, trade_connections),
                'price_volatility': self._calculate_price_volatility(region_id),
                'trade_connectivity': len(trade_connections.get('incoming', [])) + len(trade_connections.get('outgoing', [])),
                'dominant_resources': self._identify_dominant_resources(prices),
                'trade_balance': self._calculate_trade_balance(trade_connections),
                'recommendations': self._generate_economic_recommendations(prices, trade_connections)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze regional economy: {e}")
            return {'error': str(e)}
    
    # ===== PRIVATE HELPER METHODS =====
    
    async def _update_region_trade_connections(
        self,
        origin_region: str,
        destination_region: str,
        resource_type: str,
        is_active: bool
    ):
        """Update trade connections for regions"""
        try:
            # Update outgoing connections for origin
            outgoing_key = f"regions.{origin_region}.trade_connections.outgoing.{destination_region}"
            if is_active:
                outgoing_data = await self.world_state_service.get_state_variable(outgoing_key, region_id=origin_region) or []
                if resource_type not in outgoing_data:
                    outgoing_data.append(resource_type)
                await self.world_state_service.set_state_variable(
                    outgoing_key, outgoing_data, region_id=origin_region, category=StateCategory.ECONOMIC
                )
            else:
                outgoing_data = await self.world_state_service.get_state_variable(outgoing_key, region_id=origin_region) or []
                if resource_type in outgoing_data:
                    outgoing_data.remove(resource_type)
                    await self.world_state_service.set_state_variable(
                        outgoing_key, outgoing_data, region_id=origin_region, category=StateCategory.ECONOMIC
                    )
            
            # Update incoming connections for destination
            incoming_key = f"regions.{destination_region}.trade_connections.incoming.{origin_region}"
            if is_active:
                incoming_data = await self.world_state_service.get_state_variable(incoming_key, region_id=destination_region) or []
                if resource_type not in incoming_data:
                    incoming_data.append(resource_type)
                await self.world_state_service.set_state_variable(
                    incoming_key, incoming_data, region_id=destination_region, category=StateCategory.ECONOMIC
                )
            else:
                incoming_data = await self.world_state_service.get_state_variable(incoming_key, region_id=destination_region) or []
                if resource_type in incoming_data:
                    incoming_data.remove(resource_type)
                    await self.world_state_service.set_state_variable(
                        incoming_key, incoming_data, region_id=destination_region, category=StateCategory.ECONOMIC
                    )
                    
        except Exception as e:
            logger.error(f"Failed to update trade connections: {e}")
    
    async def _get_region_trade_connections(self, region_id: str) -> Dict[str, Any]:
        """Get trade connections for a region"""
        try:
            query_result = await self.world_state_service.query_state(
                category=StateCategory.ECONOMIC,
                region_id=region_id,
                key_pattern=f"regions.{region_id}.trade_connections.*"
            )
            
            connections = {'incoming': {}, 'outgoing': {}}
            
            for key, value in query_result.items():
                parts = key.split('.')
                if len(parts) >= 5:
                    direction = parts[3]  # 'incoming' or 'outgoing'
                    partner_region = parts[4]
                    if direction in connections:
                        connections[direction][partner_region] = value
            
            return connections
            
        except Exception as e:
            logger.error(f"Failed to get trade connections: {e}")
            return {'incoming': {}, 'outgoing': {}}
    
    def _calculate_economic_health(self, prices: Dict[str, float], trade_connections: Dict[str, Any]) -> str:
        """Calculate economic health based on prices and trade"""
        if not prices:
            return "unknown"
        
        # Simple heuristic based on number of resources and trade connections
        resource_diversity = len(prices)
        trade_diversity = len(trade_connections.get('incoming', {})) + len(trade_connections.get('outgoing', {}))
        
        if resource_diversity >= 3 and trade_diversity >= 2:
            return "healthy"
        elif resource_diversity >= 2 or trade_diversity >= 1:
            return "moderate"
        else:
            return "poor"
    
    def _calculate_price_volatility(self, region_id: str) -> str:
        """Calculate price volatility (simplified)"""
        # This would require historical price data
        # For now, return a placeholder
        return "low"
    
    def _identify_dominant_resources(self, prices: Dict[str, float]) -> List[str]:
        """Identify the most valuable resources in the region"""
        if not prices:
            return []
        
        # Sort by price (assuming higher price = more valuable)
        sorted_resources = sorted(prices.items(), key=lambda x: x[1], reverse=True)
        return [resource for resource, price in sorted_resources[:3]]  # Top 3
    
    def _calculate_trade_balance(self, trade_connections: Dict[str, Any]) -> str:
        """Calculate trade balance"""
        incoming = len(trade_connections.get('incoming', {}))
        outgoing = len(trade_connections.get('outgoing', {}))
        
        if outgoing > incoming * 1.5:
            return "export_surplus"
        elif incoming > outgoing * 1.5:
            return "import_dependent"
        else:
            return "balanced"
    
    def _generate_economic_recommendations(self, prices: Dict[str, float], trade_connections: Dict[str, Any]) -> List[str]:
        """Generate economic recommendations"""
        recommendations = []
        
        if len(prices) < 2:
            recommendations.append("Diversify resource production")
        
        if len(trade_connections.get('outgoing', {})) < 1:
            recommendations.append("Establish export trade routes")
        
        if len(trade_connections.get('incoming', {})) < 1:
            recommendations.append("Develop import partnerships")
        
        return recommendations


async def create_economy_world_state_integration(
    world_state_service: WorldStateService,
    economy_service: Optional[EconomyServiceProtocol] = None
) -> EconomyWorldStateIntegration:
    """Factory function to create economy world state integration"""
    return EconomyWorldStateIntegration(world_state_service, economy_service) 