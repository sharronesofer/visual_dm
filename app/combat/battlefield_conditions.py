from typing import List, Dict, Tuple, Optional, Any, Set
from enum import Enum
import math
from dataclasses import dataclass
from app.core.rules.balance_constants import (
    BASE_MOVEMENT_SPEED,
    DIAGONAL_MOVEMENT_COST
)

class TerrainType(Enum):
    """Types of terrain that can exist on the battlefield."""
    NORMAL = "normal"
    DIFFICULT = "difficult"
    HAZARDOUS = "hazardous"
    IMPASSABLE = "impassable"
    COVER = "cover"
    ELEVATED = "elevated"
    WATER = "water"
    
class LightLevel(Enum):
    """Light levels affecting visibility."""
    BRIGHT = "bright"
    DIM = "dim"
    DARK = "dark"
    
class WeatherCondition(Enum):
    """Weather conditions affecting the battlefield."""
    CLEAR = "clear"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    FOG = "fog"
    HEAVY_FOG = "heavy_fog"
    SNOW = "snow"
    STORM = "storm"

@dataclass
class Position:
    """Represents a position on the battlefield grid."""
    x: int
    y: int
    z: int = 0  # For elevation
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate distance to another position including elevation."""
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        dz = abs(self.z - other.z)
        
        # Calculate horizontal distance using diagonal movement rules
        horizontal = math.sqrt(dx * dx + dy * dy) * DIAGONAL_MOVEMENT_COST
        # Add vertical distance
        return math.sqrt(horizontal * horizontal + dz * dz)

@dataclass
class TerrainEffect:
    """Represents the effects of a terrain type."""
    movement_cost: float  # Multiplier for movement cost
    provides_cover: bool  # Whether this terrain provides cover
    damage_per_turn: int  # Damage dealt per turn (for hazardous terrain)
    elevation: int       # Height of the terrain (for elevated terrain)
    
class BattlefieldCondition:
    """
    Represents an environmental or terrain effect on the battlefield.
    """
    def __init__(self, name: str, area: List[Tuple[int, int]], effect_type: str, magnitude: float = 1.0, duration: Optional[int] = None, source: Optional[str] = None, dynamic: bool = False):
        """
        Args:
            name: Name of the condition (e.g., 'fire', 'cover', 'difficult_terrain')
            area: List of (q, r) hex coordinates affected
            effect_type: Type/category of effect (e.g., 'hazard', 'terrain', 'cover')
            magnitude: Strength of the effect
            duration: Rounds the effect lasts (None for permanent)
            source: Source of the effect (e.g., spell, trap)
            dynamic: If True, the area can change (e.g., spreading fire)
        """
        self.name = name
        self.area = set(area)
        self.effect_type = effect_type
        self.magnitude = magnitude
        self.duration = duration
        self.source = source
        self.dynamic = dynamic

    def tick(self):
        """Advance the condition by one round, updating duration and area if dynamic."""
        if self.duration is not None:
            self.duration -= 1
        # Example: Spreading fire (expand area)
        if self.dynamic and self.name == 'fire':
            self._spread_fire()

    def _spread_fire(self):
        """Example logic for spreading fire to adjacent hexes."""
        new_area = set(self.area)
        for q, r in self.area:
            for dq, dr in [(-1,0),(1,0),(0,-1),(0,1),(-1,1),(1,-1)]:
                new_area.add((q+dq, r+dr))
        self.area = new_area

    def is_expired(self) -> bool:
        return self.duration is not None and self.duration <= 0

class BattlefieldConditionManager:
    """
    Manages all battlefield conditions and applies their effects to participants.
    """
    def __init__(self):
        self.conditions: List[BattlefieldCondition] = []

    def add_condition(self, condition: BattlefieldCondition):
        self.conditions.append(condition)

    def remove_expired(self):
        self.conditions = [c for c in self.conditions if not c.is_expired()]

    def tick(self):
        for condition in self.conditions:
            condition.tick()
        self.remove_expired()

    def get_conditions_at(self, pos: Tuple[int, int]) -> List[BattlefieldCondition]:
        return [c for c in self.conditions if pos in c.area]

    def apply_conditions(self, participant: Any) -> Dict[str, float]:
        """
        Aggregate and apply all relevant conditions to a participant at their position.
        Returns a dict of modifiers (e.g., movement, defense, damage).
        """
        pos = getattr(participant, 'position', None)
        if pos is None:
            return {}
        modifiers = {'movement': 1.0, 'defense': 1.0, 'damage': 1.0, 'cover': 0.0}
        for cond in self.get_conditions_at(pos):
            if cond.name == 'difficult_terrain':
                modifiers['movement'] *= 0.5 * cond.magnitude
            elif cond.name == 'cover':
                modifiers['defense'] *= 1.2 * cond.magnitude
                modifiers['cover'] += cond.magnitude
            elif cond.name == 'fire':
                modifiers['damage'] += 1.0 * cond.magnitude
            # Add more condition types as needed
        return modifiers

    def apply_area_effect(self, area: List[Tuple[int, int]], effect: Dict[str, Any]):
        """
        Apply an area effect (e.g., spell, hazard) to the specified area.
        """
        condition = BattlefieldCondition(
            name=effect['name'],
            area=area,
            effect_type=effect.get('effect_type', 'hazard'),
            magnitude=effect.get('magnitude', 1.0),
            duration=effect.get('duration'),
            source=effect.get('source'),
            dynamic=effect.get('dynamic', False)
        )
        self.add_condition(condition)

class BattlefieldConditionsManager:
    """
    Manages environmental conditions and terrain effects on the battlefield.
    """
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.terrain_grid: Dict[Tuple[int, int], TerrainType] = {}
        self.terrain_effects: Dict[TerrainType, TerrainEffect] = {
            TerrainType.NORMAL: TerrainEffect(1.0, False, 0, 0),
            TerrainType.DIFFICULT: TerrainEffect(2.0, False, 0, 0),
            TerrainType.HAZARDOUS: TerrainEffect(1.5, False, 5, 0),
            TerrainType.IMPASSABLE: TerrainEffect(float('inf'), False, 0, 0),
            TerrainType.COVER: TerrainEffect(1.0, True, 0, 0),
            TerrainType.ELEVATED: TerrainEffect(1.5, True, 0, 1),
            TerrainType.WATER: TerrainEffect(2.0, False, 0, 0)
        }
        self.weather: WeatherCondition = WeatherCondition.CLEAR
        self.light_level: LightLevel = LightLevel.BRIGHT
        self.temporary_effects: Dict[Tuple[int, int], List[Dict]] = {}
        
    def set_terrain(self, x: int, y: int, terrain_type: TerrainType) -> bool:
        """Set the terrain type at a specific position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.terrain_grid[(x, y)] = terrain_type
            return True
        return False
        
    def get_terrain(self, x: int, y: int) -> TerrainType:
        """Get the terrain type at a specific position."""
        return self.terrain_grid.get((x, y), TerrainType.NORMAL)
        
    def set_weather(self, condition: WeatherCondition):
        """Set the current weather condition."""
        self.weather = condition
        
    def set_light_level(self, level: LightLevel):
        """Set the current light level."""
        self.light_level = level
        
    def add_temporary_effect(self, x: int, y: int, effect: Dict):
        """Add a temporary effect to a position."""
        if (x, y) not in self.temporary_effects:
            self.temporary_effects[(x, y)] = []
        self.temporary_effects[(x, y)].append(effect)
        
    def remove_temporary_effect(self, x: int, y: int, effect_id: str):
        """Remove a temporary effect from a position."""
        if (x, y) in self.temporary_effects:
            self.temporary_effects[(x, y)] = [
                e for e in self.temporary_effects[(x, y)]
                if e.get('id') != effect_id
            ]
            
    def calculate_movement_cost(self, start: Position, end: Position) -> float:
        """Calculate the movement cost between two positions."""
        # Get base distance
        base_distance = start.distance_to(end)
        
        # Get terrain costs
        start_terrain = self.get_terrain(start.x, start.y)
        end_terrain = self.get_terrain(end.x, end.y)
        terrain_cost = max(
            self.terrain_effects[start_terrain].movement_cost,
            self.terrain_effects[end_terrain].movement_cost
        )
        
        # Apply weather effects
        weather_multiplier = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.RAIN: 1.2,
            WeatherCondition.HEAVY_RAIN: 1.5,
            WeatherCondition.FOG: 1.0,
            WeatherCondition.HEAVY_FOG: 1.0,
            WeatherCondition.SNOW: 1.5,
            WeatherCondition.STORM: 2.0
        }[self.weather]
        
        return base_distance * terrain_cost * weather_multiplier
        
    def check_line_of_sight(self, start: Position, end: Position) -> bool:
        """Check if there is line of sight between two positions."""
        # Implementation of Bresenham's line algorithm
        dx = abs(end.x - start.x)
        dy = abs(end.y - start.y)
        x, y = start.x, start.y
        n = 1 + dx + dy
        x_inc = 1 if end.x > start.x else -1
        y_inc = 1 if end.y > start.y else -1
        error = dx - dy
        dx *= 2
        dy *= 2

        blocked_positions: Set[Tuple[int, int]] = set()
        for pos, terrain in self.terrain_grid.items():
            if terrain in [TerrainType.IMPASSABLE]:
                blocked_positions.add(pos)

        while n > 0:
            if (x, y) in blocked_positions:
                return False
                
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx
                
            n -= 1
            
        # Check weather and light effects
        max_visibility = {
            WeatherCondition.CLEAR: float('inf'),
            WeatherCondition.RAIN: 60,
            WeatherCondition.HEAVY_RAIN: 30,
            WeatherCondition.FOG: 30,
            WeatherCondition.HEAVY_FOG: 15,
            WeatherCondition.SNOW: 45,
            WeatherCondition.STORM: 20
        }[self.weather]
        
        light_multiplier = {
            LightLevel.BRIGHT: 1.0,
            LightLevel.DIM: 0.5,
            LightLevel.DARK: 0.25
        }[self.light_level]
        
        max_visibility *= light_multiplier
        
        return start.distance_to(end) <= max_visibility
        
    def get_cover_bonus(self, attacker: Position, target: Position) -> int:
        """Calculate cover bonus to AC and saves based on terrain."""
        if not self.check_line_of_sight(attacker, target):
            return float('inf')  # Total cover
            
        # Check if target is in cover
        target_terrain = self.get_terrain(target.x, target.y)
        if self.terrain_effects[target_terrain].provides_cover:
            # Calculate angle and distance to determine cover effectiveness
            angle = math.atan2(target.y - attacker.y, target.x - attacker.x)
            distance = attacker.distance_to(target)
            
            # More effective cover at longer distances
            distance_factor = min(1.0, distance / 30.0)
            return int(2 + distance_factor * 2)  # 2-4 bonus to AC
            
        return 0
        
    def apply_terrain_effects(self, position: Position) -> List[Dict]:
        """Get all effects that apply to a position."""
        effects = []
        
        # Get terrain effects
        terrain = self.get_terrain(position.x, position.y)
        terrain_effect = self.terrain_effects[terrain]
        
        if terrain_effect.damage_per_turn > 0:
            effects.append({
                'type': 'damage',
                'amount': terrain_effect.damage_per_turn,
                'source': f'{terrain.value} terrain'
            })
            
        if terrain_effect.provides_cover:
            effects.append({
                'type': 'cover',
                'bonus': 2,
                'source': f'{terrain.value} terrain'
            })
            
        # Add temporary effects
        if (position.x, position.y) in self.temporary_effects:
            effects.extend(self.temporary_effects[(position.x, position.y)])
            
        # Add weather effects
        if self.weather != WeatherCondition.CLEAR:
            weather_effects = {
                WeatherCondition.RAIN: {
                    'type': 'disadvantage',
                    'on': ['ranged_attacks', 'perception'],
                    'source': 'rain'
                },
                WeatherCondition.HEAVY_RAIN: {
                    'type': 'disadvantage',
                    'on': ['ranged_attacks', 'perception'],
                    'source': 'heavy rain'
                },
                WeatherCondition.FOG: {
                    'type': 'disadvantage',
                    'on': ['perception'],
                    'source': 'fog'
                },
                WeatherCondition.HEAVY_FOG: {
                    'type': 'disadvantage',
                    'on': ['attacks', 'perception'],
                    'source': 'heavy fog'
                },
                WeatherCondition.SNOW: {
                    'type': 'disadvantage',
                    'on': ['ranged_attacks', 'perception'],
                    'source': 'snow'
                },
                WeatherCondition.STORM: {
                    'type': 'disadvantage',
                    'on': ['attacks', 'perception'],
                    'source': 'storm'
                }
            }
            if self.weather in weather_effects:
                effects.append(weather_effects[self.weather])
                
        # Add light level effects
        if self.light_level != LightLevel.BRIGHT:
            light_effects = {
                LightLevel.DIM: {
                    'type': 'disadvantage',
                    'on': ['perception'],
                    'source': 'dim light'
                },
                LightLevel.DARK: {
                    'type': 'disadvantage',
                    'on': ['attacks', 'perception'],
                    'source': 'darkness'
                }
            }
            effects.append(light_effects[self.light_level])
            
        return effects 