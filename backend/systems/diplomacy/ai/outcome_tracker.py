"""
Decision Outcome Tracker

This module tracks the outcomes of AI diplomatic decisions, analyzes their effectiveness,
and provides learning capabilities to improve future decision-making strategies.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import logging
import json
import statistics
from collections import defaultdict, deque

# Import our AI components
from .decision_engine import DecisionResult, DecisionOption, DecisionType
from .goal_system import DiplomaticGoalType

logger = logging.getLogger(__name__)

class OutcomeCategory(Enum):
    """Categories of decision outcomes"""
    
    SUCCESS = "success"                 # Decision achieved intended result
    PARTIAL_SUCCESS = "partial_success" # Some benefits but not full success
    FAILURE = "failure"                 # Decision failed to achieve goals
    BACKFIRE = "backfire"              # Decision had negative consequences
    NEUTRAL = "neutral"                # No significant impact
    PENDING = "pending"                # Outcome not yet determined

class ImpactType(Enum):
    """Types of impact from decisions"""
    
    DIPLOMATIC = "diplomatic"          # Impact on relationships
    STRATEGIC = "strategic"            # Impact on strategic position
    ECONOMIC = "economic"              # Impact on economic situation
    MILITARY = "military"              # Impact on military capabilities
    REPUTATION = "reputation"          # Impact on faction reputation
    GOAL_PROGRESS = "goal_progress"    # Impact on goal achievement

class LearningInsight(Enum):
    """Types of learning insights"""
    
    TIMING_PATTERN = "timing_pattern"           # Patterns in timing effectiveness
    PERSONALITY_MATCH = "personality_match"     # Personality-decision compatibility
    RELATIONSHIP_FACTOR = "relationship_factor" # Relationship impact patterns
    STRATEGIC_CONTEXT = "strategic_context"     # Strategic situation patterns
    GOAL_ALIGNMENT = "goal_alignment"          # Goal alignment effectiveness
    RISK_ASSESSMENT = "risk_assessment"        # Risk prediction accuracy

@dataclass
class OutcomeMetrics:
    """Metrics for measuring decision outcomes"""
    
    # Success metrics
    success_rate: float = 0.0           # Percentage of successful decisions
    goal_achievement_rate: float = 0.0  # Rate of goal progress
    relationship_improvement: float = 0.0  # Average relationship change
    strategic_gain: float = 0.0         # Average strategic position change
    
    # Risk metrics
    risk_accuracy: float = 0.0          # How accurate risk assessments were
    unexpected_outcomes: float = 0.0    # Rate of surprising results
    
    # Efficiency metrics
    decision_speed: float = 0.0         # Average time to make decisions
    resource_efficiency: float = 0.0    # Resource cost vs benefit
    
    # Learning metrics
    improvement_trend: float = 0.0      # Rate of improvement over time
    pattern_recognition: float = 0.0    # Ability to recognize patterns

@dataclass
class DecisionOutcome:
    """Detailed outcome of a diplomatic decision"""
    
    outcome_id: UUID = field(default_factory=uuid4)
    decision_result: DecisionResult = None
    
    # Outcome classification
    category: OutcomeCategory = OutcomeCategory.PENDING
    confidence: float = 0.5             # Confidence in outcome assessment
    
    # Impact measurements
    impacts: Dict[ImpactType, float] = field(default_factory=dict)
    
    # Detailed analysis
    expected_vs_actual: Dict[str, Any] = field(default_factory=dict)
    contributing_factors: List[str] = field(default_factory=list)
    unexpected_elements: List[str] = field(default_factory=list)
    
    # Timeline tracking
    immediate_effects: Dict[str, Any] = field(default_factory=dict)
    short_term_effects: Dict[str, Any] = field(default_factory=dict)
    long_term_effects: Dict[str, Any] = field(default_factory=dict)
    
    # Learning data
    lessons_learned: List[str] = field(default_factory=list)
    pattern_matches: List[str] = field(default_factory=list)
    
    # Metadata
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    evaluation_method: str = "automatic"
    
    def update_impact(self, impact_type: ImpactType, value: float) -> None:
        """Update impact measurement"""
        self.impacts[impact_type] = value
        self.last_updated = datetime.utcnow()
    
    def add_lesson(self, lesson: str) -> None:
        """Add a lesson learned"""
        if lesson not in self.lessons_learned:
            self.lessons_learned.append(lesson)
            self.last_updated = datetime.utcnow()
    
    def calculate_overall_success_score(self) -> float:
        """Calculate overall success score (0.0 to 1.0)"""
        if self.category == OutcomeCategory.SUCCESS:
            return 1.0
        elif self.category == OutcomeCategory.PARTIAL_SUCCESS:
            return 0.6
        elif self.category == OutcomeCategory.NEUTRAL:
            return 0.5
        elif self.category == OutcomeCategory.FAILURE:
            return 0.2
        elif self.category == OutcomeCategory.BACKFIRE:
            return 0.0
        else:  # PENDING
            return 0.5

@dataclass
class LearningPattern:
    """A learned pattern from decision outcomes"""
    
    pattern_id: UUID = field(default_factory=uuid4)
    insight_type: LearningInsight = None
    
    # Pattern description
    pattern_name: str = ""
    description: str = ""
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Pattern strength
    confidence: float = 0.0             # Confidence in pattern (0.0 to 1.0)
    sample_size: int = 0                # Number of observations
    success_rate: float = 0.0           # Success rate when pattern applies
    
    # Pattern application
    applicable_decisions: List[DecisionType] = field(default_factory=list)
    applicable_contexts: List[str] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    avoid_conditions: List[str] = field(default_factory=list)
    
    # Metadata
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    last_validated: datetime = field(default_factory=datetime.utcnow)
    validation_count: int = 0

class DiplomaticOutcomeTracker:
    """Tracks and analyzes diplomatic decision outcomes for learning"""
    
    def __init__(self, diplomacy_service=None, faction_service=None):
        """Initialize the outcome tracker"""
        self.diplomacy_service = diplomacy_service
        self.faction_service = faction_service
        
        # Outcome storage
        self.outcomes: Dict[UUID, DecisionOutcome] = {}
        self.faction_outcomes: Dict[UUID, List[UUID]] = defaultdict(list)
        
        # Learning data
        self.learned_patterns: Dict[UUID, LearningPattern] = {}
        self.faction_metrics: Dict[UUID, OutcomeMetrics] = {}
        
        # Analysis windows
        self.recent_outcomes = deque(maxlen=100)  # Last 100 outcomes
        self.analysis_window = timedelta(days=30)  # 30-day analysis window
        
        # Configuration
        self.min_pattern_samples = 5       # Minimum samples to establish pattern
        self.pattern_confidence_threshold = 0.7  # Minimum confidence for patterns
        self.outcome_evaluation_delay = timedelta(hours=6)  # Wait before evaluating
        
        logger.info("Diplomatic Outcome Tracker initialized")
    
    def track_decision_outcome(
        self, 
        decision_result: DecisionResult,
        immediate_context: Dict[str, Any] = None
    ) -> UUID:
        """Start tracking the outcome of a decision"""
        
        if immediate_context is None:
            immediate_context = {}
        
        outcome = DecisionOutcome(decision_result=decision_result)
        
        # Extract faction ID from decision
        faction_id = self._extract_faction_id(decision_result)
        
        # Store outcome
        self.outcomes[outcome.outcome_id] = outcome
        if faction_id:
            self.faction_outcomes[faction_id].append(outcome.outcome_id)
        
        self.recent_outcomes.append(outcome.outcome_id)
        
        # Schedule evaluation
        self._schedule_outcome_evaluation(outcome.outcome_id)
        
        logger.debug(f"Started tracking outcome {outcome.outcome_id} for decision "
                    f"{decision_result.decision_option.decision_type.value}")
        
        return outcome.outcome_id
    
    def update_outcome_status(
        self, 
        outcome_id: UUID, 
        category: OutcomeCategory,
        impacts: Dict[ImpactType, float] = None,
        additional_data: Dict[str, Any] = None
    ) -> None:
        """Update the status of a tracked outcome"""
        
        outcome = self.outcomes.get(outcome_id)
        if not outcome:
            logger.warning(f"Outcome {outcome_id} not found")
            return
        
        outcome.category = category
        outcome.last_updated = datetime.utcnow()
        
        if impacts:
            outcome.impacts.update(impacts)
        
        if additional_data:
            outcome.expected_vs_actual.update(additional_data)
        
        # Trigger learning analysis
        self._analyze_outcome_for_learning(outcome)
        
        # Update faction metrics
        faction_id = self._extract_faction_id(outcome.decision_result)
        if faction_id:
            self._update_faction_metrics(faction_id)
        
        logger.debug(f"Updated outcome {outcome_id} to {category.value}")
    
    def evaluate_decision_effectiveness(
        self, 
        faction_id: UUID, 
        decision_type: DecisionType,
        time_window: timedelta = None
    ) -> Dict[str, Any]:
        """Evaluate the effectiveness of a specific decision type for a faction"""
        
        if time_window is None:
            time_window = self.analysis_window
        
        cutoff_time = datetime.utcnow() - time_window
        
        # Get relevant outcomes
        relevant_outcomes = []
        for outcome_id in self.faction_outcomes.get(faction_id, []):
            outcome = self.outcomes.get(outcome_id)
            if (outcome and 
                outcome.decision_result.decision_option.decision_type == decision_type and
                outcome.evaluated_at >= cutoff_time):
                relevant_outcomes.append(outcome)
        
        if not relevant_outcomes:
            return {"error": "No outcomes found for analysis"}
        
        # Calculate metrics
        total_outcomes = len(relevant_outcomes)
        success_count = sum(1 for o in relevant_outcomes 
                          if o.category in [OutcomeCategory.SUCCESS, OutcomeCategory.PARTIAL_SUCCESS])
        
        success_rate = success_count / total_outcomes if total_outcomes > 0 else 0.0
        
        # Average impacts
        impact_averages = {}
        for impact_type in ImpactType:
            values = [o.impacts.get(impact_type, 0.0) for o in relevant_outcomes 
                     if impact_type in o.impacts]
            if values:
                impact_averages[impact_type.value] = statistics.mean(values)
        
        # Success scores
        success_scores = [o.calculate_overall_success_score() for o in relevant_outcomes]
        avg_success_score = statistics.mean(success_scores) if success_scores else 0.0
        
        return {
            "decision_type": decision_type.value,
            "faction_id": faction_id,
            "analysis_period": time_window.days,
            "total_decisions": total_outcomes,
            "success_rate": success_rate,
            "average_success_score": avg_success_score,
            "impact_averages": impact_averages,
            "trend": self._calculate_effectiveness_trend(relevant_outcomes),
            "recommendations": self._generate_effectiveness_recommendations(
                faction_id, decision_type, relevant_outcomes
            )
        }
    
    def get_learning_insights(self, faction_id: UUID = None) -> List[Dict[str, Any]]:
        """Get learning insights for a faction or globally"""
        
        insights = []
        
        # Filter patterns by faction if specified
        relevant_patterns = []
        for pattern in self.learned_patterns.values():
            if faction_id is None or self._pattern_applies_to_faction(pattern, faction_id):
                relevant_patterns.append(pattern)
        
        # Sort by confidence and relevance
        relevant_patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        for pattern in relevant_patterns[:10]:  # Top 10 insights
            insights.append({
                "insight_type": pattern.insight_type.value,
                "pattern_name": pattern.pattern_name,
                "description": pattern.description,
                "confidence": pattern.confidence,
                "sample_size": pattern.sample_size,
                "success_rate": pattern.success_rate,
                "recommendations": pattern.recommendations,
                "applicable_decisions": [d.value for d in pattern.applicable_decisions]
            })
        
        return insights
    
    def predict_decision_success(
        self, 
        faction_id: UUID, 
        decision_type: DecisionType,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Predict the likely success of a decision based on learned patterns"""
        
        if context is None:
            context = {}
        
        # Get historical data for this decision type
        historical_analysis = self.evaluate_decision_effectiveness(faction_id, decision_type)
        
        base_success_rate = historical_analysis.get("success_rate", 0.5)
        
        # Apply pattern-based adjustments
        pattern_adjustments = []
        applicable_patterns = self._find_applicable_patterns(faction_id, decision_type, context)
        
        for pattern in applicable_patterns:
            if pattern.confidence >= self.pattern_confidence_threshold:
                # Adjust prediction based on pattern
                pattern_success_rate = pattern.success_rate
                adjustment = (pattern_success_rate - 0.5) * pattern.confidence
                pattern_adjustments.append({
                    "pattern": pattern.pattern_name,
                    "adjustment": adjustment,
                    "confidence": pattern.confidence
                })
        
        # Calculate final prediction
        total_adjustment = sum(adj["adjustment"] for adj in pattern_adjustments)
        predicted_success = max(0.0, min(1.0, base_success_rate + total_adjustment))
        
        # Calculate confidence in prediction
        prediction_confidence = min(1.0, len(pattern_adjustments) * 0.2 + 0.3)
        
        return {
            "predicted_success_rate": predicted_success,
            "prediction_confidence": prediction_confidence,
            "base_success_rate": base_success_rate,
            "pattern_adjustments": pattern_adjustments,
            "recommendations": self._generate_prediction_recommendations(
                faction_id, decision_type, context, applicable_patterns
            )
        }
    
    def get_faction_learning_summary(self, faction_id: UUID) -> Dict[str, Any]:
        """Get a summary of learning data for a faction"""
        
        outcomes = [self.outcomes[oid] for oid in self.faction_outcomes.get(faction_id, [])]
        recent_outcomes = [o for o in outcomes 
                          if o.evaluated_at >= datetime.utcnow() - self.analysis_window]
        
        if not recent_outcomes:
            return {"error": "No recent outcomes for faction"}
        
        # Calculate metrics
        total_decisions = len(recent_outcomes)
        successful_decisions = sum(1 for o in recent_outcomes 
                                 if o.category in [OutcomeCategory.SUCCESS, OutcomeCategory.PARTIAL_SUCCESS])
        
        # Decision type breakdown
        decision_breakdown = defaultdict(list)
        for outcome in recent_outcomes:
            decision_type = outcome.decision_result.decision_option.decision_type
            decision_breakdown[decision_type].append(outcome)
        
        type_analysis = {}
        for decision_type, type_outcomes in decision_breakdown.items():
            success_count = sum(1 for o in type_outcomes 
                              if o.category in [OutcomeCategory.SUCCESS, OutcomeCategory.PARTIAL_SUCCESS])
            type_analysis[decision_type.value] = {
                "total": len(type_outcomes),
                "successful": success_count,
                "success_rate": success_count / len(type_outcomes) if type_outcomes else 0.0
            }
        
        # Learning progress
        learning_progress = self._calculate_learning_progress(faction_id, recent_outcomes)
        
        return {
            "faction_id": faction_id,
            "analysis_period_days": self.analysis_window.days,
            "total_decisions": total_decisions,
            "successful_decisions": successful_decisions,
            "overall_success_rate": successful_decisions / total_decisions if total_decisions > 0 else 0.0,
            "decision_type_analysis": type_analysis,
            "learning_progress": learning_progress,
            "applicable_patterns": len(self._get_faction_patterns(faction_id)),
            "improvement_trend": self._calculate_improvement_trend(faction_id),
            "recommendations": self._generate_faction_recommendations(faction_id)
        }
    
    def _schedule_outcome_evaluation(self, outcome_id: UUID) -> None:
        """Schedule automatic evaluation of an outcome"""
        # In a full implementation, this would use a task scheduler
        # For now, we'll mark it for manual evaluation
        outcome = self.outcomes.get(outcome_id)
        if outcome:
            outcome.evaluation_method = "scheduled"
    
    def _analyze_outcome_for_learning(self, outcome: DecisionOutcome) -> None:
        """Analyze an outcome to extract learning insights"""
        
        # Extract decision characteristics
        decision = outcome.decision_result.decision_option
        faction_id = self._extract_faction_id(outcome.decision_result)
        
        # Look for patterns
        self._update_timing_patterns(outcome)
        self._update_personality_patterns(outcome, faction_id)
        self._update_relationship_patterns(outcome)
        self._update_strategic_patterns(outcome)
        self._update_goal_alignment_patterns(outcome)
        self._update_risk_assessment_patterns(outcome)
        
        # Generate lessons learned
        lessons = self._extract_lessons_from_outcome(outcome)
        for lesson in lessons:
            outcome.add_lesson(lesson)
    
    def _update_timing_patterns(self, outcome: DecisionOutcome) -> None:
        """Update patterns related to decision timing"""
        
        decision = outcome.decision_result.decision_option
        
        # Analyze timing effectiveness
        # This would examine factors like time of day, urgency, etc.
        # For now, create a basic pattern
        
        pattern_key = f"timing_{decision.decision_type.value}"
        pattern = self._get_or_create_pattern(
            pattern_key, 
            LearningInsight.TIMING_PATTERN,
            f"Timing effectiveness for {decision.decision_type.value}"
        )
        
        # Update pattern with outcome data
        self._update_pattern_with_outcome(pattern, outcome)
    
    def _update_personality_patterns(self, outcome: DecisionOutcome, faction_id: UUID) -> None:
        """Update patterns related to personality-decision compatibility"""
        
        if not faction_id:
            return
        
        decision = outcome.decision_result.decision_option
        
        # This would analyze how personality traits affect decision success
        pattern_key = f"personality_{faction_id}_{decision.decision_type.value}"
        pattern = self._get_or_create_pattern(
            pattern_key,
            LearningInsight.PERSONALITY_MATCH,
            f"Personality compatibility for {decision.decision_type.value}"
        )
        
        self._update_pattern_with_outcome(pattern, outcome)
    
    def _update_relationship_patterns(self, outcome: DecisionOutcome) -> None:
        """Update patterns related to relationship factors"""
        
        decision = outcome.decision_result.decision_option
        
        if decision.target_faction_id:
            pattern_key = f"relationship_{decision.decision_type.value}"
            pattern = self._get_or_create_pattern(
                pattern_key,
                LearningInsight.RELATIONSHIP_FACTOR,
                f"Relationship impact on {decision.decision_type.value}"
            )
            
            self._update_pattern_with_outcome(pattern, outcome)
    
    def _update_strategic_patterns(self, outcome: DecisionOutcome) -> None:
        """Update patterns related to strategic context"""
        
        decision = outcome.decision_result.decision_option
        
        pattern_key = f"strategic_{decision.decision_type.value}"
        pattern = self._get_or_create_pattern(
            pattern_key,
            LearningInsight.STRATEGIC_CONTEXT,
            f"Strategic context for {decision.decision_type.value}"
        )
        
        self._update_pattern_with_outcome(pattern, outcome)
    
    def _update_goal_alignment_patterns(self, outcome: DecisionOutcome) -> None:
        """Update patterns related to goal alignment"""
        
        decision = outcome.decision_result.decision_option
        
        pattern_key = f"goal_alignment_{decision.decision_type.value}"
        pattern = self._get_or_create_pattern(
            pattern_key,
            LearningInsight.GOAL_ALIGNMENT,
            f"Goal alignment effectiveness for {decision.decision_type.value}"
        )
        
        self._update_pattern_with_outcome(pattern, outcome)
    
    def _update_risk_assessment_patterns(self, outcome: DecisionOutcome) -> None:
        """Update patterns related to risk assessment accuracy"""
        
        decision = outcome.decision_result.decision_option
        
        pattern_key = f"risk_{decision.decision_type.value}"
        pattern = self._get_or_create_pattern(
            pattern_key,
            LearningInsight.RISK_ASSESSMENT,
            f"Risk assessment accuracy for {decision.decision_type.value}"
        )
        
        self._update_pattern_with_outcome(pattern, outcome)
    
    def _get_or_create_pattern(
        self, 
        pattern_key: str, 
        insight_type: LearningInsight, 
        description: str
    ) -> LearningPattern:
        """Get existing pattern or create new one"""
        
        # Look for existing pattern
        for pattern in self.learned_patterns.values():
            if pattern.pattern_name == pattern_key:
                return pattern
        
        # Create new pattern
        pattern = LearningPattern(
            insight_type=insight_type,
            pattern_name=pattern_key,
            description=description
        )
        
        self.learned_patterns[pattern.pattern_id] = pattern
        return pattern
    
    def _update_pattern_with_outcome(self, pattern: LearningPattern, outcome: DecisionOutcome) -> None:
        """Update a pattern with new outcome data"""
        
        pattern.sample_size += 1
        pattern.last_validated = datetime.utcnow()
        pattern.validation_count += 1
        
        # Update success rate
        success_score = outcome.calculate_overall_success_score()
        if pattern.sample_size == 1:
            pattern.success_rate = success_score
        else:
            # Running average
            pattern.success_rate = (
                (pattern.success_rate * (pattern.sample_size - 1) + success_score) / 
                pattern.sample_size
            )
        
        # Update confidence based on sample size
        pattern.confidence = min(1.0, pattern.sample_size / self.min_pattern_samples)
        
        # Add applicable decision type
        decision_type = outcome.decision_result.decision_option.decision_type
        if decision_type not in pattern.applicable_decisions:
            pattern.applicable_decisions.append(decision_type)
    
    def _extract_lessons_from_outcome(self, outcome: DecisionOutcome) -> List[str]:
        """Extract specific lessons from an outcome"""
        
        lessons = []
        decision = outcome.decision_result.decision_option
        
        if outcome.category == OutcomeCategory.SUCCESS:
            lessons.append(f"{decision.decision_type.value} was effective in this context")
        elif outcome.category == OutcomeCategory.FAILURE:
            lessons.append(f"{decision.decision_type.value} was ineffective in this context")
        elif outcome.category == OutcomeCategory.BACKFIRE:
            lessons.append(f"{decision.decision_type.value} had negative consequences - avoid similar situations")
        
        # Add impact-specific lessons
        for impact_type, value in outcome.impacts.items():
            if value > 0.5:
                lessons.append(f"Decision had positive {impact_type.value} impact")
            elif value < -0.5:
                lessons.append(f"Decision had negative {impact_type.value} impact")
        
        return lessons
    
    def _extract_faction_id(self, decision_result: DecisionResult) -> Optional[UUID]:
        """Extract faction ID from decision result"""
        # This would depend on how faction ID is stored in the decision
        # For now, return None as placeholder
        return decision_result.decision_option.parameters.get('faction_id')
    
    def _update_faction_metrics(self, faction_id: UUID) -> None:
        """Update metrics for a specific faction"""
        
        outcomes = [self.outcomes[oid] for oid in self.faction_outcomes.get(faction_id, [])]
        recent_outcomes = [o for o in outcomes 
                          if o.evaluated_at >= datetime.utcnow() - self.analysis_window]
        
        if not recent_outcomes:
            return
        
        metrics = OutcomeMetrics()
        
        # Calculate success rate
        successful = sum(1 for o in recent_outcomes 
                        if o.category in [OutcomeCategory.SUCCESS, OutcomeCategory.PARTIAL_SUCCESS])
        metrics.success_rate = successful / len(recent_outcomes)
        
        # Calculate other metrics
        success_scores = [o.calculate_overall_success_score() for o in recent_outcomes]
        metrics.goal_achievement_rate = statistics.mean(success_scores)
        
        # Calculate improvement trend
        if len(recent_outcomes) >= 10:
            first_half = recent_outcomes[:len(recent_outcomes)//2]
            second_half = recent_outcomes[len(recent_outcomes)//2:]
            
            first_avg = statistics.mean([o.calculate_overall_success_score() for o in first_half])
            second_avg = statistics.mean([o.calculate_overall_success_score() for o in second_half])
            
            metrics.improvement_trend = second_avg - first_avg
        
        self.faction_metrics[faction_id] = metrics
    
    def _calculate_effectiveness_trend(self, outcomes: List[DecisionOutcome]) -> str:
        """Calculate trend in decision effectiveness"""
        
        if len(outcomes) < 4:
            return "insufficient_data"
        
        # Split into first and second half
        mid_point = len(outcomes) // 2
        first_half = outcomes[:mid_point]
        second_half = outcomes[mid_point:]
        
        first_avg = statistics.mean([o.calculate_overall_success_score() for o in first_half])
        second_avg = statistics.mean([o.calculate_overall_success_score() for o in second_half])
        
        difference = second_avg - first_avg
        
        if difference > 0.1:
            return "improving"
        elif difference < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _generate_effectiveness_recommendations(
        self, 
        faction_id: UUID, 
        decision_type: DecisionType, 
        outcomes: List[DecisionOutcome]
    ) -> List[str]:
        """Generate recommendations based on effectiveness analysis"""
        
        recommendations = []
        
        success_rate = sum(1 for o in outcomes 
                          if o.category in [OutcomeCategory.SUCCESS, OutcomeCategory.PARTIAL_SUCCESS]) / len(outcomes)
        
        if success_rate < 0.3:
            recommendations.append(f"Consider avoiding {decision_type.value} - low success rate")
        elif success_rate > 0.7:
            recommendations.append(f"Continue using {decision_type.value} - high success rate")
        
        # Analyze common failure patterns
        failures = [o for o in outcomes if o.category in [OutcomeCategory.FAILURE, OutcomeCategory.BACKFIRE]]
        if failures:
            common_factors = self._find_common_failure_factors(failures)
            for factor in common_factors:
                recommendations.append(f"Avoid {decision_type.value} when {factor}")
        
        return recommendations
    
    def _find_common_failure_factors(self, failures: List[DecisionOutcome]) -> List[str]:
        """Find common factors in failed decisions"""
        # Placeholder implementation
        return ["under high stress", "without sufficient preparation"]
    
    def _find_applicable_patterns(
        self, 
        faction_id: UUID, 
        decision_type: DecisionType, 
        context: Dict[str, Any]
    ) -> List[LearningPattern]:
        """Find patterns applicable to a specific decision context"""
        
        applicable = []
        
        for pattern in self.learned_patterns.values():
            if (decision_type in pattern.applicable_decisions and
                pattern.confidence >= self.pattern_confidence_threshold):
                applicable.append(pattern)
        
        return applicable
    
    def _pattern_applies_to_faction(self, pattern: LearningPattern, faction_id: UUID) -> bool:
        """Check if a pattern applies to a specific faction"""
        # This would check if the pattern is relevant to the faction
        # For now, return True as placeholder
        return True
    
    def _generate_prediction_recommendations(
        self, 
        faction_id: UUID, 
        decision_type: DecisionType, 
        context: Dict[str, Any], 
        patterns: List[LearningPattern]
    ) -> List[str]:
        """Generate recommendations based on prediction analysis"""
        
        recommendations = []
        
        for pattern in patterns:
            if pattern.success_rate > 0.7:
                recommendations.extend(pattern.recommendations)
            elif pattern.success_rate < 0.3:
                recommendations.extend(pattern.avoid_conditions)
        
        return recommendations
    
    def _calculate_learning_progress(self, faction_id: UUID, outcomes: List[DecisionOutcome]) -> Dict[str, Any]:
        """Calculate learning progress metrics"""
        
        if len(outcomes) < 5:
            return {"status": "insufficient_data"}
        
        # Calculate improvement over time
        chronological_outcomes = sorted(outcomes, key=lambda o: o.evaluated_at)
        
        # Split into quarters
        quarter_size = len(chronological_outcomes) // 4
        if quarter_size < 2:
            return {"status": "insufficient_data"}
        
        quarters = [
            chronological_outcomes[i:i+quarter_size] 
            for i in range(0, len(chronological_outcomes), quarter_size)
        ]
        
        quarter_scores = []
        for quarter in quarters:
            if quarter:
                avg_score = statistics.mean([o.calculate_overall_success_score() for o in quarter])
                quarter_scores.append(avg_score)
        
        # Calculate trend
        if len(quarter_scores) >= 2:
            trend = quarter_scores[-1] - quarter_scores[0]
        else:
            trend = 0.0
        
        return {
            "status": "calculated",
            "trend": trend,
            "quarter_scores": quarter_scores,
            "improvement_rate": trend / len(quarter_scores) if quarter_scores else 0.0
        }
    
    def _get_faction_patterns(self, faction_id: UUID) -> List[LearningPattern]:
        """Get patterns applicable to a faction"""
        return [p for p in self.learned_patterns.values() 
                if self._pattern_applies_to_faction(p, faction_id)]
    
    def _calculate_improvement_trend(self, faction_id: UUID) -> float:
        """Calculate improvement trend for a faction"""
        metrics = self.faction_metrics.get(faction_id)
        return metrics.improvement_trend if metrics else 0.0
    
    def _generate_faction_recommendations(self, faction_id: UUID) -> List[str]:
        """Generate recommendations for a faction based on learning data"""
        
        recommendations = []
        
        # Get faction patterns
        patterns = self._get_faction_patterns(faction_id)
        
        # High-confidence positive patterns
        good_patterns = [p for p in patterns if p.confidence > 0.7 and p.success_rate > 0.7]
        for pattern in good_patterns:
            recommendations.append(f"Continue using strategies from: {pattern.pattern_name}")
        
        # High-confidence negative patterns
        bad_patterns = [p for p in patterns if p.confidence > 0.7 and p.success_rate < 0.3]
        for pattern in bad_patterns:
            recommendations.append(f"Avoid strategies from: {pattern.pattern_name}")
        
        # General recommendations
        metrics = self.faction_metrics.get(faction_id)
        if metrics:
            if metrics.success_rate < 0.4:
                recommendations.append("Consider more conservative diplomatic strategies")
            elif metrics.success_rate > 0.8:
                recommendations.append("Current strategies are highly effective - maintain approach")
        
        return recommendations

# Global outcome tracker instance
_outcome_tracker = None

def get_outcome_tracker(diplomacy_service=None, faction_service=None) -> DiplomaticOutcomeTracker:
    """Get the global outcome tracker instance"""
    global _outcome_tracker
    if _outcome_tracker is None:
        _outcome_tracker = DiplomaticOutcomeTracker(diplomacy_service, faction_service)
    return _outcome_tracker 