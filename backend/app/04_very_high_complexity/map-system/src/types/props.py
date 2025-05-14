from typing import Any, Dict, List, Union



  Position, 
  Dimensions, 
  TerrainType,
  MovementType,
  FactionAffiliation
} from './common'
  TileState,
  ViewportState,
  MovementState,
  POIData,
  RegionState,
  MapState
} from './state'
class MapContainerProps:
    children?: ReactNode
    initialState?: Partial[MapState]
    onStateChange?: (state: MapState) => None
    className?: str
class ViewportManagerProps:
    children?: ReactNode
    state: ViewportState
    onStateChange: (state: ViewportState) => None
    onDrag?: (offset: Position) => None
    onZoom?: (zoom: float) => None
    className?: str
class TileLayerProps:
    tiles: Dict[str, TileState>
    viewport: ViewportState
    onTileClick?: (position: Position) => None
    onTileHover?: Union[(position: Position, None) => None]
    selectedTile?: Position
    hoveredTile?: Position
    className?: str
class TileProps:
    state: TileState
    selected?: bool
    hovered?: bool
    onClick?: () => None
    onHover?: () => None
    className?: str
class POILayerProps:
    pois: Dict[str, POIData>
    viewport: ViewportState
    onPOIClick?: (id: str) => None
    onPOIHover?: Union[(id: str, None) => None]
    className?: str
class MovementSystemProps:
    state: MovementState
    tiles: Dict[str, TileState>
    onStateChange: (state: MovementState) => None
    onPathUpdate?: (path: List[Position]) => None
    className?: str
class FogOfWarProps:
    tiles: Dict[str, TileState>
    viewport: ViewportState
    currentPosition: Position
    visionRadius: float
    className?: str
class RegionBorderProps:
    region: RegionState
    viewport: ViewportState
    discovered: bool
    className?: str
class InfoPanelProps:
    tile?: TileState
    poi?: POIData
    region?: RegionState
    className?: str
class MapContextValue:
    state: MapState
    dispatch: (action: MapAction) => None
MapAction = Union[, { type: 'UPDATE_TILE'] payload: Dict[str, Any] }
  | { type: 'SELECT_TILE'; payload: Position | undefined }
  | { type: 'HOVER_TILE'; payload: Position | undefined }
  | { type: 'UPDATE_VIEWPORT'; payload: Partial<ViewportState> }
  | { type: 'UPDATE_MOVEMENT'; payload: Partial<MovementState> }
  | { type: 'UPDATE_POI'; payload: Dict[str, Any] }
  | { type: 'UPDATE_REGION'; payload: Dict[str, Any] } 