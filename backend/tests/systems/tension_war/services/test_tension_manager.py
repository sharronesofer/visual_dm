from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
"""
Tests for TensionManager service.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from backend.systems.tension_war.services.tension_manager import TensionManager
from backend.systems.tension_war.models import TensionConfig, TensionLevel


class TestTensionManager(unittest.TestCase): pass
    """Test cases for TensionManager."""

    def setUp(self): pass
        """Set up test fixtures."""
        self.config = TensionConfig()
        self.manager = TensionManager(self.config)

    def test_init(self): pass
        """Test TensionManager initialization."""
        # Test with default config
        manager = TensionManager()
        self.assertIsNotNone(manager.config)
        self.assertEqual(manager._tensions, {})

        # Test with custom config
        custom_config = TensionConfig(base_tension=25.0)
        manager = TensionManager(custom_config)
        self.assertEqual(manager.config.base_tension, 25.0)

    def test_get_tension_new_region(self): pass
        """Test getting tension for a new region."""
        result = self.manager.get_tension("region1")
        
        self.assertEqual(result["region_id"], "region1")
        self.assertEqual(result["factions"], {})
        self.assertIn("last_updated", result)

    def test_get_tension_existing_region(self): pass
        """Test getting tension for an existing region."""
        # First modify tension to create the region
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        self.manager.modify_tension("region1", faction_pair, 10.0)
        
        result = self.manager.get_tension("region1")
        
        self.assertEqual(result["region_id"], "region1")
        self.assertIn("factions", result)
        self.assertIn("last_updated", result)

    def test_modify_tension_positive(self): pass
        """Test modifying tension with positive value."""
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        
        result = self.manager.modify_tension("region1", faction_pair, 15.0, "Test increase")
        
        self.assertEqual(result["region_id"], "region1")
        self.assertIn("factions", result)
        
        # Check that tension was increased
        tension = self.manager.get_faction_tension("region1", "faction1", "faction2")
        self.assertEqual(tension, self.config.base_tension + 15.0)

    def test_modify_tension_negative(self): pass
        """Test modifying tension with negative value."""
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        
        result = self.manager.modify_tension("region1", faction_pair, -10.0, "Test decrease")
        
        self.assertEqual(result["region_id"], "region1")
        
        # Check that tension was decreased
        tension = self.manager.get_faction_tension("region1", "faction1", "faction2")
        self.assertEqual(tension, self.config.base_tension - 10.0)

    def test_modify_tension_zero_change(self): pass
        """Test modifying tension with zero value."""
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        
        result = self.manager.modify_tension("region1", faction_pair, 0.0, "No change")
        
        # Check that tension remained at base level
        tension = self.manager.get_faction_tension("region1", "faction1", "faction2")
        self.assertEqual(tension, self.config.base_tension)

    def test_reset_tension(self): pass
        """Test resetting tension for a region."""
        # First add some tension
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        self.manager.modify_tension("region1", faction_pair, 20.0)
        
        # Reset tension
        result = self.manager.reset_tension("region1")
        
        self.assertEqual(result["region_id"], "region1")
        self.assertEqual(result["factions"], {})
        self.assertIn("last_updated", result)

    def test_decay_tension_single_day(self): pass
        """Test tension decay for a single day."""
        # First add some tension
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        self.manager.modify_tension("region1", faction_pair, 20.0)
        
        # Apply decay
        result = self.manager.decay_tension("region1", 1)
        
        # Check that tension was reduced
        tension = self.manager.get_faction_tension("region1", "faction1", "faction2")
        self.assertLess(tension, self.config.base_tension + 20.0)

    def test_decay_tension_multiple_days(self): pass
        """Test tension decay for multiple days."""
        # First add some tension
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        self.manager.modify_tension("region1", faction_pair, 30.0)
        
        # Apply decay for multiple days
        result = self.manager.decay_tension("region1", 5)
        
        # Check that tension was reduced more than single day
        tension = self.manager.get_faction_tension("region1", "faction1", "faction2")
        self.assertLess(tension, self.config.base_tension + 30.0)

    def test_get_faction_tension(self): pass
        """Test getting tension between specific factions."""
        # First add some tension
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        self.manager.modify_tension("region1", faction_pair, 25.0)
        
        # Get tension
        tension = self.manager.get_faction_tension("region1", "faction1", "faction2")
        self.assertEqual(tension, self.config.base_tension + 25.0)
        
        # Test reverse order (should be same)
        tension_reverse = self.manager.get_faction_tension("region1", "faction2", "faction1")
        self.assertEqual(tension, tension_reverse)

    def test_get_faction_tension_no_data(self): pass
        """Test getting tension for factions with no existing data."""
        tension = self.manager.get_faction_tension("region1", "faction1", "faction2")
        self.assertEqual(tension, self.config.base_tension)

    def test_calculate_event_impact(self): pass
        """Test calculating event impact on tension."""
        affected_factions = [
            {"faction_a": "faction1", "faction_b": "faction2"},
            {"faction_a": "faction1", "faction_b": "faction3"}
        ]
        
        result = self.manager.calculate_event_impact(
            "region1", "border_skirmish", 0.7, affected_factions, "Test event"
        )
        
        self.assertEqual(result["region_id"], "region1")
        self.assertIn("factions", result)

    def test_calculate_event_impact_multiple_factions(self): pass
        """Test calculating event impact with multiple faction pairs."""
        affected_factions = [
            {"faction_a": "faction1", "faction_b": "faction2"},
            {"faction_a": "faction2", "faction_b": "faction3"},
            {"faction_a": "faction1", "faction_b": "faction3"}
        ]
        
        result = self.manager.calculate_event_impact(
            "region1", "trade_dispute", 0.5, affected_factions, "Multi-faction event"
        )
        
        self.assertEqual(result["region_id"], "region1")
        self.assertIn("factions", result)

    def test_config_usage(self): pass
        """Test that manager uses provided configuration."""
        custom_config = TensionConfig(
            base_tension=30.0,
            min_tension=-50.0,
            max_tension=150.0
        )
        manager = TensionManager(custom_config)
        
        self.assertEqual(manager.config.base_tension, 30.0)
        self.assertEqual(manager.config.min_tension, -50.0)
        self.assertEqual(manager.config.max_tension, 150.0)

    def test_tension_level_classification(self): pass
        """Test tension level classification."""
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        
        # Test high tension
        self.manager.modify_tension("region1", faction_pair, 60.0)
        tension_data = self.manager.get_tension("region1")
        faction_key = "faction1_faction2"
        self.assertIn("level", tension_data["factions"][faction_key])

    def test_tension_bounds(self): pass
        """Test that tension is properly bounded."""
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        
        # Test upper bound
        self.manager.modify_tension("region1", faction_pair, 200.0)
        tension = self.manager.get_faction_tension("region1", "faction1", "faction2")
        self.assertLessEqual(tension, self.config.max_tension)
        
        # Test lower bound
        self.manager.modify_tension("region1", faction_pair, -200.0)
        tension = self.manager.get_faction_tension("region1", "faction1", "faction2")
        self.assertGreaterEqual(tension, self.config.min_tension)

    def test_multiple_regions(self): pass
        """Test managing tension across multiple regions."""
        faction_pair = {"faction_a": "faction1", "faction_b": "faction2"}
        
        # Add tension in different regions
        self.manager.modify_tension("region1", faction_pair, 20.0)
        self.manager.modify_tension("region2", faction_pair, 30.0)
        
        # Check that regions are independent
        tension1 = self.manager.get_faction_tension("region1", "faction1", "faction2")
        tension2 = self.manager.get_faction_tension("region2", "faction1", "faction2")
        
        self.assertEqual(tension1, self.config.base_tension + 20.0)
        self.assertEqual(tension2, self.config.base_tension + 30.0)

    def test_faction_pair_symmetry(self): pass
        """Test that faction pairs are treated symmetrically."""
        # Add tension using different order
        faction_pair1 = {"faction_a": "faction1", "faction_b": "faction2"}
        faction_pair2 = {"faction_a": "faction2", "faction_b": "faction1"}
        
        self.manager.modify_tension("region1", faction_pair1, 15.0)
        self.manager.modify_tension("region1", faction_pair2, 10.0)
        
        # Should be cumulative
        tension = self.manager.get_faction_tension("region1", "faction1", "faction2")
        self.assertEqual(tension, self.config.base_tension + 25.0)


if __name__ == "__main__": pass
    unittest.main() 