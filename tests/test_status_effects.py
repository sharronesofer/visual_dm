import pytest
from unittest.mock import MagicMock
from app.combat.status_effects_manager import StatusEffectManager
from datetime import datetime, timedelta
from app.combat.status_effects import (
    StatusEffectsSystem,
    StatusEffect,
    EffectType,
    DurationType,
    EffectModifier,
    load_effects_from_config
)
import os

class DummyParticipant:
    def __init__(self):
        self.id = "dummy"
        self.status_effects = []
        self.updated_at = None
        self.action_points = 1
        self.damage_taken = 0
        self.healed = 0
    def take_damage(self, amount):
        self.damage_taken += amount
    def heal(self, amount):
        self.healed += amount

@pytest.fixture
def db_session():
    db = MagicMock()
    db.commit = MagicMock()
    return db

@pytest.fixture
def manager(db_session):
    return StatusEffectManager(db_session)

@pytest.fixture
def participant():
    return DummyParticipant()

@pytest.fixture
def system():
    return StatusEffectsSystem()

@pytest.fixture
def basic_effect():
    return StatusEffect(
        id="test_effect",
        name="Test Effect",
        type=EffectType.BUFF,
        description="A test effect",
        modifiers=[
            EffectModifier("strength", 2, "add"),
            EffectModifier("speed", 1.5, "multiply")
        ],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="test"
    )

@pytest.fixture
def stackable_effect():
    return StatusEffect(
        id="stack_effect",
        name="Stacking Effect",
        type=EffectType.BUFF,
        description="A stacking effect",
        modifiers=[EffectModifier("damage", 1, "add")],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="test",
        stackable=True,
        max_stacks=3
    )

# Helper to reset the global system state between tests
def reset_status_effects_system():
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../app/combat/effects/effects_config.json')
    effects = load_effects_from_config(CONFIG_PATH)
    system = StatusEffectsSystem()
    for effect in effects.values():
        system.register_effect(effect)
    return system

def make_manager_with_effect(effect):
    system = StatusEffectsSystem()
    system.register_effect(effect)
    db = MagicMock()
    return StatusEffectManager(db, system=system)

def test_apply_effect_refresh():
    participant = DummyParticipant()
    effect = StatusEffect(
        id="buff_strength",
        name="Strength Buff",
        type=EffectType.BUFF,
        description="Increases strength by 2.",
        modifiers=[EffectModifier("strength", 2, "add")],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="potion",
        stackable=False,
        max_stacks=1
    )
    manager = make_manager_with_effect(effect)
    manager.apply_effect(participant, effect.id, stacking='refresh')
    manager.apply_effect(participant, effect.id, stacking='refresh')
    assert len(participant.status_effects) == 1
    assert participant.status_effects[0]['duration'] == 3

def test_apply_effect_replace():
    participant = DummyParticipant()
    effect = StatusEffect(
        id="buff_strength",
        name="Strength Buff",
        type=EffectType.BUFF,
        description="Increases strength by 2.",
        modifiers=[EffectModifier("strength", 2, "add")],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="potion",
        stackable=False,
        max_stacks=1
    )
    manager = make_manager_with_effect(effect)
    manager.apply_effect(participant, effect.id, stacking='replace')
    manager.apply_effect(participant, effect.id, stacking='replace')
    assert len(participant.status_effects) == 1
    assert participant.status_effects[0]['duration'] == 3

def test_apply_effect_stack():
    participant = DummyParticipant()
    effect = StatusEffect(
        id="debuff_poison",
        name="Poison",
        type=EffectType.DEBUFF,
        description="Deals 1 damage per round. Stackable.",
        modifiers=[EffectModifier("health", -1, "add")],
        duration_type=DurationType.ROUNDS,
        duration_value=2,
        source="enemy_attack",
        stackable=True,
        max_stacks=3
    )
    manager = make_manager_with_effect(effect)
    manager.apply_effect(participant, effect.id, stacking='stack')
    manager.apply_effect(participant, effect.id, stacking='stack')
    assert len(participant.status_effects) == 1
    assert participant.status_effects[0]['stacks'] == 2

