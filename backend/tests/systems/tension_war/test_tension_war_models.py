from backend.systems.shared.config import WarConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import WarConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import WarConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import WarConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import WarConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import WarConfig
from backend.systems.shared.config import TensionConfig
from typing import Any
from typing import Type
"""
Tests for the models in the tension_war system.
"""

import unittest
from datetime import datetime
from typing import Dict, Any

# Direct import of the models module
import sys
import os

# Add parent directory to path if needed
test_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(test_dir, "../../../"))

# Import models directly
from backend.systems.tension_war.models import (
    TensionLevel,
    WarOutcomeType,
    TensionConfig,
    WarConfig,
    WarOutcome,
    WarState,
)


class TestTensionLevel(unittest.TestCase): pass
    """Tests for the TensionLevel enum."""

    def test_values(self): pass
        """Test that the TensionLevel enum has the expected values."""
        self.assertEqual(TensionLevel.ALLIANCE, "alliance")
        self.assertEqual(TensionLevel.FRIENDLY, "friendly")
        self.assertEqual(TensionLevel.NEUTRAL, "neutral")
        self.assertEqual(TensionLevel.RIVALRY, "rivalry")
        self.assertEqual(TensionLevel.HOSTILE, "hostile")
        self.assertEqual(TensionLevel.WAR, "war")

    def test_iteration(self): pass
        """Test iteration over TensionLevel values."""
        levels = list(TensionLevel)
        self.assertEqual(len(levels), 6)  # Check we have all expected values
        self.assertIn(TensionLevel.ALLIANCE, levels)
        self.assertIn(TensionLevel.WAR, levels)


class TestWarOutcomeType(unittest.TestCase): pass
    """Tests for the WarOutcomeType enum."""

    def test_values(self): pass
        """Test that the WarOutcomeType enum has the expected values."""
        self.assertEqual(WarOutcomeType.DECISIVE_VICTORY, "decisive_victory")
        self.assertEqual(WarOutcomeType.VICTORY, "victory")
        self.assertEqual(WarOutcomeType.STALEMATE, "stalemate")
        self.assertEqual(WarOutcomeType.CEASEFIRE, "ceasefire")
        self.assertEqual(WarOutcomeType.WHITE_PEACE, "white_peace")

    def test_iteration(self): pass
        """Test iteration over WarOutcomeType values."""
        outcomes = list(WarOutcomeType)
        self.assertEqual(len(outcomes), 5)  # Check we have all expected values
        self.assertIn(WarOutcomeType.DECISIVE_VICTORY, outcomes)
        self.assertIn(WarOutcomeType.WHITE_PEACE, outcomes)


class TestTensionConfig(unittest.TestCase): pass
    """Tests for the TensionConfig model."""

    def test_default_values(self): pass
        """Test that the TensionConfig has the expected default values."""
        config = TensionConfig()
        self.assertEqual(config.base_tension, 0.0)
        self.assertEqual(config.decay_rate, 0.1)
        self.assertEqual(config.max_tension, 100.0)
        self.assertEqual(config.min_tension, -100.0)
        self.assertEqual(config.faction_impact, 0.5)
        self.assertEqual(config.border_impact, 0.3)
        self.assertEqual(config.event_impact, 0.2)

    def test_custom_values(self): pass
        """Test that TensionConfig accepts custom values."""
        config = TensionConfig(
            base_tension=10.0,
            decay_rate=0.2,
            max_tension=120.0,
            min_tension=-120.0,
            faction_impact=0.6,
            border_impact=0.2,
            event_impact=0.3,
        )
        self.assertEqual(config.base_tension, 10.0)
        self.assertEqual(config.decay_rate, 0.2)
        self.assertEqual(config.max_tension, 120.0)
        self.assertEqual(config.min_tension, -120.0)
        self.assertEqual(config.faction_impact, 0.6)
        self.assertEqual(config.border_impact, 0.2)
        self.assertEqual(config.event_impact, 0.3)


class TestWarConfig(unittest.TestCase): pass
    """Tests for the WarConfig model."""

    def test_default_values(self): pass
        """Test that the WarConfig has the expected default values."""
        config = WarConfig()
        self.assertEqual(config.default_war_duration, 30)
        self.assertEqual(config.exhaustion_rate, 2.0)
        self.assertEqual(config.max_exhaustion, 100.0)
        self.assertEqual(config.min_peace_duration, 7)
        self.assertEqual(config.attrition_factor, 1.5)
        self.assertEqual(config.battle_frequency, 5.0)
        self.assertEqual(config.outcome_weights, {})

    def test_custom_values(self): pass
        """Test that WarConfig accepts custom values."""
        outcome_weights = {
            "decisive_victory": 0.1,
            "victory": 0.3,
            "stalemate": 0.3,
            "ceasefire": 0.2,
            "white_peace": 0.1,
        }

        config = WarConfig(
            default_war_duration=45,
            exhaustion_rate=1.5,
            max_exhaustion=150.0,
            min_peace_duration=14,
            attrition_factor=2.0,
            battle_frequency=3.0,
            outcome_weights=outcome_weights,
        )

        self.assertEqual(config.default_war_duration, 45)
        self.assertEqual(config.exhaustion_rate, 1.5)
        self.assertEqual(config.max_exhaustion, 150.0)
        self.assertEqual(config.min_peace_duration, 14)
        self.assertEqual(config.attrition_factor, 2.0)
        self.assertEqual(config.battle_frequency, 3.0)
        self.assertEqual(config.outcome_weights, outcome_weights)


