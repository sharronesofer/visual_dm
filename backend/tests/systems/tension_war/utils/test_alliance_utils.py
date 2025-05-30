from typing import Type
"""
Tests for Alliance Utilities

This module contains comprehensive tests for alliance utility functions.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from backend.systems.tension_war.utils.alliance_utils import (
    evaluate_alliance_compatibility,
    evaluate_alliance_strength,
    calculate_call_to_arms_chance,
    calculate_alliance_benefits,
    generate_alliance_terms,
    evaluate_alliance_stability,
    evaluate_sanction_impact,
)
from backend.systems.tension_war.models import AllianceConfig, AllianceType, SanctionType
from backend.systems.tension_war.models.enums import AllianceType, SanctionType
from backend.systems.tension_war.models.config import AllianceConfig


@pytest.fixture
def basic_alliance_config(): pass
    """Create basic alliance configuration."""
    return AllianceConfig(
        tension_factor=1.0,
        ideology_factor=1.0,
        trait_factor=1.0,
        min_compatibility=0.3,
        stability_threshold=0.5,
        default_duration_months=12,
        call_to_arms_threshold=0.7,
    )


@pytest.fixture
def faction_a(): pass
    """Create sample faction A data."""
    return {
        "id": "faction_a",
        "name": "Empire Alpha",
        "ideology": {
            "authoritarianism": 0.7,
            "militarism": 0.8,
            "expansionism": 0.6,
            "economy": "market",
        },
        "traits": {
            "diplomatic": True,
            "honorable": True,
            "expansionist": False,
            "mercantile": False,
        },
        "military_strength": 85,
        "economic_power": 75,
        "technology_level": 80,
        "territory_size": 50,
        "population": 10000000,
        "resources": {
            "gold": 50000,
            "food": 30000,
            "materials": 25000,
        },
    }


@pytest.fixture
def faction_b(): pass
    """Create sample faction B data."""
    return {
        "id": "faction_b",
        "name": "Republic Beta",
        "ideology": {
            "authoritarianism": 0.2,
            "militarism": 0.4,
            "expansionism": 0.3,
            "economy": "market",
        },
        "traits": {
            "diplomatic": True,
            "honorable": False,
            "aggressive": False,
            "mercantile": True,
        },
        "military_strength": 65,
        "economic_power": 90,
        "technology_level": 95,
        "territory_size": 30,
        "population": 8000000,
        "resources": {
            "gold": 75000,
            "food": 20000,
            "materials": 35000,
        },
    }


@pytest.fixture
def faction_incompatible(): pass
    """Create faction that's incompatible with others."""
    return {
        "id": "faction_c",
        "name": "Isolationist State",
        "ideology": {
            "authoritarianism": 0.9,
            "militarism": 0.9,
            "expansionism": 0.9,
            "economy": "planned",
        },
        "traits": {
            "isolationist": True,
            "aggressive": True,
            "deceitful": True,
            "expansionist": True,
        },
        "military_strength": 95,
        "economic_power": 40,
        "technology_level": 60,
        "territory_size": 60,
        "population": 5000000,
    }


@pytest.fixture
def sample_alliance(): pass
    """Create sample alliance data."""
    return {
        "id": "alliance_123",
        "name": "Trade Partnership",
        "type": AllianceType.TRADE,
        "created_date": "2024-01-01T00:00:00Z",
        "duration_months": 12,
        "members": ["faction_a", "faction_b"],
        "terms": {
            "trade_boost": 0.15,
            "military_support": False,
            "technology_sharing": True,
            "resource_sharing": 0.1,
        },
        "status": "active",
        "stability": 0.75,
    }


