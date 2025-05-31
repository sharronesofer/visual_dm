from sqlalchemy import Column, String, Integer, Float, Enum, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
import enum
from backend.infrastructure.models import BaseModel

class ItemRarity(enum.Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"
    UNIQUE = "unique"

class ItemType(enum.Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST_ITEM = "quest_item"
    KEY_ITEM = "key_item"
    CONTAINER = "container"
    CURRENCY = "currency"
    TOOL = "tool"
    BOOK = "book"
    MISCELLANEOUS = "miscellaneous"

class Item(BaseModel):
    __tablename__ = 'item'
    """Item model representing objects that can be collected and used."""
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Basic properties
    type = Column(Enum(ItemType), nullable=False)
    rarity = Column(Enum(ItemRarity), default=ItemRarity.COMMON)
    value = Column(Integer, default=0)  # Base value in game currency
    weight = Column(Float, default=0.0)  # Weight in kg or other unit
    
    # Usage properties
    durability = Column(Integer)
    max_durability = Column(Integer)
    level_requirement = Column(Integer, default=1)
    
    # Item functionality
    properties = Column(JSON)  # Special properties and effects
    stats = Column(JSON)  # Stat modifiers (damage, defense, etc.)
    usage_effects = Column(JSON)  # Effects when used (healing, etc.)
    
    # Status flags
    is_quest_item = Column(Boolean, default=False)
    is_stackable = Column(Boolean, default=False)
    max_stack_size = Column(Integer, default=1)
    is_equippable = Column(Boolean, default=False)
    is_consumable = Column(Boolean, default=False)
    is_tradable = Column(Boolean, default=True)
    
    # Source and location
    location_id = Column(Integer, ForeignKey('location.id'), nullable=True)
    location = relationship("Location")
    
    def __repr__(self):
        return f"<Item {self.name} ({self.type.name}, {self.rarity.name})>" 