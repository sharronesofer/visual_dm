from typing import Any, Dict, List, Union


/**
 * Represents a geographic coordinate
 */
Coordinate = [float, float] 
/**
 * Represents a bounding box in the format [minLng, minLat, maxLng, maxLat]
 */
BoundingBox = [float, float, float, float]
/**
 * Represents a geographic region with boundaries and metadata
 */
class Region:
    id: str
    name: str
    boundaries: List[List[Coordinate]]
    properties: Dict[str, Any]
/**
 * Represents the current state of the map viewport
 */
class ViewportState:
    zoom: float
    center: Coordinate
    bounds: BoundingBox
    pitch?: float
    bearing?: float
    padding?: { top: float
    right: float
    bottom: float
    left: float
}
/**
 * POI definition for the map system
 */
class POI:
    id: str
    name: str
    coordinates: Coordinate
    type: str
    metadata?: Dict[str, Any>
/**
 * Props for the main RegionMap component
 */
class RegionMapProps:
    regions: List[Region]
    initialViewport?: Partial[ViewportState]
    onRegionClick?: (region: \'Region\', event: React.MouseEvent) => None
    onViewportChange?: (viewport: ViewportState) => None
    selectedRegionId?: str
    highlightedRegionId?: str
    style?: React.CSSProperties
    className?: str
    mapStyle?: Union[str, dict]
    interactive?: bool
/**
 * Props for the RegionLayer component
 */
class RegionLayerProps:
    regions: List[Region]
    selectedRegionId?: str
    highlightedRegionId?: str
    onRegionClick?: (region: \'Region\', event: React.MouseEvent) => None
    onRegionHover?: Union[(region: \'Region\', None, event: React.MouseEvent) => None]
    fillOpacity?: float
    strokeWidth?: float
    defaultFillColor?: str
    selectedFillColor?: str
    highlightedFillColor?: str
/**
 * Props for the ViewportManager component
 */
class ViewportManagerProps:
    initialViewport: \'ViewportState\'
    onChange?: (viewport: ViewportState) => None
    fitBounds?: BoundingBox
    fitBoundsPadding?: float
    children: (
    viewport: \'ViewportState\',
    setViewport: (viewport: ViewportState) => None
  ) => React.ReactNode
/**
 * Props for the RegionSystem component
 */
class RegionSystemProps:
    regions: List[Region]
    children?: React.ReactNode
    onRegionSelect?: Union[(region: \'Region\', None) => None]
    initialSelectedRegionId?: str
    mapControls?: {
    zoom?: bool
    pan?: bool
    rotate?: bool
}
/**
 * Type guard to check if a value is a valid Region
 */
function isRegion(value: Any): value is Region {
  return (
    value &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    Array.isArray(value.boundaries) &&
    typeof value.properties === 'object'
  )
}
/**
 * Utility type for partial region updates
 */
RegionUpdate = Pick[Region, 'id'> & Partial<Omit<Region, 'id'>]
/**
 * Event types for region interactions
 */
RegionEvent = {
  region: \'Region\'
  domEvent: React.MouseEvent | React.TouchEvent
  coordinate: Coordinate
}
/**
 * Style properties for rendering a region
 */
class RegionStyle:
    fillColor?: str
    strokeColor?: str
    strokeWidth?: float
    opacity?: float
    zIndex?: float
    [key: str]: Any
/**
 * State of a region for rendering/interaction
 */
RegionState = Union['normal', 'hover', 'selected', 'disabled']
/**
 * Extended Region interface for rendering
 */
class RenderableRegion:
    style?: \'RegionStyle\'
    state?: RegionState
function isRenderableRegion(value: Any): value is RenderableRegion {
  return (
    isRegion(value) &&
    (typeof (value as RenderableRegion).style === 'undefined' ||
      typeof (value as RenderableRegion).style === 'object')
  )
}
const sampleStyledRegion: \'RenderableRegion\' = {
  id: 'region-2',
  name: 'Styled Region',
  boundaries: [
    [
      [100.0, 0.0],
      [101.0, 0.0],
      [101.0, 1.0],
      [100.0, 1.0],
      [100.0, 0.0],
    ],
  ],
  properties: Dict[str, Any],
  style: Dict[str, Any],
  state: 'normal',
}
const sampleRegion: \'Region\' = {
  id: 'region-1',
  name: 'Sample Region',
  boundaries: [
    [
      [100.0, 0.0],
      [101.0, 0.0],
      [101.0, 1.0],
      [100.0, 1.0],
      [100.0, 0.0],
    ],
  ],
  properties: Dict[str, Any],
  style: Dict[str, Any],
  state: 'normal',
}
const sampleViewport: \'ViewportState\' = {
  zoom: 10,
  center: [100.5, 0.5],
  bounds: [100.0, 0.0, 101.0, 1.0],
}