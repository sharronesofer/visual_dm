import pytest
from unittest.mock import Mock, patch
from app.core.combat import CombatSystem
from app.combat.damage_engine import DamageType, AttackType, DamageResult

@pytest.fixture
def mock_app():
    app = Mock()
    app.db.collection.return_value = Mock()
    return app

@pytest.fixture
def combat_system(mock_app):
    return CombatSystem(mock_app)

@pytest.fixture
def mock_characters():
    attacker = {
        'id': 'attacker_id',
        'name': 'Test Attacker',
        'health': 100,
        'strength': 15,
        'dexterity': 14,
        'equipped_weapon': {
            'name': 'Longsword',
            'damage': 8,
            'damage_type': 'physical',
            'properties': ['versatile']
        },
        'status_effects': []
    }
    
    defender = {
        'id': 'defender_id',
        'name': 'Test Defender',
        'health': 100,
        'constitution': 12,
        'armor_class': 15,
        'resistances': ['physical'],
        'status_effects': []
    }
    
    return attacker, defender

def test_combat_initialization(combat_system):
    """Test that combat system initializes correctly."""
    assert combat_system.damage_engine is not None
    assert combat_system.combat_collection is not None

def test_process_attack(combat_system, mock_characters):
    """Test basic attack processing."""
    attacker, defender = mock_characters
    
    # Mock the character system
    combat_system.app.character_system.get_character.side_effect = lambda id: (
        attacker if id == 'attacker_id' else defender
    )
    
    # Mock combat retrieval
    mock_combat = {
        'id': 'test_combat',
        'participants': [attacker['id'], defender['id']],
        'actions': [],
        'terrain': {'high_ground': False},
        'environment': {'rain': False}
    }
    combat_system.get_combat = Mock(return_value=mock_combat)
    
    # Process attack
    result = combat_system.process_attack(
        combat_id='test_combat',
        attacker_id=attacker['id'],
        defender_id=defender['id'],
        attack_type='melee'
    )
    
    # Verify result structure
    assert result['success'] is True
    assert 'damage_result' in result
    assert 'defender_health' in result
    
    # Verify damage result contains all expected fields
    damage_result = result['damage_result']
    assert 'damage' in damage_result
    assert 'raw_damage' in damage_result
    assert 'critical' in damage_result
    assert 'damage_type' in damage_result
    assert 'absorbed' in damage_result
    assert 'reduced' in damage_result
    assert 'effects' in damage_result
    assert 'hit_location' in damage_result
    
    # Verify combat log was updated
    combat_system.combat_collection.document().update.assert_called_once()

def test_battlefield_conditions(combat_system):
    """Test battlefield conditions extraction."""
    combat = {
        'terrain': {
            'high_ground': True,
            'difficult_terrain': False
        },
        'environment': {
            'rain': True,
            'water': False
        }
    }
    
    conditions = combat_system._get_battlefield_conditions(combat)
    assert conditions['high_ground'] is True
    assert conditions['difficult_terrain'] is False
    assert conditions['rain'] is True
    assert conditions['water'] is False

def test_status_effects(combat_system):
    """Test status effects collection."""
    attacker = {
        'status_effects': [
            {'type': 'rage', 'duration': 3}
        ]
    }
    defender = {
        'status_effects': [
            {'type': 'poisoned', 'duration': 2}
        ]
    }
    
    effects = combat_system._get_status_effects(attacker, defender)
    assert len(effects) == 2
    assert any(effect['type'] == 'rage' for effect in effects)
    assert any(effect['type'] == 'poisoned' for effect in effects)

def test_apply_combat_effect(combat_system):
    """Test applying combat effects to a target."""
    target = {}
    
    # Test bleeding effect
    combat_system._apply_combat_effect(target, 'bleeding')
    assert 'status_effects' in target
    assert len(target['status_effects']) == 1
    assert target['status_effects'][0]['type'] == 'bleeding'
    assert target['status_effects'][0]['damage'] == 2
    assert target['status_effects'][0]['duration'] == 3
    
    # Test stunned effect
    combat_system._apply_combat_effect(target, 'stunned')
    assert len(target['status_effects']) == 2
    assert target['status_effects'][1]['type'] == 'stunned'
    assert target['status_effects'][1]['duration'] == 1

def test_critical_hit(combat_system, mock_characters):
    """Test critical hit processing."""
    attacker, defender = mock_characters
    
    # Mock character system
    combat_system.app.character_system.get_character.side_effect = lambda id: (
        attacker if id == 'attacker_id' else defender
    )
    
    # Mock combat
    mock_combat = {
        'id': 'test_combat',
        'participants': [attacker['id'], defender['id']],
        'actions': [],
        'terrain': {},
        'environment': {}
    }
    combat_system.get_combat = Mock(return_value=mock_combat)
    
    # Force critical hit
    with patch('random.randint', return_value=20):
        result = combat_system.process_attack(
            combat_id='test_combat',
            attacker_id=attacker['id'],
            defender_id=defender['id'],
            attack_type='melee'
        )
    
    assert result['damage_result']['critical'] is True
    assert result['damage_result']['raw_damage'] > 0  # Should have some damage
    
def test_combat_end(combat_system, mock_characters):
    """Test combat ending when defender health reaches 0."""
    attacker, defender = mock_characters
    defender['health'] = 1  # Set defender to low health
    
    # Mock character system
    combat_system.app.character_system.get_character.side_effect = lambda id: (
        attacker if id == 'attacker_id' else defender
    )
    
    # Mock combat
    mock_combat = {
        'id': 'test_combat',
        'participants': [attacker['id'], defender['id']],
        'actions': [],
        'terrain': {},
        'environment': {}
    }
    combat_system.get_combat = Mock(return_value=mock_combat)
    
    # Mock the damage engine to ensure fatal damage
    mock_damage_result = DamageResult(
        raw_damage=10,
        final_damage=10,
        damage_type=DamageType.PHYSICAL,
        critical=False,
        absorbed_damage=0,
        damage_reduction=0,
        effects_applied=[],
        hit_location='torso'
    )
    combat_system.damage_engine.calculate_damage = Mock(return_value=mock_damage_result)
    
    # Process attack
    result = combat_system.process_attack(
        combat_id='test_combat',
        attacker_id=attacker['id'],
        defender_id=defender['id'],
        attack_type='melee'
    )
    
    assert result['success'] is True
    assert result['defender_health'] == 0  # Health should be reduced to 0
    combat_system._end_combat.assert_called_once_with('test_combat', attacker['id']) 