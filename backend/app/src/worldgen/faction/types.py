from typing import Any, Dict, List, Union


FactionType = Union['guild', 'order', 'syndicate', 'militia', 'cult']
class FactionStyle:
    id: str
    name: str
    description: str
    colorScheme: List[str]
    architecturalFeatures: List[str]
    decor: List[str]
class FactionRoom:
    id: str
    type: str
    x: float
    y: float
    width: float
    length: float
    specialPurpose?: str
class FactionNPC:
    id: str
    role: str
    hierarchyLevel: float
    behaviorProfile: str
class SecurityFeature:
    id: str
    type: str
    location: Dict[str, Any]
class FactionHQLayout:
    rooms: List[FactionRoom]
    npcs: List[FactionNPC]
    security: List[SecurityFeature]
    style: \'FactionStyle\'
    decor: List[str] 