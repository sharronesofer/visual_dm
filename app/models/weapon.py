from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Weapon:
    id: int
    name: str
    damage_dice: str  # e.g. "1d8"
    damage_type: str  # e.g. "slashing"
    weapon_type: str  # e.g. "martial melee"
    properties: List[str]  # e.g. ["versatile", "finesse"]
    weight: float
    cost: float
    range_normal: Optional[int] = None
    range_long: Optional[int] = None
    versatile_damage: Optional[str] = None  # e.g. "1d10"
    
    @property
    def is_melee(self) -> bool:
        return "melee" in self.weapon_type.lower()
    
    @property
    def is_ranged(self) -> bool:
        return "ranged" in self.weapon_type.lower()
    
    @property
    def is_martial(self) -> bool:
        return "martial" in self.weapon_type.lower()
    
    @property
    def is_simple(self) -> bool:
        return "simple" in self.weapon_type.lower() 