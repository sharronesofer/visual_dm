from typing import Any, Dict, List, Union
from enum import Enum



class Point:
    x: float
    y: float
class Size:
    width: float
    height: float
class Viewport:
    position: \'Point\'
    size: \'Size\'
    zoom: float
    rotation: float
class Tile:
    id: str
    type: \'TerrainType\'
    position: \'Point\'
    elevation: float
    walkable: bool
    explored: bool
    visible: bool
    weather?: str
class TerrainType(Enum):
    GRASS = 'grass'
    FOREST = 'forest'
    MOUNTAIN = 'mountain'
    WATER = 'water'
    URBAN = 'urban'
class MapData:
    size: \'Size\'
    tiles: List[List[Tile]]
    objects: List[Mapdict]
class MapObject:
    id: str
    type: str
    position: \'Point\'
    size: \'Size\'
    elevation: float
    interactive: bool
    data: Dict[str, Any>
class LightSource:
    position: \'Point\'
    intensity: float
    radius: float
    color: str
class RenderOptions:
    showGrid: bool
    showFogOfWar: bool
    showLighting: bool
    showObjects: bool
    levelOfDetail: float
class MapInteractionEvent:
    type: Union['click', 'hover', 'drag']
    position: \'Point\'
    tile?: \'Tile\'
    object?: Mapdict
class MapUpdateEvent:
    type: Union['tile', 'dict', 'lighting', 'viewport']
    data: Any
MapEventListener = Union[(event: \'MapInteractionEvent\', MapUpdateEvent) => None] 