from typing import Any, Dict, List


/**
 * Building location in 3D space
 */
class Location:
    x: float
    y: float
    z: float
/**
 * Building dimensions
 */
class Dimensions:
    width: float
    height: float
    length: float
/**
 * Building room data
 */
class Room:
    id: str
    name: str
    type: str
    floor: float
    dimensions: \'Dimensions\'
    position: \'Location\'
/**
 * Room connection data
 */
class Connection:
    from: str
    to: str
    type: str
/**
 * Building interior data
 */
class BuildingInterior:
    floors: float
    rooms: List[Room]
    connections: List[Connection]
/**
 * Building state information
 */
class BuildingState:
    condition: float
    occupancy: float
    power: Dict[str, Any]
/**
 * Building metadata
 */
class BuildingMetadata:
    description?: str
    owner?: str
    constructionDate?: Date
    lastRenovation?: Date
    customFields?: Dict[str, Any>
/**
 * Main building data structure
 */
class Building:
    id: str
    name: str
    type: str
    position: \'Location\'
    dimensions: \'Dimensions\'
    interior?: \'BuildingInterior\'
    state?: \'BuildingState\'
    metadata?: \'BuildingMetadata\'
    createdAt?: Date
    updatedAt?: Date 