"""
Diplomatic Decision Engine

This module implements decision tree algorithms for autonomous diplomatic decision-making.
It integrates with the goal system, relationship evaluator, and strategic analyzer to make
intelligent decisions about treaty proposals, alliance formation, conflict initiation, and mediation.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID
import logging
import random

from .goal_system import (
    DiplomaticGoalType, FactionGoal, GoalPriority, FactionGoalManager, get_goal_manager
)
from .relationship_evaluator import (
    RelationshipAnalysis, ThreatLevel, OpportunityType, TrustLevel, RelationshipEvaluator, get_relationship_evaluator
)
from .strategic_analyzer import (
    PowerBalance, CoalitionOpportunity, RiskAssessment, RiskLevel, TimingAnalysis, TimingFactor, StrategicAnalyzer, get_strategic_analyzer
)
from .personality_integration import PersonalityIntegrator, get_personality_integrator

from ..models.core_models import TreatyType, DiplomaticStatus, DiplomaticIncidentType, SanctionType
from ..services.core_services import DiplomacyService, TensionService

logger = logging.getLogger(__name__)

class DiplomaticDecisionType(Enum):
    """Types of diplomatic decisions the AI can make"""
    
    TREATY_PROPOSAL = "treaty_proposal"
    ALLIANCE_FORMATION = "alliance_formation"
    CONFLICT_INITIATION = "conflict_initiation"
    MEDIATION_ATTEMPT = "mediation_attempt"
    SANCTION_PROPOSAL = "sanction_proposal"
    ULTIMATUM_ISSUANCE = "ultimatum_issuance"
    TRADE_AGREEMENT = "trade_agreement"
    NON_AGGRESSION_PACT = "non_aggression_pact"

@dataclass
class DecisionContext:
    """Context information for making diplomatic decisions"""
    
    faction_id: UUID
    target_faction_id: Optional[UUID] = None
    third_party_faction_id: Optional[UUID] = None  # For mediation
    
    # Current state
    current_goals: List[FactionGoal] = field(default_factory=list)
    relationship_analysis: Optional[RelationshipAnalysis] = None
    power_balance: Optional[PowerBalance] = None
    risk_assessment: Optional[RiskAssessment] = None
    timing_analysis: Optional[TimingAnalysis] = None
    
    # External factors
    recent_events: List[Dict[str, Any]] = field(default_factory=list)
    active_conflicts: List[UUID] = field(default_factory=list)
    existing_treaties: List[Dict[str, Any]] = field(default_factory=list)
    
    # Decision parameters
    urgency_level: float = 0.5  # 0.0 to 1.0
    confidence_threshold: float = 0.6
    risk_tolerance: float = 0.5

@dataclass
class DecisionOutcome:
    """Result of a diplomatic decision evaluation"""
    
    decision_type: DiplomaticDecisionType
    recommended: bool
    confidence: float = 0.0
    priority: float = 0.0
    
    # Decision details
    proposal_details: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""
    risk_factors: List[str] = field(default_factory=list)
    success_probability: float = 0.0
    
    # Reasoning
    reasoning: List[str] = field(default_factory=list)
    supporting_factors: List[str] = field(default_factory=list)
    opposing_factors: List[str] = field(default_factory=list)
    
    # Timing
    suggested_timing: TimingFactor = TimingFactor.ACCEPTABLE
    deadline: Optional[datetime] = None

@dataclass
class DecisionOption:
    """Represents a possible diplomatic decision option"""
    
    decision_type: DiplomaticDecisionType
    target_faction_id: UUID
    priority: float = 0.0
    confidence: float = 0.0
    estimated_cost: float = 0.0
    estimated_benefit: float = 0.0
    risk_level: str = "MODERATE"
    reasoning: str = ""
    
    def __post_init__(self):
        """Validate the decision option"""
        if not (0.0 <= self.priority <= 1.0):
            raise ValueError("Priority must be between 0.0 and 1.0")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")

@dataclass
class DecisionResult:
    """Result of executing a diplomatic decision"""
    
    decision_type: DiplomaticDecisionType
    faction_id: UUID
    target_faction_id: UUID
    success: bool
    outcome_description: str = ""
    actual_cost: float = 0.0
    actual_benefit: float = 0.0
    unexpected_consequences: List[str] = field(default_factory=list)
    execution_time: datetime = field(default_factory=datetime.now)
    
    # Learning data
    predicted_success_probability: float = 0.0
    actual_success: bool = False
    learning_feedback: Dict[str, Any] = field(default_factory=dict)

class DiplomaticDecisionEngine:
    """Main engine for making diplomatic decisions using decision trees"""
    
    def __init__(self, 
                 diplomacy_service: Optional[DiplomacyService] = None,
                 faction_service = None,
                 economy_service = None):
        """Initialize with required services"""
        self.diplomacy_service = diplomacy_service or DiplomacyService()
        self.faction_service = faction_service
        self.economy_service = economy_service
        
        # AI components
        self.goal_manager = get_goal_manager()
        self.relationship_evaluator = get_relationship_evaluator(diplomacy_service, faction_service)
        self.strategic_analyzer = get_strategic_analyzer(diplomacy_service, faction_service, economy_service)
        self.personality_integrator = get_personality_integrator()
        
        # Decision configuration
        self.min_confidence_threshold = 0.5
        self.max_risk_tolerance = 0.8
        self.decision_cooldown = timedelta(hours=6)  # Minimum time between similar decisions
        
        # Decision history for learning
        self.decision_history: Dict[UUID, List[Dict[str, Any]]] = {}
    
    def evaluate_all_decisions(self, faction_id: UUID) -> List[DecisionOutcome]:
        """Evaluate all possible diplomatic decisions for a faction"""
        context = self._build_decision_context(faction_id)
        decisions = []
        
        # Get all potential targets
        potential_targets = self._get_potential_targets(faction_id)
        
        for target_id in potential_targets:
            context.target_faction_id = target_id
            context.relationship_analysis = self.relationship_evaluator.evaluate_relationship(faction_id, target_id)
            context.power_balance = self.strategic_analyzer.analyze_power_balance(faction_id, target_id)
            
            # Evaluate each decision type
            decisions.append(self.evaluate_treaty_proposal(context))
            decisions.append(self.evaluate_alliance_formation(context))
            decisions.append(self.evaluate_conflict_initiation(context))
            
        # Evaluate mediation opportunities (requires two other factions)
        mediation_opportunities = self._identify_mediation_opportunities(faction_id)
        for mediator_context in mediation_opportunities:
            decisions.append(self.evaluate_mediation_attempt(mediator_context))
        
        # Filter and rank decisions
        recommended_decisions = [d for d in decisions if d.recommended and d.confidence >= self.min_confidence_threshold]
        recommended_decisions.sort(key=lambda x: (x.priority, x.confidence), reverse=True)
        
        return recommended_decisions
    
    def evaluate_treaty_proposal(self, context: DecisionContext) -> DecisionOutcome:
        """Decision tree for treaty proposals"""
        outcome = DecisionOutcome(
            decision_type=DiplomaticDecisionType.TREATY_PROPOSAL,
            recommended=False
        )
        
        if not context.target_faction_id or not context.relationship_analysis:
            return outcome
        
        rel = context.relationship_analysis
        
        # Decision tree logic
        reasoning = []
        supporting_factors = []
        opposing_factors = []
        
        # 1. Check if we should propose a treaty at all
        if rel.trust_level.value < TrustLevel.NEUTRAL.value:
            opposing_factors.append("Insufficient trust for meaningful treaty")
            outcome.confidence = 0.2
            outcome.reasoning = ["Trust level too low for treaty negotiation"]
            return outcome
        
        # 2. Determine treaty type based on goals and relationship
        dominant_goals = self.goal_manager.get_dominant_goals(context.faction_id, limit=3)
        treaty_type = self._determine_optimal_treaty_type(context, dominant_goals)
        
        if not treaty_type:
            opposing_factors.append("No suitable treaty type identified")
            outcome.confidence = 0.3
            outcome.reasoning = ["No beneficial treaty type available"]
            return outcome
        
        # 3. Check existing treaties to avoid duplication
        if self._has_similar_treaty(context.faction_id, context.target_faction_id, treaty_type):
            opposing_factors.append("Similar treaty already exists")
            outcome.confidence = 0.1
            outcome.reasoning = ["Similar treaty relationship already established"]
            return outcome
        
        # 4. Evaluate strategic benefit
        strategic_benefit = self._calculate_treaty_benefit(context, treaty_type)
        if strategic_benefit < 0.4:
            opposing_factors.append("Limited strategic benefit")
            outcome.confidence = 0.3
            outcome.reasoning = ["Insufficient strategic value"]
            return outcome
        
        supporting_factors.append(f"High strategic benefit ({strategic_benefit:.2f})")
        
        # 5. Risk assessment
        risk_assessment = self.strategic_analyzer.assess_decision_risk(
            "treaty_proposal", context.faction_id, context.target_faction_id,
            {"treaty_type": treaty_type}
        )
        
        if risk_assessment.overall_risk.value > RiskLevel.MODERATE.value:
            opposing_factors.append(f"High risk ({risk_assessment.overall_risk.name})")
            if risk_assessment.overall_risk.value >= RiskLevel.HIGH.value:
                outcome.confidence = 0.2
                outcome.reasoning = ["Risk level too high for treaty proposal"]
                return outcome
        
        # 6. Timing evaluation
        timing = self.strategic_analyzer.analyze_timing("treaty_proposal", context.faction_id)
        if timing.current_timing in [TimingFactor.POOR, TimingFactor.CRITICAL_DELAY]:
            opposing_factors.append("Poor timing conditions")
            outcome.confidence = 0.4
            outcome.reasoning = ["Current timing not favorable"]
            return outcome
        
        supporting_factors.append(f"Good timing ({timing.current_timing.value})")
        
        # 7. Personality integration
        personality_modifier = self.personality_integrator.calculate_decision_modifier(
            context.faction_id, "treaty_proposal", context
        )
        
        # 8. Calculate final recommendation
        base_score = strategic_benefit * 0.4 + rel.trust_score * 0.3 + timing.timing_score * 0.3
        final_score = base_score * personality_modifier
        
        if final_score >= 0.6:
            outcome.recommended = True
            outcome.confidence = min(0.95, final_score)
            outcome.priority = self._calculate_decision_priority(context, dominant_goals)
            
            # Generate proposal details
            outcome.proposal_details = self._generate_treaty_proposal_details(context, treaty_type)
            outcome.expected_outcome = f"Successful {treaty_type.value} treaty"
            outcome.success_probability = self._estimate_treaty_success_probability(context, treaty_type)
            
            reasoning.append(f"High overall benefit score ({final_score:.2f})")
            reasoning.append(f"Recommended treaty type: {treaty_type.value}")
        else:
            opposing_factors.append(f"Low overall score ({final_score:.2f})")
        
        outcome.reasoning = reasoning
        outcome.supporting_factors = supporting_factors
        outcome.opposing_factors = opposing_factors
        outcome.risk_factors = risk_assessment.risk_factors
        outcome.suggested_timing = timing.current_timing
        
        return outcome
    
    def evaluate_alliance_formation(self, context: DecisionContext) -> DecisionOutcome:
        """Decision tree for alliance formation"""
        outcome = DecisionOutcome(
            decision_type=DiplomaticDecisionType.ALLIANCE_FORMATION,
            recommended=False
        )
        
        if not context.target_faction_id or not context.relationship_analysis:
            return outcome
        
        rel = context.relationship_analysis
        reasoning = []
        supporting_factors = []
        opposing_factors = []
        
        # 1. Check if alliance is viable based on trust
        if rel.trust_level.value < TrustLevel.CORDIAL.value:
            opposing_factors.append("Insufficient trust for alliance")
            outcome.confidence = 0.2
            outcome.reasoning = ["Trust level too low for alliance formation"]
            return outcome
        
        supporting_factors.append(f"Adequate trust level ({rel.trust_level.name})")
        
        # 2. Check for existing alliance
        if self.diplomacy_service.are_allied(context.faction_id, context.target_faction_id):
            opposing_factors.append("Already allied")
            outcome.confidence = 0.1
            outcome.reasoning = ["Alliance already exists"]
            return outcome
        
        # 3. Evaluate mutual threat assessment
        mutual_threats = self._identify_mutual_threats(context.faction_id, context.target_faction_id)
        if len(mutual_threats) == 0:
            opposing_factors.append("No mutual threats identified")
            outcome.confidence = 0.3
            outcome.reasoning = ["Insufficient mutual security interests"]
            return outcome
        
        supporting_factors.append(f"Mutual threats identified: {len(mutual_threats)}")
        
        # 4. Check goal alignment
        goal_alignment = self._assess_goal_alignment(context.faction_id, context.target_faction_id)
        if goal_alignment < 0.5:
            opposing_factors.append("Poor goal alignment")
            outcome.confidence = 0.3
            outcome.reasoning = ["Insufficient strategic goal alignment"]
            return outcome
        
        supporting_factors.append(f"Good goal alignment ({goal_alignment:.2f})")
        
        # 5. Power balance consideration
        if context.power_balance and abs(context.power_balance.overall_balance) > 0.7:
            opposing_factors.append("Extreme power imbalance")
            # Very strong or very weak partners can be problematic
            outcome.confidence = 0.4
        else:
            supporting_factors.append("Reasonable power balance")
        
        # 6. Coalition opportunity analysis
        coalition_opportunities = self.strategic_analyzer.identify_coalition_opportunities(
            context.faction_id, [context.target_faction_id], "security"
        )
        
        if not coalition_opportunities or not coalition_opportunities[0].is_viable():
            opposing_factors.append("Alliance not strategically viable")
            outcome.confidence = 0.3
            outcome.reasoning = ["Strategic analysis shows low alliance viability"]
            return outcome
        
        coalition = coalition_opportunities[0]
        supporting_factors.append(f"High coalition value ({coalition.get_net_value():.2f})")
        
        # 7. Risk assessment
        risk_assessment = self.strategic_analyzer.assess_decision_risk(
            "alliance_formation", context.faction_id, context.target_faction_id
        )
        
        if risk_assessment.overall_risk.value > RiskLevel.MODERATE.value:
            opposing_factors.append(f"High risk ({risk_assessment.overall_risk.name})")
        
        # 8. Personality integration
        personality_modifier = self.personality_integrator.calculate_decision_modifier(
            context.faction_id, "alliance_formation", context
        )
        
        # 9. Calculate final recommendation
        base_score = (goal_alignment * 0.3 + rel.trust_score * 0.3 + 
                     coalition.get_net_value() * 0.4)
        final_score = base_score * personality_modifier
        
        if final_score >= 0.65:
            outcome.recommended = True
            outcome.confidence = min(0.95, final_score)
            outcome.priority = self._calculate_decision_priority(context, context.current_goals)
            
            outcome.proposal_details = self._generate_alliance_proposal_details(context, coalition)
            outcome.expected_outcome = "Successful military/diplomatic alliance"
            outcome.success_probability = self._estimate_alliance_success_probability(context)
            
            reasoning.append(f"High alliance viability score ({final_score:.2f})")
            reasoning.append(f"Mutual security interests identified")
        else:
            opposing_factors.append(f"Low viability score ({final_score:.2f})")
        
        outcome.reasoning = reasoning
        outcome.supporting_factors = supporting_factors
        outcome.opposing_factors = opposing_factors
        outcome.risk_factors = risk_assessment.risk_factors
        
        return outcome
    
    def evaluate_conflict_initiation(self, context: DecisionContext) -> DecisionOutcome:
        """Decision tree for conflict initiation"""
        outcome = DecisionOutcome(
            decision_type=DiplomaticDecisionType.CONFLICT_INITIATION,
            recommended=False
        )
        
        if not context.target_faction_id or not context.relationship_analysis:
            return outcome
        
        rel = context.relationship_analysis
        reasoning = []
        supporting_factors = []
        opposing_factors = []
        
        # 1. Check if we're already at war
        if self.diplomacy_service.are_at_war(context.faction_id, context.target_faction_id):
            opposing_factors.append("Already at war")
            outcome.confidence = 0.1
            outcome.reasoning = ["Conflict already exists"]
            return outcome
        
        # 2. Check threat level - need significant threat or opportunity
        if rel.threat_level.value < ThreatLevel.MODERATE.value:
            # Check if this is an expansion opportunity instead
            expansion_goals = [g for g in context.current_goals 
                             if g.goal_type == DiplomaticGoalType.EXPANSION]
            
            if not expansion_goals:
                opposing_factors.append("No significant threat or expansion goal")
                outcome.confidence = 0.2
                outcome.reasoning = ["Insufficient justification for conflict"]
                return outcome
            
            supporting_factors.append("Expansion opportunity identified")
        else:
            supporting_factors.append(f"Significant threat detected ({rel.threat_level.name})")
        
        # 3. Power balance assessment - need reasonable chance of success
        if context.power_balance and context.power_balance.overall_balance < -0.3:
            opposing_factors.append("Unfavorable power balance")
            outcome.confidence = 0.3
            outcome.reasoning = ["Military disadvantage too significant"]
            return outcome
        
        if context.power_balance and context.power_balance.overall_balance > 0.2:
            supporting_factors.append(f"Favorable power balance ({context.power_balance.overall_balance:.2f})")
        
        # 4. Check for allies and coalition support
        ally_support = self._assess_conflict_ally_support(context.faction_id, context.target_faction_id)
        if ally_support < 0.3:
            opposing_factors.append("Insufficient ally support")
            outcome.confidence = 0.4
        else:
            supporting_factors.append(f"Good ally support ({ally_support:.2f})")
        
        # 5. Economic readiness
        economic_readiness = self._assess_economic_war_readiness(context.faction_id)
        if economic_readiness < 0.4:
            opposing_factors.append("Poor economic readiness for war")
            outcome.confidence = 0.3
            outcome.reasoning = ["Insufficient economic resources for sustained conflict"]
            return outcome
        
        supporting_factors.append(f"Adequate economic readiness ({economic_readiness:.2f})")
        
        # 6. Check for justification (incidents, treaty violations, etc.)
        justification_score = self._assess_conflict_justification(context.faction_id, context.target_faction_id)
        if justification_score < 0.3:
            opposing_factors.append("Weak justification for conflict")
            outcome.confidence = 0.4
        else:
            supporting_factors.append(f"Good casus belli ({justification_score:.2f})")
        
        # 7. Risk assessment - conflict is inherently high risk
        risk_assessment = self.strategic_analyzer.assess_decision_risk(
            "conflict_initiation", context.faction_id, context.target_faction_id
        )
        
        if risk_assessment.overall_risk.value >= RiskLevel.EXTREME.value:
            opposing_factors.append("Extreme risk level")
            outcome.confidence = 0.1
            outcome.reasoning = ["Risk level unacceptably high"]
            return outcome
        
        # 8. Personality integration - some factions are more aggressive
        personality_modifier = self.personality_integrator.calculate_decision_modifier(
            context.faction_id, "conflict_initiation", context
        )
        
        # 9. Calculate final recommendation (higher threshold for conflict)
        base_factors = [
            context.power_balance.overall_balance + 0.3 if context.power_balance else 0.3,
            ally_support,
            economic_readiness,
            justification_score,
            min(0.8, 1.0 - (risk_assessment.overall_risk.value - 1) * 0.2)  # Risk penalty
        ]
        
        base_score = sum(base_factors) / len(base_factors)
        final_score = base_score * personality_modifier
        
        # Conflict requires high confidence due to consequences
        if final_score >= 0.75 and personality_modifier >= 0.8:
            outcome.recommended = True
            outcome.confidence = min(0.9, final_score)
            outcome.priority = self._calculate_decision_priority(context, context.current_goals) * 1.2
            
            outcome.proposal_details = self._generate_conflict_proposal_details(context)
            outcome.expected_outcome = "Successful military campaign"
            outcome.success_probability = self._estimate_conflict_success_probability(context)
            
            reasoning.append(f"High conflict viability score ({final_score:.2f})")
            reasoning.append("Strong justification and favorable conditions")
        else:
            opposing_factors.append(f"Insufficient overall score ({final_score:.2f})")
        
        outcome.reasoning = reasoning
        outcome.supporting_factors = supporting_factors
        outcome.opposing_factors = opposing_factors
        outcome.risk_factors = risk_assessment.risk_factors
        
        return outcome
    
    def evaluate_mediation_attempt(self, context: DecisionContext) -> DecisionOutcome:
        """Decision tree for mediation attempts"""
        outcome = DecisionOutcome(
            decision_type=DiplomaticDecisionType.MEDIATION_ATTEMPT,
            recommended=False
        )
        
        if not context.target_faction_id or not context.third_party_faction_id:
            return outcome
        
        reasoning = []
        supporting_factors = []
        opposing_factors = []
        
        # 1. Check if there's an actual conflict to mediate
        conflict_exists = (
            self.diplomacy_service.are_at_war(context.target_faction_id, context.third_party_faction_id) or
            self._has_high_tension(context.target_faction_id, context.third_party_faction_id)
        )
        
        if not conflict_exists:
            opposing_factors.append("No significant conflict to mediate")
            outcome.confidence = 0.1
            outcome.reasoning = ["No conflict requiring mediation"]
            return outcome
        
        supporting_factors.append("Active conflict identified")
        
        # 2. Check mediator's relationship with both parties
        rel_a = self.relationship_evaluator.evaluate_relationship(context.faction_id, context.target_faction_id)
        rel_b = self.relationship_evaluator.evaluate_relationship(context.faction_id, context.third_party_faction_id)
        
        if (rel_a.trust_level.value < TrustLevel.NEUTRAL.value or 
            rel_b.trust_level.value < TrustLevel.NEUTRAL.value):
            opposing_factors.append("Insufficient trust with one or both parties")
            outcome.confidence = 0.3
            outcome.reasoning = ["Mediator lacks trust with conflicting parties"]
            return outcome
        
        supporting_factors.append("Adequate trust with both parties")
        
        # 3. Check neutrality - mediator shouldn't be allied with only one side
        allied_a = self.diplomacy_service.are_allied(context.faction_id, context.target_faction_id)
        allied_b = self.diplomacy_service.are_allied(context.faction_id, context.third_party_faction_id)
        
        if allied_a and not allied_b:
            opposing_factors.append("Biased toward one party (allied)")
            outcome.confidence = 0.2
        elif allied_b and not allied_a:
            opposing_factors.append("Biased toward one party (allied)")
            outcome.confidence = 0.2
        else:
            supporting_factors.append("Neutral position maintained")
        
        # 4. Assess mediation capacity and reputation
        mediation_capacity = self._assess_mediation_capacity(context.faction_id)
        if mediation_capacity < 0.4:
            opposing_factors.append("Low diplomatic capacity for mediation")
            outcome.confidence = 0.3
            outcome.reasoning = ["Insufficient diplomatic capability"]
            return outcome
        
        supporting_factors.append(f"Good mediation capacity ({mediation_capacity:.2f})")
        
        # 5. Check strategic interest in resolution
        strategic_interest = self._assess_mediation_strategic_interest(context)
        if strategic_interest < 0.3:
            opposing_factors.append("Low strategic interest in resolution")
            outcome.confidence = 0.4
        else:
            supporting_factors.append(f"Strong strategic interest ({strategic_interest:.2f})")
        
        # 6. Assess success probability
        success_factors = [
            min(rel_a.trust_score, rel_b.trust_score),  # Trust with both parties
            mediation_capacity,
            strategic_interest,
            1.0 - min(0.8, abs(rel_a.power_balance) * 0.5)  # Penalty for large power imbalance
        ]
        
        success_probability = sum(success_factors) / len(success_factors)
        
        if success_probability < 0.5:
            opposing_factors.append(f"Low success probability ({success_probability:.2f})")
            outcome.confidence = 0.4
            outcome.reasoning = ["Low likelihood of successful mediation"]
            return outcome
        
        # 7. Personality integration
        personality_modifier = self.personality_integrator.calculate_decision_modifier(
            context.faction_id, "mediation_attempt", context
        )
        
        # 8. Calculate final recommendation
        base_score = success_probability * strategic_interest
        final_score = base_score * personality_modifier
        
        if final_score >= 0.6:
            outcome.recommended = True
            outcome.confidence = min(0.9, final_score)
            outcome.priority = self._calculate_decision_priority(context, context.current_goals) * 0.8  # Lower priority than direct actions
            
            outcome.proposal_details = self._generate_mediation_proposal_details(context)
            outcome.expected_outcome = "Successful conflict resolution"
            outcome.success_probability = success_probability
            
            reasoning.append(f"High mediation viability score ({final_score:.2f})")
            reasoning.append("Good position to facilitate resolution")
        else:
            opposing_factors.append(f"Low viability score ({final_score:.2f})")
        
        outcome.reasoning = reasoning
        outcome.supporting_factors = supporting_factors
        outcome.opposing_factors = opposing_factors
        
        return outcome
    
    # Helper methods for decision logic
    
    def _build_decision_context(self, faction_id: UUID) -> DecisionContext:
        """Build decision context for a faction"""
        context = DecisionContext(faction_id=faction_id)
        
        # Get current goals
        context.current_goals = self.goal_manager.get_faction_goals(faction_id)
        
        # Get recent events and existing treaties
        context.existing_treaties = self.diplomacy_service.list_treaties(faction_id, active_only=True)
        
        # Set decision parameters based on faction personality
        faction_attributes = self.personality_integrator.get_faction_attributes(faction_id)
        if faction_attributes:
            context.risk_tolerance = faction_attributes.get('pragmatism', 50) / 100.0
            context.urgency_level = faction_attributes.get('ambition', 50) / 100.0
        
        return context
    
    def _get_potential_targets(self, faction_id: UUID) -> List[UUID]:
        """Get list of potential target factions for diplomatic actions"""
        # This would query the faction service for all other factions
        # For now, return empty list - needs faction service integration
        return []
    
    def _identify_mediation_opportunities(self, faction_id: UUID) -> List[DecisionContext]:
        """Identify mediation opportunities between other factions"""
        opportunities = []
        
        # Find pairs of factions in conflict where we could mediate
        # This would require querying current conflicts and tensions
        # For now, return empty list - needs conflict tracking integration
        
        return opportunities
    
    def _determine_optimal_treaty_type(self, context: DecisionContext, goals: List[FactionGoal]) -> Optional[TreatyType]:
        """Determine the best treaty type based on goals and relationship"""
        if not goals:
            return None
        
        # Analyze dominant goals to suggest treaty type
        goal_types = [g.goal_type for g in goals]
        
        if DiplomaticGoalType.SECURITY in goal_types:
            return TreatyType.NON_AGGRESSION
        elif DiplomaticGoalType.PROSPERITY in goal_types:
            return TreatyType.TRADE
        elif DiplomaticGoalType.ALLIANCE_BUILDING in goal_types:
            return TreatyType.ALLIANCE
        else:
            return TreatyType.NON_AGGRESSION  # Default safe option
    
    def _has_similar_treaty(self, faction_a_id: UUID, faction_b_id: UUID, treaty_type: TreatyType) -> bool:
        """Check if similar treaty already exists"""
        return self.diplomacy_service.has_treaty_of_type(faction_a_id, faction_b_id, treaty_type)
    
    def _calculate_treaty_benefit(self, context: DecisionContext, treaty_type: TreatyType) -> float:
        """Calculate strategic benefit of proposed treaty"""
        # Base benefit calculation
        base_benefit = 0.5
        
        # Adjust based on relationship opportunity score
        if context.relationship_analysis:
            base_benefit += context.relationship_analysis.opportunity_score * 0.3
        
        # Adjust based on goal alignment
        goal_alignment = self._assess_goal_alignment(context.faction_id, context.target_faction_id)
        base_benefit += goal_alignment * 0.2
        
        return min(1.0, base_benefit)
    
    def _calculate_decision_priority(self, context: DecisionContext, goals: List[FactionGoal]) -> float:
        """Calculate priority score for a decision"""
        if not goals:
            return 0.5
        
        # Weight by goal priorities and urgency
        total_weight = 0.0
        total_priority = 0.0
        
        for goal in goals:
            weight = goal.priority.value / 100.0
            urgency = goal.calculate_urgency()
            priority = weight * urgency
            
            total_weight += weight
            total_priority += priority
        
        return total_priority / max(1.0, total_weight) if total_weight > 0 else 0.5
    
    def _identify_mutual_threats(self, faction_a_id: UUID, faction_b_id: UUID) -> List[UUID]:
        """Identify factions that threaten both factions"""
        # This would analyze threat assessments for both factions
        # and find common threats
        return []
    
    def _assess_goal_alignment(self, faction_a_id: UUID, faction_b_id: UUID) -> float:
        """Assess how well faction goals align"""
        goals_a = self.goal_manager.get_faction_goals(faction_a_id)
        goals_b = self.goal_manager.get_faction_goals(faction_b_id)
        
        if not goals_a or not goals_b:
            return 0.5
        
        # Simple alignment based on goal type overlap
        types_a = set(g.goal_type for g in goals_a)
        types_b = set(g.goal_type for g in goals_b)
        
        overlap = len(types_a.intersection(types_b))
        total = len(types_a.union(types_b))
        
        return overlap / max(1, total)
    
    def _assess_conflict_ally_support(self, faction_id: UUID, target_faction_id: UUID) -> float:
        """Assess level of ally support for potential conflict"""
        # Analyze allies and their likelihood to support conflict
        return 0.5  # Placeholder
    
    def _assess_economic_war_readiness(self, faction_id: UUID) -> float:
        """Assess faction's economic readiness for war"""
        # This would check economic resources, trade routes, etc.
        return 0.5  # Placeholder
    
    def _assess_conflict_justification(self, faction_id: UUID, target_faction_id: UUID) -> float:
        """Assess justification for conflict (incidents, violations, etc.)"""
        # Check for recent incidents, treaty violations, etc.
        return 0.5  # Placeholder
    
    def _has_high_tension(self, faction_a_id: UUID, faction_b_id: UUID) -> bool:
        """Check if factions have high tension"""
        relationship = self.diplomacy_service.get_faction_relationship(faction_a_id, faction_b_id)
        return relationship.get('tension', 0) > 60
    
    def _assess_mediation_capacity(self, faction_id: UUID) -> float:
        """Assess faction's capacity for diplomatic mediation"""
        # This would check diplomatic skill, reputation, resources
        return 0.5  # Placeholder
    
    def _assess_mediation_strategic_interest(self, context: DecisionContext) -> float:
        """Assess strategic interest in mediating conflict"""
        # Analyze how resolution benefits the mediator
        return 0.5  # Placeholder
    
    # Proposal generation methods
    
    def _generate_treaty_proposal_details(self, context: DecisionContext, treaty_type: TreatyType) -> Dict[str, Any]:
        """Generate specific details for treaty proposal"""
        return {
            "treaty_type": treaty_type.value,
            "proposed_terms": self._generate_treaty_terms(context, treaty_type),
            "duration": "5 years",  # Default duration
            "renewal_clause": True,
            "negotiation_deadline": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    
    def _generate_alliance_proposal_details(self, context: DecisionContext, coalition: CoalitionOpportunity) -> Dict[str, Any]:
        """Generate specific details for alliance proposal"""
        return {
            "alliance_type": "military_diplomatic",
            "mutual_defense": True,
            "information_sharing": True,
            "coordinated_diplomacy": True,
            "trade_preferences": True,
            "objectives": coalition.strategic_objectives,
            "duration": "indefinite",
            "review_period": "2 years"
        }
    
    def _generate_conflict_proposal_details(self, context: DecisionContext) -> Dict[str, Any]:
        """Generate specific details for conflict initiation"""
        return {
            "casus_belli": "Territorial dispute",  # Would be determined by analysis
            "objectives": ["Territory control", "Resource access"],
            "escalation_limits": "Limited war",
            "civilian_protection": True,
            "estimated_duration": "3-6 months"
        }
    
    def _generate_mediation_proposal_details(self, context: DecisionContext) -> Dict[str, Any]:
        """Generate specific details for mediation attempt"""
        return {
            "mediation_type": "neutral_arbitration",
            "venue": "neutral_territory",
            "scope": "full_conflict_resolution",
            "timeline": "30 days",
            "binding_arbitration": False,
            "guarantees": ["Ceasefire during negotiations"]
        }
    
    def _generate_treaty_terms(self, context: DecisionContext, treaty_type: TreatyType) -> Dict[str, Any]:
        """Generate specific terms for treaty based on type"""
        if treaty_type == TreatyType.TRADE:
            return {
                "tariff_reduction": "25%",
                "trade_routes": "protected",
                "dispute_resolution": "arbitration",
                "currency_exchange": "favorable_rates"
            }
        elif treaty_type == TreatyType.NON_AGGRESSION:
            return {
                "military_non_aggression": True,
                "territorial_integrity": True,
                "third_party_conflicts": "neutral",
                "violation_penalties": "economic_sanctions"
            }
        elif treaty_type == TreatyType.ALLIANCE:
            return {
                "mutual_defense": True,
                "military_cooperation": True,
                "intelligence_sharing": True,
                "coordinated_foreign_policy": True
            }
        else:
            return {}
    
    # Success probability estimation methods
    
    def _estimate_treaty_success_probability(self, context: DecisionContext, treaty_type: TreatyType) -> float:
        """Estimate probability of successful treaty negotiation"""
        base_probability = 0.5
        
        if context.relationship_analysis:
            # Higher trust increases success probability
            base_probability += context.relationship_analysis.trust_score * 0.3
        
        # Adjust based on goal alignment
        goal_alignment = self._assess_goal_alignment(context.faction_id, context.target_faction_id)
        base_probability += goal_alignment * 0.2
        
        return min(0.95, base_probability)
    
    def _estimate_alliance_success_probability(self, context: DecisionContext) -> float:
        """Estimate probability of successful alliance formation"""
        base_probability = 0.4  # Lower base due to complexity
        
        if context.relationship_analysis:
            base_probability += context.relationship_analysis.trust_score * 0.3
        
        # Check for mutual threats
        mutual_threats = self._identify_mutual_threats(context.faction_id, context.target_faction_id)
        if mutual_threats:
            base_probability += 0.2
        
        return min(0.9, base_probability)
    
    def _estimate_conflict_success_probability(self, context: DecisionContext) -> float:
        """Estimate probability of successful conflict outcome"""
        base_probability = 0.3  # Low base due to war complexity
        
        if context.power_balance:
            # Power advantage increases success probability
            base_probability += max(0, context.power_balance.overall_balance) * 0.4
        
        # Ally support increases chances
        ally_support = self._assess_conflict_ally_support(context.faction_id, context.target_faction_id)
        base_probability += ally_support * 0.3
        
        return min(0.85, base_probability)


# Global instance management
_decision_engine_instance = None

def get_decision_engine(diplomacy_service=None, faction_service=None, economy_service=None) -> DiplomaticDecisionEngine:
    """Get or create the global decision engine instance"""
    global _decision_engine_instance
    if _decision_engine_instance is None:
        _decision_engine_instance = DiplomaticDecisionEngine(diplomacy_service, faction_service, economy_service)
    return _decision_engine_instance 