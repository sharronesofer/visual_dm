from typing import Any, List
from enum import Enum


class ExplorationFeature:
    category: POICategory.EXPLORATION
    discoveryDC: float
    interactionType: List[InteractionType]
    seasonalAvailability: List[Season]
class Ruins:
    type: BuildingType.RUINS
    civilization: str
    age: float
    preservationState: \'PreservationState\'
    artifactTypes: List[ArtifactType]
class Campsite:
    type: BuildingType.CAMPSITE
    capacity: float
    facilities: List[CampsiteFacility]
    restQuality: \'RestQuality\'
class Landmark:
    type: BuildingType.LANDMARK
    landmarkType: \'LandmarkType\'
    visibility: float
    significance: List[str]
class ResourceNode:
    type: BuildingType.RESOURCE_NODE
    resourceType: \'ResourceType\'
    quantity: float
    respawnTime: float
    toolsRequired: List[str]
class InteractionType(Enum):
    GATHER = 'GATHER'
    INVESTIGATE = 'INVESTIGATE'
    REST = 'REST'
    NAVIGATE = 'NAVIGATE'
    HARVEST = 'HARVEST'
class Season(Enum):
    SPRING = 'SPRING'
    SUMMER = 'SUMMER'
    AUTUMN = 'AUTUMN'
    WINTER = 'WINTER'
class PreservationState(Enum):
    PRISTINE = 'PRISTINE'
    WEATHERED = 'WEATHERED'
    DAMAGED = 'DAMAGED'
    CRUMBLING = 'CRUMBLING'
    BURIED = 'BURIED'
class ArtifactType(Enum):
    POTTERY = 'POTTERY'
    WEAPONS = 'WEAPONS'
    JEWELRY = 'JEWELRY'
    SCROLLS = 'SCROLLS'
    STATUES = 'STATUES'
    TOOLS = 'TOOLS'
class CampsiteFacility(Enum):
    FIREPIT = 'FIREPIT'
    SHELTER = 'SHELTER'
    WATER_SOURCE = 'WATER_SOURCE'
    STORAGE = 'STORAGE'
    WORKBENCH = 'WORKBENCH'
class RestQuality(Enum):
    POOR = 'POOR'
    ADEQUATE = 'ADEQUATE'
    GOOD = 'GOOD'
    EXCELLENT = 'EXCELLENT'
class LandmarkType(Enum):
    NATURAL = 'NATURAL'
    ARTIFICIAL = 'ARTIFICIAL'
    MAGICAL = 'MAGICAL'
    HISTORICAL = 'HISTORICAL'
class ResourceType(Enum):
    ORE = 'ORE'
    HERBS = 'HERBS'
    WOOD = 'WOOD'
    CRYSTAL = 'CRYSTAL'
    ANIMAL = 'ANIMAL'
    MAGICAL = 'MAGICAL' 