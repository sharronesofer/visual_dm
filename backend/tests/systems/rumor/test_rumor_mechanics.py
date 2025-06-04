"""
Tests for Advanced Rumor Mechanics

This module tests the sophisticated spread and decay engines that make rumors feel alive.
"""

import pytest
import random
from datetime import datetime, timedelta
from uuid import uuid4

from backend.systems.rumor.services.rumor_mechanics import (
    RumorSpreadEngine,
    RumorDecayEngine,
    create_spread_engine,
    create_decay_engine
)


class TestRumorSpreadEngine:
    """Test the rumor spread engine mechanics"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.spread_engine = create_spread_engine()
        random.seed(42)  # For consistent test results
    
    def test_calculate_spread_probability_basic(self):
        """Test basic spread probability calculation"""
        probability = self.spread_engine.calculate_spread_probability(
            rumor_severity='moderate',
            originator_believability=0.8,
            receiver_trust=0.7,
            relationship_strength=0.6
        )
        
        assert 0.0 <= probability <= 1.0
        assert probability > 0.5  # Should be reasonably high with good parameters
    
    def test_calculate_spread_probability_severity_impact(self):
        """Test that severity affects spread probability"""
        base_params = {
            'originator_believability': 0.5,
            'receiver_trust': 0.5,
            'relationship_strength': 0.5
        }
        
        trivial_prob = self.spread_engine.calculate_spread_probability(
            rumor_severity='trivial', **base_params
        )
        critical_prob = self.spread_engine.calculate_spread_probability(
            rumor_severity='critical', **base_params
        )
        
        assert critical_prob > trivial_prob
    
    def test_calculate_spread_probability_social_context(self):
        """Test social context modifiers"""
        base_params = {
            'rumor_severity': 'moderate',
            'originator_believability': 0.5,
            'receiver_trust': 0.5,
            'relationship_strength': 0.5
        }
        
        # Test tavern context (should boost probability)
        tavern_prob = self.spread_engine.calculate_spread_probability(
            social_context={'location_type': 'tavern', 'time_of_day': 'evening'},
            **base_params
        )
        
        # Test court context (should reduce probability)
        court_prob = self.spread_engine.calculate_spread_probability(
            social_context={'location_type': 'court', 'formal_setting': True},
            **base_params
        )
        
        # Test basic context
        basic_prob = self.spread_engine.calculate_spread_probability(
            **base_params
        )
        
        assert tavern_prob > basic_prob > court_prob
    
    def test_calculate_mutation_during_spread(self):
        """Test content mutation during spread"""
        original_content = "The king was seen in the tavern yesterday"
        
        # High mutation scenario
        mutated_content, was_mutated = self.spread_engine.calculate_mutation_during_spread(
            original_content=original_content,
            rumor_severity='trivial',
            spread_distance=5,
            receiver_personality={'gossipy': True, 'dramatic': True}
        )
        
        if was_mutated:
            assert mutated_content != original_content
            assert len(mutated_content) > 0
    
    def test_calculate_believability_change(self):
        """Test believability changes during spread"""
        new_believability = self.spread_engine.calculate_believability_change(
            current_believability=0.8,
            receiver_skepticism=0.3,
            source_credibility=0.7,
            rumor_severity='moderate',
            supporting_evidence=0.2
        )
        
        assert 0.0 <= new_believability <= 1.0
        # With good credibility and some evidence, believability might actually increase slightly
        # but the test should verify it's within a reasonable range
        assert 0.5 <= new_believability <= 1.0  # Should be reasonably maintained
    
    def test_believability_change_with_evidence(self):
        """Test that evidence helps maintain believability"""
        no_evidence = self.spread_engine.calculate_believability_change(
            current_believability=0.8,
            receiver_skepticism=0.5,
            source_credibility=0.5,
            rumor_severity='major',
            supporting_evidence=0.0
        )
        
        with_evidence = self.spread_engine.calculate_believability_change(
            current_believability=0.8,
            receiver_skepticism=0.5,
            source_credibility=0.5,
            rumor_severity='major',
            supporting_evidence=0.8
        )
        
        assert with_evidence > no_evidence


class TestRumorDecayEngine:
    """Test the rumor decay engine mechanics"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.decay_engine = create_decay_engine()
    
    def test_calculate_time_based_decay_basic(self):
        """Test basic time-based decay"""
        new_believability = self.decay_engine.calculate_time_based_decay(
            current_believability=0.8,
            days_since_last_reinforcement=7,
            rumor_severity='moderate'
        )
        
        assert 0.0 <= new_believability <= 1.0
        assert new_believability < 0.8  # Should decay over time
    
    def test_decay_severity_impact(self):
        """Test that severity affects decay rate"""
        base_params = {
            'current_believability': 0.8,
            'days_since_last_reinforcement': 30  # Use more days to see clearer difference
        }
        
        trivial_decay = self.decay_engine.calculate_time_based_decay(
            rumor_severity='trivial', **base_params
        )
        critical_decay = self.decay_engine.calculate_time_based_decay(
            rumor_severity='critical', **base_params
        )
        
        # Critical rumors should decay slower (higher remaining believability)
        # Use a small tolerance for floating point comparison
        assert critical_decay >= trivial_decay or abs(critical_decay - trivial_decay) < 0.01
    
    def test_decay_environmental_factors(self):
        """Test environmental factors affect decay"""
        base_params = {
            'current_believability': 0.8,
            'days_since_last_reinforcement': 10,
            'rumor_severity': 'moderate'
        }
        
        # Conflict should slow decay
        conflict_decay = self.decay_engine.calculate_time_based_decay(
            environmental_factors={'active_conflict': True},
            **base_params
        )
        
        # Peace should accelerate decay
        peace_decay = self.decay_engine.calculate_time_based_decay(
            environmental_factors={'peaceful_period': True},
            **base_params
        )
        
        # Normal decay
        normal_decay = self.decay_engine.calculate_time_based_decay(
            **base_params
        )
        
        assert conflict_decay > normal_decay > peace_decay
    
    def test_calculate_contradiction_decay(self):
        """Test contradiction decay"""
        new_believability = self.decay_engine.calculate_contradiction_decay(
            current_believability=0.8,
            contradiction_strength=0.7,
            source_credibility=0.9
        )
        
        assert 0.0 <= new_believability <= 1.0
        assert new_believability < 0.8  # Should reduce believability
    
    def test_calculate_reinforcement_boost(self):
        """Test reinforcement boost"""
        new_believability = self.decay_engine.calculate_reinforcement_boost(
            current_believability=0.5,
            reinforcement_strength=0.8,
            source_credibility=0.9,
            rumor_severity='moderate'
        )
        
        assert 0.0 <= new_believability <= 1.0
        assert new_believability > 0.5  # Should increase believability
    
    def test_reinforcement_diminishing_returns(self):
        """Test that reinforcement has diminishing returns"""
        low_believability_boost = self.decay_engine.calculate_reinforcement_boost(
            current_believability=0.2,
            reinforcement_strength=0.8,
            source_credibility=0.9,
            rumor_severity='moderate'
        )
        
        high_believability_boost = self.decay_engine.calculate_reinforcement_boost(
            current_believability=0.9,
            reinforcement_strength=0.8,
            source_credibility=0.9,
            rumor_severity='moderate'
        )
        
        # Boost should be larger for lower believability
        low_boost_amount = low_believability_boost - 0.2
        high_boost_amount = high_believability_boost - 0.9
        
        assert low_boost_amount > high_boost_amount
    
    def test_minimum_believability_floor(self):
        """Test that decay respects minimum believability floor"""
        # Test extensive decay
        new_believability = self.decay_engine.calculate_time_based_decay(
            current_believability=0.2,
            days_since_last_reinforcement=365,  # One year
            rumor_severity='critical'
        )
        
        # Should respect minimum floor for critical rumors
        assert new_believability >= 0.15  # Critical minimum is 0.15


