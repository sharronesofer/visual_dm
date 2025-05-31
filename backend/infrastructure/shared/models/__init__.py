"""Domain Models Package."""

from .base import BaseModel, CoreBaseModel, BaseRepository, BaseService
from .character import Character, Skill
from .npc import NPC, PersonalityTrait
from .quest import Quest, QuestStatus, ConditionType
from .faction import Faction, FactionAlignment
from .item import Item, ItemType, ItemRarity
from .location import Location, LocationType
from .world import World, Season, WeatherCondition
from .market import MarketItem, TradeOffer, Transaction, PriceHistory
from .models import (
    SharedEntity, 
    SharedModel, 
    SharedBaseModel,
    CreateSharedRequest,
    UpdateSharedRequest,
    SharedResponse,
    SharedListResponse
)

__all__ = [
    'BaseModel', 'CoreBaseModel', 'BaseRepository', 'BaseService',
    'Character', 'Skill',
    'NPC', 'PersonalityTrait',
    'Quest', 'QuestStatus', 'ConditionType',
    'Faction', 'FactionAlignment',
    'Item', 'ItemType', 'ItemRarity',
    'Location', 'LocationType',
    'World', 'Season', 'WeatherCondition',
    'MarketItem', 'TradeOffer', 'Transaction', 'PriceHistory',
    'SharedEntity', 'SharedModel', 'SharedBaseModel',
    'CreateSharedRequest', 'UpdateSharedRequest', 'SharedResponse', 'SharedListResponse'
] 