from typing import Any, Dict, List, Union


/** Terrain types */
TerrainType = Union['plains', 'forest', 'mountain', 'water', 'desert', 'swamp']
Direction = Union['north', 'south', 'east', 'west']
BorderType = Union['normal', 'difficult', 'impassable', 'bridge', 'gate']
class Border:
    type: BorderType
    direction: Direction
    connected: bool
/** Region interface */
class Region:
    id: str
    name: str
    position: Position
    width: float
    height: float
    terrain: TerrainType
    borders: List[Border]
    metadata?: Dict[str, unknown>
    type: RegionType
    description?: str
    boundaries: List[[float, float]>
/** POI (Point of Interest) interface */
class POI:
    id: str
    type: POIType
    name: str
    position: Position
    description?: str
    icon?: str
    metadata?: Dict[str, unknown>
/** Map chunk interface */
class MapChunk:
    position: Position
    width: float
    height: float
    terrain: List[List[TerrainType]]
    pois: List[POI]
    regions: List[Region]
    lastUpdated: float
/** Map data interface */
class MapData:
    id: str
    name: str
    width: float
    height: float
    chunks: Dict[str, MapChunk>
    regions: List[Region]
    metadata?: Dict[str, unknown>
/** Map generation state interface */
class MapGenerationState:
    isGenerating: bool
    progress: float
    currentChunk?: Position
    error?: str
/** Map chunk key interface */
class MapChunkKey:
    x: float
    y: float
    toString(): str
/** POI types */
POIType = Union['city', 'dungeon', 'quest', 'landmark']
/** Map response types */
class MapResponse:
    map: \'MapData\'
    generationId: str
class RegionResponse:
    region: \'Region\'
    pois: List[POI]
class ChunkResponse:
    chunk: \'MapChunk\'
    complete: bool
/** Map generation options */
class GenerateMapOptions:
    width: float
    height: float
    seed?: str
    terrainConfig?: Dict[TerrainType, float>
    poiDensity?: float
const getChunkKey = (position: Position): str => `${position.x},${position.y}`
const getRegionKey = (position: Position): str => `${position.x},${position.y}`
const calculateChunkPosition = (position: Position, chunkSize: float): Position => ({
  x: Math.floor(position.x / chunkSize),
  y: Math.floor(position.y / chunkSize),
})
RegionType = Union['city', 'dungeon', 'wilderness', 'custom']