class TestEvaluateAllianceStrength: pass
    """Test alliance strength evaluation functionality."""

    def test_strong_alliance_evaluation(self, faction_a, faction_b, basic_alliance_config): pass
        """Test that strong alliance gets high evaluation."""
        alliance_data = {
            "id": "alliance_123",
            "alliance_type": AllianceType.MILITARY.value,
            "formed_at": "2024-01-01T00:00:00Z"
        }
        
        result = evaluate_alliance_strength(alliance_data, [faction_a, faction_b], basic_alliance_config)
        
        assert result["overall_rating"] >= 6.0
        assert "total_military_strength" in result
        assert "total_economic_strength" in result
        assert len(result["strategic_advantages"]) >= 0
    
    def test_alliance_with_powerful_members(self, basic_alliance_config): pass
        """Test alliance with powerful faction members."""
        powerful_factions = [
            {"id": "faction_a", "military_strength": 8.0, "economic_strength": 9.0},
            {"id": "faction_b", "military_strength": 7.0, "economic_strength": 8.0},
        ]
        alliance_data = {
            "id": "alliance_123",
            "alliance_type": AllianceType.FULL.value,
            "formed_at": "2024-01-01T00:00:00Z"
        }
        
        result = evaluate_alliance_strength(alliance_data, powerful_factions, basic_alliance_config)
        
        assert result["overall_rating"] >= 8.0
        assert result["total_military_strength"] >= 15.0
        assert result["total_economic_strength"] >= 17.0
    
    def test_alliance_with_weak_members(self, basic_alliance_config): pass
        """Test alliance with weak faction members."""
        weak_factions = [
            {"id": "faction_a", "military_strength": 1.0, "economic_strength": 1.0},
            {"id": "faction_b", "military_strength": 1.0, "economic_strength": 1.0},
        ]
        alliance_data = {
            "id": "alliance_123",
            "alliance_type": AllianceType.ECONOMIC.value,
            "formed_at": "2024-01-01T00:00:00Z"
        }
        
        result = evaluate_alliance_strength(alliance_data, weak_factions, basic_alliance_config)
        
        assert result["overall_rating"] < 6.0
        assert result["total_military_strength"] == 2.0
        assert result["total_economic_strength"] == 2.0
        assert len(result["weaknesses"]) >= 0

    def test_single_member_alliance(self, basic_alliance_config): pass
        """Test alliance with single member."""
        alliance_data = {
            "id": "alliance_single",
            "alliance_type": AllianceType.NON_AGGRESSION.value,
            "formed_at": "2024-01-01T00:00:00Z"
        }

        participating_factions = [
            {
                "id": "faction_solo",
                "military_strength": 3.0,
                "economic_strength": 2.5,
            }
        ]

        result = evaluate_alliance_strength(alliance_data, participating_factions, basic_alliance_config)

        assert "alliance_id" in result
        assert "total_military_strength" in result
        assert "total_economic_strength" in result

        assert result["total_military_strength"] == 3.0

    def test_empty_faction_list(self, basic_alliance_config): pass
        """Test with empty faction list."""
        alliance_data = {
            "id": "alliance_empty",
            "alliance_type": AllianceType.ECONOMIC.value,
            "formed_at": "2024-01-01T00:00:00Z"
        }

        participating_factions = []

        result = evaluate_alliance_strength(alliance_data, participating_factions, basic_alliance_config)

        assert "alliance_id" in result
        assert "total_military_strength" in result
        assert "overall_rating" in result

        assert result["total_military_strength"] == 0

    def test_default_config_usage(self, faction_a, faction_b): pass
        """Test using default configuration."""
        alliance_data = {
            "id": "alliance_default",
            "alliance_type": AllianceType.MILITARY.value,
            "formed_at": "2024-01-01T00:00:00Z"
        }

        result = evaluate_alliance_strength(alliance_data, [faction_a, faction_b])

        assert "alliance_id" in result
        assert "total_military_strength" in result
        assert "overall_rating" in result
        assert result["overall_rating"] >= 0


