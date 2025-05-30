from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import uuid
from typing import Any, Type, List, Dict, Optional, Union

from backend.systems.tension_war.services.diplomatic_manager import DiplomaticManager
from backend.systems.tension_war.models.enums import (
    SanctionType, 
    PeaceBrokeringStatus,
    TensionLevel
)
from backend.systems.tension_war.models.config import TensionConfig


class TestDiplomaticManager: pass
    """Test the DiplomaticManager class."""

    @pytest.fixture
    def manager(self): pass
        """Create a DiplomaticManager instance."""
        return DiplomaticManager()

    @pytest.fixture
    def custom_config(self): pass
        """Create a custom TensionConfig."""
        return TensionConfig(
            max_tension=100,
            min_tension=0,
            decay_rate=0.1,
            war_threshold=80
        )

    @pytest.fixture
    def manager_with_config(self, custom_config): pass
        """Create a DiplomaticManager with custom config."""
        return DiplomaticManager(custom_config)

    @pytest.fixture
    def war_data(self): pass
        """Sample war data."""
        return {
            "id": "war_123",
            "faction_a_id": "faction_alpha",
            "faction_b_id": "faction_beta",
            "status": "active"
        }

    @pytest.fixture
    def warring_factions(self): pass
        """Sample warring factions data."""
        return {
            "faction_a_id": "faction_alpha",
            "faction_b_id": "faction_beta"
        }

    @pytest.fixture
    def peace_terms(self): pass
        """Sample peace terms."""
        return {
            "territory_changes": {"region_1": "faction_alpha"},
            "reparations": {"faction_beta": 10000},
            "trade_restrictions": [],
            "military_limitations": {"faction_beta": {"max_army_size": 5000}},
            "duration_years": 10
        }

    @pytest.fixture
    def incentives(self): pass
        """Sample broker incentives."""
        return {
            "economic_aid": 5000,
            "trade_agreements": ["faction_alpha", "faction_beta"],
            "security_guarantees": True
        }

    def test_init_default_config(self): pass
        """Test DiplomaticManager initialization with default config."""
        manager = DiplomaticManager()
        assert manager.config is not None
        assert hasattr(manager, 'event_dispatcher')
        assert manager._peace_brokering_attempts == {}
        assert manager._sanctions == {}
        assert manager._diplomatic_events == {}

    def test_init_custom_config(self, custom_config): pass
        """Test DiplomaticManager initialization with custom config."""
        manager = DiplomaticManager(custom_config)
        assert manager.config == custom_config

    @patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance')
    def test_broker_peace_success(self, mock_acceptance, manager, warring_factions, peace_terms, incentives): pass
        """Test successful peace brokering."""
        # Mock acceptance chances
        mock_acceptance.side_effect = [0.7, 0.6]  # faction_a, faction_b

        result = manager.broker_peace(
            war_id="war_123",
            broker_faction_id="broker_faction",
            warring_factions=warring_factions,
            proposed_terms=peace_terms,
            incentives=incentives
        )

        # Verify result structure
        assert "id" in result
        assert result["war_id"] == "war_123"
        assert result["broker_faction_id"] == "broker_faction"
        assert result["faction_a_id"] == "faction_alpha"
        assert result["faction_b_id"] == "faction_beta"
        assert result["proposed_terms"] == peace_terms
        assert result["incentives"] == incentives
        assert result["status"] == PeaceBrokeringStatus.PROPOSED.value
        assert "acceptance_chance" in result
        assert len(result["history"]) == 1

        # Verify storage
        assert result["id"] in manager._peace_brokering_attempts

    @patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance')
    def test_broker_peace_without_incentives(self, mock_acceptance, manager, warring_factions, peace_terms): pass
        """Test peace brokering without incentives."""
        mock_acceptance.return_value = 0.5

        result = manager.broker_peace(
            war_id="war_123",
            broker_faction_id="broker_faction",
            warring_factions=warring_factions,
            proposed_terms=peace_terms
        )

        assert result["incentives"] == {}

    def test_respond_to_peace_brokering_accept(self, manager, warring_factions, peace_terms): pass
        """Test accepting a peace brokering attempt."""
        # Create peace attempt first
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance', return_value=0.7): pass
            attempt = manager.broker_peace(
                war_id="war_123",
                broker_faction_id="broker_faction",
                warring_factions=warring_factions,
                proposed_terms=peace_terms
            )

        # Respond with acceptance
        result = manager.respond_to_peace_brokering(
            attempt_id=attempt["id"],
            faction_id="faction_alpha",
            response="accept",
            response_details={"reason": "Terms are acceptable"}
        )

        assert "faction_alpha" in result["responses"]
        assert result["responses"]["faction_alpha"]["response"] == "accept"
        assert len(result["history"]) == 2

    def test_respond_to_peace_brokering_counter(self, manager, warring_factions, peace_terms): pass
        """Test countering a peace brokering attempt."""
        # Create peace attempt first
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance', return_value=0.7): pass
            attempt = manager.broker_peace(
                war_id="war_123",
                broker_faction_id="broker_faction",
                warring_factions=warring_factions,
                proposed_terms=peace_terms
            )

        counter_terms = {
            "territory_changes": {},
            "reparations": {"faction_beta": 5000},  # Reduced reparations
        }

        result = manager.respond_to_peace_brokering(
            attempt_id=attempt["id"],
            faction_id="faction_beta",
            response="counter",
            counter_terms=counter_terms
        )

        assert result["responses"]["faction_beta"]["response"] == "counter"
        assert result["responses"]["faction_beta"]["counter_terms"] == counter_terms
        assert result["status"] == PeaceBrokeringStatus.COUNTERED.value

    def test_respond_to_peace_brokering_reject(self, manager, warring_factions, peace_terms): pass
        """Test rejecting a peace brokering attempt."""
        # Create peace attempt first
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance', return_value=0.7): pass
            attempt = manager.broker_peace(
                war_id="war_123",
                broker_faction_id="broker_faction",
                warring_factions=warring_factions,
                proposed_terms=peace_terms
            )

        result = manager.respond_to_peace_brokering(
            attempt_id=attempt["id"],
            faction_id="faction_alpha",
            response="reject",
            response_details={"reason": "Unacceptable terms"}
        )

        assert result["responses"]["faction_alpha"]["response"] == "reject"
        assert result["status"] == PeaceBrokeringStatus.REJECTED.value

    def test_respond_to_peace_brokering_both_accept(self, manager, warring_factions, peace_terms): pass
        """Test when both factions accept."""
        # Create peace attempt first
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance', return_value=0.7): pass
            attempt = manager.broker_peace(
                war_id="war_123",
                broker_faction_id="broker_faction",
                warring_factions=warring_factions,
                proposed_terms=peace_terms
            )

        # First faction accepts
        manager.respond_to_peace_brokering(
            attempt_id=attempt["id"],
            faction_id="faction_alpha",
            response="accept"
        )

        # Second faction accepts
        result = manager.respond_to_peace_brokering(
            attempt_id=attempt["id"],
            faction_id="faction_beta",
            response="accept"
        )

        assert result["status"] == PeaceBrokeringStatus.ACCEPTED.value

    def test_respond_to_peace_brokering_invalid_attempt(self, manager): pass
        """Test responding to non-existent attempt."""
        with pytest.raises(ValueError, match="Peace brokering attempt .* not found"): pass
            manager.respond_to_peace_brokering(
                attempt_id="invalid_id",
                faction_id="faction_alpha",
                response="accept"
            )

    def test_respond_to_peace_brokering_wrong_faction(self, manager, warring_factions, peace_terms): pass
        """Test responding with faction not involved in war."""
        # Create peace attempt first
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance', return_value=0.7): pass
            attempt = manager.broker_peace(
                war_id="war_123",
                broker_faction_id="broker_faction",
                warring_factions=warring_factions,
                proposed_terms=peace_terms
            )

        with pytest.raises(ValueError, match="Faction .* is not involved"): pass
            manager.respond_to_peace_brokering(
                attempt_id=attempt["id"],
                faction_id="uninvolved_faction",
                response="accept"
            )

    def test_get_peace_brokering_attempt(self, manager, warring_factions, peace_terms): pass
        """Test retrieving a peace brokering attempt."""
        # Create peace attempt first
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance', return_value=0.7): pass
            attempt = manager.broker_peace(
                war_id="war_123",
                broker_faction_id="broker_faction",
                warring_factions=warring_factions,
                proposed_terms=peace_terms
            )

        result = manager.get_peace_brokering_attempt(attempt["id"])
        assert result is not None
        assert result["id"] == attempt["id"]

        # Test non-existent attempt
        result = manager.get_peace_brokering_attempt("invalid_id")
        assert result is None

    def test_get_peace_brokering_attempts_by_war(self, manager, warring_factions, peace_terms): pass
        """Test getting peace attempts by war ID."""
        # Create multiple attempts for same war
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance', return_value=0.7): pass
            attempt1 = manager.broker_peace(
                war_id="war_123",
                broker_faction_id="broker_1",
                warring_factions=warring_factions,
                proposed_terms=peace_terms
            )
            attempt2 = manager.broker_peace(
                war_id="war_123",
                broker_faction_id="broker_2",
                warring_factions=warring_factions,
                proposed_terms=peace_terms
            )

        results = manager.get_peace_brokering_attempts_by_war("war_123")
        assert len(results) == 2
        attempt_ids = [r["id"] for r in results]
        assert attempt1["id"] in attempt_ids
        assert attempt2["id"] in attempt_ids

        # Test non-existent war
        results = manager.get_peace_brokering_attempts_by_war("invalid_war")
        assert len(results) == 0

    def test_get_peace_brokering_attempts_by_broker(self, manager, warring_factions, peace_terms): pass
        """Test getting peace attempts by broker faction."""
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance', return_value=0.7): pass
            attempt = manager.broker_peace(
                war_id="war_123",
                broker_faction_id="broker_faction",
                warring_factions=warring_factions,
                proposed_terms=peace_terms
            )

        results = manager.get_peace_brokering_attempts_by_broker("broker_faction")
        assert len(results) == 1
        assert results[0]["id"] == attempt["id"]

    def test_get_peace_brokering_attempts_by_faction(self, manager, warring_factions, peace_terms): pass
        """Test getting peace attempts by involved faction."""
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_peace_acceptance_chance', return_value=0.7): pass
            attempt = manager.broker_peace(
                war_id="war_123",
                broker_faction_id="broker_faction",
                warring_factions=warring_factions,
                proposed_terms=peace_terms
            )

        # Test for faction_alpha
        results = manager.get_peace_brokering_attempts_by_faction("faction_alpha")
        assert len(results) == 1
        assert results[0]["id"] == attempt["id"]

        # Test for faction_beta
        results = manager.get_peace_brokering_attempts_by_faction("faction_beta")
        assert len(results) == 1
        assert results[0]["id"] == attempt["id"]

    @patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_sanction_impact')
    def test_apply_economic_sanctions(self, mock_impact, manager): pass
        """Test applying economic sanctions."""
        mock_impact.return_value = {
            "economic_impact": -0.15,
            "reputation_impact": -0.1,
            "effects": []
        }

        result = manager.apply_economic_sanctions(
            faction_a_id="sanctioning_faction",
            faction_b_id="target_faction",
            sanction_type=SanctionType.TRADE_EMBARGO.value,
            duration_days=90,
            reason="Trade violations"
        )

        # Verify the mock was called with correct parameters
        mock_impact.assert_called_once_with(
            "sanctioning_faction",
            "target_faction", 
            SanctionType.TRADE_EMBARGO.value,
            3  # 90 days = 3 months
        )

        assert "id" in result
        assert result["sanctioning_faction_id"] == "sanctioning_faction"
        assert result["target_faction_id"] == "target_faction"
        assert result["sanction_type"] == SanctionType.TRADE_EMBARGO.value
        assert result["duration_days"] == 90
        assert result["reason"] == "Trade violations"
        assert result["status"] == "active"
        assert "impact" in result

        # Verify storage
        assert result["id"] in manager._sanctions

    @patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_sanction_impact')
    def test_apply_economic_sanctions_default_duration(self, mock_impact, manager): pass
        """Test applying sanctions with default duration."""
        mock_impact.return_value = {"economic_impact": -0.1, "effects": []}

        result = manager.apply_economic_sanctions(
            faction_a_id="sanctioning_faction",
            faction_b_id="target_faction"
        )

        # Should use default 365 days = 12 months
        mock_impact.assert_called_once_with(
            "sanctioning_faction",
            "target_faction",
            SanctionType.FULL.value,
            12  # 365 days = 12 months
        )
        
        assert result["duration_days"] == 365  # Default 1 year

    def test_lift_economic_sanctions(self, manager): pass
        """Test lifting economic sanctions."""
        # Create sanction first
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_sanction_impact', return_value={}): pass
            sanction = manager.apply_economic_sanctions(
                faction_a_id="sanctioning_faction",
                faction_b_id="target_faction"
            )

        result = manager.lift_economic_sanctions(
            sanction_id=sanction["id"],
            reason="Diplomatic resolution"
        )

        assert result["status"] == "lifted"
        assert result["lifted_reason"] == "Diplomatic resolution"
        assert "lifted_at" in result

    def test_lift_economic_sanctions_not_found(self, manager): pass
        """Test lifting non-existent sanctions."""
        with pytest.raises(ValueError, match="Sanction .* not found"): pass
            manager.lift_economic_sanctions("invalid_id")

    def test_lift_economic_sanctions_already_lifted(self, manager): pass
        """Test lifting already lifted sanctions."""
        # Create and lift sanction
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_sanction_impact', return_value={}): pass
            sanction = manager.apply_economic_sanctions(
                faction_a_id="sanctioning_faction",
                faction_b_id="target_faction"
            )
            manager.lift_economic_sanctions(sanction["id"])

        with pytest.raises(ValueError, match="Sanction .* is not active"): pass
            manager.lift_economic_sanctions(sanction["id"])

    def test_get_sanction(self, manager): pass
        """Test getting a specific sanction."""
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_sanction_impact', return_value={}): pass
            sanction = manager.apply_economic_sanctions(
                faction_a_id="sanctioning_faction",
                faction_b_id="target_faction"
            )

        result = manager.get_sanction(sanction["id"])
        assert result is not None
        assert result["id"] == sanction["id"]

        # Test non-existent sanction
        result = manager.get_sanction("invalid_id")
        assert result is None

    def test_get_sanctions_between_factions(self, manager): pass
        """Test getting sanctions between specific factions."""
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_sanction_impact', return_value={}): pass
            sanction = manager.apply_economic_sanctions(
                faction_a_id="faction_a",
                faction_b_id="faction_b"
            )

        # Test active sanctions only
        results = manager.get_sanctions_between_factions("faction_a", "faction_b", active_only=True)
        assert len(results) == 1
        assert results[0]["id"] == sanction["id"]

        # Lift sanction and test with active_only=False
        manager.lift_economic_sanctions(sanction["id"])
        results = manager.get_sanctions_between_factions("faction_a", "faction_b", active_only=False)
        assert len(results) == 1

        results = manager.get_sanctions_between_factions("faction_a", "faction_b", active_only=True)
        assert len(results) == 0

    def test_get_sanctions_by_faction(self, manager): pass
        """Test getting sanctions involving a specific faction."""
        with patch('backend.systems.tension_war.utils.diplomatic_utils.calculate_sanction_impact', return_value={}): pass
            # Faction as sanctioner
            sanction1 = manager.apply_economic_sanctions(
                faction_a_id="test_faction",
                faction_b_id="other_faction"
            )
            # Faction as target
            sanction2 = manager.apply_economic_sanctions(
                faction_a_id="other_faction",
                faction_b_id="test_faction"
            )

        results = manager.get_sanctions_by_faction("test_faction")
        assert len(results) == 2
        sanction_ids = [s["id"] for s in results]
        assert sanction1["id"] in sanction_ids
        assert sanction2["id"] in sanction_ids

    def test_record_diplomatic_event(self, manager): pass
        """Test recording a diplomatic event."""
        event_data = {
            "ambassador_name": "John Diplomat",
            "meeting_location": "Neutral Territory",
            "outcome": "Agreement reached"
        }

        result = manager.record_diplomatic_event(
            event_type="diplomatic_meeting",
            factions=["faction_a", "faction_b"],
            event_data=event_data
        )

        assert "id" in result
        assert result["event_type"] == "diplomatic_meeting"
        assert result["factions"] == ["faction_a", "faction_b"]
        assert result["data"] == event_data  # Note: stored as "data", not "event_data"
        assert "timestamp" in result

        # Verify storage
        assert result["id"] in manager._diplomatic_events

    def test_get_diplomatic_events_all(self, manager): pass
        """Test getting all diplomatic events."""
        # Record multiple events
        manager.record_diplomatic_event("meeting", ["faction_a", "faction_b"], {})
        manager.record_diplomatic_event("treaty", ["faction_c", "faction_d"], {})

        results = manager.get_diplomatic_events()
        assert len(results) == 2

    def test_get_diplomatic_events_by_faction(self, manager): pass
        """Test getting events by faction."""
        manager.record_diplomatic_event("meeting", ["faction_a", "faction_b"], {})
        manager.record_diplomatic_event("treaty", ["faction_c", "faction_d"], {})

        results = manager.get_diplomatic_events(faction_id="faction_a")
        assert len(results) == 1
        assert "faction_a" in results[0]["factions"]

    def test_get_diplomatic_events_by_type(self, manager): pass
        """Test getting events by type."""
        manager.record_diplomatic_event("meeting", ["faction_a", "faction_b"], {})
        manager.record_diplomatic_event("treaty", ["faction_c", "faction_d"], {})

        results = manager.get_diplomatic_events(event_type="meeting")
        assert len(results) == 1
        assert results[0]["event_type"] == "meeting"

    def test_get_diplomatic_events_by_time_range(self, manager): pass
        """Test getting events by time range."""
        now = datetime.utcnow()
        start_time = now - timedelta(hours=1)
        end_time = now + timedelta(hours=1)

        manager.record_diplomatic_event("meeting", ["faction_a", "faction_b"], {})

        results = manager.get_diplomatic_events(start_time=start_time, end_time=end_time)
        assert len(results) == 1

        # Test outside time range
        old_start = now - timedelta(days=2)
        old_end = now - timedelta(days=1)
        results = manager.get_diplomatic_events(start_time=old_start, end_time=old_end)
        assert len(results) == 0 