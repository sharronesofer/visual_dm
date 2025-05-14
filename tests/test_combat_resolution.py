import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from app.combat.resolution import (
    CombatResolutionManager, CombatEndCondition, CombatResolutionResult
)
from app.combat.loot_generator import (
    LootGenerator,
    LootResult,
    Currency,
    ItemRarity,
    LootTableEntry
)

@pytest.fixture
def mock_app():
    """Create a mock application instance."""
    app = MagicMock()
    app.db = MagicMock()
    app.db.collection = MagicMock(return_value=MagicMock())
    app.combat_system = MagicMock()
    app.character_system = MagicMock()
    app.npc_system = MagicMock()
    app.logger = MagicMock()
    app.config = {'max_combat_rounds': 50}
    return app

@pytest.fixture
def resolution_manager(mock_app):
    """Create a CombatResolutionManager instance with a mock app."""
    return CombatResolutionManager(mock_app)

@pytest.fixture
def sample_combat_state():
    return {
        'id': 'test_combat_1',
        'participants': ['player1', 'player2', 'enemy1', 'enemy2'],
        'current_round': 5,
        'objectives': [
            {'type': 'defeat_target', 'target_id': 'enemy1', 'completed': False},
            {'type': 'protect_npc', 'npc_id': 'npc1', 'completed': True}
        ]
    }

@pytest.fixture
def sample_participants():
    return [
        {
            'id': 'player1',
            'type': 'player',
            'status': 'active',
            'health': 50,
            'max_health': 100,
            'position': {'x': 0, 'y': 0}
        },
        {
            'id': 'player2',
            'type': 'player',
            'status': 'defeated',
            'health': 0,
            'max_health': 80,
            'position': {'x': 1, 'y': 1}
        },
        {
            'id': 'enemy1',
            'type': 'enemy',
            'status': 'active',
            'health': 30,
            'max_health': 60,
            'position': {'x': 5, 'y': 5}
        },
        {
            'id': 'enemy2',
            'type': 'enemy',
            'status': 'defeated',
            'health': 0,
            'max_health': 40,
            'position': {'x': 6, 'y': 6}
        }
    ]

@pytest.fixture
def mock_combat_state():
    """Create a mock combat state."""
    return {
        'id': 'test_combat',
        'current_round': 5,
        'participants': ['player1', 'player2', 'enemy1', 'enemy2'],
        'status': 'active'
    }

@pytest.fixture
def mock_participants():
    """Create mock participant data."""
    return [
        {'id': 'player1', 'type': 'player', 'status': 'active', 'health': 50, 'max_health': 100},
        {'id': 'player2', 'type': 'player', 'status': 'active', 'health': 75, 'max_health': 100},
        {'id': 'enemy1', 'type': 'enemy', 'status': 'defeated', 'health': 0, 'max_health': 50},
        {'id': 'enemy2', 'type': 'enemy', 'status': 'defeated', 'health': 0, 'max_health': 50}
    ]

@pytest.fixture
def mock_loot_table():
    """Create a mock loot table."""
    return [
        LootTableEntry(
            item_id="test_weapon",
            rarity=ItemRarity.COMMON,
            drop_chance=1.0,
            level_requirement=1,
            quantity_range=(1, 1)
        ),
        LootTableEntry(
            item_id="test_armor",
            rarity=ItemRarity.UNCOMMON,
            drop_chance=0.5,
            level_requirement=1,
            quantity_range=(1, 1)
        )
    ]

