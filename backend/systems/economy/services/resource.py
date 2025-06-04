"""Resource management module with rich production mechanics."""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class ResourceCategory(Enum):
    """Resource categories for classification"""
    RAW_MATERIALS = "raw_materials"
    FOOD_RESOURCES = "food_resources" 
    LUXURY_GOODS = "luxury_goods"
    MANUFACTURED_GOODS = "manufactured_goods"
    MAGICAL_COMPONENTS = "magical_components"


class StorageType(Enum):
    """Storage types with different decay rates"""
    OUTDOOR = "outdoor"
    SHED = "shed" 
    WAREHOUSE = "warehouse"
    GRANARY = "granary"
    CLIMATE_CONTROLLED = "climate_controlled"
    MAGICAL_VAULT = "magical_vault"


@dataclass
class ProductionRequirements:
    """Production requirements for a resource"""
    biome_types: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    skill_required: Optional[str] = None
    time_to_harvest: int = 1  # in hours
    renewable: bool = True
    renewal_time: Optional[int] = None  # in days
    depletion_rate: Optional[float] = None  # for non-renewable resources
    seasonal: bool = False
    seasons: List[str] = field(default_factory=list)
    climate_dependent: bool = False
    requires_infrastructure: Optional[str] = None
    magical_requirements: bool = False
    rarity: Optional[str] = None


@dataclass 
class ProcessingOption:
    """Processing option for transforming a resource"""
    value_multiplier: float = 1.0
    tools: List[str] = field(default_factory=list)
    time: int = 1  # in hours
    skill_required: Optional[str] = None
    infrastructure_required: Optional[str] = None


@dataclass
class StorageDecay:
    """Storage decay rates by storage type"""
    rates: Dict[str, float] = field(default_factory=dict)
    
    def get_decay_rate(self, storage_type: str) -> float:
        """Get decay rate for storage type"""
        return self.rates.get(storage_type, 0.01)  # Default 1% decay


@dataclass
class TradeModifiers:
    """Trade price modifiers by region type"""
    modifiers: Dict[str, float] = field(default_factory=dict)
    
    def get_modifier(self, region_type: str) -> float:
        """Get trade modifier for region type"""
        return self.modifiers.get(region_type, 1.0)  # Default no modification


@dataclass
class MagicalProperties:
    """Magical properties for magical resources"""
    conductivity: Optional[str] = None
    resistance: Optional[str] = None
    amplification: Optional[float] = None
    school_affinity: Optional[str] = None
    mana_capacity: Optional[int] = None


