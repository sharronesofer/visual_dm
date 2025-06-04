"""
Strategic Analysis Framework

This module provides strategic analysis capabilities for diplomatic AI decision-making.
It evaluates power balance, coalition opportunities, risk assessment, and timing considerations.
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

class PowerCategory(Enum):
    """Categories of power for strategic analysis"""
    
    MILITARY = "military"           # Armed forces and military capability
    ECONOMIC = "economic"           # Economic resources and trade power
    DIPLOMATIC = "diplomatic"       # Alliance network and influence
    TERRITORIAL = "territorial"     # Land control and strategic positions
    TECHNOLOGICAL = "technological" # Advanced capabilities and innovation
    CULTURAL = "cultural"           # Soft power and influence

class RiskLevel(Enum):
    """Risk assessment levels for strategic decisions"""
    
    MINIMAL = 1      # Very low risk, high confidence
    LOW = 2          # Some risk but manageable
    MODERATE = 3     # Significant risk requiring careful planning
    HIGH = 4         # Major risk, requires strong justification
    EXTREME = 5      # Potentially catastrophic risk

class TimingFactor(Enum):
    """Factors affecting timing of strategic decisions"""
    
    IMMEDIATE = "immediate"         # Act now or lose opportunity
    URGENT = "urgent"              # Act within days/weeks
    OPTIMAL = "optimal"            # Best time to act
    ACCEPTABLE = "acceptable"      # Reasonable time to act
    POOR = "poor"                  # Bad timing, should wait
    CRITICAL_DELAY = "critical_delay"  # Waiting too long is dangerous

@dataclass
class PowerBalance:
    """Analysis of relative power between factions"""
    
    faction_a_id: UUID
    faction_b_id: UUID
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Power scores by category (0.0 to 1.0 for each faction)
    military_balance: float = 0.0      # Positive = A stronger, Negative = B stronger
    economic_balance: float = 0.0
    diplomatic_balance: float = 0.0
    territorial_balance: float = 0.0
    technological_balance: float = 0.0
    cultural_balance: float = 0.0
    
    # Overall assessment
    overall_balance: float = 0.0       # -1.0 to 1.0
    confidence: float = 0.5            # How confident we are in this assessment
    
    # Trend analysis
    balance_trend: str = "stable"      # "improving", "deteriorating", "stable"
    projected_balance_6m: float = 0.0  # Projected balance in 6 months
    
    def get_dominant_faction(self) -> Optional[UUID]:
        """Get the faction with overall advantage"""
        if abs(self.overall_balance) < 0.1:
            return None  # Too close to call
        return self.faction_a_id if self.overall_balance > 0 else self.faction_b_id
    
    def get_power_gap(self) -> float:
        """Get the magnitude of power difference (0.0 to 1.0)"""
        return abs(self.overall_balance)
    
    def is_balanced(self, threshold: float = 0.2) -> bool:
        """Check if power is relatively balanced"""
        return abs(self.overall_balance) < threshold

@dataclass
class CoalitionOpportunity:
    """Analysis of potential coalition formation"""
    
    primary_faction_id: UUID
    potential_partners: List[UUID] = field(default_factory=list)
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Coalition strength assessment
    combined_power_score: float = 0.0   # Total power if coalition forms
    power_multiplier: float = 1.0       # Synergy effects (>1.0 = synergy, <1.0 = friction)
    stability_score: float = 0.5        # How stable the coalition would be
    
    # Strategic value
    strategic_objectives: List[str] = field(default_factory=list)
    target_factions: List[UUID] = field(default_factory=list)  # Who coalition would oppose
    success_probability: float = 0.5
    
    # Costs and risks
    formation_difficulty: float = 0.5   # How hard to form (0.0 = easy, 1.0 = very hard)
    maintenance_cost: float = 0.3       # Ongoing diplomatic cost
    betrayal_risk: float = 0.2          # Risk of partners betraying
    
    # Timing
    optimal_formation_window: Tuple[datetime, datetime] = field(default=None)
    urgency_score: float = 0.3          # How urgent formation is
    
    def get_net_value(self) -> float:
        """Calculate net strategic value of coalition"""
        benefits = self.combined_power_score * self.power_multiplier * self.success_probability
        costs = self.formation_difficulty + self.maintenance_cost + self.betrayal_risk
        return max(0.0, benefits - costs)
    
    def is_viable(self, threshold: float = 0.3) -> bool:
        """Check if coalition is strategically viable"""
        return self.get_net_value() > threshold and self.stability_score > 0.4

@dataclass
class RiskAssessment:
    """Comprehensive risk analysis for strategic decisions"""
    
    decision_type: str  # Type of decision being evaluated
    faction_id: UUID
    target_faction_id: Optional[UUID] = None
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Risk categories
    military_risk: RiskLevel = RiskLevel.MODERATE
    economic_risk: RiskLevel = RiskLevel.MODERATE
    diplomatic_risk: RiskLevel = RiskLevel.MODERATE
    reputation_risk: RiskLevel = RiskLevel.MODERATE
    
    # Specific risk factors
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    
    # Probability assessments
    success_probability: float = 0.5
    catastrophic_failure_probability: float = 0.1
    acceptable_outcome_probability: float = 0.7
    
    # Impact assessments
    success_impact: float = 0.5         # Positive impact if successful
    failure_impact: float = -0.3        # Negative impact if failed
    
    # Overall risk score
    overall_risk: RiskLevel = RiskLevel.MODERATE
    risk_tolerance_required: float = 0.5  # How much risk tolerance needed
    
    def calculate_expected_value(self) -> float:
        """Calculate expected value of the decision"""
        expected_success = self.success_probability * self.success_impact
        expected_failure = (1.0 - self.success_probability) * self.failure_impact
        return expected_success + expected_failure
    
    def is_acceptable_risk(self, faction_risk_tolerance: float) -> bool:
        """Check if risk is acceptable given faction's risk tolerance"""
        return self.risk_tolerance_required <= faction_risk_tolerance

