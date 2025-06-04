"""
Memory Behavior Influence Service
---------------------------------

This service provides algorithms to translate memories into behavioral changes and decision-making factors.
It implements the memory-behavior integration requirements from Task 73.

Key Features:
- Trust calculation based on memory history using JSON configuration weights
- Risk assessment from past experiences
- Opportunity recognition through memory patterns
- Emotional response triggers from traumatic/positive memories
- Cross-system integration for economy, combat, social, and faction behaviors
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import math
import json
import os

from backend.systems.memory.services.memory import Memory
from backend.infrastructure.memory_utils.memory_categorization import MemoryCategory, get_category_info
from backend.systems.memory.services.memory_manager_core import MemoryManager

logger = logging.getLogger(__name__)


class BehaviorInfluenceType(Enum):
    """Types of behavioral influences that memories can have"""
    TRUST = "trust"
    RISK_ASSESSMENT = "risk_assessment"
    OPPORTUNITY_RECOGNITION = "opportunity_recognition"
    EMOTIONAL_RESPONSE = "emotional_response"
    FACTION_BIAS = "faction_bias"
    ECONOMIC_BEHAVIOR = "economic_behavior"
    COMBAT_BEHAVIOR = "combat_behavior"
    SOCIAL_BEHAVIOR = "social_behavior"


@dataclass
class BehaviorModifier:
    """Represents a behavioral modification derived from memories"""
    influence_type: BehaviorInfluenceType
    modifier_value: float  # -1.0 to 1.0 range
    confidence: float  # 0.0 to 1.0, how confident we are in this modifier
    source_memories: List[str] = field(default_factory=list)  # Memory IDs that contributed
    context: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class TrustCalculation:
    """Result of trust calculation for a specific entity"""
    entity_id: str
    trust_level: float  # 0.0 to 1.0
    trust_change: float  # How much trust changed from baseline
    contributing_memories: List[Tuple[str, float]]  # (memory_id, trust_impact)
    confidence: float


@dataclass
class RiskAssessment:
    """Risk assessment based on past experiences"""
    situation_type: str
    risk_level: float  # 0.0 to 1.0
    risk_factors: Dict[str, float]
    past_experiences: List[str]  # Memory IDs of relevant experiences
    confidence: float


@dataclass
class EmotionalTrigger:
    """Emotional response trigger from memories"""
    emotion: str  # anger, fear, joy, sadness, etc.
    intensity: float  # 0.0 to 1.0
    trigger_memories: List[str]
    duration_estimate: timedelta
    behavioral_effects: Dict[str, float]


class MemoryBehaviorInfluenceService:
    """
    Service that analyzes memories to determine their influence on NPC behavior.
    
    This service implements the core memory-behavior integration algorithms
    required by Task 73, using JSON configuration for trust calculations.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.entity_id = memory_manager.entity_id
        self.entity_type = memory_manager.entity_type
        
        # Load trust calculation configuration from JSON
        self.trust_config = self._load_trust_config()
        
        # Configuration for influence calculations
        self.config = {
            'trust_decay_days': 30,
            'risk_memory_relevance_days': 90,
            'emotional_trigger_threshold': 0.7,
            'memory_recency_weight': self.trust_config.get('temporal_factors', {}).get('recency_weight', 0.3),
            'memory_importance_weight': self.trust_config.get('temporal_factors', {}).get('importance_weight', 0.7)
        }
    
    def _load_trust_config(self) -> Dict[str, Any]:
        """Load trust calculation configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '../../../data/systems/memory/trust_calculation.json')
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('trust_factors', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load trust configuration: {e}. Using defaults.")
            return {
                'interaction_weights': {
                    'betrayal_weight': -0.8,
                    'help_weight': 0.6,
                    'trade_fairness_weight': 0.4,
                    'promise_keeping_weight': 0.7,
                    'information_sharing_weight': 0.3,
                    'protection_offering_weight': 0.8,
                    'resource_sharing_weight': 0.5,
                    'honest_communication_weight': 0.4,
                    'conflict_resolution_weight': 0.5,
                    'loyalty_demonstration_weight': 0.6
                },
                'temporal_factors': {
                    'time_decay_factor': 0.95,
                    'recency_weight': 0.3,
                    'importance_weight': 0.7,
                    'frequency_bonus': 0.2,
                    'consistency_bonus': 0.4
                },
                'emotional_modifiers': {
                    'trauma_amplification': 1.5,
                    'joy_amplification': 1.2,
                    'anger_amplification': 1.3,
                    'fear_amplification': 1.4,
                    'gratitude_amplification': 1.1,
                    'disappointment_amplification': 1.2
                },
                'relationship_baselines': {
                    'stranger_baseline': 0.5,
                    'acquaintance_baseline': 0.55,
                    'friend_baseline': 0.7,
                    'close_friend_baseline': 0.8,
                    'family_baseline': 0.85,
                    'enemy_baseline': 0.2,
                    'rival_baseline': 0.3
                },
                'calculation_settings': {
                    'max_memories_considered': 50,
                    'minimum_interaction_count': 3,
                    'confidence_threshold': 0.6,
                    'memory_importance_threshold': 0.3,
                    'recent_memory_days': 30
                }
            }
    
    async def calculate_trust_level(self, target_entity_id: str, 
                                  context: Optional[str] = None) -> TrustCalculation:
        """
        Calculate trust level for a specific entity based on memory history.
        
        Trust is calculated using JSON configuration weights for different interaction types,
        temporal factors, and emotional modifiers as specified in trust_calculation.json.
        """
        # Get all memories involving the target entity
        memories = await self.memory_manager.get_memories_involving_entity(target_entity_id)
        
        # Apply configuration limits
        max_memories = self.trust_config.get('calculation_settings', {}).get('max_memories_considered', 50)
        if len(memories) > max_memories:
            # Sort by importance and recency, take top memories
            memories = sorted(memories, 
                            key=lambda m: (m.importance, m.created_at), 
                            reverse=True)[:max_memories]
        
        min_interactions = self.trust_config.get('calculation_settings', {}).get('minimum_interaction_count', 3)
        if len(memories) < min_interactions:
            # Insufficient data for reliable trust calculation
            baseline = self.trust_config.get('relationship_baselines', {}).get('stranger_baseline', 0.5)
            return TrustCalculation(
                entity_id=target_entity_id,
                trust_level=baseline,
                trust_change=0.0,
                contributing_memories=[],
                confidence=0.0
            )
        
        trust_contributions = []
        total_weight = 0.0
        weighted_trust_sum = 0.0
        
        current_time = datetime.now()
        interaction_weights = self.trust_config.get('interaction_weights', {})
        temporal_factors = self.trust_config.get('temporal_factors', {})
        emotional_modifiers = self.trust_config.get('emotional_modifiers', {})
        
        for memory in memories:
            # Calculate memory weight using JSON temporal factors
            memory_weight = self._calculate_memory_weight_with_config(memory, current_time, temporal_factors)
            
            # Determine trust impact using JSON interaction weights
            trust_impact = self._calculate_trust_impact_with_config(
                memory, target_entity_id, interaction_weights, emotional_modifiers
            )
            
            if trust_impact != 0.0:
                trust_contributions.append((memory.memory_id, trust_impact))
                weighted_trust_sum += trust_impact * memory_weight
                total_weight += memory_weight
        
        # Calculate final trust level using baseline
        baseline = self.trust_config.get('relationship_baselines', {}).get('stranger_baseline', 0.5)
        if total_weight > 0:
            # Apply time decay factor
            decay_factor = temporal_factors.get('time_decay_factor', 0.95)
            trust_adjustment = (weighted_trust_sum / total_weight) * decay_factor
            trust_level = baseline + trust_adjustment
            trust_level = max(0.0, min(1.0, trust_level))  # Clamp to valid range
            trust_change = trust_level - baseline
        else:
            trust_level = baseline
            trust_change = 0.0
        
        # Calculate confidence based on interaction count and configuration
        confidence_threshold = self.trust_config.get('calculation_settings', {}).get('confidence_threshold', 0.6)
        confidence = min(1.0, (len(memories) / max_memories) * confidence_threshold)
        
        logger.info(f"Calculated trust level {trust_level:.2f} for entity {target_entity_id} using JSON config")
        
        return TrustCalculation(
            entity_id=target_entity_id,
            trust_level=trust_level,
            trust_change=trust_change,
            contributing_memories=trust_contributions,
            confidence=confidence
        )
    
    def _calculate_memory_weight_with_config(self, memory: Memory, current_time: datetime, 
                                           temporal_factors: Dict[str, float]) -> float:
        """Calculate memory weight using JSON temporal configuration"""
        importance_weight = temporal_factors.get('importance_weight', 0.7)
        recency_weight = temporal_factors.get('recency_weight', 0.3)
        frequency_bonus = temporal_factors.get('frequency_bonus', 0.2)
        
        # Base weight from importance
        weight = memory.importance * importance_weight
        
        # Add recency component
        memory_date = datetime.fromisoformat(memory.created_at) if isinstance(memory.created_at, str) else memory.created_at
        days_old = (current_time - memory_date).days
        recency_factor = max(0.1, 1.0 - (days_old / 365.0))  # Decay over a year
        weight += recency_factor * recency_weight
        
        # Add frequency bonus for memories that have been accessed multiple times
        if hasattr(memory, 'access_count') and memory.access_count > 1:
            weight += min(0.5, memory.access_count * 0.1) * frequency_bonus
        
        return weight
    
    def _calculate_trust_impact_with_config(self, memory: Memory, target_entity_id: str,
                                          interaction_weights: Dict[str, float],
                                          emotional_modifiers: Dict[str, float]) -> float:
        """Calculate trust impact using JSON interaction weights and emotional modifiers"""
        trust_impact = 0.0
        
        # Analyze memory content for interaction types
        content_lower = memory.content.lower()
        
        # Apply interaction weights based on memory content
        for interaction_type, weight in interaction_weights.items():
            if self._memory_contains_interaction_type(content_lower, interaction_type):
                trust_impact += weight
        
        # Apply emotional modifiers based on memory categories
        for category in memory.categories:
            emotion_modifier = self._get_emotional_modifier_for_category(category, emotional_modifiers)
            trust_impact *= emotion_modifier
        
        # Normalize trust impact to [-1, 1] range
        trust_impact = max(-1.0, min(1.0, trust_impact))
        
        return trust_impact
    
    def _memory_contains_interaction_type(self, content: str, interaction_type: str) -> bool:
        """Check if memory content contains specific interaction type"""
        interaction_keywords = {
            'betrayal_weight': ['betray', 'deceive', 'lie', 'cheat', 'backstab', 'false'],
            'help_weight': ['help', 'assist', 'aid', 'support', 'rescue', 'save'],
            'trade_fairness_weight': ['fair', 'honest', 'good deal', 'reasonable', 'trade'],
            'promise_keeping_weight': ['promise', 'oath', 'vow', 'keep word', 'reliable'],
            'information_sharing_weight': ['tell', 'share', 'inform', 'explain', 'reveal'],
            'protection_offering_weight': ['protect', 'defend', 'guard', 'shield', 'safety'],
            'resource_sharing_weight': ['share', 'give', 'donate', 'lend', 'provide'],
            'honest_communication_weight': ['honest', 'truth', 'sincere', 'open', 'frank'],
            'conflict_resolution_weight': ['resolve', 'mediate', 'peaceful', 'compromise'],
            'loyalty_demonstration_weight': ['loyal', 'faithful', 'stand by', 'support']
        }
        
        keywords = interaction_keywords.get(interaction_type, [])
        return any(keyword in content for keyword in keywords)
    
    def _get_emotional_modifier_for_category(self, category: str, emotional_modifiers: Dict[str, float]) -> float:
        """Get emotional modifier based on memory category"""
        category_emotion_map = {
            'trauma': emotional_modifiers.get('trauma_amplification', 1.5),
            'achievement': emotional_modifiers.get('joy_amplification', 1.2),
            'betrayal': emotional_modifiers.get('anger_amplification', 1.3),
            'threat': emotional_modifiers.get('fear_amplification', 1.4),
            'gratitude': emotional_modifiers.get('gratitude_amplification', 1.1),
            'disappointment': emotional_modifiers.get('disappointment_amplification', 1.2)
        }
        
        return category_emotion_map.get(category.lower(), 1.0)
    
    async def assess_risk(self, situation_type: str, 
                         context: Optional[Dict[str, Any]] = None) -> RiskAssessment:
        """
        Assess risk level for a situation based on past experiences.
        
        Risk assessment analyzes memories of similar situations to determine
        likely outcomes and danger levels.
        """
        # Get memories related to similar situations
        relevant_memories = await self._get_memories_for_situation(situation_type, context)
        
        if not relevant_memories:
            return RiskAssessment(
                situation_type=situation_type,
                risk_level=0.5,  # Neutral risk when no data
                risk_factors={},
                past_experiences=[],
                confidence=0.0
            )
        
        risk_factors = {}
        total_weight = 0.0
        weighted_risk_sum = 0.0
        experience_ids = []
        
        current_time = datetime.now()
        
        for memory in relevant_memories:
            memory_weight = self._calculate_memory_weight(memory, current_time)
            risk_impact = self._calculate_risk_impact_from_memory(memory, situation_type)
            
            if risk_impact is not None:
                weighted_risk_sum += risk_impact * memory_weight
                total_weight += memory_weight
                experience_ids.append(memory.memory_id)
                
                # Extract specific risk factors
                factors = self._extract_risk_factors_from_memory(memory)
                for factor, value in factors.items():
                    if factor not in risk_factors:
                        risk_factors[factor] = 0.0
                    risk_factors[factor] += value * memory_weight
        
        # Normalize risk factors
        if total_weight > 0:
            for factor in risk_factors:
                risk_factors[factor] /= total_weight
            
            risk_level = weighted_risk_sum / total_weight
            risk_level = max(0.0, min(1.0, risk_level))
        else:
            risk_level = 0.5
        
        confidence = min(1.0, len(relevant_memories) / 5.0)
        
        logger.info(f"Assessed risk level {risk_level:.2f} for situation {situation_type}")
        
        return RiskAssessment(
            situation_type=situation_type,
            risk_level=risk_level,
            risk_factors=risk_factors,
            past_experiences=experience_ids,
            confidence=confidence
        )
    
    async def identify_emotional_triggers(self, context: Optional[str] = None) -> List[EmotionalTrigger]:
        """
        Identify potential emotional triggers based on memory content.
        
        Analyzes traumatic and highly emotional memories to predict what
        situations might trigger strong emotional responses.
        """
        # Get highly emotional memories (trauma, achievement, etc.)
        emotional_memories = await self._get_emotional_memories()
        
        triggers = []
        
        for memory in emotional_memories:
            # Determine emotion type and intensity from memory
            emotion_data = self._analyze_memory_emotion(memory)
            
            if emotion_data and emotion_data['intensity'] >= self.config['emotional_trigger_threshold']:
                # Extract behavioral effects this emotion might cause
                behavioral_effects = self._calculate_emotional_behavioral_effects(
                    emotion_data['emotion'], 
                    emotion_data['intensity']
                )
                
                trigger = EmotionalTrigger(
                    emotion=emotion_data['emotion'],
                    intensity=emotion_data['intensity'],
                    trigger_memories=[memory.memory_id],
                    duration_estimate=timedelta(hours=emotion_data['intensity'] * 24),
                    behavioral_effects=behavioral_effects
                )
                
                triggers.append(trigger)
        
        logger.info(f"Identified {len(triggers)} emotional triggers")
        return triggers
    
    async def calculate_faction_bias(self, faction_id: str) -> float:
        """
        Calculate bias towards/against a specific faction based on memory history.
        
        Returns a value from -1.0 (strongly against) to 1.0 (strongly for).
        """
        faction_memories = await self._get_faction_memories(faction_id)
        
        if not faction_memories:
            return 0.0  # Neutral if no memories
        
        total_weight = 0.0
        weighted_bias_sum = 0.0
        current_time = datetime.now()
        
        for memory in faction_memories:
            memory_weight = self._calculate_memory_weight(memory, current_time)
            bias_impact = self._calculate_faction_bias_from_memory(memory, faction_id)
            
            weighted_bias_sum += bias_impact * memory_weight
            total_weight += memory_weight
        
        if total_weight > 0:
            bias = weighted_bias_sum / total_weight
            return max(-1.0, min(1.0, bias))
        
        return 0.0
    
    async def generate_behavior_modifiers(self, context: Optional[str] = None) -> List[BehaviorModifier]:
        """
        Generate a comprehensive set of behavior modifiers based on memory analysis.
        
        This is the main method that provides behavior modifications for other systems.
        """
        modifiers = []
        
        # Generate various types of behavioral influences
        # Trust modifiers would be calculated per-entity when needed
        
        # Risk assessment modifier for general cautiousness
        general_risk = await self.assess_risk("general", {"context": context})
        if general_risk.confidence > 0.3:
            risk_modifier = BehaviorModifier(
                influence_type=BehaviorInfluenceType.RISK_ASSESSMENT,
                modifier_value=general_risk.risk_level - 0.5,  # Convert to [-0.5, 0.5]
                confidence=general_risk.confidence,
                source_memories=general_risk.past_experiences,
                context=context
            )
            modifiers.append(risk_modifier)
        
        # Emotional state modifiers
        emotional_triggers = await self.identify_emotional_triggers(context)
        for trigger in emotional_triggers:
            for behavior_type, effect_value in trigger.behavioral_effects.items():
                emotion_modifier = BehaviorModifier(
                    influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
                    modifier_value=effect_value,
                    confidence=0.8,  # High confidence in emotional effects
                    source_memories=trigger.trigger_memories,
                    context=f"emotional_trigger_{trigger.emotion}",
                    expires_at=datetime.now() + trigger.duration_estimate
                )
                modifiers.append(emotion_modifier)
        
        logger.info(f"Generated {len(modifiers)} behavior modifiers")
        return modifiers
    
    # Private helper methods
    
    def _calculate_memory_weight(self, memory: Memory, current_time: datetime) -> float:
        """Calculate the weight of a memory based on importance and recency."""
        # Recency weight (more recent = higher weight)
        memory_time = datetime.fromisoformat(memory.created_at.replace('Z', '+00:00'))
        days_old = (current_time - memory_time).days
        recency_factor = math.exp(-days_old / self.config['trust_decay_days'])
        
        # Importance weight
        importance_factor = memory.importance
        
        # Combined weight
        weight = (self.config['memory_importance_weight'] * importance_factor + 
                 self.config['memory_recency_weight'] * recency_factor)
        
        return weight
    
    def _calculate_trust_impact_from_memory(self, memory: Memory, target_entity_id: str) -> float:
        """Determine how a memory affects trust towards a specific entity."""
        # Analyze memory content and categories to determine trust impact
        trust_impact = 0.0
        
        # Check if the target entity is mentioned in this memory
        entities_in_memory = memory.metadata.get('entities', [])
        if target_entity_id not in entities_in_memory:
            return 0.0  # No impact if entity not involved
        
        # Category-based trust impacts
        if MemoryCategory.TRAUMA in memory.categories:
            trust_impact -= 0.8  # Strong negative impact
        elif MemoryCategory.ACHIEVEMENT in memory.categories:
            trust_impact += 0.6  # Positive impact for achievements involving the entity
        elif MemoryCategory.INTERACTION in memory.categories:
            # Analyze interaction sentiment (would need sentiment analysis)
            trust_impact += self._analyze_interaction_sentiment(memory, target_entity_id)
        
        return trust_impact
    
    def _analyze_interaction_sentiment(self, memory: Memory, target_entity_id: str) -> float:
        """Analyze sentiment of an interaction memory."""
        # Simplified sentiment analysis based on keywords
        # In production, this would use proper sentiment analysis
        content = memory.content.lower()
        
        positive_keywords = ['helped', 'kind', 'generous', 'friendly', 'honest', 'saved', 'protected']
        negative_keywords = ['betrayed', 'lied', 'cheated', 'attacked', 'stole', 'threatened', 'abandoned']
        
        positive_score = sum(1 for word in positive_keywords if word in content)
        negative_score = sum(1 for word in negative_keywords if word in content)
        
        if positive_score > negative_score:
            return 0.3
        elif negative_score > positive_score:
            return -0.3
        else:
            return 0.0
    
    async def _get_memories_for_situation(self, situation_type: str, 
                                        context: Optional[Dict[str, Any]]) -> List[Memory]:
        """Get memories relevant to a specific situation type."""
        # This would search for memories with similar context
        # For now, return memories with relevant categories
        relevant_categories = {
            'combat': [MemoryCategory.TRAUMA, MemoryCategory.EVENT],
            'trade': [MemoryCategory.INTERACTION, MemoryCategory.KNOWLEDGE],
            'diplomacy': [MemoryCategory.FACTION, MemoryCategory.RELATIONSHIP],
            'general': [MemoryCategory.EVENT, MemoryCategory.TRAUMA, MemoryCategory.ACHIEVEMENT]
        }
        
        categories = relevant_categories.get(situation_type, relevant_categories['general'])
        memories = []
        
        for category in categories:
            category_memories = await self.memory_manager.get_memories_by_category(category)
            memories.extend(category_memories)
        
        return memories
    
    def _calculate_risk_impact_from_memory(self, memory: Memory, situation_type: str) -> Optional[float]:
        """Calculate risk impact from a specific memory."""
        # Simplified risk calculation based on memory outcome
        if MemoryCategory.TRAUMA in memory.categories:
            return 0.8  # High risk if trauma occurred
        elif MemoryCategory.ACHIEVEMENT in memory.categories:
            return 0.2  # Low risk if positive outcome
        else:
            return 0.5  # Neutral risk
    
    def _extract_risk_factors_from_memory(self, memory: Memory) -> Dict[str, float]:
        """Extract specific risk factors from a memory."""
        factors = {}
        
        # Extract factors based on memory content and metadata
        if 'combat' in memory.content.lower():
            factors['combat_risk'] = 0.7
        if 'betrayal' in memory.content.lower():
            factors['trust_risk'] = 0.8
        if 'loss' in memory.content.lower():
            factors['resource_risk'] = 0.6
        
        return factors
    
    async def _get_emotional_memories(self) -> List[Memory]:
        """Get memories with high emotional content."""
        emotional_categories = [MemoryCategory.TRAUMA, MemoryCategory.ACHIEVEMENT, MemoryCategory.RELATIONSHIP]
        memories = []
        
        for category in emotional_categories:
            category_memories = await self.memory_manager.get_memories_by_category(category)
            memories.extend(category_memories)
        
        return memories
    
    def _analyze_memory_emotion(self, memory: Memory) -> Optional[Dict[str, Any]]:
        """Analyze the emotional content of a memory."""
        # Simplified emotion analysis
        content = memory.content.lower()
        
        emotions = {
            'anger': ['angry', 'furious', 'rage', 'betrayed'],
            'fear': ['afraid', 'terrified', 'scared', 'panic'],
            'sadness': ['sad', 'grief', 'loss', 'mourning'],
            'joy': ['happy', 'joyful', 'celebration', 'victory'],
            'trust': ['trust', 'loyal', 'reliable', 'honest'],
            'disgust': ['disgusted', 'revolted', 'sickened']
        }
        
        for emotion, keywords in emotions.items():
            if any(keyword in content for keyword in keywords):
                # Intensity based on memory importance and category
                intensity = memory.importance
                if MemoryCategory.TRAUMA in memory.categories:
                    intensity = min(1.0, intensity + 0.3)
                
                return {
                    'emotion': emotion,
                    'intensity': intensity
                }
        
        return None
    
    def _calculate_emotional_behavioral_effects(self, emotion: str, intensity: float) -> Dict[str, float]:
        """Calculate how an emotion affects behavior."""
        effects = {}
        
        emotion_effects = {
            'anger': {'aggression': 0.8, 'caution': -0.5, 'trust': -0.6},
            'fear': {'caution': 0.9, 'aggression': -0.4, 'trust': -0.3},
            'sadness': {'motivation': -0.5, 'social': -0.4, 'caution': 0.2},
            'joy': {'trust': 0.4, 'social': 0.6, 'caution': -0.3},
            'trust': {'cooperation': 0.7, 'caution': -0.2},
            'disgust': {'avoidance': 0.8, 'aggression': 0.3}
        }
        
        base_effects = emotion_effects.get(emotion, {})
        
        # Scale effects by intensity
        for effect_type, base_value in base_effects.items():
            effects[effect_type] = base_value * intensity
        
        return effects
    
    async def _get_faction_memories(self, faction_id: str) -> List[Memory]:
        """Get memories related to a specific faction."""
        faction_memories = await self.memory_manager.get_memories_by_category(MemoryCategory.FACTION)
        
        # Filter for specific faction
        relevant_memories = []
        for memory in faction_memories:
            if faction_id in memory.content or faction_id in memory.metadata.get('entities', []):
                relevant_memories.append(memory)
        
        return relevant_memories
    
    def _calculate_faction_bias_from_memory(self, memory: Memory, faction_id: str) -> float:
        """Calculate faction bias from a specific memory."""
        # Simplified faction bias calculation
        content = memory.content.lower()
        
        positive_indicators = ['helped', 'protected', 'allied', 'supported']
        negative_indicators = ['attacked', 'betrayed', 'enemy', 'hostile']
        
        positive_score = sum(1 for indicator in positive_indicators if indicator in content)
        negative_score = sum(1 for indicator in negative_indicators if indicator in content)
        
        if positive_score > negative_score:
            return 0.5 * memory.importance
        elif negative_score > positive_score:
            return -0.5 * memory.importance
        else:
            return 0.0 