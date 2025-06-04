"""
Advanced AI Content Mutation System

This module provides sophisticated rumor content mutation using NLP techniques,
semantic analysis, and context-aware transformations for realistic rumor evolution.
"""

import random
import re
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from enum import Enum
import logging

from backend.systems.rumor.utils.rumor_rules import get_rumor_config

logger = logging.getLogger(__name__)


class MutationType(Enum):
    """Types of content mutations"""
    SEMANTIC_SHIFT = "semantic_shift"
    EMOTIONAL_AMPLIFICATION = "emotional_amplification"
    DETAIL_DISTORTION = "detail_distortion"
    PERSPECTIVE_CHANGE = "perspective_change"
    TEMPORAL_SHIFT = "temporal_shift"
    CAUSALITY_MODIFICATION = "causality_modification"
    AUTHORITY_TRANSFER = "authority_transfer"
    SCOPE_EXPANSION = "scope_expansion"


@dataclass
class MutationContext:
    """Context for content mutation"""
    spreader_personality: Optional[str] = None
    receiver_personality: Optional[str] = None
    social_pressure: float = 0.5
    emotional_state: Optional[str] = None
    time_since_original: float = 0.0
    mutation_count: int = 0
    cultural_context: Optional[str] = None


class AdvancedContentMutator:
    """Sophisticated content mutation using NLP-inspired techniques"""
    
    def __init__(self):
        self.config = get_rumor_config()
        self.mutation_rules = self._load_mutation_rules()
        self.semantic_networks = self._load_semantic_networks()
        self.emotional_amplifiers = self._load_emotional_amplifiers()
        
    def _load_mutation_rules(self) -> Dict[str, Dict]:
        """Load sophisticated mutation transformation rules"""
        return {
            MutationType.SEMANTIC_SHIFT.value: {
                "word_substitutions": {
                    # Action verbs - escalation patterns
                    "planning": ["plotting", "scheming", "conspiring", "orchestrating"],
                    "meeting": ["secretly gathering", "conspiring", "plotting together"],
                    "discussing": ["whispering about", "secretly planning", "quietly organizing"],
                    "considering": ["actively pursuing", "definitely planning", "committed to"],
                    
                    # Emotion intensifiers
                    "angry": ["furious", "enraged", "livid", "seething"],
                    "worried": ["terrified", "panicked", "desperately concerned"],
                    "surprised": ["shocked", "stunned", "devastated by the news"],
                    
                    # Authority escalation
                    "someone": ["a high-ranking official", "multiple sources", "insider contacts"],
                    "person": ["authority figure", "government insider", "trusted informant"],
                    "people": ["influential circles", "those in power", "the inner circle"],
                    
                    # Certainty modifiers
                    "might": ["will definitely", "is confirmed to", "has been proven to"],
                    "could": ["is going to", "will certainly", "has already begun to"],
                    "possibly": ["undoubtedly", "without question", "absolutely"],
                    "maybe": ["definitely", "for certain", "beyond doubt"]
                },
                
                "phrase_transformations": {
                    r"I heard (\w+)": [
                        r"Multiple sources confirm \1",
                        r"Reliable contacts report \1", 
                        r"Insider information reveals \1"
                    ],
                    r"(\w+) was seen": [
                        r"\1 was caught",
                        r"\1 was discovered",
                        r"Witnesses saw \1"
                    ],
                    r"there might be": [
                        "there is definitely",
                        "sources confirm there is",
                        "intelligence reports show there is"
                    ]
                }
            },
            
            MutationType.DETAIL_DISTORTION.value: {
                "number_inflation": {
                    "patterns": [r"(\d+)", r"a few", r"some", r"several"],
                    "multipliers": [2, 3, 5, 10],
                    "qualifiers": ["at least", "over", "more than", "upwards of"]
                },
                
                "time_distortion": {
                    "yesterday": ["last week", "recently", "not long ago"],
                    "last week": ["last month", "a while back", "some time ago"],
                    "recently": ["months ago", "a long time ago", "ages ago"],
                    "soon": ["immediately", "any moment", "within hours"],
                    "next week": ["tomorrow", "very soon", "within days"]
                },
                
                "location_generalization": {
                    "specific_places": [
                        r"(\w+)'s house",
                        r"the (\w+) tavern", 
                        r"(\w+) street"
                    ],
                    "generalizations": [
                        "somewhere in the noble district",
                        "a tavern in the city",
                        "somewhere downtown"
                    ]
                }
            },
            
            MutationType.EMOTIONAL_AMPLIFICATION.value: {
                "intensity_escalation": {
                    "low": ["concerning", "troubling", "worrying", "disturbing"],
                    "medium": ["alarming", "shocking", "devastating", "catastrophic"],
                    "high": ["apocalyptic", "world-ending", "civilization-threatening"]
                },
                
                "emotional_injection": {
                    "fear_words": ["terrifying", "nightmare", "horrifying", "spine-chilling"],
                    "urgency_words": ["urgent", "critical", "emergency", "immediate"],
                    "conspiracy_words": ["secret", "hidden", "cover-up", "conspiracy"]
                }
            },
            
            MutationType.PERSPECTIVE_CHANGE.value: {
                "voice_shifts": {
                    "first_person": [
                        r"I (\w+)",
                        r"My (\w+)",
                        r"I've (\w+)"
                    ],
                    "second_person": [
                        r"You should know \1",
                        r"Your \1 told me",
                        r"You've probably heard \1"
                    ],
                    "third_person": [
                        r"Everyone knows \1",
                        r"They say \1",
                        r"Word is \1"
                    ]
                },
                
                "authority_claims": [
                    "My cousin in the guard told me",
                    "A friend who works in the castle said",
                    "Someone with inside knowledge revealed",
                    "A merchant who deals with them mentioned",
                    "I overheard officials discussing"
                ]
            }
        }
    
    def _load_semantic_networks(self) -> Dict[str, List[str]]:
        """Load semantic relationship networks for content transformation"""
        return {
            "political_concepts": {
                "power": ["authority", "control", "dominance", "influence", "command"],
                "corruption": ["bribery", "conspiracy", "scandal", "cover-up", "fraud"],
                "conflict": ["war", "rebellion", "uprising", "revolution", "coup"],
                "alliance": ["partnership", "treaty", "agreement", "pact", "coalition"]
            },
            
            "social_concepts": {
                "reputation": ["honor", "standing", "prestige", "dignity", "respect"],
                "relationship": ["affair", "romance", "courtship", "marriage", "scandal"],
                "community": ["neighborhood", "district", "society", "circle", "group"],
                "status": ["rank", "position", "class", "nobility", "commoner"]
            },
            
            "economic_concepts": {
                "wealth": ["fortune", "riches", "prosperity", "affluence", "treasure"],
                "trade": ["commerce", "business", "exchange", "dealing", "transaction"],
                "poverty": ["destitution", "hardship", "struggle", "bankruptcy", "ruin"],
                "value": ["worth", "price", "cost", "expense", "investment"]
            },
            
            "emotional_concepts": {
                "anger": ["rage", "fury", "wrath", "indignation", "outrage"],
                "fear": ["terror", "dread", "anxiety", "panic", "horror"],
                "joy": ["happiness", "delight", "elation", "euphoria", "bliss"],
                "sadness": ["grief", "sorrow", "melancholy", "despair", "misery"]
            }
        }
    
    def _load_emotional_amplifiers(self) -> Dict[str, List[str]]:
        """Load emotional amplification patterns"""
        return {
            "catastrophic_prefixes": [
                "Absolutely devastating:", "Shocking revelation:",
                "Unbelievable news:", "Crisis alert:",
                "Emergency situation:", "Urgent warning:"
            ],
            
            "conspiracy_markers": [
                "What they don't want you to know:",
                "The truth they're hiding:",
                "Secret information reveals:",
                "Insider sources confirm:",
                "Leaked documents show:"
            ],
            
            "urgency_suffixes": [
                "- immediate action required!",
                "- this changes everything!",
                "- spread the word before it's too late!",
                "- they're trying to cover this up!",
                "- time is running out!"
            ]
        }
    
    def mutate_content(
        self,
        original_content: str,
        context: MutationContext,
        mutation_intensity: float = 0.5
    ) -> Tuple[str, List[str]]:
        """
        Apply sophisticated content mutation
        
        Args:
            original_content: The original rumor content
            context: Mutation context and parameters
            mutation_intensity: How much to mutate (0.0 to 1.0)
            
        Returns:
            Tuple of (mutated_content, applied_mutations)
        """
        content = original_content
        applied_mutations = []
        
        # Determine number of mutations based on intensity and context
        base_mutations = max(1, int(mutation_intensity * 4))
        
        # Add mutations based on context factors
        if context.mutation_count > 3:
            base_mutations += 1  # More mutations for longer chains
        if context.social_pressure > 0.7:
            base_mutations += 1  # Social pressure increases mutation
        if context.emotional_state in ["excited", "angry", "fearful"]:
            base_mutations += 1  # Emotional states increase mutation
            
        # Apply mutations
        for _ in range(base_mutations):
            mutation_type = self._select_mutation_type(context, mutation_intensity)
            content, mutation_applied = self._apply_mutation(
                content, mutation_type, context, mutation_intensity
            )
            if mutation_applied:
                applied_mutations.append(mutation_applied)
        
        return content, applied_mutations
    
    def _select_mutation_type(
        self, 
        context: MutationContext, 
        intensity: float
    ) -> MutationType:
        """Select appropriate mutation type based on context"""
        
        # Weight mutation types based on context
        weights = {
            MutationType.SEMANTIC_SHIFT: 1.0,
            MutationType.DETAIL_DISTORTION: 1.0,
            MutationType.EMOTIONAL_AMPLIFICATION: 0.5,
            MutationType.PERSPECTIVE_CHANGE: 0.7,
            MutationType.TEMPORAL_SHIFT: 0.6,
            MutationType.CAUSALITY_MODIFICATION: 0.4,
            MutationType.AUTHORITY_TRANSFER: 0.8,
            MutationType.SCOPE_EXPANSION: 0.5
        }
        
        # Adjust weights based on context
        if context.spreader_personality == "dramatic":
            weights[MutationType.EMOTIONAL_AMPLIFICATION] *= 2
            weights[MutationType.SCOPE_EXPANSION] *= 1.5
            
        if context.spreader_personality == "gossipy":
            weights[MutationType.DETAIL_DISTORTION] *= 1.5
            weights[MutationType.AUTHORITY_TRANSFER] *= 1.3
            
        if context.emotional_state in ["angry", "fearful"]:
            weights[MutationType.EMOTIONAL_AMPLIFICATION] *= 1.8
            
        if context.time_since_original > 0.5:
            weights[MutationType.TEMPORAL_SHIFT] *= 1.5
            weights[MutationType.DETAIL_DISTORTION] *= 1.3
            
        if intensity > 0.7:
            weights[MutationType.SCOPE_EXPANSION] *= 1.4
            weights[MutationType.CAUSALITY_MODIFICATION] *= 1.2
        
        # Select weighted random mutation type
        mutation_types = list(weights.keys())
        mutation_weights = list(weights.values())
        
        return random.choices(mutation_types, weights=mutation_weights)[0]
    
    def _apply_mutation(
        self,
        content: str,
        mutation_type: MutationType,
        context: MutationContext,
        intensity: float
    ) -> Tuple[str, str]:
        """Apply specific mutation type to content"""
        
        original_content = content
        
        if mutation_type == MutationType.SEMANTIC_SHIFT:
            content = self._apply_semantic_shift(content, context, intensity)
            
        elif mutation_type == MutationType.DETAIL_DISTORTION:
            content = self._apply_detail_distortion(content, context, intensity)
            
        elif mutation_type == MutationType.EMOTIONAL_AMPLIFICATION:
            content = self._apply_emotional_amplification(content, context, intensity)
            
        elif mutation_type == MutationType.PERSPECTIVE_CHANGE:
            content = self._apply_perspective_change(content, context, intensity)
            
        elif mutation_type == MutationType.TEMPORAL_SHIFT:
            content = self._apply_temporal_shift(content, context, intensity)
            
        elif mutation_type == MutationType.AUTHORITY_TRANSFER:
            content = self._apply_authority_transfer(content, context, intensity)
            
        elif mutation_type == MutationType.SCOPE_EXPANSION:
            content = self._apply_scope_expansion(content, context, intensity)
            
        # Return mutation type if content changed
        mutation_applied = mutation_type.value if content != original_content else None
        return content, mutation_applied
    
    def _apply_semantic_shift(self, content: str, context: MutationContext, intensity: float) -> str:
        """Apply semantic word substitutions"""
        rules = self.mutation_rules[MutationType.SEMANTIC_SHIFT.value]
        
        # Apply word substitutions
        for original, replacements in rules["word_substitutions"].items():
            if original in content.lower():
                # Select replacement based on intensity
                if intensity > 0.7:
                    replacement = replacements[-1]  # Most intense
                elif intensity > 0.4:
                    replacement = random.choice(replacements[1:])  # Mid to high
                else:
                    replacement = random.choice(replacements[:2])  # Low to mid
                
                # Case-aware replacement
                pattern = re.compile(re.escape(original), re.IGNORECASE)
                content = pattern.sub(replacement, content, count=1)
        
        # Apply phrase transformations
        for pattern, replacements in rules["phrase_transformations"].items():
            if re.search(pattern, content, re.IGNORECASE):
                replacement = random.choice(replacements)
                content = re.sub(pattern, replacement, content, count=1, flags=re.IGNORECASE)
                break
        
        return content
    
    def _apply_detail_distortion(self, content: str, context: MutationContext, intensity: float) -> str:
        """Apply detail distortions and exaggerations"""
        rules = self.mutation_rules[MutationType.DETAIL_DISTORTION.value]
        
        # Number inflation
        number_rules = rules["number_inflation"]
        for pattern in number_rules["patterns"]:
            matches = re.findall(pattern, content)
            for match in matches:
                if match.isdigit():
                    original_num = int(match)
                    multiplier = random.choice(number_rules["multipliers"])
                    new_num = original_num * multiplier
                    qualifier = random.choice(number_rules["qualifiers"])
                    
                    if intensity > 0.6:
                        replacement = f"{qualifier} {new_num}"
                    else:
                        replacement = str(new_num)
                    
                    content = content.replace(match, replacement, 1)
        
        # Time distortion
        time_rules = rules["time_distortion"]
        for original, replacements in time_rules.items():
            if original in content.lower():
                if intensity > 0.5:
                    replacement = replacements[-1]  # Most distorted
                else:
                    replacement = random.choice(replacements[:2])
                content = re.sub(re.escape(original), replacement, content, count=1, flags=re.IGNORECASE)
        
        return content
    
    def _apply_emotional_amplification(self, content: str, context: MutationContext, intensity: float) -> str:
        """Amplify emotional content and urgency"""
        amplifiers = self.emotional_amplifiers
        
        # Add catastrophic prefix
        if intensity > 0.7 and random.random() < 0.4:
            prefix = random.choice(amplifiers["catastrophic_prefixes"])
            content = f"{prefix} {content}"
        
        # Add conspiracy markers
        if intensity > 0.6 and random.random() < 0.3:
            marker = random.choice(amplifiers["conspiracy_markers"])
            content = f"{marker} {content}"
        
        # Add urgency suffix
        if intensity > 0.5 and random.random() < 0.5:
            suffix = random.choice(amplifiers["urgency_suffixes"])
            content = f"{content}{suffix}"
        
        # Apply intensity escalation
        rules = self.mutation_rules[MutationType.EMOTIONAL_AMPLIFICATION.value]
        intensity_rules = rules["intensity_escalation"]
        
        # Find and amplify emotional words
        for level, replacements in intensity_rules.items():
            for replacement in replacements:
                if replacement in content.lower():
                    if level == "low" and intensity > 0.6:
                        # Escalate from low to medium/high
                        new_word = random.choice(intensity_rules["medium"])
                        content = re.sub(re.escape(replacement), new_word, content, count=1, flags=re.IGNORECASE)
                    elif level == "medium" and intensity > 0.8:
                        # Escalate from medium to high
                        new_word = random.choice(intensity_rules["high"])
                        content = re.sub(re.escape(replacement), new_word, content, count=1, flags=re.IGNORECASE)
        
        return content
    
    def _apply_perspective_change(self, content: str, context: MutationContext, intensity: float) -> str:
        """Change narrative perspective and add authority claims"""
        rules = self.mutation_rules[MutationType.PERSPECTIVE_CHANGE.value]
        
        # Add authority claim
        if intensity > 0.4 and random.random() < 0.6:
            authority_claim = random.choice(rules["authority_claims"])
            content = f"{authority_claim} that {content.lower()}"
        
        return content
    
    def _apply_temporal_shift(self, content: str, context: MutationContext, intensity: float) -> str:
        """Shift temporal references"""
        # Simple temporal shifts
        temporal_shifts = {
            "will": "has already",
            "is going to": "has begun to",
            "might": "is definitely going to",
            "could": "will certainly",
            "planning": "actively doing",
            "considering": "committed to"
        }
        
        for original, replacement in temporal_shifts.items():
            if original in content.lower():
                content = re.sub(re.escape(original), replacement, content, count=1, flags=re.IGNORECASE)
                break
        
        return content
    
    def _apply_authority_transfer(self, content: str, context: MutationContext, intensity: float) -> str:
        """Transfer rumor to higher authority sources"""
        authority_patterns = [
            "According to government sources,",
            "Official reports confirm that",
            "Intelligence agencies report",
            "High-ranking officials state",
            "Authoritative sources reveal"
        ]
        
        if intensity > 0.5 and random.random() < 0.4:
            authority = random.choice(authority_patterns)
            content = f"{authority} {content.lower()}"
        
        return content
    
    def _apply_scope_expansion(self, content: str, context: MutationContext, intensity: float) -> str:
        """Expand the scope and implications of the rumor"""
        expansion_patterns = [
            "This is just the beginning -",
            "What's worse,",
            "But that's not all -",
            "The real problem is",
            "More concerning is the fact that"
        ]
        
        implications = [
            "this affects everyone in the city",
            "the implications are staggering",
            "this could destabilize the entire region",
            "similar incidents are happening elsewhere",
            "this is part of a larger pattern"
        ]
        
        if intensity > 0.6 and random.random() < 0.3:
            expansion = random.choice(expansion_patterns)
            implication = random.choice(implications)
            content = f"{content}. {expansion} {implication}."
        
        return content
    
    def analyze_mutation_chain(self, mutation_history: List[str]) -> Dict[str, Any]:
        """Analyze how content has evolved through mutations"""
        analysis = {
            "total_mutations": len(mutation_history),
            "mutation_types": {},
            "complexity_increase": 0,
            "emotional_amplification": 0,
            "authority_escalation": 0
        }
        
        # Count mutation types
        for mutation in mutation_history:
            analysis["mutation_types"][mutation] = analysis["mutation_types"].get(mutation, 0) + 1
        
        # Analyze trends
        emotional_mutations = sum([
            analysis["mutation_types"].get(MutationType.EMOTIONAL_AMPLIFICATION.value, 0),
            analysis["mutation_types"].get(MutationType.SCOPE_EXPANSION.value, 0)
        ])
        
        authority_mutations = sum([
            analysis["mutation_types"].get(MutationType.AUTHORITY_TRANSFER.value, 0),
            analysis["mutation_types"].get(MutationType.PERSPECTIVE_CHANGE.value, 0)
        ])
        
        analysis["emotional_amplification"] = emotional_mutations / max(1, len(mutation_history))
        analysis["authority_escalation"] = authority_mutations / max(1, len(mutation_history))
        
        return analysis


# Factory function
def create_advanced_content_mutator() -> AdvancedContentMutator:
    """Create advanced content mutator instance"""
    return AdvancedContentMutator() 