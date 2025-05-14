from typing import Any, Dict, List
from enum import Enum



class SocialBuilding:
    category: POICategory.SOCIAL
    npcCapacity: float
    openingHours: Dict[str, Any]
class SocialService(Enum):
    LODGING = 'LODGING'
    TRADING = 'TRADING'
    FOOD_DRINK = 'FOOD_DRINK'
    QUEST_GIVING = 'QUEST_GIVING'
    FACTION_SERVICES = 'FACTION_SERVICES'
    INFORMATION = 'INFORMATION'
class Inn:
    type: BuildingType.INN
    roomCount: float
    roomTypes: List[RoomType]
class Shop:
    type: BuildingType.SHOP
    shopType: \'ShopType\'
    inventorySize: float
class Tavern:
    type: BuildingType.TAVERN
    specialties: List[str]
    entertainmentTypes: List[EntertainmentType]
class GuildHall:
    type: BuildingType.GUILD_HALL
    guildType: str
    membershipLevels: List[str]
    facilities: List[str]
class NPCHome:
    type: BuildingType.NPC_HOME
    residentCount: float
    socialStatus: \'SocialStatus\'
class RoomType(Enum):
    BASIC = 'BASIC'
    COMFORTABLE = 'COMFORTABLE'
    LUXURIOUS = 'LUXURIOUS'
class ShopType(Enum):
    GENERAL = 'GENERAL'
    WEAPONS = 'WEAPONS'
    ARMOR = 'ARMOR'
    MAGIC = 'MAGIC'
    ALCHEMY = 'ALCHEMY'
    SPECIALTY = 'SPECIALTY'
class EntertainmentType(Enum):
    MUSIC = 'MUSIC'
    GAMBLING = 'GAMBLING'
    STORYTELLING = 'STORYTELLING'
    PERFORMANCES = 'PERFORMANCES'
class SocialStatus(Enum):
    POOR = 'POOR'
    MODEST = 'MODEST'
    WEALTHY = 'WEALTHY'
    NOBLE = 'NOBLE' 