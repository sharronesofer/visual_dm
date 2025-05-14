import pytest
from app.combat.initiative_tracker import InitiativeTracker

@pytest.fixture
def participants():
    return [
        {'id': 'A', 'dexterity': 16, 'initiative_bonus': 2},
        {'id': 'B', 'dexterity': 12, 'initiative_bonus': 1},
        {'id': 'C', 'dexterity': 8, 'initiative_bonus': 0},
    ]

def test_initiative_order_deterministic(monkeypatch, participants):
    # Patch random.randint to return fixed values for reproducibility
    rolls = [15, 10, 5]
    monkeypatch.setattr('random.randint', lambda a, b: rolls.pop(0))
    tracker = InitiativeTracker(participants)
    order = tracker.get_initiative_order()
    # A: 15+3+2=20, B: 10+1+1=12, C: 5-1+0=4
    assert order == ['A', 'B', 'C']

def test_turn_and_round_progression(monkeypatch, participants):
    monkeypatch.setattr('random.randint', lambda a, b: 10)
    tracker = InitiativeTracker(participants)
    assert tracker.get_turn_index() == 0
    assert tracker.get_round_number() == 1
    tracker.advance_turn()
    assert tracker.get_turn_index() == 1
    tracker.advance_turn()
    assert tracker.get_turn_index() == 2
    tracker.advance_turn()
    # Should wrap to next round
    assert tracker.get_turn_index() == 0
    assert tracker.get_round_number() == 2

def test_ready_and_delay_action(monkeypatch, participants):
    monkeypatch.setattr('random.randint', lambda a, b: 10)
    tracker = InitiativeTracker(participants)
    order = tracker.get_initiative_order()
    # Move 'A' to end
    tracker.ready_action('A')
    assert tracker.get_initiative_order() == ['B', 'C', 'A']
    # Delay 'B' (should move to end)
    tracker.delay_action('B')
    assert tracker.get_initiative_order() == ['C', 'A', 'B']

def test_get_current_participant(monkeypatch, participants):
    monkeypatch.setattr('random.randint', lambda a, b: 10)
    tracker = InitiativeTracker(participants)
    current = tracker.get_current_participant()
    assert current['id'] == 'A'
    tracker.advance_turn()
    current = tracker.get_current_participant()
    assert current['id'] == 'B'

def test_reset(monkeypatch, participants):
    monkeypatch.setattr('random.randint', lambda a, b: 10)
    tracker = InitiativeTracker(participants)
    tracker.advance_turn()
    tracker.advance_turn()
    tracker.reset()
    assert tracker.get_turn_index() == 0
    assert tracker.get_round_number() == 1
    assert len(tracker.get_initiative_order()) == 3

def test_empty_participants():
    tracker = InitiativeTracker([])
    assert tracker.get_initiative_order() == []
    assert tracker.get_current_participant() is None 