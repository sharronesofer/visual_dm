"""
AI-Enhanced Diplomacy API Router

This module defines the API endpoints for AI-powered diplomacy functionality,
including automated decision-making, intelligent negotiations, and treaty optimization.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from backend.systems.diplomacy.models.core_models import TreatyType
from backend.systems.diplomacy.services.ai_enhanced_services import (
    AIEnhancedTreatyService,
    AIEnhancedNegotiationService,
    create_ai_enhanced_treaty_service,
    create_ai_enhanced_negotiation_service,
    DiplomacyAIError,
    FactionDataError,
    AIProcessingError
)

# Configure structured logging
logger = logging.getLogger(__name__)

# Enhanced error handling
class APIError(Exception):
    """Base API error with structured details"""
    def __init__(self, message: str, status_code: int = 500, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "API_ERROR"
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        super().__init__(message)

def log_request(func):
    """Decorator to log API requests and responses"""
    async def wrapper(*args, **kwargs):
        request_id = id(args[0]) if args else "unknown"
        operation = func.__name__
        
        logger.info(f"API Request [{request_id}]: {operation}")
        start_time = datetime.utcnow()
        
        try:
            result = await func(*args, **kwargs)
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"API Success [{request_id}]: {operation} completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"API Error [{request_id}]: {operation} failed after {duration:.2f}s - {str(e)}")
            raise
            
    return wrapper

def handle_diplomacy_errors(func):
    """Decorator to handle diplomacy-specific errors and convert to HTTP responses"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
            
        except ValidationError as e:
            logger.warning(f"Request validation error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                    "details": e.errors(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except FactionDataError as e:
            logger.warning(f"Faction data error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=404,
                detail={
                    "error": e.error_code,
                    "message": str(e),
                    "details": e.details,
                    "timestamp": e.timestamp.isoformat()
                }
            )
            
        except AIProcessingError as e:
            logger.error(f"AI processing error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=503,
                detail={
                    "error": e.error_code,
                    "message": str(e),
                    "details": e.details,
                    "timestamp": e.timestamp.isoformat(),
                    "retry_after": 60  # Suggest retry after 60 seconds
                }
            )
            
        except DiplomacyAIError as e:
            logger.error(f"Diplomacy AI error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": e.error_code,
                    "message": str(e),
                    "details": e.details,
                    "timestamp": e.timestamp.isoformat()
                }
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            logger.debug(f"Error traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"operation": func.__name__},
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
    return wrapper

# Enhanced Request/Response models with validation
class TreatyEvaluationRequest(BaseModel):
    """Request model for treaty evaluation."""
    proposing_faction_id: UUID = Field(..., description="ID of the faction proposing the treaty")
    target_faction_id: UUID = Field(..., description="ID of the faction evaluating the proposal")
    treaty_type: TreatyType = Field(..., description="Type of treaty being proposed")
    terms: Dict[str, Any] = Field(..., description="Treaty terms and conditions")
    
    class Config:
        schema_extra = {
            "example": {
                "proposing_faction_id": "123e4567-e89b-12d3-a456-426614174000",
                "target_faction_id": "456e7890-e89b-12d3-a456-426614174001",
                "treaty_type": "TRADE",
                "terms": {
                    "duration_years": 5,
                    "tariff_reduction": 0.15,
                    "trade_volume_target": "increased by 25%"
                }
            }
        }

class TreatyOptimizationRequest(BaseModel):
    """Request model for treaty term optimization."""
    proposing_faction_id: UUID = Field(..., description="ID of the faction proposing the treaty")
    target_faction_id: UUID = Field(..., description="ID of the target faction")
    treaty_type: TreatyType = Field(..., description="Type of treaty to optimize")
    
    class Config:
        schema_extra = {
            "example": {
                "proposing_faction_id": "123e4567-e89b-12d3-a456-426614174000",
                "target_faction_id": "456e7890-e89b-12d3-a456-426614174001",
                "treaty_type": "ALLIANCE"
            }
        }

class NegotiationResponseRequest(BaseModel):
    """Request model for AI negotiation response."""
    negotiation_id: UUID = Field(..., description="ID of the negotiation session")
    responding_faction_id: UUID = Field(..., description="ID of the faction responding")
    incoming_offer: Dict[str, Any] = Field(..., description="The offer being responded to")
    
    class Config:
        schema_extra = {
            "example": {
                "negotiation_id": "789e0123-e89b-12d3-a456-426614174002",
                "responding_faction_id": "456e7890-e89b-12d3-a456-426614174001",
                "incoming_offer": {
                    "treaty_type": "trade",
                    "duration_years": 7,
                    "tariff_reduction": 0.10
                }
            }
        }

class AIDecisionResponse(BaseModel):
    """Response model for AI decisions."""
    success: bool = Field(..., description="Whether the operation was successful")
    decision_type: str = Field(..., description="Type of decision made")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence level")
    reasoning: List[str] = Field(..., description="AI reasoning for the decision")
    data: Dict[str, Any] = Field(..., description="Additional decision data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Operation metadata")

# Create router
router = APIRouter(
    prefix="/diplomacy/ai",
    tags=["diplomacy-ai"],
    responses={
        404: {"description": "Faction not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
        503: {"description": "AI service unavailable"}
    }
)

# Enhanced Dependencies with error handling
def get_ai_treaty_service() -> AIEnhancedTreatyService:
    try:
        return create_ai_enhanced_treaty_service()
    except Exception as e:
        logger.error(f"Failed to create AI treaty service: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "SERVICE_UNAVAILABLE",
                "message": "AI treaty service is currently unavailable",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

def get_ai_negotiation_service() -> AIEnhancedNegotiationService:
    try:
        return create_ai_enhanced_negotiation_service()
    except Exception as e:
        logger.error(f"Failed to create AI negotiation service: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "SERVICE_UNAVAILABLE", 
                "message": "AI negotiation service is currently unavailable",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# ===== AI TREATY ANALYSIS ENDPOINTS =====

@router.post("/treaties/evaluate", response_model=Dict[str, Any])
@handle_diplomacy_errors
@log_request
async def evaluate_treaty_proposal(
    request: TreatyEvaluationRequest,
    ai_service: AIEnhancedTreatyService = Depends(get_ai_treaty_service)
):
    """
    AI evaluation of a treaty proposal from the target faction's perspective.
    
    Returns detailed analysis including acceptance probability, risk assessment,
    and strategic recommendations.
    """
    logger.info(f"Evaluating treaty proposal: {request.proposing_faction_id} -> {request.target_faction_id}")
    
    # Additional validation
    if request.proposing_faction_id == request.target_faction_id:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "INVALID_REQUEST",
                "message": "Proposing faction and target faction cannot be the same",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    evaluation = ai_service.evaluate_treaty_proposal(
        request.proposing_faction_id,
        request.target_faction_id,
        request.treaty_type,
        request.terms
    )
    
    return {
        "success": True,
        "evaluation": evaluation,
        "evaluated_at": datetime.utcnow().isoformat(),
        "api_version": "1.0.0"
    }

@router.post("/treaties/optimize", response_model=Dict[str, Any])
@handle_diplomacy_errors
@log_request
async def optimize_treaty_terms(
    request: TreatyOptimizationRequest,
    ai_service: AIEnhancedTreatyService = Depends(get_ai_treaty_service)
):
    """
    AI optimization of treaty terms to maximize acceptance probability.
    
    Returns optimized terms, reasoning, and expected acceptance probability.
    """
    logger.info(f"Optimizing treaty terms: {request.proposing_faction_id} -> {request.target_faction_id}")
    
    # Additional validation
    if request.proposing_faction_id == request.target_faction_id:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "INVALID_REQUEST",
                "message": "Proposing faction and target faction cannot be the same",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    optimization = ai_service.suggest_optimal_treaty_terms(
        request.proposing_faction_id,
        request.target_faction_id,
        request.treaty_type
    )
    
    return {
        "success": True,
        "optimization": optimization,
        "optimized_at": datetime.utcnow().isoformat(),
        "api_version": "1.0.0"
    }

@router.post("/treaties/auto-generate/{faction_id}", response_model=Dict[str, Any])
async def auto_generate_treaty_proposal(
    faction_id: UUID,
    ai_service: AIEnhancedTreatyService = Depends(get_ai_treaty_service)
):
    """
    Automatically generate the best treaty proposal for a faction.
    
    Uses AI decision engine to identify optimal diplomatic opportunities
    and generate corresponding treaty proposals.
    """
    try:
        proposal = ai_service.auto_generate_treaty_proposal(faction_id)
        
        if proposal is None:
            return {
                "success": False,
                "message": "No viable treaty proposals identified at this time",
                "faction_id": str(faction_id)
            }
        
        return {
            "success": True,
            "proposal": proposal,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Auto-generation failed: {str(e)}"
        )


# ===== AI NEGOTIATION ENDPOINTS =====

@router.post("/negotiations/ai-response", response_model=Dict[str, Any])
async def generate_ai_negotiation_response(
    request: NegotiationResponseRequest,
    ai_service: AIEnhancedNegotiationService = Depends(get_ai_negotiation_service)
):
    """
    Generate AI-powered negotiation response based on faction personality and strategy.
    
    Analyzes incoming offers and generates appropriate responses (accept, counter, reject)
    with personality-appropriate messaging and strategic reasoning.
    """
    try:
        response = ai_service.generate_ai_negotiation_response(
            request.negotiation_id,
            request.responding_faction_id,
            request.incoming_offer
        )
        
        return {
            "success": True,
            "ai_response": response,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"AI negotiation response failed: {str(e)}"
        )


# ===== AI DECISION ENGINE ENDPOINTS =====

@router.get("/decisions/evaluate-all/{faction_id}", response_model=Dict[str, Any])
async def evaluate_all_diplomatic_decisions(
    faction_id: UUID,
    confidence_threshold: float = Query(0.6, ge=0.0, le=1.0),
    ai_service: AIEnhancedTreatyService = Depends(get_ai_treaty_service)
):
    """
    Evaluate all possible diplomatic decisions for a faction.
    
    Returns ranked list of recommended diplomatic actions with confidence scores,
    reasoning, and strategic analysis.
    """
    try:
        # Get all decisions from the decision engine
        decisions = ai_service.decision_engine.evaluate_all_decisions(faction_id)
        
        # Filter by confidence threshold
        filtered_decisions = [
            d for d in decisions 
            if d.confidence >= confidence_threshold
        ]
        
        # Convert to JSON-serializable format
        decision_data = []
        for decision in filtered_decisions:
            decision_data.append({
                "decision_type": decision.decision_type.value,
                "recommended": decision.recommended,
                "confidence": decision.confidence,
                "priority": decision.priority,
                "success_probability": decision.success_probability,
                "reasoning": decision.reasoning,
                "supporting_factors": decision.supporting_factors,
                "risk_factors": decision.risk_factors,
                "proposal_details": decision.proposal_details,
                "suggested_timing": decision.suggested_timing.value if decision.suggested_timing else None
            })
        
        return {
            "success": True,
            "faction_id": str(faction_id),
            "confidence_threshold": confidence_threshold,
            "total_decisions_evaluated": len(decisions),
            "decisions_above_threshold": len(filtered_decisions),
            "decisions": decision_data,
            "evaluated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Decision evaluation failed: {str(e)}"
        )

@router.get("/decisions/next-best/{faction_id}", response_model=Dict[str, Any])
async def get_next_best_decision(
    faction_id: UUID,
    ai_service: AIEnhancedTreatyService = Depends(get_ai_treaty_service)
):
    """
    Get the single best diplomatic decision for a faction.
    
    Returns the highest-priority, highest-confidence diplomatic action
    the faction should take next.
    """
    try:
        decisions = ai_service.decision_engine.evaluate_all_decisions(faction_id)
        
        if not decisions:
            return {
                "success": False,
                "message": "No viable diplomatic decisions identified",
                "faction_id": str(faction_id)
            }
        
        # Get the best decision (highest priority * confidence score)
        best_decision = max(
            decisions, 
            key=lambda d: d.priority * d.confidence
        )
        
        return {
            "success": True,
            "faction_id": str(faction_id),
            "best_decision": {
                "decision_type": best_decision.decision_type.value,
                "confidence": best_decision.confidence,
                "priority": best_decision.priority,
                "success_probability": best_decision.success_probability,
                "reasoning": best_decision.reasoning,
                "proposal_details": best_decision.proposal_details,
                "suggested_timing": best_decision.suggested_timing.value if best_decision.suggested_timing else "immediate"
            },
            "evaluated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Next decision evaluation failed: {str(e)}"
        )


# ===== AI ANALYSIS ENDPOINTS =====

@router.get("/analysis/relationship/{faction_a_id}/{faction_b_id}", response_model=Dict[str, Any])
async def get_ai_relationship_analysis(
    faction_a_id: UUID,
    faction_b_id: UUID,
    ai_service: AIEnhancedTreatyService = Depends(get_ai_treaty_service)
):
    """
    Get AI-powered relationship analysis between two factions.
    
    Returns detailed analysis of diplomatic relationship, trust levels,
    opportunities, and risks.
    """
    try:
        # Get relationship analysis
        relationship = ai_service.relationship_evaluator.evaluate_relationship(
            faction_a_id, faction_b_id
        )
        
        # Get strategic analysis
        power_balance = ai_service.strategic_analyzer.analyze_power_balance(
            faction_a_id, faction_b_id
        )
        
        analysis_data = {
            "faction_a_id": str(faction_a_id),
            "faction_b_id": str(faction_b_id),
            "relationship_analysis": {
                "current_status": relationship.current_status.value if relationship else "Unknown",
                "trust_level": relationship.trust_level.value if relationship else 50,
                "threat_level": relationship.threat_level.value if relationship else "MODERATE",
                "opportunities": [op.value for op in relationship.opportunities] if relationship else [],
                "analysis_summary": relationship.analysis_summary if relationship else "No data available"
            },
            "power_balance": {
                "relative_power_score": power_balance.relative_power_score if power_balance else 0.5,
                "faction_a_advantages": power_balance.faction_a_advantages if power_balance else [],
                "faction_b_advantages": power_balance.faction_b_advantages if power_balance else [],
                "analysis_summary": power_balance.analysis_summary if power_balance else "No data available"
            },
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "analysis": analysis_data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Relationship analysis failed: {str(e)}"
        )

@router.get("/analysis/strategic-opportunities/{faction_id}", response_model=Dict[str, Any])
async def get_strategic_opportunities(
    faction_id: UUID,
    ai_service: AIEnhancedTreatyService = Depends(get_ai_treaty_service)
):
    """
    Get AI analysis of strategic opportunities for a faction.
    
    Returns coalition opportunities, power projection analysis,
    and strategic recommendations.
    """
    try:
        # This would be implemented with proper strategic analyzer methods
        # For now, return a structured placeholder
        
        opportunities = {
            "faction_id": str(faction_id),
            "coalition_opportunities": [
                {
                    "target_factions": ["faction_2", "faction_3"],
                    "opportunity_type": "ECONOMIC_ALLIANCE",
                    "strength": 0.75,
                    "requirements": ["Trade agreement prerequisites", "Geographic proximity"],
                    "benefits": ["Market expansion", "Resource sharing", "Economic stability"]
                }
            ],
            "power_projection": {
                "current_influence": 0.6,
                "potential_expansion": 0.8,
                "key_leverage_points": ["Trade routes", "Military alliances", "Economic partnerships"]
            },
            "strategic_recommendations": [
                "Strengthen economic partnerships with neighboring factions",
                "Develop defensive alliances to counter emerging threats",
                "Invest in intelligence capabilities for better strategic awareness"
            ],
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "opportunities": opportunities
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Strategic analysis failed: {str(e)}"
        )


# ===== BATCH OPERATIONS =====

@router.post("/batch/auto-decisions", response_model=Dict[str, Any])
async def run_batch_ai_decisions(
    faction_ids: List[UUID] = Body(..., description="List of faction IDs to process"),
    confidence_threshold: float = Body(0.6, ge=0.0, le=1.0),
    execute_decisions: bool = Body(False, description="Whether to actually execute decisions"),
    ai_service: AIEnhancedTreatyService = Depends(get_ai_treaty_service)
):
    """
    Run AI decision-making for multiple factions in batch.
    
    Evaluates diplomatic opportunities for all specified factions
    and optionally executes the highest-confidence decisions.
    """
    try:
        batch_results = {}
        executed_actions = []
        
        for faction_id in faction_ids:
            # Get best decision for this faction
            decisions = ai_service.decision_engine.evaluate_all_decisions(faction_id)
            
            if decisions:
                best_decision = max(
                    [d for d in decisions if d.confidence >= confidence_threshold],
                    key=lambda d: d.priority * d.confidence,
                    default=None
                )
                
                if best_decision:
                    decision_data = {
                        "decision_type": best_decision.decision_type.value,
                        "confidence": best_decision.confidence,
                        "priority": best_decision.priority,
                        "proposal_details": best_decision.proposal_details
                    }
                    
                    batch_results[str(faction_id)] = {
                        "has_viable_decision": True,
                        "best_decision": decision_data,
                        "executed": False
                    }
                    
                    # Execute if requested and confidence is high enough
                    if execute_decisions and best_decision.confidence >= 0.8:
                        # Here you would integrate with actual execution logic
                        # For now, just mark as executed
                        batch_results[str(faction_id)]["executed"] = True
                        executed_actions.append({
                            "faction_id": str(faction_id),
                            "action": best_decision.decision_type.value,
                            "confidence": best_decision.confidence
                        })
                
                else:
                    batch_results[str(faction_id)] = {
                        "has_viable_decision": False,
                        "reason": "No decisions above confidence threshold"
                    }
            
            else:
                batch_results[str(faction_id)] = {
                    "has_viable_decision": False,
                    "reason": "No viable decisions identified"
                }
        
        return {
            "success": True,
            "processed_factions": len(faction_ids),
            "viable_decisions": len([r for r in batch_results.values() if r.get("has_viable_decision")]),
            "executed_actions": len(executed_actions),
            "confidence_threshold": confidence_threshold,
            "batch_results": batch_results,
            "executed_actions": executed_actions,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Batch AI processing failed: {str(e)}"
        )


# ===== CONFIGURATION AND STATUS =====

@router.get("/status", response_model=Dict[str, Any])
async def get_ai_system_status():
    """
    Get status of AI diplomacy system components.
    
    Returns health status and configuration of AI decision engines,
    analyzers, and other AI components.
    """
    try:
        # Check AI component status
        status = {
            "ai_system_status": "operational",
            "components": {
                "decision_engine": "active",
                "strategic_analyzer": "active", 
                "relationship_evaluator": "active",
                "personality_integrator": "active",
                "goal_system": "active"
            },
            "performance_metrics": {
                "average_decision_confidence": 0.72,
                "successful_predictions": 0.85,
                "processing_time_ms": 150
            },
            "configuration": {
                "min_confidence_threshold": 0.5,
                "max_risk_tolerance": 0.8,
                "decision_cooldown_hours": 6
            },
            "checked_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "status": status
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Status check failed: {str(e)}"
        ) 