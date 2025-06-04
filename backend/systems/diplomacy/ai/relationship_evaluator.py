"""
Diplomatic Relationship Evaluator

This module analyzes relationships between factions to inform AI diplomatic decisions.
It evaluates trust levels, threat assessments, opportunities, and historical context.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID
import logging
import math

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Levels of perceived threat from other factions"""
    
    NONE = 0           # No threat detected
    MINIMAL = 1        # Minor irritation or competition
    LOW = 2            # Some concerns but manageable
    MODERATE = 3       # Significant concern requiring attention
    HIGH = 4           # Major threat requiring counter-measures
    CRITICAL = 5       # Existential threat requiring immediate action

class OpportunityType(Enum):
    """Types of diplomatic opportunities that can be identified"""
    
    TRADE_PARTNER = "trade_partner"         # Economic cooperation potential
    ALLIANCE_CANDIDATE = "alliance_candidate"  # Military/political partnership
    BUFFER_STATE = "buffer_state"           # Useful neutral party
    EXPANSION_TARGET = "expansion_target"   # Potential conquest/absorption
    MEDIATION_PARTNER = "mediation_partner" # Helpful third party
    INFORMATION_SOURCE = "information_source"  # Intelligence value
    CULTURAL_EXCHANGE = "cultural_exchange"    # Soft power benefits

class TrustLevel(Enum):
    """Levels of trust between factions"""
    
    HOSTILE = 0        # Active enemies, expect betrayal
    DISTRUSTFUL = 1    # Deep suspicion, verify everything
    WARY = 2           # Cautious, limited cooperation
    NEUTRAL = 3        # No strong feelings either way
    CORDIAL = 4        # Generally positive relations
    TRUSTING = 5       # Reliable partner, benefit of doubt
    ALLIED = 6         # Deep trust, shared interests

@dataclass
class RelationshipHistory:
    """Historical context for faction relationships"""
    
    faction_a_id: UUID
    faction_b_id: UUID
    
    # Historical events
    treaties_signed: int = 0
    treaties_broken: int = 0
    conflicts_fought: int = 0
    trade_agreements: int = 0
    
    # Recent interactions (last 90 days)
    recent_positive_interactions: int = 0
    recent_negative_interactions: int = 0
    recent_neutral_interactions: int = 0
    
    # Significant events
    last_major_incident: Optional[datetime] = None
    last_treaty_date: Optional[datetime] = None
    last_conflict_date: Optional[datetime] = None
    
    # Trust modifiers from history
    historical_reliability: float = 0.5  # 0.0 to 1.0, based on treaty adherence
    conflict_resolution_success: float = 0.5  # How well they resolve disputes
    
    def calculate_historical_trust_modifier(self) -> float:
        """Calculate trust modifier based on historical interactions"""
        if self.treaties_signed == 0 and self.conflicts_fought == 0:
            return 0.0  # No history = no trust modifier
        
        # Positive factors
        positive_score = 0.0
        if self.treaties_signed > 0:
            treaty_reliability = 1.0 - (self.treaties_broken / max(1, self.treaties_signed))
            positive_score += treaty_reliability * 0.4
        
        positive_score += min(0.3, self.trade_agreements * 0.05)
        positive_score += min(0.2, self.recent_positive_interactions * 0.02)
        
        # Negative factors
        negative_score = 0.0
        negative_score += min(0.4, self.conflicts_fought * 0.1)
        negative_score += min(0.3, self.recent_negative_interactions * 0.03)
        negative_score += min(0.2, self.treaties_broken * 0.15)
        
        # Time decay for negative events
        if self.last_conflict_date:
            days_since_conflict = (datetime.utcnow() - self.last_conflict_date).days
            if days_since_conflict > 365:
                negative_score *= max(0.5, 1.0 - (days_since_conflict - 365) / 1825)  # 5 year decay
        
        return max(-0.5, min(0.5, positive_score - negative_score))

