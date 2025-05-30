from typing import Any, List


class TacticalHexCell:
    q: float
    r: float
    terrainType: str
    terrainEffect: str
    cover: float
    movementCost: float
    visibility: float
    elevation?: float
    features?: List[str]
    environmentalEffects?: List[{
    type: str
    magnitude: float
    duration?: float>
} 