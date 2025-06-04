"""
Personality Interpreter
----------------------
Translates numerical personality attribute values into descriptive text
that LLMs and humans can better understand and work with.
Enhanced to provide comprehensive deterministic personality generation.
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
import json
import re

# Infrastructure imports
from backend.infrastructure.config_loaders.character_config_loader import config_loader

logger = logging.getLogger(__name__)


class PersonalityInterpreter:
    """
    Converts numerical personality attributes (0-6 scale) into rich descriptive text
    for better LLM understanding and human readability.
    Enhanced with comprehensive deterministic personality generation.
    """
    
    def __init__(self):
        self.personality_config = config_loader.load_personality_config()
        self.hidden_attributes = self.personality_config.get("hidden_attributes", {}).get("attributes", {})
        self.behavioral_applications = self.personality_config.get("behavioral_applications", {})
        self.attribute_interactions = self.personality_config.get("attribute_interactions", {})
        
        # Enhanced descriptors for richer personality generation
        self._initialize_descriptors()
    
    def _initialize_descriptors(self):
        """Initialize enhanced personality descriptors for deterministic generation."""
        self.trait_descriptors = {
            "ambition": {
                "high": ["driven", "goal-oriented", "ambitious", "achievement-focused", "aspirational"],
                "medium": ["moderately motivated", "balanced in goals", "selective ambition"],
                "low": ["content", "unambitious", "satisfied with status quo", "modest goals"]
            },
            "integrity": {
                "high": ["honest", "principled", "ethical", "trustworthy", "moral"],
                "medium": ["generally honest", "situationally flexible", "pragmatic ethics"],
                "low": ["opportunistic", "flexible morals", "self-serving", "expedient"]
            },
            "discipline": {
                "high": ["disciplined", "self-controlled", "methodical", "structured", "reliable"],
                "medium": ["moderately organized", "situational discipline", "balanced approach"],
                "low": ["impulsive", "disorganized", "spontaneous", "inconsistent"]
            },
            "impulsivity": {
                "high": ["impulsive", "spontaneous", "reactive", "emotional", "quick to act"],
                "medium": ["balanced responses", "thoughtful but decisive", "measured reactions"],
                "low": ["deliberate", "cautious", "calculated", "reserved", "thoughtful"]
            },
            "pragmatism": {
                "high": ["practical", "realistic", "pragmatic", "solution-focused", "efficient"],
                "medium": ["balanced idealism", "practical when needed", "situational realism"],
                "low": ["idealistic", "theoretical", "principle-driven", "visionary"]
            },
            "resilience": {
                "high": ["resilient", "hardy", "determined", "bounces back quickly", "emotionally stable"],
                "medium": ["generally stable", "recovers with time", "manageable stress response"],
                "low": ["sensitive", "easily overwhelmed", "fragile", "stress-prone"]
            }
        }
        
        self.speech_patterns = {
            "high_integrity_high_discipline": ["speaks carefully", "measured words", "keeps promises"],
            "high_ambition_low_pragmatism": ["grand statements", "visionary language", "lofty goals"],
            "high_impulsivity_low_discipline": ["interrupts often", "emotional outbursts", "reactive speech"],
            "high_pragmatism_high_discipline": ["direct communication", "efficient language", "clear instructions"],
        }
        
        self.motivation_templates = {
            "high_ambition": ["seeks advancement", "drives toward success", "pursues recognition"],
            "high_integrity": ["maintains moral standards", "protects principles", "upholds values"],
            "high_resilience": ["overcomes challenges", "perseveres through difficulty", "adapts to change"],
            "low_ambition": ["seeks comfort", "values stability", "prefers simplicity"],
            "low_integrity": ["pursues advantage", "prioritizes self-interest", "exploits opportunities"],
        }

    def generate_complete_personality_profile(self, personality_attributes: Dict[str, int], 
                                           profession: Optional[str] = None,
                                           race: Optional[str] = None,
                                           age: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate a complete, deterministic personality profile that can replace LLM generation.
        
        Args:
            personality_attributes: Dictionary of attribute names to values
            profession: Character's profession for context
            race: Character's race for context
            age: Character's age for context
            
        Returns:
            Comprehensive personality profile with all necessary components
        """
        # Get base interpretation
        interpretation = self.interpret_full_personality(personality_attributes)
        
        # Generate enhanced components
        personality_summary = self._generate_personality_summary(personality_attributes)
        speech_style = self._generate_speech_style(personality_attributes)
        motivations = self._generate_motivations(personality_attributes, profession)
        quirks = self._generate_personality_quirks(personality_attributes)
        professional_attitude = self._generate_professional_attitude(personality_attributes, profession)
        
        return {
            **interpretation,
            "personality_summary": personality_summary,
            "speech_style": speech_style,
            "primary_motivations": motivations,
            "personality_quirks": quirks,
            "professional_attitude": professional_attitude,
            "context": {
                "profession": profession,
                "race": race,
                "age": age
            }
        }
    
    def _generate_personality_summary(self, personality_attributes: Dict[str, int]) -> str:
        """Generate a rich personality summary deterministically."""
        descriptors = []
        
        # Identify dominant traits
        sorted_attrs = sorted(personality_attributes.items(), key=lambda x: x[1], reverse=True)
        
        for attr, value in sorted_attrs:
            if value >= 5:  # High traits
                trait_list = self.trait_descriptors.get(attr, {}).get("high", [f"high {attr}"])
                descriptors.append(random.choice(trait_list))
            elif value <= 1:  # Low traits (notable)
                trait_list = self.trait_descriptors.get(attr, {}).get("low", [f"low {attr}"])
                descriptors.append(f"notably {random.choice(trait_list)}")
        
        # Limit to 3-4 key descriptors
        key_descriptors = descriptors[:4]
        
        if len(key_descriptors) >= 2:
            return f"A {key_descriptors[0]} individual who is {', '.join(key_descriptors[1:-1])} and {key_descriptors[-1]}."
        elif len(key_descriptors) == 1:
            return f"A {key_descriptors[0]} individual."
        else:
            return "A person of moderate temperament with balanced traits."
    
    def _generate_speech_style(self, personality_attributes: Dict[str, int]) -> str:
        """Generate speech style based on personality traits."""
        patterns = []
        
        # Check for specific combinations
        for pattern_key, descriptions in self.speech_patterns.items():
            if self._matches_pattern(personality_attributes, pattern_key):
                patterns.extend(descriptions)
        
        # Add individual trait influences
        if personality_attributes.get('impulsivity', 3) >= 5:
            patterns.append("speaks quickly and emotionally")
        if personality_attributes.get('discipline', 3) >= 5:
            patterns.append("chooses words carefully")
        if personality_attributes.get('integrity', 3) >= 5:
            patterns.append("speaks truthfully")
        if personality_attributes.get('pragmatism', 3) >= 5:
            patterns.append("uses practical, direct language")
        
        if not patterns:
            return "Speaks in a straightforward manner."
        
        return f"Speech style: {', '.join(patterns[:3])}."
    
    def _generate_motivations(self, personality_attributes: Dict[str, int], 
                            profession: Optional[str] = None) -> List[str]:
        """Generate primary motivations based on personality and context."""
        motivations = []
        
        # Add trait-based motivations
        for attr, value in personality_attributes.items():
            if value >= 5:  # High values drive behavior
                trait_motivations = self.motivation_templates.get(f"high_{attr}", [])
                if trait_motivations:
                    motivations.append(random.choice(trait_motivations))
            elif value <= 1:  # Low values also drive behavior
                trait_motivations = self.motivation_templates.get(f"low_{attr}", [])
                if trait_motivations:
                    motivations.append(random.choice(trait_motivations))
        
        # Add profession-specific motivations if available
        if profession:
            profession_motivations = {
                "merchant": "builds wealth and connections",
                "guard": "maintains order and safety", 
                "scholar": "pursues knowledge and understanding",
                "artisan": "creates beautiful and functional works",
                "farmer": "provides for family and community"
            }
            if profession in profession_motivations:
                motivations.append(profession_motivations[profession])
        
        return motivations[:3]  # Limit to top 3 motivations
    
    def _generate_personality_quirks(self, personality_attributes: Dict[str, int]) -> List[str]:
        """Generate 2-3 distinctive personality quirks."""
        quirks = []
        
        # Quirks based on extreme values
        if personality_attributes.get('discipline', 3) >= 5:
            quirks.append("organizes everything in precise order")
        elif personality_attributes.get('discipline', 3) <= 1:
            quirks.append("frequently loses track of belongings")
            
        if personality_attributes.get('impulsivity', 3) >= 5:
            quirks.append("makes snap decisions without consulting others")
        elif personality_attributes.get('impulsivity', 3) <= 1:
            quirks.append("takes a long time to make even simple decisions")
            
        if personality_attributes.get('integrity', 3) >= 5:
            quirks.append("cannot tell even white lies")
        elif personality_attributes.get('integrity', 3) <= 1:
            quirks.append("embellishes stories for dramatic effect")
            
        if personality_attributes.get('ambition', 3) >= 5:
            quirks.append("constantly talks about future plans and goals")
        elif personality_attributes.get('ambition', 3) <= 1:
            quirks.append("content to do the same thing every day")
            
        # Add some general quirks based on combinations
        resilience = personality_attributes.get('resilience', 3)
        pragmatism = personality_attributes.get('pragmatism', 3)
        
        if resilience >= 5 and pragmatism >= 5:
            quirks.append("always has a backup plan")
        elif resilience <= 2 and pragmatism <= 2:
            quirks.append("gets overwhelmed by theoretical problems")
        
        return quirks[:3]
    
    def _generate_professional_attitude(self, personality_attributes: Dict[str, int], 
                                      profession: Optional[str] = None) -> str:
        """Generate attitude toward profession/work."""
        if not profession:
            return "Views work as a necessary part of life."
        
        ambition = personality_attributes.get('ambition', 3)
        integrity = personality_attributes.get('integrity', 3)
        discipline = personality_attributes.get('discipline', 3)
        pragmatism = personality_attributes.get('pragmatism', 3)
        
        attitude_components = []
        
        if ambition >= 5:
            attitude_components.append("sees it as a path to advancement")
        elif ambition <= 1:
            attitude_components.append("views it as simply a way to get by")
        
        if integrity >= 5:
            attitude_components.append("takes pride in doing quality work")
        elif integrity <= 1:
            attitude_components.append("focuses on getting the job done with minimal effort")
        
        if discipline >= 5:
            attitude_components.append("maintains high professional standards")
        elif discipline <= 1:
            attitude_components.append("has an inconsistent work approach")
        
        if attitude_components:
            return f"Professional attitude: {' and '.join(attitude_components)}."
        else:
            return f"Has a balanced, practical approach to {profession} work."
    
    def _matches_pattern(self, personality_attributes: Dict[str, int], pattern_key: str) -> bool:
        """Check if personality matches a specific pattern like 'high_integrity_high_discipline'."""
        parts = pattern_key.split('_')
        conditions = []
        
        i = 0
        while i < len(parts) - 1:
            if parts[i] in ["high", "low"]:
                level = parts[i]
                attribute = parts[i + 1]
                if attribute in personality_attributes:
                    value = personality_attributes[attribute]
                    if level == "high" and value >= 5:
                        conditions.append(True)
                    elif level == "low" and value <= 1:
                        conditions.append(True)
                    else:
                        conditions.append(False)
                i += 2
            else:
                i += 1
        
        return all(conditions) and len(conditions) >= 2
    
    def interpret_single_attribute(self, attribute_name: str, value: int) -> Dict[str, str]:
        """
        Convert a single attribute value to descriptive text.
        
        Args:
            attribute_name: Name of the attribute (e.g., 'integrity', 'ambition')
            value: Numerical value (0-6)
            
        Returns:
            Dictionary containing descriptive information about the attribute
        """
        if attribute_name not in self.hidden_attributes:
            logger.warning(f"Unknown personality attribute: {attribute_name}")
            return {
                "attribute": attribute_name,
                "value": str(value),
                "description": f"Unknown attribute with value {value}",
                "behavior": "Behavior pattern unknown"
            }
        
        attribute_info = self.hidden_attributes[attribute_name]
        behavioral_indicators = attribute_info.get("behavioral_indicators", {})
        
        # Determine which range the value falls into
        behavior_description = "Behavior pattern not defined"
        for range_key, description in behavioral_indicators.items():
            if self._value_in_range(value, range_key):
                behavior_description = description
                break
        
        return {
            "attribute": attribute_info.get("name", attribute_name.title()),
            "value": f"{value}/6",
            "description": attribute_info.get("description", ""),
            "behavior": behavior_description,
            "intensity": self._get_intensity_description(value)
        }
    
    def interpret_full_personality(self, personality_attributes: Dict[str, int]) -> Dict[str, Any]:
        """
        Convert a full personality profile to rich descriptive text.
        
        Args:
            personality_attributes: Dictionary of attribute names to values
            
        Returns:
            Comprehensive personality interpretation
        """
        interpreted_attributes = {}
        
        # Interpret each individual attribute
        for attr_name, value in personality_attributes.items():
            interpreted_attributes[attr_name] = self.interpret_single_attribute(attr_name, value)
        
        # Analyze attribute interactions and conflicts
        personality_dynamics = self._analyze_personality_dynamics(personality_attributes)
        
        # Generate behavioral predictions
        behavioral_predictions = self._generate_behavioral_predictions(personality_attributes)
        
        # Create a narrative summary
        narrative_summary = self._create_personality_narrative(personality_attributes, interpreted_attributes)
        
        return {
            "attributes": interpreted_attributes,
            "personality_dynamics": personality_dynamics,
            "behavioral_predictions": behavioral_predictions,
            "narrative_summary": narrative_summary,
            "raw_values": personality_attributes
        }
    
    def create_llm_prompt_description(self, personality_attributes: Dict[str, int]) -> str:
        """
        Create a concise but rich description suitable for LLM prompts.
        
        Args:
            personality_attributes: Dictionary of attribute names to values
            
        Returns:
            Formatted string ready for LLM consumption
        """
        interpretation = self.interpret_full_personality(personality_attributes)
        
        # Build the description
        lines = ["**Personality Profile:**"]
        
        # Add each attribute with its behavior
        for attr_name, attr_data in interpretation["attributes"].items():
            lines.append(f"- **{attr_data['attribute']}** ({attr_data['value']}): {attr_data['behavior']}")
        
        # Add personality dynamics if significant
        if interpretation["personality_dynamics"]["conflicts"]:
            lines.append("\n**Internal Tensions:**")
            for conflict in interpretation["personality_dynamics"]["conflicts"]:
                lines.append(f"- {conflict}")
        
        if interpretation["personality_dynamics"]["synergies"]:
            lines.append("\n**Personality Strengths:**")
            for synergy in interpretation["personality_dynamics"]["synergies"]:
                lines.append(f"- {synergy}")
        
        # Add behavioral predictions
        if interpretation["behavioral_predictions"]["decision_making"]:
            lines.append(f"\n**Decision-Making Style:** {interpretation['behavioral_predictions']['decision_making']}")
        
        if interpretation["behavioral_predictions"]["relationship_patterns"]:
            lines.append(f"**Relationship Approach:** {interpretation['behavioral_predictions']['relationship_patterns']}")
        
        if interpretation["behavioral_predictions"]["goal_pursuit"]:
            lines.append(f"**Goal Pursuit:** {interpretation['behavioral_predictions']['goal_pursuit']}")
        
        return "\n".join(lines)
    
    def _value_in_range(self, value: int, range_key: str) -> bool:
        """Check if a value falls within a range key like '0-1', '2-3', '4-5', '6'."""
        if range_key == "6":
            return value == 6
        elif "-" in range_key:
            min_val, max_val = map(int, range_key.split("-"))
            return min_val <= value <= max_val
        else:
            return str(value) == range_key
    
    def _get_intensity_description(self, value: int) -> str:
        """Get a general intensity description for a value."""
        if value == 0:
            return "Extremely Low"
        elif value == 1:
            return "Very Low"
        elif value == 2:
            return "Low"
        elif value == 3:
            return "Moderate"
        elif value == 4:
            return "High"
        elif value == 5:
            return "Very High"
        elif value == 6:
            return "Extremely High"
        else:
            return "Unknown"
    
    def _analyze_personality_dynamics(self, personality_attributes: Dict[str, int]) -> Dict[str, List[str]]:
        """Analyze conflicts and synergies in the personality profile."""
        conflicts = []
        synergies = []
        
        # Check for conflicting pairs
        conflicting_pairs = self.attribute_interactions.get("conflicting_pairs", {})
        for pair_key, description in conflicting_pairs.items():
            if self._check_conflicting_pair(personality_attributes, pair_key):
                conflicts.append(description)
        
        # Check for synergistic pairs
        synergistic_pairs = self.attribute_interactions.get("synergistic_pairs", {})
        for pair_key, description in synergistic_pairs.items():
            if self._check_synergistic_pair(personality_attributes, pair_key):
                synergies.append(description)
        
        return {
            "conflicts": conflicts,
            "synergies": synergies
        }
    
    def _check_conflicting_pair(self, personality_attributes: Dict[str, int], pair_key: str) -> bool:
        """Check if a conflicting personality pair exists."""
        # Parse patterns like "high_ambition_high_integrity" or "low_resilience_high_ambition"
        parts = pair_key.split("_")
        
        conditions = []
        i = 0
        while i < len(parts):
            if parts[i] in ["high", "low"]:
                level = parts[i]
                attribute = parts[i + 1]
                if attribute in personality_attributes:
                    value = personality_attributes[attribute]
                    if level == "high" and value >= 5:
                        conditions.append(True)
                    elif level == "low" and value <= 2:
                        conditions.append(True)
                    else:
                        conditions.append(False)
                i += 2
            else:
                i += 1
        
        return all(conditions) and len(conditions) == 2
    
    def _check_synergistic_pair(self, personality_attributes: Dict[str, int], pair_key: str) -> bool:
        """Check if a synergistic personality pair exists."""
        return self._check_conflicting_pair(personality_attributes, pair_key)  # Same logic
    
    def _generate_behavioral_predictions(self, personality_attributes: Dict[str, int]) -> Dict[str, str]:
        """Generate predictions about how this personality will behave."""
        predictions = {
            "decision_making": "",
            "relationship_patterns": "",
            "goal_pursuit": ""
        }
        
        behavioral_apps = self.behavioral_applications
        
        # Decision-making style
        decision_patterns = []
        for attr, value in personality_attributes.items():
            if value >= 5:  # High values
                pattern = behavioral_apps.get("decision_making", {}).get(f"high_{attr}")
                if pattern:
                    decision_patterns.append(pattern)
            elif value <= 1:  # Low values
                pattern = behavioral_apps.get("decision_making", {}).get(f"low_{attr}")
                if pattern:
                    decision_patterns.append(pattern)
        
        if decision_patterns:
            predictions["decision_making"] = "; ".join(decision_patterns)
        
        # Relationship patterns
        relationship_patterns = []
        for attr, value in personality_attributes.items():
            if value >= 5:  # High values
                pattern = behavioral_apps.get("relationship_patterns", {}).get(f"high_{attr}")
                if pattern:
                    relationship_patterns.append(pattern)
            elif value <= 1:  # Low values
                pattern = behavioral_apps.get("relationship_patterns", {}).get(f"low_{attr}")
                if pattern:
                    relationship_patterns.append(pattern)
        
        if relationship_patterns:
            predictions["relationship_patterns"] = "; ".join(relationship_patterns)
        
        # Goal pursuit
        goal_patterns = []
        for attr, value in personality_attributes.items():
            if value >= 5:  # High values
                pattern = behavioral_apps.get("goal_pursuit", {}).get(f"high_{attr}")
                if pattern:
                    goal_patterns.append(pattern)
            elif value <= 1:  # Low values
                pattern = behavioral_apps.get("goal_pursuit", {}).get(f"low_{attr}")
                if pattern:
                    goal_patterns.append(pattern)
        
        if goal_patterns:
            predictions["goal_pursuit"] = "; ".join(goal_patterns)
        
        return predictions
    
    def _create_personality_narrative(self, personality_attributes: Dict[str, int], 
                                    interpreted_attributes: Dict[str, Dict[str, str]]) -> str:
        """Create a flowing narrative description of the personality."""
        narrative_parts = []
        
        # Find the most dominant traits (highest and lowest values)
        sorted_attrs = sorted(personality_attributes.items(), key=lambda x: x[1], reverse=True)
        highest_attr = sorted_attrs[0]
        lowest_attr = sorted_attrs[-1]
        
        # Start with the strongest trait
        if highest_attr[1] >= 4:
            attr_info = interpreted_attributes[highest_attr[0]]
            narrative_parts.append(f"This character is primarily defined by their {attr_info['behavior'].lower()}")
        
        # Mention the weakest trait if it's significantly low
        if lowest_attr[1] <= 2:
            attr_info = interpreted_attributes[lowest_attr[0]]
            narrative_parts.append(f"while struggling with {attr_info['behavior'].lower()}")
        
        # Add any notable middle traits
        middle_traits = [attr for attr in sorted_attrs[1:-1] if attr[1] >= 4]
        if middle_traits:
            trait_descriptions = []
            for attr_name, value in middle_traits[:2]:  # Limit to 2 to avoid overload
                attr_info = interpreted_attributes[attr_name]
                trait_descriptions.append(f"{attr_info['behavior'].lower()}")
            if trait_descriptions:
                narrative_parts.append(f"They also tend toward {' and '.join(trait_descriptions)}")
        
        return ". ".join(narrative_parts) + "."


