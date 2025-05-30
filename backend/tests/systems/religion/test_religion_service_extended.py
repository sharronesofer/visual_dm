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
import os
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import tempfile
import os

from backend.systems.religion.models import Religion, ReligionMembership, ReligionType, MembershipLevel
from backend.systems.religion.services import ReligionService, get_religion_service
from backend.systems.religion.repository import ReligionRepository
from typing import Type


class TestReligionServiceExtended: pass
    """Extended tests for religion service to improve coverage."""

    @pytest.fixture
    def service(self): pass
        """Provide a religion service instance."""
        # Make sure we test with a temporary data file
        os.environ["RELIGION_DATA_PATH"] = "test_religions_extended.json"
        os.environ["RELIGION_MEMBERSHIP_DATA_PATH"] = "test_memberships_extended.json"

        service = ReligionService()
        yield service

        # Cleanup
        if os.path.exists("test_religions_extended.json"): pass
            os.remove("test_religions_extended.json")
        if os.path.exists("test_memberships_extended.json"): pass
            os.remove("test_memberships_extended.json")

    @pytest.fixture
    def isolated_service(self): pass
        """Provide an isolated religion service instance with clean data."""
        # Create unique temporary directory for this test
        temp_dir = tempfile.mkdtemp(suffix="_religion_test")
        
        # Create new repository with unique storage
        repository = ReligionRepository(storage_dir=temp_dir)
        
        # Create service and directly set the repository
        service = ReligionService()
        service.repository = repository
        
        yield service

        # Cleanup
        try: pass
            import shutil
            shutil.rmtree(temp_dir)
        except: pass
            pass

    def test_get_religion_service_function(self): pass
        """Test the get_religion_service module function."""
        service = get_religion_service()
        assert isinstance(service, ReligionService)

    def test_service_initialization_without_dependencies(self): pass
        """Test service initialization when optional dependencies are missing."""
        with patch('backend.systems.religion.services.HAS_EVENT_DISPATCHER', False), \
             patch('backend.systems.religion.services.HAS_FACTION_SYSTEM', False), \
             patch('backend.systems.religion.services.HAS_QUEST_SYSTEM', False): pass
            service = ReligionService()
            assert service.event_dispatcher is None
            assert service.faction_service is None
            assert service.quest_service is None

    def test_create_religion_without_event_dispatcher(self, isolated_service): pass
        """Test creating religion without event dispatcher."""
        # Mock the event dispatcher to be None
        isolated_service.event_dispatcher = None
        
        religion_data = {
            "name": "Test Faith No Events",
            "description": "A test religion without events",
            "type": ReligionType.MONOTHEISTIC,
        }

        religion = isolated_service.create_religion(religion_data)
        assert religion.name == "Test Faith No Events"

    def test_get_religions_with_filters(self, isolated_service): pass
        """Test getting religions with various filters."""
        # Create test religions with unique names to avoid conflicts
        religion1 = isolated_service.create_religion({
            "name": f"Isolated Regional Faith {os.urandom(4).hex()}",
            "description": "A regional religion",
            "type": ReligionType.ANIMISTIC,
            "region_ids": ["region1", "region2"],
        })

        religion2 = isolated_service.create_religion({
            "name": f"Isolated Monotheistic Faith {os.urandom(4).hex()}",
            "description": "A monotheistic religion",
            "type": ReligionType.MONOTHEISTIC,
            "region_ids": ["region2", "region3"],
        })

        # Test region filter
        religions = isolated_service.get_religions(region_id="region1")
        assert len(religions) == 1
        assert religions[0].id == religion1.id

        # Test religion_type filter
        religions = isolated_service.get_religions(religion_type=ReligionType.MONOTHEISTIC)
        assert len(religions) == 1
        assert religions[0].id == religion2.id

        # Test combined filters
        religions = isolated_service.get_religions(region_id="region2", religion_type=ReligionType.ANIMISTIC)
        assert len(religions) == 1
        assert religions[0].id == religion1.id

    def test_get_religions_by_faction(self, isolated_service): pass
        """Test getting religions by faction ID."""
        # Mock the repository to test faction filtering
        with patch.object(isolated_service.repository, 'get_religions_by_faction') as mock_get_by_faction: pass
            mock_get_by_faction.return_value = [Religion(
                id="test_id",
                name="Faction Religion",
                description="A faction-based religion",
                type=ReligionType.CULT,
            )]

            religions = isolated_service.get_religions(faction_id="faction123")
            mock_get_by_faction.assert_called_once_with("faction123")
            assert len(religions) == 1
            assert religions[0].name == "Faction Religion"

    def test_update_religion_not_found(self, isolated_service): pass
        """Test updating a non-existent religion."""
        result = isolated_service.update_religion("nonexistent_id", {"name": "Updated Name"})
        assert result is None

    def test_update_religion_with_event_dispatcher(self, isolated_service): pass
        """Test updating religion with event dispatcher."""
        # Create a religion first
        religion = isolated_service.create_religion({
            "name": "Updatable Faith",
            "description": "A religion to be updated",
            "type": ReligionType.POLYTHEISTIC,
        })

        # Mock event dispatcher
        mock_dispatcher = Mock()
        isolated_service.event_dispatcher = mock_dispatcher

        # Update the religion
        update_data = {"description": "Updated description", "tenets": ["New tenet"]}
        updated = isolated_service.update_religion(religion.id, update_data)

        assert updated is not None
        assert updated.description == "Updated description"
        assert "New tenet" in updated.tenets
        
        # Verify event was published
        mock_dispatcher.publish.assert_called()

    def test_delete_religion_not_found(self, isolated_service): pass
        """Test deleting a non-existent religion."""
        result = isolated_service.delete_religion("nonexistent_id")
        assert result is False

    def test_delete_religion_with_memberships(self, isolated_service): pass
        """Test deleting a religion that has memberships."""
        # Create religion
        religion = isolated_service.create_religion({
            "name": "Religion to Delete",
            "description": "A religion with memberships",
            "type": ReligionType.ANCESTOR,
        })

        # Create membership
        membership = isolated_service.create_membership({
            "entity_id": "character123",
            "religion_id": religion.id,
            "level": MembershipLevel.FOLLOWER,
        })

        # Mock event dispatcher
        mock_dispatcher = Mock()
        isolated_service.event_dispatcher = mock_dispatcher

        # Delete the religion
        result = isolated_service.delete_religion(religion.id)
        
        assert result is True
        
        # Verify the religion was deleted
        assert isolated_service.get_religion(religion.id) is None
        
        # Verify event was published
        mock_dispatcher.publish.assert_called()

    def test_membership_filtering_by_entity_type_and_level(self, isolated_service): pass
        """Test membership filtering by entity type and level."""
        # Create religion
        religion = isolated_service.create_religion({
            "name": "Test Religion",
            "description": "Test filtering",
            "type": ReligionType.POLYTHEISTIC,
        })

        # Create memberships with different types and levels
        isolated_service.create_membership({
            "entity_id": "character1",
            "religion_id": religion.id,
            "entity_type": "character",
            "level": MembershipLevel.FOLLOWER,
        })

        isolated_service.create_membership({
            "entity_id": "npc1",
            "religion_id": religion.id,
            "entity_type": "npc",
            "level": MembershipLevel.DEVOTED,
        })

        # Test filtering by entity type
        memberships = isolated_service.get_religion_memberships(religion.id, entity_type="character")
        assert len(memberships) == 1
        assert memberships[0].entity_type == "character"

        # Test filtering by level
        memberships = isolated_service.get_religion_memberships(religion.id, level=MembershipLevel.DEVOTED)
        assert len(memberships) == 1
        assert memberships[0].level == MembershipLevel.DEVOTED

        # Test combined filtering
        memberships = isolated_service.get_religion_memberships(
            religion.id, 
            entity_type="npc", 
            level=MembershipLevel.DEVOTED
        )
        assert len(memberships) == 1

    def test_update_membership_level_with_events(self, isolated_service): pass
        """Test updating membership level with event publishing."""
        # Create religion and membership
        religion = isolated_service.create_religion({
            "name": "Test Religion",
            "description": "Test level updates",
            "type": ReligionType.CULT,
        })

        membership = isolated_service.create_membership({
            "entity_id": "character456",
            "religion_id": religion.id,
            "level": MembershipLevel.FOLLOWER,
        })

        # Mock event dispatcher
        mock_dispatcher = Mock()
        isolated_service.event_dispatcher = mock_dispatcher

        # Update membership level
        updated = isolated_service.update_membership_level(
            "character456",
            religion.id,
            MembershipLevel.ZEALOT,
            reason="Extreme dedication"
        )

        assert updated is not None
        assert updated.level == MembershipLevel.ZEALOT
        assert updated.metadata.get("level_change_reason") == "Extreme dedication"
        
        # Verify events were published (membership and narrative events)
        assert mock_dispatcher.publish.call_count == 2

    def test_remove_membership_with_events(self, isolated_service): pass
        """Test removing membership with event publishing."""
        # Create religion and membership
        religion = isolated_service.create_religion({
            "name": "Test Religion",
            "description": "Test membership removal",
            "type": ReligionType.ANIMISTIC,
        })

        membership = isolated_service.create_membership({
            "entity_id": "character789",
            "religion_id": religion.id,
            "level": MembershipLevel.DEVOTED,
        })

        # Mock event dispatcher
        mock_dispatcher = Mock()
        isolated_service.event_dispatcher = mock_dispatcher

        # Remove membership
        result = isolated_service.remove_membership(
            "character789",
            religion.id,
            reason="Lost faith"
        )

        assert result is True
        
        # Verify membership was removed
        assert isolated_service.get_membership("character789", religion.id) is None
        
        # Verify events were published
        assert mock_dispatcher.publish.call_count == 2

    def test_remove_nonexistent_membership(self, isolated_service): pass
        """Test removing a non-existent membership."""
        result = isolated_service.remove_membership("nonexistent", "nonexistent_religion")
        assert result is False

    def test_update_devotion_apostasy(self, isolated_service): pass
        """Test update devotion that results in apostasy (devotion = 0)."""
        # Create religion and membership
        religion = isolated_service.create_religion({
            "name": "Test Religion",
            "description": "Test apostasy",
            "type": ReligionType.MONOTHEISTIC,
        })

        membership = isolated_service.create_membership({
            "entity_id": "character_apostate",
            "religion_id": religion.id,
            "devotion_level": 10,
        })

        # Reduce devotion to 0
        result = isolated_service.update_devotion(
            "character_apostate",
            religion.id,
            -10,  # This should bring devotion to 0
            reason="Complete loss of faith"
        )

        # Should return None because membership was removed due to apostasy
        assert result is None
        
        # Verify membership was removed
        assert isolated_service.get_membership("character_apostate", religion.id) is None

    def test_update_devotion_nonexistent_membership(self, isolated_service): pass
        """Test updating devotion for non-existent membership."""
        result = isolated_service.update_devotion("nonexistent", "nonexistent_religion", 10)
        assert result is None

    def test_get_membership_count(self, isolated_service): pass
        """Test getting membership count with filters."""
        # Create religion
        religion = isolated_service.create_religion({
            "name": "Test Religion",
            "description": "Test counting",
            "type": ReligionType.POLYTHEISTIC,
        })

        # Create memberships
        isolated_service.create_membership({
            "entity_id": "char1",
            "religion_id": religion.id,
            "entity_type": "character",
            "level": MembershipLevel.FOLLOWER,
        })

        isolated_service.create_membership({
            "entity_id": "char2",
            "religion_id": religion.id,
            "entity_type": "character",
            "level": MembershipLevel.DEVOTED,
        })

        isolated_service.create_membership({
            "entity_id": "npc1",
            "religion_id": religion.id,
            "entity_type": "npc",
            "level": MembershipLevel.FOLLOWER,
        })

        # Test total count
        count = isolated_service.get_membership_count(religion.id)
        assert count == 3

        # Test count by entity type
        count = isolated_service.get_membership_count(religion.id, entity_type="character")
        assert count == 2

        # Test count by level
        count = isolated_service.get_membership_count(religion.id, level=MembershipLevel.FOLLOWER)
        assert count == 2

        # Test combined filters
        count = isolated_service.get_membership_count(
            religion.id, 
            entity_type="character", 
            level=MembershipLevel.DEVOTED
        )
        assert count == 1

    def test_trigger_narrative_hook_nonexistent_membership(self, isolated_service): pass
        """Test triggering narrative hook for non-existent membership."""
        result = isolated_service.trigger_narrative_hook(
            "nonexistent_entity",
            "nonexistent_religion",
            "conversion",
            {}
        )
        assert result is None

    def test_trigger_narrative_hook_nonexistent_religion(self, isolated_service): pass
        """Test triggering narrative hook when religion doesn't exist."""
        # Create a membership but then mock repository to return None for religion
        religion = isolated_service.create_religion({
            "name": "Test Religion",
            "description": "Test hooks",
            "type": ReligionType.CULT,
        })

        membership = isolated_service.create_membership({
            "entity_id": "character123",
            "religion_id": religion.id,
        })

        # Mock repository to return membership but no religion
        with patch.object(isolated_service.repository, 'get_religion', return_value=None): pass
            result = isolated_service.trigger_narrative_hook(
                "character123",
                religion.id,
                "conversion",
                {}
            )
            assert result is None

    def test_trigger_narrative_hook_success(self, isolated_service): pass
        """Test successful narrative hook triggering."""
        # Create religion and membership
        religion = isolated_service.create_religion({
            "name": "Test Religion",
            "description": "Test hooks",
            "type": ReligionType.ANCESTOR,
        })

        membership = isolated_service.create_membership({
            "entity_id": "character456",
            "religion_id": religion.id,
            "level": MembershipLevel.DEVOTED,
            "devotion_level": 75,
        })

        # Mock event dispatcher
        mock_dispatcher = Mock()
        isolated_service.event_dispatcher = mock_dispatcher

        # Trigger narrative hook
        hook_data = {
            "location": "Sacred Grove",
            "witnesses": ["npc1", "npc2"]
        }
        
        result = isolated_service.trigger_narrative_hook(
            "character456",
            religion.id,
            "miracle",
            hook_data
        )

        assert result is not None
        assert "character456" in result
        assert "Test Religion" in result
        
        # Verify event was published
        mock_dispatcher.publish.assert_called()

    def test_sync_with_faction_success(self, isolated_service): pass
        """Test successful faction synchronization."""
        # Create religion
        religion = isolated_service.create_religion({
            "name": "Faction Religion",
            "description": "A religion tied to a faction",
            "type": ReligionType.CULT,
        })

        # Mock event dispatcher
        mock_dispatcher = Mock()
        isolated_service.event_dispatcher = mock_dispatcher

        # Sync with faction
        result = isolated_service.sync_with_faction("faction123", religion.id, make_exclusive=True)
        
        assert result is True
        
        # Verify religion was updated
        updated_religion = isolated_service.get_religion(religion.id)
        assert updated_religion.faction_id == "faction123"
        assert updated_religion.metadata.get("exclusive_to_faction") is True
        assert updated_religion.metadata.get("auto_faction_join") is True
        
        # Verify event was published
        mock_dispatcher.publish.assert_called()

    def test_sync_with_faction_not_found(self, isolated_service): pass
        """Test faction sync with non-existent religion."""
        result = isolated_service.sync_with_faction("faction123", "nonexistent_religion")
        assert result is False

    def test_handle_faction_membership_change_joined(self, isolated_service): pass
        """Test faction membership change handling for joined action."""
        # Create religion with faction metadata
        religion = isolated_service.create_religion({
            "name": "Auto-Join Religion",
            "description": "Religion that auto-joins faction",
            "type": ReligionType.CULT,
            "faction_id": "faction456",
            "metadata": {
                "auto_faction_join": True,
                "exclusive_to_faction": True
            }
        })

        # Mock faction service and enable faction system
        mock_faction_service = Mock()
        isolated_service.faction_service = mock_faction_service

        # Mock the HAS_FACTION_SYSTEM to be True
        with patch('backend.systems.religion.services.HAS_FACTION_SYSTEM', True): pass
            # Test the private method directly
            isolated_service._handle_faction_membership_change(
                "character789",
                religion,
                "joined",
                "character"
            )

            # Verify faction service was called
            mock_faction_service.add_member.assert_called_once_with("faction456", "character789")

    def test_handle_faction_membership_change_left(self, isolated_service): pass
        """Test faction membership change handling for left action."""
        # Create religion with auto-leave metadata
        religion = isolated_service.create_religion({
            "name": "Auto-Leave Religion",
            "description": "Religion that auto-leaves faction",
            "type": ReligionType.MONOTHEISTIC,
            "faction_id": "faction789",
            "metadata": {
                "auto_faction_leave": True
            }
        })

        # Mock faction service and enable faction system
        mock_faction_service = Mock()
        isolated_service.faction_service = mock_faction_service

        # Mock the HAS_FACTION_SYSTEM to be True
        with patch('backend.systems.religion.services.HAS_FACTION_SYSTEM', True): pass
            # Test the private method directly
            isolated_service._handle_faction_membership_change(
                "character999",
                religion,
                "left",
                "character"
            )

            # Verify faction service was called
            mock_faction_service.remove_member.assert_called_once_with("faction789", "character999")

    def test_handle_faction_membership_change_role_changed(self, isolated_service): pass
        """Test faction membership change handling for role changed action."""
        # Create religion with role sync metadata
        religion = isolated_service.create_religion({
            "name": "Role-Sync Religion",
            "description": "Religion that syncs roles with faction",
            "type": ReligionType.POLYTHEISTIC,
            "faction_id": "faction111",
            "metadata": {
                "sync_roles": True
            }
        })

        # Mock faction service with update_member_standing method and enable faction system
        mock_faction_service = Mock()
        mock_faction_service.update_member_standing = Mock()
        isolated_service.faction_service = mock_faction_service

        # Mock the HAS_FACTION_SYSTEM to be True
        with patch('backend.systems.religion.services.HAS_FACTION_SYSTEM', True): pass
            # Test the private method directly
            isolated_service._handle_faction_membership_change(
                "character222",
                religion,
                "role_changed",
                "character"
            )

            # Verify faction service was called
            mock_faction_service.update_member_standing.assert_called_once_with("faction111", "character222")

    def test_handle_faction_membership_change_no_faction(self, isolated_service): pass
        """Test faction membership change handling when religion has no faction."""
        # Create religion without faction
        religion = isolated_service.create_religion({
            "name": "No Faction Religion",
            "description": "Religion without faction tie",
            "type": ReligionType.ANIMISTIC,
        })

        # Mock faction service
        mock_faction_service = Mock()
        isolated_service.faction_service = mock_faction_service

        # Test the private method directly
        isolated_service._handle_faction_membership_change(
            "character333",
            religion,
            "joined",
            "character"
        )

        # Verify faction service was NOT called
        mock_faction_service.add_member.assert_not_called()

    def test_check_for_quest_integration_without_quest_service(self, isolated_service): pass
        """Test quest integration check when quest service is not available."""
        # Create religion
        religion = isolated_service.create_religion({
            "name": "Test Religion",
            "description": "Test quest integration",
            "type": ReligionType.CULT,
        })

        # Ensure quest service is None
        isolated_service.quest_service = None

        # This should not raise an error
        isolated_service._check_for_quest_integration(
            "character444",
            religion,
            "conversion",
            {"location": "temple"}
        )

    def test_check_for_quest_integration_with_quest_service(self, isolated_service): pass
        """Test quest integration check with quest service available."""
        # Create religion
        religion = isolated_service.create_religion({
            "name": "Quest Religion",
            "description": "Religion that integrates with quests",
            "type": ReligionType.MONOTHEISTIC,
        })

        # Mock quest service
        mock_quest_service = Mock()
        isolated_service.quest_service = mock_quest_service

        # Test different hook types
        hook_types = ["conversion", "promotion", "ritual", "pilgrimage", "miracle"]
        
        for hook_type in hook_types: pass
            isolated_service._check_for_quest_integration(
                "character555",
                religion,
                hook_type,
                {"location": "sacred_site"}
            )

        # Should not raise any errors (quest integration is a placeholder)

    def test_existing_membership_update_in_create(self, isolated_service): pass
        """Test creating membership when one already exists - should update instead."""
        # Create religion
        religion = isolated_service.create_religion({
            "name": "Update Test Religion",
            "description": "Test membership updates",
            "type": ReligionType.POLYTHEISTIC,
        })

        # Create initial membership
        initial = isolated_service.create_membership({
            "entity_id": "character666",
            "religion_id": religion.id,
            "level": MembershipLevel.FOLLOWER,
            "devotion_level": 30,
        })

        # Try to create another membership for same entity/religion
        updated = isolated_service.create_membership({
            "entity_id": "character666",
            "religion_id": religion.id,
            "level": MembershipLevel.ZEALOT,
            "role": "high_priest",
            "metadata": {"updated": True}
        })

        # Should be the same membership object, but updated
        assert updated.id == initial.id
        assert updated.level == MembershipLevel.ZEALOT
        assert updated.role == "high_priest"
        assert updated.devotion_level == 40  # Should have increased by 10
        assert updated.metadata.get("updated") is True

    def test_update_membership_level_not_found(self, isolated_service): pass
        """Test updating level for non-existent membership."""
        result = isolated_service.update_membership_level(
            "nonexistent_entity",
            "nonexistent_religion",
            MembershipLevel.DEVOTED
        )
        assert result is None

    def test_devotion_level_changes_trigger_level_changes(self, isolated_service): pass
        """Test that devotion changes automatically trigger appropriate level changes."""
        # Create religion and membership
        religion = isolated_service.create_religion({
            "name": "Level Change Religion",
            "description": "Test level changes from devotion",
            "type": ReligionType.ANCESTOR,
        })

        membership = isolated_service.create_membership({
            "entity_id": "character777",
            "religion_id": religion.id,
            "level": MembershipLevel.FOLLOWER,
            "devotion_level": 45,
        })

        # Mock event dispatcher
        mock_dispatcher = Mock()
        isolated_service.event_dispatcher = mock_dispatcher

        # Increase devotion to trigger level change to DEVOTED
        isolated_service.update_devotion("character777", religion.id, 10)  # Should be 55, triggering DEVOTED
        
        updated = isolated_service.get_membership("character777", religion.id)
        assert updated.level == MembershipLevel.DEVOTED
        assert updated.devotion_level == 55

        # Increase devotion to trigger level change to ZEALOT
        isolated_service.update_devotion("character777", religion.id, 30)  # Should be 85, triggering ZEALOT
        
        updated = isolated_service.get_membership("character777", religion.id)
        assert updated.level == MembershipLevel.ZEALOT
        assert updated.devotion_level == 85

        # Decrease devotion to trigger level change back to FOLLOWER
        isolated_service.update_devotion("character777", religion.id, -40)  # Should be 45, triggering FOLLOWER
        
        updated = isolated_service.get_membership("character777", religion.id)
        assert updated.level == MembershipLevel.FOLLOWER
        assert updated.devotion_level == 45

    def test_create_membership_with_kwargs_only(self, isolated_service): pass
        """Test creating membership using only keyword arguments."""
        # Create religion
        religion = isolated_service.create_religion({
            "name": "Kwargs Religion",
            "description": "Test kwargs-only creation",
            "type": ReligionType.SYNCRETIC,
        })

        # Create membership using kwargs only (simulating test call pattern)
        membership = isolated_service.create_membership(
            religion_id=religion.id,
            entity_id="character888",
            entity_type="npc",
            level=MembershipLevel.DEVOTED,
            role="priest"
        )

        assert membership is not None
        assert membership.entity_id == "character888"
        assert membership.religion_id == religion.id
        assert membership.entity_type == "npc"
        assert membership.level == MembershipLevel.DEVOTED
        assert membership.role == "priest"

    def test_create_membership_missing_entity_id(self, isolated_service): pass
        """Test creating membership with missing entity_id raises error."""
        # Create religion
        religion = isolated_service.create_religion({
            "name": "Error Test Religion",
            "description": "Test error handling",
            "type": ReligionType.CULT,
        })

        # Try to create membership without entity_id
        with pytest.raises(ValueError, match="entity_id is required"): pass
            isolated_service.create_membership(religion.id, entity_id=None)

    def test_get_entity_memberships(self, isolated_service): pass
        """Test getting all memberships for a specific entity."""
        # Use unique entity ID to avoid conflicts
        entity_id = f"multi_member_{os.urandom(4).hex()}"
        
        # Create multiple religions
        religion1 = isolated_service.create_religion({
            "name": f"Isolated Religion 1 {os.urandom(4).hex()}",
            "description": "First religion",
            "type": ReligionType.MONOTHEISTIC,
        })

        religion2 = isolated_service.create_religion({
            "name": f"Isolated Religion 2 {os.urandom(4).hex()}", 
            "description": "Second religion",
            "type": ReligionType.POLYTHEISTIC,
        })

        # Create memberships for same entity
        isolated_service.create_membership({
            "entity_id": entity_id,
            "religion_id": religion1.id,
            "level": MembershipLevel.FOLLOWER,
        })

        isolated_service.create_membership({
            "entity_id": entity_id,
            "religion_id": religion2.id,
            "level": MembershipLevel.DEVOTED,
        })

        # Get all memberships for the entity
        memberships = isolated_service.get_entity_memberships(entity_id)
        
        assert len(memberships) == 2
        religion_ids = [m.religion_id for m in memberships]
        assert religion1.id in religion_ids
        assert religion2.id in religion_ids 