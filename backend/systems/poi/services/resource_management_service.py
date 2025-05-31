"""
Resource Management Service

Handles resource production, consumption, trading, and storage management
for Points of Interest in the POI system.
"""

from typing import Dict, List, Optional, Tuple, Set, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from backend.systems.poi.models import PoiEntity, POIType, POIState
from backend.infrastructure.database import get_db
from backend.infrastructure.events import EventDispatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    """Types of resources in the game world"""
    # Basic Resources
    FOOD = "food"
    WATER = "water"
    WOOD = "wood"
    STONE = "stone"
    METAL = "metal"
    
    # Manufactured Goods
    TOOLS = "tools"
    WEAPONS = "weapons"
    ARMOR = "armor"
    CLOTHING = "clothing"
    POTTERY = "pottery"
    
    # Trade Goods
    SPICES = "spices"
    GEMS = "gems"
    SILK = "silk"
    WINE = "wine"
    
    # Special Resources
    MAGICAL_COMPONENTS = "magical_components"
    RARE_HERBS = "rare_herbs"
    GOLD = "gold"
    SILVER = "silver"


class ResourceCategory(str, Enum):
    """Categories for grouping resources"""
    BASIC = "basic"
    MANUFACTURED = "manufactured"
    LUXURY = "luxury"
    MAGICAL = "magical"
    CURRENCY = "currency"


class ProductionModifier(str, Enum):
    """Modifiers that affect resource production"""
    WEATHER = "weather"
    SEASON = "season"
    POPULATION = "population"
    TECHNOLOGY = "technology"
    FACTION_CONTROL = "faction_control"
    MAGICAL_INFLUENCE = "magical_influence"


@dataclass
class Resource:
    """Represents a single resource type with its properties"""
    type: ResourceType
    category: ResourceCategory
    base_value: Decimal
    weight_per_unit: float
    spoilage_rate: float = 0.0  # Units lost per day
    storage_requirements: str = "normal"
    
    def get_spoiled_amount(self, quantity: Decimal, days: int) -> Decimal:
        """Calculate how much of this resource spoils over time"""
        if self.spoilage_rate == 0:
            return Decimal('0')
        return min(quantity, quantity * Decimal(str(self.spoilage_rate)) * Decimal(str(days)))


@dataclass
class ResourceStock:
    """Represents a stock of resources at a POI"""
    resource_type: ResourceType
    quantity: Decimal
    quality: float = 1.0  # 0.0 to 1.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    reserved: Decimal = field(default=Decimal('0'))  # Reserved for trades/commitments
    
    @property
    def available(self) -> Decimal:
        """Get available quantity (total - reserved)"""
        return max(Decimal('0'), self.quantity - self.reserved)
    
    def reserve(self, amount: Decimal) -> bool:
        """Reserve resources for a transaction"""
        if amount <= self.available:
            self.reserved += amount
            return True
        return False
    
    def release_reservation(self, amount: Decimal):
        """Release reserved resources"""
        self.reserved = max(Decimal('0'), self.reserved - amount)
    
    def consume(self, amount: Decimal) -> Decimal:
        """Consume resources and return actual amount consumed"""
        consumable = min(amount, self.quantity)
        self.quantity -= consumable
        self.reserved = max(Decimal('0'), self.reserved - consumable)
        self.last_updated = datetime.utcnow()
        return consumable
    
    def add(self, amount: Decimal, quality: float = 1.0):
        """Add resources to stock"""
        if self.quantity == 0:
            self.quality = quality
        else:
            # Weighted average of qualities
            total_value = (self.quantity * Decimal(str(self.quality))) + (amount * Decimal(str(quality)))
            self.quantity += amount
            self.quality = float(total_value / self.quantity)
        self.last_updated = datetime.utcnow()


@dataclass
class ProductionCapability:
    """Represents a POI's ability to produce a resource"""
    resource_type: ResourceType
    base_production_rate: Decimal  # Units per day
    efficiency: float = 1.0  # Current efficiency multiplier
    input_requirements: Dict[ResourceType, Decimal] = field(default_factory=dict)
    workforce_requirement: int = 0
    technology_level: int = 1
    
    def get_daily_production(self, modifiers: Dict[ProductionModifier, float] = None) -> Decimal:
        """Calculate daily production considering modifiers"""
        modifiers = modifiers or {}
        
        total_modifier = self.efficiency
        for modifier, value in modifiers.items():
            total_modifier *= value
        
        return self.base_production_rate * Decimal(str(total_modifier))