# Global instance for easy access
personality_interpreter = PersonalityInterpreter()


# Convenience functions for common use cases
def interpret_personality_for_llm(personality_attributes: Dict[str, int]) -> str:
    """
    Quick function to get LLM-ready personality description.
    
    Args:
        personality_attributes: Dictionary of attribute names to values
        
    Returns:
        Formatted string ready for LLM prompts
    """
    return personality_interpreter.create_llm_prompt_description(personality_attributes)


def generate_complete_personality_deterministic(personality_attributes: Dict[str, int],
                                              profession: Optional[str] = None,
                                              race: Optional[str] = None,
                                              age: Optional[int] = None) -> Dict[str, Any]:
    """
    Generate a complete personality profile using deterministic methods only.
    This replaces LLM-generated personality content.
    
    Args:
        personality_attributes: Dictionary of attribute names to values
        profession: Character's profession for context
        race: Character's race for context  
        age: Character's age for context
        
    Returns:
        Complete personality profile ready for character use
    """
    return personality_interpreter.generate_complete_personality_profile(
        personality_attributes, profession, race, age
    )


def get_personality_backstory_elements(personality_attributes: Dict[str, int],
                                     profession: Optional[str] = None,
                                     race: Optional[str] = None) -> Dict[str, str]:
    """
    Generate backstory elements based on personality, profession, and race.
    Provides deterministic backstory generation without LLM dependency.
    
    Args:
        personality_attributes: Dictionary of attribute names to values
        profession: Character's profession
        race: Character's race
        
    Returns:
        Dictionary with backstory elements
    """
    backstory_elements = {}
    
    # Generate childhood influence based on personality
    ambition = personality_attributes.get('ambition', 3)
    integrity = personality_attributes.get('integrity', 3)
    resilience = personality_attributes.get('resilience', 3)
    
    if ambition >= 5:
        backstory_elements["childhood"] = "Showed early signs of drive and determination"
    elif ambition <= 1:
        backstory_elements["childhood"] = "Was content with simple pleasures and routines"
    else:
        backstory_elements["childhood"] = "Had a balanced upbringing with modest goals"
    
    # Generate formative experience
    if resilience >= 5 and integrity >= 4:
        backstory_elements["formative_experience"] = "Overcame a significant challenge while maintaining moral principles"
    elif resilience <= 2:
        backstory_elements["formative_experience"] = "Struggled with a difficult period that left lasting effects"
    else:
        backstory_elements["formative_experience"] = "Had typical life experiences that shaped their worldview"
    
    # Generate professional path
    if profession:
        discipline = personality_attributes.get('discipline', 3)
        pragmatism = personality_attributes.get('pragmatism', 3)
        
        if discipline >= 5:
            backstory_elements["professional_path"] = f"Methodically trained and studied to become a skilled {profession}"
        elif pragmatism >= 5:
            backstory_elements["professional_path"] = f"Chose {profession} work for practical reasons"
        else:
            backstory_elements["professional_path"] = f"Found their way into {profession} work through circumstance"
    
    # Generate current situation
    impulsivity = personality_attributes.get('impulsivity', 3)
    if impulsivity >= 5:
        backstory_elements["current_situation"] = "Recently made a significant life change on impulse"
    elif ambition >= 5:
        backstory_elements["current_situation"] = "Actively working toward bigger goals and aspirations"
    else:
        backstory_elements["current_situation"] = "Living a stable, predictable life"
    
    return backstory_elements


