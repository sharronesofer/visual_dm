"""Tests for the moderation dashboard functionality."""

import pytest
from datetime import datetime, timedelta
from app.core.models.infraction import Infraction
from app.core.models.consequence import Consequence
from app.core.models.appeal import Appeal
from app.core.models.user import User, Role
from app.core.services.moderation_service import ModerationService
from app.core.enums import InfractionSeverity, ConsequenceType, AppealStatus
from app.core.database import db

@pytest.fixture
def moderation_service(db_session):
    return ModerationService(session=db_session)

@pytest.fixture
def admin_user(db_session):
    """Create an admin user with full permissions."""
    admin_role = Role(name='admin')
    db_session.add(admin_role)
    admin = User(
        username='admin_test',
        email='admin@test.com',
        role=admin_role
    )
    db_session.add(admin)
    db_session.commit()
    return admin

@pytest.fixture
def moderator_user(db_session):
    """Create a moderator user with limited permissions."""
    mod_role = Role(name='moderator')
    db_session.add(mod_role)
    moderator = User(
        username='mod_test',
        email='mod@test.com',
        role=mod_role
    )
    db_session.add(moderator)
    db_session.commit()
    return moderator

@pytest.fixture
def sample_infraction(db_session):
    """Create a sample infraction for testing."""
    infraction = Infraction(
        player_id=1,
        character_id=1,
        type="COMBAT_GRIEFING",
        severity=InfractionSeverity.MODERATE,
        timestamp=datetime.utcnow(),
        details="Test infraction"
    )
    db_session.add(infraction)
    db_session.commit()
    return infraction

@pytest.fixture
def sample_appeal(db_session, sample_infraction):
    """Create a sample appeal for testing."""
    appeal = Appeal(
        infraction_id=sample_infraction.id,
        player_id=1,
        status=AppealStatus.PENDING,
        reason="Test appeal reason",
        submitted_at=datetime.utcnow()
    )
    db_session.add(appeal)
    db_session.commit()
    return appeal

class TestModerationDashboard:
    def test_admin_permissions(self, moderation_service, admin_user):
        """Test that admin users have full access to moderation features."""
        assert moderation_service.can_view_infractions(admin_user)
        assert moderation_service.can_modify_consequences(admin_user)
        assert moderation_service.can_process_appeals(admin_user)
        assert moderation_service.can_override_status(admin_user)

    def test_moderator_permissions(self, moderation_service, moderator_user):
        """Test that moderator users have appropriate limited permissions."""
        assert moderation_service.can_view_infractions(moderator_user)
        assert moderation_service.can_process_appeals(moderator_user)
        assert not moderation_service.can_override_status(moderator_user)

    def test_infraction_review(self, moderation_service, sample_infraction, admin_user):
        """Test infraction review functionality."""
        # Test fetching infraction details
        infraction = moderation_service.get_infraction(sample_infraction.id)
        assert infraction.type == "COMBAT_GRIEFING"
        assert infraction.severity == InfractionSeverity.MODERATE

        # Test updating infraction details
        updated = moderation_service.update_infraction(
            infraction_id=sample_infraction.id,
            admin_id=admin_user.id,
            updates={
                "severity": InfractionSeverity.MAJOR,
                "details": "Updated details"
            }
        )
        assert updated.severity == InfractionSeverity.MAJOR
        assert updated.details == "Updated details"

    def test_manual_status_adjustment(self, moderation_service, sample_infraction, admin_user):
        """Test manual adjustment of player status and consequences."""
        # Test adding a manual consequence
        consequence = moderation_service.add_consequence(
            player_id=sample_infraction.player_id,
            admin_id=admin_user.id,
            consequence_type=ConsequenceType.SUSPENSION,
            duration_hours=24,
            reason="Manual suspension"
        )
        assert consequence.type == ConsequenceType.SUSPENSION
        assert consequence.active is True

        # Test overriding consequence status
        updated = moderation_service.override_consequence(
            consequence_id=consequence.id,
            admin_id=admin_user.id,
            active=False,
            reason="Early termination"
        )
        assert updated.active is False

    def test_appeal_processing(self, moderation_service, sample_appeal, moderator_user):
        """Test the appeal review and processing system."""
        # Test fetching appeal details
        appeal = moderation_service.get_appeal(sample_appeal.id)
        assert appeal.status == AppealStatus.PENDING

        # Test processing an appeal
        processed = moderation_service.process_appeal(
            appeal_id=sample_appeal.id,
            moderator_id=moderator_user.id,
            decision=AppealStatus.APPROVED,
            response="Appeal approved based on evidence"
        )
        assert processed.status == AppealStatus.APPROVED
        assert processed.processed_by_id == moderator_user.id

    def test_bulk_operations(self, moderation_service, db_session, admin_user):
        """Test bulk operations on infractions and consequences."""
        # Create multiple test infractions
        infractions = []
        for i in range(3):
            infraction = Infraction(
                player_id=1,
                character_id=1,
                type="COMBAT_GRIEFING",
                severity=InfractionSeverity.MODERATE,
                timestamp=datetime.utcnow(),
                details=f"Test infraction {i}"
            )
            db_session.add(infraction)
            infractions.append(infraction)
        db_session.commit()

        # Test bulk status update
        updated = moderation_service.bulk_update_infractions(
            infraction_ids=[i.id for i in infractions],
            admin_id=admin_user.id,
            updates={"resolved": True}
        )
        assert all(i.resolved for i in updated)

    def test_notification_system(self, moderation_service, sample_appeal, moderator_user):
        """Test that notifications are properly sent for moderation actions."""
        # Process appeal and check notification
        notification = moderation_service.process_appeal_with_notification(
            appeal_id=sample_appeal.id,
            moderator_id=moderator_user.id,
            decision=AppealStatus.APPROVED,
            response="Appeal approved",
            notify_player=True
        )
        assert notification.player_id == sample_appeal.player_id
        assert notification.type == "APPEAL_DECISION"
        assert notification.read is False

    def test_audit_logging(self, moderation_service, sample_infraction, admin_user):
        """Test that all moderation actions are properly logged."""
        # Perform a moderation action
        action = moderation_service.update_infraction(
            infraction_id=sample_infraction.id,
            admin_id=admin_user.id,
            updates={"severity": InfractionSeverity.MAJOR}
        )

        # Verify audit log entry
        log_entry = moderation_service.get_audit_log_entry(action.id)
        assert log_entry.admin_id == admin_user.id
        assert log_entry.action_type == "UPDATE_INFRACTION"
        assert log_entry.target_id == str(sample_infraction.id) 