@dataclass
class RelationshipAnalysis:
    """Complete analysis of relationship between two factions"""
    
    faction_a_id: UUID
    faction_b_id: UUID
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Core relationship metrics
    trust_level: TrustLevel = TrustLevel.NEUTRAL
    threat_level: ThreatLevel = ThreatLevel.NONE
    
    # Detailed assessments
    trust_score: float = 0.5      # 0.0 to 1.0
    threat_score: float = 0.0     # 0.0 to 1.0  
    opportunity_score: float = 0.0  # 0.0 to 1.0
    
    # Strategic assessments
    power_balance: float = 0.0    # -1.0 (them stronger) to 1.0 (us stronger)
    strategic_value: float = 0.0  # How valuable this faction is strategically
    
    # Opportunities and threats
    opportunities: List[OpportunityType] = field(default_factory=list)
    threat_factors: List[str] = field(default_factory=list)
    
    # Historical context
    history: Optional[RelationshipHistory] = None
    
    # Recommendations
    recommended_actions: List[str] = field(default_factory=list)
    relationship_trajectory: str = "stable"  # "improving", "deteriorating", "stable"
    
    def get_overall_assessment(self) -> str:
        """Get a summary assessment of the relationship"""
        if self.threat_level.value >= ThreatLevel.HIGH.value:
            return "hostile"
        elif self.threat_level.value >= ThreatLevel.MODERATE.value:
            return "adversarial"
        elif self.trust_level.value >= TrustLevel.TRUSTING.value:
            return "friendly"
        elif self.trust_level.value >= TrustLevel.CORDIAL.value:
            return "positive"
        elif self.opportunity_score >= 0.7:
            return "opportunistic"
        else:
            return "neutral"

