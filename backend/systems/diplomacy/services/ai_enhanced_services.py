"""
AI-Enhanced Diplomacy Services

This module integrates AI decision-making capabilities into the core diplomacy services,
providing intelligent diplomatic analysis, automatic decision recommendations, and
autonomous faction behavior.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import logging
import traceback

from ..ai.decision_engine import DiplomaticDecisionEngine, DecisionContext, DecisionOutcome
from ..ai.strategic_analyzer import StrategicAnalyzer
from ..ai.relationship_evaluator import RelationshipEvaluator
from ..ai.personality_integration import PersonalityIntegrator
from ..ai.goal_system import FactionGoalManager
from .core_services import TensionManagementService, TreatyManagementService, NegotiationService
from ..models.core_models import Treaty, TreatyType, DiplomaticStatus, DiplomaticEvent

# Configure detailed logging
logger = logging.getLogger(__name__)

class DiplomacyAIError(Exception):
    """Base exception for diplomacy AI errors"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code or "DIPLOMACY_AI_ERROR"
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class FactionDataError(DiplomacyAIError):
    """Error when faction data is unavailable or invalid"""
    def __init__(self, faction_id: UUID, message: str = None):
        super().__init__(
            message or f"Faction data error for faction {faction_id}",
            "FACTION_DATA_ERROR",
            {"faction_id": str(faction_id)}
        )

class AIProcessingError(DiplomacyAIError):
    """Error during AI decision processing"""
    def __init__(self, process: str, message: str, details: Dict[str, Any] = None):
        super().__init__(
            f"AI processing error in {process}: {message}",
            "AI_PROCESSING_ERROR",
            {"process": process, **(details or {})}
        )


def log_performance(func):
    """Decorator to log performance metrics for AI operations"""
    def wrapper(self, *args, **kwargs):
        start_time = datetime.utcnow()
        operation_name = func.__name__
        
        try:
            logger.info(f"Starting AI operation: {operation_name}")
            result = func(self, *args, **kwargs)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"AI operation completed: {operation_name} in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"AI operation failed: {operation_name} after {duration:.2f}s - {str(e)}")
            raise
            
    return wrapper


