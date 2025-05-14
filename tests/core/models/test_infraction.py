"""
Tests for the Infraction model.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app.core.models.infraction import Infraction
from app.core.enums import InfractionType, InfractionSeverity

@pytest.fixture
def sample_infraction(session):
    """Create a sample infraction for testing."""
    infraction = Infraction(
        player_id=1,
        character_id=1,
        type=InfractionType.ATTACK_FRIENDLY_NPC,
        severity=InfractionSeverity.MAJOR,
        timestamp=datetime.now(timezone.utc),
        location='Oakvale',
        target_npc_id=1,
        details='Attacked town guard',
        resolved=False
    )
    session.add(infraction)
    session.commit()
    return infraction

def test_infraction_creation(session, sample_infraction):
    """Test basic infraction creation with all fields."""
    assert sample_infraction.id is not None
    assert sample_infraction.player_id == 1
    assert sample_infraction.character_id == 1
    assert sample_infraction.type == InfractionType.ATTACK_FRIENDLY_NPC
    assert sample_infraction.severity == InfractionSeverity.MAJOR
    assert sample_infraction.location == 'Oakvale'
    assert sample_infraction.target_npc_id == 1
    assert sample_infraction.details == 'Attacked town guard'
    assert sample_infraction.resolved is False
    assert isinstance(sample_infraction.timestamp, datetime)

def test_infraction_required_fields(session):
    """Test that required fields must be provided."""
    # Missing player_id
    with pytest.raises(IntegrityError):
        infraction = Infraction(
            character_id=1,
            type=InfractionType.ATTACK_FRIENDLY_NPC,
            severity=InfractionSeverity.MAJOR
        )
        session.add(infraction)
        session.commit()
    session.rollback()

    # Missing character_id
    with pytest.raises(IntegrityError):
        infraction = Infraction(
            player_id=1,
            type=InfractionType.ATTACK_FRIENDLY_NPC,
            severity=InfractionSeverity.MAJOR
        )
        session.add(infraction)
        session.commit()
    session.rollback()

    # Missing type
    with pytest.raises(IntegrityError):
        infraction = Infraction(
            player_id=1,
            character_id=1,
            severity=InfractionSeverity.MAJOR
        )
        session.add(infraction)
        session.commit()
    session.rollback()

    # Missing severity
    with pytest.raises(IntegrityError):
        infraction = Infraction(
            player_id=1,
            character_id=1,
            type=InfractionType.ATTACK_FRIENDLY_NPC
        )
        session.add(infraction)
        session.commit()
    session.rollback()

def test_infraction_optional_fields(session):
    """Test that optional fields can be omitted."""
    infraction = Infraction(
        player_id=1,
        character_id=1,
        type=InfractionType.ATTACK_FRIENDLY_NPC,
        severity=InfractionSeverity.MAJOR
    )
    session.add(infraction)
    session.commit()

    assert infraction.id is not None
    assert infraction.location is None
    assert infraction.target_npc_id is None
    assert infraction.details is None
    assert infraction.resolved is False
    assert isinstance(infraction.timestamp, datetime)

def test_infraction_relationships(session, sample_infraction):
    """Test that relationships are properly configured."""
    # Note: This test assumes the existence of User, Character, and NPC models
    # We're just testing that the relationship attributes exist and are of the right type
    assert hasattr(sample_infraction, 'player')
    assert hasattr(sample_infraction, 'character')
    assert hasattr(sample_infraction, 'target_npc')

def test_infraction_to_dict(sample_infraction):
    """Test the to_dict method returns the correct format."""
    data = sample_infraction.to_dict()
    
    assert isinstance(data, dict)
    assert data['id'] == sample_infraction.id
    assert data['player_id'] == sample_infraction.player_id
    assert data['character_id'] == sample_infraction.character_id
    assert data['target_npc_id'] == sample_infraction.target_npc_id
    assert data['type'] == sample_infraction.type.value
    assert data['severity'] == sample_infraction.severity.value
    assert isinstance(data['timestamp'], str)
    assert data['location'] == sample_infraction.location
    assert data['details'] == sample_infraction.details
    assert data['resolved'] == sample_infraction.resolved
    assert isinstance(data['created_at'], str)
    assert isinstance(data['updated_at'], str)

def test_infraction_repr(sample_infraction):
    """Test the string representation of the infraction."""
    expected = f'<Infraction {sample_infraction.id} type={sample_infraction.type} severity={sample_infraction.severity} player={sample_infraction.player_id} character={sample_infraction.character_id}>'
    assert str(sample_infraction) == expected

def test_infraction_enum_values(session):
    """Test that infraction type and severity must be valid enum values."""
    # Invalid type
    with pytest.raises(ValueError):
        Infraction(
            player_id=1,
            character_id=1,
            type='invalid_type',
            severity=InfractionSeverity.MAJOR
        )

    # Invalid severity
    with pytest.raises(ValueError):
        Infraction(
            player_id=1,
            character_id=1,
            type=InfractionType.ATTACK_FRIENDLY_NPC,
            severity='invalid_severity'
        )

def test_infraction_timestamp_default(session):
    """Test that timestamp is automatically set to current time if not provided."""
    before = datetime.now(timezone.utc)
    infraction = Infraction(
        player_id=1,
        character_id=1,
        type=InfractionType.ATTACK_FRIENDLY_NPC,
        severity=InfractionSeverity.MAJOR
    )
    session.add(infraction)
    session.commit()
    after = datetime.now(timezone.utc)

    assert before <= infraction.timestamp <= after

def test_infraction_resolved_default(session):
    """Test that resolved defaults to False."""
    infraction = Infraction(
        player_id=1,
        character_id=1,
        type=InfractionType.ATTACK_FRIENDLY_NPC,
        severity=InfractionSeverity.MAJOR
    )
    session.add(infraction)
    session.commit()

    assert infraction.resolved is False

def test_infraction_cascade_delete(session, sample_infraction):
    """Test that deleting an infraction works correctly."""
    infraction_id = sample_infraction.id
    session.delete(sample_infraction)
    session.commit()

    assert session.query(Infraction).get(infraction_id) is None 