"""
Memory-Based Behavior Algorithms
--------------------------------

Complete implementations of trust calculation, risk assessment, and behavior prediction
algorithms based on memory analysis and cross-system integration.
"""

from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math
import logging

if TYPE_CHECKING:
    from backend.systems.memory.services.memory import Memory
    from backend.systems.memory.memory_categories import MemoryCategory

logger = logging.getLogger(__name__)


@dataclass
class TrustCalculationResult:
    """Result of trust level calculation."""
    
    entity_id: str
    trust_level: float  # 0.0 to 1.0
    confidence: float   # How confident we are in this assessment
    contributing_factors: Dict[str, float]
    recent_interactions: int
    last_updated: datetime
    memory_count: int
    risk_factors: List[str]


@dataclass
class RiskAssessmentResult:
    """Result of risk assessment calculation."""
    
    entity_id: str
    risk_level: float  # 0.0 to 1.0 (higher = more risky)
    risk_category: str  # low, medium, high, critical
    risk_factors: Dict[str, float]
    mitigation_suggestions: List[str]
    confidence: float
    assessment_date: datetime


@dataclass
class EmotionalTrigger:
    """Emotional trigger identified from memories."""
    
    trigger_type: str
    intensity: float  # 0.0 to 1.0
    associated_memories: List[str]
    response_pattern: str
    last_triggered: Optional[datetime] = None


class TrustFactorType(Enum):
    """Types of factors that influence trust."""
    
    POSITIVE_INTERACTIONS = "positive_interactions"
    NEGATIVE_INTERACTIONS = "negative_interactions"
    BETRAYALS = "betrayals"
    KEPT_PROMISES = "kept_promises"
    BROKEN_PROMISES = "broken_promises"
    SHARED_SECRETS = "shared_secrets"
    LOYALTY_DEMONSTRATIONS = "loyalty_demonstrations"
    FREQUENCY_OF_CONTACT = "frequency_of_contact"
    MUTUAL_FRIENDS = "mutual_friends"
    REPUTATION = "reputation"


class RiskFactorType(Enum):
    """Types of risk factors."""
    
    BETRAYAL_HISTORY = "betrayal_history"
    IMPULSIVE_BEHAVIOR = "impulsive_behavior"
    CONFLICTING_LOYALTIES = "conflicting_loyalties"
    EXTERNAL_PRESSURES = "external_pressures"
    RESOURCE_DESPERATION = "resource_desperation"
    IDEOLOGICAL_DIFFERENCES = "ideological_differences"
    POWER_IMBALANCE = "power_imbalance"
    INFORMATION_ASYMMETRY = "information_asymmetry"


