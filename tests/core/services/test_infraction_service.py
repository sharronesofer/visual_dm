"""
Tests for the InfractionService.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from app.core.services.infraction_service import InfractionService
from app.core.models.infraction import Infraction
from app.core.enums import InfractionType, InfractionSeverity

@pytest.fixture
def infraction_service(session):
    """Create an InfractionService instance for testing."""
    return InfractionService(session=session)

@pytest.fixture
def sample_infraction_data():
    """Create sample infraction data for testing."""
    return {
        'player_id': 1,
        'character_id': 1,
        'type': InfractionType.ATTACK_FRIENDLY_NPC,
        'severity': InfractionSeverity.MAJOR,
        'location': 'Oakvale',
        'target_npc_id': 1,
        'details': 'Attacked town guard'
    }

def test_record_infraction(infraction_service, sample_infraction_data):
    """Test recording a new infraction."""
    infraction = infraction_service.record_infraction(**sample_infraction_data)
    
    assert infraction.id is not None
    assert infraction.player_id == sample_infraction_data['player_id']
    assert infraction.character_id == sample_infraction_data['character_id']
    assert infraction.type == sample_infraction_data['type']
    assert infraction.severity == sample_infraction_data['severity']
    assert infraction.location == sample_infraction_data['location']
    assert infraction.target_npc_id == sample_infraction_data['target_npc_id']
    assert infraction.details == sample_infraction_data['details']
    assert infraction.resolved is False

def test_record_infraction_minimal(infraction_service):
    """Test recording an infraction with only required fields."""
    infraction = infraction_service.record_infraction(
        player_id=1,
        character_id=1,
        type=InfractionType.ATTACK_FRIENDLY_NPC,
        severity=InfractionSeverity.MAJOR
    )
    
    assert infraction.id is not None
    assert infraction.location is None
    assert infraction.target_npc_id is None
    assert infraction.details is None

def test_record_infraction_with_consequence_manager(infraction_service, sample_infraction_data):
    """Test that consequences are applied when recording an infraction."""
    with patch('app.core.services.infraction_service.ConsequenceManager') as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance
        
        infraction = infraction_service.record_infraction(**sample_infraction_data)
        
        mock_manager.assert_called_once_with(infraction_service.session)
        mock_instance.apply_consequences.assert_called_once_with(infraction)

def test_record_infraction_rollback_on_error(infraction_service, sample_infraction_data):
    """Test that transaction is rolled back on error."""
    with patch('app.core.services.infraction_service.ConsequenceManager') as mock_manager:
        mock_instance = Mock()
        mock_instance.apply_consequences.side_effect = Exception('Test error')
        mock_manager.return_value = mock_instance
        
        with pytest.raises(Exception):
            infraction_service.record_infraction(**sample_infraction_data)
        
        # Verify no infraction was saved
        infractions = infraction_service.get_player_infractions(sample_infraction_data['player_id'])
        assert len(infractions) == 0

def test_get_player_infractions(infraction_service, sample_infraction_data):
    """Test retrieving infractions for a player."""
    # Create multiple infractions
    infraction1 = infraction_service.record_infraction(**sample_infraction_data)
    infraction2 = infraction_service.record_infraction(**sample_infraction_data)
    
    # Get all infractions
    infractions = infraction_service.get_player_infractions(sample_infraction_data['player_id'])
    assert len(infractions) == 2
    assert all(i.player_id == sample_infraction_data['player_id'] for i in infractions)
    
    # Test filtering by resolved status
    assert len(infraction_service.get_player_infractions(sample_infraction_data['player_id'], resolved=True)) == 0
    
    # Resolve one infraction
    infraction_service.resolve_infraction(infraction1.id)
    assert len(infraction_service.get_player_infractions(sample_infraction_data['player_id'], resolved=True)) == 1
    assert len(infraction_service.get_player_infractions(sample_infraction_data['player_id'], resolved=False)) == 1

def test_resolve_infraction(infraction_service, sample_infraction_data):
    """Test resolving an infraction."""
    infraction = infraction_service.record_infraction(**sample_infraction_data)
    
    # Test resolving
    assert infraction_service.resolve_infraction(infraction.id) is True
    resolved = infraction_service.session.query(Infraction).get(infraction.id)
    assert resolved.resolved is True
    
    # Test resolving non-existent infraction
    assert infraction_service.resolve_infraction(9999) is False

def test_calculate_severity(infraction_service):
    """Test severity calculation logic."""
    # Test ATTACK_FRIENDLY_NPC severity escalation
    assert infraction_service.calculate_severity(InfractionType.ATTACK_FRIENDLY_NPC, frequency=1) == InfractionSeverity.MINOR
    assert infraction_service.calculate_severity(InfractionType.ATTACK_FRIENDLY_NPC, frequency=2) == InfractionSeverity.MODERATE
    assert infraction_service.calculate_severity(InfractionType.ATTACK_FRIENDLY_NPC, frequency=3) == InfractionSeverity.MAJOR
    assert infraction_service.calculate_severity(InfractionType.ATTACK_FRIENDLY_NPC, frequency=4) == InfractionSeverity.MAJOR
    
    # Test THEFT severity escalation
    assert infraction_service.calculate_severity(InfractionType.THEFT, frequency=1) == InfractionSeverity.MINOR
    assert infraction_service.calculate_severity(InfractionType.THEFT, frequency=2) == InfractionSeverity.MODERATE
    assert infraction_service.calculate_severity(InfractionType.THEFT, frequency=3) == InfractionSeverity.MAJOR
    
    # Test PROPERTY_DAMAGE severity
    assert infraction_service.calculate_severity(InfractionType.PROPERTY_DAMAGE, frequency=1) == InfractionSeverity.MINOR
    assert infraction_service.calculate_severity(InfractionType.PROPERTY_DAMAGE, frequency=2) == InfractionSeverity.MODERATE
    
    # Test CHEATING severity (always critical)
    assert infraction_service.calculate_severity(InfractionType.CHEATING, frequency=1) == InfractionSeverity.CRITICAL
    
    # Test default case
    assert infraction_service.calculate_severity(InfractionType.OTHER, frequency=1) == InfractionSeverity.MINOR

def test_get_player_infractions_ordering(infraction_service, sample_infraction_data):
    """Test that infractions are ordered by timestamp descending."""
    # Create infractions with different timestamps
    data1 = dict(sample_infraction_data)
    data1['timestamp'] = datetime(2024, 1, 1, tzinfo=timezone.utc)
    data2 = dict(sample_infraction_data)
    data2['timestamp'] = datetime(2024, 1, 2, tzinfo=timezone.utc)
    
    infraction1 = infraction_service.record_infraction(**data1)
    infraction2 = infraction_service.record_infraction(**data2)
    
    infractions = infraction_service.get_player_infractions(sample_infraction_data['player_id'])
    assert len(infractions) == 2
    assert infractions[0].id == infraction2.id  # Most recent first
    assert infractions[1].id == infraction1.id 