def test_apply_effect_ignore():
    participant = DummyParticipant()
    effect = StatusEffect(
        id="buff_strength",
        name="Strength Buff",
        type=EffectType.BUFF,
        description="Increases strength by 2.",
        modifiers=[EffectModifier("strength", 2, "add")],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="potion",
        stackable=False,
        max_stacks=1
    )
    manager = make_manager_with_effect(effect)
    manager.apply_effect(participant, effect.id, stacking='ignore')
    manager.apply_effect(participant, effect.id, stacking='ignore')
    assert len(participant.status_effects) == 1
    assert participant.status_effects[0]['duration'] == 3

def test_remove_effect(manager, participant):
    effect_id = 'buff_strength'
    manager.apply_effect(participant, effect_id)
    manager.remove_effect(participant, effect_id)
    assert len(participant.status_effects) == 0

def test_decrement_durations():
    participant = DummyParticipant()
    effect = StatusEffect(
        id="buff_strength",
        name="Strength Buff",
        type=EffectType.BUFF,
        description="Increases strength by 2.",
        modifiers=[EffectModifier("strength", 2, "add")],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="potion",
        stackable=False,
        max_stacks=1
    )
    manager = make_manager_with_effect(effect)
    manager.apply_effect(participant, effect.id)
    # First decrement: duration goes to 2
    manager.decrement_durations(participant)
    assert participant.status_effects[0]['duration'] == 2
    # Second decrement: duration goes to 1
    manager.decrement_durations(participant)
    assert participant.status_effects[0]['duration'] == 1
    # Third decrement: effect is removed
    manager.decrement_durations(participant)
    assert len(participant.status_effects) == 0

def test_process_start_of_turn(manager):
    participant = DummyParticipant()
    effect_id = 'debuff_poison'
    manager.apply_effect(participant, effect_id)
    manager.process_start_of_turn(participant)
    # The dummy participant and effect config do not apply damage at start of turn
    assert participant.damage_taken == 0

def test_process_end_of_turn(manager, participant):
    effect_id = 'buff_strength'
    manager.apply_effect(participant, effect_id)
    manager.process_end_of_turn(participant)
    assert participant.healed == 0

def test_register_and_get_effect(system, basic_effect):
    system.register_effect(basic_effect)
    retrieved = system.get_effect("test_effect")
    assert retrieved == basic_effect
    assert retrieved.name == "Test Effect"
    assert retrieved.type == EffectType.BUFF

def test_apply_effect(system, basic_effect):
    system.register_effect(basic_effect)
    start_time = datetime.now()
    
    # Test applying effect
    instance_id = system.apply_effect("target1", "test_effect", start_time)
    assert instance_id is not None
    
    # Verify effect is active
    effects = system.get_active_effects("target1")
    assert len(effects) == 1
    assert effects[0].effect.id == "test_effect"
    assert effects[0].remaining_duration == 3

def test_stacking_effects(system, stackable_effect):
    system.register_effect(stackable_effect)
    start_time = datetime.now()
    
    # Apply effect multiple times
    instance_id = system.apply_effect("target1", "stack_effect", start_time)
    assert instance_id is not None
    
    # Add more stacks
    system.apply_effect("target1", "stack_effect", start_time)
    system.apply_effect("target1", "stack_effect", start_time)
    
    # Verify stacks
    effects = system.get_active_effects("target1")
    assert len(effects) == 1
    assert effects[0].current_stacks == 3
    
    # Try to exceed max stacks
    result = system.apply_effect("target1", "stack_effect", start_time)
    assert result is None
    assert effects[0].current_stacks == 3

def test_remove_effect(system, basic_effect, stackable_effect):
    system.register_effect(basic_effect)
    system.register_effect(stackable_effect)
    start_time = datetime.now()
    
    # Apply both effects
    basic_id = system.apply_effect("target1", "test_effect", start_time)
    stack_id = system.apply_effect("target1", "stack_effect", start_time)
    system.apply_effect("target1", "stack_effect", start_time)  # Add a stack
    
    # Remove basic effect
    assert system.remove_effect("target1", basic_id)
    effects = system.get_active_effects("target1")
    assert len(effects) == 1
    assert effects[0].effect.id == "stack_effect"
    
    # Remove one stack
    assert system.remove_effect("target1", stack_id, remove_all_stacks=False)
    assert effects[0].current_stacks == 1
    
    # Remove remaining stack
    assert system.remove_effect("target1", stack_id)
    assert len(system.get_active_effects("target1")) == 0

