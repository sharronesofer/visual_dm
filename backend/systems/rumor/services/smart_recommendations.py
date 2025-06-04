"""
Smart Rumor Recommendations System

This module provides AI-driven recommendations for optimal rumor spreading
strategies based on context analysis, target assessment, and historical data.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Types of recommendations"""
    TARGET_SELECTION = "target_selection"
    CONTENT_OPTIMIZATION = "content_optimization"
    TIMING_STRATEGY = "timing_strategy"
    SPREAD_PATTERN = "spread_pattern"
    MUTATION_STRATEGY = "mutation_strategy"
    COUNTER_STRATEGY = "counter_strategy"


class RecommendationPriority(Enum):
    """Priority levels for recommendations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TargetProfile:
    """Profile for recommendation targeting"""
    target_id: str
    characteristics: Dict[str, Any]
    vulnerabilities: List[str]
    resistances: List[str]
    historical_response: Dict[str, float]
    current_status: Dict[str, Any]


@dataclass
class SmartRecommendation:
    """AI-generated rumor strategy recommendation"""
    recommendation_id: str
    recommendation_type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    rationale: str
    suggested_actions: List[str]
    expected_outcomes: Dict[str, float]
    confidence_score: float
    implementation_cost: float
    risk_assessment: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


class SmartRecommendationEngine:
    """AI-powered recommendation engine for rumor strategies"""
    
    def __init__(self):
        self.target_profiles: Dict[str, TargetProfile] = {}
        self.recommendation_history: List[SmartRecommendation] = []
        self.strategy_templates: Dict[str, Dict] = {}
        self.performance_metrics: Dict[str, Dict] = {}
        self.learning_data: Dict[str, List] = {}
        
        self.recommendation_rules = self._load_recommendation_rules()
        
    def _load_recommendation_rules(self) -> Dict[str, Dict]:
        """Load recommendation rules and strategies"""
        return {
            "target_analysis_factors": {
                "vulnerability": 0.25,
                "influence_potential": 0.20,
                "objective_alignment": 0.20,
                "accessibility": 0.20,
                "risk_level": 0.15
            },
            
            "optimization_strategies": {
                "content_emotional_alignment": {
                    "angry_targets": ["outrage", "injustice", "betrayal"],
                    "fearful_targets": ["threats", "dangers", "uncertainties"],
                    "hopeful_targets": ["opportunities", "positive_changes", "rewards"],
                    "skeptical_targets": ["evidence", "proof", "verification"]
                },
                
                "timing_patterns": {
                    "morning": {"effectiveness": 1.1, "receptivity": 0.8},
                    "afternoon": {"effectiveness": 1.0, "receptivity": 1.0},
                    "evening": {"effectiveness": 1.2, "receptivity": 1.1},
                    "night": {"effectiveness": 0.9, "receptivity": 0.7}
                },
                
                "spread_patterns": {
                    "viral": {"speed": 1.5, "reach": 1.3, "persistence": 0.7},
                    "gradual": {"speed": 0.8, "reach": 1.0, "persistence": 1.2},
                    "targeted": {"speed": 1.0, "reach": 0.8, "persistence": 1.0},
                    "broadcast": {"speed": 1.2, "reach": 1.4, "persistence": 0.6}
                }
            },
            
            "risk_factors": {
                "detection_risk": ["unusual_patterns", "rapid_spread", "inconsistencies"],
                "backfire_risk": ["over_exaggeration", "targeting_allies", "timing_conflicts"],
                "resource_waste": ["low_impact_targets", "redundant_content", "poor_timing"]
            }
        }
    
    def analyze_situation(
        self,
        context: Dict[str, Any],
        objectives: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[SmartRecommendation]:
        """Analyze current situation and generate recommendations"""
        
        recommendations = []
        
        # Generate different types of recommendations
        target_recommendations = self._analyze_target_opportunities(context, objectives)
        recommendations.extend(target_recommendations)
        
        content_recommendations = self._analyze_content_optimization(context, objectives)
        recommendations.extend(content_recommendations)
        
        timing_recommendations = self._analyze_timing_strategies(context, objectives)
        recommendations.extend(timing_recommendations)
        
        pattern_recommendations = self._analyze_spread_patterns(context, objectives)
        recommendations.extend(pattern_recommendations)
        
        # Apply constraints and filtering
        if constraints:
            recommendations = self._apply_constraints(recommendations, constraints)
        
        # Rank recommendations by effectiveness and feasibility
        recommendations = self._rank_recommendations(recommendations, context)
        
        # Store recommendations for learning
        self.recommendation_history.extend(recommendations)
        
        logger.info(f"Generated {len(recommendations)} smart recommendations")
        return recommendations
    
    def _analyze_target_opportunities(
        self, 
        context: Dict[str, Any], 
        objectives: List[str]
    ) -> List[SmartRecommendation]:
        """Analyze and recommend optimal targets"""
        
        recommendations = []
        available_targets = context.get("available_targets", [])
        
        if not available_targets:
            return recommendations
        
        # Score each target
        target_scores = {}
        for target_id in available_targets:
            score = self._calculate_target_score(target_id, context, objectives)
            target_scores[target_id] = score
        
        # Find high-value targets
        sorted_targets = sorted(target_scores.items(), key=lambda x: x[1], reverse=True)
        top_targets = sorted_targets[:3]  # Top 3 targets
        
        for target_id, score in top_targets:
            if score > 0.6:  # High-value threshold
                profile = self.target_profiles.get(target_id, {})
                
                recommendation = SmartRecommendation(
                    recommendation_id=f"target_{target_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    recommendation_type=RecommendationType.TARGET_SELECTION,
                    priority=RecommendationPriority.HIGH if score > 0.75 else RecommendationPriority.MEDIUM,
                    title=f"Priority Target: {target_id}",
                    description=f"Target {target_id} shows high potential for rumor influence",
                    rationale=f"Analysis indicates {score:.1%} effectiveness potential based on current state and objectives",
                    suggested_actions=[
                        f"Focus initial rumor deployment on {target_id}",
                        f"Customize content for {target_id}'s personality profile",
                        f"Monitor {target_id}'s response patterns closely"
                    ],
                    expected_outcomes={
                        "influence_probability": score,
                        "expected_spread_rate": score * 1.2,
                        "objective_alignment": self._calculate_objective_alignment(target_id, objectives)
                    },
                    confidence_score=min(0.95, score + 0.1),
                    implementation_cost=50.0 * (1.0 - score),  # Lower cost for easier targets
                    risk_assessment={
                        "detection_risk": max(0.1, 0.5 - score * 0.3),
                        "backfire_risk": max(0.05, 0.3 - score * 0.2),
                        "resource_efficiency": score
                    }
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_content_optimization(
        self, 
        context: Dict[str, Any], 
        objectives: List[str]
    ) -> List[SmartRecommendation]:
        """Analyze and recommend content optimization strategies"""
        
        recommendations = []
        current_content = context.get("current_rumors", [])
        target_audience = context.get("target_audience", [])
        
        if not current_content:
            return recommendations
        
        # Analyze content effectiveness patterns
        content_analysis = self._analyze_content_patterns(current_content, target_audience)
        
        # Generate optimization recommendations
        if content_analysis.get("emotional_alignment_score", 0) < 0.6:
            recommendation = SmartRecommendation(
                recommendation_id=f"content_emotion_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                recommendation_type=RecommendationType.CONTENT_OPTIMIZATION,
                priority=RecommendationPriority.HIGH,
                title="Improve Emotional Alignment",
                description="Current content lacks emotional resonance with target audience",
                rationale="Analysis shows low emotional engagement scores, reducing spread effectiveness",
                suggested_actions=[
                    "Incorporate more emotionally charged language",
                    "Align content tone with audience mood",
                    "Add personal stakes and consequences",
                    "Use vivid imagery and specific details"
                ],
                expected_outcomes={
                    "engagement_increase": 0.3,
                    "spread_rate_improvement": 0.25,
                    "believability_boost": 0.2
                },
                confidence_score=0.85,
                implementation_cost=30.0,
                risk_assessment={
                    "over_dramatization_risk": 0.2,
                    "credibility_loss_risk": 0.15,
                    "detection_risk": 0.1
                }
            )
            recommendations.append(recommendation)
        
        if content_analysis.get("credibility_score", 0) < 0.7:
            recommendation = SmartRecommendation(
                recommendation_id=f"content_credibility_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                recommendation_type=RecommendationType.CONTENT_OPTIMIZATION,
                priority=RecommendationPriority.MEDIUM,
                title="Enhance Content Credibility",
                description="Content needs more believable details and supporting elements",
                rationale="Low credibility scores indicate audience skepticism",
                suggested_actions=[
                    "Add specific dates, locations, and names",
                    "Include verifiable details mixed with rumors",
                    "Reference recent known events",
                    "Use authoritative source language"
                ],
                expected_outcomes={
                    "believability_increase": 0.4,
                    "persistence_improvement": 0.3,
                    "resistance_reduction": 0.2
                },
                confidence_score=0.8,
                implementation_cost=25.0,
                risk_assessment={
                    "fact_checking_risk": 0.3,
                    "inconsistency_risk": 0.2,
                    "complexity_risk": 0.1
                }
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_timing_strategies(
        self, 
        context: Dict[str, Any], 
        objectives: List[str]
    ) -> List[SmartRecommendation]:
        """Analyze and recommend optimal timing strategies"""
        
        recommendations = []
        current_time = datetime.now().hour
        target_activity_patterns = context.get("target_activity_patterns", {})
        upcoming_events = context.get("upcoming_events", [])
        
        # Analyze current timing effectiveness
        timing_effectiveness = self._calculate_timing_effectiveness(current_time, target_activity_patterns)
        
        if timing_effectiveness < 0.7:
            # Find optimal timing windows
            optimal_windows = self._find_optimal_timing_windows(target_activity_patterns, upcoming_events)
            
            if optimal_windows:
                best_window = optimal_windows[0]
                
                recommendation = SmartRecommendation(
                    recommendation_id=f"timing_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    recommendation_type=RecommendationType.TIMING_STRATEGY,
                    priority=RecommendationPriority.HIGH,
                    title=f"Optimal Timing Window: {best_window['description']}",
                    description=f"Current timing is suboptimal. Better window available at {best_window['time']}",
                    rationale=f"Analysis shows {best_window['effectiveness']:.1%} effectiveness vs current {timing_effectiveness:.1%}",
                    suggested_actions=[
                        f"Delay rumor release until {best_window['time']}",
                        f"Coordinate with {best_window['concurrent_events']}",
                        "Prepare content for immediate deployment",
                        "Monitor target readiness indicators"
                    ],
                    expected_outcomes={
                        "effectiveness_increase": best_window['effectiveness'] - timing_effectiveness,
                        "audience_reach_improvement": 0.3,
                        "engagement_boost": 0.25
                    },
                    confidence_score=0.9,
                    implementation_cost=10.0,  # Low cost, just timing adjustment
                    risk_assessment={
                        "missed_opportunity_risk": 0.1,
                        "competition_risk": 0.15,
                        "relevance_decay_risk": 0.05
                    }
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_spread_patterns(
        self, 
        context: Dict[str, Any], 
        objectives: List[str]
    ) -> List[SmartRecommendation]:
        """Analyze and recommend optimal spreading patterns"""
        
        recommendations = []
        current_pattern = context.get("current_spread_pattern", "gradual")
        network_structure = context.get("network_structure", {})
        resource_constraints = context.get("resource_constraints", {})
        
        # Analyze pattern effectiveness for current context
        pattern_analysis = self._analyze_pattern_suitability(current_pattern, network_structure, objectives)
        
        if pattern_analysis.get("suitability_score", 0) < 0.6:
            # Find better patterns
            alternative_patterns = self._evaluate_alternative_patterns(network_structure, objectives, resource_constraints)
            
            if alternative_patterns:
                best_pattern = alternative_patterns[0]
                
                recommendation = SmartRecommendation(
                    recommendation_id=f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    recommendation_type=RecommendationType.SPREAD_PATTERN,
                    priority=RecommendationPriority.MEDIUM,
                    title=f"Switch to {best_pattern['name']} Pattern",
                    description=f"Current {current_pattern} pattern is suboptimal for objectives",
                    rationale=f"{best_pattern['name']} pattern offers {best_pattern['improvement']:.1%} better alignment",
                    suggested_actions=[
                        f"Implement {best_pattern['name']} spreading strategy",
                        f"Adjust resource allocation: {best_pattern['resource_allocation']}",
                        f"Focus on {best_pattern['key_nodes']} network nodes",
                        "Monitor pattern effectiveness metrics"
                    ],
                    expected_outcomes={
                        "pattern_efficiency": best_pattern['efficiency'],
                        "objective_alignment": best_pattern['objective_alignment'],
                        "resource_optimization": best_pattern['resource_efficiency']
                    },
                    confidence_score=0.75,
                    implementation_cost=best_pattern['implementation_cost'],
                    risk_assessment={
                        "pattern_disruption_risk": 0.2,
                        "adaptation_time_risk": 0.15,
                        "coordination_risk": 0.1
                    }
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_target_score(
        self, 
        target_id: str, 
        context: Dict[str, Any], 
        objectives: List[str]
    ) -> float:
        """Calculate effectiveness score for a target"""
        
        profile = self.target_profiles.get(target_id)
        if not profile:
            return 0.3  # Default low score for unknown targets
        
        score_factors = {
            "vulnerability": self._assess_target_vulnerability(profile, context),
            "influence_potential": self._assess_influence_potential(profile, context),
            "objective_alignment": self._calculate_objective_alignment(target_id, objectives),
            "accessibility": self._assess_target_accessibility(profile, context),
            "risk_level": 1.0 - self._assess_target_risk(profile, context)
        }
        
        # Weighted combination
        weights = self.recommendation_rules["target_analysis_factors"]
        
        total_score = sum(
            score_factors[factor] * weight 
            for factor, weight in weights.items() 
            if factor in score_factors
        )
        
        return min(1.0, max(0.0, total_score))
    
    def _assess_target_vulnerability(self, profile: TargetProfile, context: Dict[str, Any]) -> float:
        """Assess how vulnerable a target is to rumor influence"""
        
        vulnerability_score = 0.5  # Base score
        
        # Personality-based vulnerabilities
        vulnerable_traits = ["gullible", "emotional", "social", "impulsive"]
        for trait in vulnerable_traits:
            if trait in profile.characteristics.get("personality_traits", []):
                vulnerability_score += 0.1
        
        # Current state vulnerabilities
        current_mood = profile.current_status.get("mood", "neutral")
        mood_vulnerabilities = {
            "worried": 0.2,
            "angry": 0.15,
            "fearful": 0.25,
            "excited": 0.1,
            "suspicious": -0.1
        }
        vulnerability_score += mood_vulnerabilities.get(current_mood, 0)
        
        # Social isolation increases vulnerability
        social_connections = profile.characteristics.get("social_connections", 5)
        if social_connections < 3:
            vulnerability_score += 0.15
        
        return min(1.0, max(0.0, vulnerability_score))
    
    def _assess_influence_potential(self, profile: TargetProfile, context: Dict[str, Any]) -> float:
        """Assess the potential influence impact of targeting this entity"""
        
        influence_factors = {
            "social_position": profile.characteristics.get("social_status", 0.5),
            "network_centrality": profile.characteristics.get("network_centrality", 0.5),
            "credibility": profile.characteristics.get("credibility", 0.5),
            "activity_level": profile.characteristics.get("activity_level", 0.5)
        }
        
        return sum(influence_factors.values()) / len(influence_factors)
    
    def _calculate_objective_alignment(self, target_id: str, objectives: List[str]) -> float:
        """Calculate how well targeting this entity aligns with objectives"""
        
        # Simplified alignment calculation
        # In practice, this would analyze objective content and target characteristics
        
        alignment_score = 0.3  # Reduced default alignment
        
        # Normalize target ID for better matching (handle underscores, etc.)
        normalized_target_id = target_id.lower().replace("_", " ")
        target_keywords = normalized_target_id.split()
        
        # Check if target is mentioned in objectives (stronger bonus)
        for objective in objectives:
            objective_lower = objective.lower()
            
            # Direct match (original logic)
            if target_id.lower() in objective_lower:
                alignment_score += 0.5  # Increased from 0.3
            
            # Normalized match (handle underscores/spaces)
            elif normalized_target_id in objective_lower:
                alignment_score += 0.5
                
            # Partial keyword match (if target has multiple words)
            elif len(target_keywords) > 1:
                matches = sum(1 for keyword in target_keywords if keyword in objective_lower)
                if matches >= len(target_keywords) // 2:  # At least half the keywords match
                    alignment_score += 0.4
                    
        # Check for objective keywords that match target characteristics
        profile = self.target_profiles.get(target_id)
        if profile:
            target_roles = profile.characteristics.get("roles", [])
            for objective in objectives:
                for role in target_roles:
                    if role.lower() in objective.lower():
                        alignment_score += 0.1
                        
            # Check for specific targeting language
            targeting_keywords = ["target", "focus", "specifically", "priority"]
            for objective in objectives:
                objective_lower = objective.lower()
                for keyword in targeting_keywords:
                    if keyword in objective_lower and (
                        target_id.lower() in objective_lower or 
                        normalized_target_id in objective_lower or
                        any(tk in objective_lower for tk in target_keywords)
                    ):
                        alignment_score += 0.2  # Bonus for explicit targeting
        
        return min(1.0, alignment_score)
    
    def _assess_target_accessibility(self, profile: TargetProfile, context: Dict[str, Any]) -> float:
        """Assess how accessible a target is for rumor influence"""
        
        accessibility = 0.7  # Base accessibility
        
        # Check for protective factors
        protection_level = profile.characteristics.get("protection_level", 0)
        accessibility -= protection_level * 0.3
        
        # Check for isolation
        isolation_level = profile.characteristics.get("isolation_level", 0)
        accessibility -= isolation_level * 0.2
        
        # Check for counter-intelligence
        counter_intel = profile.characteristics.get("counter_intelligence", 0)
        accessibility -= counter_intel * 0.2
        
        return max(0.1, accessibility)
    
    def _assess_target_risk(self, profile: TargetProfile, context: Dict[str, Any]) -> float:
        """Assess the risk of targeting this entity"""
        
        risk_factors = {
            "detection_capability": profile.characteristics.get("detection_capability", 0.3),
            "retaliation_potential": profile.characteristics.get("retaliation_potential", 0.2),
            "investigation_resources": profile.characteristics.get("investigation_resources", 0.2),
            "allied_support": profile.characteristics.get("allied_support", 0.3)
        }
        
        return sum(risk_factors.values()) / len(risk_factors)
    
    def get_recommendation_effectiveness(self, recommendation_id: str) -> Optional[Dict[str, float]]:
        """Get effectiveness metrics for a implemented recommendation"""
        
        # This would integrate with actual rumor system to track outcomes
        # For now, return simulated effectiveness data
        
        recommendation = None
        for rec in self.recommendation_history:
            if rec.recommendation_id == recommendation_id:
                recommendation = rec
                break
        
        if not recommendation:
            return None
        
        # Simulate effectiveness based on confidence score and random factors
        base_effectiveness = recommendation.confidence_score
        random_factor = random.uniform(0.8, 1.2)
        actual_effectiveness = min(1.0, base_effectiveness * random_factor)
        
        return {
            "overall_effectiveness": actual_effectiveness,
            "objective_progress": actual_effectiveness * 0.8,
            "resource_efficiency": recommendation.confidence_score * 0.9,
            "risk_materialization": max(0.0, 0.3 - actual_effectiveness * 0.2),
            "unexpected_benefits": max(0.0, (actual_effectiveness - base_effectiveness) * 0.5)
        }
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get system-wide recommendation performance metrics"""
        
        if not self.recommendation_history:
            return {"error": "No recommendation history available"}
        
        # Analyze recommendation types
        type_distribution = {}
        for rec in self.recommendation_history:
            rec_type = rec.recommendation_type.value
            type_distribution[rec_type] = type_distribution.get(rec_type, 0) + 1
        
        # Calculate average confidence
        avg_confidence = sum(rec.confidence_score for rec in self.recommendation_history) / len(self.recommendation_history)
        
        # Analyze priority distribution
        priority_distribution = {}
        for rec in self.recommendation_history:
            priority = rec.priority.value
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        return {
            "total_recommendations": len(self.recommendation_history),
            "average_confidence_score": round(avg_confidence, 3),
            "recommendation_type_distribution": type_distribution,
            "priority_distribution": priority_distribution,
            "recent_recommendations": len([
                rec for rec in self.recommendation_history 
                if (datetime.now() - rec.timestamp).days < 7
            ])
        }

    def _analyze_content_patterns(self, content_list: List[str], target_audience: List[str]) -> Dict[str, float]:
        """Analyze current content patterns for effectiveness"""
        
        analysis = {
            "emotional_alignment_score": 0.5,
            "credibility_score": 0.5,
            "engagement_potential": 0.5,
            "clarity_score": 0.5
        }
        
        if not content_list:
            return analysis
        
        # Analyze emotional content
        emotional_keywords = ["angry", "fear", "hope", "excited", "worried", "happy", "sad", "outraged"]
        total_emotional_words = 0
        total_words = 0
        
        for content in content_list:
            words = content.lower().split()
            total_words += len(words)
            for word in words:
                if any(emotion in word for emotion in emotional_keywords):
                    total_emotional_words += 1
        
        if total_words > 0:
            analysis["emotional_alignment_score"] = min(1.0, total_emotional_words / total_words * 10)
        
        # Analyze credibility indicators
        credibility_keywords = ["sources", "evidence", "confirmed", "witnessed", "official", "reported"]
        credibility_score = 0.0
        
        for content in content_list:
            content_lower = content.lower()
            for keyword in credibility_keywords:
                if keyword in content_lower:
                    credibility_score += 0.1
        
        analysis["credibility_score"] = min(1.0, credibility_score)
        
        # Engagement potential (length and complexity)
        avg_length = sum(len(content) for content in content_list) / len(content_list)
        analysis["engagement_potential"] = min(1.0, avg_length / 100)  # Normalize around 100 chars
        
        return analysis
    
    def _calculate_timing_effectiveness(self, current_hour: int, activity_patterns: Dict[str, Dict]) -> float:
        """Calculate effectiveness of current timing"""
        
        if not activity_patterns:
            return 0.5  # Default moderate effectiveness
        
        # Map hour to time period
        time_periods = {
            "morning": list(range(6, 12)),
            "afternoon": list(range(12, 17)),
            "evening": list(range(17, 22)),
            "night": list(range(22, 24)) + list(range(0, 6))
        }
        
        current_period = "afternoon"  # Default
        for period, hours in time_periods.items():
            if current_hour in hours:
                current_period = period
                break
        
        # Get effectiveness for current period
        period_data = activity_patterns.get(current_period, {"activity": 0.5, "receptivity": 0.5})
        
        activity_level = period_data.get("activity", 0.5)
        receptivity_level = period_data.get("receptivity", 0.5)
        
        # Combine activity and receptivity
        effectiveness = (activity_level * 0.6) + (receptivity_level * 0.4)
        
        return min(1.0, max(0.0, effectiveness))
    
    def _find_optimal_timing_windows(
        self, 
        activity_patterns: Dict[str, Dict], 
        upcoming_events: List[str]
    ) -> List[Dict[str, Any]]:
        """Find optimal timing windows for rumor deployment"""
        
        windows = []
        
        if not activity_patterns:
            return windows
        
        # Analyze each time period
        for period, data in activity_patterns.items():
            activity = data.get("activity", 0.5)
            receptivity = data.get("receptivity", 0.5)
            
            effectiveness = (activity * 0.6) + (receptivity * 0.4)
            
            # Add event bonuses
            event_bonus = 0.0
            relevant_events = [event for event in upcoming_events if period in event.lower()]
            if relevant_events:
                event_bonus = len(relevant_events) * 0.1
            
            total_effectiveness = min(1.0, effectiveness + event_bonus)
            
            windows.append({
                "time": period,
                "description": f"{period.title()} period",
                "effectiveness": total_effectiveness,
                "concurrent_events": relevant_events,
                "base_activity": activity,
                "base_receptivity": receptivity
            })
        
        # Sort by effectiveness
        windows.sort(key=lambda x: x["effectiveness"], reverse=True)
        
        return windows
    
    def _evaluate_alternative_patterns(
        self, 
        network_structure: Dict[str, Any], 
        objectives: List[str], 
        resource_constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate alternative spreading patterns"""
        
        patterns = []
        
        # Define pattern characteristics
        pattern_types = {
            "viral": {
                "speed": 1.5,
                "reach": 1.3,
                "persistence": 0.7,
                "resource_cost": 1.2,
                "complexity": 0.6
            },
            "targeted": {
                "speed": 1.0,
                "reach": 0.8,
                "persistence": 1.0,
                "resource_cost": 0.8,
                "complexity": 0.8
            },
            "broadcast": {
                "speed": 1.2,
                "reach": 1.4,
                "persistence": 0.6,
                "resource_cost": 1.5,
                "complexity": 0.4
            },
            "gradual": {
                "speed": 0.8,
                "reach": 1.0,
                "persistence": 1.2,
                "resource_cost": 0.7,
                "complexity": 0.7
            }
        }
        
        # Evaluate each pattern
        for pattern_name, characteristics in pattern_types.items():
            # Calculate objective alignment
            objective_alignment = 0.5
            if "fast" in " ".join(objectives).lower():
                objective_alignment += characteristics["speed"] * 0.2
            if "wide" in " ".join(objectives).lower():
                objective_alignment += characteristics["reach"] * 0.2
            if "lasting" in " ".join(objectives).lower():
                objective_alignment += characteristics["persistence"] * 0.2
            
            # Calculate resource efficiency
            max_budget = resource_constraints.get("max_budget", 1000)
            cost_efficiency = min(1.0, max_budget / (characteristics["resource_cost"] * 100))
            
            # Calculate improvement over current
            improvement = (objective_alignment + cost_efficiency) / 2 - 0.5
            
            patterns.append({
                "name": pattern_name,
                "efficiency": (characteristics["speed"] + characteristics["reach"] + characteristics["persistence"]) / 3,
                "objective_alignment": objective_alignment,
                "resource_efficiency": cost_efficiency,
                "improvement": improvement,
                "implementation_cost": characteristics["resource_cost"] * 50,
                "resource_allocation": f"Speed: {characteristics['speed']:.1f}, Reach: {characteristics['reach']:.1f}",
                "key_nodes": "high-centrality nodes" if pattern_name == "targeted" else "broad network"
            })
        
        # Sort by improvement potential
        patterns.sort(key=lambda x: x["improvement"], reverse=True)
        
        return patterns
    
    def _analyze_pattern_suitability(
        self, 
        current_pattern: str, 
        network_structure: Dict[str, Any], 
        objectives: List[str]
    ) -> Dict[str, float]:
        """Analyze suitability of current spreading pattern"""
        
        # Default suitability
        suitability_score = 0.5
        
        # Analyze network structure compatibility
        network_density = network_structure.get("density", 0.5)
        network_clustering = network_structure.get("clustering", 0.5)
        
        # Pattern-specific suitability rules
        if current_pattern == "viral":
            # Viral works better in dense, highly clustered networks
            suitability_score += (network_density * 0.3) + (network_clustering * 0.2)
        elif current_pattern == "targeted":
            # Targeted works better with moderate density, high clustering
            suitability_score += (min(network_density, 0.7) * 0.2) + (network_clustering * 0.3)
        elif current_pattern == "broadcast":
            # Broadcast works better in sparse networks
            suitability_score += ((1.0 - network_density) * 0.3) + (network_clustering * 0.1)
        elif current_pattern == "gradual":
            # Gradual works consistently across different network types
            suitability_score += 0.2
        
        # Objective alignment
        objective_text = " ".join(objectives).lower()
        if "fast" in objective_text and current_pattern in ["viral", "broadcast"]:
            suitability_score += 0.2
        elif "persistent" in objective_text and current_pattern in ["gradual", "targeted"]:
            suitability_score += 0.2
        
        return {
            "suitability_score": min(1.0, max(0.0, suitability_score)),
            "network_compatibility": min(1.0, (network_density + network_clustering) / 2),
            "objective_alignment": min(1.0, suitability_score * 1.2)
        }
    
    def _apply_constraints(
        self, 
        recommendations: List[SmartRecommendation], 
        constraints: Dict[str, Any]
    ) -> List[SmartRecommendation]:
        """Apply constraints to filter and modify recommendations"""
        
        filtered_recommendations = []
        
        max_budget = constraints.get("max_budget", float('inf'))
        blacklisted_targets = constraints.get("blacklisted_targets", [])
        priority_filter = constraints.get("min_priority")
        
        for rec in recommendations:
            # Budget constraint
            if rec.implementation_cost > max_budget:
                continue
            
            # Target blacklist constraint
            if any(target in rec.description for target in blacklisted_targets):
                continue
            
            # Priority constraint
            if priority_filter:
                priority_values = {
                    RecommendationPriority.LOW: 1,
                    RecommendationPriority.MEDIUM: 2,
                    RecommendationPriority.HIGH: 3,
                    RecommendationPriority.CRITICAL: 4
                }
                if priority_values.get(rec.priority, 0) < priority_values.get(priority_filter, 0):
                    continue
            
            filtered_recommendations.append(rec)
        
        return filtered_recommendations
    
    def _rank_recommendations(
        self, 
        recommendations: List[SmartRecommendation], 
        context: Dict[str, Any]
    ) -> List[SmartRecommendation]:
        """Rank recommendations by effectiveness and feasibility"""
        
        def calculate_ranking_score(rec: SmartRecommendation) -> float:
            # Base score from confidence
            score = rec.confidence_score * 0.4
            
            # Priority boost
            priority_multipliers = {
                RecommendationPriority.CRITICAL: 1.3,
                RecommendationPriority.HIGH: 1.2,
                RecommendationPriority.MEDIUM: 1.0,
                RecommendationPriority.LOW: 0.8
            }
            score *= priority_multipliers.get(rec.priority, 1.0)
            
            # Cost efficiency (lower cost = higher score)
            if rec.implementation_cost > 0:
                cost_efficiency = min(1.0, 100.0 / rec.implementation_cost)
                score += cost_efficiency * 0.2
            
            # Risk assessment (lower risk = higher score)
            avg_risk = sum(rec.risk_assessment.values()) / max(1, len(rec.risk_assessment))
            risk_score = max(0.0, 1.0 - avg_risk)
            score += risk_score * 0.2
            
            # Expected outcomes boost
            avg_outcome = sum(rec.expected_outcomes.values()) / max(1, len(rec.expected_outcomes))
            score += avg_outcome * 0.2
            
            return score
        
        # Calculate scores and sort
        scored_recommendations = [(rec, calculate_ranking_score(rec)) for rec in recommendations]
        scored_recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [rec for rec, score in scored_recommendations]


# Factory function  
def create_smart_recommendation_engine() -> SmartRecommendationEngine:
    """Create smart recommendation engine instance"""
    return SmartRecommendationEngine() 