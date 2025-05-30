from typing import Any, Dict
from enum import Enum



class BuildingBase:
    id: str
    name: str
    type: \'BuildingType\'
    category: \'POICategory\'
    dimensions: Dict[str, Any]
class BuildingType(Enum):
    INN = 'INN'
    SHOP = 'SHOP'
    TAVERN = 'TAVERN'
    GUILD_HALL = 'GUILD_HALL'
    NPC_HOME = 'NPC_HOME'
    ENEMY_LAIR = 'ENEMY_LAIR'
    PUZZLE_ROOM = 'PUZZLE_ROOM'
    TREASURE_CHAMBER = 'TREASURE_CHAMBER'
    TRAP_ROOM = 'TRAP_ROOM'
    RUINS = 'RUINS'
    CAMPSITE = 'CAMPSITE'
    LANDMARK = 'LANDMARK'
    RESOURCE_NODE = 'RESOURCE_NODE'
class POICategory(Enum):
    SOCIAL = 'SOCIAL'
    DUNGEON = 'DUNGEON'
    EXPLORATION = 'EXPLORATION'
class Coordinate:
    x: float
    y: float 