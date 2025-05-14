import pytest
from app.combat.battlefield_conditions import BattlefieldCondition, BattlefieldConditionManager
from app.combat.battlefield_conditions import (
    BattlefieldConditionsManager,
    TerrainType,
    LightLevel,
    WeatherCondition,
    Position,
    TerrainEffect
)
from app.core.rules.balance_constants import (
    BASE_MOVEMENT_SPEED,
    DIAGONAL_MOVEMENT_COST,
    HALF_COVER_BONUS
)

class DummyParticipant:
    def __init__(self, position):
        self.position = position

@pytest.fixture
def manager():
    return BattlefieldConditionManager()

@pytest.fixture
def battlefield():
    return BattlefieldConditionsManager(10, 10)  # 10x10 grid

def test_add_and_remove_condition(manager):
    cond = BattlefieldCondition('cover', [(0,0)], 'cover', magnitude=1.5, duration=2)
    manager.add_condition(cond)
    assert len(manager.conditions) == 1
    manager.tick()
    assert cond.duration == 1
    manager.tick()
    assert cond.is_expired()
    manager.remove_expired()
    assert len(manager.conditions) == 0

def test_get_conditions_at(manager):
    cond1 = BattlefieldCondition('cover', [(1,1)], 'cover')
    cond2 = BattlefieldCondition('fire', [(2,2)], 'hazard')
    manager.add_condition(cond1)
    manager.add_condition(cond2)
    assert manager.get_conditions_at((1,1))[0].name == 'cover'
    assert manager.get_conditions_at((2,2))[0].name == 'fire'
    assert manager.get_conditions_at((0,0)) == []

def test_apply_conditions_modifiers(manager):
    cond1 = BattlefieldCondition('difficult_terrain', [(0,0)], 'terrain', magnitude=2.0)
    cond2 = BattlefieldCondition('cover', [(0,0)], 'cover', magnitude=1.2)
    manager.add_condition(cond1)
    manager.add_condition(cond2)
    participant = DummyParticipant((0,0))
    mods = manager.apply_conditions(participant)
    assert mods['movement'] == 1.0  # 0.5 * 2.0 = 1.0
    assert mods['defense'] == 1.2 * 1.2
    assert mods['cover'] == 1.2

def test_dynamic_spreading_fire(manager):
    fire = BattlefieldCondition('fire', [(0,0)], 'hazard', dynamic=True, duration=2)
    manager.add_condition(fire)
    area_sizes = []
    for _ in range(2):
        area_sizes.append(len(fire.area))
        manager.tick()
    assert area_sizes[1] > area_sizes[0]
    assert fire.is_expired()
    manager.remove_expired()
    assert len(manager.conditions) == 0

def test_apply_area_effect(manager):
    area = [(3,3), (3,4)]
    effect = {'name': 'spell_zone', 'effect_type': 'hazard', 'magnitude': 2.0, 'duration': 1}
    manager.apply_area_effect(area, effect)
    assert len(manager.conditions) == 1
    cond = manager.conditions[0]
    assert cond.name == 'spell_zone'
    assert (3,3) in cond.area and (3,4) in cond.area
    assert cond.magnitude == 2.0

def test_terrain_management(battlefield):
    # Test setting terrain
    assert battlefield.set_terrain(5, 5, TerrainType.DIFFICULT)
    assert battlefield.get_terrain(5, 5) == TerrainType.DIFFICULT
    
    # Test invalid coordinates
    assert not battlefield.set_terrain(11, 11, TerrainType.NORMAL)
    assert battlefield.get_terrain(11, 11) == TerrainType.NORMAL  # Default terrain
    
    # Test overwriting terrain
    assert battlefield.set_terrain(5, 5, TerrainType.HAZARDOUS)
    assert battlefield.get_terrain(5, 5) == TerrainType.HAZARDOUS

def test_weather_and_light(battlefield):
    # Test weather changes
    battlefield.set_weather(WeatherCondition.RAIN)
    assert battlefield.weather == WeatherCondition.RAIN
    
    battlefield.set_weather(WeatherCondition.STORM)
    assert battlefield.weather == WeatherCondition.STORM
    
    # Test light level changes
    battlefield.set_light_level(LightLevel.DIM)
    assert battlefield.light_level == LightLevel.DIM
    
    battlefield.set_light_level(LightLevel.DARK)
    assert battlefield.light_level == LightLevel.DARK

def test_temporary_effects(battlefield):
    effect = {
        'id': 'test_effect',
        'type': 'damage',
        'amount': 5,
        'duration': 3
    }
    
    # Test adding effect
    battlefield.add_temporary_effect(3, 3, effect)
    assert len(battlefield.temporary_effects.get((3, 3), [])) == 1
    assert battlefield.temporary_effects[(3, 3)][0] == effect
    
    # Test removing effect
    battlefield.remove_temporary_effect(3, 3, 'test_effect')
    assert len(battlefield.temporary_effects.get((3, 3), [])) == 0
    
    # Test removing non-existent effect
    battlefield.remove_temporary_effect(3, 3, 'non_existent')  # Should not raise error

