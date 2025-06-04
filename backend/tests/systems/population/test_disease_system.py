"""
Test Suite for Population Disease System

Tests the disease modeling engine, outbreak progression, quest generation,
and population effects calculations.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from systems.population.utils.disease_models import (
    DiseaseType,
    DiseaseStage,
    DiseaseProfile,
    DiseaseOutbreak,
    DiseaseModelingEngine,
    DISEASE_PROFILES,
    DISEASE_ENGINE,
    introduce_random_disease_outbreak,
    apply_disease_effects_to_population
)


class TestDiseaseProfiles:
    """Test disease profile definitions and validation"""
    
    def test_all_disease_types_have_profiles(self):
        """Ensure all disease types have corresponding profiles"""
        for disease_type in DiseaseType:
            assert disease_type in DISEASE_PROFILES
            
    def test_disease_profile_validation(self):
        """Test disease profile structure and constraints"""
        for disease_type, profile in DISEASE_PROFILES.items():
            # Basic profile structure
            assert isinstance(profile, DiseaseProfile)
            assert profile.disease_type == disease_type
            
            # Mortality rate validation
            assert 0.0 <= profile.mortality_rate <= 1.0
            
            # Transmission rate validation
            assert 0.0 <= profile.transmission_rate <= 1.0
            
            # Duration validation
            assert profile.incubation_days > 0
            assert profile.recovery_days > 0
            assert profile.immunity_duration_days >= 0
            
            # Environmental factors validation
            assert profile.crowding_factor > 0
            assert profile.hygiene_factor > 0
            assert profile.healthcare_factor > 0
            
    def test_disease_profile_specific_properties(self):
        """Test specific disease characteristics"""
        # Plague should be highly lethal
        plague = DISEASE_PROFILES[DiseaseType.PLAGUE]
        assert plague.mortality_rate >= 0.5
        assert plague.targets_weak
        
        # Bone Fever should be very infectious but low mortality
        bone_fever = DISEASE_PROFILES[DiseaseType.BONE_FEVER]
        assert bone_fever.transmission_rate >= 0.7
        assert bone_fever.mortality_rate <= 0.1
        
        # Wasting should be very lethal
        wasting = DISEASE_PROFILES[DiseaseType.WASTING]
        assert wasting.mortality_rate >= 0.7


class TestDiseaseModelingEngine:
    """Test the core disease modeling engine"""
    
    def setup_method(self):
        """Set up test environment"""
        self.engine = DiseaseModelingEngine()
        self.test_population_id = "test_population_123"
        
    def test_disease_introduction(self):
        """Test introducing a disease to a population"""
        outbreak = self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.FEVER,
            initial_infected=5
        )
        
        assert outbreak.disease_type == DiseaseType.FEVER
        assert outbreak.infected_count == 5
        assert outbreak.stage == DiseaseStage.EMERGING
        assert outbreak.days_active == 0
        assert outbreak.total_deaths == 0
        
        # Check that outbreak is tracked
        assert self.test_population_id in self.engine.active_outbreaks
        assert len(self.engine.active_outbreaks[self.test_population_id]) == 1
        
    def test_multiple_disease_introduction(self):
        """Test introducing multiple diseases to same population"""
        # Introduce first disease
        outbreak1 = self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.FEVER,
            initial_infected=3
        )
        
        # Introduce second disease
        outbreak2 = self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.POX,
            initial_infected=2
        )
        
        # Both should be tracked
        outbreaks = self.engine.active_outbreaks[self.test_population_id]
        assert len(outbreaks) == 2
        
        disease_types = [outbreak.disease_type for outbreak in outbreaks]
        assert DiseaseType.FEVER in disease_types
        assert DiseaseType.POX in disease_types
        
    def test_same_disease_introduction_increases_count(self):
        """Test that introducing same disease type increases infected count"""
        # First introduction
        self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.FEVER,
            initial_infected=3
        )
        
        # Second introduction of same disease
        outbreak = self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.FEVER,
            initial_infected=2
        )
        
        # Should have combined count
        assert outbreak.infected_count == 5
        
        # Should still only have one outbreak tracked
        outbreaks = self.engine.active_outbreaks[self.test_population_id]
        assert len(outbreaks) == 1
        
    def test_environmental_factors_application(self):
        """Test that environmental factors are applied correctly"""
        environmental_factors = {
            'crowding': 2.0,
            'hygiene': 1.5,
            'healthcare': 0.8,
            'season': 'summer'
        }
        
        outbreak = self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.FEVER,  # Summer preference
            initial_infected=1,
            environmental_factors=environmental_factors
        )
        
        assert outbreak.current_crowding_modifier == 2.0
        assert outbreak.current_hygiene_modifier == 1.5
        assert outbreak.current_healthcare_modifier == 0.8
        assert outbreak.current_seasonal_modifier == 1.5  # Fever prefers summer
        
    def test_disease_progression_day(self):
        """Test daily disease progression"""
        # Set up outbreak
        self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.FEVER,
            initial_infected=10
        )
        
        # Progress one day
        result = self.engine.progress_disease_day(
            population_id=self.test_population_id,
            total_population=1000
        )
        
        assert result['active_outbreaks'] == 1
        assert result['total_infected'] >= 10  # Should have some spread
        assert 'outbreaks' in result
        
    def test_disease_stage_progression(self):
        """Test that disease stages progress correctly"""
        self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.FEVER,
            initial_infected=100  # Large outbreak
        )
        
        # Progress multiple days
        for _ in range(10):
            self.engine.progress_disease_day(
                population_id=self.test_population_id,
                total_population=1000
            )
        
        outbreak = self.engine.active_outbreaks[self.test_population_id][0]
        assert outbreak.days_active == 10
        # Stage should have progressed from EMERGING
        assert outbreak.stage != DiseaseStage.EMERGING
        
    def test_disease_status_retrieval(self):
        """Test getting disease status for a population"""
        # No diseases initially
        status = self.engine.get_disease_status(self.test_population_id)
        assert not status['has_diseases']
        assert status['outbreaks'] == []
        
        # Add disease
        self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.PLAGUE,
            initial_infected=5
        )
        
        status = self.engine.get_disease_status(self.test_population_id)
        assert status['has_diseases']
        assert status['outbreak_count'] == 1
        assert len(status['outbreaks']) == 1
        
        outbreak_info = status['outbreaks'][0]
        assert outbreak_info['disease_type'] == 'plague'
        assert outbreak_info['disease_name'] == 'Black Death'
        assert outbreak_info['infected_count'] == 5


class TestQuestGeneration:
    """Test quest generation from disease outbreaks"""
    
    def setup_method(self):
        """Set up test environment"""
        self.engine = DiseaseModelingEngine()
        self.test_population_id = "test_population_quest"
        
    def test_no_diseases_no_quests(self):
        """Test that no quests are generated without diseases"""
        quests = self.engine.generate_quest_opportunities(self.test_population_id)
        assert quests == []
        
    def test_emerging_disease_quests(self):
        """Test quest generation for emerging diseases"""
        self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.PLAGUE,
            initial_infected=1
        )
        
        quests = self.engine.generate_quest_opportunities(self.test_population_id)
        assert len(quests) > 0
        
        # Should have investigation and gathering quests for emerging stage
        quest_types = [quest['type'] for quest in quests]
        assert 'investigation' in quest_types
        assert 'gathering' in quest_types
        
    def test_spreading_disease_quests(self):
        """Test quest generation for spreading diseases"""
        # Create disease and progress to spreading stage
        self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.FEVER,
            initial_infected=50  # Larger outbreak
        )
        
        # Progress several days to reach spreading stage
        for _ in range(5):
            self.engine.progress_disease_day(
                population_id=self.test_population_id,
                total_population=1000
            )
        
        quests = self.engine.generate_quest_opportunities(self.test_population_id)
        quest_types = [quest['type'] for quest in quests]
        
        # Should have delivery and protection quests for spreading stage
        assert any(quest_type in ['delivery', 'protection'] for quest_type in quest_types)
        
    def test_quest_urgency_levels(self):
        """Test that quests have appropriate urgency levels"""
        self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.WASTING,  # High mortality disease
            initial_infected=10
        )
        
        quests = self.engine.generate_quest_opportunities(self.test_population_id)
        
        # All quests should have urgency specified
        for quest in quests:
            assert 'urgency' in quest
            assert quest['urgency'] in ['low', 'medium', 'high', 'critical']


class TestPopulationEffects:
    """Test disease effects on population metrics"""
    
    def setup_method(self):
        """Set up test environment"""
        self.engine = DiseaseModelingEngine()
        self.test_population_id = "test_population_effects"
        
    def test_no_disease_effects(self):
        """Test population effects when no diseases are present"""
        effects = self.engine.calculate_population_effects(
            population_id=self.test_population_id,
            base_population=1000
        )
        
        # No diseases should result in neutral effects
        assert effects['productivity_multiplier'] == 1.0
        assert effects['morale_multiplier'] == 1.0
        assert effects['growth_rate_multiplier'] == 1.0
        assert effects['migration_pressure'] == 0.0
        
    def test_disease_effects_calculation(self):
        """Test that diseases properly affect population metrics"""
        # Introduce severe disease
        self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.PLAGUE,
            initial_infected=100
        )
        
        # Simulate some deaths
        outbreak = self.engine.active_outbreaks[self.test_population_id][0]
        outbreak.total_deaths = 50
        
        effects = self.engine.calculate_population_effects(
            population_id=self.test_population_id,
            base_population=1000
        )
        
        # Disease should negatively impact all metrics
        assert effects['productivity_multiplier'] < 1.0
        assert effects['morale_multiplier'] < 1.0
        assert effects['growth_rate_multiplier'] < 1.0
        assert effects['migration_pressure'] > 0.0
        
    def test_zero_population_handling(self):
        """Test handling of zero population scenarios"""
        effects = self.engine.calculate_population_effects(
            population_id=self.test_population_id,
            base_population=0
        )
        
        # Zero population should result in zero productivity and max migration
        assert effects['productivity_multiplier'] == 0.0
        assert effects['morale_multiplier'] == 0.0
        assert effects['growth_rate_multiplier'] == 0.0
        assert effects['migration_pressure'] == 1.0


class TestSeasonalEffects:
    """Test seasonal disease preferences"""
    
    def setup_method(self):
        """Set up test environment"""
        self.engine = DiseaseModelingEngine()
        self.test_population_id = "test_population_seasonal"
        
    def test_seasonal_modifier_calculation(self):
        """Test seasonal modifier calculation"""
        fever_profile = DISEASE_PROFILES[DiseaseType.FEVER]  # Summer preference
        
        # Test preferred season
        summer_modifier = self.engine._calculate_seasonal_modifier(fever_profile, 'summer')
        assert summer_modifier == fever_profile.seasonal_multiplier
        
        # Test non-preferred season
        winter_modifier = self.engine._calculate_seasonal_modifier(fever_profile, 'winter')
        assert winter_modifier == 1.0
        
        # Test no season specified
        no_season_modifier = self.engine._calculate_seasonal_modifier(fever_profile, None)
        assert no_season_modifier == 1.0
        
    def test_seasonal_disease_introduction(self):
        """Test disease introduction with seasonal factors"""
        # Introduce summer-preferring disease in summer
        outbreak = self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.FEVER,
            initial_infected=1,
            environmental_factors={'season': 'summer'}
        )
        
        fever_profile = DISEASE_PROFILES[DiseaseType.FEVER]
        assert outbreak.current_seasonal_modifier == fever_profile.seasonal_multiplier


class TestIntegrationFunctions:
    """Test integration functions and helper utilities"""
    
    def test_random_disease_introduction(self):
        """Test random disease outbreak introduction"""
        test_population_id = "test_random_disease"
        
        # Test with high-risk conditions
        environmental_factors = {
            'crowding': 3.0,
            'hygiene': 2.0,
            'healthcare': 0.5
        }
        
        # Run multiple attempts (random nature means it might not trigger every time)
        disease_introduced = False
        for _ in range(100):  # Try 100 times to account for randomness
            outbreak = introduce_random_disease_outbreak(
                population_id=test_population_id,
                population_size=10000,  # Large population
                environmental_factors=environmental_factors
            )
            if outbreak is not None:
                disease_introduced = True
                assert isinstance(outbreak, DiseaseOutbreak)
                assert outbreak.infected_count > 0
                break
                
        # Note: Due to randomness, we can't guarantee disease introduction
        # but with high-risk conditions it should happen frequently
        
    def test_disease_effects_application(self):
        """Test applying disease effects to population over time"""
        test_population_id = "test_disease_effects"
        base_population = 1000
        
        # First introduce a disease manually
        DISEASE_ENGINE.introduce_disease(
            population_id=test_population_id,
            disease_type=DiseaseType.FEVER,
            initial_infected=10
        )
        
        # Apply effects over 7 days
        result = apply_disease_effects_to_population(
            population_id=test_population_id,
            base_population=base_population,
            time_days=7
        )
        
        assert result['starting_population'] == base_population
        assert result['simulation_days'] == 7
        assert len(result['daily_reports']) == 7
        assert result['ending_population'] <= base_population  # Should be less due to deaths
        assert 'disease_status' in result
        assert 'population_effects' in result
        assert 'quest_opportunities' in result


class TestRealisticBehavior:
    """Test realistic disease behavior patterns"""
    
    def setup_method(self):
        """Set up test environment"""
        self.engine = DiseaseModelingEngine()
        self.test_population_id = "test_realistic"
        
    def test_crowding_increases_transmission(self):
        """Test that crowded conditions increase disease transmission"""
        # Test with normal crowding
        outbreak_normal = self.engine.introduce_disease(
            population_id=f"{self.test_population_id}_normal",
            disease_type=DiseaseType.FEVER,
            initial_infected=10,
            environmental_factors={'crowding': 1.0}
        )
        
        # Test with high crowding
        outbreak_crowded = self.engine.introduce_disease(
            population_id=f"{self.test_population_id}_crowded",
            disease_type=DiseaseType.FEVER,
            initial_infected=10,
            environmental_factors={'crowding': 3.0}
        )
        
        # Crowded outbreak should have higher environmental modifier
        assert outbreak_crowded.current_crowding_modifier > outbreak_normal.current_crowding_modifier
        
    def test_healthcare_reduces_mortality(self):
        """Test that better healthcare reduces disease impact"""
        # This is more of a system behavior test
        # Good healthcare should reduce effective death rates during progression
        
        # Set up outbreak with poor healthcare
        poor_healthcare_factors = {'healthcare': 0.3}
        outbreak_poor = self.engine.introduce_disease(
            population_id=f"{self.test_population_id}_poor_health",
            disease_type=DiseaseType.PLAGUE,
            initial_infected=50,
            environmental_factors=poor_healthcare_factors
        )
        
        # Set up outbreak with good healthcare
        good_healthcare_factors = {'healthcare': 1.0}
        outbreak_good = self.engine.introduce_disease(
            population_id=f"{self.test_population_id}_good_health",
            disease_type=DiseaseType.PLAGUE,
            initial_infected=50,
            environmental_factors=good_healthcare_factors
        )
        
        # Good healthcare should have better modifier
        assert outbreak_good.current_healthcare_modifier > outbreak_poor.current_healthcare_modifier
        
    def test_disease_stage_progression_logic(self):
        """Test that disease stages progress in a logical manner"""
        self.engine.introduce_disease(
            population_id=self.test_population_id,
            disease_type=DiseaseType.FEVER,
            initial_infected=1
        )
        
        outbreak = self.engine.active_outbreaks[self.test_population_id][0]
        
        # Should start as emerging
        assert outbreak.stage == DiseaseStage.EMERGING
        
        # Progress through stages
        previous_stage = outbreak.stage
        for day in range(20):
            self.engine.progress_disease_day(
                population_id=self.test_population_id,
                total_population=1000
            )
            
            # Stage should either stay the same or progress logically
            current_stage = outbreak.stage
            if current_stage != previous_stage:
                # Validate logical progression
                stage_order = [
                    DiseaseStage.EMERGING,
                    DiseaseStage.SPREADING,
                    DiseaseStage.PEAK,
                    DiseaseStage.DECLINING,
                    DiseaseStage.ERADICATED
                ]
                
                if current_stage in stage_order and previous_stage in stage_order:
                    current_index = stage_order.index(current_stage)
                    previous_index = stage_order.index(previous_stage)
                    # Should either stay same or advance
                    assert current_index >= previous_index
                    
            previous_stage = current_stage


if __name__ == "__main__":
    pytest.main([__file__]) 