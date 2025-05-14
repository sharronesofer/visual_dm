"""
Tests for the consequence escalation system.
"""

import pytest
from datetime import datetime, timedelta
from app.core.services.consequence_manager import ConsequenceManager
from app.core.models.infraction import Infraction
from app.core.models.consequence import Consequence
from app.core.enums import InfractionSeverity, ConsequenceType
from app.core.database import db

@pytest.fixture
def consequence_manager(db_session):
    return ConsequenceManager(session=db_session)

@pytest.fixture
def player_with_history(db_session):
    """Create a player with a history of infractions."""
    # Create past infractions with varying severities
    infractions = [
        Infraction(
            player_id=1,
            character_id=1,
            type="CHAT_SPAM",
            severity=InfractionSeverity.MINOR,
            details="Past minor infraction",
            created_at=datetime.utcnow() - timedelta(days=30)
        ),
        Infraction(
            player_id=1,
            character_id=1,
            type="COMBAT_GRIEFING",
            severity=InfractionSeverity.MODERATE,
            details="Past moderate infraction",
            created_at=datetime.utcnow() - timedelta(days=15)
        )
    ]
    
    for infraction in infractions:
        db_session.add(infraction)
    db_session.commit()
    return infractions

class TestConsequenceEscalation:
    def test_repeat_minor_infractions(self, consequence_manager, player_with_history, db_session):
        """Test that repeated minor infractions lead to escalated consequences."""
        # Create a new minor infraction
        new_infraction = Infraction(
            player_id=1,
            character_id=1,
            type="CHAT_SPAM",
            severity=InfractionSeverity.MINOR,
            details="Repeat minor infraction"
        )
        db_session.add(new_infraction)
        db_session.commit()
        
        # Apply consequences
        consequences = consequence_manager.apply_consequences(new_infraction)
        
        # Verify consequences are escalated
        assert any(c.type == ConsequenceType.FINE for c in consequences), "Should include a fine for repeat offense"
        assert any(c.severity == InfractionSeverity.MODERATE for c in consequences), "Should escalate to moderate severity"

    def test_escalation_to_major(self, consequence_manager, db_session):
        """Test escalation to major consequences after multiple moderate infractions."""
        # Create history of moderate infractions
        for i in range(3):
            infraction = Infraction(
                player_id=1,
                character_id=1,
                type="COMBAT_GRIEFING",
                severity=InfractionSeverity.MODERATE,
                details=f"Moderate infraction #{i+1}",
                created_at=datetime.utcnow() - timedelta(days=30-i)
            )
            db_session.add(infraction)
            consequences = consequence_manager.apply_consequences(infraction)
        db_session.commit()
        
        # Create one more moderate infraction
        new_infraction = Infraction(
            player_id=1,
            character_id=1,
            type="COMBAT_GRIEFING",
            severity=InfractionSeverity.MODERATE,
            details="Fourth moderate infraction"
        )
        db_session.add(new_infraction)
        db_session.commit()
        
        consequences = consequence_manager.apply_consequences(new_infraction)
        
        # Verify escalation to major consequences
        assert any(c.type == ConsequenceType.SUSPENSION for c in consequences), "Should include suspension"
        assert any(c.severity == InfractionSeverity.MAJOR for c in consequences), "Should escalate to major severity"

    def test_critical_consequence_permanence(self, consequence_manager, db_session):
        """Test that critical consequences (like bans) remain permanent."""
        # Create a critical infraction
        critical_infraction = Infraction(
            player_id=1,
            character_id=1,
            type="HACKING",
            severity=InfractionSeverity.CRITICAL,
            details="Critical violation"
        )
        db_session.add(critical_infraction)
        db_session.commit()
        
        consequences = consequence_manager.apply_consequences(critical_infraction)
        
        # Verify ban is permanent
        ban_consequence = next(c for c in consequences if c.type == ConsequenceType.BAN)
        assert ban_consequence is not None
        assert ban_consequence.expires_at is None, "Ban should be permanent"
        assert ban_consequence.active is True, "Ban should be active"

    def test_consequence_stacking(self, consequence_manager, db_session):
        """Test that multiple active consequences can stack appropriately."""
        # Create two different types of infractions close together
        infractions = [
            Infraction(
                player_id=1,
                character_id=1,
                type="COMBAT_GRIEFING",
                severity=InfractionSeverity.MODERATE,
                details="First infraction"
            ),
            Infraction(
                player_id=1,
                character_id=1,
                type="CHAT_SPAM",
                severity=InfractionSeverity.MINOR,
                details="Second infraction"
            )
        ]
        
        all_consequences = []
        for infraction in infractions:
            db_session.add(infraction)
            db_session.commit()
            consequences = consequence_manager.apply_consequences(infraction)
            all_consequences.extend(consequences)
        
        # Get all active consequences for the player
        active_consequences = consequence_manager.get_active_consequences(1)
        
        # Verify multiple consequences are active
        assert len(active_consequences) > len(infractions), "Should have multiple active consequences"
        consequence_types = {c.type for c in active_consequences}
        assert len(consequence_types) > 1, "Should have different types of consequences"

    def test_expired_consequence_renewal(self, consequence_manager, db_session):
        """Test that expired consequences can be renewed with new infractions."""
        # Create an initial infraction with time-limited consequence
        initial_infraction = Infraction(
            player_id=1,
            character_id=1,
            type="COMBAT_GRIEFING",
            severity=InfractionSeverity.MODERATE,
            details="Initial infraction",
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db_session.add(initial_infraction)
        db_session.commit()
        
        initial_consequences = consequence_manager.apply_consequences(initial_infraction)
        
        # Fast forward time by expiring consequences
        consequence_manager.expire_consequences()
        
        # Create a new similar infraction
        new_infraction = Infraction(
            player_id=1,
            character_id=1,
            type="COMBAT_GRIEFING",
            severity=InfractionSeverity.MODERATE,
            details="Repeat infraction"
        )
        db_session.add(new_infraction)
        db_session.commit()
        
        new_consequences = consequence_manager.apply_consequences(new_infraction)
        
        # Verify consequences are renewed and possibly escalated
        assert len(new_consequences) >= len(initial_consequences), "Should have at least as many consequences"
        assert all(c.active for c in new_consequences), "All new consequences should be active"
        assert any(c.severity > InfractionSeverity.MODERATE for c in new_consequences), "Should include escalated consequences"

    def test_concurrent_infraction_handling(self, consequence_manager, db_session):
        """Test handling of multiple infractions occurring close together."""
        # Create multiple infractions in quick succession
        infractions = []
        for i in range(3):
            infraction = Infraction(
                player_id=1,
                character_id=1,
                type="COMBAT_GRIEFING",
                severity=InfractionSeverity.MODERATE,
                details=f"Concurrent infraction #{i+1}",
                created_at=datetime.utcnow() + timedelta(seconds=i)  # Very close together
            )
            db_session.add(infraction)
            db_session.commit()
            infractions.append(infraction)
        
        # Apply consequences for all infractions
        all_consequences = []
        for infraction in infractions:
            consequences = consequence_manager.apply_consequences(infraction)
            all_consequences.extend(consequences)
        
        # Verify proper handling of concurrent infractions
        active_consequences = consequence_manager.get_active_consequences(1)
        assert len(active_consequences) > 0, "Should have active consequences"
        
        # Check for escalation due to rapid succession
        severity_counts = {}
        for c in active_consequences:
            severity_counts[c.severity] = severity_counts.get(c.severity, 0) + 1
        
        # Should have some escalated consequences due to rapid infractions
        assert any(sev > InfractionSeverity.MODERATE for sev in severity_counts.keys()), \
            "Should include escalated consequences for rapid infractions" 