@dataclass
class TradeOffer:
    """Represents a trade offer between POIs"""
    id: UUID
    from_poi_id: UUID
    to_poi_id: UUID
    offered_resources: Dict[ResourceType, Decimal]
    requested_resources: Dict[ResourceType, Decimal]
    status: str = "pending"  # pending, accepted, rejected, expired
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if the trade offer has expired"""
        return self.expires_at and datetime.utcnow() > self.expires_at


class ResourceManagementService:
    """Service for managing resource production, consumption, and trading"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db()
        self.event_dispatcher = EventDispatcher()
        
        # Initialize resource definitions
        self.resource_definitions = self._initialize_resource_definitions()
        
        # Trade and production data (in a real system, this would be in the database)
        self.poi_resources: Dict[UUID, Dict[ResourceType, ResourceStock]] = {}
        self.production_capabilities: Dict[UUID, List[ProductionCapability]] = {}
        self.trade_offers: Dict[UUID, TradeOffer] = {}
        
        # Configuration
        self.trade_distance_limit = 100.0  # Maximum distance for trade routes
        self.storage_efficiency = 0.95  # 5% storage loss
    
    def _initialize_resource_definitions(self) -> Dict[ResourceType, Resource]:
        """Initialize the definitions for all resource types"""
        return {
            ResourceType.FOOD: Resource(
                ResourceType.FOOD, ResourceCategory.BASIC, 
                Decimal('1'), 1.0, 0.1, "cold_storage"
            ),
            ResourceType.WATER: Resource(
                ResourceType.WATER, ResourceCategory.BASIC,
                Decimal('0.1'), 1.0, 0.05, "containers"
            ),
            ResourceType.WOOD: Resource(
                ResourceType.WOOD, ResourceCategory.BASIC,
                Decimal('2'), 0.5, 0.0, "dry_storage"
            ),
            ResourceType.STONE: Resource(
                ResourceType.STONE, ResourceCategory.BASIC,
                Decimal('1'), 2.0, 0.0, "outdoor"
            ),
            ResourceType.METAL: Resource(
                ResourceType.METAL, ResourceCategory.BASIC,
                Decimal('10'), 5.0, 0.0, "dry_storage"
            ),
            ResourceType.TOOLS: Resource(
                ResourceType.TOOLS, ResourceCategory.MANUFACTURED,
                Decimal('25'), 2.0, 0.001, "normal"
            ),
            ResourceType.WEAPONS: Resource(
                ResourceType.WEAPONS, ResourceCategory.MANUFACTURED,
                Decimal('50'), 3.0, 0.001, "armory"
            ),
            ResourceType.SPICES: Resource(
                ResourceType.SPICES, ResourceCategory.LUXURY,
                Decimal('100'), 0.1, 0.02, "dry_storage"
            ),
            ResourceType.GOLD: Resource(
                ResourceType.GOLD, ResourceCategory.CURRENCY,
                Decimal('1000'), 0.02, 0.0, "vault"
            )
        }
    
    def initialize_poi_resources(self, poi_id: UUID, initial_resources: Dict[ResourceType, Decimal] = None):
        """Initialize resource stocks for a POI"""
        try:
            if poi_id not in self.poi_resources:
                self.poi_resources[poi_id] = {}
            
            # Add initial resources if provided
            if initial_resources:
                for resource_type, quantity in initial_resources.items():
                    self.add_resources(poi_id, resource_type, quantity)
            
            logger.info(f"Initialized resources for POI {poi_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing POI resources: {e}")
            return False
    
    def add_production_capability(self, poi_id: UUID, capability: ProductionCapability) -> bool:
        """Add a production capability to a POI"""
        try:
            if poi_id not in self.production_capabilities:
                self.production_capabilities[poi_id] = []
            
            self.production_capabilities[poi_id].append(capability)
            
            logger.info(f"Added production capability for {capability.resource_type} to POI {poi_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding production capability: {e}")
            return False
    
    def process_daily_production(self, poi_id: UUID) -> Dict[ResourceType, Decimal]:
        """Process daily resource production for a POI"""
        try:
            production_results = {}
            
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                return production_results
            
            capabilities = self.production_capabilities.get(poi_id, [])
            
            for capability in capabilities:
                # Check input requirements
                can_produce = True
                for input_type, required_amount in capability.input_requirements.items():
                    available = self.get_resource_quantity(poi_id, input_type)
                    if available < required_amount:
                        can_produce = False
                        break
                
                if not can_produce:
                    continue
                
                # Consume input resources
                for input_type, required_amount in capability.input_requirements.items():
                    self.consume_resources(poi_id, input_type, required_amount)
                
                # Calculate production modifiers
                modifiers = self._calculate_production_modifiers(poi, capability)
                
                # Produce resources
                produced = capability.get_daily_production(modifiers)
                self.add_resources(poi_id, capability.resource_type, produced)
                
                production_results[capability.resource_type] = produced
            
            return production_results
            
        except Exception as e:
            logger.error(f"Error processing daily production: {e}")
            return {}
    
    def consume_resources(self, poi_id: UUID, resource_type: ResourceType, amount: Decimal) -> Decimal:
        """Consume resources from a POI"""
        try:
            if poi_id not in self.poi_resources:
                return Decimal('0')
            
            stock = self.poi_resources[poi_id].get(resource_type)
            if not stock:
                return Decimal('0')
            
            consumed = stock.consume(amount)
            
            # Dispatch consumption event
            self.event_dispatcher.publish({
                'type': 'resource_consumed',
                'poi_id': str(poi_id),
                'resource_type': resource_type.value,
                'amount': str(consumed),
                'remaining': str(stock.quantity),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return consumed
            
        except Exception as e:
            logger.error(f"Error consuming resources: {e}")
            return Decimal('0')
    
    def add_resources(self, poi_id: UUID, resource_type: ResourceType, amount: Decimal, quality: float = 1.0):
        """Add resources to a POI"""
        try:
            if poi_id not in self.poi_resources:
                self.poi_resources[poi_id] = {}
            
            if resource_type not in self.poi_resources[poi_id]:
                self.poi_resources[poi_id][resource_type] = ResourceStock(
                    resource_type=resource_type,
                    quantity=Decimal('0')
                )
            
            stock = self.poi_resources[poi_id][resource_type]
            stock.add(amount, quality)
            
            # Dispatch addition event
            self.event_dispatcher.publish({
                'type': 'resource_added',
                'poi_id': str(poi_id),
                'resource_type': resource_type.value,
                'amount': str(amount),
                'quality': quality,
                'total': str(stock.quantity),
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error adding resources: {e}")
    
    def get_resource_quantity(self, poi_id: UUID, resource_type: ResourceType) -> Decimal:
        """Get available quantity of a resource at a POI"""
        try:
            if poi_id not in self.poi_resources:
                return Decimal('0')
            
            stock = self.poi_resources[poi_id].get(resource_type)
            return stock.available if stock else Decimal('0')
            
        except Exception as e:
            logger.error(f"Error getting resource quantity: {e}")
            return Decimal('0')
    
    def get_all_resources(self, poi_id: UUID) -> Dict[ResourceType, ResourceStock]:
        """Get all resource stocks for a POI"""
        return self.poi_resources.get(poi_id, {}).copy()
    
    def create_trade_offer(self, from_poi_id: UUID, to_poi_id: UUID, 
                          offered: Dict[ResourceType, Decimal], 
                          requested: Dict[ResourceType, Decimal],
                          duration_hours: int = 24) -> Optional[TradeOffer]:
        """Create a trade offer between POIs"""
        try:
            # Validate that offering POI has the resources
            for resource_type, amount in offered.items():
                available = self.get_resource_quantity(from_poi_id, resource_type)
                if available < amount:
                    logger.warning(f"Insufficient {resource_type} for trade offer")
                    return None
            
            # Check trade distance
            if not self._can_trade_between_pois(from_poi_id, to_poi_id):
                logger.warning(f"POIs too far apart for trade")
                return None
            
            # Reserve the offered resources
            for resource_type, amount in offered.items():
                stock = self.poi_resources[from_poi_id][resource_type]
                stock.reserve(amount)
            
            # Create trade offer
            trade_offer = TradeOffer(
                id=UUID(),
                from_poi_id=from_poi_id,
                to_poi_id=to_poi_id,
                offered_resources=offered,
                requested_resources=requested,
                expires_at=datetime.utcnow() + timedelta(hours=duration_hours)
            )
            
            self.trade_offers[trade_offer.id] = trade_offer
            
            # Dispatch trade offer event
            self.event_dispatcher.publish({
                'type': 'trade_offer_created',
                'offer_id': str(trade_offer.id),
                'from_poi': str(from_poi_id),
                'to_poi': str(to_poi_id),
                'offered': {k.value: str(v) for k, v in offered.items()},
                'requested': {k.value: str(v) for k, v in requested.items()},
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return trade_offer
            
        except Exception as e:
            logger.error(f"Error creating trade offer: {e}")
            return None
    
    def accept_trade_offer(self, offer_id: UUID) -> bool:
        """Accept a trade offer"""
        try:
            offer = self.trade_offers.get(offer_id)
            if not offer or offer.is_expired():
                return False
            
            # Validate that receiving POI has the requested resources
            for resource_type, amount in offer.requested_resources.items():
                available = self.get_resource_quantity(offer.to_poi_id, resource_type)
                if available < amount:
                    return False
            
            # Execute the trade
            # Remove requested resources from receiving POI
            for resource_type, amount in offer.requested_resources.items():
                self.consume_resources(offer.to_poi_id, resource_type, amount)
            
            # Add offered resources to receiving POI
            for resource_type, amount in offer.offered_resources.items():
                self.add_resources(offer.to_poi_id, resource_type, amount)
            
            # Remove offered resources from offering POI
            for resource_type, amount in offer.offered_resources.items():
                self.consume_resources(offer.from_poi_id, resource_type, amount)
            
            # Add requested resources to offering POI
            for resource_type, amount in offer.requested_resources.items():
                self.add_resources(offer.from_poi_id, resource_type, amount)
            
            offer.status = "accepted"
            
            # Dispatch trade completion event
            self.event_dispatcher.publish({
                'type': 'trade_completed',
                'offer_id': str(offer_id),
                'from_poi': str(offer.from_poi_id),
                'to_poi': str(offer.to_poi_id),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error accepting trade offer: {e}")
            return False
    
    def process_resource_spoilage(self, poi_id: UUID) -> Dict[ResourceType, Decimal]:
        """Process daily resource spoilage for a POI"""
        try:
            spoilage_results = {}
            
            if poi_id not in self.poi_resources:
                return spoilage_results
            
            for resource_type, stock in self.poi_resources[poi_id].items():
                resource_def = self.resource_definitions.get(resource_type)
                if not resource_def or resource_def.spoilage_rate == 0:
                    continue
                
                spoiled = resource_def.get_spoiled_amount(stock.quantity, 1)
                if spoiled > 0:
                    stock.consume(spoiled)
                    spoilage_results[resource_type] = spoiled
            
            return spoilage_results
            
        except Exception as e:
            logger.error(f"Error processing resource spoilage: {e}")
            return {}
    
    def calculate_resource_value(self, poi_id: UUID) -> Decimal:
        """Calculate total value of all resources at a POI"""
        try:
            total_value = Decimal('0')
            
            for resource_type, stock in self.poi_resources.get(poi_id, {}).items():
                resource_def = self.resource_definitions.get(resource_type)
                if resource_def:
                    value = stock.quantity * resource_def.base_value * Decimal(str(stock.quality))
                    total_value += value
            
            return total_value
            
        except Exception as e:
            logger.error(f"Error calculating resource value: {e}")
            return Decimal('0')
    
    def get_resource_deficit(self, poi_id: UUID) -> Dict[ResourceType, Decimal]:
        """Calculate resource deficits based on population needs"""
        try:
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                return {}
            
            population = poi.population or 0
            deficits = {}
            
            # Basic needs calculation
            daily_food_need = Decimal(str(population * 2))  # 2 food per person per day
            daily_water_need = Decimal(str(population * 3))  # 3 water per person per day
            
            current_food = self.get_resource_quantity(poi_id, ResourceType.FOOD)
            current_water = self.get_resource_quantity(poi_id, ResourceType.WATER)
            
            if current_food < daily_food_need:
                deficits[ResourceType.FOOD] = daily_food_need - current_food
            
            if current_water < daily_water_need:
                deficits[ResourceType.WATER] = daily_water_need - current_water
            
            return deficits
            
        except Exception as e:
            logger.error(f"Error calculating resource deficit: {e}")
            return {}
    
    def _calculate_production_modifiers(self, poi: PoiEntity, capability: ProductionCapability) -> Dict[ProductionModifier, float]:
        """Calculate production modifiers for a POI"""
        modifiers = {}
        
        # Population modifier
        if capability.workforce_requirement > 0:
            workforce_ratio = (poi.population or 0) / capability.workforce_requirement
            modifiers[ProductionModifier.POPULATION] = min(workforce_ratio, 1.0)
        
        # Seasonal modifier (simplified)
        modifiers[ProductionModifier.SEASON] = 1.0
        
        # Weather modifier (simplified)
        modifiers[ProductionModifier.WEATHER] = 1.0
        
        return modifiers
    
    def _can_trade_between_pois(self, poi1_id: UUID, poi2_id: UUID) -> bool:
        """Check if two POIs can trade based on distance"""
        try:
            poi1 = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi1_id).first()
            poi2 = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi2_id).first()
            
            if not poi1 or not poi2:
                return False
            
            if not all([poi1.location_x, poi1.location_y, poi2.location_x, poi2.location_y]):
                return False
            
            distance = ((poi1.location_x - poi2.location_x) ** 2 + 
                       (poi1.location_y - poi2.location_y) ** 2) ** 0.5
            
            return distance <= self.trade_distance_limit
            
        except Exception as e:
            logger.error(f"Error checking trade distance: {e}")
            return False


# Factory function for dependency injection
def get_resource_management_service(db_session: Optional[Session] = None) -> ResourceManagementService:
    """Factory function to create ResourceManagementService instance"""
    return ResourceManagementService(db_session) 