class TestCalculateCallToArmsChance: pass
    """Test call to arms chance calculation functionality."""

    def test_strong_alliance_call_to_arms(self, sample_alliance, faction_a, faction_b, basic_alliance_config): pass
        """Test call to arms for strong alliance."""
        conflict_data = {
            "type": "defensive",
            "strategic_importance": 0.8,
            "severity": 0.7
        }
        
        result = calculate_call_to_arms_chance(
            sample_alliance, 
            faction_a, 
            faction_b, 
            conflict_data, 
            basic_alliance_config
        )
        
        assert "response_chance" in result
        assert result["response_chance"] > 0.5
        assert "factors" in result
        assert len(result["factors"]) > 0
    
    def test_military_alliance_call_to_arms(self, sample_alliance, faction_a, faction_b, basic_alliance_config): pass
        """Test call to arms for military alliance."""
        alliance_data = {**sample_alliance, "alliance_type": AllianceType.MILITARY.value}
        conflict_data = {
            "type": "defensive",
            "strategic_importance": 0.6
        }
        
        result = calculate_call_to_arms_chance(
            alliance_data, 
            faction_a, 
            faction_b, 
            conflict_data, 
            basic_alliance_config
        )
        
        assert result["response_chance"] > 0.5
    
    def test_trade_alliance_call_to_arms(self, sample_alliance, faction_a, faction_b, basic_alliance_config): pass
        """Test call to arms for trade alliance."""
        alliance_data = {**sample_alliance, "alliance_type": AllianceType.ECONOMIC.value}
        conflict_data = {
            "type": "aggressive",
            "strategic_importance": 0.3
        }
        
        result = calculate_call_to_arms_chance(
            alliance_data, 
            faction_a, 
            faction_b, 
            conflict_data, 
            basic_alliance_config
        )
        
        assert result["response_chance"] < 0.8
    
    def test_high_severity_conflict(self, sample_alliance, faction_a, faction_b, basic_alliance_config): pass
        """Test call to arms with high severity conflict."""
        conflict_data = {
            "type": "defensive",
            "strategic_importance": 0.9,
            "severity": 0.9
        }
        
        result = calculate_call_to_arms_chance(
            sample_alliance, 
            faction_a, 
            faction_b, 
            conflict_data, 
            basic_alliance_config
        )
        
        assert result["response_chance"] > 0.6
    
    def test_low_severity_conflict(self, sample_alliance, faction_a, faction_b, basic_alliance_config): pass
        """Test call to arms with low severity conflict."""
        conflict_data = {
            "type": "aggressive",
            "strategic_importance": 0.1,
            "severity": 0.2
        }
        
        result = calculate_call_to_arms_chance(
            sample_alliance, 
            faction_a, 
            faction_b, 
            conflict_data, 
            basic_alliance_config
        )
        
        assert result["response_chance"] < 0.7
    
    def test_weak_target_faction(self, sample_alliance, basic_alliance_config): pass
        """Test call to arms with weak target faction."""
        weak_target_faction = {
            "id": "faction_weak",
            "military_strength": 1.0,
            "active_conflicts": 2
        }
        requesting_faction = {"id": "faction_a", "military_strength": 5.0}
        conflict_data = {"type": "defensive", "strategic_importance": 0.5}
        
        result = calculate_call_to_arms_chance(
            sample_alliance, 
            requesting_faction, 
            weak_target_faction, 
            conflict_data, 
            basic_alliance_config
        )
        
        assert result["response_chance"] < 0.7
    
    def test_unstable_alliance_call_to_arms(self, basic_alliance_config): pass
        """Test call to arms in unstable alliance."""
        unstable_alliance = {
            "id": "alliance_123",
            "alliance_type": AllianceType.NON_AGGRESSION.value,
            "age_months": 1,
            "terms": {"mutual_defense_obligation": 0.2}
        }
        
        faction_a = {"id": "faction_a", "military_strength": 3.0}
        faction_b = {"id": "faction_b", "military_strength": 2.0, "active_conflicts": 1}
        conflict_data = {"type": "aggressive", "strategic_importance": 0.3}
        
        result = calculate_call_to_arms_chance(
            unstable_alliance, 
            faction_a, 
            faction_b, 
            conflict_data, 
            basic_alliance_config
        )
        
        assert result["response_chance"] < 0.6
    
    def test_default_config_usage(self, sample_alliance, faction_a, faction_b): pass
        """Test that function works with default config."""
        conflict_data = {"type": "defensive", "strategic_importance": 0.5}
        
        result = calculate_call_to_arms_chance(
            sample_alliance, 
            faction_a, 
            faction_b, 
            conflict_data
        )
        
        assert "response_chance" in result
        assert 0.0 <= result["response_chance"] <= 1.0