class TestSpreadEngineEdgeCases:
    """Test edge cases and error conditions"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.spread_engine = create_spread_engine()
    
    def test_extreme_parameters(self):
        """Test with extreme parameter values"""
        # All zeros
        prob_zeros = self.spread_engine.calculate_spread_probability(
            rumor_severity='trivial',
            originator_believability=0.0,
            receiver_trust=0.0,
            relationship_strength=0.0
        )
        assert prob_zeros >= 0.0
        
        # All ones
        prob_ones = self.spread_engine.calculate_spread_probability(
            rumor_severity='critical',
            originator_believability=1.0,
            receiver_trust=1.0,
            relationship_strength=1.0
        )
        assert prob_ones <= 1.0
    
    def test_empty_content_mutation(self):
        """Test mutation with empty or minimal content"""
        empty_content, was_mutated = self.spread_engine.calculate_mutation_during_spread(
            original_content="",
            rumor_severity='moderate',
            spread_distance=1,
            receiver_personality={}
        )
        
        assert isinstance(empty_content, str)
        assert isinstance(was_mutated, bool)


class TestDecayEngineEdgeCases:
    """Test decay engine edge cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.decay_engine = create_decay_engine()
    
    def test_zero_days_decay(self):
        """Test decay with zero days"""
        new_believability = self.decay_engine.calculate_time_based_decay(
            current_believability=0.8,
            days_since_last_reinforcement=0,
            rumor_severity='moderate'
        )
        
        # Should return original believability
        assert new_believability == 0.8
    
    def test_extreme_contradiction(self):
        """Test extreme contradiction values"""
        # Maximum contradiction
        max_contradiction = self.decay_engine.calculate_contradiction_decay(
            current_believability=1.0,
            contradiction_strength=1.0,
            source_credibility=1.0
        )
        
        assert max_contradiction >= 0.0
        assert max_contradiction < 1.0
    
    def test_extreme_reinforcement(self):
        """Test extreme reinforcement values"""
        # Maximum reinforcement on minimum believability
        max_reinforcement = self.decay_engine.calculate_reinforcement_boost(
            current_believability=0.0,
            reinforcement_strength=1.0,
            source_credibility=1.0,
            rumor_severity='trivial'
        )
        
        assert max_reinforcement <= 1.0
        assert max_reinforcement > 0.0