def get_attribute_description(attribute_name: str, value: int) -> str:
    """
    Get a human-readable description of a single personality attribute.
    
    Args:
        attribute_name: Name of the attribute
        value: Numerical value (0-6)
        
    Returns:
        Descriptive string for the attribute
    """
    return personality_interpreter.interpret_single_attribute(attribute_name, value).get("behavior", f"{attribute_name}: {value}")


def format_personality_for_display(personality_attributes: Dict[str, int],
                                 include_full_profile: bool = False,
                                 profession: Optional[str] = None,
                                 race: Optional[str] = None,
                                 age: Optional[int] = None) -> str:
    """
    Format personality for display to players or GMs.
    
    Args:
        personality_attributes: Dictionary of attribute names to values
        include_full_profile: Whether to include complete personality breakdown
        profession: Character's profession for context
        race: Character's race for context
        age: Character's age for context
        
    Returns:
        Formatted string for display
    """
    if include_full_profile:
        profile = generate_complete_personality_deterministic(
            personality_attributes, profession, race, age
        )
        
        lines = [
            f"**Personality:** {profile['personality_summary']}",
            f"**{profile['speech_style']}**",
            f"**Motivations:** {', '.join(profile['primary_motivations'])}",
            f"**Quirks:** {'; '.join(profile['personality_quirks'])}",
        ]
        
        if profile['professional_attitude'] and profession:
            lines.append(f"**{profile['professional_attitude']}**")
        
        return "\n".join(lines)
    else:
        return interpret_personality_for_llm(personality_attributes) 