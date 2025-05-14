"""
Base hex cell implementation.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum, auto

class TerrainType(str, Enum):
    """Types of terrain that can exist in a hex cell."""
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    SWAMP = "swamp"
    WATER = "water"
    URBAN = "urban"
    DUNGEON = "dungeon"

class WeatherType(str, Enum):
    """Types of weather conditions that can affect a hex cell."""
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    STORM = "storm"
    SANDSTORM = "sandstorm"
    BLIZZARD = "blizzard"

@dataclass
class HexCell:
    """Base class for hex grid cells."""
    q: int  # Axial coordinate q
    r: int  # Axial coordinate r
    terrain: str = "plains"
    weather: Optional[str] = None
    discovered: bool = False
    effects: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.effects is None:
            self.effects = {}

    def serialize(self) -> Dict[str, Any]:
        """Convert the cell to a dictionary."""
        return {
            'q': self.q,
            'r': self.r,
            'terrain': self.terrain,
            'weather': self.weather,
            'discovered': self.discovered,
            'effects': self.effects
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'HexCell':
        """Create a HexCell from serialized data."""
        return cls(
            q=data['q'],
            r=data['r'],
            terrain=data.get('terrain', 'plains'),
            weather=data.get('weather'),
            discovered=data.get('discovered', False),
            effects=data.get('effects', {})
        ) 