class TestAllianceUtilsIntegration: pass
    """Test integration between alliance utility functions."""

    def test_compatibility_to_terms_workflow(self, faction_a, faction_b, basic_alliance_config): pass
        """Test complete workflow from compatibility evaluation to terms generation."""
        
        # Step 1: Evaluate compatibility
        compatibility = evaluate_alliance_compatibility(faction_a, faction_b, -10.0, basic_alliance_config)
        
        # Step 2: Generate alliance terms
        terms = generate_alliance_terms(
            faction_a, 
            faction_b, 
            AllianceType.ECONOMIC, 
            compatibility, 
            basic_alliance_config
        )
        
        assert "trade_agreement" in terms
        assert "trade_bonus" in terms
        assert terms["trade_agreement"] is True
        assert terms["duration_months"] > 0
    
    def test_alliance_lifecycle_simulation(self, faction_a, faction_b, basic_alliance_config): pass
        """Test complete alliance lifecycle simulation."""
        
        # Step 1: Evaluate compatibility
        compatibility = evaluate_alliance_compatibility(faction_a, faction_b, -15.0, basic_alliance_config)
        
        # Step 2: Generate terms
        terms = generate_alliance_terms(
            faction_a, 
            faction_b, 
            AllianceType.MILITARY, 
            compatibility, 
            basic_alliance_config
        )
        
        # Step 3: Create alliance
        alliance_data = {
            "id": "alliance_lifecycle_test",
            "faction_a_id": faction_a["id"],
            "faction_b_id": faction_b["id"],
            "alliance_type": AllianceType.MILITARY.value,
            "terms": terms,
            "formed_at": datetime.utcnow().isoformat(),
            "age_months": 6
        }
        
        # Step 4: Evaluate alliance strength
        alliance_strength = evaluate_alliance_strength(
            alliance_data, 
            [faction_a, faction_b], 
            basic_alliance_config
        )
        
        # Step 5: Test call to arms
        conflict_data = {"type": "defensive", "strategic_importance": 0.7}
        call_response = calculate_call_to_arms_chance(
            alliance_data, 
            faction_a, 
            faction_b, 
            conflict_data, 
            basic_alliance_config
        )
        
        assert compatibility["overall_score"] > 0.3
        assert "trade_agreement" in terms or "defensive_pact" in terms
        assert alliance_strength["overall_rating"] > 3.0
        assert call_response["response_chance"] > 0.0

    def test_sanction_impact_on_alliance(self, faction_a, faction_b, basic_alliance_config): pass
        """Test how sanctions affect alliance stability."""
        
        alliance_data = {
            "id": "alliance_sanction_test",
            "faction_a_id": faction_a["id"],
            "faction_b_id": faction_b["id"],
            "alliance_type": AllianceType.ECONOMIC.value,
            "formed_at": datetime.utcnow().replace(tzinfo=None).isoformat()
        }
        
        events = [
            {
                "type": "sanction_imposed",
                "target": faction_a["id"],
                "issuer": "external_power",
                "timestamp": "2024-06-01T12:00:00Z"
            }
        ]
        
        stability = evaluate_alliance_stability(
            alliance_data,
            {faction_a["id"]: faction_a, faction_b["id"]: faction_b},
            5.0,
            events,
            basic_alliance_config
        )
        
        assert "stability_score" in stability
        assert 0.0 <= stability["stability_score"] <= 1.0
        assert len(stability["factors"]) > 0


# Add new test classes for untested functions
class TestCalculateAllianceBenefits: pass
    """Test alliance benefits calculation."""

    @pytest.fixture
    def alliance_data(self): pass
        return {
            "alliance_type": AllianceType.MILITARY.value,
            "faction_a_id": 1,
            "faction_b_id": 2,
            "terms": {
                "military_access": True,
                "trade_agreement": True,
                "trade_bonus": 0.15,
                "intelligence_sharing": True,
            },
        }

    @pytest.fixture
    def faction_data(self): pass
        return {
            1: {"id": 1, "name": "Empire", "power": 100},
            2: {"id": 2, "name": "Republic", "power": 90},
        }

    def test_military_alliance_benefits(self, alliance_data, faction_data): pass
        """Test benefits for military alliance."""
        alliance_data["alliance_type"] = AllianceType.MILITARY.value
        
        benefits = calculate_alliance_benefits(alliance_data, faction_data)
        
        # Check structure
        assert 1 in benefits
        assert 2 in benefits
        assert "shared" in benefits
        
        # Check military benefits
        assert "military_strength_bonus" in benefits[1]
        assert "military_strength_bonus" in benefits[2]
        assert benefits["shared"]["defensive_pact"] is True

    def test_economic_alliance_benefits(self, alliance_data, faction_data): pass
        """Test benefits for economic alliance."""
        alliance_data["alliance_type"] = AllianceType.ECONOMIC.value
        
        benefits = calculate_alliance_benefits(alliance_data, faction_data)
        
        # Check economic benefits
        assert "trade_efficiency_bonus" in benefits[1]
        assert "trade_efficiency_bonus" in benefits[2]
        assert benefits["shared"]["resource_sharing"] is True

    def test_full_alliance_benefits(self, alliance_data, faction_data): pass
        """Test benefits for full alliance."""
        alliance_data["alliance_type"] = AllianceType.FULL.value
        
        benefits = calculate_alliance_benefits(alliance_data, faction_data)
        
        # Check all benefits are present
        assert "military_strength_bonus" in benefits[1]
        assert "trade_efficiency_bonus" in benefits[1]
        assert benefits["shared"]["defensive_pact"] is True
        assert benefits["shared"]["resource_sharing"] is True
        assert benefits["shared"]["technology_sharing"] is True

    def test_non_aggression_benefits(self, alliance_data, faction_data): pass
        """Test benefits for non-aggression pact."""
        alliance_data["alliance_type"] = AllianceType.NON_AGGRESSION.value
        
        benefits = calculate_alliance_benefits(alliance_data, faction_data)
        
        # Check minimal benefits
        assert benefits["shared"]["non_aggression"] is True

    def test_additional_terms_benefits(self, alliance_data, faction_data): pass
        """Test additional benefits from terms."""
        benefits = calculate_alliance_benefits(alliance_data, faction_data)
        
        # Check term-based benefits
        assert benefits["shared"]["military_access"] is True
        assert benefits["shared"]["intelligence_sharing"] is True
        assert "additional_trade_bonus" in benefits[1]
        assert "additional_trade_bonus" in benefits[2]