class TestWarOutcome(unittest.TestCase): pass
    """Tests for the WarOutcome model."""

    def test_required_fields(self): pass
        """Test that the WarOutcome model enforces required fields."""
        with self.assertRaises(ValueError): pass
            # Missing required fields
            WarOutcome()

        # Minimal valid instance
        outcome = WarOutcome(outcome_type=WarOutcomeType.STALEMATE, duration=30)
        self.assertEqual(outcome.outcome_type, WarOutcomeType.STALEMATE)
        self.assertEqual(outcome.duration, 30)

    def test_complete_instance(self): pass
        """Test creating a complete WarOutcome instance."""
        territorial_changes = [
            {
                "region_id": "region1",
                "from_faction": "faction_b",
                "to_faction": "faction_a",
            }
        ]
        resource_transfers = {
            "gold": {"faction_a": 1000, "faction_b": -1000},
            "wood": {"faction_a": 500, "faction_b": -500},
        }
        reputation_changes = {"faction_a": 10, "faction_b": -10, "neutral_faction": -5}
        casualties = {"faction_a": 200, "faction_b": 350}

        outcome = WarOutcome(
            winner_id="faction_a",
            loser_id="faction_b",
            outcome_type=WarOutcomeType.VICTORY,
            territorial_changes=territorial_changes,
            resource_transfers=resource_transfers,
            reputation_changes=reputation_changes,
            tension_changes=-20.0,
            casualties=casualties,
            duration=45,
        )

        self.assertEqual(outcome.winner_id, "faction_a")
        self.assertEqual(outcome.loser_id, "faction_b")
        self.assertEqual(outcome.outcome_type, WarOutcomeType.VICTORY)
        self.assertEqual(outcome.territorial_changes, territorial_changes)
        self.assertEqual(outcome.resource_transfers, resource_transfers)
        self.assertEqual(outcome.reputation_changes, reputation_changes)
        self.assertEqual(outcome.tension_changes, -20.0)
        self.assertEqual(outcome.casualties, casualties)
        self.assertEqual(outcome.duration, 45)


class TestWarState(unittest.TestCase): pass
    """Tests for the WarState model."""

    def test_required_fields(self): pass
        """Test that the WarState model enforces required fields."""
        with self.assertRaises(ValueError): pass
            # Missing required fields
            WarState()

        # Minimal valid instance
        now = datetime.now()
        state = WarState(
            id="war_1",
            faction_a_id="faction_a", 
            faction_b_id="faction_b", 
            start_date=now
        )

        self.assertEqual(state.id, "war_1")
        self.assertEqual(state.faction_a_id, "faction_a")
        self.assertEqual(state.faction_b_id, "faction_b")
        self.assertEqual(state.start_date, now)
        self.assertEqual(state.exhaustion_a, 0.0)
        self.assertEqual(state.exhaustion_b, 0.0)
        self.assertEqual(state.battles, [])
        self.assertEqual(state.current_peace_offer, None)
        self.assertEqual(state.disputed_regions, [])
        self.assertEqual(state.is_active, True)

    def test_complete_instance(self): pass
        """Test creating a complete WarState instance."""
        now = datetime.now()
        battles = [
            {
                "id": "battle1",
                "date": now,
                "location": "disputed_region",
                "winner": "faction_a",
                "casualties_a": 50,
                "casualties_b": 75,
            }
        ]
        peace_offer = {
            "id": "offer1",
            "offering_faction": "faction_b",
            "terms": {"territory_concessions": ["region1"]},
        }
        disputed_regions = ["region1", "region2"]

        state = WarState(
            id="war_1",
            faction_a_id="faction_a",
            faction_b_id="faction_b",
            start_date=now,
            exhaustion_a=25.0,
            exhaustion_b=40.0,
            battles=battles,
            current_peace_offer=peace_offer,
            disputed_regions=disputed_regions,
            is_active=True,
        )

        self.assertEqual(state.id, "war_1")
        self.assertEqual(state.faction_a_id, "faction_a")
        self.assertEqual(state.faction_b_id, "faction_b")
        self.assertEqual(state.start_date, now)
        self.assertEqual(state.exhaustion_a, 25.0)
        self.assertEqual(state.exhaustion_b, 40.0)
        self.assertEqual(state.battles, battles)
        self.assertEqual(state.current_peace_offer, peace_offer)
        self.assertEqual(state.disputed_regions, disputed_regions)
        self.assertEqual(state.is_active, True)


if __name__ == "__main__": pass
    unittest.main()