class TestCombatResolutionManager:
    async def test_check_end_conditions_victory(self, resolution_manager, mock_app, sample_participants):
        """Test victory condition when all enemies are defeated."""
        # Modify sample participants for victory condition
        participants = sample_participants.copy()
        for p in participants:
            if p['type'] == 'enemy':
                p['status'] = 'defeated'
                
        mock_app.combat_system.get_combat.return_value = {'participants': ['player1', 'enemy1']}
        resolution_manager._get_participant_statuses = Mock(return_value=participants)
        
        result = await resolution_manager.check_end_conditions('test_combat_1')
        assert result == CombatEndCondition.VICTORY

    async def test_check_end_conditions_defeat(self, resolution_manager, mock_app, sample_participants):
        """Test defeat condition when all players are defeated."""
        # Modify sample participants for defeat condition
        participants = sample_participants.copy()
        for p in participants:
            if p['type'] == 'player':
                p['status'] = 'defeated'
                
        mock_app.combat_system.get_combat.return_value = {'participants': ['player1', 'enemy1']}
        resolution_manager._get_participant_statuses = Mock(return_value=participants)
        
        result = await resolution_manager.check_end_conditions('test_combat_1')
        assert result == CombatEndCondition.DEFEAT

    async def test_check_retreat_conditions(self, resolution_manager, mock_app, sample_participants):
        """Test retreat conditions for players."""
        mock_app.combat_system.get_combat.return_value = {'participants': ['player1', 'enemy1']}
        mock_app.combat_system.get_battlefield.return_value = {
            'exit_points': [{'x': 0, 'y': 1}],
            'exit_range': 2
        }
        
        resolution_manager._is_path_blocked = Mock(return_value=False)
        result = await resolution_manager._check_retreat_conditions('test_combat_1', sample_participants)
        assert result == True

    async def test_check_escape_conditions(self, resolution_manager, mock_app, sample_participants):
        """Test escape conditions for enemies."""
        mock_app.combat_system.get_combat.return_value = {'participants': ['player1', 'enemy1']}
        mock_app.combat_system.get_battlefield.return_value = {
            'exit_points': [{'x': 5, 'y': 6}],
            'exit_range': 2
        }
        
        # Modify sample participants for escape condition (few enemies remaining)
        participants = sample_participants.copy()
        for p in participants:
            if p['type'] == 'enemy' and p['id'] != 'enemy1':
                p['status'] = 'defeated'
                
        resolution_manager._is_path_blocked = Mock(return_value=False)
        result = await resolution_manager._check_escape_conditions('test_combat_1', participants)
        assert result == True

    async def test_resolve_combat(self, resolution_manager, mock_app, sample_participants):
        """Test complete combat resolution process."""
        mock_app.combat_system.get_combat.return_value = {'participants': ['player1', 'enemy1']}
        resolution_manager._get_participant_statuses = Mock(return_value=sample_participants)
        resolution_manager._determine_winner = Mock(return_value='players')
        resolution_manager._calculate_experience = Mock(return_value={'player1': 100})
        resolution_manager._get_special_conditions = Mock(return_value={})
        
        result = await resolution_manager.resolve_combat('test_combat_1', CombatEndCondition.VICTORY)
        
        assert isinstance(result, CombatResolutionResult)
        assert result.end_condition == CombatEndCondition.VICTORY
        assert result.winner == 'players'
        assert len(result.survivors) > 0
        assert len(result.casualties) > 0
        assert 'player1' in result.experience_awarded

    async def test_calculate_experience(self, resolution_manager, mock_app, sample_participants):
        """Test experience calculation for different end conditions."""
        mock_app.combat_system.get_combat.return_value = {'participants': ['player1', 'enemy1']}
        resolution_manager._get_enemy_xp_value = Mock(return_value=100)
        resolution_manager._apply_xp_modifiers = Mock(return_value=100)
        
        # Test XP for victory
        xp_victory = await resolution_manager._calculate_experience(
            'test_combat_1', sample_participants, CombatEndCondition.VICTORY
        )
        assert xp_victory['player1'] == 100  # Full XP for victory
        
        # Test XP for retreat
        xp_retreat = await resolution_manager._calculate_experience(
            'test_combat_1', sample_participants, CombatEndCondition.RETREAT
        )
        assert xp_retreat['player1'] == 50  # Half XP for retreat

    async def test_cleanup_combat(self, resolution_manager, mock_app):
        """Test combat cleanup process."""
        mock_app.combat_system.get_combat.return_value = {
            'participants': ['player1', 'enemy1']
        }
        
        await resolution_manager._cleanup_combat('test_combat_1')
        
        # Verify cleanup calls
        mock_app.effect_system.remove_combat_effects.assert_called()
        mock_app.character_system.reset_combat_flags.assert_called()
        mock_app.combat_system.clear_battlefield_effects.assert_called_with('test_combat_1')
        mock_app.combat_system.archive_combat_log.assert_called_with('test_combat_1')

    def test_calculate_distance(self, resolution_manager):
        """Test distance calculation between positions."""
        pos1 = {'x': 0, 'y': 0}
        pos2 = {'x': 3, 'y': 4}
        distance = resolution_manager._calculate_distance(pos1, pos2)
        assert distance == 5.0  # 3-4-5 triangle 

