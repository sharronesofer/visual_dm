from typing import Any, Dict, List



class TileState:
    position: Position
    terrainType: TerrainType
    discovered: bool
    visible: bool
    selected: bool
    movementCost: float
    faction?: FactionAffiliation
    poi?: \'POIData\'
class ViewportState:
    offset: Position
    zoom: float
    visibleRange: Range
    loading: bool
    dimensions: Dict[str, Any]
class MovementState:
    active: bool
    path?: List[Position]
    startTile?: Position
    endTile?: Position
    currentTile: Position
    movementCost: float
    availableMoves: List[Position]
    movementType: MovementType
    isMoving: bool
class POIData:
    id: str
    position: Position
    type: str
    name: str
    description?: str
    faction?: FactionAffiliation
    discovered: bool
    interactable: bool
class RegionState:
    id: str
    boundaries: List[Position]
    discovered: bool
    name: str
    faction?: FactionAffiliation
    terrainDistribution: Dict[TerrainType, float>
class MapState:
    tiles: Dict[str, TileState>
    regions: Dict[str, RegionState>
    pois: Dict[str, POIData>
    viewport: \'ViewportState\'
    movement: \'MovementState\'
    selectedTile?: Position
    hoveredTile?: Position
TileKey = `${float},${float}`
const createTileKey = (position: Position): TileKey => 
  `${position.x},${position.y}`
const parseTileKey = (key: TileKey): Position => {
  const [xStr, yStr] = key.split(',')
  const x = Number(xStr)
  const y = Number(yStr)
  if (isNaN(x) || isNaN(y)) {
    throw new Error(`Invalid tile key: ${key}`)
  }
  return { x, y }
} 