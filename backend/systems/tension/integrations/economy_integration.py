"""
Tension-Economy System Integration

Modifies economic behavior based on regional tension levels:
- Dynamic pricing adjustments based on local stability
- Trade route modifications during high tension periods
- Market availability changes during conflicts
- Economic sanctions and embargos during faction disputes
- Resource flow modifications based on regional safety

This follows the integration patterns from other game systems.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass

from backend.systems.tension import UnifiedTensionManager
from backend.infrastructure.events import event_bus

logger = logging.getLogger(__name__)


class EconomicTensionEffect(Enum):
    """Types of economic effects from tension"""
    STABLE_MARKET = "stable_market"
    PRICE_INFLATION = "price_inflation"
    TRADE_DISRUPTION = "trade_disruption"
    MARKET_CLOSURE = "market_closure"
    EMBARGO = "embargo"
    RESOURCE_HOARDING = "resource_hoarding"


@dataclass
class EconomicModifiers:
    """Economic modifiers based on tension levels"""
    effect_type: EconomicTensionEffect
    price_modifiers: Dict[str, float]  # item_type -> price_multiplier
    availability_modifiers: Dict[str, float]  # item_type -> availability_multiplier
    trade_route_modifications: Dict[str, float]  # route_id -> safety_multiplier
    market_operation_status: Dict[str, bool]  # market_id -> is_operational
    transaction_fees: Dict[str, float]  # transaction_type -> fee_multiplier


@dataclass
class TradeRouteStatus:
    """Status of trade routes affected by tension"""
    route_id: str
    origin_region: str
    destination_region: str
    safety_rating: float  # 0.0 = extremely dangerous, 1.0 = completely safe
    price_impact: float  # Multiplier for goods traveling this route
    availability_impact: float  # Reduction in goods flow
    estimated_delay: Optional[timedelta]
    recommended_alternatives: List[str]
    risk_factors: List[str]


class TensionEconomyIntegration:
    """Manages economic system integration with tension system"""
    
    def __init__(self, tension_manager: Optional[UnifiedTensionManager] = None):
        self.tension_manager = tension_manager or UnifiedTensionManager()
        self.integration_active = True
        self.economic_cache: Dict[str, EconomicModifiers] = {}
        self.trade_route_cache: Dict[str, TradeRouteStatus] = {}
        
        # Economic parameters
        self.price_sensitivity = 1.5  # How much tension affects prices
        self.availability_sensitivity = 1.2  # How much tension affects availability
        self.trade_route_sensitivity = 2.0  # How much tension affects trade routes
        
        # Economic thresholds
        self.market_closure_threshold = 0.8  # Tension level that closes markets
        self.embargo_threshold = 0.7  # Tension level that triggers embargos
        self.hoarding_threshold = 0.6  # Tension level that triggers resource hoarding
        
        # Register for tension events
        self._register_economic_handlers()
        
        logger.info("Economy-Tension integration initialized")
    
    def _register_economic_handlers(self) -> None:
        """Register event handlers for economic responses to tension"""
        event_bus.subscribe("tension:major_change", self._handle_tension_economic_impact)
        event_bus.subscribe("tension:conflict_triggered", self._handle_conflict_economic_impact)
        event_bus.subscribe("economy:trade_request", self._handle_trade_request)
        event_bus.subscribe("economy:market_query", self._handle_market_query)
    
    def get_economic_modifiers(self, region_id: str, poi_id: str = 'default') -> EconomicModifiers:
        """Get economic modifiers for a specific location based on tension"""
        try:
            # Get current tension
            current_tension = self.tension_manager.calculate_tension(region_id, poi_id)
            
            # Determine economic effect type
            effect_type = self._determine_economic_effect(current_tension)
            
            # Calculate price modifiers
            price_modifiers = self._calculate_price_modifiers(current_tension, effect_type, region_id)
            
            # Calculate availability modifiers
            availability_modifiers = self._calculate_availability_modifiers(current_tension, effect_type)
            
            # Calculate trade route modifications
            trade_route_mods = self._calculate_trade_route_modifications(current_tension, region_id)
            
            # Determine market operational status
            market_status = self._determine_market_status(current_tension, effect_type, region_id)
            
            # Calculate transaction fees
            transaction_fees = self._calculate_transaction_fees(current_tension, effect_type)
            
            modifiers = EconomicModifiers(
                effect_type=effect_type,
                price_modifiers=price_modifiers,
                availability_modifiers=availability_modifiers,
                trade_route_modifications=trade_route_mods,
                market_operation_status=market_status,
                transaction_fees=transaction_fees
            )
            
            # Cache for performance
            cache_key = f"{region_id}:{poi_id}"
            self.economic_cache[cache_key] = modifiers
            
            logger.debug(f"Economic modifiers for {region_id}/{poi_id}: {effect_type.value}")
            
            return modifiers
            
        except Exception as e:
            logger.error(f"Error calculating economic modifiers: {e}")
            return self._get_default_economic_modifiers()
    
    def get_trade_route_status(self, route_id: str, origin_region: str, 
                             destination_region: str) -> TradeRouteStatus:
        """Get status of a trade route based on regional tensions"""
        try:
            # Get tension levels for both regions
            origin_tension = self.tension_manager.calculate_tension(origin_region, 'default')
            dest_tension = self.tension_manager.calculate_tension(destination_region, 'default')
            
            # Calculate overall route tension (weighted average + danger bonus)
            route_tension = (origin_tension + dest_tension) / 2.0
            intermediate_danger = self._calculate_intermediate_route_danger(origin_region, destination_region)
            route_tension = min(1.0, route_tension + intermediate_danger)
            
            # Calculate safety rating (inverse of tension)
            safety_rating = max(0.0, 1.0 - route_tension)
            
            # Calculate economic impacts
            price_impact = 1.0 + (route_tension * self.trade_route_sensitivity)
            availability_impact = max(0.1, 1.0 - (route_tension * self.availability_sensitivity))
            
            # Estimate delays
            estimated_delay = self._calculate_trade_delay(route_tension)
            
            # Find alternative routes
            alternatives = self._find_alternative_routes(route_id, origin_region, destination_region, route_tension)
            
            # Identify risk factors
            risk_factors = self._identify_trade_risk_factors(origin_region, destination_region, route_tension)
            
            status = TradeRouteStatus(
                route_id=route_id,
                origin_region=origin_region,
                destination_region=destination_region,
                safety_rating=safety_rating,
                price_impact=price_impact,
                availability_impact=availability_impact,
                estimated_delay=estimated_delay,
                recommended_alternatives=alternatives,
                risk_factors=risk_factors
            )
            
            # Cache for performance
            self.trade_route_cache[route_id] = status
            
            logger.info(f"Trade route {route_id} status: safety={safety_rating:.2f}, price_impact={price_impact:.2f}")
            
            return status
            
        except Exception as e:
            logger.error(f"Error calculating trade route status: {e}")
            return self._get_default_trade_route_status(route_id, origin_region, destination_region)
    
    def apply_economic_sanctions(self, target_region: str, sanctioning_regions: List[str], 
                               severity: float = 0.5) -> Dict[str, Any]:
        """Apply economic sanctions to a region based on tension/conflict"""
        try:
            sanctions = {
                'target_region': target_region,
                'sanctioning_regions': sanctioning_regions,
                'severity': severity,
                'economic_effects': {},
                'trade_restrictions': {},
                'applied_at': datetime.utcnow().isoformat()
            }
            
            # Calculate economic effects of sanctions
            sanctions['economic_effects'] = {
                'price_inflation': 1.0 + (severity * 0.8),  # Prices increase
                'import_availability': max(0.1, 1.0 - severity),  # Imports decrease
                'export_penalties': 1.0 + (severity * 0.6),  # Export costs increase
                'currency_devaluation': severity * 0.3  # Currency loses value
            }
            
            # Define trade restrictions
            sanctions['trade_restrictions'] = {
                'luxury_goods': severity > 0.3,
                'military_supplies': severity > 0.1,
                'food_medicine': severity > 0.8,  # Only extreme sanctions affect essentials
                'technology': severity > 0.4,
                'raw_materials': severity > 0.6
            }
            
            # Apply sanctions to affected trade routes
            affected_routes = self._get_trade_routes_to_region(target_region)
            for route_id in affected_routes:
                self._apply_sanctions_to_route(route_id, severity)
            
            # Emit sanctions event
            event_bus.emit("economy:sanctions_applied", sanctions)
            
            logger.warning(f"Economic sanctions applied to {target_region} with severity {severity}")
            
            return sanctions
            
        except Exception as e:
            logger.error(f"Error applying economic sanctions: {e}")
            return {'error': str(e)}
    
    def calculate_market_panic_effects(self, region_id: str, panic_level: float) -> Dict[str, Any]:
        """Calculate effects of market panic during high tension periods"""
        try:
            panic_effects = {
                'region_id': region_id,
                'panic_level': panic_level,
                'market_effects': {},
                'trader_behavior': {},
                'long_term_impacts': {}
            }
            
            # Market effects
            panic_effects['market_effects'] = {
                'volatility_increase': panic_level * 2.0,
                'liquidity_decrease': panic_level * 0.8,
                'speculation_increase': panic_level * 1.5,
                'trust_decrease': panic_level * 0.6
            }
            
            # Trader behavior changes
            panic_effects['trader_behavior'] = {
                'risk_aversion': min(1.0, panic_level * 1.3),
                'hoarding_tendency': panic_level * 0.9,
                'price_gouging': panic_level * 0.7,
                'market_exit_probability': panic_level * 0.4
            }
            
            # Long-term economic impacts
            panic_effects['long_term_impacts'] = {
                'investment_withdrawal': panic_level * 0.5,
                'economic_growth_impact': -panic_level * 0.3,
                'recovery_time_weeks': int(panic_level * 12),
                'reputation_damage': panic_level * 0.4
            }
            
            return panic_effects
            
        except Exception as e:
            logger.error(f"Error calculating market panic effects: {e}")
            return {'error': str(e)}
    
    async def _handle_tension_economic_impact(self, event_data: Dict[str, Any]) -> None:
        """Handle economic impacts of tension changes"""
        try:
            region_id = event_data.get('region_id')
            new_tension = event_data.get('tension_level', 0.0)
            change_magnitude = event_data.get('change_magnitude', 0.0)
            
            # If significant tension change, update economic modifiers
            if change_magnitude > 0.1:
                modifiers = self.get_economic_modifiers(region_id)
                
                # Emit economic update event
                event_bus.emit("economy:tension_update", {
                    'region_id': region_id,
                    'tension_level': new_tension,
                    'economic_effect': modifiers.effect_type.value,
                    'price_impacts': modifiers.price_modifiers,
                    'availability_impacts': modifiers.availability_modifiers
                })
                
                # If severe tension, consider market panic
                if new_tension > 0.7:
                    panic_effects = self.calculate_market_panic_effects(region_id, new_tension)
                    event_bus.emit("economy:market_panic", panic_effects)
            
        except Exception as e:
            logger.error(f"Error handling tension economic impact: {e}")
    
    async def _handle_conflict_economic_impact(self, event_data: Dict[str, Any]) -> None:
        """Handle economic impacts of conflicts"""
        try:
            region_id = event_data.get('region_id')
            conflict_type = event_data.get('conflict_type')
            severity = event_data.get('severity', 1.0)
            
            # Apply economic consequences based on conflict type
            if conflict_type in ['faction_war', 'civil_conflict']:
                # Apply severe economic disruption
                sanctions = self.apply_economic_sanctions(
                    target_region=region_id,
                    sanctioning_regions=['neighboring_regions'],  # Would be actual neighboring regions
                    severity=min(1.0, severity * 0.8)
                )
                
                # Close markets during active warfare
                if severity > 0.8:
                    event_bus.emit("economy:emergency_market_closure", {
                        'region_id': region_id,
                        'closure_reason': 'active_conflict',
                        'estimated_duration': 'indefinite'
                    })
            
        except Exception as e:
            logger.error(f"Error handling conflict economic impact: {e}")
    
    async def _handle_trade_request(self, event_data: Dict[str, Any]) -> None:
        """Handle trade requests with tension-based modifications"""
        try:
            origin = event_data.get('origin_region')
            destination = event_data.get('destination_region')
            goods = event_data.get('goods', [])
            
            if origin and destination:
                # Get trade route status
                route_status = self.get_trade_route_status(
                    f"{origin}_to_{destination}", origin, destination
                )
                
                # Modify trade based on route status
                modified_trade = {
                    'original_request': event_data,
                    'route_safety': route_status.safety_rating,
                    'price_adjustments': route_status.price_impact,
                    'availability_adjustments': route_status.availability_impact,
                    'estimated_delay': route_status.estimated_delay.total_seconds() if route_status.estimated_delay else 0,
                    'risk_warnings': route_status.risk_factors,
                    'alternative_routes': route_status.recommended_alternatives
                }
                
                event_bus.emit("economy:trade_route_analysis", modified_trade)
            
        except Exception as e:
            logger.error(f"Error handling trade request: {e}")
    
    async def _handle_market_query(self, event_data: Dict[str, Any]) -> None:
        """Handle market queries with tension-based information"""
        try:
            region_id = event_data.get('region_id')
            
            if region_id:
                modifiers = self.get_economic_modifiers(region_id)
                
                market_info = {
                    'region_id': region_id,
                    'market_status': modifiers.effect_type.value,
                    'operational_markets': modifiers.market_operation_status,
                    'price_trends': modifiers.price_modifiers,
                    'availability_status': modifiers.availability_modifiers,
                    'transaction_costs': modifiers.transaction_fees
                }
                
                event_bus.emit("economy:market_status_response", market_info)
            
        except Exception as e:
            logger.error(f"Error handling market query: {e}")
    
    def _determine_economic_effect(self, tension: float) -> EconomicTensionEffect:
        """Determine economic effect type based on tension level"""
        if tension >= self.market_closure_threshold:
            return EconomicTensionEffect.MARKET_CLOSURE
        elif tension >= self.embargo_threshold:
            return EconomicTensionEffect.EMBARGO
        elif tension >= self.hoarding_threshold:
            return EconomicTensionEffect.RESOURCE_HOARDING
        elif tension >= 0.4:
            return EconomicTensionEffect.TRADE_DISRUPTION
        elif tension >= 0.2:
            return EconomicTensionEffect.PRICE_INFLATION
        else:
            return EconomicTensionEffect.STABLE_MARKET
    
    def _calculate_price_modifiers(self, tension: float, effect_type: EconomicTensionEffect, 
                                 region_id: str) -> Dict[str, float]:
        """Calculate price modifiers for different item types"""
        base_modifier = 1.0 + (tension * self.price_sensitivity)
        
        modifiers = {
            'food': base_modifier * 1.2,  # Food prices more sensitive
            'weapons': base_modifier * 1.5,  # Weapons spike during conflict
            'medicine': base_modifier * 1.3,  # Medicine becomes expensive
            'luxury_goods': max(0.5, base_modifier * 0.8),  # Luxury demand drops
            'raw_materials': base_modifier * 1.1,
            'manufactured_goods': base_modifier,
            'fuel': base_modifier * 1.4,  # Fuel critical during crisis
            'information': base_modifier * 2.0  # Information becomes valuable
        }
        
        # Apply effect-specific modifications
        if effect_type == EconomicTensionEffect.RESOURCE_HOARDING:
            modifiers['food'] *= 1.5
            modifiers['medicine'] *= 1.4
        elif effect_type == EconomicTensionEffect.EMBARGO:
            modifiers['luxury_goods'] *= 2.0
            modifiers['manufactured_goods'] *= 1.3
        
        return modifiers
    
    def _calculate_availability_modifiers(self, tension: float, 
                                        effect_type: EconomicTensionEffect) -> Dict[str, float]:
        """Calculate availability modifiers for different item types"""
        base_reduction = tension * self.availability_sensitivity
        
        modifiers = {
            'food': max(0.3, 1.0 - base_reduction * 0.8),  # Food always somewhat available
            'weapons': max(0.1, 1.0 - base_reduction * 1.5),  # Weapons restricted
            'medicine': max(0.4, 1.0 - base_reduction * 0.7),  # Medicine protected
            'luxury_goods': max(0.0, 1.0 - base_reduction * 2.0),  # Luxury disappears first
            'raw_materials': max(0.2, 1.0 - base_reduction),
            'manufactured_goods': max(0.3, 1.0 - base_reduction * 1.2),
            'fuel': max(0.2, 1.0 - base_reduction * 1.3),
            'information': min(1.2, 1.0 + base_reduction * 0.5)  # More info during crisis
        }
        
        return modifiers
    
    def _calculate_trade_route_modifications(self, tension: float, region_id: str) -> Dict[str, float]:
        """Calculate trade route safety modifications"""
        # This would integrate with actual trade route data
        return {
            'primary_route': max(0.1, 1.0 - tension),
            'secondary_route': max(0.3, 1.0 - tension * 0.7),
            'emergency_route': max(0.5, 1.0 - tension * 0.5)
        }
    
    def _determine_market_status(self, tension: float, effect_type: EconomicTensionEffect, 
                               region_id: str) -> Dict[str, bool]:
        """Determine which markets are operational"""
        if effect_type == EconomicTensionEffect.MARKET_CLOSURE:
            return {
                'primary_market': False,
                'secondary_market': False,
                'black_market': True  # Black markets thrive during closures
            }
        elif effect_type == EconomicTensionEffect.EMBARGO:
            return {
                'primary_market': True,
                'secondary_market': False,
                'black_market': True
            }
        else:
            return {
                'primary_market': True,
                'secondary_market': True,
                'black_market': tension > 0.4  # Black market emerges in medium tension
            }
    
    def _calculate_transaction_fees(self, tension: float, 
                                  effect_type: EconomicTensionEffect) -> Dict[str, float]:
        """Calculate transaction fee multipliers"""
        base_fee_increase = tension * 0.5
        
        return {
            'trade_fee': 1.0 + base_fee_increase,
            'security_fee': 1.0 + (tension * 2.0),  # Security costs spike
            'transport_fee': 1.0 + (tension * 1.5),
            'insurance_fee': 1.0 + (tension * 3.0),  # Insurance very expensive
            'storage_fee': 1.0 + (tension * 0.8)
        }
    
    def _calculate_intermediate_route_danger(self, origin: str, destination: str) -> float:
        """Calculate danger from intermediate regions on trade route"""
        # This would calculate tension in regions between origin and destination
        # For now, return a simple placeholder
        return 0.1  # 10% base intermediate danger
    
    def _calculate_trade_delay(self, route_tension: float) -> Optional[timedelta]:
        """Calculate estimated delay for trade routes"""
        if route_tension > 0.8:
            return timedelta(weeks=2)
        elif route_tension > 0.6:
            return timedelta(days=10)
        elif route_tension > 0.4:
            return timedelta(days=3)
        elif route_tension > 0.2:
            return timedelta(days=1)
        else:
            return None
    
    def _find_alternative_routes(self, route_id: str, origin: str, 
                               destination: str, current_danger: float) -> List[str]:
        """Find alternative trade routes"""
        # This would integrate with actual route planning system
        alternatives = []
        
        if current_danger > 0.6:
            alternatives.extend(['sea_route', 'mountain_pass'])
        if current_danger > 0.8:
            alternatives.extend(['underground_route', 'diplomatic_pouch'])
        
        return alternatives
    
    def _identify_trade_risk_factors(self, origin: str, destination: str, 
                                   route_tension: float) -> List[str]:
        """Identify specific risk factors for trade routes"""
        risks = []
        
        if route_tension > 0.7:
            risks.extend(['bandit_activity', 'military_checkpoints'])
        if route_tension > 0.5:
            risks.extend(['political_instability', 'supply_disruption'])
        if route_tension > 0.3:
            risks.extend(['increased_inspections', 'currency_fluctuation'])
        
        return risks
    
    def _get_trade_routes_to_region(self, region_id: str) -> List[str]:
        """Get all trade routes that include a specific region"""
        # This would query actual trade route data
        return [f"route_to_{region_id}_1", f"route_to_{region_id}_2"]
    
    def _apply_sanctions_to_route(self, route_id: str, severity: float) -> None:
        """Apply sanction effects to a specific trade route"""
        # This would modify actual trade route configurations
        logger.info(f"Applied sanctions to route {route_id} with severity {severity}")
    
    def _get_default_economic_modifiers(self) -> EconomicModifiers:
        """Get default economic modifiers when calculation fails"""
        return EconomicModifiers(
            effect_type=EconomicTensionEffect.STABLE_MARKET,
            price_modifiers={'default': 1.0},
            availability_modifiers={'default': 1.0},
            trade_route_modifications={'default': 1.0},
            market_operation_status={'primary_market': True},
            transaction_fees={'default': 1.0}
        )
    
    def _get_default_trade_route_status(self, route_id: str, origin: str, 
                                      destination: str) -> TradeRouteStatus:
        """Get default trade route status when calculation fails"""
        return TradeRouteStatus(
            route_id=route_id,
            origin_region=origin,
            destination_region=destination,
            safety_rating=0.5,
            price_impact=1.0,
            availability_impact=1.0,
            estimated_delay=None,
            recommended_alternatives=[],
            risk_factors=['unknown']
        )
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'integration_active': self.integration_active,
            'cached_economic_modifiers': len(self.economic_cache),
            'cached_trade_routes': len(self.trade_route_cache),
            'price_sensitivity': self.price_sensitivity,
            'thresholds': {
                'market_closure': self.market_closure_threshold,
                'embargo': self.embargo_threshold,
                'hoarding': self.hoarding_threshold
            }
        } 