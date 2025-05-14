"""
Tests for the ConsequenceManager service.
"""

import pytest
from datetime import datetime, timedelta
from app.core.services.consequence_manager import ConsequenceManager, CONSEQUENCE_CONFIG
from app.core.models.infraction import Infraction
from app.core.models.consequence import Consequence
from app.core.enums import InfractionSeverity, ConsequenceType
from app.core.database import db

@pytest.fixture
def consequence_manager(db_session):
    return ConsequenceManager(session=db_session)

@pytest.fixture
def sample_infraction(db_session):
    infraction = Infraction(
        player_id=1,
        character_id=1,
        type="COMBAT_GRIEFING",
        severity=InfractionSeverity.MODERATE,
        details="Test infraction"
    )
    db_session.add(infraction)
    db_session.commit()
    return infraction

class TestConsequenceManager:
    def test_determine_consequences_minor(self, consequence_manager):
        """Test consequence determination for minor infractions."""
        infraction = Infraction(
            player_id=1,
            character_id=1,
            type="CHAT_SPAM",
            severity=InfractionSeverity.MINOR,
            details="Minor test infraction"
        )
        
        consequences = consequence_manager.determine_consequences(infraction)
        assert len(consequences) == 2
        assert consequences[0].type == ConsequenceType.WARNING
        assert consequences[1].type == ConsequenceType.FINE
        assert all(c.expires_at is None for c in consequences)  # No duration for minor consequences

    def test_determine_consequences_moderate(self, consequence_manager):
        """Test consequence determination for moderate infractions."""
        infraction = Infraction(
            player_id=1,
            character_id=1,
            type="COMBAT_GRIEFING",
            severity=InfractionSeverity.MODERATE,
            details="Moderate test infraction"
        )
        
        consequences = consequence_manager.determine_consequences(infraction)
        assert len(consequences) == 3
        assert consequences[0].type == ConsequenceType.FINE
        assert consequences[1].type == ConsequenceType.ITEM_CONFISCATION
        assert consequences[2].type == ConsequenceType.NPC_HOSTILITY
        assert consequences[2].expires_at is not None  # NPC hostility has duration

    def test_determine_consequences_major(self, consequence_manager):
        """Test consequence determination for major infractions."""
        infraction = Infraction(
            player_id=1,
            character_id=1,
            type="EXPLOIT_ABUSE",
            severity=InfractionSeverity.MAJOR,
            details="Major test infraction"
        )
        
        consequences = consequence_manager.determine_consequences(infraction)
        assert len(consequences) == 3
        assert consequences[0].type == ConsequenceType.NPC_HOSTILITY
        assert consequences[1].type == ConsequenceType.SUSPENSION
        assert consequences[2].type == ConsequenceType.BOUNTY
        assert consequences[0].expires_at is not None  # NPC hostility has duration
        assert consequences[1].expires_at is not None  # Suspension has duration

    def test_determine_consequences_critical(self, consequence_manager):
        """Test consequence determination for critical infractions."""
        infraction = Infraction(
            player_id=1,
            character_id=1,
            type="HACKING",
            severity=InfractionSeverity.CRITICAL,
            details="Critical test infraction"
        )
        
        consequences = consequence_manager.determine_consequences(infraction)
        assert len(consequences) == 1
        assert consequences[0].type == ConsequenceType.BAN
        assert consequences[0].expires_at is None  # Permanent ban

    def test_apply_consequences(self, consequence_manager, sample_infraction, db_session):
        """Test applying consequences to the database."""
        consequences = consequence_manager.apply_consequences(sample_infraction)
        
        # Verify consequences were saved to database
        db_consequences = db_session.query(Consequence).filter_by(
            infraction_id=sample_infraction.id
        ).all()
        
        assert len(db_consequences) == len(consequences)
        for c in db_consequences:
            assert c.active is True
            assert c.player_id == sample_infraction.player_id
            assert c.character_id == sample_infraction.character_id

    def test_expire_consequences(self, consequence_manager, db_session):
        """Test expiring consequences that have passed their expiration time."""
        # Create some consequences with different expiration times
        past = datetime.utcnow() - timedelta(hours=1)
        future = datetime.utcnow() + timedelta(hours=1)
        
        consequences = [
            Consequence(
                player_id=1,
                character_id=1,
                type=ConsequenceType.NPC_HOSTILITY,
                severity=InfractionSeverity.MODERATE,
                active=True,
                expires_at=past
            ),
            Consequence(
                player_id=1,
                character_id=1,
                type=ConsequenceType.SUSPENSION,
                severity=InfractionSeverity.MAJOR,
                active=True,
                expires_at=future
            ),
            Consequence(
                player_id=1,
                character_id=1,
                type=ConsequenceType.BAN,
                severity=InfractionSeverity.CRITICAL,
                active=True,
                expires_at=None  # Permanent
            )
        ]
        
        for c in consequences:
            db_session.add(c)
        db_session.commit()

        # Run expiration
        expired = consequence_manager.expire_consequences()
        
        # Verify only past consequences were expired
        assert len(expired) == 1
        assert expired[0].type == ConsequenceType.NPC_HOSTILITY
        assert not expired[0].active
        
        # Verify future and permanent consequences are still active
        active = db_session.query(Consequence).filter_by(active=True).all()
        assert len(active) == 2
        assert any(c.type == ConsequenceType.SUSPENSION for c in active)
        assert any(c.type == ConsequenceType.BAN for c in active)

    def test_get_active_consequences(self, consequence_manager, db_session):
        """Test retrieving active consequences for a player."""
        # Create mix of active and inactive consequences
        consequences = [
            Consequence(
                player_id=1,
                character_id=1,
                type=ConsequenceType.WARNING,
                severity=InfractionSeverity.MINOR,
                active=True
            ),
            Consequence(
                player_id=1,
                character_id=1,
                type=ConsequenceType.FINE,
                severity=InfractionSeverity.MODERATE,
                active=False
            ),
            Consequence(
                player_id=2,  # Different player
                character_id=2,
                type=ConsequenceType.WARNING,
                severity=InfractionSeverity.MINOR,
                active=True
            )
        ]
        
        for c in consequences:
            db_session.add(c)
        db_session.commit()

        # Get active consequences for player 1
        active = consequence_manager.get_active_consequences(1)
        
        assert len(active) == 1
        assert active[0].type == ConsequenceType.WARNING
        assert active[0].player_id == 1

    def test_consequence_config_coverage(self):
        """Test that consequence configuration covers all severity levels."""
        for severity in InfractionSeverity:
            assert severity in CONSEQUENCE_CONFIG, f"Missing config for severity {severity}"
            consequences = CONSEQUENCE_CONFIG[severity]
            assert len(consequences) > 0, f"No consequences defined for severity {severity}"
            
            for consequence in consequences:
                assert "type" in consequence, "Consequence missing type"
                assert "duration" in consequence, "Consequence missing duration"
                assert isinstance(consequence["duration"], (int, float)), "Duration must be numeric" 