import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.combat.combat_logger import (
    CombatLogger, LogLevel, LogCategory, CombatLogEntry
)
from app.core.enums import DamageType
from app.combat.damage_engine import AttackType, DamageResult

@pytest.fixture
def mock_db():
    db = Mock()
    collection = Mock()
    db.collection.return_value = collection
    return db

@pytest.fixture
def combat_logger(mock_db):
    return CombatLogger("test_combat_id", mock_db)

@pytest.fixture
def mock_damage_result():
    return DamageResult(
        raw_damage=15,
        final_damage=10,
        damage_type=DamageType.PHYSICAL,
        critical=False,
        absorbed_damage=3,
        damage_reduction=2,
        effects_applied=['bleeding'],
        hit_location='torso'
    )

def test_initialization(combat_logger):
    """Test CombatLogger initialization."""
    assert combat_logger.combat_id == "test_combat_id"
    assert combat_logger.current_round == 1
    assert combat_logger.current_turn == 1
    
    # Check statistics initialization
    stats = combat_logger.statistics
    assert stats['total_damage_dealt'] == 0
    assert stats['critical_hits'] == 0
    assert stats['misses'] == 0
    assert all(value == 0 for value in stats['damage_by_type'].values())
    assert all(value == 0 for value in stats['attacks_by_type'].values())

def test_log_initiative(combat_logger):
    """Test initiative logging."""
    combat_logger.log_initiative(
        actor_id="player1",
        roll=15,
        modifiers={'dexterity': 2, 'feat_bonus': 1},
        final_value=18
    )
    
    # Verify log entry creation
    combat_logger.log_collection.add.assert_called_once()
    call_args = combat_logger.log_collection.add.call_args[0][0]
    
    assert call_args['combat_id'] == "test_combat_id"
    assert call_args['category'] == LogCategory.INITIATIVE.value
    assert call_args['level'] == LogLevel.INFO.value
    assert "player1" in call_args['message']
    assert call_args['details']['roll'] == 15
    assert call_args['details']['final_value'] == 18

def test_log_attack(combat_logger):
    """Test attack logging and statistics update."""
    combat_logger.log_attack(
        attacker_id="player1",
        defender_id="enemy1",
        attack_type=AttackType.MELEE,
        roll=18,
        modifiers={'strength': 3, 'proficiency': 2},
        success=True,
        critical=True
    )
    
    # Verify log entry
    combat_logger.log_collection.add.assert_called_once()
    call_args = combat_logger.log_collection.add.call_args[0][0]
    
    assert call_args['actor_id'] == "player1"
    assert call_args['target_id'] == "enemy1"
    assert call_args['category'] == LogCategory.ATTACK.value
    
    # Verify statistics update
    assert combat_logger.statistics['attacks_by_type']['melee'] == 1
    assert combat_logger.statistics['critical_hits'] == 1
    assert combat_logger.statistics['misses'] == 0

def test_log_damage(combat_logger, mock_damage_result):
    """Test damage logging and statistics update."""
    combat_logger.log_damage(
        attacker_id="player1",
        defender_id="enemy1",
        damage_result=mock_damage_result
    )
    
    # Verify log entry
    combat_logger.log_collection.add.assert_called_once()
    call_args = combat_logger.log_collection.add.call_args[0][0]
    
    assert call_args['category'] == LogCategory.DAMAGE.value
    assert call_args['details']['final_damage'] == 10
    assert call_args['details']['damage_type'] == DamageType.PHYSICAL.value
    
    # Verify statistics update
    assert combat_logger.statistics['total_damage_dealt'] == 10
    assert combat_logger.statistics['damage_by_type'][DamageType.PHYSICAL.value] == 10
    assert combat_logger.statistics['participant_stats']['player1']['damage_dealt'] == 10
    assert combat_logger.statistics['participant_stats']['enemy1']['damage_taken'] == 10

def test_log_effect(combat_logger):
    """Test effect logging."""
    combat_logger.log_effect(
        source_id="player1",
        target_id="enemy1",
        effect="stunned",
        duration=2,
        is_applied=True
    )
    
    # Verify log entry
    combat_logger.log_collection.add.assert_called_once()
    call_args = combat_logger.log_collection.add.call_args[0][0]
    
    assert call_args['category'] == LogCategory.EFFECT.value
    assert "stunned" in call_args['message']
    assert call_args['details']['duration'] == 2
    
    # Verify statistics update
    assert combat_logger.statistics['effects_applied'] == 1

