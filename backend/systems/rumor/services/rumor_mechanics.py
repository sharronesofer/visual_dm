"""
Advanced Rumor Mechanics - Spread & Decay Engine

This module implements the core mechanics that make rumors feel alive:
- Sophisticated spread calculations based on relationships and context
- Realistic decay over time with environmental factors
- Believability modeling with trust networks
- Mutation tracking and content evolution
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID

from backend.systems.rumor.utils.rumor_rules import get_rumor_config


class RumorSpreadEngine:
    """Advanced engine for calculating rumor spread mechanics"""
    
    def __init__(self):
        self.config = get_rumor_config()
    
    def calculate_spread_probability(
        self,
        rumor_severity: str,
        originator_believability: float,
        receiver_trust: float,
        relationship_strength: float,
        social_context: Dict[str, Any] = None
    ) -> float:
        """
        Calculate the probability that a rumor will spread from one entity to another.
        
        Args:
            rumor_severity: Severity level of the rumor
            originator_believability: How believable the originator is (0.0-1.0)
            receiver_trust: How much the receiver trusts the originator (0.0-1.0)
            relationship_strength: Strength of relationship between entities (0.0-1.0)
            social_context: Additional context factors
            
        Returns:
            Probability of spread (0.0-1.0)
        """
        social_context = social_context or {}
        
        # Base spread probability from severity
        base_probability = self._get_base_spread_probability(rumor_severity)
        
        # Trust and believability factors
        trust_factor = (receiver_trust + originator_believability) / 2.0
        
        # Relationship strength boost
        relationship_boost = relationship_strength * 0.3
        
        # Social context modifiers
        context_modifier = self._calculate_context_modifier(social_context)
        
        # Environmental factors
        environment_modifier = self._calculate_environment_modifier(social_context)
        
        # Calculate final probability
        final_probability = (
            base_probability * 
            trust_factor * 
            (1.0 + relationship_boost) * 
            context_modifier * 
            environment_modifier
        )
        
        # Clamp to valid range
        return max(0.0, min(1.0, final_probability))
    
    def calculate_mutation_during_spread(
        self,
        original_content: str,
        rumor_severity: str,
        spread_distance: int,
        receiver_personality: Dict[str, Any] = None
    ) -> Tuple[str, bool]:
        """
        Calculate if and how a rumor mutates during spread.
        
        Args:
            original_content: Original rumor content
            rumor_severity: Severity level
            spread_distance: How many "hops" from the original source
            receiver_personality: Personality traits that affect mutation
            
        Returns:
            Tuple of (new_content, was_mutated)
        """
        receiver_personality = receiver_personality or {}
        
        # Calculate mutation probability
        mutation_chance = self._calculate_mutation_chance(
            rumor_severity, spread_distance, receiver_personality
        )
        
        # Roll for mutation
        if random.random() > mutation_chance:
            return original_content, False
        
        # Apply mutation
        mutated_content = self._apply_content_mutation(
            original_content, rumor_severity, receiver_personality
        )
        
        return mutated_content, True
    
    def calculate_believability_change(
        self,
        current_believability: float,
        receiver_skepticism: float,
        source_credibility: float,
        rumor_severity: str,
        supporting_evidence: float = 0.0
    ) -> float:
        """
        Calculate how believability changes when a rumor spreads to a new person.
        
        Args:
            current_believability: Current believability level (0.0-1.0)
            receiver_skepticism: How skeptical the receiver is (0.0-1.0)
            source_credibility: How credible the source is perceived to be (0.0-1.0)
            rumor_severity: Severity level
            supporting_evidence: Amount of supporting evidence (0.0-1.0)
            
        Returns:
            New believability level (0.0-1.0)
        """
        # Skepticism reduces believability
        skepticism_reduction = receiver_skepticism * 0.2
        
        # Source credibility affects change
        credibility_modifier = source_credibility * 0.3
        
        # Evidence can boost believability
        evidence_boost = supporting_evidence * 0.25
        
        # Severe rumors are harder to believe without evidence
        severity_skepticism = self._get_severity_skepticism_modifier(rumor_severity)
        
        # Calculate new believability
        new_believability = (
            current_believability 
            - skepticism_reduction 
            + credibility_modifier 
            + evidence_boost 
            - severity_skepticism
        )
        
        # Apply natural degradation (Chinese whispers effect)
        degradation = 0.05 * random.uniform(0.5, 1.5)
        new_believability -= degradation
        
        return max(0.0, min(1.0, new_believability))
    
    def _get_base_spread_probability(self, severity: str) -> float:
        """Get base spread probability for severity level"""
        severity_probabilities = {
            'trivial': 0.3,
            'minor': 0.5,
            'moderate': 0.7,
            'major': 0.8,
            'critical': 0.9
        }
        return severity_probabilities.get(severity, 0.5)
    
    def _calculate_context_modifier(self, context: Dict[str, Any]) -> float:
        """Calculate context-based modifiers"""
        modifier = 1.0
        
        # Social gathering boost
        if context.get('social_gathering', False):
            modifier += 0.3
        
        # Alcohol/relaxed environment
        if context.get('relaxed_environment', False):
            modifier += 0.2
        
        # Formal/professional setting reduction
        if context.get('formal_setting', False):
            modifier -= 0.2
        
        # Privacy level (more private = more likely to spread secrets)
        privacy_level = context.get('privacy_level', 0.5)  # 0.0 = public, 1.0 = private
        modifier += privacy_level * 0.2
        
        return max(0.1, modifier)
    
    def _calculate_environment_modifier(self, context: Dict[str, Any]) -> float:
        """Calculate environmental modifiers"""
        modifier = 1.0
        
        # Time of day (rumors spread more at night/evening)
        time_of_day = context.get('time_of_day', 'day')  # 'morning', 'day', 'evening', 'night'
        time_modifiers = {
            'morning': 0.8,
            'day': 1.0,
            'evening': 1.3,
            'night': 1.2
        }
        modifier *= time_modifiers.get(time_of_day, 1.0)
        
        # Location type
        location_type = context.get('location_type', 'neutral')
        location_modifiers = {
            'tavern': 1.5,
            'market': 1.3,
            'court': 0.7,
            'temple': 0.6,
            'battlefield': 1.4,
            'neutral': 1.0
        }
        modifier *= location_modifiers.get(location_type, 1.0)
        
        return modifier
    
    def _calculate_mutation_chance(
        self, 
        severity: str, 
        spread_distance: int, 
        personality: Dict[str, Any]
    ) -> float:
        """Calculate chance of mutation during spread"""
        config = self.config.get('mutation', {})
        base_chance = config.get('base_chance', 0.2)
        severity_multipliers = config.get('severity_multipliers', {})
        
        # Base mutation chance modified by severity
        mutation_chance = base_chance * severity_multipliers.get(severity, 1.0)
        
        # Distance increases mutation chance (Chinese whispers)
        distance_factor = 1.0 + (spread_distance * 0.1)
        mutation_chance *= distance_factor
        
        # Personality factors
        if personality.get('gossipy', False):
            mutation_chance *= 1.4
        if personality.get('dramatic', False):
            mutation_chance *= 1.3
        if personality.get('careful', False):
            mutation_chance *= 0.7
        if personality.get('honest', False):
            mutation_chance *= 0.8
        
        return min(1.0, mutation_chance)
    
    def _apply_content_mutation(
        self, 
        content: str, 
        severity: str, 
        personality: Dict[str, Any]
    ) -> str:
        """Apply actual content mutation using templates"""
        config = self.config.get('mutation', {})
        templates = config.get('templates', {})
        
        mutated_content = content
        
        # Apply uncertainty phrases
        if random.random() < 0.4:
            uncertainty_phrases = templates.get('uncertainty_phrases', [])
            if uncertainty_phrases:
                phrase = random.choice(uncertainty_phrases)
                mutated_content = f"{phrase} {mutated_content}"
        
        # Apply location vagueness
        if random.random() < 0.3:
            location_vagueness = templates.get('location_vagueness', [])
            if location_vagueness:
                # Simple replacement of specific locations with vague terms
                for vague_term in location_vagueness:
                    if random.random() < 0.5:
                        # This is a simplified example - in practice you'd use more sophisticated NLP
                        mutated_content = mutated_content.replace(' in ', f' {vague_term} ')
                        break
        
        # Apply time vagueness  
        if random.random() < 0.3:
            time_vagueness = templates.get('time_vagueness', [])
            if time_vagueness:
                time_phrase = random.choice(time_vagueness)
                # Add time vagueness to the beginning or replace specific time references
                if 'yesterday' in mutated_content or 'today' in mutated_content:
                    mutated_content = mutated_content.replace('yesterday', time_phrase)
                    mutated_content = mutated_content.replace('today', time_phrase)
                elif random.random() < 0.3:
                    mutated_content = f"{time_phrase}, {mutated_content}"
        
        # Apply intensity modifiers based on personality
        intensity_modifiers = templates.get('intensity_modifiers', {})
        if personality.get('dramatic', False) and random.random() < 0.4:
            amplifiers = intensity_modifiers.get('amplify', [])
            if amplifiers:
                amplifier = random.choice(amplifiers)
                mutated_content = f"{amplifier} {mutated_content}"
        elif personality.get('cautious', False) and random.random() < 0.4:
            diminishers = intensity_modifiers.get('diminish', [])
            if diminishers:
                diminisher = random.choice(diminishers)
                mutated_content = f"{diminisher} {mutated_content}"
        
        return mutated_content
    
    def _get_severity_skepticism_modifier(self, severity: str) -> float:
        """Get skepticism modifier based on severity"""
        modifiers = {
            'trivial': 0.0,
            'minor': 0.05,
            'moderate': 0.1,
            'major': 0.2,
            'critical': 0.3
        }
        return modifiers.get(severity, 0.1)


class RumorDecayEngine:
    """Advanced engine for calculating rumor decay over time"""
    
    def __init__(self):
        self.config = get_rumor_config()
    
    def calculate_time_based_decay(
        self,
        current_believability: float,
        days_since_last_reinforcement: int,
        rumor_severity: str,
        environmental_factors: Dict[str, Any] = None
    ) -> float:
        """
        Calculate how much believability decays over time.
        
        Args:
            current_believability: Current believability level
            days_since_last_reinforcement: Days since rumor was last reinforced
            rumor_severity: Severity level
            environmental_factors: Environmental context affecting decay
            
        Returns:
            New believability level after decay
        """
        environmental_factors = environmental_factors or {}
        
        # Get base decay rate
        decay_config = self.config.get('decay', {})
        base_rate = decay_config.get('base_rate_per_day', 0.05)
        severity_multipliers = decay_config.get('severity_multipliers', {})
        
        # Severity affects decay rate (more severe = slower decay)
        severity_multiplier = severity_multipliers.get(rumor_severity, 1.0)
        daily_decay_rate = base_rate / severity_multiplier
        
        # Environmental factors
        environment_modifier = self._calculate_decay_environment_modifier(environmental_factors)
        adjusted_decay_rate = daily_decay_rate * environment_modifier
        
        # Apply logarithmic decay (fast initial decay, then slower)
        if days_since_last_reinforcement <= 0:
            return current_believability
        
        # Logarithmic decay formula: new_value = current * exp(-rate * log(days + 1))
        decay_factor = math.exp(-adjusted_decay_rate * math.log(days_since_last_reinforcement + 1))
        new_believability = current_believability * decay_factor
        
        # Minimum believability floor (some rumors never completely die)
        min_believability = self._get_minimum_believability(rumor_severity)
        
        return max(min_believability, new_believability)
    
    def calculate_contradiction_decay(
        self,
        current_believability: float,
        contradiction_strength: float,
        source_credibility: float
    ) -> float:
        """
        Calculate believability loss when a rumor is contradicted.
        
        Args:
            current_believability: Current believability level
            contradiction_strength: Strength of the contradiction (0.0-1.0)
            source_credibility: Credibility of the contradicting source (0.0-1.0)
            
        Returns:
            New believability level
        """
        # Calculate decay based on contradiction strength and source credibility
        decay_amount = contradiction_strength * source_credibility * 0.4
        
        # Apply decay with some randomness
        actual_decay = decay_amount * random.uniform(0.7, 1.3)
        
        new_believability = current_believability - actual_decay
        return max(0.0, new_believability)
    
    def calculate_reinforcement_boost(
        self,
        current_believability: float,
        reinforcement_strength: float,
        source_credibility: float,
        rumor_severity: str
    ) -> float:
        """
        Calculate believability boost when a rumor is reinforced.
        
        Args:
            current_believability: Current believability level
            reinforcement_strength: Strength of the reinforcement (0.0-1.0)
            source_credibility: Credibility of the reinforcing source (0.0-1.0)
            rumor_severity: Severity level
            
        Returns:
            New believability level
        """
        # Calculate boost
        boost_amount = reinforcement_strength * source_credibility * 0.3
        
        # Severe rumors are harder to reinforce without strong evidence
        severity_resistance = self._get_severity_resistance(rumor_severity)
        adjusted_boost = boost_amount * (1.0 - severity_resistance)
        
        # Diminishing returns - harder to boost already high believability
        diminishing_factor = 1.0 - (current_believability * 0.5)
        final_boost = adjusted_boost * diminishing_factor
        
        new_believability = current_believability + final_boost
        return min(1.0, new_believability)
    
    def _calculate_decay_environment_modifier(self, factors: Dict[str, Any]) -> float:
        """Calculate environmental modifiers for decay"""
        modifier = 1.0
        
        # Active conflict/war slows decay of related rumors
        if factors.get('active_conflict', False):
            modifier *= 0.7
        
        # Peaceful times accelerate decay
        if factors.get('peaceful_period', False):
            modifier *= 1.3
        
        # Information availability affects decay
        info_abundance = factors.get('information_abundance', 0.5)  # 0.0 = scarce, 1.0 = abundant
        modifier *= (1.0 + info_abundance * 0.4)  # More info = faster decay
        
        # Social stability
        stability = factors.get('social_stability', 0.5)  # 0.0 = chaotic, 1.0 = stable
        modifier *= (1.0 + stability * 0.2)  # More stable = faster decay
        
        return modifier
    
    def _get_minimum_believability(self, severity: str) -> float:
        """Get minimum believability floor for severity level"""
        minimums = {
            'trivial': 0.0,
            'minor': 0.02,
            'moderate': 0.05,
            'major': 0.1,
            'critical': 0.15
        }
        return minimums.get(severity, 0.05)
    
    def _get_severity_resistance(self, severity: str) -> float:
        """Get resistance to reinforcement based on severity"""
        resistances = {
            'trivial': 0.1,
            'minor': 0.2,
            'moderate': 0.3,
            'major': 0.4,
            'critical': 0.5
        }
        return resistances.get(severity, 0.3)


# Factory functions for dependency injection
def create_spread_engine() -> RumorSpreadEngine:
    """Create rumor spread engine instance"""
    return RumorSpreadEngine()


def create_decay_engine() -> RumorDecayEngine:
    """Create rumor decay engine instance"""
    return RumorDecayEngine() 