def test_duration_updates():
    from copy import deepcopy
    effect = StatusEffect(
        id="test_effect",
        name="Test Effect",
        type=EffectType.BUFF,
        description="A test effect",
        modifiers=[EffectModifier("strength", 2, "add")],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="test"
    )
    system = StatusEffectsSystem()
    system.register_effect(effect)
    start_time = datetime.now()
    system.apply_effect("target1", effect.id, start_time)
    # First update: duration goes to 2
    system.update_durations(start_time + timedelta(days=1), DurationType.ROUNDS.value)
    effects = system.get_active_effects("target1")
    assert len(effects) == 1
    assert effects[0].remaining_duration == 2
    # Second update: duration goes to 1
    system.update_durations(start_time + timedelta(days=2), DurationType.ROUNDS.value)
    effects = system.get_active_effects("target1")
    assert len(effects) == 1
    assert effects[0].remaining_duration == 1
    # Third update: effect is removed
    system.update_durations(start_time + timedelta(days=3), DurationType.ROUNDS.value)
    assert len(system.get_active_effects("target1")) == 0

def test_effect_modifiers(system, basic_effect):
    system.register_effect(basic_effect)
    start_time = datetime.now()
    
    system.apply_effect("target1", "test_effect", start_time)
    
    # Test additive modifier
    modified_strength = system.calculate_modified_value("target1", "strength", 10)
    assert modified_strength == 12  # Base 10 + 2
    
    # Test multiplicative modifier
    modified_speed = system.calculate_modified_value("target1", "speed", 10)
    assert modified_speed == 15  # Base 10 * 1.5

def test_immunities_and_resistances(system):
    immune_effect = StatusEffect(
        id="immune_effect",
        name="Immunity Effect",
        type=EffectType.BUFF,
        description="Grants immunities",
        modifiers=[],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="test",
        immunities_granted={"poison", "disease"}
    )
    
    resist_effect = StatusEffect(
        id="resist_effect",
        name="Resistance Effect",
        type=EffectType.BUFF,
        description="Grants resistances",
        modifiers=[],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="test",
        resistances_granted={"fire": 0.5, "cold": 0.25}
    )
    
    system.register_effect(immune_effect)
    system.register_effect(resist_effect)
    start_time = datetime.now()
    
    # Apply both effects
    system.apply_effect("target1", "immune_effect", start_time)
    system.apply_effect("target1", "resist_effect", start_time)
    
    # Test immunities
    immunities = system.get_immunities("target1")
    assert "poison" in immunities
    assert "disease" in immunities
    
    # Test resistances
    resistances = system.get_resistances("target1")
    assert resistances["fire"] == 0.5
    assert resistances["cold"] == 0.25

def test_effect_type_checking(system, basic_effect):
    system.register_effect(basic_effect)
    start_time = datetime.now()
    
    # Test before applying effect
    assert not system.has_effect_type("target1", EffectType.BUFF)
    
    # Apply effect and test
    system.apply_effect("target1", "test_effect", start_time)
    assert system.has_effect_type("target1", EffectType.BUFF)
    assert not system.has_effect_type("target1", EffectType.DEBUFF)

def test_immunity_prevention(system):
    effect1 = StatusEffect(
        id="effect1",
        name="First Effect",
        type=EffectType.BUFF,
        description="Grants immunity to effect2",
        modifiers=[],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="test",
        immunities_granted={"effect2"}
    )
    
    effect2 = StatusEffect(
        id="effect2",
        name="Second Effect",
        type=EffectType.DEBUFF,
        description="Should be prevented",
        modifiers=[],
        duration_type=DurationType.ROUNDS,
        duration_value=3,
        source="test"
    )
    
    system.register_effect(effect1)
    system.register_effect(effect2)
    start_time = datetime.now()
    
    # Apply immunity effect
    system.apply_effect("target1", "effect1", start_time)
    
    # Try to apply prevented effect
    result = system.apply_effect("target1", "effect2", start_time)
    assert result is None
    assert not system.has_effect_type("target1", EffectType.DEBUFF)

def test_permanent_effects(system, basic_effect):
    from copy import deepcopy
    effect = deepcopy(basic_effect)
    effect.duration_type = DurationType.PERMANENT
    system.register_effect(effect)
    start_time = datetime.now()
    system.apply_effect("target1", effect.id, start_time)
    for i in range(10):
        system.update_durations(start_time + timedelta(days=i), DurationType.PERMANENT.value)
        effects = system.get_active_effects("target1")
        assert len(effects) == 1
        assert effects[0].remaining_duration == effect.duration_value 