def test_log_movement(combat_logger):
    """Test movement logging."""
    start_pos = {'x': 0, 'y': 0}
    end_pos = {'x': 3, 'y': 4}
    
    combat_logger.log_movement(
        actor_id="player1",
        start_position=start_pos,
        end_position=end_pos,
        movement_type="walk"
    )
    
    # Verify log entry
    combat_logger.log_collection.add.assert_called_once()
    call_args = combat_logger.log_collection.add.call_args[0][0]
    
    assert call_args['category'] == LogCategory.MOVEMENT.value
    assert call_args['level'] == LogLevel.DEBUG.value
    assert call_args['details']['movement_type'] == "walk"
    assert call_args['details']['start_position'] == start_pos
    assert call_args['details']['end_position'] == end_pos

def test_log_environment_change(combat_logger):
    """Test environment change logging."""
    affected_area = {'x1': 0, 'y1': 0, 'x2': 5, 'y2': 5}
    
    combat_logger.log_environment_change(
        condition="difficult_terrain",
        affected_area=affected_area,
        duration=3
    )
    
    # Verify log entry
    combat_logger.log_collection.add.assert_called_once()
    call_args = combat_logger.log_collection.add.call_args[0][0]
    
    assert call_args['category'] == LogCategory.ENVIRONMENT.value
    assert "difficult_terrain" in call_args['message']
    assert call_args['details']['duration'] == 3
    assert call_args['details']['affected_area'] == affected_area

def test_round_and_turn_tracking(combat_logger):
    """Test round and turn tracking."""
    # Start first round
    combat_logger.start_round()
    assert combat_logger.statistics['rounds_elapsed'] == 1
    
    # Start turn for player1
    combat_logger.start_turn("player1")
    assert combat_logger.statistics['turns_elapsed'] == 1
    
    # Verify log entries
    assert combat_logger.log_collection.add.call_count == 2
    round_call = combat_logger.log_collection.add.call_args_list[0][0][0]
    turn_call = combat_logger.log_collection.add.call_args_list[1][0][0]
    
    assert round_call['category'] == LogCategory.SYSTEM.value
    assert "Round 1" in round_call['message']
    assert turn_call['actor_id'] == "player1"

def test_end_combat(combat_logger):
    """Test combat end logging with statistics."""
    # Add some statistics
    combat_logger.statistics['total_damage_dealt'] = 50
    combat_logger.statistics['critical_hits'] = 2
    
    combat_logger.end_combat(winner_id="player1", reason="enemy defeated")
    
    # Verify log entry
    combat_logger.log_collection.add.assert_called_once()
    call_args = combat_logger.log_collection.add.call_args[0][0]
    
    assert call_args['category'] == LogCategory.SYSTEM.value
    assert call_args['level'] == LogLevel.CRITICAL.value
    assert call_args['details']['winner_id'] == "player1"
    assert call_args['details']['reason'] == "enemy defeated"
    assert call_args['details']['final_statistics']['total_damage_dealt'] == 50
    assert call_args['details']['final_statistics']['critical_hits'] == 2

def test_get_combat_log_filtering(combat_logger):
    """Test combat log retrieval with filters."""
    # Mock query building
    query = Mock()
    combat_logger.log_collection.where.return_value = query
    query.where.return_value = query
    query.stream.return_value = [
        Mock(to_dict=lambda: {'message': 'Test log 1'}),
        Mock(to_dict=lambda: {'message': 'Test log 2'})
    ]
    
    # Test with multiple filters
    filters = {
        'category': LogCategory.ATTACK.value,
        'level': LogLevel.IMPORTANT.value,
        'actor_id': 'player1',
        'round_number': 1
    }
    
    logs = combat_logger.get_combat_log(filters)
    
    # Verify query building
    combat_logger.log_collection.where.assert_called_with('combat_id', '==', 'test_combat_id')
    assert query.where.call_count == 4  # One for each filter
    
    # Verify results
    assert len(logs) == 2
    assert logs[0]['message'] == 'Test log 1'
    assert logs[1]['message'] == 'Test log 2'

def test_get_statistics(combat_logger):
    """Test statistics retrieval."""
    # Add some test statistics
    combat_logger.statistics['total_damage_dealt'] = 100
    combat_logger.statistics['critical_hits'] = 3
    combat_logger.statistics['participant_stats'] = {
        'player1': {'damage_dealt': 60, 'damage_taken': 40},
        'enemy1': {'damage_dealt': 40, 'damage_taken': 60}
    }
    
    stats = combat_logger.get_statistics()
    
    assert stats['total_damage_dealt'] == 100
    assert stats['critical_hits'] == 3
    assert stats['participant_stats']['player1']['damage_dealt'] == 60
    assert stats['participant_stats']['enemy1']['damage_taken'] == 60 