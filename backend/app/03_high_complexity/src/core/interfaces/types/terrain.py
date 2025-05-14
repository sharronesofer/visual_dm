from typing import Any, Dict, List
from enum import Enum



class TerrainFeatureType(Enum):
    PLAIN = 'PLAIN'
    MOUNTAIN = 'MOUNTAIN'
    WATER = 'WATER'
    FOREST = 'FOREST'
    SWAMP = 'SWAMP'
class TerrainModificationType(Enum):
    LEVEL = 'LEVEL'
    SMOOTH = 'SMOOTH'
    RAMP = 'RAMP'
    FOUNDATION = 'FOUNDATION'
class TerrainModification:
    position: GridPosition
    type: \'TerrainModificationType\'
    params: Dict[str, Any>
class TerrainAnalysisResult:
    slope: float
    buildabilityScore: float
    nearbyFeatures: List[TerrainFeatureType]
    environmentalImpact: float
class TerrainFeature:
    type: \'TerrainFeatureType\'
    position: Coordinates
    size: GridDimensions
class BuildableArea:
    position: Coordinates
    size: GridDimensions
    slope: float
    preferredCategories: List[POICategory]
class TerrainData:
    heightMap: List[List[float]]
    features: List[TerrainFeature]
    buildableAreas: List[BuildableArea] 