"""
Personality Integration System

This module integrates faction personality attributes into diplomatic AI decision-making.
It translates hidden attributes (ambition, integrity, pragmatism, etc.) into behavioral patterns
and decision modifiers for realistic and varied diplomatic behavior.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
import logging
import math

logger = logging.getLogger(__name__)

class PersonalityTrait(Enum):
    """Faction personality traits that influence diplomatic behavior"""
    
    AMBITION = "hidden_ambition"           # Drive for power and expansion
    INTEGRITY = "hidden_integrity"         # Honesty and treaty adherence
    DISCIPLINE = "hidden_discipline"       # Organization and strategic thinking
    IMPULSIVITY = "hidden_impulsivity"     # Quick reactions vs careful planning
    PRAGMATISM = "hidden_pragmatism"       # Practical vs idealistic approach
    RESILIENCE = "hidden_resilience"       # Recovery from setbacks

class BehaviorPattern(Enum):
    """Behavioral patterns derived from personality combinations"""
    
    AGGRESSIVE_EXPANSIONIST = "aggressive_expansionist"     # High ambition, low integrity
    HONORABLE_WARRIOR = "honorable_warrior"                 # High ambition, high integrity
    CAUTIOUS_DIPLOMAT = "cautious_diplomat"                 # Low impulsivity, high discipline
    OPPORTUNISTIC_TRADER = "opportunistic_trader"          # High pragmatism, moderate ambition
    ISOLATIONIST = "isolationist"                          # Low ambition, high discipline
    UNPREDICTABLE_WILDCARD = "unpredictable_wildcard"      # High impulsivity, low discipline
    RELIABLE_ALLY = "reliable_ally"                        # High integrity, high resilience
    SCHEMING_MANIPULATOR = "scheming_manipulator"          # High ambition, low integrity, high discipline

@dataclass
class PersonalityProfile:
    """Complete personality profile for a faction"""
    
    faction_id: UUID
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Core attributes (0-6 scale)
    ambition: int = 3
    integrity: int = 3
    discipline: int = 3
    impulsivity: int = 3
    pragmatism: int = 3
    resilience: int = 3
    
    # Derived characteristics
    primary_behavior_pattern: BehaviorPattern = BehaviorPattern.CAUTIOUS_DIPLOMAT
    secondary_patterns: List[BehaviorPattern] = field(default_factory=list)
    
    # Decision modifiers (how personality affects different decision types)
    risk_tolerance: float = 0.5         # 0.0 = very risk averse, 1.0 = very risk seeking
    aggression_level: float = 0.5       # 0.0 = very peaceful, 1.0 = very aggressive
    cooperation_tendency: float = 0.5   # 0.0 = prefers isolation, 1.0 = seeks cooperation
    treaty_reliability: float = 0.5     # 0.0 = breaks treaties easily, 1.0 = very reliable
    negotiation_style: str = "balanced" # "aggressive", "cooperative", "balanced"
    
    # Situational modifiers
    stress_response: str = "measured"    # "panic", "aggressive", "measured", "withdrawal"
    success_response: str = "steady"     # "overconfident", "steady", "cautious"
    
    def get_attribute_score(self, trait: PersonalityTrait) -> int:
        """Get the score for a specific personality trait"""
        return getattr(self, trait.value.replace("hidden_", ""))
    
    def is_high_in_trait(self, trait: PersonalityTrait, threshold: int = 4) -> bool:
        """Check if faction scores high in a specific trait"""
        return self.get_attribute_score(trait) >= threshold
    
    def is_low_in_trait(self, trait: PersonalityTrait, threshold: int = 3) -> bool:
        """Check if faction scores low in a specific trait"""
        return self.get_attribute_score(trait) <= threshold
    
    def get_dominant_traits(self, count: int = 2) -> List[PersonalityTrait]:
        """Get the most prominent personality traits"""
        trait_scores = [
            (PersonalityTrait.AMBITION, self.ambition),
            (PersonalityTrait.INTEGRITY, self.integrity),
            (PersonalityTrait.DISCIPLINE, self.discipline),
            (PersonalityTrait.IMPULSIVITY, self.impulsivity),
            (PersonalityTrait.PRAGMATISM, self.pragmatism),
            (PersonalityTrait.RESILIENCE, self.resilience)
        ]
        
        # Sort by score and return top traits
        trait_scores.sort(key=lambda x: x[1], reverse=True)
        return [trait for trait, score in trait_scores[:count]]

@dataclass
class DecisionModifier:
    """Modifiers applied to decisions based on personality"""
    
    decision_type: str
    faction_id: UUID
    
    # Probability modifiers
    success_probability_modifier: float = 0.0    # Added to base success probability
    risk_assessment_modifier: float = 0.0        # Added to risk scores
    
    # Behavioral modifiers
    aggression_modifier: float = 0.0             # How much more/less aggressive
    cooperation_modifier: float = 0.0            # How much more/less cooperative
    patience_modifier: float = 0.0               # How much more/less patient
    
    # Decision preferences
    preferred_actions: List[str] = field(default_factory=list)
    avoided_actions: List[str] = field(default_factory=list)
    
    # Timing modifiers
    urgency_modifier: float = 0.0                # How much more/less urgent
    planning_time_modifier: float = 0.0          # How much more/less planning time needed

class PersonalityIntegrator:
    """Integrates personality traits into diplomatic AI decision-making"""
    
    def __init__(self, faction_service=None):
        """Initialize with faction service for accessing personality data"""
        self.faction_service = faction_service
        self.personality_cache: Dict[UUID, PersonalityProfile] = {}
        self.cache_duration = 3600  # Cache for 1 hour
    
    def get_personality_profile(self, faction_id: UUID, force_refresh: bool = False) -> PersonalityProfile:
        """Get or create personality profile for a faction"""
        
        # Check cache first
        if not force_refresh and faction_id in self.personality_cache:
            cached = self.personality_cache[faction_id]
            if (datetime.utcnow() - cached.evaluated_at).total_seconds() < self.cache_duration:
                return cached
        
        # Create new profile
        profile = PersonalityProfile(faction_id=faction_id)
        
        # Get faction attributes from service
        if self.faction_service:
            try:
                faction_data = self.faction_service.get_faction(faction_id)
                if faction_data:
                    # Extract hidden attributes
                    hidden_attrs = faction_data.get("hidden_attributes", {})
                    profile.ambition = hidden_attrs.get("hidden_ambition", 3)
                    profile.integrity = hidden_attrs.get("hidden_integrity", 3)
                    profile.discipline = hidden_attrs.get("hidden_discipline", 3)
                    profile.impulsivity = hidden_attrs.get("hidden_impulsivity", 3)
                    profile.pragmatism = hidden_attrs.get("hidden_pragmatism", 3)
                    profile.resilience = hidden_attrs.get("hidden_resilience", 3)
            except Exception as e:
                logger.warning(f"Error getting faction attributes for {faction_id}: {e}")
        
        # Calculate derived characteristics
        self._calculate_behavior_patterns(profile)
        self._calculate_decision_modifiers(profile)
        self._calculate_situational_responses(profile)
        
        # Cache the profile
        self.personality_cache[faction_id] = profile
        
        logger.debug(f"Generated personality profile for faction {faction_id}: "
                    f"pattern={profile.primary_behavior_pattern.value}")
        
        return profile
    
    def _calculate_behavior_patterns(self, profile: PersonalityProfile) -> None:
        """Calculate primary and secondary behavior patterns"""
        
        patterns = []
        
        # Aggressive Expansionist: High ambition, low integrity
        if profile.ambition >= 5 and profile.integrity <= 2:
            patterns.append((BehaviorPattern.AGGRESSIVE_EXPANSIONIST, 0.9))
        
        # Honorable Warrior: High ambition, high integrity
        elif profile.ambition >= 4 and profile.integrity >= 5:
            patterns.append((BehaviorPattern.HONORABLE_WARRIOR, 0.8))
        
        # Cautious Diplomat: Low impulsivity, high discipline
        elif profile.impulsivity <= 2 and profile.discipline >= 4:
            patterns.append((BehaviorPattern.CAUTIOUS_DIPLOMAT, 0.8))
        
        # Opportunistic Trader: High pragmatism, moderate ambition
        elif profile.pragmatism >= 5 and 3 <= profile.ambition <= 4:
            patterns.append((BehaviorPattern.OPPORTUNISTIC_TRADER, 0.7))
        
        # Isolationist: Low ambition, high discipline
        elif profile.ambition <= 2 and profile.discipline >= 4:
            patterns.append((BehaviorPattern.ISOLATIONIST, 0.8))
        
        # Unpredictable Wildcard: High impulsivity, low discipline
        elif profile.impulsivity >= 5 and profile.discipline <= 2:
            patterns.append((BehaviorPattern.UNPREDICTABLE_WILDCARD, 0.9))
        
        # Reliable Ally: High integrity, high resilience
        elif profile.integrity >= 5 and profile.resilience >= 4:
            patterns.append((BehaviorPattern.RELIABLE_ALLY, 0.8))
        
        # Scheming Manipulator: High ambition, low integrity, high discipline
        elif profile.ambition >= 4 and profile.integrity <= 2 and profile.discipline >= 4:
            patterns.append((BehaviorPattern.SCHEMING_MANIPULATOR, 0.9))
        
        # Default to cautious diplomat if no clear pattern
        if not patterns:
            patterns.append((BehaviorPattern.CAUTIOUS_DIPLOMAT, 0.5))
        
        # Sort by strength and assign primary/secondary
        patterns.sort(key=lambda x: x[1], reverse=True)
        profile.primary_behavior_pattern = patterns[0][0]
        
        # Add secondary patterns (weaker matches)
        profile.secondary_patterns = [pattern for pattern, strength in patterns[1:3] if strength > 0.4]
    
    def _calculate_decision_modifiers(self, profile: PersonalityProfile) -> None:
        """Calculate how personality affects decision-making"""
        
        # Risk tolerance based on ambition, impulsivity, and resilience
        risk_base = (profile.ambition + profile.impulsivity + profile.resilience) / 18.0
        risk_caution = (profile.discipline + profile.integrity) / 12.0
        profile.risk_tolerance = max(0.1, min(0.9, risk_base - risk_caution * 0.3))
        
        # Aggression level based on ambition and impulsivity, moderated by integrity
        aggression_base = (profile.ambition + profile.impulsivity) / 12.0
        aggression_moderation = profile.integrity / 6.0
        profile.aggression_level = max(0.1, min(0.9, aggression_base - aggression_moderation * 0.2))
        
        # Cooperation tendency based on integrity and pragmatism, reduced by high ambition
        cooperation_base = (profile.integrity + profile.pragmatism) / 12.0
        cooperation_reduction = max(0, profile.ambition - 3) / 6.0
        profile.cooperation_tendency = max(0.1, min(0.9, cooperation_base - cooperation_reduction * 0.3))
        
        # Treaty reliability primarily based on integrity and discipline
        reliability_base = (profile.integrity * 2 + profile.discipline) / 18.0
        reliability_penalty = profile.impulsivity / 12.0
        profile.treaty_reliability = max(0.1, min(0.9, reliability_base - reliability_penalty * 0.2))
        
        # Negotiation style
        if profile.aggression_level > 0.7:
            profile.negotiation_style = "aggressive"
        elif profile.cooperation_tendency > 0.7:
            profile.negotiation_style = "cooperative"
        else:
            profile.negotiation_style = "balanced"
    
    def _calculate_situational_responses(self, profile: PersonalityProfile) -> None:
        """Calculate how faction responds to different situations"""
        
        # Stress response based on resilience and discipline
        if profile.resilience <= 2 and profile.impulsivity >= 4:
            profile.stress_response = "panic"
        elif profile.resilience <= 2 and profile.aggression_level >= 0.6:
            profile.stress_response = "aggressive"
        elif profile.discipline >= 4:
            profile.stress_response = "measured"
        else:
            profile.stress_response = "withdrawal"
        
        # Success response based on ambition and discipline
        if profile.ambition >= 5 and profile.discipline <= 3:
            profile.success_response = "overconfident"
        elif profile.discipline >= 4:
            profile.success_response = "steady"
        else:
            profile.success_response = "cautious"
    
    def get_decision_modifiers(
        self, 
        faction_id: UUID, 
        decision_type: str, 
        context: Dict[str, Any] = None
    ) -> DecisionModifier:
        """Get personality-based modifiers for a specific decision"""
        
        if context is None:
            context = {}
        
        profile = self.get_personality_profile(faction_id)
        modifier = DecisionModifier(decision_type=decision_type, faction_id=faction_id)
        
        # Apply pattern-specific modifiers
        self._apply_pattern_modifiers(modifier, profile, decision_type, context)
        
        # Apply trait-specific modifiers
        self._apply_trait_modifiers(modifier, profile, decision_type, context)
        
        # Apply situational modifiers
        self._apply_situational_modifiers(modifier, profile, decision_type, context)
        
        return modifier
    
    def _apply_pattern_modifiers(
        self, 
        modifier: DecisionModifier, 
        profile: PersonalityProfile, 
        decision_type: str, 
        context: Dict[str, Any]
    ) -> None:
        """Apply modifiers based on primary behavior pattern"""
        
        pattern = profile.primary_behavior_pattern
        
        if pattern == BehaviorPattern.AGGRESSIVE_EXPANSIONIST:
            if decision_type in ["declare_war", "territorial_expansion", "aggressive_negotiation"]:
                modifier.success_probability_modifier += 0.1
                modifier.aggression_modifier += 0.3
                modifier.urgency_modifier += 0.2
                modifier.preferred_actions.extend(["military_action", "territorial_claims", "intimidation"])
            
            if decision_type in ["form_alliance", "peaceful_negotiation"]:
                modifier.success_probability_modifier -= 0.1
                modifier.patience_modifier -= 0.2
        
        elif pattern == BehaviorPattern.HONORABLE_WARRIOR:
            if decision_type in ["honor_alliance", "defensive_action", "just_war"]:
                modifier.success_probability_modifier += 0.15
                modifier.cooperation_modifier += 0.2
                modifier.preferred_actions.extend(["honor_commitments", "defend_allies", "righteous_cause"])
            
            if decision_type in ["betray_ally", "unprovoked_attack", "break_treaty"]:
                modifier.success_probability_modifier -= 0.3
                modifier.avoided_actions.extend(["betrayal", "dishonor", "treaty_breaking"])
        
        elif pattern == BehaviorPattern.CAUTIOUS_DIPLOMAT:
            if decision_type in ["diplomatic_negotiation", "mediation", "careful_planning"]:
                modifier.success_probability_modifier += 0.1
                modifier.planning_time_modifier += 0.3
                modifier.risk_assessment_modifier -= 0.1
                modifier.preferred_actions.extend(["thorough_analysis", "diplomatic_solution", "careful_planning"])
            
            if decision_type in ["hasty_action", "impulsive_decision"]:
                modifier.success_probability_modifier -= 0.2
                modifier.avoided_actions.extend(["rushed_decisions", "impulsive_actions"])
        
        elif pattern == BehaviorPattern.OPPORTUNISTIC_TRADER:
            if decision_type in ["trade_negotiation", "economic_alliance", "pragmatic_deal"]:
                modifier.success_probability_modifier += 0.15
                modifier.cooperation_modifier += 0.1
                modifier.preferred_actions.extend(["economic_benefit", "practical_solutions", "win_win_deals"])
            
            if decision_type in ["idealistic_stance", "costly_principle"]:
                modifier.success_probability_modifier -= 0.1
                modifier.avoided_actions.extend(["costly_idealism", "unprofitable_ventures"])
        
        elif pattern == BehaviorPattern.ISOLATIONIST:
            if decision_type in ["defensive_action", "border_security", "self_reliance"]:
                modifier.success_probability_modifier += 0.1
                modifier.cooperation_modifier -= 0.2
                modifier.preferred_actions.extend(["defensive_measures", "self_sufficiency", "minimal_engagement"])
            
            if decision_type in ["foreign_intervention", "alliance_obligations"]:
                modifier.success_probability_modifier -= 0.15
                modifier.avoided_actions.extend(["foreign_entanglements", "external_commitments"])
        
        elif pattern == BehaviorPattern.UNPREDICTABLE_WILDCARD:
            # Add randomness to all decisions
            import random
            modifier.success_probability_modifier += random.uniform(-0.2, 0.2)
            modifier.urgency_modifier += random.uniform(-0.3, 0.3)
            modifier.aggression_modifier += random.uniform(-0.2, 0.4)
            
            # Sometimes prefer unexpected actions
            if random.random() < 0.3:
                modifier.preferred_actions.append("unexpected_action")
        
        elif pattern == BehaviorPattern.RELIABLE_ALLY:
            if decision_type in ["honor_alliance", "support_ally", "treaty_adherence"]:
                modifier.success_probability_modifier += 0.2
                modifier.cooperation_modifier += 0.3
                modifier.preferred_actions.extend(["alliance_support", "treaty_compliance", "reliable_partnership"])
            
            if decision_type in ["abandon_ally", "break_commitment"]:
                modifier.success_probability_modifier -= 0.4
                modifier.avoided_actions.extend(["abandoning_allies", "breaking_commitments"])
        
        elif pattern == BehaviorPattern.SCHEMING_MANIPULATOR:
            if decision_type in ["covert_operation", "manipulation", "long_term_planning"]:
                modifier.success_probability_modifier += 0.15
                modifier.planning_time_modifier += 0.2
                modifier.preferred_actions.extend(["covert_action", "manipulation", "long_term_schemes"])
            
            if decision_type in ["direct_confrontation", "honest_negotiation"]:
                modifier.success_probability_modifier -= 0.1
                modifier.preferred_actions.append("indirect_approach")
    
    def _apply_trait_modifiers(
        self, 
        modifier: DecisionModifier, 
        profile: PersonalityProfile, 
        decision_type: str, 
        context: Dict[str, Any]
    ) -> None:
        """Apply modifiers based on individual personality traits"""
        
        # High ambition effects
        if profile.ambition >= 5:
            if decision_type in ["expansion", "power_grab", "dominance"]:
                modifier.success_probability_modifier += 0.1
                modifier.urgency_modifier += 0.1
            
            if decision_type in ["status_quo", "defensive_only"]:
                modifier.success_probability_modifier -= 0.1
        
        # High integrity effects
        if profile.integrity >= 5:
            if decision_type in ["honest_dealing", "treaty_compliance"]:
                modifier.success_probability_modifier += 0.15
            
            if decision_type in ["deception", "treaty_violation"]:
                modifier.success_probability_modifier -= 0.3
                modifier.risk_assessment_modifier += 0.2
        
        # High discipline effects
        if profile.discipline >= 5:
            if decision_type in ["long_term_planning", "strategic_patience"]:
                modifier.success_probability_modifier += 0.1
                modifier.planning_time_modifier += 0.2
            
            modifier.risk_assessment_modifier -= 0.1  # Better risk assessment
        
        # High impulsivity effects
        if profile.impulsivity >= 5:
            if decision_type in ["quick_response", "immediate_action"]:
                modifier.success_probability_modifier += 0.1
                modifier.urgency_modifier += 0.3
            
            if decision_type in ["careful_planning", "patient_waiting"]:
                modifier.success_probability_modifier -= 0.15
                modifier.planning_time_modifier -= 0.2
        
        # High pragmatism effects
        if profile.pragmatism >= 5:
            if decision_type in ["practical_solution", "compromise"]:
                modifier.success_probability_modifier += 0.1
                modifier.cooperation_modifier += 0.1
            
            if decision_type in ["idealistic_stance", "principled_stand"]:
                modifier.success_probability_modifier -= 0.1
        
        # High resilience effects
        if profile.resilience >= 5:
            if decision_type in ["recovery_action", "perseverance"]:
                modifier.success_probability_modifier += 0.15
            
            # Better handling of setbacks
            modifier.risk_assessment_modifier -= 0.05
    
    def _apply_situational_modifiers(
        self, 
        modifier: DecisionModifier, 
        profile: PersonalityProfile, 
        decision_type: str, 
        context: Dict[str, Any]
    ) -> None:
        """Apply modifiers based on current situation and context"""
        
        # Stress situation modifiers
        if context.get("under_threat", False):
            if profile.stress_response == "panic":
                modifier.success_probability_modifier -= 0.2
                modifier.urgency_modifier += 0.4
            elif profile.stress_response == "aggressive":
                modifier.aggression_modifier += 0.3
                modifier.cooperation_modifier -= 0.2
            elif profile.stress_response == "measured":
                modifier.success_probability_modifier += 0.1
                modifier.planning_time_modifier += 0.1
            elif profile.stress_response == "withdrawal":
                modifier.cooperation_modifier -= 0.3
                modifier.preferred_actions.append("defensive_withdrawal")
        
        # Recent success modifiers
        if context.get("recent_success", False):
            if profile.success_response == "overconfident":
                modifier.risk_assessment_modifier -= 0.2
                modifier.aggression_modifier += 0.2
            elif profile.success_response == "steady":
                modifier.success_probability_modifier += 0.05
            elif profile.success_response == "cautious":
                modifier.planning_time_modifier += 0.1
        
        # Recent failure modifiers
        if context.get("recent_failure", False):
            if profile.resilience <= 2:
                modifier.success_probability_modifier -= 0.1
                modifier.risk_assessment_modifier += 0.2
            elif profile.resilience >= 5:
                modifier.success_probability_modifier += 0.05  # Learn from failure
    
    def evaluate_decision_compatibility(
        self, 
        faction_id: UUID, 
        decision_type: str, 
        context: Dict[str, Any] = None
    ) -> float:
        """Evaluate how compatible a decision is with faction personality (0.0 to 1.0)"""
        
        profile = self.get_personality_profile(faction_id)
        modifier = self.get_decision_modifiers(faction_id, decision_type, context)
        
        # Base compatibility
        compatibility = 0.5
        
        # Adjust based on preferred/avoided actions
        if any(action in decision_type.lower() for action in modifier.preferred_actions):
            compatibility += 0.3
        
        if any(action in decision_type.lower() for action in modifier.avoided_actions):
            compatibility -= 0.4
        
        # Adjust based on success probability modifier
        compatibility += modifier.success_probability_modifier
        
        # Adjust based on behavior pattern alignment
        pattern_alignment = self._calculate_pattern_alignment(profile, decision_type)
        compatibility += pattern_alignment * 0.2
        
        return max(0.0, min(1.0, compatibility))
    
    def _calculate_pattern_alignment(self, profile: PersonalityProfile, decision_type: str) -> float:
        """Calculate how well a decision aligns with behavior patterns"""
        
        pattern = profile.primary_behavior_pattern
        
        alignment_map = {
            BehaviorPattern.AGGRESSIVE_EXPANSIONIST: {
                "war": 0.8, "expansion": 0.9, "aggression": 0.8, "peace": -0.5
            },
            BehaviorPattern.HONORABLE_WARRIOR: {
                "honor": 0.9, "alliance": 0.7, "defense": 0.8, "betrayal": -0.9
            },
            BehaviorPattern.CAUTIOUS_DIPLOMAT: {
                "negotiation": 0.8, "diplomacy": 0.9, "planning": 0.7, "hasty": -0.7
            },
            BehaviorPattern.OPPORTUNISTIC_TRADER: {
                "trade": 0.9, "economic": 0.8, "practical": 0.7, "idealistic": -0.5
            },
            BehaviorPattern.ISOLATIONIST: {
                "defensive": 0.8, "isolation": 0.9, "intervention": -0.8, "alliance": -0.6
            },
            BehaviorPattern.RELIABLE_ALLY: {
                "alliance": 0.9, "support": 0.8, "reliable": 0.9, "abandon": -0.9
            }
        }
        
        pattern_scores = alignment_map.get(pattern, {})
        
        # Check for keyword matches
        decision_lower = decision_type.lower()
        total_alignment = 0.0
        matches = 0
        
        for keyword, score in pattern_scores.items():
            if keyword in decision_lower:
                total_alignment += score
                matches += 1
        
        return total_alignment / max(1, matches)
    
    def suggest_personality_driven_actions(
        self, 
        faction_id: UUID, 
        available_actions: List[str],
        context: Dict[str, Any] = None
    ) -> List[Tuple[str, float]]:
        """Suggest actions ranked by personality compatibility"""
        
        suggestions = []
        
        for action in available_actions:
            compatibility = self.evaluate_decision_compatibility(faction_id, action, context)
            suggestions.append((action, compatibility))
        
        # Sort by compatibility score
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return suggestions
    
    def get_negotiation_style_modifiers(self, faction_id: UUID) -> Dict[str, float]:
        """Get negotiation style modifiers for diplomatic interactions"""
        
        profile = self.get_personality_profile(faction_id)
        
        modifiers = {
            "aggression": profile.aggression_level,
            "cooperation": profile.cooperation_tendency,
            "patience": 1.0 - (profile.impulsivity / 6.0),
            "reliability": profile.treaty_reliability,
            "risk_tolerance": profile.risk_tolerance
        }
        
        # Style-specific adjustments
        if profile.negotiation_style == "aggressive":
            modifiers["aggression"] += 0.2
            modifiers["patience"] -= 0.2
        elif profile.negotiation_style == "cooperative":
            modifiers["cooperation"] += 0.2
            modifiers["aggression"] -= 0.1
        
        # Ensure all values are in valid range
        for key in modifiers:
            modifiers[key] = max(0.0, min(1.0, modifiers[key]))
        
        return modifiers

# Global integrator instance
_personality_integrator = None

def get_personality_integrator(faction_service=None) -> PersonalityIntegrator:
    """Get the global personality integrator instance"""
    global _personality_integrator
    if _personality_integrator is None:
        _personality_integrator = PersonalityIntegrator(faction_service)
    return _personality_integrator 