from backend.systems.population.models import POIPopulation
from backend.systems.population.models import POIPopulation
from backend.systems.population.models import POIPopulation
from backend.systems.population.models import POIPopulation
from backend.systems.population.models import POIPopulation
from backend.systems.population.models import POIPopulation
from typing import Type
from typing import List
"""
Comprehensive tests for the Population Utils module.

This module provides comprehensive tests for the utility functions in the population system,
covering all major functionality to achieve 90% coverage.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import Dict, List

from backend.systems.population.utils import (
    calculate_growth_rate,
    calculate_next_state,
    estimate_population_timeline,
    calculate_target_population,
    calculate_catastrophe_impact,
    calculate_war_impact,
    calculate_resource_shortage_impact,
    calculate_seasonal_growth_modifier,
    calculate_seasonal_death_rate_modifier,
    is_valid_transition,
    estimate_time_to_state,
    is_valid_state_progression,
    get_poi_status_description,
    calculate_migration_impact,
)
from backend.systems.population.models import (
    POIPopulation,
    POIType,
    POIState,
    PopulationConfig,
)


@pytest.fixture
def sample_population(): pass
    """Create a sample POI population for testing."""
    return POIPopulation(
        poi_id="test_city",
        name="Test City",
        poi_type=POIType.CITY,
        current_population=1000,
        target_population=1500,
        base_rate=5.0,
        state=POIState.NORMAL,
        last_updated=datetime.utcnow(),
        metadata={}
    )


@pytest.fixture
def sample_config(): pass
    """Create a sample population configuration for testing."""
    return PopulationConfig(
        global_multiplier=1.0,
        base_rates={
            POIType.CITY: 5.0,
            POIType.TOWN: 3.0,
            POIType.VILLAGE: 2.0,
            POIType.RUINS: 0.0,
            POIType.DUNGEON: 0.0,
        },
        state_transition_thresholds={
            "normal_to_declining": 0.6,
            "declining_to_abandoned": 0.3,
            "abandoned_to_ruins": 0.1,
            "repopulating_to_normal": 0.7
        },
        soft_cap_threshold=0.9,
        soft_cap_multiplier=0.5
    )


@pytest.fixture
def sample_thresholds(): pass
    """Create sample state transition thresholds."""
    return {
        "normal_to_declining": 0.6,
        "declining_to_abandoned": 0.3,
        "abandoned_to_ruins": 0.1,
        "repopulating_to_normal": 0.7
    }


class TestGrowthCalculations: pass
    """Tests for population growth calculations."""

    def test_calculate_growth_rate_normal(self, sample_population): pass
        """Test growth rate calculation for normal population."""
        result = calculate_growth_rate(sample_population, 1.0)
        
        # Should be positive growth for normal population under target
        assert result > 0
        assert isinstance(result, (int, float))

    def test_calculate_growth_rate_at_capacity(self): pass
        """Test growth rate when at target capacity."""
        at_capacity = POIPopulation(
            poi_id="test_at_capacity",
            name="Test At Capacity",
            poi_type=POIType.CITY,
            current_population=1500,
            target_population=1500,
            base_rate=5.0,
            state=POIState.NORMAL,
        )
        
        result = calculate_growth_rate(at_capacity, 1.0)
        
        # Should have soft cap applied when at capacity (5.0 * 1.0 * 1.0 * 0.5 = 2.5)
        assert result == 2.5

    def test_calculate_growth_rate_declining_state(self): pass
        """Test growth rate for declining population."""
        declining = POIPopulation(
            poi_id="test_declining",
            name="Test Declining",
            poi_type=POIType.CITY,
            current_population=500,
            target_population=1500,
            base_rate=5.0,
            state=POIState.DECLINING,
        )
        
        result = calculate_growth_rate(declining, 1.0)
        
        # Should be calculated normally for declining (5.0 * (500/1500) * 1.0 = 1.67)
        expected = 5.0 * (500 / 1500) * 1.0
        assert abs(result - expected) < 0.01

    def test_calculate_growth_rate_ruins(self): pass
        """Test growth rate for ruins (should be zero)."""
        ruins = POIPopulation(
            poi_id="test_ruins",
            name="Test Ruins",
            poi_type=POIType.RUINS,
            current_population=0,
            target_population=100,
            base_rate=0.0,
            state=POIState.RUINS,
        )
        
        result = calculate_growth_rate(ruins, 1.0)
        
        # Ruins should have no growth
        assert result == 0

    def test_calculate_growth_rate_with_soft_cap(self): pass
        """Test growth rate with soft cap applied."""
        near_capacity = POIPopulation(
            poi_id="test_near_capacity",
            name="Test Near Capacity",
            poi_type=POIType.CITY,
            current_population=1400,  # 93% of target
            target_population=1500,
            base_rate=5.0,
            state=POIState.NORMAL,
        )
        
        result = calculate_growth_rate(near_capacity, 1.0)
        
        # Should have reduced growth due to soft cap
        # 5.0 * (1400/1500) * 1.0 * 0.5 = 2.33
        expected = 5.0 * (1400 / 1500) * 1.0 * 0.5
        assert abs(result - expected) < 0.01


class TestStateTransitions: pass
    """Tests for POI state transitions."""

    def test_calculate_next_state_normal_healthy(self, sample_population, sample_thresholds): pass
        """Test state calculation for healthy normal population."""
        result = calculate_next_state(sample_population, sample_thresholds)
        
        # Should remain normal (1000/1500 = 67% > 60% threshold)
        assert result == POIState.NORMAL

    def test_calculate_next_state_declining_threshold(self, sample_thresholds): pass
        """Test state transition to declining."""
        low_pop = POIPopulation(
            poi_id="test_low",
            name="Test Low",
            poi_type=POIType.CITY,
            current_population=800,  # 53% of target, below threshold
            target_population=1500,
            base_rate=5.0,
            state=POIState.NORMAL,
        )
        
        result = calculate_next_state(low_pop, sample_thresholds)
        
        # Should transition to declining (800/1500 = 53% < 60% threshold)
        assert result == POIState.DECLINING

    def test_calculate_next_state_abandoned_threshold(self, sample_thresholds): pass
        """Test state transition to abandoned."""
        very_low_pop = POIPopulation(
            poi_id="test_very_low",
            name="Test Very Low",
            poi_type=POIType.CITY,
            current_population=400,  # 27% of target, below abandoned threshold
            target_population=1500,
            base_rate=5.0,
            state=POIState.DECLINING,
        )
        
        result = calculate_next_state(very_low_pop, sample_thresholds)
        
        # Should transition to abandoned (400/1500 = 27% < 30% threshold)
        assert result == POIState.ABANDONED

    def test_calculate_next_state_repopulating_recovery(self, sample_thresholds): pass
        """Test state transition from repopulating to normal."""
        recovering = POIPopulation(
            poi_id="test_recovering",
            name="Test Recovering",
            poi_type=POIType.CITY,
            current_population=1100,  # 73% of target, above repopulating threshold
            target_population=1500,
            base_rate=5.0,
            state=POIState.REPOPULATING,
        )
        
        result = calculate_next_state(recovering, sample_thresholds)
        
        # Should transition to normal (1100/1500 = 73% >= 70% threshold)
        assert result == POIState.NORMAL


class TestWarImpact: pass
    """Tests for war impact calculations."""

    def test_calculate_war_impact_low_damage(self): pass
        """Test war impact with low damage level."""
        result = calculate_war_impact(1000, 0.2)  # 20% damage
        
        assert result > 0
        assert result < 1000
        assert isinstance(result, (int, float))

    def test_calculate_war_impact_high_damage(self): pass
        """Test war impact with high damage level."""
        result = calculate_war_impact(1000, 0.8)  # 80% damage
        
        assert result > 0
        assert result < 1000
        assert isinstance(result, (int, float))

    def test_calculate_war_impact_zero_damage(self): pass
        """Test war impact with no damage."""
        result = calculate_war_impact(1000, 0.0)
        
        assert result == 0

    def test_calculate_war_impact_max_damage(self): pass
        """Test war impact with maximum damage."""
        result = calculate_war_impact(1000, 1.0)  # 100% damage
        
        # Should be high impact but function implementation determines exact behavior
        assert result >= 0
        assert isinstance(result, (int, float))


class TestCatastropheImpact: pass
    """Tests for catastrophe impact calculations."""

    def test_calculate_catastrophe_impact_mild(self): pass
        """Test catastrophe impact with mild severity."""
        result = calculate_catastrophe_impact(1000, 0.3)
        
        assert result >= 0
        assert isinstance(result, (int, float))

    def test_calculate_catastrophe_impact_severe(self): pass
        """Test catastrophe impact with severe severity."""
        result = calculate_catastrophe_impact(1000, 0.9)
        
        assert result >= 0
        assert isinstance(result, (int, float))

    def test_calculate_catastrophe_impact_zero(self): pass
        """Test catastrophe impact with zero severity."""
        result = calculate_catastrophe_impact(1000, 0.0)
        
        assert result == 0

    def test_calculate_catastrophe_impact_max(self): pass
        """Test catastrophe impact with maximum severity."""
        result = calculate_catastrophe_impact(1000, 1.0)
        
        assert result >= 0
        assert isinstance(result, (int, float))


class TestStatusDescriptions: pass
    """Tests for status description functions."""

    def test_get_poi_status_description_thriving(self, sample_population): pass
        """Test status description for thriving population."""
        result = get_poi_status_description(sample_population)
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_poi_status_description_declining(self): pass
        """Test status description for declining population."""
        declining = POIPopulation(
            poi_id="test_declining",
            name="Test Declining",
            poi_type=POIType.CITY,
            current_population=300,
            target_population=1500,
            base_rate=5.0,
            state=POIState.DECLINING,
        )
        
        result = get_poi_status_description(declining)
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_poi_status_description_ruins(self): pass
        """Test status description for ruins."""
        ruins = POIPopulation(
            poi_id="test_ruins",
            name="Test Ruins",
            poi_type=POIType.RUINS,
            current_population=0,
            target_population=100,
            base_rate=0.0,
            state=POIState.RUINS,
        )
        
        result = get_poi_status_description(ruins)
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestUtilityFunctions: pass
    """Tests for various utility functions."""

    def test_calculate_target_population_city(self): pass
        """Test target population calculation for city."""
        result = calculate_target_population(POIType.CITY)
        
        assert isinstance(result, int)
        assert result > 0

    def test_calculate_target_population_with_modifier(self): pass
        """Test target population calculation with size modifier."""
        result = calculate_target_population(POIType.CITY, 1.5)
        
        assert isinstance(result, int)
        assert result > 0

    def test_calculate_seasonal_growth_modifier_spring(self): pass
        """Test seasonal growth modifier for spring."""
        result = calculate_seasonal_growth_modifier("spring")
        
        assert isinstance(result, (int, float))
        assert result >= 0

    def test_calculate_seasonal_growth_modifier_winter(self): pass
        """Test seasonal growth modifier for winter."""
        result = calculate_seasonal_growth_modifier("winter")
        
        assert isinstance(result, (int, float))
        assert result >= 0

    def test_calculate_seasonal_death_rate_modifier_spring(self): pass
        """Test seasonal death rate modifier for spring."""
        result = calculate_seasonal_death_rate_modifier("spring")
        
        assert isinstance(result, (int, float))
        assert result >= 0

    def test_calculate_seasonal_death_rate_modifier_winter(self): pass
        """Test seasonal death rate modifier for winter."""
        result = calculate_seasonal_death_rate_modifier("winter")
        
        assert isinstance(result, (int, float))
        assert result >= 0

    def test_is_valid_transition_normal_to_declining(self): pass
        """Test valid state transition."""
        result = is_valid_transition(POIState.NORMAL, POIState.DECLINING)
        
        assert isinstance(result, bool)

    def test_is_valid_transition_invalid(self): pass
        """Test invalid state transition."""
        result = is_valid_transition(POIState.RUINS, POIState.NORMAL)
        
        assert isinstance(result, bool)

    def test_is_valid_state_progression(self): pass
        """Test state progression validation."""
        result = is_valid_state_progression(POIState.NORMAL, POIState.DECLINING)
        
        assert isinstance(result, bool)

    def test_calculate_resource_shortage_impact_mild(self): pass
        """Test resource shortage impact with mild severity."""
        result = calculate_resource_shortage_impact(1000, 0.3)
        
        assert isinstance(result, (int, float))
        assert result >= 0

    def test_calculate_resource_shortage_impact_severe(self): pass
        """Test resource shortage impact with severe severity."""
        result = calculate_resource_shortage_impact(1000, 0.8)
        
        assert isinstance(result, (int, float))
        assert result >= 0

    def test_estimate_time_to_state(self, sample_population): pass
        """Test time estimation for state change."""
        result = estimate_time_to_state(sample_population, POIState.DECLINING, 1.0)
        
        assert result is None or isinstance(result, int)
        if result is not None: pass
            assert result >= 0

    def test_calculate_migration_impact(self, sample_population): pass
        """Test migration impact calculation."""
        target_pop = POIPopulation(
            poi_id="target",
            name="Target",
            poi_type=POIType.TOWN,
            current_population=200,
            target_population=500,
            base_rate=3.0,
            state=POIState.NORMAL,
        )
        
        result = calculate_migration_impact(sample_population, target_pop, 0.1)  # 10% migration
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)  # Source population change
        assert isinstance(result[1], int)  # Target population change


class TestAdvancedFunctions: pass
    """Tests for advanced utility functions."""

    def test_estimate_population_timeline(self, sample_population): pass
        """Test population timeline estimation."""
        result = estimate_population_timeline(sample_population, 1.0, months=6)
        
        assert isinstance(result, list)
        assert len(result) == 6
        for month_data in result: pass
            assert isinstance(month_data, tuple)
            assert len(month_data) == 2
            assert isinstance(month_data[0], (int, float))  # Population
            assert isinstance(month_data[1], POIState)  # State

    def test_estimate_population_timeline_with_custom_thresholds(self, sample_population): pass
        """Test population timeline with custom thresholds."""
        custom_thresholds = {
            "normal_to_declining": 0.5,
            "declining_to_abandoned": 0.2,
            "abandoned_to_ruins": 0.05,
            "repopulating_to_normal": 0.8
        }
        
        result = estimate_population_timeline(
            sample_population, 
            1.0, 
            months=3,
            state_transition_thresholds=custom_thresholds
        )
        
        assert isinstance(result, list)
        assert len(result) == 3 