@dataclass
class ResourceData:
    """
    Rich data model for a resource with complex production mechanics.
    
    This model supports the full resource_types.json structure including
    production requirements, processing chains, storage mechanics, and trade effects.
    """
    # Basic properties
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: ResourceCategory = ResourceCategory.RAW_MATERIALS
    
    # Economic properties
    base_value: float = 1.0
    current_price: float = 1.0
    weight: float = 1.0
    volume: float = 1.0
    
    # Quantity and location
    quantity: int = 0
    amount: float = 0.0  # For fractional amounts
    region_id: str = ""
    
    # Rich mechanics
    production_requirements: ProductionRequirements = field(default_factory=ProductionRequirements)
    processing_options: Dict[str, ProcessingOption] = field(default_factory=dict)
    storage_decay: StorageDecay = field(default_factory=StorageDecay)
    trade_modifiers: TradeModifiers = field(default_factory=TradeModifiers)
    
    # Special properties
    magical_properties: Optional[MagicalProperties] = None
    nutritional_value: Optional[int] = None
    population_sustenance: Optional[float] = None
    cultural_value: Optional[str] = None
    status_symbol: bool = False
    rarity_level: str = "common"
    
    # Metadata and timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_production_time(self, skill_level: int = 1, tool_quality: float = 1.0) -> float:
        """Calculate actual production time based on skill and tools"""
        base_time = self.production_requirements.time_to_harvest
        
        # Skill modifier (higher skill = faster production)
        skill_modifier = max(0.5, 1.0 - (skill_level - 1) * 0.1)
        
        # Tool quality modifier
        tool_modifier = max(0.5, 1.0 / tool_quality)
        
        return base_time * skill_modifier * tool_modifier
    
    def calculate_processed_value(self, processing_type: str) -> float:
        """Calculate value after processing"""
        if processing_type not in self.processing_options:
            return self.base_value
        
        option = self.processing_options[processing_type]
        return self.base_value * option.value_multiplier
    
    def calculate_decay_after_time(self, storage_type: str, days: int) -> float:
        """Calculate remaining quantity after storage decay"""
        decay_rate = self.storage_decay.get_decay_rate(storage_type)
        daily_decay = decay_rate / 365  # Convert annual rate to daily
        remaining_factor = (1 - daily_decay) ** days
        return self.quantity * remaining_factor
    
    def calculate_regional_price(self, region_type: str) -> float:
        """Calculate price adjusted for regional trade modifiers"""
        modifier = self.trade_modifiers.get_modifier(region_type)
        return self.current_price * modifier
    
    def can_be_produced_in_biome(self, biome_type: str) -> bool:
        """Check if resource can be produced in given biome"""
        if not self.production_requirements.biome_types:
            return True  # No restrictions
        return biome_type in self.production_requirements.biome_types
    
    def has_required_tools(self, available_tools: List[str]) -> bool:
        """Check if required tools are available"""
        required = set(self.production_requirements.tools_required)
        available = set(available_tools)
        return required.issubset(available)
    
    def is_seasonal_available(self, current_season: str) -> bool:
        """Check if resource is available in current season"""
        if not self.production_requirements.seasonal:
            return True
        return current_season in self.production_requirements.seasons
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "base_value": self.base_value,
            "current_price": self.current_price,
            "weight": self.weight,
            "volume": self.volume,
            "quantity": self.quantity,
            "amount": self.amount,
            "region_id": self.region_id,
            "production_requirements": {
                "biome_types": self.production_requirements.biome_types,
                "tools_required": self.production_requirements.tools_required,
                "skill_required": self.production_requirements.skill_required,
                "time_to_harvest": self.production_requirements.time_to_harvest,
                "renewable": self.production_requirements.renewable,
                "renewal_time": self.production_requirements.renewal_time,
                "depletion_rate": self.production_requirements.depletion_rate,
                "seasonal": self.production_requirements.seasonal,
                "seasons": self.production_requirements.seasons,
                "climate_dependent": self.production_requirements.climate_dependent,
                "requires_infrastructure": self.production_requirements.requires_infrastructure,
                "magical_requirements": self.production_requirements.magical_requirements,
                "rarity": self.production_requirements.rarity
            },
            "processing_options": {
                name: {
                    "value_multiplier": option.value_multiplier,
                    "tools": option.tools,
                    "time": option.time,
                    "skill_required": option.skill_required,
                    "infrastructure_required": option.infrastructure_required
                }
                for name, option in self.processing_options.items()
            },
            "storage_decay": self.storage_decay.rates,
            "trade_modifiers": self.trade_modifiers.modifiers,
            "magical_properties": {
                "conductivity": self.magical_properties.conductivity,
                "resistance": self.magical_properties.resistance,
                "amplification": self.magical_properties.amplification,
                "school_affinity": self.magical_properties.school_affinity,
                "mana_capacity": self.magical_properties.mana_capacity
            } if self.magical_properties else None,
            "nutritional_value": self.nutritional_value,
            "population_sustenance": self.population_sustenance,
            "cultural_value": self.cultural_value,
            "status_symbol": self.status_symbol,
            "rarity_level": self.rarity_level,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_json_config(cls, resource_id: str, config_data: Dict[str, Any]) -> 'ResourceData':
        """Create ResourceData from JSON configuration"""
        # Basic properties
        resource = cls(
            id=resource_id,
            name=config_data.get("name", ""),
            description=config_data.get("description", ""),
            category=ResourceCategory(config_data.get("category", "raw_materials")),
            base_value=config_data.get("base_value", 1.0),
            current_price=config_data.get("base_value", 1.0),
            weight=config_data.get("weight", 1.0),
            volume=config_data.get("volume", 1.0),
            rarity_level=config_data.get("rarity_level", "common")
        )
        
        # Production requirements
        prod_req_data = config_data.get("production_requirements", {})
        resource.production_requirements = ProductionRequirements(
            biome_types=prod_req_data.get("biome_types", []),
            tools_required=prod_req_data.get("tools_required", []),
            skill_required=prod_req_data.get("skill_required"),
            time_to_harvest=prod_req_data.get("time_to_harvest", 1),
            renewable=prod_req_data.get("renewable", True),
            renewal_time=prod_req_data.get("renewal_time"),
            depletion_rate=prod_req_data.get("depletion_rate"),
            seasonal=prod_req_data.get("seasonal", False),
            seasons=prod_req_data.get("seasons", []),
            climate_dependent=prod_req_data.get("climate_dependent", False),
            requires_infrastructure=prod_req_data.get("requires_infrastructure"),
            magical_requirements=prod_req_data.get("magical_requirements", False),
            rarity=prod_req_data.get("rarity")
        )
        
        # Processing options
        proc_data = config_data.get("processing_options", {})
        for proc_name, proc_config in proc_data.items():
            resource.processing_options[proc_name] = ProcessingOption(
                value_multiplier=proc_config.get("value_multiplier", 1.0),
                tools=proc_config.get("tools", []),
                time=proc_config.get("time", 1),
                skill_required=proc_config.get("skill_required"),
                infrastructure_required=proc_config.get("infrastructure_required")
            )
        
        # Storage decay
        storage_data = config_data.get("storage_decay", {})
        resource.storage_decay = StorageDecay(rates=storage_data)
        
        # Trade modifiers
        trade_data = config_data.get("trade_modifiers", {})
        resource.trade_modifiers = TradeModifiers(modifiers=trade_data)
        
        # Magical properties
        magic_data = config_data.get("magical_properties")
        if magic_data:
            resource.magical_properties = MagicalProperties(
                conductivity=magic_data.get("conductivity"),
                resistance=magic_data.get("resistance"),
                amplification=magic_data.get("amplification"),
                school_affinity=magic_data.get("school_affinity"),
                mana_capacity=magic_data.get("mana_capacity")
            )
        
        # Special properties
        resource.nutritional_value = config_data.get("nutritional_value")
        resource.population_sustenance = config_data.get("population_sustenance")
        resource.cultural_value = config_data.get("cultural_value")
        resource.status_symbol = config_data.get("status_symbol", False)
        
        return resource


