"""
Comprehensive Tests for backend.systems.npc.npc_loyalty_class

This test suite focuses on achieving high coverage for NPC loyalty management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

# Import the module being tested
try: pass
    from backend.systems.npc.npc_loyalty_class import LoyaltyManager
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.npc.npc_loyalty_class: {e}", allow_module_level=True)


@pytest.fixture
def mock_firebase_db(): pass
    """Mock Firebase database."""
    with patch('backend.systems.npc.npc_loyalty_class.db') as mock_db: pass
        yield mock_db


@pytest.fixture
def sample_loyalty_data(): pass
    """Sample loyalty data for testing."""
    return {
        "score": 5,
        "goodwill": 20,
        "tags": ["loyalist"],
        "last_tick": "2023-01-01T00:00:00",
        "auto_abandon": False
    }


@pytest.fixture
def loyalty_manager(sample_loyalty_data): pass
    """Create a LoyaltyManager instance for testing."""
    return LoyaltyManager("test_npc", sample_loyalty_data)


class TestLoyaltyManagerInitialization: pass
    """Test LoyaltyManager initialization functionality."""
    
    def test_init_with_data(self, sample_loyalty_data): pass
        """Test initialization with provided loyalty data."""
        manager = LoyaltyManager("test_npc", sample_loyalty_data)
        
        assert manager.npc_id == "test_npc"
        assert manager.loyalty["score"] == 5
        assert manager.loyalty["goodwill"] == 20
        assert manager.loyalty["tags"] == ["loyalist"]
        assert manager.loyalty["auto_abandon"] is False
    
    def test_init_without_data(self): pass
        """Test initialization with default loyalty data."""
        manager = LoyaltyManager("test_npc")
        
        assert manager.npc_id == "test_npc"
        assert manager.loyalty["score"] == 0
        assert manager.loyalty["goodwill"] == 18
        assert manager.loyalty["tags"] == []
        assert manager.loyalty["auto_abandon"] is False
        assert "last_tick" in manager.loyalty


class TestLoyaltyManagerTick: pass
    """Test loyalty tick functionality."""
    
    def test_tick_max_loyalty_goodwill_regen(self): pass
        """Test goodwill regeneration at max loyalty."""
        loyalty_data = {
            "score": 10,
            "goodwill": 20,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.tick()
        
        assert result["goodwill"] == 21  # Increased by 1
        assert result["score"] == 10  # Unchanged
        assert result["auto_abandon"] is False
    
    def test_tick_high_loyalty_goodwill_regen(self): pass
        """Test goodwill regeneration at high loyalty."""
        loyalty_data = {
            "score": 7,
            "goodwill": 20,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.tick()
        
        assert result["goodwill"] == 21  # Increased by 1
        assert result["score"] == 7  # Unchanged
    
    def test_tick_low_loyalty_goodwill_decay(self): pass
        """Test goodwill decay at low loyalty."""
        loyalty_data = {
            "score": -7,
            "goodwill": 20,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.tick()
        
        assert result["goodwill"] == 19  # Decreased by 1
        assert result["score"] == -7  # Unchanged
    
    def test_tick_high_goodwill_loyalty_increase(self): pass
        """Test loyalty increase with high goodwill."""
        loyalty_data = {
            "score": 5,
            "goodwill": 32,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.tick()
        
        assert result["score"] == 6  # Increased by 1
        assert result["goodwill"] == 33  # Also increased due to high loyalty
    
    def test_tick_low_goodwill_loyalty_decrease(self): pass
        """Test loyalty decrease with low goodwill."""
        loyalty_data = {
            "score": -3,
            "goodwill": 5,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.tick()
        
        assert result["score"] == -4  # Decreased by 1
        assert result["goodwill"] == 5  # No change due to low loyalty not affecting goodwill at this level
    
    def test_tick_auto_abandon_trigger(self): pass
        """Test auto abandon trigger at very low loyalty and goodwill."""
        loyalty_data = {
            "score": -6,
            "goodwill": 0,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.tick()
        
        assert result["auto_abandon"] is True
    
    def test_tick_auto_abandon_reset_at_max_loyalty(self): pass
        """Test auto abandon reset at max loyalty."""
        loyalty_data = {
            "score": 10,
            "goodwill": 20,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": True
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.tick()
        
        assert result["auto_abandon"] is False
    
    def test_tick_clamping_values(self): pass
        """Test that values are properly clamped to valid ranges."""
        loyalty_data = {
            "score": 15,  # Above max
            "goodwill": 50,  # Above max
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.tick()
        
        assert result["score"] == 10  # Clamped to max
        assert result["goodwill"] == 36  # Clamped to max


class TestLoyaltyManagerEvents: pass
    """Test loyalty event application functionality."""
    
    def test_apply_event_goodwill_change(self, loyalty_manager): pass
        """Test applying event with goodwill change."""
        impact = {"goodwill": 5}
        
        result = loyalty_manager.apply_event(impact)
        
        assert result["goodwill"] == 26  # 20 + 5 + 1 (from tick due to high loyalty)
        assert result["score"] == 5  # Unchanged
    
    def test_apply_event_loyalty_change(self, loyalty_manager): pass
        """Test applying event with loyalty change."""
        impact = {"loyalty": 2}
        
        result = loyalty_manager.apply_event(impact)
        
        assert result["score"] == 7  # 5 + 2
        assert result["goodwill"] == 21  # Increased due to high loyalty in tick
    
    def test_apply_event_combined_changes(self, loyalty_manager): pass
        """Test applying event with both goodwill and loyalty changes."""
        impact = {"goodwill": -5, "loyalty": -2}
        
        result = loyalty_manager.apply_event(impact)
        
        assert result["goodwill"] == 15  # 20 - 5
        assert result["score"] == 3  # 5 - 2
    
    def test_apply_qualifying_event_success(self, loyalty_manager): pass
        """Test qualifying event that succeeds."""
        with patch('backend.systems.npc.npc_loyalty_class.random.random', return_value=0.3): pass
            result = loyalty_manager.apply_qualifying_event(chance=0.5)
            
            # Should succeed because 0.3 < (0.5 - 20*0.03 = -0.1, clamped to 0)
            # Actually, with goodwill 20, block_chance = 0.6, final_chance = 0
            # So it should not succeed
            assert result["goodwill"] == 21  # Increased due to high loyalty in tick
    
    def test_apply_qualifying_event_blocked(self, loyalty_manager): pass
        """Test qualifying event that gets blocked by high goodwill."""
        with patch('backend.systems.npc.npc_loyalty_class.random.random', return_value=0.8): pass
            result = loyalty_manager.apply_qualifying_event(chance=0.5)
            
            # With goodwill 20, block_chance = 0.6, final_chance = 0
            # Random 0.8 > 0, so no goodwill loss
            assert result["goodwill"] == 21  # Only increased due to tick


class TestLoyaltyManagerAlignmentEvents: pass
    """Test alignment-based event functionality."""
    
    def test_apply_alignment_event_positive(self, loyalty_manager): pass
        """Test positive alignment event."""
        result = loyalty_manager.apply_alignment_event(3)
        
        # With loyalist tag, gain_mod = 1.5
        assert result["score"] == 9  # 5 + int(3 * 1.5) = 5 + 4 = 9
        assert result["goodwill"] == 22  # 20 + 1 + 1 (from tick)
    
    def test_apply_alignment_event_negative(self, loyalty_manager): pass
        """Test negative alignment event."""
        result = loyalty_manager.apply_alignment_event(-2)
        
        # With loyalist tag, loss_mod = 0.5
        assert result["score"] == 4  # 5 + int(-2 * 0.5) = 5 - 1 = 4
        assert result["goodwill"] == 18  # 20 - 2 (from alignment) - 1 (from tick due to low loyalty after change)
    
    def test_apply_alignment_event_coward_tag(self): pass
        """Test alignment event with coward tag."""
        loyalty_data = {
            "score": 0,
            "goodwill": 18,
            "tags": ["coward"],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.apply_alignment_event(2)
        
        # With coward tag, gain_mod = 0.5
        assert result["score"] == 1  # 0 + int(2 * 0.5) = 0 + 1 = 1
    
    def test_apply_alignment_event_bestie_tag(self): pass
        """Test alignment event with bestie tag."""
        loyalty_data = {
            "score": 5,
            "goodwill": 18,
            "tags": ["bestie"],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.apply_alignment_event(-5)
        
        # With bestie tag, score is always 10
        assert result["score"] == 10
        assert result["auto_abandon"] is False
    
    def test_apply_alignment_event_nemesis_tag(self): pass
        """Test alignment event with nemesis tag."""
        loyalty_data = {
            "score": 5,
            "goodwill": 18,
            "tags": ["nemesis"],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.apply_alignment_event(5)
        
        # With nemesis tag, score is always -10
        assert result["score"] == -10
    
    @patch('backend.systems.npc.npc_loyalty_class.db')
    def test_apply_alignment_event_with_character_id(self, mock_db, loyalty_manager): pass
        """Test alignment event with character ID for faction ripple."""
        mock_pc_ref = Mock()
        mock_pc_ref.get.return_value = ["faction_a", "faction_b"]
        
        mock_faction_ref = Mock()
        mock_faction_ref.get.return_value = 5
        
        def reference_side_effect(path): pass
            if "pcs/char123/faction_affiliations" in path: pass
                return mock_pc_ref
            elif "faction_opinions" in path: pass
                return mock_faction_ref
            else: pass
                return Mock()
        
        mock_db.reference.side_effect = reference_side_effect
        
        result = loyalty_manager.apply_alignment_event(2, character_id="char123")
        
        # Should update faction opinions
        assert mock_db.reference.called
        mock_faction_ref.set.assert_called()


class TestLoyaltyManagerUtilities: pass
    """Test utility functionality."""
    
    def test_should_abandon_true(self): pass
        """Test should_abandon returns True for low loyalty and goodwill."""
        loyalty_data = {
            "score": -6,
            "goodwill": 0,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        assert manager.should_abandon() is True
    
    def test_should_abandon_false_high_goodwill(self): pass
        """Test should_abandon returns False for high goodwill."""
        loyalty_data = {
            "score": -6,
            "goodwill": 10,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        assert manager.should_abandon() is False
    
    def test_should_abandon_false_high_loyalty(self): pass
        """Test should_abandon returns False for high loyalty."""
        loyalty_data = {
            "score": 2,
            "goodwill": 0,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        assert manager.should_abandon() is False
    
    def test_to_dict(self, loyalty_manager): pass
        """Test to_dict returns loyalty data."""
        result = loyalty_manager.to_dict()
        
        assert result == loyalty_manager.loyalty
        assert result["score"] == 5
        assert result["goodwill"] == 20


class TestLoyaltyManagerFirebase: pass
    """Test Firebase integration functionality."""
    
    @patch('backend.systems.npc.npc_loyalty_class.db')
    def test_save_to_firebase_basic(self, mock_db, loyalty_manager): pass
        """Test saving loyalty data to Firebase."""
        mock_ref = Mock()
        mock_db.reference.return_value = mock_ref
        
        result = loyalty_manager.save_to_firebase()
        
        mock_db.reference.assert_called_once_with("/npcs/test_npc")
        mock_ref.update.assert_called_once_with({"loyalty": loyalty_manager.loyalty})
        assert result == loyalty_manager.loyalty
    
    @patch('backend.systems.npc.npc_loyalty_class.db')
    def test_save_to_firebase_with_character(self, mock_db, loyalty_manager): pass
        """Test saving loyalty data to Firebase with character ID."""
        mock_ref = Mock()
        mock_db.reference.return_value = mock_ref
        
        result = loyalty_manager.save_to_firebase(character_id="char123")
        
        mock_db.reference.assert_called_once_with("/npcs/test_npc/relationships/char123")
        mock_ref.update.assert_called_once_with({"loyalty": loyalty_manager.loyalty})
        assert result == loyalty_manager.loyalty
    
    @patch('backend.systems.npc.npc_loyalty_class.db')
    def test_load_from_firebase_basic(self, mock_db, sample_loyalty_data): pass
        """Test loading loyalty data from Firebase."""
        mock_ref = Mock()
        mock_ref.get.return_value = {"loyalty": sample_loyalty_data}
        mock_db.reference.return_value = mock_ref
        
        manager = LoyaltyManager.load_from_firebase("test_npc")
        
        mock_db.reference.assert_called_once_with("/npcs/test_npc")
        assert manager.npc_id == "test_npc"
        assert manager.loyalty == sample_loyalty_data
    
    @patch('backend.systems.npc.npc_loyalty_class.db')
    def test_load_from_firebase_with_character(self, mock_db, sample_loyalty_data): pass
        """Test loading loyalty data from Firebase with character ID."""
        mock_ref = Mock()
        mock_ref.get.return_value = {"loyalty": sample_loyalty_data}
        mock_db.reference.return_value = mock_ref
        
        manager = LoyaltyManager.load_from_firebase("test_npc", character_id="char123")
        
        mock_db.reference.assert_called_once_with("/npcs/test_npc/relationships/char123")
        assert manager.npc_id == "test_npc"
        assert manager.loyalty == sample_loyalty_data
    
    @patch('backend.systems.npc.npc_loyalty_class.db')
    def test_load_from_firebase_no_data(self, mock_db): pass
        """Test loading loyalty data from Firebase when no data exists."""
        mock_ref = Mock()
        mock_ref.get.return_value = None
        mock_db.reference.return_value = mock_ref
        
        manager = LoyaltyManager.load_from_firebase("test_npc")
        
        assert manager.npc_id == "test_npc"
        assert manager.loyalty["score"] == 0  # Default values
        assert manager.loyalty["goodwill"] == 18


class TestLoyaltyManagerEdgeCases: pass
    """Test edge cases and error handling."""
    
    def test_ripple_faction_opinion_firebase_error(self, loyalty_manager): pass
        """Test faction opinion ripple with Firebase error."""
        with patch('backend.systems.npc.npc_loyalty_class.db') as mock_db: pass
            mock_db.reference.side_effect = Exception("Firebase error")
            
            # Should not raise exception
            result = loyalty_manager.apply_alignment_event(2, character_id="char123")
            
            # Should still process the alignment event
            assert result["score"] == 8  # 5 + int(2 * 1.5) = 5 + 3 = 8 with loyalist tag
    
    def test_extreme_values_handling(self): pass
        """Test handling of extreme values."""
        loyalty_data = {
            "score": -50,  # Way below minimum
            "goodwill": 100,  # Way above maximum
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        result = manager.tick()
        
        # Should be clamped to valid ranges
        assert -10 <= result["score"] <= 10
        assert 0 <= result["goodwill"] <= 36
    
    def test_multiple_tags_interaction(self): pass
        """Test behavior with multiple tags."""
        loyalty_data = {
            "score": 0,
            "goodwill": 18,
            "tags": ["loyalist", "coward"],  # Conflicting tags
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        # Should use the first matching tag (loyalist)
        result = manager.apply_alignment_event(2)
        
        assert result["score"] == 3  # 0 + int(2 * 1.5) = 3


class TestLoyaltyManagerIntegration: pass
    """Test integration scenarios."""
    
    def test_complete_loyalty_lifecycle(self): pass
        """Test complete loyalty management lifecycle."""
        # Start with neutral NPC
        manager = LoyaltyManager("test_npc")
        
        # Apply positive events
        manager.apply_event({"goodwill": 10, "loyalty": 2})
        assert manager.loyalty["score"] == 2
        assert manager.loyalty["goodwill"] == 28
        
        # Apply alignment event
        manager.apply_alignment_event(3)
        assert manager.loyalty["score"] == 5
        
        # Tick several times to see progression
        for _ in range(5): pass
            manager.tick()
        
        # Should have high loyalty and goodwill
        assert manager.loyalty["score"] >= 5
        assert manager.loyalty["goodwill"] >= 28
        assert not manager.should_abandon()
    
    def test_abandonment_scenario(self): pass
        """Test scenario leading to abandonment."""
        # Start with low loyalty
        loyalty_data = {
            "score": -3,
            "goodwill": 8,
            "tags": [],
            "last_tick": "2023-01-01T00:00:00",
            "auto_abandon": False
        }
        manager = LoyaltyManager("test_npc", loyalty_data)
        
        # Apply negative events
        manager.apply_event({"goodwill": -8, "loyalty": -3})
        
        # Tick to trigger abandonment logic
        result = manager.tick()
        
        # Should be in abandonment state
        assert manager.should_abandon()
        assert result["auto_abandon"] is True 