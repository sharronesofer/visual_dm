"""Models package."""

from backend.app.db.session import engine, SessionLocal, get_db, async_engine, AsyncSessionLocal, get_async_db, Base
from .base import BaseModel
from .cleanup import CleanupRule, CleanupEntry
from .cloud_provider import CloudProvider
from .character import Character, Skill
from .market import MarketItem, TradeOffer, Transaction, PriceHistory

# Import new entity models
from .world import World, Season, WeatherCondition
from .npc import NPC, PersonalityTrait
from .location import Location, LocationType
from .item import Item, ItemType, ItemRarity
from .quest import Quest, QuestStatus, ConditionType
from .faction import Faction, FactionAlignment

# Import User, Role, Permission, and APIKey models
from backend.app.models.user import User, Role, Permission
from backend.app.models.api_key import APIKey

# These imports are necessary for SQLAlchemy to detect the models
__all__ = [
    'BaseModel',
    'CleanupRule', 'CleanupEntry',
    'CloudProvider',
    'Character', 'Skill',
    'MarketItem', 'TradeOffer', 'Transaction', 'PriceHistory',
    'World', 'Season', 'WeatherCondition',
    'NPC', 'PersonalityTrait',
    'Location', 'LocationType',
    'Item', 'ItemType', 'ItemRarity',
    'Quest', 'QuestStatus', 'ConditionType',
    'Faction', 'FactionAlignment',
    'User', 'Role', 'Permission', 'APIKey'
] 