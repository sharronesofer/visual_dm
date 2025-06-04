"""
Tests for Population System Demographic Mathematical Models

This module tests the mathematical models implemented for Task 74 including
birth/death rates, migration patterns, and demographic changes.
"""

import pytest
import math
from typing import Dict, Any

from backend.systems.population.utils.demographic_models import (
    DemographicModels,
    PopulationProjectionModels,
    DemographicProfile,
    AgeGroup,
    MigrationType,
    SettlementType
)


class TestDemographicModels:
    """Test suite for demographic mathematical models"""
    
    def test_age_based_mortality_calculation(self):
        """Test age-based mortality rate calculations"""
        # Test infant mortality (should be highest)
        infant_mortality = DemographicModels.calculate_age_based_mortality(
            AgeGroup.INFANT, 0.008, 0.5, 0.5
        )
        
        # Test adult mortality (baseline)
        adult_mortality = DemographicModels.calculate_age_based_mortality(
            AgeGroup.ADULT, 0.008, 0.5, 0.5
        )
        
        # Test elder mortality (should be high)
        elder_mortality = DemographicModels.calculate_age_based_mortality(
            AgeGroup.ELDER, 0.008, 0.5, 0.5
        )
        
        # Assertions
        assert infant_mortality > adult_mortality, "Infant mortality should be higher than adult"
        assert elder_mortality > adult_mortality, "Elder mortality should be higher than adult"
        assert 0.001 <= infant_mortality <= 0.95, "Mortality should be within valid range"
        assert 0.001 <= adult_mortality <= 0.95, "Mortality should be within valid range"
        assert 0.001 <= elder_mortality <= 0.95, "Mortality should be within valid range"
    
    def test_healthcare_impact_on_mortality(self):
        """Test that healthcare quality reduces mortality rates"""
        base_mortality = DemographicModels.calculate_age_based_mortality(
            AgeGroup.ADULT, 0.008, 0.0, 0.5  # No healthcare
        )
        
        good_healthcare_mortality = DemographicModels.calculate_age_based_mortality(
            AgeGroup.ADULT, 0.008, 1.0, 0.5  # Excellent healthcare
        )
        
        assert good_healthcare_mortality < base_mortality, "Good healthcare should reduce mortality"
    
    def test_safety_impact_on_mortality(self):
        """Test that safety level affects mortality rates"""
        dangerous_mortality = DemographicModels.calculate_age_based_mortality(
            AgeGroup.ADULT, 0.008, 0.5, 0.0  # Very dangerous
        )
        
        safe_mortality = DemographicModels.calculate_age_based_mortality(
            AgeGroup.ADULT, 0.008, 0.5, 1.0  # Very safe
        )
        
        assert dangerous_mortality > safe_mortality, "Dangerous areas should have higher mortality"
    
    def test_fertility_rate_calculation(self):
        """Test age-based fertility rate calculations"""
        # Test reproductive age groups
        young_adult_fertility = DemographicModels.calculate_fertility_rate(
            AgeGroup.YOUNG_ADULT, 0.12, 0.5, 0.5
        )
        
        adult_fertility = DemographicModels.calculate_fertility_rate(
            AgeGroup.ADULT, 0.12, 0.5, 0.5
        )
        
        # Test non-reproductive age groups
        child_fertility = DemographicModels.calculate_fertility_rate(
            AgeGroup.CHILD, 0.12, 0.5, 0.5
        )
        
        elder_fertility = DemographicModels.calculate_fertility_rate(
            AgeGroup.ELDER, 0.12, 0.5, 0.5
        )
        
        # Assertions
        assert young_adult_fertility > 0, "Young adults should have fertility"
        assert adult_fertility > 0, "Adults should have fertility"
        assert child_fertility == 0, "Children should have no fertility"
        assert elder_fertility == 0, "Elders should have no fertility"
        assert young_adult_fertility >= adult_fertility, "Young adults should have peak fertility"
    
    def test_economic_impact_on_fertility(self):
        """Test that economic conditions affect fertility rates"""
        poor_fertility = DemographicModels.calculate_fertility_rate(
            AgeGroup.YOUNG_ADULT, 0.12, 0.1, 0.5  # Very poor
        )
        
        moderate_fertility = DemographicModels.calculate_fertility_rate(
            AgeGroup.YOUNG_ADULT, 0.12, 0.5, 0.5  # Moderate prosperity
        )
        
        wealthy_fertility = DemographicModels.calculate_fertility_rate(
            AgeGroup.YOUNG_ADULT, 0.12, 0.9, 0.5  # Very wealthy
        )
        
        # Moderate prosperity should have highest fertility
        assert moderate_fertility >= poor_fertility, "Moderate prosperity should increase fertility over poverty"
        assert moderate_fertility >= wealthy_fertility, "Moderate prosperity should have higher fertility than extreme wealth"
    
    def test_life_expectancy_calculation(self):
        """Test life expectancy calculations based on regional factors"""
        # Test baseline conditions
        baseline_expectancy = DemographicModels.calculate_life_expectancy(0.5, 0.5, 0.5, 0.5)
        
        # Test excellent conditions
        excellent_expectancy = DemographicModels.calculate_life_expectancy(1.0, 1.0, 1.0, 1.0)
        
        # Test poor conditions
        poor_expectancy = DemographicModels.calculate_life_expectancy(0.0, 0.0, 0.0, 0.0)
        
        # Assertions
        assert 25.0 <= baseline_expectancy <= 95.0, "Life expectancy should be within valid range"
        assert excellent_expectancy > baseline_expectancy, "Excellent conditions should increase life expectancy"
        assert poor_expectancy < baseline_expectancy, "Poor conditions should decrease life expectancy"
        assert excellent_expectancy > poor_expectancy, "Excellent conditions should be better than poor"
    
    def test_population_pyramid_generation(self):
        """Test population pyramid generation"""
        pyramid = DemographicModels.generate_population_pyramid(10000, 60.0, 0.02)
        
        # Check structure
        assert isinstance(pyramid, dict), "Pyramid should be a dictionary"
        assert len(pyramid) > 0, "Pyramid should have age groups"
        
        # Check that all age groups have male/female/total
        for age_range, data in pyramid.items():
            assert "male" in data, f"Age group {age_range} should have male count"
            assert "female" in data, f"Age group {age_range} should have female count"
            assert "total" in data, f"Age group {age_range} should have total count"
            assert data["total"] == data["male"] + data["female"], f"Total should equal male + female for {age_range}"
        
        # Check total population approximately matches
        total_in_pyramid = sum(data["total"] for data in pyramid.values())
        assert abs(total_in_pyramid - 10000) < 500, "Pyramid total should be close to target population"
    
    def test_migration_probability_calculation(self):
        """Test migration probability calculations"""
        origin_factors = {
            "economic_opportunity": 0.2,  # Poor economy
            "safety_level": 0.3,          # Unsafe
            "resource_availability": 0.4   # Limited resources
        }
        
        destination_factors = {
            "economic_opportunity": 0.8,   # Good economy
            "safety_level": 0.9,           # Safe
            "resource_availability": 0.7,  # Good resources
            "family_connections": 0.1       # Some family
        }
        
        # Test economic migration
        economic_prob = DemographicModels.calculate_migration_probability(
            origin_factors, destination_factors, 100.0, MigrationType.ECONOMIC
        )
        
        # Test safety migration
        safety_prob = DemographicModels.calculate_migration_probability(
            origin_factors, destination_factors, 100.0, MigrationType.SAFETY
        )
        
        # Test forced migration
        forced_prob = DemographicModels.calculate_migration_probability(
            origin_factors, destination_factors, 100.0, MigrationType.FORCED
        )
        
        # Assertions
        assert 0.0 <= economic_prob <= 1.0, "Migration probability should be between 0 and 1"
        assert 0.0 <= safety_prob <= 1.0, "Migration probability should be between 0 and 1"
        assert 0.0 <= forced_prob <= 1.0, "Migration probability should be between 0 and 1"
        assert safety_prob >= economic_prob, "Safety migration should have higher urgency"
        assert forced_prob >= safety_prob, "Forced migration should have highest probability"
    
    def test_distance_decay_in_migration(self):
        """Test that distance reduces migration probability"""
        origin_factors = {"economic_opportunity": 0.2, "safety_level": 0.3, "resource_availability": 0.4}
        destination_factors = {"economic_opportunity": 0.8, "safety_level": 0.9, "resource_availability": 0.7, "family_connections": 0.1}
        
        close_prob = DemographicModels.calculate_migration_probability(
            origin_factors, destination_factors, 50.0, MigrationType.ECONOMIC
        )
        
        far_prob = DemographicModels.calculate_migration_probability(
            origin_factors, destination_factors, 500.0, MigrationType.ECONOMIC
        )
        
        assert close_prob > far_prob, "Closer destinations should have higher migration probability"
    
    def test_settlement_growth_dynamics(self):
        """Test settlement growth dynamics calculations"""
        growth_data = DemographicModels.calculate_settlement_growth_dynamics(
            current_population=1000,
            settlement_type=SettlementType.TOWN,
            economic_activity=0.7,
            resource_capacity=5000,
            infrastructure_level=0.6
        )
        
        # Check required fields
        required_fields = [
            "current_population", "settlement_type", "annual_growth_rate",
            "projected_population_1_year", "projected_population_5_years",
            "projected_population_10_years", "carrying_capacity",
            "capacity_utilization", "urbanization_pressure"
        ]
        
        for field in required_fields:
            assert field in growth_data, f"Growth data should include {field}"
        
        # Check logical relationships
        assert growth_data["projected_population_1_year"] >= growth_data["current_population"], "1-year projection should be >= current"
        assert growth_data["projected_population_5_years"] >= growth_data["projected_population_1_year"], "5-year projection should be >= 1-year"
        assert growth_data["projected_population_10_years"] >= growth_data["projected_population_5_years"], "10-year projection should be >= 5-year"
        assert 0.0 <= growth_data["capacity_utilization"] <= 2.0, "Capacity utilization should be reasonable"
        assert 0.0 <= growth_data["urbanization_pressure"] <= 1.0, "Urbanization pressure should be between 0 and 1"
    
    def test_settlement_type_growth_rates(self):
        """Test that different settlement types have appropriate growth rates"""
        village_growth = DemographicModels.calculate_settlement_growth_dynamics(
            200, SettlementType.VILLAGE, 0.5, 1000, 0.5
        )
        
        city_growth = DemographicModels.calculate_settlement_growth_dynamics(
            5000, SettlementType.CITY, 0.5, 20000, 0.5
        )
        
        metropolis_growth = DemographicModels.calculate_settlement_growth_dynamics(
            100000, SettlementType.METROPOLIS, 0.5, 500000, 0.5
        )
        
        # Cities should generally have higher growth rates than villages
        # Metropolises should have lower growth rates due to size constraints
        assert city_growth["annual_growth_rate"] > village_growth["annual_growth_rate"], "Cities should grow faster than villages"
        assert metropolis_growth["annual_growth_rate"] < city_growth["annual_growth_rate"], "Metropolises should grow slower than cities"
    
    def test_demographic_profile_creation(self):
        """Test comprehensive demographic profile creation"""
        region_factors = {
            "healthcare_quality": 0.6,
            "safety_level": 0.7,
            "economic_prosperity": 0.5,
            "environmental_quality": 0.8
        }
        
        profile = DemographicModels.create_demographic_profile(5000, region_factors)
        
        # Check profile structure
        assert isinstance(profile, DemographicProfile), "Should return DemographicProfile object"
        assert profile.total_population == 5000, "Total population should match input"
        assert len(profile.age_distribution) == len(AgeGroup), "Should have all age groups"
        assert profile.birth_rate > 0, "Birth rate should be positive"
        assert profile.death_rate > 0, "Death rate should be positive"
        assert profile.life_expectancy > 0, "Life expectancy should be positive"
        assert profile.dependency_ratio >= 0, "Dependency ratio should be non-negative"
        
        # Check age distribution sums to total
        age_total = sum(profile.age_distribution.values())
        assert age_total == profile.total_population, "Age distribution should sum to total population"


