import pytest
from datetime import datetime
from app.combat.initiative_tracker import InitiativeTracker
from app.core.models.combat import CombatState
from app.core.database import db

@pytest.fixture
def sample_participants():
    return [
        {'id': '1', 'name': 'Fighter', 'dexterity': 14, 'initiative_bonus': 2},
        {'id': '2', 'name': 'Rogue', 'dexterity': 16, 'initiative_bonus': 4},
        {'id': '3', 'name': 'Wizard', 'dexterity': 10, 'initiative_bonus': 0}
    ]

@pytest.fixture
def combat_state(sample_participants):
    state = CombatState(
        round_number=1,
        current_turn=0,
        initiative_order=[],
        status='active'
    )
    db.session.add(state)
    db.session.commit()
    return state

@pytest.fixture
def tracker(sample_participants):
    return InitiativeTracker(sample_participants)

@pytest.fixture
def db_tracker(sample_participants, combat_state):
    return InitiativeTracker(sample_participants, combat_state.id)

def test_initiative_calculation():
    """Test initiative calculation with fixed roll."""
    initiative = InitiativeTracker.calculate_initiative(
        dexterity=14,  # +2 modifier
        bonus=2,
        base_roll=15
    )
    assert initiative == 19  # 15 + 2 + 2

def test_initiative_order(tracker):
    """Test that initiative order is properly sorted."""
    order = tracker.get_initiative_order()
    assert len(order) == 3
    
    # Get initiatives for verification
    initiatives = {
        p['id']: p['initiative']
        for p in tracker.participants
    }
    
    # Verify descending order
    for i in range(len(order) - 1):
        assert initiatives[order[i]] >= initiatives[order[i + 1]]

def test_initiative_log(tracker):
    """Test that initiative log contains correct information."""
    log = tracker.get_initiative_log()
    assert len(log) == 3
    
    for entry in log:
        assert all(key in entry for key in [
            'participant_id', 'name', 'base_roll', 'dexterity_mod',
            'bonus', 'total', 'timestamp'
        ])
        
        # Verify timestamp format
        datetime.fromisoformat(entry['timestamp'])

def test_current_participant(tracker):
    """Test getting current participant."""
    current = tracker.get_current_participant()
    assert current is not None
    assert current['id'] == tracker.initiative_order[0]

def test_advance_turn(tracker):
    """Test turn advancement and round increment."""
    initial_round = tracker.get_round_number()
    
    # Advance through all participants
    for _ in range(len(tracker.participants)):
        round_changed, next_participant = tracker.advance_turn()
        assert next_participant is not None
        
    # Should be back to first participant in new round
    assert tracker.get_round_number() == initial_round + 1
    assert tracker.get_turn_index() == 0

def test_ready_action(tracker):
    """Test readying an action."""
    initial_order = tracker.get_initiative_order()
    current_id = initial_order[0]
    
    # Ready the current participant's action
    success = tracker.ready_action(current_id)
    assert success
    
    new_order = tracker.get_initiative_order()
    assert new_order[-1] == current_id  # Should be moved to end
    assert len(new_order) == len(initial_order)  # No duplicates

def test_invalid_ready_action(tracker):
    """Test readying an action for invalid participant."""
    success = tracker.ready_action('invalid_id')
    assert not success

def test_insert_participant(tracker):
    """Test inserting a new participant."""
    new_participant = {
        'id': '4',
        'name': 'Cleric',
        'dexterity': 12,
        'initiative_bonus': 1
    }
    
    initial_count = len(tracker.get_initiative_order())
    success = tracker.insert_participant(new_participant)
    
    assert success
    assert len(tracker.get_initiative_order()) == initial_count + 1
    assert new_participant['id'] in tracker.get_initiative_order()

def test_remove_participant(tracker):
    """Test removing a participant."""
    initial_order = tracker.get_initiative_order()
    to_remove = initial_order[0]
    
    success = tracker.remove_participant(to_remove)
    assert success
    
    new_order = tracker.get_initiative_order()
    assert len(new_order) == len(initial_order) - 1
    assert to_remove not in new_order

def test_database_integration(db_tracker):
    """Test integration with CombatState database."""
    # Verify initial state
    combat_state = db.session.query(CombatState).get(db_tracker.combat_state_id)
    assert combat_state.round_number == db_tracker.get_round_number()
    assert combat_state.initiative_order == db_tracker.get_initiative_order()
    
    # Make some changes
    db_tracker.advance_turn()
    db_tracker.ready_action(db_tracker.initiative_order[0])
    
    # Verify database was updated
    combat_state = db.session.query(CombatState).get(db_tracker.combat_state_id)
    assert combat_state.current_turn == db_tracker.get_turn_index()
    assert combat_state.initiative_order == db_tracker.get_initiative_order()

def test_dexterity_tiebreaker(sample_participants):
    """Test that dexterity is used as a tiebreaker for initiative."""
    # Create participants with same initiative bonus but different dexterity
    participants = [
        {'id': '1', 'name': 'High Dex', 'dexterity': 18, 'initiative_bonus': 0},
        {'id': '2', 'name': 'Low Dex', 'dexterity': 12, 'initiative_bonus': 0}
    ]
    
    # Force same base roll for both
    def mock_roll(*args, **kwargs):
        return 15
    
    import random
    original_randint = random.randint
    random.randint = mock_roll
    
    try:
        tracker = InitiativeTracker(participants)
        order = tracker.get_initiative_order()
        
        # High dex should go first
        assert order[0] == '1'
        assert order[1] == '2'
    finally:
        random.randint = original_randint  # Restore original random 