@dataclass
class TimingAnalysis:
    """Analysis of optimal timing for strategic decisions"""
    
    decision_type: str
    faction_id: UUID
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Current timing assessment
    current_timing: TimingFactor = TimingFactor.ACCEPTABLE
    timing_score: float = 0.5           # 0.0 = terrible timing, 1.0 = perfect timing
    
    # Window analysis
    optimal_window_start: Optional[datetime] = None
    optimal_window_end: Optional[datetime] = None
    deadline: Optional[datetime] = None  # Latest possible action time
    
    # Timing factors
    internal_readiness: float = 0.5     # How ready the faction is
    external_conditions: float = 0.5    # How favorable external conditions are
    opportunity_decay: float = 0.1      # How quickly opportunity diminishes
    
    # Specific timing considerations
    timing_factors: List[str] = field(default_factory=list)
    
    def get_timing_urgency(self) -> float:
        """Calculate how urgent action is (0.0 = no rush, 1.0 = act immediately)"""
        urgency = 0.0
        
        # Deadline pressure
        if self.deadline:
            time_remaining = (self.deadline - datetime.utcnow()).total_seconds()
            if time_remaining > 0:
                urgency += min(0.4, 86400.0 / time_remaining)  # 1 day = 0.4 urgency
        
        # Opportunity decay
        urgency += self.opportunity_decay * 0.3
        
        # Current timing quality
        if self.current_timing == TimingFactor.IMMEDIATE:
            urgency += 0.5
        elif self.current_timing == TimingFactor.URGENT:
            urgency += 0.3
        
        return min(1.0, urgency)
    
    def should_act_now(self) -> bool:
        """Determine if action should be taken immediately"""
        return (self.current_timing in [TimingFactor.IMMEDIATE, TimingFactor.URGENT] or
                self.get_timing_urgency() > 0.7)