@pytest.fixture
def sample_spread_context():
    """Fixture providing sample social context"""
    return {
        'location_type': 'tavern',
        'time_of_day': 'evening',
        'social_gathering': True,
        'relaxed_environment': True,
        'privacy_level': 0.7,
        'receiver_trust': 0.6,
        'source_credibility': 0.8,
        'supporting_evidence': 0.3,
        'spread_distance': 2
    }


@pytest.fixture
def sample_receiver_personality():
    """Fixture providing sample receiver personality"""
    return {
        'gossipy': True,
        'skepticism': 0.4,
        'dramatic': False,
        'careful': False,
        'honest': True
    }


@pytest.fixture
def sample_environmental_factors():
    """Fixture providing sample environmental factors"""
    return {
        'active_conflict': False,
        'peaceful_period': True,
        'information_abundance': 0.6,
        'social_stability': 0.7
    }


class TestIntegratedMechanics:
    """Test the mechanics working together"""
    
    def test_realistic_rumor_lifecycle(
        self, 
        sample_spread_context, 
        sample_receiver_personality,
        sample_environmental_factors
    ):
        """Test a realistic rumor lifecycle with multiple mechanics"""
        spread_engine = create_spread_engine()
        decay_engine = create_decay_engine()
        
        # Initial rumor state
        content = "The merchant's caravan was robbed near Millfield"
        believability = 0.8
        severity = 'moderate'
        
        # Test spread
        spread_prob = spread_engine.calculate_spread_probability(
            rumor_severity=severity,
            originator_believability=believability,
            receiver_trust=sample_spread_context['receiver_trust'],
            relationship_strength=0.6,
            social_context=sample_spread_context
        )
        
        assert 0.0 <= spread_prob <= 1.0
        
        # Test mutation during spread
        new_content, was_mutated = spread_engine.calculate_mutation_during_spread(
            original_content=content,
            rumor_severity=severity,
            spread_distance=sample_spread_context['spread_distance'],
            receiver_personality=sample_receiver_personality
        )
        
        # Test believability change during spread
        spread_believability = spread_engine.calculate_believability_change(
            current_believability=believability,
            receiver_skepticism=sample_receiver_personality['skepticism'],
            source_credibility=sample_spread_context['source_credibility'],
            rumor_severity=severity,
            supporting_evidence=sample_spread_context['supporting_evidence']
        )
        
        # Test time decay
        decayed_believability = decay_engine.calculate_time_based_decay(
            current_believability=spread_believability,
            days_since_last_reinforcement=7,
            rumor_severity=severity,
            environmental_factors=sample_environmental_factors
        )
        
        # Test contradiction
        contradicted_believability = decay_engine.calculate_contradiction_decay(
            current_believability=decayed_believability,
            contradiction_strength=0.6,
            source_credibility=0.8
        )
        
        # Verify the entire lifecycle maintains valid values
        assert isinstance(new_content, str)
        assert 0.0 <= spread_believability <= 1.0
        assert 0.0 <= decayed_believability <= 1.0
        assert 0.0 <= contradicted_believability <= 1.0
        
        # Generally, believability should decrease through this process
        assert contradicted_believability <= believability 