class TestPopulationProjectionModels:
    """Test suite for population projection models"""
    
    def test_population_projection_basic(self):
        """Test basic population projection functionality"""
        # Create a simple demographic profile
        age_distribution = {ag: 1000 for ag in AgeGroup}
        profile = DemographicProfile(
            total_population=8000,
            age_distribution=age_distribution,
            birth_rate=25.0,
            death_rate=15.0,
            fertility_rate=0.1,
            life_expectancy=60.0,
            population_pyramid={},
            migration_rate=0.0,
            growth_rate=0.01,
            dependency_ratio=0.5
        )
        
        projections = PopulationProjectionModels.project_population_change(profile, 12)
        
        # Check projection structure
        assert len(projections) == 13, "Should have 13 projections (initial + 12 months)"
        assert projections[0] == profile, "First projection should be the initial profile"
        
        # Check that population changes over time
        final_population = projections[-1].total_population
        assert final_population != profile.total_population, "Population should change over time"
    
    def test_population_projection_with_external_factors(self):
        """Test population projection with external factors (wars, economic changes)"""
        age_distribution = {ag: 1000 for ag in AgeGroup}
        profile = DemographicProfile(
            total_population=8000,
            age_distribution=age_distribution,
            birth_rate=25.0,
            death_rate=15.0,
            fertility_rate=0.1,
            life_expectancy=60.0,
            population_pyramid={},
            migration_rate=0.0,
            growth_rate=0.01,
            dependency_ratio=0.5
        )
        
        # Test war impact
        war_factors = {
            "war": {
                "start_month": 2,
                "end_month": 8,
                "intensity": 0.3,
                "refugee_outflow": 0.1
            }
        }
        
        war_projections = PopulationProjectionModels.project_population_change(
            profile, 12, war_factors
        )
        
        # Test economic boom
        boom_factors = {
            "economic_boom": {
                "start_month": 0,
                "end_month": 12,
                "prosperity_boost": 0.2,
                "immigration": 0.05
            }
        }
        
        boom_projections = PopulationProjectionModels.project_population_change(
            profile, 12, boom_factors
        )
        
        # War should reduce population more than normal
        normal_projections = PopulationProjectionModels.project_population_change(profile, 12)
        
        assert war_projections[-1].total_population < normal_projections[-1].total_population, "War should reduce final population"
        assert boom_projections[-1].total_population > normal_projections[-1].total_population, "Economic boom should increase final population"
    
    def test_population_projection_age_distribution_changes(self):
        """Test that age distribution changes appropriately over time"""
        age_distribution = {ag: 1000 for ag in AgeGroup}
        profile = DemographicProfile(
            total_population=8000,
            age_distribution=age_distribution,
            birth_rate=30.0,  # High birth rate
            death_rate=10.0,  # Low death rate
            fertility_rate=0.15,
            life_expectancy=70.0,
            population_pyramid={},
            migration_rate=0.0,
            growth_rate=0.02,
            dependency_ratio=0.5
        )
        
        projections = PopulationProjectionModels.project_population_change(profile, 12)
        
        # Check that infant population increases due to births
        initial_infants = projections[0].age_distribution[AgeGroup.INFANT]
        final_infants = projections[-1].age_distribution[AgeGroup.INFANT]
        
        assert final_infants > initial_infants, "Infant population should increase with high birth rate"