def test_movement_cost_calculation(battlefield):
    # Set up some terrain
    battlefield.set_terrain(1, 1, TerrainType.DIFFICULT)
    battlefield.set_terrain(2, 2, TerrainType.WATER)
    
    # Test normal movement
    start = Position(0, 0)
    end = Position(1, 0)
    cost = battlefield.calculate_movement_cost(start, end)
    assert cost == 1.0  # Normal terrain, clear weather
    
    # Test difficult terrain
    end = Position(1, 1)
    cost = battlefield.calculate_movement_cost(start, end)
    assert cost == DIAGONAL_MOVEMENT_COST * 2.0  # Diagonal + difficult terrain
    
    # Test weather effects
    battlefield.set_weather(WeatherCondition.STORM)
    cost = battlefield.calculate_movement_cost(start, end)
    assert cost == DIAGONAL_MOVEMENT_COST * 2.0 * 2.0  # Diagonal + difficult + storm

def test_line_of_sight(battlefield):
    # Set up some blocking terrain
    battlefield.set_terrain(2, 2, TerrainType.IMPASSABLE)
    
    # Test clear line of sight
    start = Position(0, 0)
    end = Position(1, 1)
    assert battlefield.check_line_of_sight(start, end)
    
    # Test blocked line of sight
    end = Position(4, 4)
    assert not battlefield.check_line_of_sight(start, end)
    
    # Test weather effects on visibility
    battlefield.set_weather(WeatherCondition.HEAVY_FOG)
    end = Position(3, 3)  # Should be beyond heavy fog visibility
    assert not battlefield.check_line_of_sight(start, end)
    
    # Test light level effects
    battlefield.set_weather(WeatherCondition.CLEAR)
    battlefield.set_light_level(LightLevel.DARK)
    assert not battlefield.check_line_of_sight(start, end)  # Dark reduces visibility

def test_cover_bonus(battlefield):
    # Set up cover terrain
    battlefield.set_terrain(2, 2, TerrainType.COVER)
    
    # Test no cover
    attacker = Position(0, 0)
    target = Position(1, 1)
    assert battlefield.get_cover_bonus(attacker, target) == 0
    
    # Test with cover
    target = Position(2, 2)
    bonus = battlefield.get_cover_bonus(attacker, target)
    assert 2 <= bonus <= 4  # Cover bonus should be between 2-4 based on distance
    
    # Test total cover (blocked line of sight)
    battlefield.set_terrain(1, 1, TerrainType.IMPASSABLE)
    assert battlefield.get_cover_bonus(attacker, target) == float('inf')

def test_terrain_effects(battlefield):
    # Set up hazardous terrain
    battlefield.set_terrain(1, 1, TerrainType.HAZARDOUS)
    position = Position(1, 1)
    
    # Test hazardous terrain damage
    effects = battlefield.apply_terrain_effects(position)
    damage_effect = next(e for e in effects if e['type'] == 'damage')
    assert damage_effect['amount'] == 5
    
    # Test cover effects
    battlefield.set_terrain(1, 1, TerrainType.COVER)
    effects = battlefield.apply_terrain_effects(position)
    cover_effect = next(e for e in effects if e['type'] == 'cover')
    assert cover_effect['bonus'] == 2

def test_weather_effects(battlefield):
    position = Position(1, 1)
    
    # Test rain effects
    battlefield.set_weather(WeatherCondition.RAIN)
    effects = battlefield.apply_terrain_effects(position)
    rain_effect = next(e for e in effects if e['source'] == 'rain')
    assert 'ranged_attacks' in rain_effect['on']
    assert 'perception' in rain_effect['on']
    
    # Test storm effects
    battlefield.set_weather(WeatherCondition.STORM)
    effects = battlefield.apply_terrain_effects(position)
    storm_effect = next(e for e in effects if e['source'] == 'storm')
    assert 'attacks' in storm_effect['on']
    assert 'perception' in storm_effect['on']

def test_light_level_effects(battlefield):
    position = Position(1, 1)
    
    # Test dim light
    battlefield.set_light_level(LightLevel.DIM)
    effects = battlefield.apply_terrain_effects(position)
    dim_effect = next(e for e in effects if e['source'] == 'dim light')
    assert 'perception' in dim_effect['on']
    
    # Test darkness
    battlefield.set_light_level(LightLevel.DARK)
    effects = battlefield.apply_terrain_effects(position)
    dark_effect = next(e for e in effects if e['source'] == 'darkness')
    assert 'attacks' in dark_effect['on']
    assert 'perception' in dark_effect['on'] 