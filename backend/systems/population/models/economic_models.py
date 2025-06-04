"""
Economic Models for Population System (Business Logic)

Defines economic structures that influence population dynamics including:
- Economic prosperity and its effects on population growth
- Trade route systems and migration patterns
- Resource abundance and scarcity effects
- Economic events and their population impacts

This is business logic code that models economic systems affecting populations.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)


class EconomicStatus(Enum):
    """Economic status levels"""
    COLLAPSE = "collapse"           # -0.8 to -1.0 prosperity
    DEPRESSION = "depression"       # -0.4 to -0.8 prosperity
    RECESSION = "recession"         # -0.2 to -0.4 prosperity
    STAGNANT = "stagnant"          # -0.1 to 0.1 prosperity
    STABLE = "stable"              # 0.1 to 0.4 prosperity
    GROWING = "growing"            # 0.4 to 0.7 prosperity
    BOOMING = "booming"            # 0.7 to 1.0 prosperity


class ResourceType(Enum):
    """Types of resources that affect population"""
    FOOD = "food"
    WATER = "water"
    MEDICINE = "medicine"
    MATERIALS = "materials"
    LUXURY_GOODS = "luxury_goods"
    TOOLS = "tools"
    FUEL = "fuel"
    PRECIOUS_METALS = "precious_metals"


class TradeRouteStatus(Enum):
    """Status of trade routes"""
    BLOCKED = "blocked"
    DANGEROUS = "dangerous"
    SAFE = "safe"
    PROTECTED = "protected"


@dataclass
class ResourceAvailability:
    """Resource availability and pricing information"""
    resource_type: ResourceType
    base_availability: float = 1.0  # 1.0 = normal availability
    current_price_modifier: float = 1.0  # Price multiplier
    scarcity_level: float = 0.0  # 0.0 = abundant, 1.0 = scarce
    quality_modifier: float = 1.0  # Quality of available resources
    
    # Population effects
    population_growth_modifier: float = 1.0
    disease_resistance_modifier: float = 1.0
    migration_attractiveness_modifier: float = 1.0
    
    def get_abundance_category(self) -> str:
        """Get human-readable abundance category"""
        if self.scarcity_level < 0.2:
            return "abundant"
        elif self.scarcity_level < 0.4:
            return "plentiful"
        elif self.scarcity_level < 0.6:
            return "adequate"
        elif self.scarcity_level < 0.8:
            return "scarce"
        else:
            return "critical_shortage"


@dataclass
class TradeRoute:
    """Trade route connecting settlements"""
    route_id: str
    origin_settlement: str
    destination_settlement: str
    distance: float
    safety_level: TradeRouteStatus
    
    # Trade characteristics
    primary_goods: List[ResourceType]
    trade_volume_modifier: float = 1.0
    travel_time_days: int = 7
    
    # Effects on settlements
    prosperity_bonus: float = 0.1
    migration_influence: float = 0.05
    
    # Route conditions
    is_active: bool = True
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def get_effective_trade_bonus(self) -> float:
        """Calculate effective trade bonus based on route conditions"""
        if not self.is_active:
            return 0.0
        
        safety_multipliers = {
            TradeRouteStatus.BLOCKED: 0.0,
            TradeRouteStatus.DANGEROUS: 0.3,
            TradeRouteStatus.SAFE: 1.0,
            TradeRouteStatus.PROTECTED: 1.2
        }
        
        safety_multiplier = safety_multipliers.get(self.safety_level, 1.0)
        return self.prosperity_bonus * self.trade_volume_modifier * safety_multiplier


@dataclass
class EconomicEvent:
    """Economic events that affect population"""
    event_id: str
    event_type: str
    name: str
    description: str
    
    # Event timing
    start_date: datetime
    duration_days: int
    affected_settlements: List[str]
    
    # Population effects
    population_growth_modifier: float = 1.0
    migration_pressure_modifier: float = 1.0
    disease_resistance_modifier: float = 1.0
    fertility_modifier: float = 1.0
    mortality_modifier: float = 1.0
    
    # Economic effects
    prosperity_change: float = 0.0
    resource_effects: Dict[ResourceType, float] = field(default_factory=dict)
    trade_route_effects: Dict[str, float] = field(default_factory=dict)
    
    # Event state
    is_active: bool = True
    completion_effects: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EconomicState:
    """Economic state of a settlement"""
    settlement_id: str
    
    # Core economic metrics
    prosperity_level: float = 0.0  # -1.0 to 1.0
    wealth_per_capita: float = 100.0
    trade_volume: float = 1.0
    
    # Resource availability
    resources: Dict[ResourceType, ResourceAvailability] = field(default_factory=dict)
    
    # Trade connections
    active_trade_routes: List[str] = field(default_factory=list)
    trade_partners: List[str] = field(default_factory=list)
    
    # Economic trends
    prosperity_trend: float = 0.0  # Rate of change
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    # Economic events
    active_events: List[str] = field(default_factory=list)
    
    def get_economic_status(self) -> EconomicStatus:
        """Determine economic status based on prosperity level"""
        if self.prosperity_level <= -0.8:
            return EconomicStatus.COLLAPSE
        elif self.prosperity_level <= -0.4:
            return EconomicStatus.DEPRESSION
        elif self.prosperity_level <= -0.2:
            return EconomicStatus.RECESSION
        elif self.prosperity_level <= 0.1:
            return EconomicStatus.STAGNANT
        elif self.prosperity_level <= 0.4:
            return EconomicStatus.STABLE
        elif self.prosperity_level <= 0.7:
            return EconomicStatus.GROWING
        else:
            return EconomicStatus.BOOMING
    
    def get_population_growth_modifier(self) -> float:
        """Calculate population growth modifier based on economic conditions"""
        base_modifier = 1.0 + (self.prosperity_level * 0.3)  # ±30% based on prosperity
        
        # Resource effects
        resource_modifier = 1.0
        critical_resources = [ResourceType.FOOD, ResourceType.WATER, ResourceType.MEDICINE]
        
        for resource_type in critical_resources:
            if resource_type in self.resources:
                resource = self.resources[resource_type]
                resource_modifier *= resource.population_growth_modifier
        
        return max(0.1, base_modifier * resource_modifier)  # Minimum 10% of normal growth
    
    def get_disease_resistance_modifier(self) -> float:
        """Calculate disease resistance modifier based on economic conditions"""
        base_modifier = 1.0 + (self.prosperity_level * 0.2)  # ±20% based on prosperity
        
        # Medicine and food security effects
        medicine_modifier = 1.0
        if ResourceType.MEDICINE in self.resources:
            medicine = self.resources[ResourceType.MEDICINE]
            medicine_modifier = medicine.disease_resistance_modifier
        
        food_modifier = 1.0
        if ResourceType.FOOD in self.resources:
            food = self.resources[ResourceType.FOOD]
            # Well-fed populations resist disease better
            food_modifier = 1.0 + ((1.0 - food.scarcity_level) * 0.3)
        
        return max(0.5, base_modifier * medicine_modifier * food_modifier)
    
    def get_migration_attractiveness(self) -> float:
        """Calculate how attractive this settlement is for migration"""
        base_attractiveness = self.prosperity_level * 0.5  # Prosperity is major factor
        
        # Trade routes increase attractiveness
        trade_bonus = len(self.active_trade_routes) * 0.1
        
        # Resource availability effects
        resource_bonus = 0.0
        for resource in self.resources.values():
            resource_bonus += resource.migration_attractiveness_modifier * 0.1
        
        return max(-1.0, min(1.0, base_attractiveness + trade_bonus + resource_bonus))


class EconomicEngine:
    """Engine for managing economic systems and their effects on population"""
    
    def __init__(self):
        self.economic_states: Dict[str, EconomicState] = {}
        self.trade_routes: Dict[str, TradeRoute] = {}
        self.active_events: Dict[str, EconomicEvent] = {}
        self.event_counter = 0
    
    def get_economic_state(self, settlement_id: str) -> EconomicState:
        """Get or create economic state for a settlement"""
        if settlement_id not in self.economic_states:
            self.economic_states[settlement_id] = EconomicState(
                settlement_id=settlement_id
            )
            self._initialize_default_resources(settlement_id)
        
        return self.economic_states[settlement_id]
    
    def _initialize_default_resources(self, settlement_id: str):
        """Initialize default resource availability for a settlement"""
        state = self.economic_states[settlement_id]
        
        # Basic resources with normal availability
        for resource_type in ResourceType:
            availability = ResourceAvailability(
                resource_type=resource_type,
                base_availability=random.uniform(0.8, 1.2),  # Some variation
                scarcity_level=random.uniform(0.2, 0.6),  # Moderate scarcity
                quality_modifier=random.uniform(0.9, 1.1)
            )
            
            # Set population effects based on resource type
            if resource_type == ResourceType.FOOD:
                availability.population_growth_modifier = 1.0 + (1.0 - availability.scarcity_level) * 0.5
                availability.disease_resistance_modifier = 1.0 + (1.0 - availability.scarcity_level) * 0.2
            elif resource_type == ResourceType.MEDICINE:
                availability.disease_resistance_modifier = 1.0 + (1.0 - availability.scarcity_level) * 0.8
            elif resource_type == ResourceType.LUXURY_GOODS:
                availability.migration_attractiveness_modifier = 1.0 + (1.0 - availability.scarcity_level) * 0.3
            
            state.resources[resource_type] = availability
    
    def update_resource_availability(
        self,
        settlement_id: str,
        resource_type: ResourceType,
        scarcity_change: float,
        quality_change: float = 0.0
    ):
        """Update resource availability for a settlement"""
        state = self.get_economic_state(settlement_id)
        
        if resource_type in state.resources:
            resource = state.resources[resource_type]
            resource.scarcity_level = max(0.0, min(1.0, resource.scarcity_level + scarcity_change))
            resource.quality_modifier = max(0.1, min(2.0, resource.quality_modifier + quality_change))
            
            # Update price based on scarcity
            resource.current_price_modifier = 1.0 + (resource.scarcity_level * 2.0)
            
            logger.info(f"Updated {resource_type.value} in {settlement_id}: scarcity={resource.scarcity_level:.2f}")
    
    def create_trade_route(
        self,
        origin: str,
        destination: str,
        primary_goods: List[ResourceType],
        distance: float = 100.0,
        safety_level: TradeRouteStatus = TradeRouteStatus.SAFE
    ) -> str:
        """Create a new trade route between settlements"""
        route_id = f"route_{origin}_{destination}_{len(self.trade_routes)}"
        
        trade_route = TradeRoute(
            route_id=route_id,
            origin_settlement=origin,
            destination_settlement=destination,
            distance=distance,
            safety_level=safety_level,
            primary_goods=primary_goods,
            travel_time_days=max(1, int(distance / 20))  # Rough travel time calculation
        )
        
        self.trade_routes[route_id] = trade_route
        
        # Update settlement trade connections
        origin_state = self.get_economic_state(origin)
        dest_state = self.get_economic_state(destination)
        
        origin_state.active_trade_routes.append(route_id)
        dest_state.active_trade_routes.append(route_id)
        
        if destination not in origin_state.trade_partners:
            origin_state.trade_partners.append(destination)
        if origin not in dest_state.trade_partners:
            dest_state.trade_partners.append(origin)
        
        logger.info(f"Created trade route {route_id}: {origin} -> {destination}")
        return route_id
    
    def update_trade_route_safety(self, route_id: str, new_safety: TradeRouteStatus):
        """Update the safety level of a trade route"""
        if route_id in self.trade_routes:
            old_safety = self.trade_routes[route_id].safety_level
            self.trade_routes[route_id].safety_level = new_safety
            self.trade_routes[route_id].last_updated = datetime.utcnow()
            
            logger.info(f"Trade route {route_id} safety: {old_safety.value} -> {new_safety.value}")
    
    def create_economic_event(
        self,
        event_type: str,
        name: str,
        description: str,
        affected_settlements: List[str],
        duration_days: int = 30,
        **effects
    ) -> str:
        """Create a new economic event"""
        self.event_counter += 1
        event_id = f"eco_event_{event_type}_{self.event_counter}"
        
        event = EconomicEvent(
            event_id=event_id,
            event_type=event_type,
            name=name,
            description=description,
            start_date=datetime.utcnow(),
            duration_days=duration_days,
            affected_settlements=affected_settlements,
            **effects
        )
        
        self.active_events[event_id] = event
        
        # Apply immediate effects
        for settlement_id in affected_settlements:
            state = self.get_economic_state(settlement_id)
            state.active_events.append(event_id)
            
            # Apply prosperity change
            if hasattr(event, 'prosperity_change'):
                state.prosperity_level += event.prosperity_change
                state.prosperity_level = max(-1.0, min(1.0, state.prosperity_level))
        
        logger.info(f"Created economic event: {name} affecting {len(affected_settlements)} settlements")
        return event_id
    
    def progress_economic_day(self, settlement_id: str) -> Dict[str, Any]:
        """Progress economic conditions for one day"""
        state = self.get_economic_state(settlement_id)
        
        # Natural prosperity fluctuation
        prosperity_change = random.uniform(-0.01, 0.01)  # Small daily variation
        
        # Trade route effects
        trade_bonus = 0.0
        for route_id in state.active_trade_routes:
            if route_id in self.trade_routes:
                route = self.trade_routes[route_id]
                trade_bonus += route.get_effective_trade_bonus() / 100  # Daily effect
        
        # Apply changes
        state.prosperity_level += prosperity_change + trade_bonus
        state.prosperity_level = max(-1.0, min(1.0, state.prosperity_level))
        state.prosperity_trend = prosperity_change + trade_bonus
        state.last_updated = datetime.utcnow()
        
        # Process active events
        self._process_active_events(settlement_id)
        
        return {
            "settlement_id": settlement_id,
            "prosperity_level": state.prosperity_level,
            "prosperity_change": prosperity_change + trade_bonus,
            "economic_status": state.get_economic_status().value,
            "trade_routes_active": len(state.active_trade_routes),
            "active_events": len(state.active_events)
        }
    
    def _process_active_events(self, settlement_id: str):
        """Process active economic events for a settlement"""
        state = self.get_economic_state(settlement_id)
        events_to_remove = []
        
        for event_id in state.active_events:
            if event_id in self.active_events:
                event = self.active_events[event_id]
                
                # Check if event has expired
                if datetime.utcnow() > event.start_date + timedelta(days=event.duration_days):
                    events_to_remove.append(event_id)
                    event.is_active = False
                    
                    # Apply completion effects
                    if event.completion_effects:
                        self._apply_completion_effects(settlement_id, event.completion_effects)
        
        # Remove expired events
        for event_id in events_to_remove:
            state.active_events.remove(event_id)
    
    def _apply_completion_effects(self, settlement_id: str, completion_effects: Dict[str, Any]):
        """Apply effects when an economic event completes"""
        state = self.get_economic_state(settlement_id)
        
        # Apply prosperity changes
        if 'prosperity_change' in completion_effects:
            state.prosperity_level += completion_effects['prosperity_change']
            state.prosperity_level = max(-1.0, min(1.0, state.prosperity_level))
        
        # Apply resource changes
        if 'resource_changes' in completion_effects:
            for resource_type_str, change in completion_effects['resource_changes'].items():
                try:
                    resource_type = ResourceType(resource_type_str)
                    self.update_resource_availability(settlement_id, resource_type, change)
                except ValueError:
                    logger.warning(f"Unknown resource type in completion effects: {resource_type_str}")
    
    def get_population_effects(self, settlement_id: str) -> Dict[str, float]:
        """Get economic effects on population for a settlement"""
        state = self.get_economic_state(settlement_id)
        
        return {
            "population_growth_modifier": state.get_population_growth_modifier(),
            "disease_resistance_modifier": state.get_disease_resistance_modifier(),
            "migration_attractiveness": state.get_migration_attractiveness(),
            "economic_status": state.get_economic_status().value,
            "prosperity_level": state.prosperity_level,
            "trade_route_count": len(state.active_trade_routes)
        }


# Global economic engine instance
economic_engine = EconomicEngine()

# Export functions
__all__ = [
    "EconomicStatus",
    "ResourceType", 
    "TradeRouteStatus",
    "ResourceAvailability",
    "TradeRoute",
    "EconomicEvent",
    "EconomicState",
    "EconomicEngine",
    "economic_engine"
] 