class AIEnhancedTreatyService(TreatyManagementService):
    """Treaty service enhanced with AI decision-making capabilities."""
    
    def __init__(self):
        super().__init__()
        try:
            self.decision_engine = DiplomaticDecisionEngine()
            self.strategic_analyzer = StrategicAnalyzer()
            self.relationship_evaluator = RelationshipEvaluator()
            self.personality_integrator = PersonalityIntegrator()
            logger.info("AI Treaty Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Treaty Service: {e}")
            logger.debug(f"Initialization error details: {traceback.format_exc()}")
            raise AIProcessingError("initialization", str(e))
    
    @log_performance
    def evaluate_treaty_proposal(self, faction_id: UUID, target_faction_id: UUID, 
                                treaty_type: TreatyType, terms: Dict[str, Any]) -> Dict[str, Any]:
        """AI evaluation of a treaty proposal from the target faction's perspective."""
        operation_id = f"eval_{faction_id}_{target_faction_id}_{treaty_type.value}"
        
        try:
            logger.info(f"Evaluating treaty proposal: {operation_id}")
            logger.debug(f"Treaty terms: {terms}")
            
            # Validate inputs
            if not faction_id or not target_faction_id:
                raise DiplomacyAIError("Invalid faction IDs provided", "INVALID_INPUT")
            
            if faction_id == target_faction_id:
                raise DiplomacyAIError("Cannot evaluate treaty with self", "INVALID_INPUT")
            
            # Build decision context with error handling
            try:
                context = DecisionContext(
                    faction_id=target_faction_id,  # Evaluating from target's perspective
                    target_faction_id=faction_id,
                    urgency_level=0.5,
                    confidence_threshold=0.6
                )
                logger.debug(f"Decision context created for {operation_id}")
            except Exception as e:
                logger.error(f"Failed to create decision context for {operation_id}: {e}")
                raise AIProcessingError("decision_context_creation", str(e))
            
            # Get AI evaluation with fallback
            try:
                evaluation = self.decision_engine.evaluate_treaty_proposal(context)
                logger.debug(f"AI evaluation completed for {operation_id}")
            except Exception as e:
                logger.warning(f"AI evaluation failed for {operation_id}, using fallback: {e}")
                evaluation = self._create_fallback_evaluation()
            
            # Get strategic analysis with error handling
            power_balance = None
            relationship_analysis = None
            
            try:
                power_balance = self.strategic_analyzer.analyze_power_balance(target_faction_id, faction_id)
                logger.debug(f"Power balance analysis completed for {operation_id}")
            except Exception as e:
                logger.warning(f"Power balance analysis failed for {operation_id}: {e}")
            
            try:
                relationship_analysis = self.relationship_evaluator.evaluate_relationship(target_faction_id, faction_id)
                logger.debug(f"Relationship analysis completed for {operation_id}")
            except Exception as e:
                logger.warning(f"Relationship analysis failed for {operation_id}: {e}")
            
            # Calculate acceptance probability with robust error handling
            try:
                acceptance_factors = {
                    "power_balance_advantage": power_balance.relative_power_score if power_balance else 0.5,
                    "relationship_quality": (relationship_analysis.trust_level.value / 100) if relationship_analysis else 0.5,
                    "strategic_benefit": evaluation.success_probability if hasattr(evaluation, 'success_probability') else 0.5,
                    "personality_alignment": self._get_personality_compatibility(target_faction_id, faction_id),
                    "goal_alignment": self._assess_goal_alignment(target_faction_id, faction_id, treaty_type)
                }
                
                # Weighted calculation with validation
                weights = {
                    "power_balance_advantage": 0.2,
                    "relationship_quality": 0.25, 
                    "strategic_benefit": 0.3,
                    "personality_alignment": 0.15,
                    "goal_alignment": 0.1
                }
                
                acceptance_probability = sum(
                    acceptance_factors.get(factor, 0.5) * weights[factor] 
                    for factor in weights
                )
                
                # Ensure probability is within valid range
                acceptance_probability = max(0.0, min(1.0, acceptance_probability))
                
                logger.info(f"Treaty evaluation completed for {operation_id}: {acceptance_probability:.2f} acceptance probability")
                
            except Exception as e:
                logger.error(f"Failed to calculate acceptance probability for {operation_id}: {e}")
                acceptance_probability = 0.5
                acceptance_factors = {factor: 0.5 for factor in ["power_balance_advantage", "relationship_quality", "strategic_benefit", "personality_alignment", "goal_alignment"]}
            
            # Build comprehensive response
            result = {
                "operation_id": operation_id,
                "faction_id": str(target_faction_id),
                "evaluating_proposal_from": str(faction_id),
                "treaty_type": treaty_type.value,
                "acceptance_probability": round(acceptance_probability, 2),
                "recommendation": "accept" if acceptance_probability > 0.6 else "reject",
                "confidence": getattr(evaluation, 'confidence', 0.5),
                "reasoning": getattr(evaluation, 'reasoning', "Standard diplomatic evaluation"),
                "strategic_analysis": {
                    "power_balance": power_balance.analysis_summary if power_balance else "Analysis unavailable",
                    "relationship_status": relationship_analysis.current_status.value if relationship_analysis else "Unknown",
                    "key_factors": getattr(evaluation, 'supporting_factors', ["Standard evaluation factors"])
                },
                "acceptance_factors": acceptance_factors,
                "risk_assessment": {
                    "risk_level": getattr(evaluation, 'risk_factors', ["Moderate risk"]),
                    "potential_consequences": getattr(evaluation, 'opposing_factors', ["Standard consequences"])
                },
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "ai_system_version": "1.0.0",
                    "processing_errors": []  # Could track non-fatal errors
                }
            }
            
            return result
            
        except DiplomacyAIError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in treaty evaluation {operation_id}: {e}")
            logger.debug(f"Treaty evaluation error traceback: {traceback.format_exc()}")
            raise AIProcessingError("treaty_evaluation", str(e), {
                "operation_id": operation_id,
                "faction_id": str(faction_id),
                "target_faction_id": str(target_faction_id),
                "treaty_type": treaty_type.value
            })
    
    def _create_fallback_evaluation(self) -> object:
        """Create a fallback evaluation object when AI processing fails"""
        class FallbackEvaluation:
            def __init__(self):
                self.success_probability = 0.5
                self.confidence = 0.3
                self.reasoning = "Fallback evaluation - AI processing unavailable"
                self.supporting_factors = ["Basic diplomatic assessment"]
                self.risk_factors = ["Unknown risks due to AI unavailability"]
                self.opposing_factors = ["Standard diplomatic concerns"]
        
        logger.info("Using fallback evaluation due to AI processing failure")
        return FallbackEvaluation()
    
    def _get_personality_compatibility(self, faction_a_id: UUID, faction_b_id: UUID) -> float:
        """Calculate personality compatibility between factions."""
        try:
            logger.debug(f"Calculating personality compatibility: {faction_a_id} <-> {faction_b_id}")
            
            # Get faction data from the faction system
            from backend.systems.faction.services.services import FactionService
            from backend.infrastructure.database.database_service import get_database_session
            
            with get_database_session() as db:
                faction_service = FactionService(db)
                
                # Get both factions with error handling
                try:
                    faction_a_data = faction_service.business_service.get_faction_by_id(faction_a_id)
                    faction_b_data = faction_service.business_service.get_faction_by_id(faction_b_id)
                except Exception as e:
                    logger.warning(f"Failed to retrieve faction data for compatibility analysis: {e}")
                    raise FactionDataError(faction_a_id, f"Could not retrieve faction data: {e}")
                
                if not faction_a_data:
                    logger.warning(f"Faction {faction_a_id} not found for compatibility analysis")
                    raise FactionDataError(faction_a_id, "Faction not found")
                
                if not faction_b_data:
                    logger.warning(f"Faction {faction_b_id} not found for compatibility analysis")
                    raise FactionDataError(faction_b_id, "Faction not found")
                
                # Get hidden attributes for both factions
                try:
                    attrs_a = faction_a_data.get_hidden_attributes()
                    attrs_b = faction_b_data.get_hidden_attributes()
                    
                    # Validate attributes
                    required_attrs = ['hidden_integrity', 'hidden_discipline', 'hidden_pragmatism', 'hidden_impulsivity']
                    for attr in required_attrs:
                        if attr not in attrs_a or attr not in attrs_b:
                            logger.warning(f"Missing required attribute {attr} for compatibility calculation")
                            return 0.5
                    
                except Exception as e:
                    logger.error(f"Failed to get faction attributes for compatibility: {e}")
                    return 0.5
                
                # Calculate compatibility based on personality alignment
                try:
                    # Similar values in key attributes = higher compatibility
                    integrity_compat = 1.0 - abs(attrs_a['hidden_integrity'] - attrs_b['hidden_integrity']) / 10.0
                    discipline_compat = 1.0 - abs(attrs_a['hidden_discipline'] - attrs_b['hidden_discipline']) / 10.0
                    pragmatism_compat = 1.0 - abs(attrs_a['hidden_pragmatism'] - attrs_b['hidden_pragmatism']) / 10.0
                    
                    # Impulsivity differences can be complementary (not just similar)
                    impulsivity_diff = abs(attrs_a['hidden_impulsivity'] - attrs_b['hidden_impulsivity'])
                    impulsivity_compat = max(0.5, 1.0 - impulsivity_diff / 15.0)  # More forgiving
                    
                    # Weighted average
                    compatibility = (
                        integrity_compat * 0.3 +
                        discipline_compat * 0.25 +
                        pragmatism_compat * 0.25 +
                        impulsivity_compat * 0.2
                    )
                    
                    # Ensure result is in valid range
                    result = max(0.1, min(0.9, compatibility))
                    
                    logger.debug(f"Personality compatibility calculated: {result:.2f} for {faction_a_id} <-> {faction_b_id}")
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in compatibility calculation: {e}")
                    return 0.5
                
        except FactionDataError:
            # Re-raise faction data errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in personality compatibility calculation: {e}")
            logger.debug(f"Compatibility error traceback: {traceback.format_exc()}")
            return 0.5  # Safe fallback
    
    def _assess_goal_alignment(self, faction_a_id: UUID, faction_b_id: UUID, treaty_type: TreatyType) -> float:
        """Assess how well a treaty type aligns with faction goals."""
        try:
            # Get faction data to assess goal alignment
            from backend.systems.faction.services.services import FactionService
            from backend.infrastructure.database.database_service import get_database_session
            
            with get_database_session() as db:
                faction_service = FactionService(db)
                
                faction_a_data = faction_service.business_service.get_faction_by_id(faction_a_id)
                faction_b_data = faction_service.business_service.get_faction_by_id(faction_b_id)
                
                if not faction_a_data or not faction_b_data:
                    # Default alignment based on treaty type
                    alignment_map = {
                        TreatyType.TRADE: 0.8,
                        TreatyType.ALLIANCE: 0.6,
                        TreatyType.NON_AGGRESSION: 0.7,
                        TreatyType.MUTUAL_DEFENSE: 0.5
                    }
                    return alignment_map.get(treaty_type, 0.5)
                
                # Get faction attributes
                attrs_a = faction_a_data.get_hidden_attributes()
                attrs_b = faction_b_data.get_hidden_attributes()
                
                # Calculate goal alignment based on faction personalities and treaty type
                if treaty_type == TreatyType.TRADE:
                    # Trade benefits pragmatic, ambitious factions
                    a_trade_affinity = (attrs_a['hidden_pragmatism'] + attrs_a['hidden_ambition']) / 20.0
                    b_trade_affinity = (attrs_b['hidden_pragmatism'] + attrs_b['hidden_ambition']) / 20.0
                    return (a_trade_affinity + b_trade_affinity) / 2
                    
                elif treaty_type == TreatyType.ALLIANCE:
                    # Alliances work better with disciplined, integrity-based factions
                    a_alliance_affinity = (attrs_a['hidden_discipline'] + attrs_a['hidden_integrity']) / 20.0
                    b_alliance_affinity = (attrs_b['hidden_discipline'] + attrs_b['hidden_integrity']) / 20.0
                    return (a_alliance_affinity + b_alliance_affinity) / 2
                    
                elif treaty_type == TreatyType.NON_AGGRESSION:
                    # Non-aggression suits cautious, low-aggression factions
                    a_peace_affinity = (attrs_a['hidden_integrity'] + (10 - attrs_a['hidden_impulsivity'])) / 20.0
                    b_peace_affinity = (attrs_b['hidden_integrity'] + (10 - attrs_b['hidden_impulsivity'])) / 20.0
                    return (a_peace_affinity + b_peace_affinity) / 2
                    
                elif treaty_type == TreatyType.MUTUAL_DEFENSE:
                    # Mutual defense needs loyal, resilient factions
                    a_defense_affinity = (attrs_a['hidden_integrity'] + attrs_a['hidden_resilience']) / 20.0
                    b_defense_affinity = (attrs_b['hidden_integrity'] + attrs_b['hidden_resilience']) / 20.0
                    return (a_defense_affinity + b_defense_affinity) / 2
                
                return 0.5  # Default if treaty type not recognized
                
        except Exception as e:
            logger.warning(f"Failed to assess goal alignment: {e}")
            # Fallback to basic alignment map
            alignment_map = {
                TreatyType.TRADE: 0.8,
                TreatyType.ALLIANCE: 0.6,
                TreatyType.NON_AGGRESSION: 0.7,
                TreatyType.MUTUAL_DEFENSE: 0.5
            }
            return alignment_map.get(treaty_type, 0.5)
    
    def suggest_optimal_treaty_terms(self, proposing_faction_id: UUID, target_faction_id: UUID, 
                                   treaty_type: TreatyType) -> Dict[str, Any]:
        """AI-generated optimal treaty terms to maximize acceptance probability."""
        context = DecisionContext(
            faction_id=proposing_faction_id,
            target_faction_id=target_faction_id
        )
        
        # Get relationship and strategic analysis
        relationship = self.relationship_evaluator.evaluate_relationship(proposing_faction_id, target_faction_id)
        power_balance = self.strategic_analyzer.analyze_power_balance(proposing_faction_id, target_faction_id)
        
        # Generate base terms
        base_terms = self._generate_base_treaty_terms(treaty_type)
        
        # AI optimization based on target faction preferences
        optimized_terms = self._optimize_terms_for_faction(
            base_terms, target_faction_id, relationship, power_balance
        )
        
        return {
            "proposing_faction": str(proposing_faction_id),
            "target_faction": str(target_faction_id),
            "treaty_type": treaty_type.value,
            "optimized_terms": optimized_terms,
            "optimization_reasoning": [
                "Terms adjusted based on target faction's diplomatic history",
                "Economic terms balanced for mutual benefit",
                "Duration set to match faction's commitment preferences",
                "Security clauses aligned with faction's risk tolerance"
            ],
            "expected_acceptance_probability": self._estimate_acceptance_with_terms(
                proposing_faction_id, target_faction_id, treaty_type, optimized_terms
            )
        }
    
    def auto_generate_treaty_proposal(self, faction_id: UUID) -> Optional[Dict[str, Any]]:
        """Automatically generate the best treaty proposal for a faction."""
        # Get all possible diplomatic decisions
        decisions = self.decision_engine.evaluate_all_decisions(faction_id)
        
        # Filter for treaty proposals
        treaty_decisions = [d for d in decisions if d.decision_type.value == "treaty_proposal"]
        
        if not treaty_decisions:
            return None
        
        # Get the highest priority treaty proposal
        best_proposal = max(treaty_decisions, key=lambda d: d.priority)
        
        if best_proposal.confidence < 0.6:
            return None
        
        # Generate optimal terms
        optimal_terms = self.suggest_optimal_treaty_terms(
            faction_id, 
            best_proposal.proposal_details.get("target_faction_id"),
            TreatyType(best_proposal.proposal_details.get("treaty_type"))
        )
        
        return {
            "auto_generated": True,
            "faction_id": str(faction_id),
            "proposal": optimal_terms,
            "ai_confidence": best_proposal.confidence,
            "priority_score": best_proposal.priority,
            "reasoning": best_proposal.reasoning,
            "suggested_timing": best_proposal.suggested_timing.value if best_proposal.suggested_timing else "immediate"
        }
    
    def _generate_base_treaty_terms(self, treaty_type: TreatyType) -> Dict[str, Any]:
        """Generate base treaty terms for a given type."""
        base_terms = {
            "duration_years": 5,
            "renewable": True,
            "termination_notice_days": 30
        }
        
        if treaty_type == TreatyType.TRADE:
            base_terms.update({
                "tariff_reduction": 0.15,
                "trade_volume_target": "increased by 25%",
                "exclusive_goods": [],
                "trade_route_protection": True
            })
        elif treaty_type == TreatyType.ALLIANCE:
            base_terms.update({
                "military_support": True,
                "defensive_alliance": True,
                "offensive_coordination": False,
                "intelligence_sharing": True,
                "joint_military_exercises": True
            })
        elif treaty_type == TreatyType.NON_AGGRESSION:
            base_terms.update({
                "no_military_action": True,
                "border_respect": True,
                "neutral_territory_access": False,
                "third_party_conflicts": "neutral stance"
            })
        elif treaty_type == TreatyType.MUTUAL_DEFENSE:
            base_terms.update({
                "automatic_defense": True,
                "response_time_hours": 72,
                "minimum_support_level": "full military support",
                "intelligence_sharing": True
            })
        
        return base_terms
    
    def _optimize_terms_for_faction(self, base_terms: Dict[str, Any], target_faction_id: UUID,
                                  relationship: Any, power_balance: Any) -> Dict[str, Any]:
        """Optimize treaty terms for target faction preferences."""
        optimized = base_terms.copy()
        
        # Adjust based on power balance
        if power_balance and power_balance.relative_power_score < 0.5:
            # We're weaker, offer more attractive terms
            if "tariff_reduction" in optimized:
                optimized["tariff_reduction"] = min(0.25, optimized["tariff_reduction"] + 0.05)
            if "duration_years" in optimized:
                optimized["duration_years"] = max(3, optimized["duration_years"] - 1)
        
        # Adjust based on relationship quality
        if relationship and hasattr(relationship, 'trust_level'):
            if relationship.trust_level.value < 50:
                # Low trust, add verification mechanisms
                optimized["verification_mechanisms"] = True
                optimized["regular_reviews"] = True
                if "duration_years" in optimized:
                    optimized["duration_years"] = min(3, optimized["duration_years"])
        
        return optimized
    
    def _estimate_acceptance_with_terms(self, proposing_faction_id: UUID, target_faction_id: UUID,
                                      treaty_type: TreatyType, terms: Dict[str, Any]) -> float:
        """Estimate acceptance probability with specific terms."""
        # Base acceptance from treaty evaluation
        base_eval = self.evaluate_treaty_proposal(proposing_faction_id, target_faction_id, treaty_type, terms)
        base_probability = base_eval.get("acceptance_probability", 0.5)
        
        # Term-based adjustments
        term_bonus = 0.0
        
        # More attractive economic terms increase acceptance
        if "tariff_reduction" in terms and terms["tariff_reduction"] > 0.15:
            term_bonus += 0.05
        
        # Shorter commitments are less risky
        if "duration_years" in terms and terms["duration_years"] <= 3:
            term_bonus += 0.03
        
        # Verification mechanisms increase trust
        if terms.get("verification_mechanisms"):
            term_bonus += 0.02
        
        return min(1.0, base_probability + term_bonus)


