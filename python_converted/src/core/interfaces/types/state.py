from typing import Any, Dict, List, Union


class TileState:
    position: Position
    terrainType: TerrainType
    visible: bool
    discovered: bool
    poi: bool
class POIData:
    id: str
    position: Position
    type: POIType
    name: str
    description: str
    discovered: bool
class ViewportState:
    minZoom: float
    maxZoom: float
    isDragging: bool
class PlayerState:
    position: Position
    visionRadius: float
    faction: str
    discoveredTiles: Set[str>
    visitedPOIs: Set[str>
class UIState:
    selectedTile: Union[Position, None]
    hoveredTile: Union[Position, None]
    selectedPOI: Union[str, None]
    hoveredPOI: Union[str, None]
    isContextMenuOpen: bool
    contextMenuPosition: Union[Position, None]
class GameState:
    turn: float
    phase: Union['movement', 'action', 'end']
    isPlayerTurn: bool
    availableMoves: List[Position]
    availableActions: List[str]
class MapState:
    tiles: Dict[str, TileState>
    pois: Dict[str, POIData>
    viewport: \'ViewportState\'
    player: \'PlayerState\'
    ui: \'UIState\'
    game: \'GameState\'
ActionType = Union[, { type: 'MOVE_PLAYER'] payload: Position }
  | { type: 'UPDATE_VIEWPORT'; payload: Partial<ViewportState> }
  | { type: 'SELECT_TILE'; payload: Position | null }
  | { type: 'HOVER_TILE'; payload: Position | null }
  | { type: 'SELECT_POI'; payload: str | null }
  | { type: 'HOVER_POI'; payload: str | null }
  | { type: 'DISCOVER_TILE'; payload: Position }
  | { type: 'VISIT_POI'; payload: str }
  | { type: 'SET_GAME_PHASE'; payload: GameState['phase'] }
  | { type: 'CALCULATE_AVAILABLE_MOVES'; payload: List[Position] }
  | { type: 'END_TURN' }
  | { type: 'TOGGLE_CONTEXT_MENU'; payload: Position | null }