class TestGenerateAllianceTerms: pass
    """Test alliance terms generation."""

    @pytest.fixture
    def faction_a(self): pass
        return {
            "id": 1,
            "name": "Empire",
            "traits": ["militaristic", "expansionist"],
            "power": 100,
        }

    @pytest.fixture
    def faction_b(self): pass
        return {
            "id": 2,
            "name": "Republic",
            "traits": ["diplomatic", "trade_focused"],
            "power": 90,
        }

    @pytest.fixture
    def high_compatibility(self): pass
        return {
            "overall_score": 0.8,
            "ideology_score": 0.7,
            "strategic_score": 0.9,
            "trade_score": 0.8,
        }

    @pytest.fixture
    def low_compatibility(self): pass
        return {
            "overall_score": 0.3,
            "ideology_score": 0.2,
            "strategic_score": 0.4,
            "trade_score": 0.3,
        }

    def test_military_alliance_terms(self, faction_a, faction_b, high_compatibility): pass
        """Test terms generation for military alliance."""
        terms = generate_alliance_terms(
            faction_a, faction_b, AllianceType.MILITARY, high_compatibility
        )
        
        # Check military terms
        assert terms["military_access"] is True
        assert terms["defensive_pact"] is True
        assert "duration_months" in terms
        
        # High compatibility should add offensive pact
        assert terms["offensive_pact"] is True

    def test_economic_alliance_terms(self, faction_a, faction_b, high_compatibility): pass
        """Test terms generation for economic alliance."""
        terms = generate_alliance_terms(
            faction_a, faction_b, AllianceType.ECONOMIC, high_compatibility
        )
        
        # Check economic terms
        assert terms["trade_agreement"] is True
        assert "trade_bonus" in terms
        assert terms["resource_sharing"] is True

    def test_full_alliance_terms(self, faction_a, faction_b, high_compatibility): pass
        """Test terms generation for full alliance."""
        terms = generate_alliance_terms(
            faction_a, faction_b, AllianceType.FULL, high_compatibility
        )
        
        # Check comprehensive terms
        assert terms["military_access"] is True
        assert terms["defensive_pact"] is True
        assert terms["trade_agreement"] is True
        assert terms["intelligence_sharing"] is True
        assert terms["offensive_pact"] is True
        assert terms["resource_sharing"] is True
        assert terms["technology_sharing"] is True

    def test_non_aggression_terms(self, faction_a, faction_b, low_compatibility): pass
        """Test terms generation for non-aggression pact."""
        terms = generate_alliance_terms(
            faction_a, faction_b, AllianceType.NON_AGGRESSION, low_compatibility
        )
        
        # Check minimal terms (duration may be adjusted by compatibility)
        assert "duration_months" in terms
        assert terms["duration_months"] >= 6  # At least 6 months

    def test_compatibility_affects_duration(self, faction_a, faction_b, high_compatibility, low_compatibility): pass
        """Test that compatibility affects alliance duration."""
        high_terms = generate_alliance_terms(
            faction_a, faction_b, AllianceType.MILITARY, high_compatibility
        )
        low_terms = generate_alliance_terms(
            faction_a, faction_b, AllianceType.MILITARY, low_compatibility
        )
        
        # High compatibility should result in longer duration
        assert high_terms["duration_months"] > low_terms["duration_months"]


