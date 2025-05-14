import pytest
from unittest.mock import MagicMock
from app.combat.status_effects_manager import StatusEffectManager
from datetime import datetime, timedelta
from app.combat.status_effects import (
    StatusEffectsSystem,
    StatusEffect,
    EffectType,
    DurationType,
    EffectModifier
)

class DummyParticipant:
    def __init__(self):
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

def test_apply_effect_refresh(manager, participant):
    effect = {'name': 'poisoned', 'duration': 3, 'magnitude': 2}
    manager.apply_effect(participant, effect, stacking='refresh')
    assert len(participant.status_effects) == 1
    assert participant.status_effects[0]['duration'] == 3
    # Refresh should update duration
    effect2 = {'name': 'poisoned', 'duration': 5, 'magnitude': 2}
    manager.apply_effect(participant, effect2, stacking='refresh')
    assert len(participant.status_effects) == 1
    assert participant.status_effects[0]['duration'] == 5

def test_apply_effect_replace(manager, participant):
    effect = {'name': 'blessed', 'duration': 2, 'magnitude': 1}
    manager.apply_effect(participant, effect, stacking='replace')
    effect2 = {'name': 'blessed', 'duration': 4, 'magnitude': 2}
    manager.apply_effect(participant, effect2, stacking='replace')
    assert len(participant.status_effects) == 1
    assert participant.status_effects[0]['duration'] == 4
    assert participant.status_effects[0]['magnitude'] == 2

def test_apply_effect_stack(manager, participant):
    effect = {'name': 'hasted', 'duration': 2, 'magnitude': 1}
    manager.apply_effect(participant, effect, stacking='stack')
    manager.apply_effect(participant, effect, stacking='stack')
    assert len(participant.status_effects) == 2

def test_apply_effect_ignore(manager, participant):
    effect = {'name': 'slowed', 'duration': 2, 'magnitude': 1}
    manager.apply_effect(participant, effect, stacking='ignore')
    manager.apply_effect(participant, {'name': 'slowed', 'duration': 5, 'magnitude': 2}, stacking='ignore')
    assert len(participant.status_effects) == 1
    assert participant.status_effects[0]['duration'] == 2

def test_remove_effect(manager, participant):
    effect = {'name': 'stunned', 'duration': 1}
    manager.apply_effect(participant, effect)
    manager.remove_effect(participant, 'stunned')
    assert len(participant.status_effects) == 0

def test_decrement_durations(manager, participant):
    effect = {'name': 'poisoned', 'duration': 2}
    manager.apply_effect(participant, effect)
    manager.decrement_durations(participant)
    assert participant.status_effects[0]['duration'] == 1
    manager.decrement_durations(participant)
    assert len(participant.status_effects) == 0

def test_process_start_of_turn(manager, participant):
    effect = {'name': 'poisoned', 'duration': 2, 'magnitude': 3, 'timing': 'start'}
    manager.apply_effect(participant, effect)
    manager.process_start_of_turn(participant)
    assert participant.damage_taken == 3

def test_process_end_of_turn(manager, participant):
    effect = {'name': 'blessed', 'duration': 2, 'magnitude': 2, 'timing': 'end'}
    manager.apply_effect(participant, effect)
    manager.process_end_of_turn(participant)
    assert participant.healed == 2

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

def test_duration_updates(system, basic_effect):
    system.register_effect(basic_effect)
    start_time = datetime.now()
    
    system.apply_effect("target1", "test_effect", start_time)
    
    # Update duration
    system.update_durations(start_time + timedelta(rounds=1), DurationType.ROUNDS)
    effects = system.get_active_effects("target1")
    assert len(effects) == 1
    assert effects[0].remaining_duration == 2
    
    # Update until expired
    system.update_durations(start_time + timedelta(rounds=2), DurationType.ROUNDS)
    system.update_durations(start_time + timedelta(rounds=3), DurationType.ROUNDS)
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

def test_permanent_effects(system):
    permanent_effect = StatusEffect(
        id="permanent",
        name="Permanent Effect",
        type=EffectType.CONDITION,
        description="Never expires",
        modifiers=[],
        duration_type=DurationType.PERMANENT,
        duration_value=0,
        source="test"
    )
    
    system.register_effect(permanent_effect)
    start_time = datetime.now()
    
    system.apply_effect("target1", "permanent", start_time)
    
    # Try to update duration multiple times
    for i in range(10):
        system.update_durations(
            start_time + timedelta(rounds=i),
            DurationType.PERMANENT
        )
        
    # Effect should still be active
    effects = system.get_active_effects("target1")
    assert len(effects) == 1
    assert effects[0].effect.id == "permanent" 