class TestDemographicModelsEdgeCases:
    """Test edge cases and error handling for demographic models"""
    
    def test_extreme_parameter_values(self):
        """Test models with extreme parameter values"""
        # Test with minimum values
        min_mortality = DemographicModels.calculate_age_based_mortality(
            AgeGroup.ADULT, 0.0, 0.0, 0.0
        )
        assert min_mortality >= 0.001, "Mortality should have minimum floor"
        
        # Test with maximum values
        max_mortality = DemographicModels.calculate_age_based_mortality(
            AgeGroup.ANCIENT, 1.0, 0.0, 0.0
        )
        assert max_mortality <= 0.95, "Mortality should have maximum cap"
        
        # Test life expectancy extremes
        min_life = DemographicModels.calculate_life_expectancy(0.0, 0.0, 0.0, 0.0)
        max_life = DemographicModels.calculate_life_expectancy(1.0, 1.0, 1.0, 1.0)
        
        assert 25.0 <= min_life <= 95.0, "Life expectancy should be within bounds"
        assert 25.0 <= max_life <= 95.0, "Life expectancy should be within bounds"
        assert max_life > min_life, "Max conditions should give higher life expectancy"
    
    def test_zero_population_handling(self):
        """Test handling of zero or very small populations"""
        # Test with very small population
        small_pyramid = DemographicModels.generate_population_pyramid(10, 50.0, 0.01)
        assert isinstance(small_pyramid, dict), "Should handle small populations"
        
        # Test settlement growth with small population
        small_growth = DemographicModels.calculate_settlement_growth_dynamics(
            1, SettlementType.VILLAGE, 0.5, 100, 0.5
        )
        assert small_growth["current_population"] == 1, "Should handle single person settlements"
    
    def test_overcapacity_scenarios(self):
        """Test scenarios where population exceeds carrying capacity"""
        overcapacity_growth = DemographicModels.calculate_settlement_growth_dynamics(
            15000, SettlementType.CITY, 0.5, 10000, 0.5  # Population > capacity
        )
        
        assert overcapacity_growth["capacity_utilization"] > 1.0, "Should show overcapacity"
        assert overcapacity_growth["annual_growth_rate"] < 0.02, "Growth should be limited when overcapacity" 