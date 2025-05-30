from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
from backend.systems.religion.models import Religion
from backend.systems.religion.services import ReligionService
import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timedelta
from typing import Any, Type, List, Dict, Optional, Union

from backend.systems.religion.models import (
    Religion,
    ReligionMembership,
    MembershipLevel,
    ReligionType,
)
from backend.systems.religion.services import ReligionService, ReligionMembershipEvent


class TestReligionMembershipService: pass
    """Tests for the religion membership functionality in the consolidated ReligionService."""

    @pytest.fixture
    def mock_repository(self): pass
        """Create a mock repository."""
        repository = MagicMock()
        # Set up the mock repository to return None for get_membership_by_entity_religion
        # to simulate new memberships by default
        repository.get_membership_by_entity_religion.return_value = None
        return repository

    @pytest.fixture
    def mock_narrative_service(self): pass
        """Create a mock narrative service."""
        return MagicMock()

    @pytest.fixture
    def mock_faction_service(self): pass
        """Create a mock faction service."""
        return MagicMock()

    @pytest.fixture
    def mock_event_dispatcher(self): pass
        """Create a mock event dispatcher."""
        return MagicMock()

    @pytest.fixture
    def sample_religion(self): pass
        """Create a sample religion for testing."""
        return Religion(
            id="religion1",
            name="Test Religion",
            description="A test religion",
            type=ReligionType.POLYTHEISTIC,
            tenets=["Be kind", "Help others"],
            region_ids=["region1", "region2"],
            faction_id="faction1",
        )

    @pytest.fixture
    def membership_service(
        self,
        mock_repository,
        mock_narrative_service,
        mock_faction_service,
        mock_event_dispatcher,
    ): pass
        """Create a religion service with mocked dependencies."""
        # Use patch to avoid importing the services
        with patch(
            "backend.systems.religion.services.get_religion_repository",
            return_value=mock_repository,
        ): pass
            service = ReligionService()
            # Manually set the dependencies to avoid complex import mocking
            service.event_dispatcher = mock_event_dispatcher
            service.faction_service = mock_faction_service
            return service

    def test_get_entity_memberships(self, membership_service, mock_repository): pass
        """Test retrieving memberships for an entity."""
        # Setup mock
        expected_memberships = [
            ReligionMembership(
                id="membership1",
                entity_id="character1",
                religion_id="religion1",
                level=MembershipLevel.FOLLOWER,
            )
        ]
        mock_repository.get_memberships_by_entity.return_value = expected_memberships

        # Call the service
        result = membership_service.get_entity_memberships("character1")

        # Verify
        mock_repository.get_memberships_by_entity.assert_called_once_with(
            "character1", "character"
        )
        assert result == expected_memberships

    def test_get_entity_memberships_multiple(self, membership_service, mock_repository): pass
        """Test retrieving multiple memberships for an entity."""
        # Setup mock
        expected_memberships = [
            ReligionMembership(
                id="membership1",
                entity_id="character1",
                religion_id="religion1",
                level=MembershipLevel.FOLLOWER,
            ),
            ReligionMembership(
                id="membership2",
                entity_id="character1",
                religion_id="religion2",
                level=MembershipLevel.DEVOTED,
            ),
        ]
        mock_repository.get_memberships_by_entity.return_value = expected_memberships

        # Call the service
        result = membership_service.get_entity_memberships("character1")

        # Verify
        mock_repository.get_memberships_by_entity.assert_called_once_with(
            "character1", "character"
        )
        assert result == expected_memberships

    def test_get_religion_memberships(self, membership_service, mock_repository): pass
        """Test retrieving all memberships for a religion."""
        # Setup mock
        expected_memberships = [
            ReligionMembership(
                id="membership1",
                entity_id="character1",
                religion_id="religion1",
                level=MembershipLevel.FOLLOWER,
            ),
            ReligionMembership(
                id="membership2",
                entity_id="character2",
                religion_id="religion1",
                level=MembershipLevel.DEVOTED,
            ),
        ]
        mock_repository.get_memberships_by_religion.return_value = expected_memberships

        # Call the service
        result = membership_service.get_religion_memberships("religion1")

        # Verify
        mock_repository.get_memberships_by_religion.assert_called_once_with("religion1")
        assert result == expected_memberships

    def test_get_religion_memberships_with_filters(
        self, membership_service, mock_repository
    ): pass
        """Test retrieving filtered memberships for a religion."""
        # Setup mock - create memberships with different levels and entity types
        all_memberships = [
            ReligionMembership(
                id="membership1",
                entity_id="character1",
                religion_id="religion1",
                entity_type="character",
                level=MembershipLevel.FOLLOWER,
            ),
            ReligionMembership(
                id="membership2",
                entity_id="character2",
                religion_id="religion1",
                entity_type="character",
                level=MembershipLevel.DEVOTED,
            ),
            ReligionMembership(
                id="membership3",
                entity_id="faction1",
                religion_id="religion1",
                entity_type="faction",
                level=MembershipLevel.ZEALOT,
            ),
        ]
        mock_repository.get_memberships_by_religion.return_value = all_memberships

        # Call the service with filters
        result_entity_type = membership_service.get_religion_memberships(
            "religion1", entity_type="faction"
        )

        result_level = membership_service.get_religion_memberships(
            "religion1", level=MembershipLevel.DEVOTED
        )

        result_both = membership_service.get_religion_memberships(
            "religion1", entity_type="character", level=MembershipLevel.FOLLOWER
        )

        # Verify
        assert len(result_entity_type) == 1
        assert result_entity_type[0].id == "membership3"
        assert result_entity_type[0].entity_type == "faction"

        assert len(result_level) == 1
        assert result_level[0].id == "membership2"
        assert result_level[0].level == MembershipLevel.DEVOTED

        assert len(result_both) == 1
        assert result_both[0].id == "membership1"
        assert result_both[0].entity_type == "character"
        assert result_both[0].level == MembershipLevel.FOLLOWER

    def test_create_new_membership(
        self,
        membership_service,
        mock_repository,
        mock_narrative_service,
        mock_faction_service,
        mock_event_dispatcher,
        sample_religion,
    ): pass
        """Test creating a new membership."""
        # Setup mocks
        mock_repository.get_membership_by_entity_religion.return_value = (
            None  # No existing membership
        )
        mock_repository.get_religion.return_value = sample_religion

        new_membership = ReligionMembership(
            id="new_membership",
            entity_id="character1",
            religion_id="religion1",
            level=MembershipLevel.FOLLOWER,
        )
        mock_repository.create_membership.return_value = new_membership

        # Call the service
        result = membership_service.create_membership(
            religion_id="religion1",
            entity_id="character1",
            level=MembershipLevel.FOLLOWER,
            join_reason="Seeking guidance",
            metadata={"referred_by": "character2"},
        )

        # Verify repository calls
        mock_repository.get_membership_by_entity_religion.assert_called_once_with(
            "character1", "character", "religion1"
        )
        mock_repository.create_membership.assert_called_once()

        # Verify integration calls - the consolidated service publishes events instead of calling external services
        # Verify that events were published (should be called twice: membership event and narrative event)
        assert mock_event_dispatcher.publish.call_count == 2

        # Verify the first published event (membership event)
        membership_event_call = mock_event_dispatcher.publish.call_args_list[0][0][0]
        assert isinstance(membership_event_call, ReligionMembershipEvent)
        assert membership_event_call.religion_id == "religion1"
        assert membership_event_call.entity_id == "character1"
        assert membership_event_call.event_type == "join"
        assert membership_event_call.new_level == MembershipLevel.FOLLOWER.value
        assert "referred_by" in membership_event_call.metadata

        # Verify the result
        assert result == new_membership

    def test_update_existing_membership(
        self,
        membership_service,
        mock_repository,
        mock_narrative_service,
        mock_event_dispatcher,
        sample_religion,
    ): pass
        """Test updating an existing membership."""
        # Setup mocks
        existing_membership = ReligionMembership(
            id="existing_membership",
            entity_id="character1",
            religion_id="religion1",
            level=MembershipLevel.FOLLOWER,
            devotion_level=50,
        )
        mock_repository.get_membership_by_entity_religion.return_value = (
            existing_membership
        )
        mock_repository.get_religion.return_value = sample_religion

        updated_membership = ReligionMembership(
            id="existing_membership",
            entity_id="character1",
            religion_id="religion1",
            level=MembershipLevel.DEVOTED,  # Changed level
            devotion_level=50,
        )
        mock_repository.update_membership.return_value = updated_membership

        # Call the service
        result = membership_service.create_membership(
            religion_id="religion1",
            entity_id="character1",
            level=MembershipLevel.DEVOTED,  # Different level from existing
            metadata={"promotion_reason": "Dedicated service"},
        )

        # Verify repository calls
        mock_repository.get_membership_by_entity_religion.assert_called_once()
        mock_repository.update_membership.assert_called_once()

        # Verify event dispatch for level change
        event_call = mock_event_dispatcher.publish.call_args[0][0]
        assert isinstance(event_call, ReligionMembershipEvent)
        assert event_call.event_type == "level_change"
        assert event_call.old_level == MembershipLevel.FOLLOWER.value
        assert event_call.new_level == MembershipLevel.DEVOTED.value
        assert "promotion_reason" in event_call.metadata

        # Verify the result
        assert result == updated_membership

    def test_update_membership_level(
        self,
        membership_service,
        mock_repository,
        mock_narrative_service,
        mock_event_dispatcher,
    ): pass
        """Test updating a membership's level."""
        # Setup mocks
        existing_membership = ReligionMembership(
            id="membership1",
            entity_id="character1",
            religion_id="religion1",
            level=MembershipLevel.FOLLOWER,
        )
        updated_membership = ReligionMembership(
            id="membership1",
            entity_id="character1",
            religion_id="religion1",
            level=MembershipLevel.DEVOTED,  # Updated level
        )

        mock_repository.get_membership_by_entity_religion.return_value = (
            existing_membership
        )
        mock_repository.update_membership.return_value = updated_membership
        mock_repository.get_religion.return_value = Religion(
            id="religion1",
            name="Test Religion",
            description="Test",
            type=ReligionType.CULT,
        )

        # Call the service
        result = membership_service.update_membership_level(
            entity_id="character1",
            religion_id="religion1",
            new_level=MembershipLevel.DEVOTED,
            reason="Proven dedication",
        )

        # Verify repository calls
        mock_repository.get_membership_by_entity_religion.assert_called_once_with(
            "character1", "character", "religion1"
        )
        mock_repository.update_membership.assert_called_once()

        # Verify that events were published (membership event and narrative event)
        assert mock_event_dispatcher.publish.call_count == 2

        # Verify the result
        assert result == updated_membership

    def test_update_membership_level_nonexistent(
        self, membership_service, mock_repository
    ): pass
        """Test attempting to update a non-existent membership's level."""
        # Setup mock to return None for non-existent membership
        mock_repository.get_membership_by_entity_religion.return_value = None

        # Call the service
        result = membership_service.update_membership_level(
            entity_id="character1",
            religion_id="nonexistent",
            new_level=MembershipLevel.DEVOTED,
        )

        # Verify
        mock_repository.get_membership_by_entity_religion.assert_called_once_with(
            "character1", "character", "nonexistent"
        )
        mock_repository.update_membership.assert_not_called()
        assert result is None

    def test_remove_membership(
        self,
        membership_service,
        mock_repository,
        mock_narrative_service,
        mock_faction_service,
        mock_event_dispatcher,
    ): pass
        """Test removing a membership."""
        # Setup mocks
        existing_membership = ReligionMembership(
            id="membership1",
            entity_id="character1",
            religion_id="religion1",
            level=MembershipLevel.FOLLOWER,
        )
        mock_repository.get_membership_by_entity_religion.return_value = (
            existing_membership
        )
        mock_repository.delete_membership.return_value = True

        mock_repository.get_religion.return_value = Religion(
            id="religion1",
            name="Test Religion",
            description="Test",
            type=ReligionType.CULT,
        )

        # Call the service
        result = membership_service.remove_membership(
            entity_id="character1", religion_id="religion1", reason="Lost faith"
        )

        # Verify repository calls
        mock_repository.get_membership_by_entity_religion.assert_called_once_with(
            "character1", "character", "religion1"
        )
        mock_repository.delete_membership.assert_called_once_with("membership1")

        # Verify that events were published (membership event and narrative event)
        assert mock_event_dispatcher.publish.call_count == 2

        # Verify the first event (membership leave event)
        leave_event_call = mock_event_dispatcher.publish.call_args_list[0][0][0]
        assert isinstance(leave_event_call, ReligionMembershipEvent)
        assert leave_event_call.event_type == "leave"
        assert leave_event_call.religion_id == "religion1"
        assert leave_event_call.entity_id == "character1"
        assert "reason" in leave_event_call.metadata
        assert leave_event_call.metadata["reason"] == "Lost faith"

        # Verify the result
        assert result is True

    def test_remove_nonexistent_membership(self, membership_service, mock_repository): pass
        """Test attempting to remove a non-existent membership."""
        # Setup mock to return None for non-existent membership
        mock_repository.get_membership_by_entity_religion.return_value = None

        # Call the service
        result = membership_service.remove_membership(
            entity_id="character1", religion_id="nonexistent"
        )

        # Verify
        mock_repository.get_membership_by_entity_religion.assert_called_once_with(
            "character1", "character", "nonexistent"
        )
        mock_repository.delete_membership.assert_not_called()
        assert result is False

    def test_get_membership_count(self, membership_service, mock_repository): pass
        """Test getting the count of memberships for a religion."""
        # Setup mock to return multiple memberships
        mock_repository.get_memberships_by_religion.return_value = [
            ReligionMembership(
                id="m1",
                entity_id="c1",
                religion_id="r1",
                entity_type="character",
                level=MembershipLevel.FOLLOWER,
            ),
            ReligionMembership(
                id="m2",
                entity_id="c2",
                religion_id="r1",
                entity_type="character",
                level=MembershipLevel.DEVOTED,
            ),
            ReligionMembership(
                id="m3",
                entity_id="f1",
                religion_id="r1",
                entity_type="faction",
                level=MembershipLevel.ZEALOT,
            ),
        ]

        # Call the service
        total_count = membership_service.get_membership_count("r1")
        character_count = membership_service.get_membership_count(
            "r1", entity_type="character"
        )
        devoted_count = membership_service.get_membership_count(
            "r1", level=MembershipLevel.DEVOTED
        )

        # Verify
        assert total_count == 3
        assert character_count == 2
        assert devoted_count == 1