class StrategicAnalyzer:
    """Comprehensive strategic analysis for diplomatic AI"""
    
    def __init__(self, diplomacy_service=None, faction_service=None, economy_service=None):
        """Initialize with required services"""
        self.diplomacy_service = diplomacy_service
        self.faction_service = faction_service
        self.economy_service = economy_service
        
        # Analysis caches
        self.power_balance_cache: Dict[Tuple[UUID, UUID], PowerBalance] = {}
        self.coalition_cache: Dict[UUID, List[CoalitionOpportunity]] = {}
        self.cache_duration = timedelta(hours=2)
    
    def analyze_power_balance(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID,
        force_refresh: bool = False
    ) -> PowerBalance:
        """Analyze relative power balance between two factions"""
        
        # Check cache
        cache_key = (faction_a_id, faction_b_id)
        if not force_refresh and cache_key in self.power_balance_cache:
            cached = self.power_balance_cache[cache_key]
            if datetime.utcnow() - cached.evaluated_at < self.cache_duration:
                return cached
        
        balance = PowerBalance(faction_a_id=faction_a_id, faction_b_id=faction_b_id)
        
        # Analyze each power category
        balance.military_balance = self._analyze_military_balance(faction_a_id, faction_b_id)
        balance.economic_balance = self._analyze_economic_balance(faction_a_id, faction_b_id)
        balance.diplomatic_balance = self._analyze_diplomatic_balance(faction_a_id, faction_b_id)
        balance.territorial_balance = self._analyze_territorial_balance(faction_a_id, faction_b_id)
        balance.technological_balance = self._analyze_technological_balance(faction_a_id, faction_b_id)
        balance.cultural_balance = self._analyze_cultural_balance(faction_a_id, faction_b_id)
        
        # Calculate overall balance (weighted average)
        weights = {
            'military': 0.25,
            'economic': 0.20,
            'diplomatic': 0.20,
            'territorial': 0.15,
            'technological': 0.10,
            'cultural': 0.10
        }
        
        balance.overall_balance = (
            balance.military_balance * weights['military'] +
            balance.economic_balance * weights['economic'] +
            balance.diplomatic_balance * weights['diplomatic'] +
            balance.territorial_balance * weights['territorial'] +
            balance.technological_balance * weights['technological'] +
            balance.cultural_balance * weights['cultural']
        )
        
        # Assess confidence based on data availability
        balance.confidence = self._calculate_confidence(faction_a_id, faction_b_id)
        
        # Analyze trends
        balance.balance_trend = self._analyze_power_trend(faction_a_id, faction_b_id)
        balance.projected_balance_6m = self._project_future_balance(balance)
        
        # Cache result
        self.power_balance_cache[cache_key] = balance
        
        logger.debug(f"Power balance between {faction_a_id} and {faction_b_id}: "
                    f"overall={balance.overall_balance:.2f}")
        
        return balance
    
    def _analyze_military_balance(self, faction_a_id: UUID, faction_b_id: UUID) -> float:
        """Analyze relative military power"""
        # Placeholder implementation
        # In a full system, this would analyze:
        # - Military unit counts and types
        # - Military technology levels
        # - Defensive positions and fortifications
        # - Military leadership quality
        # - Recent combat experience
        
        return 0.0  # Neutral balance placeholder
    
    def _analyze_economic_balance(self, faction_a_id: UUID, faction_b_id: UUID) -> float:
        """Analyze relative economic power"""
        # Placeholder implementation
        # Would analyze:
        # - GDP and economic output
        # - Resource control and production
        # - Trade network strength
        # - Economic growth rates
        # - Financial reserves
        
        return 0.0  # Neutral balance placeholder
    
    def _analyze_diplomatic_balance(self, faction_a_id: UUID, faction_b_id: UUID) -> float:
        """Analyze relative diplomatic power"""
        if not self.diplomacy_service:
            return 0.0
        
        try:
            # Count allies and assess alliance quality
            a_allies = self._count_faction_allies(faction_a_id)
            b_allies = self._count_faction_allies(faction_b_id)
            
            # Simple comparison (would be more sophisticated in full implementation)
            if a_allies == b_allies:
                return 0.0
            elif a_allies > b_allies:
                return min(0.5, (a_allies - b_allies) * 0.1)
            else:
                return max(-0.5, (a_allies - b_allies) * 0.1)
        
        except Exception as e:
            logger.warning(f"Error analyzing diplomatic balance: {e}")
            return 0.0
    
    def _count_faction_allies(self, faction_id: UUID) -> int:
        """Count number of allies for a faction"""
        try:
            treaties = self.diplomacy_service.list_treaties(faction_id=faction_id)
            allies = 0
            
            for treaty in treaties:
                if treaty.treaty_type.value == "ALLIANCE" and treaty.status == "active":
                    allies += len(treaty.parties) - 1  # Exclude self
            
            return allies
        except Exception:
            return 0
    
    def _analyze_territorial_balance(self, faction_a_id: UUID, faction_b_id: UUID) -> float:
        """Analyze relative territorial control"""
        # Placeholder - would analyze:
        # - Territory size and quality
        # - Strategic positions
        # - Resource-rich areas
        # - Defensive terrain
        
        return 0.0
    
    def _analyze_technological_balance(self, faction_a_id: UUID, faction_b_id: UUID) -> float:
        """Analyze relative technological advancement"""
        # Placeholder - would analyze:
        # - Technology levels
        # - Research capabilities
        # - Innovation rates
        # - Access to advanced resources
        
        return 0.0
    
    def _analyze_cultural_balance(self, faction_a_id: UUID, faction_b_id: UUID) -> float:
        """Analyze relative cultural influence"""
        # Placeholder - would analyze:
        # - Cultural spread and influence
        # - Soft power projection
        # - Population loyalty
        # - Cultural appeal to others
        
        return 0.0
    
    def _calculate_confidence(self, faction_a_id: UUID, faction_b_id: UUID) -> float:
        """Calculate confidence in power balance assessment"""
        # Base confidence on data availability
        confidence = 0.5
        
        # Increase confidence if we have diplomatic data
        if self.diplomacy_service:
            confidence += 0.2
        
        # Increase confidence if we have economic data
        if self.economy_service:
            confidence += 0.2
        
        # Would increase based on intelligence gathering, recent interactions, etc.
        
        return min(1.0, confidence)
    
    def _analyze_power_trend(self, faction_a_id: UUID, faction_b_id: UUID) -> str:
        """Analyze if power balance is shifting"""
        # Placeholder - would analyze historical data to determine trends
        return "stable"
    
    def _project_future_balance(self, current_balance: PowerBalance) -> float:
        """Project power balance 6 months into the future"""
        # Simple projection based on current trend
        if current_balance.balance_trend == "improving":
            return min(1.0, current_balance.overall_balance + 0.1)
        elif current_balance.balance_trend == "deteriorating":
            return max(-1.0, current_balance.overall_balance - 0.1)
        else:
            return current_balance.overall_balance
    
    def identify_coalition_opportunities(
        self, 
        faction_id: UUID, 
        potential_partners: List[UUID],
        strategic_objective: str = "general"
    ) -> List[CoalitionOpportunity]:
        """Identify and analyze potential coalition opportunities"""
        
        opportunities = []
        
        # Import here to avoid circular imports
        from .relationship_evaluator import get_relationship_evaluator
        evaluator = get_relationship_evaluator(self.diplomacy_service, self.faction_service)
        
        # Analyze different coalition sizes and compositions
        from itertools import combinations
        
        for size in range(2, min(5, len(potential_partners) + 1)):
            for partner_combo in combinations(potential_partners, size):
                opportunity = self._analyze_coalition_composition(
                    faction_id, list(partner_combo), strategic_objective, evaluator
                )
                
                if opportunity.is_viable():
                    opportunities.append(opportunity)
        
        # Sort by net value
        opportunities.sort(key=lambda x: x.get_net_value(), reverse=True)
        
        return opportunities[:10]  # Return top 10 opportunities
    
    def _analyze_coalition_composition(
        self, 
        faction_id: UUID, 
        partners: List[UUID], 
        objective: str,
        evaluator
    ) -> CoalitionOpportunity:
        """Analyze a specific coalition composition"""
        
        opportunity = CoalitionOpportunity(
            primary_faction_id=faction_id,
            potential_partners=partners
        )
        
        # Assess combined power
        total_power = 1.0  # Base power for primary faction
        for partner_id in partners:
            # Simplified power assessment
            total_power += 0.8  # Each partner adds 0.8 power units
        
        opportunity.combined_power_score = min(5.0, total_power)
        
        # Assess synergy/friction
        synergy_score = 1.0
        friction_penalty = 0.0
        
        for partner_id in partners:
            analysis = evaluator.evaluate_relationship(faction_id, partner_id)
            
            # Trust improves synergy
            synergy_score += analysis.trust_score * 0.1
            
            # Threats create friction
            if analysis.threat_level.value >= 3:  # Moderate or higher threat
                friction_penalty += 0.2
        
        # Check partner compatibility
        for i, partner_a in enumerate(partners):
            for partner_b in partners[i+1:]:
                partner_analysis = evaluator.evaluate_relationship(partner_a, partner_b)
                if partner_analysis.threat_level.value >= 4:  # High threat
                    friction_penalty += 0.3
        
        opportunity.power_multiplier = max(0.5, synergy_score - friction_penalty)
        
        # Assess stability
        trust_scores = []
        for partner_id in partners:
            analysis = evaluator.evaluate_relationship(faction_id, partner_id)
            trust_scores.append(analysis.trust_score)
        
        if trust_scores:
            # Stability based on minimum trust and average trust
            min_trust = min(trust_scores)
            avg_trust = sum(trust_scores) / len(trust_scores)
            opportunity.stability_score = (min_trust * 0.6 + avg_trust * 0.4)
        
        # Assess formation difficulty
        difficulty = 0.2  # Base difficulty
        difficulty += len(partners) * 0.1  # Larger coalitions harder to form
        difficulty += max(0.0, 0.5 - min(trust_scores)) if trust_scores else 0.3
        opportunity.formation_difficulty = min(1.0, difficulty)
        
        # Set other parameters
        opportunity.maintenance_cost = len(partners) * 0.05  # Diplomatic overhead
        opportunity.betrayal_risk = max(0.0, 0.4 - min(trust_scores)) if trust_scores else 0.3
        opportunity.success_probability = min(0.9, opportunity.stability_score * opportunity.power_multiplier)
        
        return opportunity
    
    def assess_decision_risk(
        self, 
        decision_type: str, 
        faction_id: UUID, 
        target_faction_id: Optional[UUID] = None,
        decision_context: Dict[str, Any] = None
    ) -> RiskAssessment:
        """Perform comprehensive risk assessment for a strategic decision"""
        
        if decision_context is None:
            decision_context = {}
        
        assessment = RiskAssessment(
            decision_type=decision_type,
            faction_id=faction_id,
            target_faction_id=target_faction_id
        )
        
        # Analyze risks by category
        assessment.military_risk = self._assess_military_risk(
            decision_type, faction_id, target_faction_id, decision_context
        )
        assessment.economic_risk = self._assess_economic_risk(
            decision_type, faction_id, target_faction_id, decision_context
        )
        assessment.diplomatic_risk = self._assess_diplomatic_risk(
            decision_type, faction_id, target_faction_id, decision_context
        )
        assessment.reputation_risk = self._assess_reputation_risk(
            decision_type, faction_id, target_faction_id, decision_context
        )
        
        # Calculate overall risk
        risk_values = [
            assessment.military_risk.value,
            assessment.economic_risk.value,
            assessment.diplomatic_risk.value,
            assessment.reputation_risk.value
        ]
        
        avg_risk = sum(risk_values) / len(risk_values)
        max_risk = max(risk_values)
        
        # Overall risk is weighted average of average and maximum risk
        overall_risk_value = int(avg_risk * 0.7 + max_risk * 0.3)
        assessment.overall_risk = RiskLevel(max(1, min(5, overall_risk_value)))
        
        # Set probability assessments based on decision type and context
        assessment.success_probability = self._estimate_success_probability(
            decision_type, faction_id, target_faction_id, decision_context
        )
        
        assessment.catastrophic_failure_probability = max(0.05, (avg_risk - 2) * 0.1)
        assessment.acceptable_outcome_probability = min(0.95, assessment.success_probability + 0.2)
        
        # Set impact assessments
        assessment.success_impact = self._estimate_success_impact(decision_type, decision_context)
        assessment.failure_impact = self._estimate_failure_impact(decision_type, decision_context)
        
        # Calculate required risk tolerance
        assessment.risk_tolerance_required = avg_risk / 5.0
        
        # Generate risk factors and mitigation strategies
        assessment.risk_factors = self._identify_risk_factors(
            decision_type, faction_id, target_faction_id, decision_context
        )
        assessment.mitigation_strategies = self._suggest_mitigation_strategies(
            assessment.risk_factors, decision_type
        )
        
        return assessment
    
    def _assess_military_risk(
        self, 
        decision_type: str, 
        faction_id: UUID, 
        target_faction_id: Optional[UUID],
        context: Dict[str, Any]
    ) -> RiskLevel:
        """Assess military risks of a decision"""
        
        if decision_type in ["declare_war", "attack", "invade"]:
            return RiskLevel.HIGH
        elif decision_type in ["form_alliance", "military_support"]:
            return RiskLevel.MODERATE
        elif decision_type in ["trade_agreement", "diplomatic_mission"]:
            return RiskLevel.LOW
        else:
            return RiskLevel.MODERATE
    
    def _assess_economic_risk(
        self, 
        decision_type: str, 
        faction_id: UUID, 
        target_faction_id: Optional[UUID],
        context: Dict[str, Any]
    ) -> RiskLevel:
        """Assess economic risks of a decision"""
        
        if decision_type in ["trade_embargo", "economic_sanctions"]:
            return RiskLevel.HIGH
        elif decision_type in ["trade_agreement", "economic_alliance"]:
            return RiskLevel.MODERATE
        elif decision_type in ["military_alliance", "declare_war"]:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _assess_diplomatic_risk(
        self, 
        decision_type: str, 
        faction_id: UUID, 
        target_faction_id: Optional[UUID],
        context: Dict[str, Any]
    ) -> RiskLevel:
        """Assess diplomatic risks of a decision"""
        
        if decision_type in ["betray_ally", "break_treaty"]:
            return RiskLevel.EXTREME
        elif decision_type in ["declare_war", "aggressive_expansion"]:
            return RiskLevel.HIGH
        elif decision_type in ["form_alliance", "mediate_conflict"]:
            return RiskLevel.LOW
        else:
            return RiskLevel.MODERATE
    
    def _assess_reputation_risk(
        self, 
        decision_type: str, 
        faction_id: UUID, 
        target_faction_id: Optional[UUID],
        context: Dict[str, Any]
    ) -> RiskLevel:
        """Assess reputation risks of a decision"""
        
        if decision_type in ["betray_ally", "unprovoked_attack"]:
            return RiskLevel.EXTREME
        elif decision_type in ["break_treaty", "aggressive_expansion"]:
            return RiskLevel.HIGH
        elif decision_type in ["defensive_action", "honor_alliance"]:
            return RiskLevel.LOW
        else:
            return RiskLevel.MODERATE
    
    def _estimate_success_probability(
        self, 
        decision_type: str, 
        faction_id: UUID, 
        target_faction_id: Optional[UUID],
        context: Dict[str, Any]
    ) -> float:
        """Estimate probability of decision success"""
        
        base_probability = 0.5
        
        # Adjust based on decision type
        if decision_type in ["trade_agreement", "diplomatic_mission"]:
            base_probability = 0.7
        elif decision_type in ["form_alliance", "mediate_conflict"]:
            base_probability = 0.6
        elif decision_type in ["declare_war", "military_action"]:
            base_probability = 0.4
        
        # Adjust based on power balance if target is specified
        if target_faction_id:
            balance = self.analyze_power_balance(faction_id, target_faction_id)
            if balance.overall_balance > 0.3:  # Significant advantage
                base_probability += 0.2
            elif balance.overall_balance < -0.3:  # Significant disadvantage
                base_probability -= 0.2
        
        return max(0.1, min(0.9, base_probability))
    
    def _estimate_success_impact(self, decision_type: str, context: Dict[str, Any]) -> float:
        """Estimate positive impact if decision succeeds"""
        
        impact_map = {
            "form_alliance": 0.6,
            "trade_agreement": 0.4,
            "military_victory": 0.8,
            "diplomatic_resolution": 0.5,
            "territorial_expansion": 0.7,
            "economic_development": 0.5
        }
        
        return impact_map.get(decision_type, 0.4)
    
    def _estimate_failure_impact(self, decision_type: str, context: Dict[str, Any]) -> float:
        """Estimate negative impact if decision fails"""
        
        impact_map = {
            "declare_war": -0.8,
            "betray_ally": -0.9,
            "aggressive_expansion": -0.6,
            "trade_embargo": -0.4,
            "diplomatic_mission": -0.2
        }
        
        return impact_map.get(decision_type, -0.3)
    
    def _identify_risk_factors(
        self, 
        decision_type: str, 
        faction_id: UUID, 
        target_faction_id: Optional[UUID],
        context: Dict[str, Any]
    ) -> List[str]:
        """Identify specific risk factors for the decision"""
        
        factors = []
        
        # Common risk factors by decision type
        if decision_type in ["declare_war", "military_action"]:
            factors.extend([
                "Military casualties and losses",
                "Economic cost of warfare",
                "Potential for escalation",
                "Risk of coalition formation against us"
            ])
        
        if decision_type in ["form_alliance", "treaty_negotiation"]:
            factors.extend([
                "Partner reliability uncertainty",
                "Conflicting interests with partner",
                "Obligation to support partner in conflicts"
            ])
        
        if decision_type in ["trade_agreement", "economic_cooperation"]:
            factors.extend([
                "Economic dependency risk",
                "Market volatility exposure",
                "Potential for economic coercion"
            ])
        
        return factors
    
    def _suggest_mitigation_strategies(
        self, 
        risk_factors: List[str], 
        decision_type: str
    ) -> List[str]:
        """Suggest strategies to mitigate identified risks"""
        
        strategies = []
        
        # Generic mitigation strategies
        strategies.append("Conduct thorough intelligence gathering before proceeding")
        strategies.append("Establish clear exit strategies and contingency plans")
        strategies.append("Maintain diplomatic channels for de-escalation")
        
        # Specific strategies based on decision type
        if decision_type in ["declare_war", "military_action"]:
            strategies.extend([
                "Ensure military superiority before engagement",
                "Secure alliance support or neutrality agreements",
                "Prepare economic reserves for sustained conflict"
            ])
        
        if decision_type in ["form_alliance", "treaty_negotiation"]:
            strategies.extend([
                "Include clear terms and exit clauses",
                "Establish regular review and renegotiation schedules",
                "Maintain independent capabilities"
            ])
        
        return strategies
    
    def analyze_timing(
        self, 
        decision_type: str, 
        faction_id: UUID, 
        context: Dict[str, Any] = None
    ) -> TimingAnalysis:
        """Analyze optimal timing for a strategic decision"""
        
        if context is None:
            context = {}
        
        analysis = TimingAnalysis(
            decision_type=decision_type,
            faction_id=faction_id
        )
        
        # Assess internal readiness
        analysis.internal_readiness = self._assess_internal_readiness(
            faction_id, decision_type, context
        )
        
        # Assess external conditions
        analysis.external_conditions = self._assess_external_conditions(
            faction_id, decision_type, context
        )
        
        # Calculate overall timing score
        analysis.timing_score = (
            analysis.internal_readiness * 0.6 + 
            analysis.external_conditions * 0.4
        )
        
        # Determine timing factor
        if analysis.timing_score >= 0.8:
            analysis.current_timing = TimingFactor.OPTIMAL
        elif analysis.timing_score >= 0.6:
            analysis.current_timing = TimingFactor.ACCEPTABLE
        elif analysis.timing_score >= 0.4:
            analysis.current_timing = TimingFactor.POOR
        else:
            analysis.current_timing = TimingFactor.CRITICAL_DELAY
        
        # Set opportunity decay based on decision type
        decay_rates = {
            "military_action": 0.3,      # Military opportunities fade quickly
            "diplomatic_mission": 0.1,   # Diplomatic opportunities more stable
            "trade_agreement": 0.05,     # Economic opportunities very stable
            "alliance_formation": 0.2    # Alliance opportunities moderately stable
        }
        analysis.opportunity_decay = decay_rates.get(decision_type, 0.15)
        
        # Generate timing factors
        analysis.timing_factors = self._identify_timing_factors(
            faction_id, decision_type, context
        )
        
        return analysis
    
    def _assess_internal_readiness(
        self, 
        faction_id: UUID, 
        decision_type: str, 
        context: Dict[str, Any]
    ) -> float:
        """Assess faction's internal readiness for the decision"""
        
        # Base readiness
        readiness = 0.5
        
        # Would assess:
        # - Military preparedness for military decisions
        # - Economic resources for economic decisions
        # - Diplomatic capacity for diplomatic decisions
        # - Leadership stability
        # - Popular support
        
        return readiness
    
    def _assess_external_conditions(
        self, 
        faction_id: UUID, 
        decision_type: str, 
        context: Dict[str, Any]
    ) -> float:
        """Assess external conditions for the decision"""
        
        # Base conditions
        conditions = 0.5
        
        # Would assess:
        # - Regional stability
        # - Other factions' current focus
        # - Economic climate
        # - Seasonal factors
        # - Ongoing conflicts elsewhere
        
        return conditions
    
    def _identify_timing_factors(
        self, 
        faction_id: UUID, 
        decision_type: str, 
        context: Dict[str, Any]
    ) -> List[str]:
        """Identify factors affecting timing of the decision"""
        
        factors = []
        
        # Common timing factors
        factors.append("Current diplomatic climate")
        factors.append("Faction internal stability")
        factors.append("Regional power balance")
        
        # Decision-specific factors
        if decision_type in ["military_action", "declare_war"]:
            factors.extend([
                "Military readiness and positioning",
                "Seasonal campaign considerations",
                "Enemy preparedness and alertness"
            ])
        
        if decision_type in ["alliance_formation", "treaty_negotiation"]:
            factors.extend([
                "Partner faction's current priorities",
                "Competing diplomatic initiatives",
                "Regional threat environment"
            ])
        
        return factors

# Global analyzer instance
_strategic_analyzer = None

def get_strategic_analyzer(
    diplomacy_service=None, 
    faction_service=None, 
    economy_service=None
) -> StrategicAnalyzer:
    """Get the global strategic analyzer instance"""
    global _strategic_analyzer
    if _strategic_analyzer is None:
        _strategic_analyzer = StrategicAnalyzer(diplomacy_service, faction_service, economy_service)
    return _strategic_analyzer 