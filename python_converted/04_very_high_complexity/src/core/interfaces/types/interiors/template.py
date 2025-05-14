from typing import Any, Dict, List
from enum import Enum



class RoomType(Enum):
    ENTRANCE = 'ENTRANCE'
    MAIN_HALL = 'MAIN_HALL'
    BEDROOM = 'BEDROOM'
    KITCHEN = 'KITCHEN'
    STORAGE = 'STORAGE'
    CORRIDOR = 'CORRIDOR'
    BATHROOM = 'BATHROOM'
    STUDY = 'STUDY'
    WORKSHOP = 'WORKSHOP'
    GARDEN = 'GARDEN'
    COURTYARD = 'COURTYARD'
    THRONE_ROOM = 'THRONE_ROOM'
    TREASURY = 'TREASURY'
    ARMORY = 'ARMORY'
    LIBRARY = 'LIBRARY'
    DUNGEON = 'DUNGEON'
class FurnitureType(Enum):
    BED = 'BED'
    TABLE = 'TABLE'
    CHAIR = 'CHAIR'
    CHEST = 'CHEST'
    SHELF = 'SHELF'
    COUNTER = 'COUNTER'
    WORKBENCH = 'WORKBENCH'
    THRONE = 'THRONE'
    WEAPON_RACK = 'WEAPON_RACK'
    BOOKSHELF = 'BOOKSHELF'
    DISPLAY_CASE = 'DISPLAY_CASE'
    ALTAR = 'ALTAR'
    STATUE = 'STATUE'
    FOUNTAIN = 'FOUNTAIN'
class GroupArrangement(Enum):
    GRID = 'GRID'
    CIRCLE = 'CIRCLE'
    LINE = 'LINE'
    CLUSTER = 'CLUSTER'
class FurniturePlacementType(Enum):
    CENTER = 'CENTER'
    AGAINST_WALL = 'AGAINST_WALL'
    NEAR_WALL = 'NEAR_WALL'
    NEAR_FURNITURE = 'NEAR_FURNITURE'
    CORNER = 'CORNER'
    RANDOM = 'RANDOM'
class SpacingType(Enum):
    BETWEEN_FURNITURE = 'BETWEEN_FURNITURE'
    WALKWAY = 'WALKWAY'
    CLEARANCE = 'CLEARANCE'
class DecorationType(Enum):
    LIGHT_SOURCE = 'LIGHT_SOURCE'
    TAPESTRY = 'TAPESTRY'
    RUG = 'RUG'
    PAINTING = 'PAINTING'
    PLANT = 'PLANT'
    WINDOW = 'WINDOW'
    CURTAIN = 'CURTAIN'
    BANNER = 'BANNER'
    TROPHY = 'TROPHY'
class DecorationPlacementType(Enum):
    ON_WALL = 'ON_WALL'
    ON_FLOOR = 'ON_FLOOR'
    ON_CEILING = 'ON_CEILING'
    ON_FURNITURE = 'ON_FURNITURE'
class NPCZoneType(Enum):
    SERVICE = 'SERVICE'
    SOCIAL = 'SOCIAL'
    WORK = 'WORK'
    REST = 'REST'
    GUARD = 'GUARD'
class NPCActivityType(Enum):
    STANDING = 'STANDING'
    SITTING = 'SITTING'
    WALKING = 'WALKING'
    WORKING = 'WORKING'
    SLEEPING = 'SLEEPING'
    GUARDING = 'GUARDING'
class InteractiveObjectType(Enum):
    SERVICE_POINT = 'SERVICE_POINT'
    QUEST_BOARD = 'QUEST_BOARD'
    CRAFTING_STATION = 'CRAFTING_STATION'
    STORAGE_CONTAINER = 'STORAGE_CONTAINER'
    DOOR = 'DOOR'
    TRAP = 'TRAP'
    PUZZLE = 'PUZZLE'
    TREASURE = 'TREASURE'
class InteractiveObjectPlacementType(Enum):
    NEAR_WALL = 'NEAR_WALL'
    NEAR_FURNITURE = 'NEAR_FURNITURE'
    CENTER = 'CENTER'
    CORNER = 'CORNER'
    RANDOM = 'RANDOM'
class RoomPlacementType(Enum):
    NEAR_EDGE = 'NEAR_EDGE'
    ADJACENT_TO = 'ADJACENT_TO'
    SAME_FLOOR = 'SAME_FLOOR'
    RANDOM = 'RANDOM'
class InteriorTemplate:
    id: str
    name: str
    buildingType: BuildingType
    category: POICategory
    roomLayouts: List[RoomLayout]
    furnitureRules: List[FurnitureRule]
    decorationSchemes: List[DecorationScheme]
    npcZones: List[NPCZoneDefinition]
    interactiveObjects: List[InteractivedictRule]
class RoomLayout:
    id: str
    name: str
    type: \'RoomType\'
    minSize: Dict[str, Any]
  requiredConnections: List[RoomType]
  optionalConnections: List[RoomType]
  priority: float
  placementRules: List[RoomPlacementRule]
}
class RoomPlacementRule:
    type: \'RoomPlacementType\'
    parameters: Dict[str, Any>
class FurnitureRule:
    roomType: \'RoomType\'
    requiredFurniture: List[FurniturePlacementRule]
    optionalFurniture: List[FurniturePlacementRule]
    groupings: List[FurnitureGrouping]
    spacingRules: List[SpacingRule]
class FurniturePlacementRule:
    type: \'FurnitureType\'
    minCount: float
    maxCount: float
    placementRules: Dict[str, Any]
class FurnitureGrouping:
    name: str
    furniture: Dict[str, Any]
class SpacingRule:
    type: \'SpacingType\'
    distance: float
class DecorationScheme:
    roomType: \'RoomType\'
    theme: str
    decorations: List[DecorationRule]
    colorPalette: List[str]
    density: float
class DecorationRule:
    type: \'DecorationType\'
    minCount: float
    maxCount: float
    placementRules: Dict[str, Any]
class NPCZoneDefinition:
    roomType: \'RoomType\'
    zoneType: \'NPCZoneType\'
    capacity: float
    requiredFurniture: List[FurnitureType]
    activityType: List[NPCActivityType]
class InteractiveObjectRule:
    roomType: \'RoomType\'
    objectType: InteractivedictType
    count: float
    placementRules: Dict[str, Any] 