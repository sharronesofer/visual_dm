from typing import Any, Dict, List, Union



/**
 * Map types used across the application
 */
/** Map region type */
RegionType = Union['city', 'dungeon', 'wilderness', 'custom']
/** Map region interface */
class Region:
    id: str
    name: str
    type: RegionType
    bounds: Rectangle
    parentId?: str
    children?: List[str]
    metadata?: Dict[str, unknown>
/** Point of Interest type */
POIType = Union[, 'npc', 'quest', 'shop', 'landmark', 'encounter', 'custom']
/** Point of Interest interface */
class POI:
    id: str
    name: str
    type: POIType
    position: Position
    regionId: str
    description?: str
    icon?: str
    metadata?: Dict[str, unknown>
/** Map view state interface */
class MapViewState:
    center: Position
    zoom: float
    rotation: float
    selectedRegionId?: str
    selectedPOIId?: str
    visibleRegionIds: Set[str>
    visiblePOIIds: Set[str>
/** Map interaction mode */
MapInteractionMode = Union['pan', 'select', 'draw', 'edit']
/** Map interaction state */
class MapInteractionState:
    mode: MapInteractionMode
    isDragging: bool
    isDrawing: bool
    isEditing: bool
    startPosition?: Position
    currentPosition?: Position
/** Map data interface */
class MapData:
    regions: Dict[str, Region>
    pois: Dict[str, POI>
    metadata?: Dict[str, unknown>
/** Helper function to create a region */
const createRegion = (
  id: str,
  name: str,
  type: RegionType,
  bounds: Rectangle,
  options: Partial<Omit<Region, 'id' | 'name' | 'type' | 'bounds'>> = {}
): \'Region\' => ({
  id,
  name,
  type,
  bounds,
  ...options,
})
/** Helper function to create a POI */
const createPOI = (
  id: str,
  name: str,
  type: POIType,
  position: Position,
  regionId: str,
  options: Partial<
    Omit<POI, 'id' | 'name' | 'type' | 'position' | 'regionId'>
  > = {}
): \'POI\' => ({
  id,
  name,
  type,
  position,
  regionId,
  ...options,
})
/** Helper function to create map view state */
const createMapViewState = (
  center: Position,
  zoom: float = 1,
  rotation: float = 0
): \'MapViewState\' => ({
  center,
  zoom,
  rotation,
  visibleRegionIds: new Set(),
  visiblePOIIds: new Set(),
})
/** Helper function to create map interaction state */
const createMapInteractionState = (
  mode: MapInteractionMode = 'pan'
): \'MapInteractionState\' => ({
  mode,
  isDragging: false,
  isDrawing: false,
  isEditing: false,
})
/** Helper function to create map data */
const createMapData = (
  regions: Record<string, Region> = {},
  pois: Record<string, POI> = {},
  metadata?: Record<string, unknown>
): \'MapData\' => ({
  regions,
  pois,
  metadata,
})