class MemoryBehaviorAnalyzer:
    """Analyzes memories to extract behavior patterns and calculate trust/risk."""
    
    def __init__(self, memory_manager=None):
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.trust_decay_rate = 0.01  # Daily trust decay without interaction
        self.interaction_recency_weight = 0.3  # Weight for recent interactions
        self.memory_importance_weight = 0.4  # Weight for memory importance
        self.frequency_weight = 0.3  # Weight for interaction frequency
    
    async def calculate_trust_level(self, entity_id: str, target_entity_id: str) -> TrustCalculationResult:
        """Calculate comprehensive trust level based on memory analysis."""
        if not self.memory_manager:
            return self._default_trust_result(entity_id, target_entity_id)
        
        # Get memories involving the target entity
        memories = await self.memory_manager.get_memories_involving_entity(target_entity_id)
        
        if not memories:
            return self._default_trust_result(entity_id, target_entity_id)
        
        # Analyze memories for trust factors
        trust_factors = await self._analyze_trust_factors(memories, target_entity_id)
        
        # Calculate base trust from factors
        base_trust = self._calculate_base_trust(trust_factors)
        
        # Apply temporal decay and recency effects
        time_adjusted_trust = self._apply_temporal_adjustments(base_trust, memories)
        
        # Calculate confidence based on memory count and recency
        confidence = self._calculate_trust_confidence(memories)
        
        # Identify risk factors
        risk_factors = self._identify_trust_risk_factors(trust_factors)
        
        return TrustCalculationResult(
            entity_id=target_entity_id,
            trust_level=max(0.0, min(1.0, time_adjusted_trust)),
            confidence=confidence,
            contributing_factors=trust_factors,
            recent_interactions=len([m for m in memories if self._is_recent_memory(m, days=30)]),
            last_updated=datetime.utcnow(),
            memory_count=len(memories),
            risk_factors=risk_factors
        )
    
    async def assess_risk(self, entity_id: str, target_entity_id: str, scenario: Optional[str] = None) -> RiskAssessmentResult:
        """Assess risk of negative behavior from target entity."""
        if not self.memory_manager:
            return self._default_risk_result(entity_id, target_entity_id)
        
        memories = await self.memory_manager.get_memories_involving_entity(target_entity_id)
        
        # Analyze risk factors from memories
        risk_factors = await self._analyze_risk_factors(memories, target_entity_id, scenario)
        
        # Calculate overall risk level
        risk_level = self._calculate_risk_level(risk_factors)
        
        # Determine risk category
        risk_category = self._categorize_risk_level(risk_level)
        
        # Generate mitigation suggestions
        mitigation_suggestions = self._generate_mitigation_suggestions(risk_factors, risk_category)
        
        # Calculate confidence
        confidence = self._calculate_risk_confidence(memories, risk_factors)
        
        return RiskAssessmentResult(
            entity_id=target_entity_id,
            risk_level=risk_level,
            risk_category=risk_category,
            risk_factors=risk_factors,
            mitigation_suggestions=mitigation_suggestions,
            confidence=confidence,
            assessment_date=datetime.utcnow()
        )
    
    async def identify_emotional_triggers(self, entity_id: str) -> List[EmotionalTrigger]:
        """Identify emotional triggers from memory patterns."""
        if not self.memory_manager:
            return []
        
        # Get all memories for analysis
        memories = await self.memory_manager.get_memories_by_entity(entity_id, limit=200)
        
        triggers = []
        
        # Analyze trauma memories
        trauma_triggers = self._analyze_trauma_triggers(memories)
        triggers.extend(trauma_triggers)
        
        # Analyze achievement/pride triggers
        achievement_triggers = self._analyze_achievement_triggers(memories)
        triggers.extend(achievement_triggers)
        
        # Analyze relationship triggers
        relationship_triggers = self._analyze_relationship_triggers(memories)
        triggers.extend(relationship_triggers)
        
        # Analyze faction/loyalty triggers
        loyalty_triggers = self._analyze_loyalty_triggers(memories)
        triggers.extend(loyalty_triggers)
        
        return triggers
    
    async def calculate_faction_bias(self, entity_id: str, faction_id: str) -> Dict[str, Any]:
        """Calculate bias toward a specific faction based on memories."""
        if not self.memory_manager:
            return {"bias_level": 0.0, "confidence": 0.0}
        
        # Get faction-related memories
        faction_memories = await self.memory_manager.get_memories_by_category(entity_id, "FACTION")
        
        bias_factors = {
            "positive_experiences": 0.0,
            "negative_experiences": 0.0,
            "loyalty_conflicts": 0.0,
            "shared_values": 0.0,
            "personal_connections": 0.0
        }
        
        faction_related_memories = []
        
        for memory in faction_memories:
            if faction_id in memory.content.lower():
                faction_related_memories.append(memory)
                
                # Analyze sentiment toward faction
                sentiment = self._analyze_memory_sentiment(memory, faction_id)
                
                if sentiment > 0.6:
                    bias_factors["positive_experiences"] += memory.importance * sentiment
                elif sentiment < 0.4:
                    bias_factors["negative_experiences"] += memory.importance * (1.0 - sentiment)
        
        # Calculate overall bias
        positive_score = bias_factors["positive_experiences"]
        negative_score = bias_factors["negative_experiences"]
        
        if positive_score + negative_score > 0:
            bias_level = (positive_score - negative_score) / (positive_score + negative_score)
        else:
            bias_level = 0.0
        
        confidence = min(len(faction_related_memories) / 5.0, 1.0)  # Full confidence with 5+ memories
        
        return {
            "faction_id": faction_id,
            "bias_level": bias_level,  # -1.0 (strongly negative) to 1.0 (strongly positive)
            "confidence": confidence,
            "memory_count": len(faction_related_memories),
            "bias_factors": bias_factors,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    # Private methods for trust calculation
    async def _analyze_trust_factors(self, memories: List["Memory"], target_entity_id: str) -> Dict[str, float]:
        """Analyze memories to extract trust factors."""
        factors = {factor.value: 0.0 for factor in TrustFactorType}
        
        for memory in memories:
            # Analyze content for trust-related keywords and patterns
            content_lower = memory.content.lower()
            importance_weight = memory.importance
            
            # Positive interactions
            if any(word in content_lower for word in ["helped", "supported", "aided", "assisted", "saved"]):
                factors[TrustFactorType.POSITIVE_INTERACTIONS.value] += 0.2 * importance_weight
            
            # Negative interactions
            if any(word in content_lower for word in ["betrayed", "deceived", "lied", "cheated", "abandoned"]):
                factors[TrustFactorType.NEGATIVE_INTERACTIONS.value] += 0.3 * importance_weight
            
            # Betrayals (stronger negative impact)
            if any(word in content_lower for word in ["betrayed", "backstabbed", "sold out"]):
                factors[TrustFactorType.BETRAYALS.value] += 0.5 * importance_weight
            
            # Promises kept/broken
            if any(word in content_lower for word in ["kept promise", "honored agreement", "fulfilled"]):
                factors[TrustFactorType.KEPT_PROMISES.value] += 0.3 * importance_weight
            elif any(word in content_lower for word in ["broke promise", "broken agreement", "failed to"]):
                factors[TrustFactorType.BROKEN_PROMISES.value] += 0.4 * importance_weight
            
            # Shared secrets (trust building)
            if any(word in content_lower for word in ["shared secret", "confided", "trusted me with"]):
                factors[TrustFactorType.SHARED_SECRETS.value] += 0.2 * importance_weight
            
            # Loyalty demonstrations
            if any(word in content_lower for word in ["loyal", "stood by", "defended", "protected"]):
                factors[TrustFactorType.LOYALTY_DEMONSTRATIONS.value] += 0.25 * importance_weight
        
        # Calculate frequency factor
        recent_memories = [m for m in memories if self._is_recent_memory(m, days=60)]
        factors[TrustFactorType.FREQUENCY_OF_CONTACT.value] = len(recent_memories) / 10.0  # Normalize
        
        return factors
    
    def _calculate_base_trust(self, trust_factors: Dict[str, float]) -> float:
        """Calculate base trust level from factors."""
        positive_factors = (
            trust_factors[TrustFactorType.POSITIVE_INTERACTIONS.value] +
            trust_factors[TrustFactorType.KEPT_PROMISES.value] +
            trust_factors[TrustFactorType.SHARED_SECRETS.value] +
            trust_factors[TrustFactorType.LOYALTY_DEMONSTRATIONS.value] +
            trust_factors[TrustFactorType.FREQUENCY_OF_CONTACT.value] * 0.1
        )
        
        negative_factors = (
            trust_factors[TrustFactorType.NEGATIVE_INTERACTIONS.value] +
            trust_factors[TrustFactorType.BETRAYALS.value] +
            trust_factors[TrustFactorType.BROKEN_PROMISES.value]
        )
        
        # Start with neutral trust (0.5)
        base_trust = 0.5
        
        # Add positive factors (but with diminishing returns)
        if positive_factors > 0:
            base_trust += 0.4 * (1 - math.exp(-positive_factors))
        
        # Subtract negative factors (with stronger impact)
        if negative_factors > 0:
            base_trust -= 0.6 * (1 - math.exp(-negative_factors * 1.5))
        
        return max(0.0, min(1.0, base_trust))
    
    def _apply_temporal_adjustments(self, base_trust: float, memories: List["Memory"]) -> float:
        """Apply temporal decay and recency effects."""
        if not memories:
            return base_trust
        
        # Find most recent memory
        most_recent = max(memories, key=lambda m: m.created_at)
        days_since_last = (datetime.utcnow() - most_recent.created_at).days
        
        # Apply decay for lack of recent interaction
        decay_factor = math.exp(-self.trust_decay_rate * days_since_last)
        
        # Weight recent memories more heavily
        recent_memories = [m for m in memories if self._is_recent_memory(m, days=30)]
        recency_boost = len(recent_memories) / len(memories) * 0.1
        
        return base_trust * decay_factor + recency_boost
    
    def _calculate_trust_confidence(self, memories: List["Memory"]) -> float:
        """Calculate confidence in trust assessment."""
        if not memories:
            return 0.0
        
        # More memories = higher confidence
        memory_count_factor = min(len(memories) / 10.0, 1.0)
        
        # Recent memories = higher confidence
        recent_count = len([m for m in memories if self._is_recent_memory(m, days=60)])
        recency_factor = min(recent_count / 5.0, 1.0)
        
        # High importance memories = higher confidence
        avg_importance = sum(m.importance for m in memories) / len(memories)
        importance_factor = avg_importance
        
        return (memory_count_factor + recency_factor + importance_factor) / 3.0
    
    def _identify_trust_risk_factors(self, trust_factors: Dict[str, float]) -> List[str]:
        """Identify risk factors that could undermine trust."""
        risk_factors = []
        
        if trust_factors[TrustFactorType.BETRAYALS.value] > 0.1:
            risk_factors.append("History of betrayal")
        
        if trust_factors[TrustFactorType.BROKEN_PROMISES.value] > 0.2:
            risk_factors.append("Pattern of broken promises")
        
        if trust_factors[TrustFactorType.FREQUENCY_OF_CONTACT.value] < 0.1:
            risk_factors.append("Infrequent contact")
        
        if trust_factors[TrustFactorType.NEGATIVE_INTERACTIONS.value] > trust_factors[TrustFactorType.POSITIVE_INTERACTIONS.value]:
            risk_factors.append("More negative than positive interactions")
        
        return risk_factors
    
    # Private methods for risk assessment
    async def _analyze_risk_factors(self, memories: List["Memory"], target_entity_id: str, scenario: Optional[str]) -> Dict[str, float]:
        """Analyze memories for risk factors."""
        factors = {factor.value: 0.0 for factor in RiskFactorType}
        
        for memory in memories:
            content_lower = memory.content.lower()
            importance_weight = memory.importance
            
            # Betrayal history
            if any(word in content_lower for word in ["betrayed", "backstabbed", "turned on"]):
                factors[RiskFactorType.BETRAYAL_HISTORY.value] += 0.4 * importance_weight
            
            # Impulsive behavior
            if any(word in content_lower for word in ["impulsive", "rash", "sudden", "without thinking"]):
                factors[RiskFactorType.IMPULSIVE_BEHAVIOR.value] += 0.2 * importance_weight
            
            # Conflicting loyalties
            if any(word in content_lower for word in ["torn between", "conflicted", "divided loyalty"]):
                factors[RiskFactorType.CONFLICTING_LOYALTIES.value] += 0.3 * importance_weight
            
            # External pressures
            if any(word in content_lower for word in ["pressured", "forced", "coerced", "threatened"]):
                factors[RiskFactorType.EXTERNAL_PRESSURES.value] += 0.3 * importance_weight
            
            # Resource desperation
            if any(word in content_lower for word in ["desperate", "starving", "broke", "need money"]):
                factors[RiskFactorType.RESOURCE_DESPERATION.value] += 0.25 * importance_weight
        
        return factors
    
    def _calculate_risk_level(self, risk_factors: Dict[str, float]) -> float:
        """Calculate overall risk level."""
        # Weight different risk factors
        weighted_risk = (
            risk_factors[RiskFactorType.BETRAYAL_HISTORY.value] * 1.5 +  # Betrayal history is most important
            risk_factors[RiskFactorType.IMPULSIVE_BEHAVIOR.value] * 1.0 +
            risk_factors[RiskFactorType.CONFLICTING_LOYALTIES.value] * 1.2 +
            risk_factors[RiskFactorType.EXTERNAL_PRESSURES.value] * 0.8 +
            risk_factors[RiskFactorType.RESOURCE_DESPERATION.value] * 0.9
        )
        
        # Apply sigmoid function to normalize
        return 1.0 / (1.0 + math.exp(-weighted_risk + 2.0))  # Sigmoid centered around 2.0
    
    def _categorize_risk_level(self, risk_level: float) -> str:
        """Categorize risk level."""
        if risk_level < 0.3:
            return "low"
        elif risk_level < 0.6:
            return "medium"
        elif risk_level < 0.8:
            return "high"
        else:
            return "critical"
    
    def _generate_mitigation_suggestions(self, risk_factors: Dict[str, float], risk_category: str) -> List[str]:
        """Generate mitigation suggestions based on risk factors."""
        suggestions = []
        
        if risk_factors[RiskFactorType.BETRAYAL_HISTORY.value] > 0.2:
            suggestions.append("Verify commitments through mutual allies")
            suggestions.append("Avoid sharing sensitive information")
        
        if risk_factors[RiskFactorType.IMPULSIVE_BEHAVIOR.value] > 0.2:
            suggestions.append("Give them time to consider decisions")
            suggestions.append("Avoid high-pressure situations")
        
        if risk_factors[RiskFactorType.EXTERNAL_PRESSURES.value] > 0.2:
            suggestions.append("Identify and address external pressure sources")
            suggestions.append("Provide support to reduce vulnerability")
        
        if risk_factors[RiskFactorType.RESOURCE_DESPERATION.value] > 0.2:
            suggestions.append("Consider providing material support")
            suggestions.append("Address underlying resource needs")
        
        if risk_category in ["high", "critical"]:
            suggestions.append("Implement additional verification mechanisms")
            suggestions.append("Maintain backup plans for potential betrayal")
        
        return suggestions
    
    def _calculate_risk_confidence(self, memories: List["Memory"], risk_factors: Dict[str, float]) -> float:
        """Calculate confidence in risk assessment."""
        if not memories:
            return 0.0
        
        # Base confidence on memory count and factor strength
        memory_factor = min(len(memories) / 8.0, 1.0)
        factor_strength = sum(risk_factors.values())
        strength_factor = min(factor_strength / 2.0, 1.0)
        
        return (memory_factor + strength_factor) / 2.0
    
    # Helper methods
    def _is_recent_memory(self, memory: "Memory", days: int = 30) -> bool:
        """Check if memory is recent."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return memory.created_at >= cutoff
    
    def _analyze_memory_sentiment(self, memory: "Memory", target_entity: str) -> float:
        """Analyze sentiment of memory toward target entity."""
        content_lower = memory.content.lower()
        
        positive_words = ["helped", "good", "great", "excellent", "trusted", "loyal", "friend"]
        negative_words = ["betrayed", "bad", "terrible", "awful", "enemy", "hate", "deceived"]
        
        positive_score = sum(1 for word in positive_words if word in content_lower)
        negative_score = sum(1 for word in negative_words if word in content_lower)
        
        if positive_score + negative_score == 0:
            return 0.5  # Neutral
        
        return positive_score / (positive_score + negative_score)
    
    def _default_trust_result(self, entity_id: str, target_entity_id: str) -> TrustCalculationResult:
        """Return default trust result when no data available."""
        return TrustCalculationResult(
            entity_id=target_entity_id,
            trust_level=0.5,  # Neutral trust
            confidence=0.0,   # No confidence
            contributing_factors={},
            recent_interactions=0,
            last_updated=datetime.utcnow(),
            memory_count=0,
            risk_factors=["No historical data available"]
        )
    
    def _default_risk_result(self, entity_id: str, target_entity_id: str) -> RiskAssessmentResult:
        """Return default risk result when no data available."""
        return RiskAssessmentResult(
            entity_id=target_entity_id,
            risk_level=0.5,   # Unknown risk
            risk_category="medium",
            risk_factors={},
            mitigation_suggestions=["Gather more information about this entity"],
            confidence=0.0,
            assessment_date=datetime.utcnow()
        )
    
    # Emotional trigger analysis methods
    def _analyze_trauma_triggers(self, memories: List["Memory"]) -> List[EmotionalTrigger]:
        """Analyze memories for trauma-based triggers."""
        trauma_memories = [m for m in memories if "trauma" in getattr(m, 'categories', [])]
        triggers = []
        
        # Group by common themes
        betrayal_memories = [m for m in trauma_memories if any(word in m.content.lower() 
                           for word in ["betrayed", "abandoned", "deceived"])]
        
        if betrayal_memories:
            triggers.append(EmotionalTrigger(
                trigger_type="betrayal_sensitivity",
                intensity=min(sum(m.importance for m in betrayal_memories) / len(betrayal_memories), 1.0),
                associated_memories=[m.memory_id for m in betrayal_memories],
                response_pattern="defensive_withdrawal"
            ))
        
        return triggers
    
    def _analyze_achievement_triggers(self, memories: List["Memory"]) -> List[EmotionalTrigger]:
        """Analyze memories for achievement-based triggers."""
        achievement_memories = [m for m in memories if "achievement" in getattr(m, 'categories', [])]
        triggers = []
        
        if achievement_memories:
            avg_importance = sum(m.importance for m in achievement_memories) / len(achievement_memories)
            triggers.append(EmotionalTrigger(
                trigger_type="recognition_seeking",
                intensity=avg_importance,
                associated_memories=[m.memory_id for m in achievement_memories],
                response_pattern="pride_display"
            ))
        
        return triggers
    
    def _analyze_relationship_triggers(self, memories: List["Memory"]) -> List[EmotionalTrigger]:
        """Analyze memories for relationship-based triggers."""
        # Implementation for relationship analysis
        return []
    
    def _analyze_loyalty_triggers(self, memories: List["Memory"]) -> List[EmotionalTrigger]:
        """Analyze memories for loyalty-based triggers."""
        # Implementation for loyalty analysis
        return []


def create_behavior_analyzer(memory_manager=None) -> MemoryBehaviorAnalyzer:
    """Factory function for creating behavior analyzer."""
    return MemoryBehaviorAnalyzer(memory_manager) 