@dataclass
class Resource:
    """Simplified resource data model for backward compatibility."""
    id: str
    name: str
    type: str  # Maps to category
    value: float = 0.0
    quantity: int = 0
    amount: float = 0.0
    region_id: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'quantity': self.quantity,
            'amount': self.amount,
            'region_id': self.region_id
        }
    
    def to_resource_data(self) -> ResourceData:
        """Convert to rich ResourceData model"""
        return ResourceData(
            id=self.id,
            name=self.name,
            category=ResourceCategory(self.type) if self.type in [c.value for c in ResourceCategory] else ResourceCategory.RAW_MATERIALS,
            base_value=self.value,
            current_price=self.value,
            quantity=self.quantity,
            amount=self.amount,
            region_id=self.region_id
        )


class ResourceManager:
    """Manages game resources with rich production mechanics."""
    
    def __init__(self):
        self.resources: Dict[str, ResourceData] = {}
        self.resource_configs: Dict[str, Dict[str, Any]] = {}
    
    def load_resource_config(self, config_data: Dict[str, Any]) -> None:
        """Load resource configuration from JSON"""
        self.resource_configs = config_data.get("resources", {})
    
    def create_resource_from_config(self, resource_id: str, quantity: int = 1, region_id: str = "") -> ResourceData:
        """Create a resource instance from configuration"""
        if resource_id not in self.resource_configs:
            raise ValueError(f"Resource {resource_id} not found in configuration")
        
        config = self.resource_configs[resource_id]
        resource = ResourceData.from_json_config(resource_id, config)
        resource.quantity = quantity
        resource.region_id = region_id
        
        return resource
    
    def add_resource(self, resource: ResourceData) -> None:
        """Add a resource."""
        self.resources[resource.id] = resource
    
    def get_resource(self, resource_id: str) -> Optional[ResourceData]:
        """Get a resource by ID."""
        return self.resources.get(resource_id)
    
    def list_resources(self) -> List[ResourceData]:
        """List all resources."""
        return list(self.resources.values())
    
    def get_resources_by_category(self, category: ResourceCategory) -> List[ResourceData]:
        """Get all resources in a category"""
        return [r for r in self.resources.values() if r.category == category]
    
    def get_resources_by_biome(self, biome_type: str) -> List[ResourceData]:
        """Get all resources that can be produced in a biome"""
        return [r for r in self.resources.values() if r.can_be_produced_in_biome(biome_type)]
    
    def get_seasonal_resources(self, season: str) -> List[ResourceData]:
        """Get all resources available in a season"""
        return [r for r in self.resources.values() if r.is_seasonal_available(season)]


# Export main classes
__all__ = [
    'Resource', 'ResourceData', 'ResourceManager',
    'ResourceCategory', 'StorageType', 'ProductionRequirements',
    'ProcessingOption', 'StorageDecay', 'TradeModifiers', 'MagicalProperties'
]
