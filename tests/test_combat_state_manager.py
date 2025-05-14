import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.combat.state_manager import CombatStateManager, CombatState

@pytest.fixture
def mock_app():
    app = Mock()
    app.db.collection.return_value = Mock()
    app.logger = Mock()
    return app

@pytest.fixture
def state_manager(mock_app):
    return CombatStateManager(mock_app)

@pytest.fixture
def sample_combat_state():
    return {
        'combat_id': 'test_combat_1',
        'participants': ['player1', 'player2', 'enemy1'],
        'initiative_order': ['player1', 'enemy1', 'player2'],
        'current_round': 2,
        'current_turn': 1,
        'active_effects': {
            'player1': [{'type': 'buff', 'duration': 2}],
            'enemy1': [{'type': 'debuff', 'duration': 1}]
        },
        'battlefield_conditions': [
            {'type': 'difficult_terrain', 'area': 'north'},
            {'type': 'darkness', 'area': 'all'}
        ],
        'status': 'active',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }

@pytest.mark.asyncio
async def test_save_combat_state(state_manager, sample_combat_state):
    # Mock the database update operation
    state_manager.combat_states.update_one.return_value = Mock(modified_count=1)
    
    # Test successful save
    result = await state_manager.save_combat_state(
        sample_combat_state['combat_id'],
        sample_combat_state
    )
    assert result is True
    state_manager.combat_states.update_one.assert_called_once()
    
    # Test save with database error
    state_manager.combat_states.update_one.side_effect = Exception("Database error")
    result = await state_manager.save_combat_state(
        sample_combat_state['combat_id'],
        sample_combat_state
    )
    assert result is False

@pytest.mark.asyncio
async def test_load_combat_state(state_manager, sample_combat_state):
    # Mock the database find operation
    state_manager.combat_states.find_one.return_value = {
        **sample_combat_state,
        'created_at': sample_combat_state['created_at'].isoformat(),
        'updated_at': sample_combat_state['updated_at'].isoformat()
    }
    
    # Test successful load
    result = await state_manager.load_combat_state(sample_combat_state['combat_id'])
    assert isinstance(result, CombatState)
    assert result.combat_id == sample_combat_state['combat_id']
    assert result.participants == sample_combat_state['participants']
    
    # Test load with non-existent combat
    state_manager.combat_states.find_one.return_value = None
    result = await state_manager.load_combat_state('non_existent_combat')
    assert result is None
    
    # Test load with database error
    state_manager.combat_states.find_one.side_effect = Exception("Database error")
    result = await state_manager.load_combat_state(sample_combat_state['combat_id'])
    assert result is None

@pytest.mark.asyncio
async def test_delete_combat_state(state_manager):
    # Mock the database delete operation
    state_manager.combat_states.delete_one.return_value = Mock(deleted_count=1)
    
    # Test successful delete
    result = await state_manager.delete_combat_state('test_combat_1')
    assert result is True
    state_manager.combat_states.delete_one.assert_called_once()
    
    # Test delete non-existent combat
    state_manager.combat_states.delete_one.return_value = Mock(deleted_count=0)
    result = await state_manager.delete_combat_state('non_existent_combat')
    assert result is False
    
    # Test delete with database error
    state_manager.combat_states.delete_one.side_effect = Exception("Database error")
    result = await state_manager.delete_combat_state('test_combat_1')
    assert result is False

@pytest.mark.asyncio
async def test_list_active_combats(state_manager):
    # Mock the database find operation
    mock_active_combats = [
        {'combat_id': 'combat1'},
        {'combat_id': 'combat2'},
        {'combat_id': 'combat3'}
    ]
    state_manager.combat_states.find.return_value.to_list.return_value = mock_active_combats
    
    # Test successful listing
    result = await state_manager.list_active_combats()
    assert result == ['combat1', 'combat2', 'combat3']
    
    # Test empty list
    state_manager.combat_states.find.return_value.to_list.return_value = []
    result = await state_manager.list_active_combats()
    assert result == []
    
    # Test with database error
    state_manager.combat_states.find.side_effect = Exception("Database error")
    result = await state_manager.list_active_combats()
    assert result == []

@pytest.mark.asyncio
async def test_update_combat_status(state_manager):
    # Mock the database update operation
    state_manager.combat_states.update_one.return_value = Mock(modified_count=1)
    
    # Test successful status update
    result = await state_manager.update_combat_status('test_combat_1', 'paused')
    assert result is True
    state_manager.combat_states.update_one.assert_called_once()
    
    # Test update non-existent combat
    state_manager.combat_states.update_one.return_value = Mock(modified_count=0)
    result = await state_manager.update_combat_status('non_existent_combat', 'completed')
    assert result is False
    
    # Test update with database error
    state_manager.combat_states.update_one.side_effect = Exception("Database error")
    result = await state_manager.update_combat_status('test_combat_1', 'completed')
    assert result is False 