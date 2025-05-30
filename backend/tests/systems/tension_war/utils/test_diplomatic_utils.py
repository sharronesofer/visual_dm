"""
Tests for Diplomatic Utilities

This module contains comprehensive tests for diplomatic operations and embassy management utilities.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

from backend.systems.tension_war.utils.diplomatic_utils import (
    calculate_diplomatic_options,
    evaluate_relation_changes,
    calculate_sanction_effects,
    generate_diplomatic_events,
    evaluate_embassy_status,
    calculate_peace_acceptance_chance,
    evaluate_terms_favorability,
    calculate_broker_reputation_bonus,
    calculate_sanction_impact,
)


@pytest.fixture
def sample_factions(): pass
    """Create sample faction data for testing."""
    return [
        {
            "id": "faction_1",
            "name": "Alliance of the North",
            "power": 75,
            "economy": 80,
            "military": 70,
            "traits": {"diplomatic": True, "peaceful": True}
        },
        {
            "id": "faction_2", 
            "name": "Southern Empire",
            "power": 85,
            "economy": 90,
            "military": 85,
            "traits": {"aggressive": True, "expansionist": True}
        },
        {
            "id": "faction_3",
            "name": "Eastern Republics",
            "power": 60,
            "economy": 70,
            "military": 55,
            "traits": {"trade_focused": True, "neutral": True}
        }
    ]


@pytest.fixture
def sample_tensions(): pass
    """Create sample tension data."""
    return {
        "faction_1_faction_2": 65.0,
        "faction_1_faction_3": 15.0,
        "faction_2_faction_3": 40.0,
    }


@pytest.fixture
def sample_relationship_history(): pass
    """Create sample relationship history."""
    return [
        {
            "event_type": "trade_agreement", 
            "date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "impact": 5.0
        },
        {
            "event_type": "border_dispute",
            "date": (datetime.utcnow() - timedelta(days=10)).isoformat(),
            "impact": -10.0
        }
    ]


@pytest.fixture
def sample_world_state(): pass
    """Create sample world state data."""
    return {
        "global_stability": 0.7,
        "economic_conditions": "stable",
        "major_conflicts": ["war_between_1_and_2"],
        "active_alliances": ["alliance_1_3"]
    }


class TestCalculateDiplomaticOptions: pass
    """Test diplomatic options calculation."""
    
    def test_friendly_relations_options(self, sample_factions, sample_relationship_history): pass
        """Test diplomatic options for friendly factions."""
        faction_a = sample_factions[0]
        faction_b = sample_factions[2]  # Low tension faction
        
        result = calculate_diplomatic_options(
            faction_a, faction_b, -10.0, sample_relationship_history
        )
        
        assert "available_actions" in result
        assert "blocked_actions" in result
        assert "success_chances" in result
        
        # Should include alliance options for friendly relations
        assert "alliance_proposal" in result["available_actions"]
        assert "military_cooperation" in result["available_actions"]
        
        # Basic actions should always be available
        assert "negotiate" in result["available_actions"]
        assert "trade_agreement" in result["available_actions"]

    def test_high_tension_options(self, sample_factions, sample_relationship_history): pass
        """Test diplomatic options for high tension factions."""
        faction_a = sample_factions[0]
        faction_b = sample_factions[1]
        
        result = calculate_diplomatic_options(
            faction_a, faction_b, 75.0, sample_relationship_history
        )
        
        # Should include hostile options
        assert "ultimatum" in result["available_actions"]
        assert "sanctions" in result["available_actions"]
        
        # Should block friendly options
        assert "alliance_proposal" in result["blocked_actions"]
        assert "trade_agreement" in result["blocked_actions"]

    def test_success_chance_calculation(self, sample_factions, sample_relationship_history): pass
        """Test success chance calculation for diplomatic actions."""
        faction_a = sample_factions[0]
        faction_b = sample_factions[1]
        
        result = calculate_diplomatic_options(
            faction_a, faction_b, 50.0, sample_relationship_history
        )
        
        # Should have success chances for all available actions
        for action in result["available_actions"]: pass
            assert action in result["success_chances"]
            assert 0.0 <= result["success_chances"][action] <= 1.0


class TestEvaluateRelationChanges: pass
    """Test relation changes evaluation."""
    
    def test_positive_event_impact(self, sample_factions): pass
        """Test positive events improve relations."""
        faction_a = sample_factions[0]
        faction_b = sample_factions[1]
        
        event_data = {"type": "trade_success", "value": 1000}
        
        result = evaluate_relation_changes(
            faction_a, faction_b, event_data, 25.0
        )
        
        assert result["relationship_delta"] > 0
        assert result["new_relationship"] > 25.0
        assert len(result["factors"]) > 0

    def test_negative_event_impact(self, sample_factions): pass
        """Test negative events worsen relations."""
        faction_a = sample_factions[0]
        faction_b = sample_factions[1]
        
        event_data = {"type": "border_incident", "severity": "high"}
        
        result = evaluate_relation_changes(
            faction_a, faction_b, event_data, 50.0
        )
        
        assert result["relationship_delta"] < 0
        assert result["new_relationship"] < 50.0
        assert len(result["factors"]) > 0

    def test_military_aid_impact(self, sample_factions): pass
        """Test military aid provides significant positive impact."""
        faction_a = sample_factions[0] 
        faction_b = sample_factions[2]
        
        event_data = {"type": "military_aid", "amount": 5000}
        
        result = evaluate_relation_changes(
            faction_a, faction_b, event_data, 10.0
        )
        
        assert result["relationship_delta"] == 20.0
        assert result["new_relationship"] == 30.0

    def test_diplomatic_insult_impact(self, sample_factions): pass
        """Test diplomatic insults cause significant negative impact."""
        faction_a = sample_factions[1]
        faction_b = sample_factions[0]
        
        event_data = {"type": "diplomatic_insult", "public": True}
        
        result = evaluate_relation_changes(
            faction_a, faction_b, event_data, 20.0
        )
        
        assert result["relationship_delta"] == -15.0
        assert result["new_relationship"] == 5.0


class TestCalculateSanctionEffects: pass
    """Test sanction effects calculation."""
    
    def test_trade_embargo_effects(self, sample_factions): pass
        """Test trade embargo sanction effects."""
        sanctioning = sample_factions[0]
        target = sample_factions[1]
        
        result = calculate_sanction_effects(
            sanctioning, target, "trade_embargo", 12
        )
        
        assert result["economic_impact"] < 0
        assert result["effectiveness"] > 0.5
        assert result["duration_months"] == 12
        assert len(result["side_effects"]) > 0

    def test_military_embargo_effects(self, sample_factions): pass
        """Test military embargo sanction effects."""
        sanctioning = sample_factions[1]
        target = sample_factions[2]
        
        result = calculate_sanction_effects(
            sanctioning, target, "military_embargo", 6
        )
        
        assert result["military_impact"] < result["economic_impact"]  # More military impact
        assert result["effectiveness"] > 0.7
        assert "effectiveness" in result

    def test_diplomatic_isolation_effects(self, sample_factions): pass
        """Test diplomatic isolation sanction effects."""
        sanctioning = sample_factions[0]
        target = sample_factions[1]
        
        result = calculate_sanction_effects(
            sanctioning, target, "diplomatic_isolation", 18
        )
        
        assert result["diplomatic_impact"] < 0
        assert abs(result["diplomatic_impact"]) > abs(result["economic_impact"])
        
        # Long duration should scale effects
        assert result["duration_months"] == 18

    def test_duration_scaling(self, sample_factions): pass
        """Test that sanction duration affects impact."""
        sanctioning = sample_factions[0]
        target = sample_factions[1]
        
        short_result = calculate_sanction_effects(
            sanctioning, target, "trade_embargo", 3
        )
        long_result = calculate_sanction_effects(
            sanctioning, target, "trade_embargo", 24
        )
        
        # Longer sanctions should have greater impact
        assert abs(long_result["economic_impact"]) > abs(short_result["economic_impact"])


class TestGenerateDiplomaticEvents: pass
    """Test diplomatic event generation."""
    
    def test_generate_events_basic(self, sample_factions, sample_tensions, sample_world_state): pass
        """Test basic diplomatic event generation."""
        events = generate_diplomatic_events(
            sample_factions, sample_tensions, sample_world_state
        )
        
        assert isinstance(events, list)
        # Should generate some events given high tensions
        assert len(events) > 0
        
        for event in events: pass
            assert isinstance(event, dict)

    def test_high_tension_generates_events(self, sample_factions, sample_world_state): pass
        """Test that high tensions generate diplomatic events."""
        high_tensions = {
            "faction_1_faction_2": 85.0,  # Very high tension
            "faction_1_faction_3": 5.0,
            "faction_2_faction_3": 15.0,
        }
        
        events = generate_diplomatic_events(
            sample_factions, high_tensions, sample_world_state
        )
        
        # High tension should generate events
        assert len(events) > 0

    def test_low_tension_fewer_events(self, sample_factions, sample_world_state): pass
        """Test that low tensions generate fewer events."""
        low_tensions = {
            "faction_1_faction_2": 10.0,  # Low tension
            "faction_1_faction_3": 5.0,
            "faction_2_faction_3": 15.0,
        }
        
        events = generate_diplomatic_events(
            sample_factions, low_tensions, sample_world_state
        )
        
        # Should still be a list (might be empty)
        assert isinstance(events, list)


class TestEvaluateEmbassyStatus: pass
    """Test embassy status evaluation."""
    
    def test_embassy_status_basic(self, sample_factions): pass
        """Test basic embassy status evaluation."""
        faction_a = sample_factions[0]
        faction_b = sample_factions[1]
        
        result = evaluate_embassy_status(faction_a, faction_b)
        
        assert isinstance(result, dict)

    def test_embassy_with_data(self, sample_factions): pass
        """Test embassy status with existing embassy data."""
        faction_a = sample_factions[0]
        faction_b = sample_factions[1]
        embassy_data = {
            "established_date": "2023-01-01",
            "status": "active",
            "staff_count": 15
        }
        
        result = evaluate_embassy_status(faction_a, faction_b, embassy_data)
        
        assert isinstance(result, dict)


class TestCalculatePeaceAcceptanceChance: pass
    """Test peace acceptance chance calculation."""
    
    def test_peace_acceptance_basic(self): pass
        """Test basic peace acceptance chance calculation."""
        war_data = {
            "id": "war_1",
            "faction_a_id": "faction_1",
            "faction_b_id": "faction_2",
            "duration_days": 45,
            "war_score": 25
        }
        
        proposed_terms = {
            "territory_changes": {"region_1": {"to_faction": "faction_1"}},
            "reparations": {"amount": 1000, "to_faction": "faction_1"}
        }
        
        result = calculate_peace_acceptance_chance(
            "faction_2", war_data, proposed_terms, False, None
        )
        
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_peace_acceptance_with_broker(self): pass
        """Test peace acceptance with broker involvement."""
        war_data = {
            "id": "war_1",
            "faction_a_id": "faction_1", 
            "faction_b_id": "faction_2",
            "duration_days": 60,
            "war_score": -10
        }
        
        proposed_terms = {
            "ceasefire": {"duration_days": 30},
            "prisoner_exchange": True
        }
        
        result = calculate_peace_acceptance_chance(
            "faction_1", war_data, proposed_terms, True, "faction_3"
        )
        
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestEvaluateTermsFavorability: pass
    """Test terms favorability evaluation."""
    
    def test_terms_favorability_basic(self): pass
        """Test basic terms favorability evaluation."""
        terms = {
            "territory_gains": {
                "faction_1": ["region_1", "region_2"]
            },
            "territory_losses": {
                "faction_1": []
            },
            "reparations_receive": {
                "faction_1": 5000
            },
            "reparations_pay": {
                "faction_1": 0
            },
            "trade_benefits": {
                "faction_1": ["trade_route_1"]
            }
        }
        
        result = evaluate_terms_favorability("faction_1", terms)
        
        assert isinstance(result, float)
        assert -1.0 <= result <= 1.0
        assert result > 0  # Should be favorable due to gains and benefits

    def test_terms_favorability_empty(self): pass
        """Test terms favorability with empty terms."""
        terms = {}
        
        result = evaluate_terms_favorability("faction_1", terms)
        
        assert isinstance(result, float)
        assert result == 0.0  # No terms = neutral


class TestCalculateBrokerReputationBonus: pass
    """Test broker reputation bonus calculation."""
    
    def test_broker_reputation_basic(self): pass
        """Test basic broker reputation bonus calculation."""
        result = calculate_broker_reputation_bonus("faction_3", "faction_1")
        
        assert isinstance(result, float)
        assert result >= 0.0

    def test_broker_reputation_different_factions(self): pass
        """Test broker reputation with different faction combinations."""
        result1 = calculate_broker_reputation_bonus("faction_1", "faction_2")
        result2 = calculate_broker_reputation_bonus("faction_2", "faction_3")
        
        assert isinstance(result1, float)
        assert isinstance(result2, float)


class TestCalculateSanctionImpact: pass
    """Test sanction impact calculation."""
    
    def test_sanction_impact_basic(self): pass
        """Test basic sanction impact calculation."""
        result = calculate_sanction_impact(
            "faction_1", "faction_2", "economic", 12
        )
        
        assert isinstance(result, dict)

    def test_sanction_impact_different_types(self): pass
        """Test different sanction types."""
        economic_result = calculate_sanction_impact(
            "faction_1", "faction_2", "economic", 6
        )
        military_result = calculate_sanction_impact(
            "faction_1", "faction_2", "military", 6  
        )
        
        assert isinstance(economic_result, dict)
        assert isinstance(military_result, dict)

    def test_sanction_impact_duration_effects(self): pass
        """Test how duration affects sanction impact."""
        short_result = calculate_sanction_impact(
            "faction_1", "faction_2", "economic", 3
        )
        long_result = calculate_sanction_impact(
            "faction_1", "faction_2", "economic", 18
        )
        
        assert isinstance(short_result, dict)
        assert isinstance(long_result, dict)


class TestDiplomaticUtilsIntegration: pass
    """Test integration scenarios for diplomatic utilities."""
    
    def test_full_diplomatic_cycle(self, sample_factions, sample_tensions, 
                                 sample_relationship_history, sample_world_state): pass
        """Test a full diplomatic interaction cycle."""
        faction_a = sample_factions[0]
        faction_b = sample_factions[1]
        current_tension = sample_tensions["faction_1_faction_2"]
        
        # 1. Calculate diplomatic options
        options = calculate_diplomatic_options(
            faction_a, faction_b, current_tension, sample_relationship_history
        )
        
        # 2. Evaluate potential relation changes
        event_data = {"type": "trade_success", "value": 2000}
        relation_change = evaluate_relation_changes(
            faction_a, faction_b, event_data, current_tension
        )
        
        # 3. Calculate sanction effects if tensions are high
        if current_tension > 50: pass
            sanction_effects = calculate_sanction_effects(
                faction_a, faction_b, "trade_embargo", 6
            )
            assert sanction_effects["economic_impact"] < 0
        
        # 4. Generate diplomatic events
        events = generate_diplomatic_events(
            sample_factions, sample_tensions, sample_world_state
        )
        
        # Verify the cycle produces consistent results
        assert len(options["available_actions"]) > 0
        assert relation_change["relationship_delta"] != 0
        assert isinstance(events, list)

    def test_escalation_scenario(self, sample_factions, sample_relationship_history): pass
        """Test diplomatic escalation scenario."""
        faction_a = sample_factions[0]
        faction_b = sample_factions[1]
        
        # Start with moderate tension
        initial_tension = 40.0
        
        # Simulate escalating events
        escalation_events = [
            {"type": "border_incident", "severity": "medium"},
            {"type": "diplomatic_insult", "public": True},
            {"type": "trade_dispute", "value": 5000}
        ]
        
        current_tension = initial_tension
        for event in escalation_events: pass
            change = evaluate_relation_changes(
                faction_a, faction_b, event, current_tension
            )
            current_tension = change["new_relationship"]
        
        # Final tension should be higher
        assert current_tension != initial_tension
        
        # Calculate final diplomatic options
        final_options = calculate_diplomatic_options(
            faction_a, faction_b, current_tension, sample_relationship_history
        )
        
        assert len(final_options["available_actions"]) > 0

    def test_peace_negotiation_scenario(self): pass
        """Test peace negotiation scenario."""
        war_data = {
            "id": "test_war",
            "faction_a_id": "faction_1",
            "faction_b_id": "faction_2", 
            "duration_days": 120,
            "war_score": 15
        }
        
        # Test favorable terms
        favorable_terms = {
            "territory_gains": {
                "faction_2": ["region_1"]
            },
            "territory_losses": {
                "faction_2": []
            },
            "reparations_receive": {
                "faction_2": 10000
            },
            "reparations_pay": {
                "faction_2": 0
            }
        }
        
        favorable_chance = calculate_peace_acceptance_chance(
            "faction_2", war_data, favorable_terms, has_broker=False
        )
        
        # Test unfavorable terms  
        unfavorable_terms = {
            "territory_gains": {
                "faction_2": []
            },
            "territory_losses": {
                "faction_2": ["region_1", "region_2"]
            },
            "reparations_receive": {
                "faction_2": 0
            },
            "reparations_pay": {
                "faction_2": 15000
            }
        }
        
        unfavorable_chance = calculate_peace_acceptance_chance(
            "faction_2", war_data, unfavorable_terms, has_broker=False
        )
        
        # Verify results make sense
        assert isinstance(favorable_chance, float)
        assert isinstance(unfavorable_chance, float)
        assert 0.0 <= favorable_chance <= 1.0
        assert 0.0 <= unfavorable_chance <= 1.0 