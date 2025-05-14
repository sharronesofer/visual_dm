from typing import Any, Dict, List, Union
from enum import Enum



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
class ResourceData:
    type: \'ResourceType\'
    name: str
    baseValue: float
    weight: float
    perishable: bool
    shelfLife?: float
class ProductData:
    type: \'ProductType\'
    name: str
    baseValue: float
    weight: float
    quality: float
    durability: float
    ingredients: Dict[ResourceType, float>
class MarketData:
    id: str
    name: str
    location: Dict[str, Any]
  specialization?: ProductType[]
  reputation: float 
  lastUpdated: float
}
class TradeOffer:
    id: str
    sellerId: str
    itemType: Union[ResourceType, ProductType]
    quantity: float
    pricePerUnit: float
    expiresAt: float
    minimumQuantity?: float
    negotiable: bool
class Transaction:
    id: str
    timestamp: float
    buyerId: str
    sellerId: str
    itemType: Union[ResourceType, ProductType]
    quantity: float
    pricePerUnit: float
    marketId?: str
class ProductionRecipe:
    output: Dict[str, Any]
class EconomicRole:
    type: str
    productionRecipes?: List[ProductionRecipe]
    tradingPreferences?: List[{
    preferredResources: ResourceType]
    preferredProducts: List[ProductType]
    priceMarkup: float
    negotiationFlexibility: float
  workSchedule?: {
    startHour: float
    endHour: float
    workDays: List[number]
  }
}
class EconomicAgent:
    id: str
    role: \'EconomicRole\'
    inventory: Dict[str, float>
    currency: float
    reputation: float
    activeOffers: Set[str>
    productionQueue: Dict[str, Any]
class PriceStats:
    averagePrice: float
    medianPrice: float
    minPrice: float
    maxPrice: float
    numTransactions: float
class MarketPriceData:
    itemType: Union[ResourceType, ProductType]
    averagePrice: float
    minPrice: float
    maxPrice: float
    volume: float
    trend: float
    lastUpdate: float
class EconomicEvent:
    type: str
    affectedItems: List[Union[(ResourceType, ProductType)]]
    multiplier: float
    duration: float
    scope: List[{
    marketIds?: str]
    regionIds?: List[str]
    global: bool
  startTime: float
  description: str
} 