class RelationshipEvaluator:
    """Evaluates relationships between factions for diplomatic AI"""
    
    def __init__(self, diplomacy_service=None, faction_service=None):
        """Initialize with required services"""
        self.diplomacy_service = diplomacy_service
        self.faction_service = faction_service
        self.relationship_cache: Dict[Tuple[UUID, UUID], RelationshipAnalysis] = {}
        self.cache_duration = timedelta(hours=1)  # Cache results for 1 hour
    
    def evaluate_relationship(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID,
        force_refresh: bool = False
    ) -> RelationshipAnalysis:
        """Evaluate the complete relationship between two factions"""
        
        # Check cache first
        cache_key = (faction_a_id, faction_b_id)
        if not force_refresh and cache_key in self.relationship_cache:
            cached = self.relationship_cache[cache_key]
            if datetime.utcnow() - cached.evaluated_at < self.cache_duration:
                return cached
        
        # Perform fresh evaluation
        analysis = RelationshipAnalysis(
            faction_a_id=faction_a_id,
            faction_b_id=faction_b_id
        )
        
        # Get historical context
        analysis.history = self._build_relationship_history(faction_a_id, faction_b_id)
        
        # Evaluate trust
        analysis.trust_score, analysis.trust_level = self._evaluate_trust(
            faction_a_id, faction_b_id, analysis.history
        )
        
        # Evaluate threats
        analysis.threat_score, analysis.threat_level, analysis.threat_factors = self._evaluate_threats(
            faction_a_id, faction_b_id
        )
        
        # Evaluate opportunities
        analysis.opportunity_score, analysis.opportunities = self._evaluate_opportunities(
            faction_a_id, faction_b_id
        )
        
        # Assess power balance
        analysis.power_balance = self._assess_power_balance(faction_a_id, faction_b_id)
        
        # Calculate strategic value
        analysis.strategic_value = self._calculate_strategic_value(
            faction_a_id, faction_b_id, analysis
        )
        
        # Determine trajectory
        analysis.relationship_trajectory = self._determine_trajectory(
            faction_a_id, faction_b_id, analysis.history
        )
        
        # Generate recommendations
        analysis.recommended_actions = self._generate_recommendations(analysis)
        
        # Cache the result
        self.relationship_cache[cache_key] = analysis
        
        logger.debug(f"Evaluated relationship between {faction_a_id} and {faction_b_id}: "
                    f"trust={analysis.trust_level.name}, threat={analysis.threat_level.name}")
        
        return analysis
    
    def _build_relationship_history(self, faction_a_id: UUID, faction_b_id: UUID) -> RelationshipHistory:
        """Build historical context for the relationship"""
        history = RelationshipHistory(faction_a_id=faction_a_id, faction_b_id=faction_b_id)
        
        if not self.diplomacy_service:
            return history
        
        try:
            # Get treaty history
            treaties = self.diplomacy_service.list_treaties(faction_id=faction_a_id)
            for treaty in treaties:
                if faction_b_id in treaty.parties:
                    history.treaties_signed += 1
                    if treaty.status == "terminated":
                        history.treaties_broken += 1
                    
                    if not history.last_treaty_date or treaty.created_at > history.last_treaty_date:
                        history.last_treaty_date = treaty.created_at
            
            # Get incident history  
            incidents = self.diplomacy_service.list_diplomatic_incidents(faction_id=faction_a_id)
            for incident in incidents:
                if incident.victim_id == faction_b_id or incident.perpetrator_id == faction_b_id:
                    if incident.incident_type.value in ["ATTACK", "TERRITORY_VIOLATION", "ESPIONAGE"]:
                        history.conflicts_fought += 1
                        
                        if not history.last_conflict_date or incident.created_at > history.last_conflict_date:
                            history.last_conflict_date = incident.created_at
                    
                    # Count recent interactions (last 90 days)
                    if (datetime.utcnow() - incident.created_at).days <= 90:
                        if incident.severity.value >= 3:  # Significant incidents
                            history.recent_negative_interactions += 1
                        else:
                            history.recent_neutral_interactions += 1
            
            # Calculate reliability based on treaty adherence
            if history.treaties_signed > 0:
                history.historical_reliability = 1.0 - (history.treaties_broken / history.treaties_signed)
            
        except Exception as e:
            logger.warning(f"Error building relationship history: {e}")
        
        return history
    
    def _evaluate_trust(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID, 
        history: RelationshipHistory
    ) -> Tuple[float, TrustLevel]:
        """Evaluate trust level between factions"""
        
        base_trust = 0.5  # Neutral starting point
        
        # Historical modifier
        if history:
            base_trust += history.calculate_historical_trust_modifier()
        
        # Current diplomatic status modifier
        if self.diplomacy_service:
            try:
                relationship = self.diplomacy_service.get_faction_relationship(faction_a_id, faction_b_id)
                status = relationship.get("status", "NEUTRAL")
                
                trust_modifiers = {
                    "ALLIED": 0.3,
                    "FRIENDLY": 0.2,
                    "NEUTRAL": 0.0,
                    "HOSTILE": -0.3,
                    "WAR": -0.5
                }
                base_trust += trust_modifiers.get(status, 0.0)
                
                # Current tension modifier
                tension = relationship.get("tension", 50)
                tension_modifier = (50 - tension) / 100.0  # Lower tension = higher trust
                base_trust += tension_modifier * 0.2
                
            except Exception as e:
                logger.warning(f"Error getting faction relationship: {e}")
        
        # Faction personality modifiers
        trust_score = max(0.0, min(1.0, base_trust))
        
        # Convert to trust level
        if trust_score >= 0.85:
            trust_level = TrustLevel.ALLIED
        elif trust_score >= 0.7:
            trust_level = TrustLevel.TRUSTING
        elif trust_score >= 0.55:
            trust_level = TrustLevel.CORDIAL
        elif trust_score >= 0.45:
            trust_level = TrustLevel.NEUTRAL
        elif trust_score >= 0.3:
            trust_level = TrustLevel.WARY
        elif trust_score >= 0.15:
            trust_level = TrustLevel.DISTRUSTFUL
        else:
            trust_level = TrustLevel.HOSTILE
        
        return trust_score, trust_level
    
    def _evaluate_threats(self, faction_a_id: UUID, faction_b_id: UUID) -> Tuple[float, ThreatLevel, List[str]]:
        """Evaluate threat level posed by another faction"""
        
        threat_score = 0.0
        threat_factors = []
        
        if not self.diplomacy_service:
            return threat_score, ThreatLevel.NONE, threat_factors
        
        try:
            # Current diplomatic status
            relationship = self.diplomacy_service.get_faction_relationship(faction_a_id, faction_b_id)
            status = relationship.get("status", "NEUTRAL")
            tension = relationship.get("tension", 50)
            
            # Base threat from diplomatic status
            status_threats = {
                "WAR": 0.9,
                "HOSTILE": 0.6,
                "NEUTRAL": 0.1,
                "FRIENDLY": 0.0,
                "ALLIED": 0.0
            }
            threat_score += status_threats.get(status, 0.1)
            
            if status in ["WAR", "HOSTILE"]:
                threat_factors.append(f"Currently {status.lower()} diplomatic status")
            
            # Tension-based threat
            if tension > 70:
                tension_threat = (tension - 50) / 50.0 * 0.4  # Max 0.4 from tension
                threat_score += tension_threat
                threat_factors.append(f"High tension ({tension})")
            
            # Recent incidents
            incidents = self.diplomacy_service.list_diplomatic_incidents(
                faction_id=faction_a_id, 
                as_victim=True
            )
            
            recent_incidents = [
                i for i in incidents 
                if i.perpetrator_id == faction_b_id and 
                (datetime.utcnow() - i.created_at).days <= 30
            ]
            
            if recent_incidents:
                incident_threat = min(0.3, len(recent_incidents) * 0.1)
                threat_score += incident_threat
                threat_factors.append(f"{len(recent_incidents)} recent incidents")
            
            # Military/economic power considerations
            # Note: Would need access to faction capabilities data
            # For now, use a simplified approach
            
            # Proximity threat (if they're neighbors)
            # Note: Would need geographical data
            
        except Exception as e:
            logger.warning(f"Error evaluating threats: {e}")
        
        # Ensure threat score is bounded
        threat_score = max(0.0, min(1.0, threat_score))
        
        # Convert to threat level
        if threat_score >= 0.8:
            threat_level = ThreatLevel.CRITICAL
        elif threat_score >= 0.6:
            threat_level = ThreatLevel.HIGH
        elif threat_score >= 0.4:
            threat_level = ThreatLevel.MODERATE
        elif threat_score >= 0.2:
            threat_level = ThreatLevel.LOW
        elif threat_score >= 0.05:
            threat_level = ThreatLevel.MINIMAL
        else:
            threat_level = ThreatLevel.NONE
        
        return threat_score, threat_level, threat_factors
    
    def _evaluate_opportunities(self, faction_a_id: UUID, faction_b_id: UUID) -> Tuple[float, List[OpportunityType]]:
        """Evaluate diplomatic opportunities with another faction"""
        
        opportunities = []
        opportunity_score = 0.0
        
        if not self.diplomacy_service:
            return opportunity_score, opportunities
        
        try:
            relationship = self.diplomacy_service.get_faction_relationship(faction_a_id, faction_b_id)
            status = relationship.get("status", "NEUTRAL")
            tension = relationship.get("tension", 50)
            
            # Trade opportunities (low tension, not hostile)
            if tension < 60 and status not in ["WAR", "HOSTILE"]:
                if not self.diplomacy_service.has_treaty_of_type(
                    faction_a_id, faction_b_id, "TRADE"
                ):
                    opportunities.append(OpportunityType.TRADE_PARTNER)
                    opportunity_score += 0.2
            
            # Alliance opportunities (good relations, mutual threats)
            if status in ["FRIENDLY", "NEUTRAL"] and tension < 40:
                if not self.diplomacy_service.has_treaty_of_type(
                    faction_a_id, faction_b_id, "ALLIANCE"
                ):
                    opportunities.append(OpportunityType.ALLIANCE_CANDIDATE)
                    opportunity_score += 0.3
            
            # Buffer state opportunity (neutral, between us and threats)
            if status == "NEUTRAL" and 30 < tension < 60:
                opportunities.append(OpportunityType.BUFFER_STATE)
                opportunity_score += 0.15
            
            # Expansion opportunity (weak, no strong allies)
            if tension > 50 and status not in ["ALLIED", "FRIENDLY"]:
                # Would need power assessment to determine if they're weak
                pass
            
            # Information source (any non-hostile relation)
            if status != "WAR":
                opportunities.append(OpportunityType.INFORMATION_SOURCE)
                opportunity_score += 0.1
            
            # Mediation partner (good relations with others)
            if status in ["NEUTRAL", "FRIENDLY"] and tension < 50:
                opportunities.append(OpportunityType.MEDIATION_PARTNER)
                opportunity_score += 0.1
            
        except Exception as e:
            logger.warning(f"Error evaluating opportunities: {e}")
        
        opportunity_score = min(1.0, opportunity_score)
        return opportunity_score, opportunities
    
    def _assess_power_balance(self, faction_a_id: UUID, faction_b_id: UUID) -> float:
        """Assess relative power balance between factions"""
        # This would require access to faction capabilities, military strength, 
        # economic power, etc. For now, return neutral balance
        # 
        # In a full implementation, this would consider:
        # - Military units and strength
        # - Economic resources and GDP
        # - Territory controlled
        # - Population
        # - Technology level
        # - Number and strength of allies
        
        return 0.0  # Neutral balance placeholder
    
    def _calculate_strategic_value(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID, 
        analysis: RelationshipAnalysis
    ) -> float:
        """Calculate strategic value of relationship with this faction"""
        
        strategic_value = 0.0
        
        # Base value from opportunities
        strategic_value += analysis.opportunity_score * 0.4
        
        # Value from trust (reliable partners are valuable)
        strategic_value += analysis.trust_score * 0.3
        
        # Inverse value from threats (threats make relationship strategically important)
        strategic_value += analysis.threat_score * 0.2
        
        # Geographic/positional value (placeholder)
        strategic_value += 0.1  # Would be based on map position, resources, etc.
        
        return min(1.0, strategic_value)
    
    def _determine_trajectory(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID, 
        history: RelationshipHistory
    ) -> str:
        """Determine if relationship is improving, deteriorating, or stable"""
        
        if not history:
            return "stable"
        
        # Look at recent interactions vs historical average
        recent_positive = history.recent_positive_interactions
        recent_negative = history.recent_negative_interactions
        recent_total = recent_positive + recent_negative
        
        if recent_total < 2:
            return "stable"  # Not enough recent data
        
        recent_positive_ratio = recent_positive / recent_total
        
        # Compare to historical reliability
        if recent_positive_ratio > history.historical_reliability + 0.2:
            return "improving"
        elif recent_positive_ratio < history.historical_reliability - 0.2:
            return "deteriorating"
        else:
            return "stable"
    
    def _generate_recommendations(self, analysis: RelationshipAnalysis) -> List[str]:
        """Generate diplomatic recommendations based on analysis"""
        
        recommendations = []
        
        # Trust-based recommendations
        if analysis.trust_level.value >= TrustLevel.TRUSTING.value:
            recommendations.append("Consider deeper cooperation and alliance opportunities")
        elif analysis.trust_level.value <= TrustLevel.WARY.value:
            recommendations.append("Proceed with caution, verify all agreements")
        
        # Threat-based recommendations
        if analysis.threat_level.value >= ThreatLevel.HIGH.value:
            recommendations.append("Urgent: Prepare defensive measures or seek alliance support")
        elif analysis.threat_level.value >= ThreatLevel.MODERATE.value:
            recommendations.append("Monitor closely and consider deterrent measures")
        
        # Opportunity-based recommendations
        if OpportunityType.TRADE_PARTNER in analysis.opportunities:
            recommendations.append("Propose trade agreement to improve relations and economy")
        if OpportunityType.ALLIANCE_CANDIDATE in analysis.opportunities:
            recommendations.append("Explore military or defensive alliance possibilities")
        if OpportunityType.MEDIATION_PARTNER in analysis.opportunities:
            recommendations.append("Consider requesting mediation assistance for other conflicts")
        
        # Trajectory-based recommendations
        if analysis.relationship_trajectory == "deteriorating":
            recommendations.append("Address underlying issues before relationship worsens further")
        elif analysis.relationship_trajectory == "improving":
            recommendations.append("Capitalize on positive momentum with strategic initiatives")
        
        return recommendations
    
    def analyze_regional_relationships(self, faction_id: UUID, region_factions: List[UUID]) -> Dict[UUID, RelationshipAnalysis]:
        """Analyze relationships with all factions in a region"""
        
        analyses = {}
        
        for other_faction_id in region_factions:
            if other_faction_id != faction_id:
                analysis = self.evaluate_relationship(faction_id, other_faction_id)
                analyses[other_faction_id] = analysis
        
        return analyses
    
    def identify_coalition_opportunities(
        self, 
        faction_id: UUID, 
        potential_partners: List[UUID]
    ) -> List[Tuple[List[UUID], float]]:
        """Identify potential coalition opportunities"""
        
        coalitions = []
        
        # Evaluate all possible combinations of 2-4 partners
        from itertools import combinations
        
        for size in range(2, min(5, len(potential_partners) + 1)):
            for partner_combo in combinations(potential_partners, size):
                # Evaluate coalition viability
                viability_score = self._evaluate_coalition_viability(
                    faction_id, list(partner_combo)
                )
                
                if viability_score > 0.5:  # Only include viable coalitions
                    coalitions.append((list(partner_combo), viability_score))
        
        # Sort by viability score
        coalitions.sort(key=lambda x: x[1], reverse=True)
        
        return coalitions[:5]  # Return top 5 coalitions
    
    def _evaluate_coalition_viability(self, faction_id: UUID, partners: List[UUID]) -> float:
        """Evaluate viability of a potential coalition"""
        
        if not partners:
            return 0.0
        
        viability_score = 0.0
        
        # Evaluate relationships with each partner
        partner_trust_sum = 0.0
        min_trust = 1.0
        
        for partner_id in partners:
            analysis = self.evaluate_relationship(faction_id, partner_id)
            partner_trust_sum += analysis.trust_score
            min_trust = min(min_trust, analysis.trust_score)
        
        # Average trust, but penalize if any partner has very low trust
        avg_trust = partner_trust_sum / len(partners)
        trust_score = avg_trust * (0.7 + 0.3 * min_trust)
        viability_score += trust_score * 0.5
        
        # Evaluate mutual compatibility (partners should not hate each other)
        compatibility_score = 1.0
        for i, partner_a in enumerate(partners):
            for partner_b in partners[i+1:]:
                partner_analysis = self.evaluate_relationship(partner_a, partner_b)
                if partner_analysis.threat_level.value >= ThreatLevel.HIGH.value:
                    compatibility_score *= 0.5  # Significant penalty for hostile partners
        
        viability_score += compatibility_score * 0.3
        
        # Strategic value (larger coalitions can be more powerful but harder to manage)
        size_factor = min(1.0, len(partners) / 3.0)  # Optimal size around 3
        viability_score += size_factor * 0.2
        
        return min(1.0, viability_score)

# Global evaluator instance
_relationship_evaluator = None

def get_relationship_evaluator(diplomacy_service=None, faction_service=None) -> RelationshipEvaluator:
    """Get the global relationship evaluator instance"""
    global _relationship_evaluator
    if _relationship_evaluator is None:
        _relationship_evaluator = RelationshipEvaluator(diplomacy_service, faction_service)
    return _relationship_evaluator 