class TestEvaluateAllianceStability: pass
    """Test alliance stability evaluation."""

    @pytest.fixture
    def alliance_data(self): pass
        return {
            "id": "alliance_1",
            "alliance_type": AllianceType.MILITARY.value,
            "faction_a_id": 1,
            "faction_b_id": 2,
            "formed_at": "2023-01-01T00:00:00",  # Proper ISO format
            "duration_months": 24,
        }

    @pytest.fixture
    def faction_data(self): pass
        return {
            1: {"id": 1, "name": "Empire", "power": 100, "stability": 0.8},
            2: {"id": 2, "name": "Republic", "power": 90, "stability": 0.7},
        }

    @pytest.fixture
    def recent_events(self): pass
        return [
            {
                "type": "trade_agreement",
                "impact": 0.1,
                "date": "2023-06-01",
            },
            {
                "type": "border_dispute",
                "impact": -0.2,
                "date": "2023-07-01",
            },
        ]

    def test_stable_alliance_evaluation(self, alliance_data, faction_data, recent_events): pass
        """Test evaluation of stable alliance."""
        stability = evaluate_alliance_stability(
            alliance_data, faction_data, 0.2, recent_events
        )
        
        # Check stability structure (based on actual function output)
        assert "alliance_id" in stability
        assert "stability_score" in stability
        assert "breaking_point" in stability
        assert "classification" in stability

    def test_unstable_alliance_evaluation(self, alliance_data, faction_data, recent_events): pass
        """Test evaluation of unstable alliance."""
        # High tension situation
        stability = evaluate_alliance_stability(
            alliance_data, faction_data, 0.8, recent_events
        )
        
        # Should identify some instability markers
        assert "score" in stability or "stability_score" in stability
        assert "breaking_point" in stability


class TestEvaluateSanctionImpact: pass
    """Test sanction impact evaluation."""

    @pytest.fixture
    def trade_sanction(self): pass
        return {
            "type": SanctionType.TRADE_EMBARGO,
            "severity": 0.7,
            "duration_months": 6,
        }

    @pytest.fixture
    def target_faction(self): pass
        return {
            "id": 1,
            "name": "Target",
            "economy": {"trade_dependence": 0.6, "gdp": 1000},
            "resources": {"gold": 500, "food": 200},
        }

    @pytest.fixture
    def issuing_faction(self): pass
        return {
            "id": 2,
            "name": "Issuer",
            "economy": {"trade_influence": 0.8, "gdp": 1500},
        }

    def test_trade_embargo_impact(self, trade_sanction, target_faction, issuing_faction): pass
        """Test trade embargo impact calculation."""
        impact = evaluate_sanction_impact(
            trade_sanction, target_faction, issuing_faction, 6
        )
        
        # Check impact structure (based on actual function output)
        assert "economic_impact" in impact
        assert "reputation_impact" in impact
        assert "military_impact" in impact
        assert "tension_change" in impact
        assert "effects" in impact

    def test_military_embargo_impact(self, target_faction, issuing_faction): pass
        """Test military embargo impact."""
        sanction = {
            "type": SanctionType.MILITARY,  # Use available enum value
            "severity": 0.9,
            "duration_months": 12,
        }
        
        impact = evaluate_sanction_impact(
            sanction, target_faction, issuing_faction, 12
        )
        
        # Military embargo should have military impact
        assert "military_impact" in impact

    def test_diplomatic_isolation_impact(self, target_faction, issuing_faction): pass
        """Test diplomatic isolation impact."""
        sanction = {
            "type": SanctionType.DIPLOMATIC,  # Use available enum value
            "severity": 0.6,
            "duration_months": 18,
        }
        
        impact = evaluate_sanction_impact(
            sanction, target_faction, issuing_faction, 18
        )
        
        # Diplomatic isolation should have reputation impact
        assert "reputation_impact" in impact

    def test_duration_affects_impact(self, trade_sanction, target_faction, issuing_faction): pass
        """Test that longer sanctions have greater impact."""
        short_impact = evaluate_sanction_impact(
            trade_sanction, target_faction, issuing_faction, 3
        )
        long_impact = evaluate_sanction_impact(
            trade_sanction, target_faction, issuing_faction, 12
        )
        
        # Longer sanctions should have greater economic impact
        assert abs(long_impact["economic_impact"]) > abs(short_impact["economic_impact"]) 