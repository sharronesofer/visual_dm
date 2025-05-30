from typing import Any, Dict, Union


MaterialType = Union['wood', 'stone', 'metal', 'reinforced']
BuildingElementType = Union['wall', 'door', 'window']
class BuildingElement:
    id: str
    type: BuildingElementType
    position: Position
    health: float
    maxHealth: float
    material: MaterialType
class Wall:
    type: 'wall'
    thickness: float
    height: float
    isLoadBearing: bool
class Door:
    type: 'door'
    isOpen: bool
    isLocked: bool
    lockStrength?: float
    requiredKey?: str
class Window:
    type: 'window'
    isBroken: bool
    isBarricaded: bool
    barricadeHealth?: float
class MaterialProperties:
    weight: float
    resistance: Dict[str, Any]
class BuildingPhysics:
    gravity: float
    loadDistribution: float
    windResistance: float
    materialProperties: Dict[str, Any]
const BUILDING_PHYSICS_DEFAULTS: \'BuildingPhysics\' = {
  gravity: 9.81,
  loadDistribution: 0.7,
  windResistance: 0.5,
  materialProperties: Dict[str, Any],
      durability: 0.6,
      repairDifficulty: 0.5
    },
    stone: Dict[str, Any],
      durability: 0.9,
      repairDifficulty: 0.8
    },
    metal: Dict[str, Any],
      durability: 0.8,
      repairDifficulty: 0.7
    },
    reinforced: Dict[str, Any],
      durability: 1,
      repairDifficulty: 1
    }
  }
}
class BuildingStructure:
    id: str
    elements: Dict[str, BuildingElement>
    integrity: float 