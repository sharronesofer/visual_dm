from typing import Any, Dict, List, Union, Optional, Set
from enum import Enum
from dataclasses import dataclass, field


class ResourceType(Enum):
    FOOD = 'FOOD'
    WOOD = 'WOOD'
    STONE = 'STONE'
    METAL = 'METAL'
    CLOTH = 'CLOTH'
    LEATHER = 'LEATHER'
    HERBS = 'HERBS'
    GEMS = 'GEMS'
    MAGIC = 'MAGIC'

class ProductType(Enum):
    WEAPON = 'WEAPON'
    ARMOR = 'ARMOR'
    TOOL = 'TOOL'
    POTION = 'POTION'
    CLOTHING = 'CLOTHING'
    FURNITURE = 'FURNITURE'
    JEWELRY = 'JEWELRY'
    SCROLL = 'SCROLL'

@dataclass
class ResourceData:
    type: ResourceType
    name: str
    base_value: float
    weight: float
    perishable: bool
    shelf_life: Optional[float] = None

@dataclass
class ProductData:
    type: ProductType
    name: str
    base_value: float
    weight: float
    quality: float
    durability: float
    ingredients: Dict[ResourceType, float] = field(default_factory=dict)

@dataclass
class MarketData:
    id: str
    name: str
    location: Dict[str, Any]
    specialization: Optional[List[ProductType]] = None
    reputation: float = 0.0
    last_updated: float = 0.0

@dataclass
class TradeOffer:
    id: str
    seller_id: str
    item_type: Union[ResourceType, ProductType]
    quantity: float
    price_per_unit: float
    expires_at: float
    minimum_quantity: Optional[float] = None
    negotiable: bool = False

@dataclass
class Transaction:
    id: str
    timestamp: float
    buyer_id: str
    seller_id: str
    item_type: Union[ResourceType, ProductType]
    quantity: float
    price_per_unit: float
    market_id: Optional[str] = None

@dataclass
class ProductionRecipe:
    output: Dict[str, Any]
    inputs: List[tuple] = field(default_factory=list)
    production_time: float = 0.0
    failure_chance: float = 0.0

@dataclass
class EconomicRole:
    type: str
    production_recipes: Optional[List[ProductionRecipe]] = None
    trading_preferences: Optional[Dict[str, Any]] = None
    work_schedule: Optional[Dict[str, Any]] = None

@dataclass
class EconomicAgent:
    id: str
    role: EconomicRole
    inventory: Dict[Union[ResourceType, ProductType], float] = field(default_factory=dict)
    currency: float = 0.0
    reputation: float = 0.0
    activeOffers: Set[str] = field(default_factory=set)
    productionQueue: List[Dict[str, Any]] = field(default_factory=list)
    lastTransaction: float = 0.0

@dataclass
class PriceStats:
    average_price: float
    median_price: float
    min_price: float
    max_price: float
    num_transactions: float

@dataclass
class MarketPriceData:
    item_type: Union[ResourceType, ProductType]
    average_price: float
    min_price: float
    max_price: float
    volume: float
    trend: float
    last_update: float

@dataclass
class EconomicEvent:
    type: str
    affected_items: List[Union[ResourceType, ProductType]]
    multiplier: float
    duration: float
    scope: Optional[Dict[str, Any]] = None
    start_time: float = 0.0
    description: str = '' 