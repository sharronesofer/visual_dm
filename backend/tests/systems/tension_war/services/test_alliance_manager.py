from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher

# Import EventBase and EventDispatcher with fallbacks
try: pass
    from backend.systems.events import EventBase, EventDispatcher
except ImportError: pass
    # Fallback for tests or when events system isn't available
    class EventBase: pass
        def __init__(self, **data): pass
            for key, value in data.items(): pass
                setattr(self, key, value)
    
    class EventDispatcher: pass
        @classmethod
        def get_instance(cls): pass
            return cls()
        
        def dispatch(self, event): pass
            pass
        
        def publish(self, event): pass
            pass
        
        def emit(self, event): pass
            pass

"""
Tests for Alliance Manager Service

This module contains comprehensive tests for the AllianceManager service class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid

from backend.systems.tension_war.services.alliance_manager import AllianceManager
from backend.systems.tension_war.models import AllianceConfig
from backend.systems.tension_war.models.enums import AllianceStatus


@pytest.fixture
def alliance_config(): pass
    """Create basic alliance configuration."""
    return AllianceConfig(
        min_alliance_tension=-25.0,
        alliance_breaking_tension=25.0,
        max_allies=5,
        defensive_strength_bonus=0.25,
        call_to_arms_duration=7,
    )


@pytest.fixture
def alliance_manager(alliance_config): pass
    """Create alliance manager instance."""
    with patch('backend.systems.tension_war.services.alliance_manager.EventDispatcher'): pass
        return AllianceManager(config=alliance_config)


@pytest.fixture
def sample_alliance_terms(): pass
    """Create sample alliance terms."""
    return {
        "type": "military",
        "mutual_defense": True,
        "trade_bonus": 0.15,
        "military_support": True,
        "duration_days": 730,
    }


class TestAllianceManagerInitialization: pass
    """Test alliance manager initialization."""

    def test_default_initialization(self): pass
        """Test alliance manager with default config."""
        with patch('backend.systems.tension_war.services.alliance_manager.EventDispatcher'): pass
            manager = AllianceManager()
            
            assert manager.config is not None
            assert isinstance(manager.config, AllianceConfig)
            assert manager.alliances == {}
            assert manager.faction_alliances == {}

    def test_custom_config_initialization(self, alliance_config): pass
        """Test alliance manager with custom config."""
        with patch('backend.systems.tension_war.services.alliance_manager.EventDispatcher'): pass
            manager = AllianceManager(config=alliance_config)
            
            assert manager.config == alliance_config
            assert manager.config.max_allies == 5


class TestCreateAlliance: pass
    """Test alliance creation functionality."""

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_create_new_alliance_success(self, mock_strength, alliance_manager, sample_alliance_terms): pass
        """Test successful creation of new alliance."""
        mock_strength.return_value = {"overall_strength": 8.5, "combined_military": 150}
        
        faction_a_id = "faction_alpha"
        faction_b_id = "faction_beta"
        
        result = alliance_manager.create_alliance(
            faction_a_id, faction_b_id, sample_alliance_terms
        )
        
        # Check alliance was created
        assert result is not None
        assert "id" in result
        assert result["faction_a_id"] == faction_a_id
        assert result["faction_b_id"] == faction_b_id
        assert result["status"] == AllianceStatus.ACTIVE.value
        assert result["is_active"] is True
        assert result["terms"] == sample_alliance_terms
        assert result["formed_at"] is not None
        assert result["ended_at"] is None
        
        # Check alliance is stored
        alliance_id = result["id"]
        assert alliance_id in alliance_manager.alliances
        
        # Check faction lookup indices
        assert faction_a_id in alliance_manager.faction_alliances
        assert faction_b_id in alliance_manager.faction_alliances
        assert alliance_id in alliance_manager.faction_alliances[faction_a_id]
        assert alliance_id in alliance_manager.faction_alliances[faction_b_id]

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_create_alliance_with_default_terms(self, mock_strength, alliance_manager): pass
        """Test alliance creation with default terms."""
        mock_strength.return_value = {"overall_strength": 7.0}
        
        result = alliance_manager.create_alliance("faction_1", "faction_2")
        
        # Check default terms are set
        assert result["terms"]["type"] == "defensive"
        assert result["terms"]["mutual_defense"] is True
        assert result["terms"]["trade_bonus"] == 0.1
        assert result["terms"]["military_support"] is True
        assert result["terms"]["duration_days"] == 365

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_create_duplicate_alliance_returns_existing(self, mock_strength, alliance_manager): pass
        """Test creating duplicate alliance returns existing active alliance."""
        mock_strength.return_value = {"overall_strength": 6.0}
        
        faction_a = "faction_alpha"
        faction_b = "faction_beta"
        
        # Create first alliance
        alliance1 = alliance_manager.create_alliance(faction_a, faction_b)
        
        # Try to create duplicate
        alliance2 = alliance_manager.create_alliance(faction_a, faction_b)
        
        # Should return the same alliance
        assert alliance1["id"] == alliance2["id"]
        assert len(alliance_manager.alliances) == 1

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_reactivate_inactive_alliance(self, mock_strength, alliance_manager): pass
        """Test reactivating an inactive alliance."""
        mock_strength.return_value = {"overall_strength": 7.5}
        
        faction_a = "faction_a"
        faction_b = "faction_b"
        
        # Create alliance
        alliance = alliance_manager.create_alliance(faction_a, faction_b)
        
        # Make it inactive
        alliance["status"] = AllianceStatus.ENDED.value
        alliance["is_active"] = False
        alliance["ended_at"] = datetime.utcnow().isoformat()
        
        # Try to create again (should reactivate)
        new_terms = {"type": "trade", "trade_bonus": 0.2}
        reactivated = alliance_manager.create_alliance(faction_a, faction_b, new_terms)
        
        # Should be the same alliance but reactivated
        assert reactivated["id"] == alliance["id"]
        assert reactivated["status"] == AllianceStatus.ACTIVE.value
        assert reactivated["is_active"] is True
        assert reactivated["ended_at"] is None
        assert reactivated["terms"] == new_terms
        
        # Should have reactivation history entry
        history_events = [entry["event"] for entry in reactivated["history"]]
        assert "reactivated" in history_events


class TestGetAlliance: pass
    """Test alliance retrieval functionality."""

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_get_existing_alliance(self, mock_strength, alliance_manager): pass
        """Test getting an existing alliance."""
        mock_strength.return_value = {"overall_strength": 8.0}
        
        # Create alliance
        alliance = alliance_manager.create_alliance("faction_1", "faction_2")
        alliance_id = alliance["id"]
        
        # Get alliance
        result = alliance_manager.get_alliance(alliance_id)
        
        assert result is not None
        assert result["id"] == alliance_id
        assert result == alliance

    def test_get_nonexistent_alliance(self, alliance_manager): pass
        """Test getting a non-existent alliance."""
        result = alliance_manager.get_alliance("nonexistent_id")
        assert result is None


class TestGetAlliancesByFaction: pass
    """Test getting alliances by faction."""

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_get_alliances_for_faction_with_multiple(self, mock_strength, alliance_manager): pass
        """Test getting all alliances for a faction with multiple alliances."""
        mock_strength.return_value = {"overall_strength": 7.0}
        
        faction_id = "main_faction"
        
        # Create multiple alliances
        alliance1 = alliance_manager.create_alliance(faction_id, "faction_a")
        alliance2 = alliance_manager.create_alliance(faction_id, "faction_b")
        alliance3 = alliance_manager.create_alliance("faction_c", faction_id)
        
        # Get alliances for main faction
        result = alliance_manager.get_alliances_by_faction(faction_id)
        
        assert len(result) == 3
        alliance_ids = [a["id"] for a in result]
        assert alliance1["id"] in alliance_ids
        assert alliance2["id"] in alliance_ids
        assert alliance3["id"] in alliance_ids

    def test_get_alliances_for_faction_with_none(self, alliance_manager): pass
        """Test getting alliances for faction with no alliances."""
        result = alliance_manager.get_alliances_by_faction("lonely_faction")
        assert result == []

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_get_alliances_excludes_missing_data(self, mock_strength, alliance_manager): pass
        """Test that missing alliance data is excluded from results."""
        mock_strength.return_value = {"overall_strength": 6.0}
        
        faction_id = "test_faction"
        
        # Create alliance
        alliance = alliance_manager.create_alliance(faction_id, "other_faction")
        
        # Manually corrupt data (simulate missing alliance)
        alliance_id = alliance["id"]
        del alliance_manager.alliances[alliance_id]
        
        # Get alliances (should exclude missing data)
        result = alliance_manager.get_alliances_by_faction(faction_id)
        assert result == []


class TestGetAllianceBetweenFactions: pass
    """Test getting alliance between specific factions."""

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_get_alliance_between_factions_exists(self, mock_strength, alliance_manager): pass
        """Test getting alliance between two factions when it exists."""
        mock_strength.return_value = {"overall_strength": 8.0}
        
        faction_a = "faction_alpha"
        faction_b = "faction_beta"
        
        # Create alliance
        created_alliance = alliance_manager.create_alliance(faction_a, faction_b)
        
        # Get alliance between factions
        result = alliance_manager.get_alliance_between_factions(faction_a, faction_b)
        
        assert result is not None
        assert result["id"] == created_alliance["id"]

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_get_alliance_between_factions_reverse_order(self, mock_strength, alliance_manager): pass
        """Test getting alliance with factions in reverse order."""
        mock_strength.return_value = {"overall_strength": 7.5}
        
        faction_a = "faction_1"
        faction_b = "faction_2"
        
        # Create alliance
        created_alliance = alliance_manager.create_alliance(faction_a, faction_b)
        
        # Get alliance with reversed faction order
        result = alliance_manager.get_alliance_between_factions(faction_b, faction_a)
        
        assert result is not None
        assert result["id"] == created_alliance["id"]

    def test_get_alliance_between_factions_not_exists(self, alliance_manager): pass
        """Test getting alliance between factions when none exists."""
        result = alliance_manager.get_alliance_between_factions("faction_x", "faction_y")
        assert result is None


class TestUpdateAllianceTerms: pass
    """Test alliance terms updating."""

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_update_alliance_terms_success(self, mock_strength, alliance_manager): pass
        """Test successfully updating alliance terms."""
        mock_strength.return_value = {"overall_strength": 7.0}
        
        # Create alliance
        alliance = alliance_manager.create_alliance("faction_1", "faction_2")
        alliance_id = alliance["id"]
        
        # Update terms
        new_terms = {
            "type": "full",
            "trade_bonus": 0.3,
            "military_support": True,
            "technology_sharing": True,
        }
        
        result = alliance_manager.update_alliance_terms(alliance_id, new_terms)
        
        assert result is not None
        assert result["terms"] == new_terms
        
        # Check history entry was added
        history_events = [entry["event"] for entry in result["history"]]
        assert "terms_updated" in history_events

    def test_update_alliance_terms_nonexistent(self, alliance_manager): pass
        """Test updating terms for non-existent alliance."""
        result = alliance_manager.update_alliance_terms("fake_id", {"type": "trade"})
        assert result is None


class TestEndAlliance: pass
    """Test alliance termination."""

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_end_alliance_success(self, mock_strength, alliance_manager): pass
        """Test successfully ending an alliance."""
        mock_strength.return_value = {"overall_strength": 6.5}
        
        # Create alliance
        alliance = alliance_manager.create_alliance("faction_1", "faction_2")
        alliance_id = alliance["id"]
        
        # End alliance
        reason = "diplomatic_breakdown"
        result = alliance_manager.end_alliance(alliance_id, reason)
        
        assert result is not None
        assert result["status"] == AllianceStatus.ENDED.value
        assert result["is_active"] is False
        assert result["ended_at"] is not None
        
        # Check history entry
        last_entry = result["history"][-1]
        assert last_entry["event"] == "ended"
        assert last_entry["details"]["reason"] == reason

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_end_alliance_with_default_reason(self, mock_strength, alliance_manager): pass
        """Test ending alliance without specific reason."""
        mock_strength.return_value = {"overall_strength": 7.0}
        
        # Create and end alliance
        alliance = alliance_manager.create_alliance("faction_a", "faction_b")
        result = alliance_manager.end_alliance(alliance["id"])
        
        # Should have default reason
        last_entry = result["history"][-1]
        assert last_entry["details"]["reason"] is None

    def test_end_alliance_nonexistent(self, alliance_manager): pass
        """Test ending non-existent alliance."""
        result = alliance_manager.end_alliance("fake_id")
        assert result is None


class TestGetAlliances: pass
    """Test getting all alliances."""

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_get_all_alliances(self, mock_strength, alliance_manager): pass
        """Test getting all alliances."""
        mock_strength.return_value = {"overall_strength": 7.0}
        
        # Create multiple alliances
        alliance1 = alliance_manager.create_alliance("faction_1", "faction_2")
        alliance2 = alliance_manager.create_alliance("faction_3", "faction_4")
        
        # End one alliance
        alliance_manager.end_alliance(alliance2["id"])
        
        # Get all alliances
        all_alliances = alliance_manager.get_alliances(active_only=False)
        assert len(all_alliances) == 2
        
        # Get only active alliances
        active_alliances = alliance_manager.get_alliances(active_only=True)
        assert len(active_alliances) == 1
        assert active_alliances[0]["id"] == alliance1["id"]

    def test_get_alliances_empty(self, alliance_manager): pass
        """Test getting alliances when none exist."""
        result = alliance_manager.get_alliances()
        assert result == []


class TestPrivateMethods: pass
    """Test private helper methods."""

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_create_alliance_memory(self, mock_strength, alliance_manager): pass
        """Test alliance memory creation."""
        mock_strength.return_value = {"overall_strength": 8.0}
        
        # Mock memory service
        with patch.object(alliance_manager, '_create_alliance_memory') as mock_memory: pass
            faction_a = "faction_1"
            faction_b = "faction_2"
            
            alliance = alliance_manager.create_alliance(faction_a, faction_b)
            
            # Check memory creation was called
            mock_memory.assert_called_once_with(faction_a, faction_b, alliance)

    # @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    # def test_emit_alliance_event(self, mock_strength, alliance_manager): pass
    #     """Test alliance event emission."""
    #     mock_strength.return_value = {"overall_strength": 7.5}
        
    #     # Set up mock event dispatcher properly
    #     alliance_manager.event_dispatcher.emit = Mock()
        
    #     # Create alliance (should emit event)
    #     alliance = alliance_manager.create_alliance("faction_a", "faction_b")
        
    #     # Check event was emitted
    #     alliance_manager.event_dispatcher.emit.assert_called()
    #     call_args = alliance_manager.event_dispatcher.emit.call_args
    #     assert call_args[0][0] == "alliance_formed"
    #     assert "alliance_id" in call_args[1]


class TestEdgeCases: pass
    """Test edge cases and error conditions."""

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_create_alliance_same_faction(self, mock_strength, alliance_manager): pass
        """Test creating alliance with same faction (should work but be unusual)."""
        mock_strength.return_value = {"overall_strength": 5.0}
        
        faction_id = "same_faction"
        result = alliance_manager.create_alliance(faction_id, faction_id)
        
        # Should still work (though unusual)
        assert result is not None
        assert result["faction_a_id"] == faction_id
        assert result["faction_b_id"] == faction_id

    @patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength')
    def test_alliance_strength_evaluation_failure(self, mock_strength, alliance_manager): pass
        """Test handling of alliance strength evaluation failure."""
        # Mock strength evaluation to raise exception
        mock_strength.side_effect = Exception("Strength calculation failed")
        
        # Alliance creation should handle the exception gracefully
        with pytest.raises(Exception, match="Strength calculation failed"): pass
            alliance_manager.create_alliance("faction_1", "faction_2")

    def test_faction_alliances_index_consistency(self, alliance_manager): pass
        """Test faction alliances index remains consistent."""
        with patch('backend.systems.tension_war.services.alliance_manager.evaluate_alliance_strength') as mock_strength: pass
            mock_strength.return_value = {"overall_strength": 7.0}
            
            faction_a = "faction_alpha"
            faction_b = "faction_beta"
            
            # Create alliance
            alliance = alliance_manager.create_alliance(faction_a, faction_b)
            alliance_id = alliance["id"]
            
            # End alliance
            alliance_manager.end_alliance(alliance_id)
            
            # Index should still contain the alliance ID
            assert alliance_id in alliance_manager.faction_alliances[faction_a]
            assert alliance_id in alliance_manager.faction_alliances[faction_b]
            
            # But get_alliances_by_faction should still return it
            faction_a_alliances = alliance_manager.get_alliances_by_faction(faction_a)
            assert len(faction_a_alliances) == 1
            assert faction_a_alliances[0]["status"] == AllianceStatus.ENDED.value 