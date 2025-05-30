from typing import Any, Dict, Union


class MapContainerProps:
    className?: str
class ViewportManagerProps:
    viewport: Viewport
    onViewportChange: (viewport: Viewport) => None
    children: React.ReactNode
    className?: str
class TileLayerProps:
    tiles: Dict[str, TileState>
    viewport: Viewport
    selectedTile: Union[Position, None]
    hoveredTile: Union[Position, None]
    onTileClick?: (position: Position) => None
    onTileHover?: (position: Position) => None
    className?: str
class TileProps:
    state: TileState
    selected: bool
    hovered: bool
    onClick?: () => None
    onHover?: () => None
    className?: str
class POILayerProps:
    pois: Dict[str, POIData>
    viewport: Viewport
    onPOIClick?: (id: str) => None
    onPOIHover?: Union[(id: str, None) => None]
    className?: str
class FogOfWarProps:
    tiles: Dict[str, TileState>
    viewport: Viewport
    currentPosition: Position
    visionRadius: float
    className?: str