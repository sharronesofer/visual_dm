"""
Enhanced Diplomacy API Routes

This module provides advanced diplomacy endpoints including:
- Multi-party alliance negotiations
- Comprehensive relationship tracking
- Diplomatic network analysis
- Faction reputation management
"""

import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.infrastructure.database import get_db_session
from backend.systems.faction.services.services import FactionService
from backend.systems.faction.services.enhanced_alliance_service import (
    EnhancedAllianceService, 
    NegotiationPhase,
    NegotiationStance
)
from backend.systems.faction.services.relationship_tracker import (
    FactionRelationshipTracker,
    InteractionType,
    RelationshipTrend,
    TrustCategory
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enhanced-diplomacy", tags=["Enhanced Diplomacy"])

# Dependency to create services with database session
def get_enhanced_alliance_service(db: Session = Depends(get_db_session)) -> EnhancedAllianceService:
    """Create enhanced alliance service with database session"""
    try:
        faction_service = FactionService(db)
        return EnhancedAllianceService(faction_service=faction_service)
    except Exception as e:
        logger.warning(f"Could not create enhanced alliance service with database: {e}")
        # Return service without database dependency for demonstration
        return EnhancedAllianceService()

def get_relationship_tracker(db: Session = Depends(get_db_session)) -> FactionRelationshipTracker:
    """Create relationship tracker with database session"""
    try:
        faction_service = FactionService(db)
        return FactionRelationshipTracker(faction_service=faction_service)
    except Exception as e:
        logger.warning(f"Could not create relationship tracker with database: {e}")
        # Return service without database dependency for demonstration
        return FactionRelationshipTracker()

# Request/Response Models
class AllianceProposalRequest(BaseModel):
    """Request model for multi-party alliance proposal"""
    initiator_id: str = Field(..., description="UUID of faction initiating the alliance")
    target_faction_ids: List[str] = Field(..., description="List of faction UUIDs to invite")
    alliance_type: str = Field(default="military", description="Type of alliance to propose")
    proposed_terms: Optional[Dict[str, Any]] = Field(default=None, description="Custom terms to propose")

class NegotiationActionRequest(BaseModel):
    """Request model for negotiation actions"""
    faction_id: str = Field(..., description="UUID of faction taking the action")
    action: str = Field(..., description="Action type: accept, reject, counter_propose, modify_terms")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Action-specific parameters")

class InteractionRecordRequest(BaseModel):
    """Request model for recording faction interactions"""
    initiator_id: str = Field(..., description="Faction that initiated the interaction")
    target_id: str = Field(..., description="Faction that was the target")
    interaction_type: str = Field(..., description="Type of interaction")
    description: str = Field(..., description="Human-readable description")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    trust_impact: float = Field(default=0.0, description="Impact on trust (-1.0 to +1.0)")
    reputation_impact: float = Field(default=0.0, description="Impact on reputation (-1.0 to +1.0)")
    severity: float = Field(default=0.5, description="Event significance (0.0 to 1.0)")

class NetworkAnalysisRequest(BaseModel):
    """Request model for diplomatic network analysis"""
    faction_ids: List[str] = Field(..., description="List of faction UUIDs to analyze")

# Alliance Negotiation Endpoints

@router.post("/alliances/propose")
async def propose_multi_party_alliance(
    request: AllianceProposalRequest,
    enhanced_alliance_service: EnhancedAllianceService = Depends(get_enhanced_alliance_service)
) -> Dict[str, Any]:
    """
    Initiate a multi-party alliance negotiation
    
    Creates a new negotiation session with automatic faction response generation
    based on personalities, relationships, and proposed alliance terms.
    """
    try:
        # Convert string UUIDs to UUID objects
        initiator_uuid = UUID(request.initiator_id)
        target_uuids = [UUID(fid) for fid in request.target_faction_ids]
        
        result = await enhanced_alliance_service.initiate_multi_party_alliance(
            initiator_id=initiator_uuid,
            target_faction_ids=target_uuids,
            alliance_type=request.alliance_type,
            proposed_terms=request.proposed_terms
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        logger.error(f"Error proposing alliance: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/negotiations/{negotiation_id}/actions")
async def take_negotiation_action(
    negotiation_id: str,
    request: NegotiationActionRequest,
    enhanced_alliance_service: EnhancedAllianceService = Depends(get_enhanced_alliance_service)
) -> Dict[str, Any]:
    """
    Take an action in an ongoing alliance negotiation
    
    Actions include accept, reject, counter_propose, modify_terms, etc.
    Updates the negotiation state and triggers faction responses.
    """
    try:
        negotiation_uuid = UUID(negotiation_id)
        faction_uuid = UUID(request.faction_id)
        
        result = await enhanced_alliance_service.advance_negotiation(
            negotiation_id=negotiation_uuid,
            faction_id=faction_uuid,
            action=request.action,
            parameters=request.parameters
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        logger.error(f"Error taking negotiation action: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/negotiations/{negotiation_id}")
async def get_negotiation_status(
    negotiation_id: str,
    enhanced_alliance_service: EnhancedAllianceService = Depends(get_enhanced_alliance_service)
) -> Dict[str, Any]:
    """
    Get current status and details of an alliance negotiation
    
    Returns comprehensive negotiation state including current terms,
    faction positions, success probability, and negotiation history.
    """
    try:
        negotiation_uuid = UUID(negotiation_id)
        
        result = await enhanced_alliance_service.get_negotiation_status(negotiation_uuid)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting negotiation status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/negotiations")
async def list_active_negotiations(
    faction_id: Optional[str] = Query(None, description="Filter by faction ID"),
    enhanced_alliance_service: EnhancedAllianceService = Depends(get_enhanced_alliance_service)
) -> Dict[str, Any]:
    """
    List all active alliance negotiations
    
    Optionally filter to show only negotiations involving a specific faction.
    """
    try:
        faction_uuid = UUID(faction_id) if faction_id else None
        
        negotiations = await enhanced_alliance_service.list_active_negotiations(faction_uuid)
        
        return {
            "active_negotiations": negotiations,
            "total_count": len(negotiations)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        logger.error(f"Error listing negotiations: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Relationship Tracking Endpoints

@router.post("/interactions/record")
async def record_faction_interaction(
    request: InteractionRecordRequest,
    relationship_tracker: FactionRelationshipTracker = Depends(get_relationship_tracker)
) -> Dict[str, Any]:
    """
    Record a new interaction between factions
    
    Creates a permanent record that affects trust, reputation, and relationship trends.
    Used to track diplomatic incidents, trade agreements, betrayals, etc.
    """
    try:
        initiator_uuid = UUID(request.initiator_id)
        target_uuid = UUID(request.target_id)
        
        # Convert string to enum
        try:
            interaction_enum = InteractionType(request.interaction_type)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid interaction type: {request.interaction_type}"
            )
        
        interaction = await relationship_tracker.record_interaction(
            initiator_id=initiator_uuid,
            target_id=target_uuid,
            interaction_type=interaction_enum,
            description=request.description,
            context=request.context,
            trust_impact=request.trust_impact,
            reputation_impact=request.reputation_impact,
            severity=request.severity
        )
        
        return {
            "interaction_id": str(interaction.interaction_id),
            "timestamp": interaction.timestamp.isoformat(),
            "interaction_type": interaction.interaction_type.value,
            "trust_impact": interaction.trust_impact,
            "reputation_impact": interaction.reputation_impact,
            "message": "Interaction recorded successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/relationships/{faction_a_id}/{faction_b_id}")
async def get_relationship_summary(
    faction_a_id: str, 
    faction_b_id: str,
    relationship_tracker: FactionRelationshipTracker = Depends(get_relationship_tracker)
) -> Dict[str, Any]:
    """
    Get comprehensive relationship summary between two factions
    
    Returns detailed analysis including trust levels, interaction history,
    significant events, trends, and predictions.
    """
    try:
        faction_a_uuid = UUID(faction_a_id)
        faction_b_uuid = UUID(faction_b_id)
        
        summary = await relationship_tracker.get_relationship_summary(faction_a_uuid, faction_b_uuid)
        
        # Convert dataclass to dict for JSON serialization
        return {
            "faction_a_id": str(summary.faction_a_id),
            "faction_b_id": str(summary.faction_b_id),
            "faction_a_name": summary.faction_a_name,
            "faction_b_name": summary.faction_b_name,
            "current_trust_level": summary.current_trust_level.value,
            "mutual_trust_score": summary.mutual_trust_score,
            "relationship_trend": summary.relationship_trend.value,
            "diplomatic_status": summary.diplomatic_status,
            "relationship_duration_days": summary.relationship_duration,
            "total_interactions": summary.total_interactions,
            "positive_interactions": summary.positive_interactions,
            "negative_interactions": summary.negative_interactions,
            "last_interaction_date": summary.last_interaction_date.isoformat() if summary.last_interaction_date else None,
            "most_significant_positive_event": _serialize_interaction(summary.most_significant_positive_event),
            "most_significant_negative_event": _serialize_interaction(summary.most_significant_negative_event),
            "turning_points": [_serialize_interaction(tp) for tp in summary.turning_points],
            "predicted_trajectory": summary.predicted_trajectory.value,
            "alliance_probability": summary.alliance_probability,
            "conflict_probability": summary.conflict_probability,
            "stability_score": summary.stability_score
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting relationship summary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/factions/{faction_id}/reputation")
async def get_faction_reputation(
    faction_id: str,
    relationship_tracker: FactionRelationshipTracker = Depends(get_relationship_tracker)
) -> Dict[str, Any]:
    """
    Get comprehensive reputation analysis for a faction
    
    Returns overall reputation score, trends, and breakdown by interaction type.
    """
    try:
        faction_uuid = UUID(faction_id)
        
        reputation = await relationship_tracker.get_faction_reputation(faction_uuid)
        
        return reputation
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting faction reputation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/network/analyze")
async def analyze_diplomatic_network(
    request: NetworkAnalysisRequest,
    relationship_tracker: FactionRelationshipTracker = Depends(get_relationship_tracker)
) -> Dict[str, Any]:
    """
    Analyze diplomatic network among a group of factions
    
    Returns comprehensive network metrics, alliance clusters, tension hotspots,
    and diplomatic influence rankings.
    """
    try:
        faction_uuids = [UUID(fid) for fid in request.faction_ids]
        
        analysis = await relationship_tracker.analyze_diplomatic_network(faction_uuids)
        
        return analysis
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        logger.error(f"Error analyzing diplomatic network: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Utility Endpoints

@router.get("/interaction-types")
async def get_interaction_types() -> Dict[str, List[str]]:
    """Get all available interaction types for recording"""
    return {
        "interaction_types": [it.value for it in InteractionType],
        "descriptions": {
            "alliance_proposal": "Faction proposes an alliance",
            "alliance_acceptance": "Faction accepts an alliance proposal",
            "alliance_rejection": "Faction rejects an alliance proposal",
            "treaty_signed": "Factions sign a formal treaty",
            "treaty_violated": "Faction violates an existing treaty",
            "trade_agreement": "Factions establish trade relations",
            "military_support": "Faction provides military assistance",
            "betrayal": "Faction betrays another faction's trust",
            "diplomatic_insult": "Faction insults another diplomatically",
            "territorial_dispute": "Conflict over territorial claims",
            "resource_conflict": "Dispute over resource access",
            "cultural_exchange": "Positive cultural interaction",
            "humanitarian_aid": "Faction provides humanitarian assistance",
            "espionage_detected": "Faction's espionage activities discovered",
            "border_incident": "Minor conflict at faction borders",
            "succession_support": "Support during leadership transition",
            "mediation_attempt": "Faction attempts to mediate a dispute"
        }
    }

@router.get("/alliance-types")
async def get_alliance_types() -> Dict[str, List[str]]:
    """Get all available alliance types for negotiations"""
    return {
        "alliance_types": ["military", "economic", "defensive", "research", "cultural"],
        "descriptions": {
            "military": "Joint military operations and mutual defense",
            "economic": "Trade agreements and economic cooperation",
            "defensive": "Mutual protection against external threats",
            "research": "Shared knowledge and technological development",
            "cultural": "Cultural exchange and diplomatic cooperation"
        }
    }

@router.get("/negotiation-phases")
async def get_negotiation_phases() -> Dict[str, List[str]]:
    """Get all possible negotiation phases"""
    return {
        "negotiation_phases": [phase.value for phase in NegotiationPhase],
        "descriptions": {
            "proposal": "Initial alliance proposal presented",
            "counter_proposal": "Factions making counter-offers",
            "terms_discussion": "Detailed negotiation of terms",
            "final_review": "Final review before ratification",
            "ratification": "Formal approval process",
            "completed": "Alliance successfully formed",
            "rejected": "Alliance proposal rejected",
            "expired": "Negotiation deadline passed"
        }
    }

@router.get("/trust-categories")
async def get_trust_categories() -> Dict[str, List[str]]:
    """Get all trust level categories"""
    return {
        "trust_categories": [cat.value for cat in TrustCategory],
        "thresholds": {
            "absolute_trust": "0.9+",
            "high_trust": "0.7-0.9",
            "moderate_trust": "0.5-0.7",
            "low_trust": "0.3-0.5",
            "distrust": "0.1-0.3",
            "deep_mistrust": "0.0-0.1"
        }
    }

# Helper Functions

def _serialize_interaction(interaction) -> Optional[Dict[str, Any]]:
    """Serialize interaction record for JSON response"""
    if not interaction:
        return None
    
    return {
        "interaction_id": str(interaction.interaction_id),
        "timestamp": interaction.timestamp.isoformat(),
        "interaction_type": interaction.interaction_type.value,
        "description": interaction.description,
        "trust_impact": interaction.trust_impact,
        "reputation_impact": interaction.reputation_impact,
        "severity": interaction.severity,
        "outcome": interaction.outcome
    } 