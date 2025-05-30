from typing import Any, Dict, List
from enum import Enum



class PlacementPattern(Enum):
    GRID = 'GRID'
    ORGANIC = 'ORGANIC'
    CLUSTERED = 'CLUSTERED'
    LINEAR = 'LINEAR'
    RADIAL = 'RADIAL'
class POICategory(Enum):
    SETTLEMENT = 'SETTLEMENT'
    DUNGEON = 'DUNGEON'
    LANDMARK = 'LANDMARK'
    RESOURCE = 'RESOURCE'
    SOCIAL = 'SOCIAL'
    EXPLORATION = 'EXPLORATION'
class POIPlacementRules:
    minElevation: float
    maxElevation: float
    validTerrainTypes: List[TerrainFeatureType]
    invalidTerrainTypes: List[TerrainFeatureType]
    minDistanceFromType: Dict[POIType, float>
class CategoryConfig:
    type: POIType
    subtype: POISubtype
    count: float
    rules: \'POIPlacementRules\'
class SpatialLayoutConfig:
    minDistance: float
    maxPOIs: float
    placementPattern: \'PlacementPattern\'
    categories: List[CategoryConfig]
class POIPlacement:
    id: str
    category: \'POICategory\'
    position: Dict[str, Any]
class PathSegment:
    /** Start position of the path segment */
  from: Dict[str, Any]
  /** Path type: 'PRIMARY' (main road) or 'SECONDARY' (side street) */
  type: 'PRIMARY' | 'SECONDARY'
  /** Width of the path in grid cells */
  width: float
  /** Additional metadata for navigation, decoration, etc. */
  metadata?: Record<string, any>
}
class SpatialLayoutResult:
    placements: List[POIPlacement]
    paths: List[PathSegment]
    metrics: Dict[str, Any] 