@pytest.mark.asyncio
async def test_generate_combat_loot(resolution_manager, mock_app, mock_participants):
    """Test loot generation for defeated enemies."""
    # Mock enemy data
    mock_app.npc_system.get_npc = AsyncMock(return_value={
        'type': 'goblin',
        'level': 5,
        'is_boss': False
    })
    
    # Mock loot table data
    mock_loot_table_doc = MagicMock()
    mock_loot_table_doc.exists = True
    mock_loot_table_doc.to_dict = MagicMock(return_value={
        'entries': [
            {
                'item_id': 'test_item',
                'rarity': 1,  # COMMON
                'drop_chance': 1.0,
                'level_requirement': 1,
                'min_quantity': 1,
                'max_quantity': 1
            }
        ]
    })
    mock_app.db.collection().document().get = AsyncMock(return_value=mock_loot_table_doc)
    
    # Mock combat and character data for party level calculation
    mock_app.combat_system.get_combat = AsyncMock(return_value={
        'participants': ['player1', 'player2']
    })
    mock_app.character_system.get_character = AsyncMock(return_value={
        'level': 5
    })
    
    # Generate loot
    loot_results = await resolution_manager._generate_combat_loot('test_combat', mock_participants)
    
    # Verify loot was generated for both defeated enemies
    assert len(loot_results) == 2
    assert 'enemy1' in loot_results
    assert 'enemy2' in loot_results
    
    # Check loot structure
    for loot in loot_results.values():
        assert isinstance(loot, LootResult)
        assert isinstance(loot.currency, Currency)
        assert isinstance(loot.items, list)
        assert isinstance(loot.special_items, list)

@pytest.mark.asyncio
async def test_calculate_party_level(resolution_manager, mock_app):
    """Test party level calculation."""
    # Mock combat data
    mock_app.combat_system.get_combat = AsyncMock(return_value={
        'participants': ['player1', 'player2', 'enemy1']
    })
    
    # Mock character data
    mock_app.character_system.get_character = AsyncMock(side_effect=[
        {'level': 5},  # player1
        {'level': 7},  # player2
        None          # enemy1 (not a player)
    ])
    
    # Calculate party level
    party_level = await resolution_manager._calculate_party_level('test_combat')
    
    # Average of levels 5 and 7 = 6
    assert party_level == 6

@pytest.mark.asyncio
async def test_get_enemy_loot_table(resolution_manager, mock_app, mock_loot_table):
    """Test fetching enemy loot table from database."""
    # Mock successful loot table fetch
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict = MagicMock(return_value={
        'entries': [
            {
                'item_id': 'test_weapon',
                'rarity': 1,
                'drop_chance': 1.0,
                'level_requirement': 1,
                'min_quantity': 1,
                'max_quantity': 1
            }
        ]
    })
    mock_app.db.collection().document().get = AsyncMock(return_value=mock_doc)
    
    # Fetch loot table
    loot_table = await resolution_manager._get_enemy_loot_table('test_enemy')
    
    # Verify loot table structure
    assert len(loot_table) == 1
    assert isinstance(loot_table[0], LootTableEntry)
    assert loot_table[0].item_id == 'test_weapon'
    assert loot_table[0].rarity == ItemRarity.COMMON
    
    # Test handling of non-existent loot table
    mock_doc.exists = False
    empty_table = await resolution_manager._get_enemy_loot_table('unknown_enemy')
    assert empty_table == []

@pytest.mark.asyncio
async def test_resolve_combat_with_loot(resolution_manager, mock_app, mock_combat_state, mock_participants):
    """Test complete combat resolution including loot generation."""
    # Mock required methods
    resolution_manager.state_manager.get_state = AsyncMock(return_value=mock_combat_state)
    resolution_manager._get_participant_statuses = AsyncMock(return_value=mock_participants)
    resolution_manager._determine_winner = AsyncMock(return_value='players')
    resolution_manager._calculate_experience = AsyncMock(return_value={'player1': 100, 'player2': 100})
    resolution_manager._get_special_conditions = AsyncMock(return_value={})
    resolution_manager._cleanup_combat = AsyncMock()
    
    # Mock loot generation
    mock_loot = LootResult(
        items=[('test_item', 1)],
        currency=Currency(gold=1),
        special_items=[]
    )
    resolution_manager._generate_combat_loot = AsyncMock(return_value={
        'enemy1': mock_loot,
        'enemy2': mock_loot
    })
    
    # Resolve combat
    result = await resolution_manager.resolve_combat('test_combat', CombatEndCondition.VICTORY)
    
    # Verify result structure
    assert isinstance(result, CombatResolutionResult)
    assert result.combat_id == 'test_combat'
    assert result.end_condition == CombatEndCondition.VICTORY
    assert result.winner == 'players'
    assert len(result.loot_generated) == 2
    assert 'enemy1' in result.loot_generated
    assert 'enemy2' in result.loot_generated
    
    # Verify loot was saved to database
    mock_app.db.collection().document().set.assert_called_once()
    call_args = mock_app.db.collection().document().set.call_args[0][0]
    assert 'loot_generated' in call_args
    assert len(call_args['loot_generated']) == 2 