class AIEnhancedNegotiationService(NegotiationService):
    """Negotiation service enhanced with AI-powered dialogue and strategy."""
    
    def __init__(self):
        super().__init__()
        self.decision_engine = DiplomaticDecisionEngine()
        self.personality_integrator = PersonalityIntegrator()
    
    def generate_ai_negotiation_response(self, negotiation_id: UUID, responding_faction_id: UUID,
                                       incoming_offer: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered negotiation response based on faction personality and goals."""
        # Analyze the incoming offer
        offer_analysis = self._analyze_negotiation_offer(responding_faction_id, incoming_offer)
        
        # Generate personality-appropriate response
        response_style = self.personality_integrator.get_negotiation_style(responding_faction_id)
        
        # Determine response type
        if offer_analysis["attractiveness"] > 0.7:
            response_type = "accept"
        elif offer_analysis["attractiveness"] > 0.4:
            response_type = "counter_offer"
        else:
            response_type = "reject"
        
        response = {
            "negotiation_id": str(negotiation_id),
            "responding_faction": str(responding_faction_id),
            "response_type": response_type,
            "offer_analysis": offer_analysis,
            "response_style": response_style,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        if response_type == "accept":
            response.update({
                "message": self._generate_acceptance_message(response_style),
                "conditions": self._generate_acceptance_conditions(responding_faction_id, incoming_offer)
            })
        elif response_type == "counter_offer":
            response.update({
                "message": self._generate_counter_offer_message(response_style),
                "counter_terms": self._generate_counter_terms(responding_faction_id, incoming_offer, offer_analysis),
                "justification": self._generate_counter_justification(offer_analysis)
            })
        else:  # reject
            response.update({
                "message": self._generate_rejection_message(response_style),
                "rejection_reasons": offer_analysis["concerns"],
                "alternative_suggestions": self._generate_alternative_suggestions(responding_faction_id)
            })
        
        return response
    
    def _analyze_negotiation_offer(self, faction_id: UUID, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an incoming negotiation offer from faction's perspective."""
        # Economic analysis
        economic_value = self._assess_economic_value(faction_id, offer)
        
        # Strategic analysis  
        strategic_value = self._assess_strategic_value(faction_id, offer)
        
        # Risk analysis
        risk_level = self._assess_offer_risks(faction_id, offer)
        
        # Overall attractiveness
        attractiveness = (economic_value * 0.4 + strategic_value * 0.4 + (1 - risk_level) * 0.2)
        
        return {
            "attractiveness": attractiveness,
            "economic_value": economic_value,
            "strategic_value": strategic_value,
            "risk_level": risk_level,
            "key_benefits": self._identify_key_benefits(offer),
            "concerns": self._identify_concerns(offer, risk_level),
            "improvement_areas": self._identify_improvement_areas(offer)
        }
    
    def _assess_economic_value(self, faction_id: UUID, offer: Dict[str, Any]) -> float:
        """Assess economic value of an offer."""
        value = 0.5  # Base neutral value
        
        # Trade terms
        if "tariff_reduction" in offer:
            value += min(0.3, offer["tariff_reduction"] * 0.5)
        
        # Resource sharing
        if "resource_sharing" in offer and offer["resource_sharing"]:
            value += 0.1
        
        # Economic cooperation
        if "trade_volume_target" in offer:
            # Extract percentage increase if it's a string like "increased by 25%"
            target = offer["trade_volume_target"]
            if isinstance(target, str) and "%" in target:
                try:
                    percent = int(target.split("%")[0].split()[-1])
                    value += min(0.2, percent / 100)
                except:
                    pass
        
        return min(1.0, value)
    
    def _assess_strategic_value(self, faction_id: UUID, offer: Dict[str, Any]) -> float:
        """Assess strategic value of an offer."""
        value = 0.5  # Base neutral value
        
        # Military cooperation
        if offer.get("military_support"):
            value += 0.2
        
        # Intelligence sharing
        if offer.get("intelligence_sharing"):
            value += 0.1
        
        # Defensive agreements
        if offer.get("defensive_alliance") or offer.get("automatic_defense"):
            value += 0.15
        
        # Territory or access rights
        if offer.get("territory_access") or offer.get("neutral_territory_access"):
            value += 0.1
        
        return min(1.0, value)
    
    def _assess_offer_risks(self, faction_id: UUID, offer: Dict[str, Any]) -> float:
        """Assess risks associated with an offer."""
        risk = 0.3  # Base risk level
        
        # Long commitments increase risk
        if "duration_years" in offer and offer["duration_years"] > 5:
            risk += 0.1
        
        # Automatic military commitments increase risk
        if offer.get("automatic_defense") or offer.get("offensive_coordination"):
            risk += 0.2
        
        # Exclusive agreements increase dependency risk
        if offer.get("exclusive_goods") or offer.get("exclusive_alliance"):
            risk += 0.15
        
        # Lack of escape clauses increases risk
        if not offer.get("termination_notice_days") or offer.get("termination_notice_days", 0) > 90:
            risk += 0.1
        
        return min(1.0, risk)
    
    def _identify_key_benefits(self, offer: Dict[str, Any]) -> List[str]:
        """Identify key benefits of an offer."""
        benefits = []
        
        if offer.get("tariff_reduction", 0) > 0.1:
            benefits.append(f"Significant tariff reduction of {offer['tariff_reduction']*100:.0f}%")
        
        if offer.get("military_support"):
            benefits.append("Military support and cooperation")
        
        if offer.get("intelligence_sharing"):
            benefits.append("Intelligence and information sharing")
        
        if offer.get("trade_route_protection"):
            benefits.append("Trade route protection and security")
        
        return benefits
    
    def _identify_concerns(self, offer: Dict[str, Any], risk_level: float) -> List[str]:
        """Identify concerns with an offer."""
        concerns = []
        
        if risk_level > 0.6:
            concerns.append("High risk level due to extensive commitments")
        
        if offer.get("duration_years", 0) > 7:
            concerns.append("Very long commitment period")
        
        if offer.get("automatic_defense") and not offer.get("defensive_limits"):
            concerns.append("Unlimited military obligations")
        
        if not offer.get("verification_mechanisms"):
            concerns.append("Lack of verification and monitoring mechanisms")
        
        return concerns
    
    def _identify_improvement_areas(self, offer: Dict[str, Any]) -> List[str]:
        """Identify areas where the offer could be improved."""
        improvements = []
        
        if "verification_mechanisms" not in offer:
            improvements.append("Add verification and monitoring mechanisms")
        
        if offer.get("duration_years", 0) > 5:
            improvements.append("Reduce commitment duration")
        
        if "termination_notice_days" not in offer:
            improvements.append("Add clear termination procedures")
        
        if not offer.get("regular_reviews"):
            improvements.append("Include regular review periods")
        
        return improvements
    
    def _generate_acceptance_message(self, response_style: Dict[str, Any]) -> str:
        """Generate personality-appropriate acceptance message."""
        if response_style.get("diplomatic_approach") == "aggressive":
            return "This proposal serves our interests. We accept these terms."
        elif response_style.get("diplomatic_approach") == "cautious":
            return "After careful consideration, we find these terms acceptable and agree to proceed."
        else:  # balanced/cooperative
            return "We are pleased with this proposal and look forward to a mutually beneficial agreement."
    
    def _generate_counter_offer_message(self, response_style: Dict[str, Any]) -> str:
        """Generate personality-appropriate counter-offer message."""
        if response_style.get("diplomatic_approach") == "aggressive":
            return "The proposal has merit but requires significant modifications to be acceptable."
        elif response_style.get("diplomatic_approach") == "cautious":
            return "We appreciate the proposal but have concerns that must be addressed for our agreement."
        else:  # balanced/cooperative
            return "We see the value in this proposal and would like to suggest some adjustments for mutual benefit."
    
    def _generate_rejection_message(self, response_style: Dict[str, Any]) -> str:
        """Generate personality-appropriate rejection message."""
        if response_style.get("diplomatic_approach") == "aggressive":
            return "This proposal is unacceptable in its current form."
        elif response_style.get("diplomatic_approach") == "cautious":
            return "We must respectfully decline this proposal due to unacceptable risks and concerns."
        else:  # balanced/cooperative
            return "While we appreciate the effort, we cannot accept this proposal as currently structured."
    
    def _generate_acceptance_conditions(self, faction_id: UUID, offer: Dict[str, Any]) -> List[str]:
        """Generate conditions for acceptance."""
        conditions = []
        
        if not offer.get("verification_mechanisms"):
            conditions.append("Implementation of verification mechanisms")
        
        if not offer.get("regular_reviews"):
            conditions.append("Quarterly review meetings")
        
        return conditions
    
    def _generate_counter_terms(self, faction_id: UUID, original_offer: Dict[str, Any], 
                              analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate counter-offer terms."""
        counter_terms = original_offer.copy()
        
        # Reduce duration if too long
        if counter_terms.get("duration_years", 0) > 5:
            counter_terms["duration_years"] = 5
        
        # Add verification if missing
        if not counter_terms.get("verification_mechanisms"):
            counter_terms["verification_mechanisms"] = True
            counter_terms["regular_reviews"] = True
        
        # Adjust economic terms based on analysis
        if analysis["economic_value"] < 0.5 and "tariff_reduction" in counter_terms:
            counter_terms["tariff_reduction"] = min(0.25, counter_terms["tariff_reduction"] + 0.05)
        
        return counter_terms
    
    def _generate_counter_justification(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate justification for counter-offer."""
        justifications = []
        
        if analysis["risk_level"] > 0.6:
            justifications.append("Risk mitigation through improved terms")
        
        if analysis["economic_value"] < 0.5:
            justifications.append("Economic balance adjustment for mutual benefit")
        
        justifications.extend(analysis["improvement_areas"])
        
        return justifications
    
    def _generate_alternative_suggestions(self, faction_id: UUID) -> List[str]:
        """Generate alternative negotiation suggestions."""
        return [
            "Consider a shorter-term agreement to build trust",
            "Start with a limited trade agreement before broader cooperation",
            "Include third-party mediation for complex terms"
        ]


# Factory functions for AI-enhanced services
def create_ai_enhanced_treaty_service() -> AIEnhancedTreatyService:
    """Create AI-enhanced treaty service."""
    return AIEnhancedTreatyService()

def create_ai_enhanced_negotiation_service() -> AIEnhancedNegotiationService:
    """Create AI-enhanced negotiation service."""
    return AIEnhancedNegotiationService() 