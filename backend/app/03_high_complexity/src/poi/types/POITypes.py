from typing import Any, Dict, List, Union
from enum import Enum



/**
 * Enums and types for the POI (Point of Interest) system
 */
/**
 * Primary POI types available in the system
 *
 * - SETTLEMENT: Towns, villages, cities, outposts, etc.
 * - DUNGEON: Caves, ruins, temples, fortresses, etc.
 * - LANDMARK: Natural or constructed points of interest (mountain, lake, monument, etc.)
 * - RESOURCE: Resource locations (mine, quarry, lumber camp, etc.)
 */
class POIType(Enum):
    SETTLEMENT = 'SETTLEMENT'
    DUNGEON = 'DUNGEON'
    LANDMARK = 'LANDMARK'
    RESOURCE = 'RESOURCE'
/**
 * POI subtypes for specialized POIs, grouped by main type.
 *
 * - Settlement subtypes: VILLAGE, TOWN, CITY, OUTPOST
 * - Dungeon subtypes: CAVE, RUIN, TEMPLE, FORTRESS
 * - Landmark subtypes: MOUNTAIN, LAKE, FOREST, MONUMENT
 * - Resource subtypes: MINE, QUARRY, LUMBER_CAMP, HUNTING_GROUND
 *
 * Extend this enum as new POI subtypes are introduced.
 */
class POISubtype(Enum):
    VILLAGE = 'VILLAGE'
    TOWN = 'TOWN'
    CITY = 'CITY'
    OUTPOST = 'OUTPOST'
    CAVE = 'CAVE'
    RUIN = 'RUIN'
    TEMPLE = 'TEMPLE'
    FORTRESS = 'FORTRESS'
    MOUNTAIN = 'MOUNTAIN'
    LAKE = 'LAKE'
    FOREST = 'FOREST'
    MONUMENT = 'MONUMENT'
    MINE = 'MINE'
    QUARRY = 'QUARRY'
    LUMBER_CAMP = 'LUMBER_CAMP'
    HUNTING_GROUND = 'HUNTING_GROUND'
/**
 * Coordinates in 3D space with level information
 */
class Coordinates:
    x: float
    y: float
    z: float
    level: float
/**
 * Connection point between POIs
 */
class ConnectionPoint:
    id: str
    sourceCoords: \'Coordinates\'
    targetCoords: \'Coordinates\'
    type: Union['door', 'path', 'portal', 'bridge']
    properties: Dict[str, Any]
/**
 * Thematic elements that define the POI's atmosphere and setting
 */
class ThematicElements:
    biome: str
    climate: str
    era: str
    culture: str
    dangerLevel: float
    lighting: Union['dark', 'dim', 'bright']
    weather?: str
    ambientSounds?: List[str]
    visualEffects?: List[str]
    themes: List[str]
    difficulty?: float
    resourceDensity?: float
    population?: float
/**
 * Change history entry for state tracking
 */
class ChangeHistoryEntry:
    timestamp: Date
    type: Union['creation', 'modification', 'expansion', 'deletion']
    details: str
/**
 * State tracking for POI persistence
 */
class StateTracking:
    version: float
    lastModified: Date
    modifiedBy: str
    changeHistory: List[ChangeHistoryEntry]
    visits: float
    discoveries: float
    interactions: float
    modificationHistory: Dict[str, Any]
class POISize:
    width: float
    height: float
    depth?: float
class POIBounds:
    position: \'Coordinates\'
    size: \'POISize\' 