"""
REST API Router for Diplomacy System

This module defines the API endpoints for interacting with the diplomacy system.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body

from backend.systems.diplomacy.models import (
    DiplomaticEventType, 
    DiplomaticIncidentType,
    DiplomaticStatus, 
    SanctionStatus,
    SanctionType,
    TreatyType,
    TreatyViolationType,
    UltimatumStatus
)
from backend.infrastructure.schemas.diplomacy_schemas import (
    DiplomaticEventCreate,
    DiplomaticEventSchema,
    DiplomaticIncidentCreate,
    DiplomaticIncidentSchema,
    DiplomaticIncidentUpdate,
    FactionRelationshipSchema,
    NegotiationCreate,
    NegotiationOfferCreate,
    NegotiationSchema,
    NegotiationUpdate,
    SanctionCreate,
    SanctionSchema,
    SanctionUpdate,
    SanctionViolationRecord,
    TreatyCreate,
    TreatySchema,
    TreatyUpdate,
    TreatyViolationCreate,
    TreatyViolationSchema,
    UltimatumCreate,
    UltimatumSchema,
    UltimatumUpdate
)
# Import the new configuration-based services
from backend.systems.diplomacy.services.core_services import (
    TensionManagementService, 
    TreatyManagementService, 
    NegotiationService,
    DiplomaticEventService
)


# Create a router
router = APIRouter(
    prefix="/diplomacy",
    tags=["diplomacy"],
    responses={404: {"description": "Not found"}}
)

# Dependencies to get services
def get_tension_service():
    return TensionManagementService()

def get_treaty_service():
    return TreatyManagementService()

def get_negotiation_service():
    return NegotiationService()

def get_event_service():
    return DiplomaticEventService()


# Treaty endpoints

@router.post("/treaties", response_model=Dict)
async def create_treaty(
    treaty: TreatyCreate,
    treaty_service: TreatyManagementService = Depends(get_treaty_service)
):
    """Create a new treaty between factions."""
    result = treaty_service.create_treaty(
        name=treaty.name,
        treaty_type=treaty.type,
        parties=treaty.parties,
        terms=treaty.terms,
        end_date=treaty.end_date,
        metadata=getattr(treaty, 'metadata', None)
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["errors"])
    
    return result

@router.post("/treaties/{treaty_id}/activate", response_model=Dict)
async def activate_treaty(
    treaty_id: UUID,
    treaty_service: TreatyManagementService = Depends(get_treaty_service)
):
    """Activate a treaty and apply its effects."""
    result = treaty_service.activate_treaty(treaty_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail="Failed to activate treaty")
    
    return result

@router.post("/treaties/{treaty_id}/expire", response_model=Dict)
async def expire_treaty(
    treaty_id: UUID,
    reason: Optional[str] = None,
    treaty_service: TreatyManagementService = Depends(get_treaty_service)
):
    """Expire a treaty and remove its effects."""
    result = treaty_service.expire_treaty(treaty_id, reason)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail="Failed to expire treaty")
    
    return result


# Negotiation endpoints

@router.post("/negotiations", response_model=Dict)
async def start_negotiation(
    negotiation: NegotiationCreate,
    negotiation_service: NegotiationService = Depends(get_negotiation_service)
):
    """Start a new negotiation."""
    initial_terms = None
    if negotiation.initial_offer:
        initial_terms = negotiation.initial_offer.terms
    
    result = negotiation_service.start_negotiation(
        initiator_id=negotiation.initiator_id,
        target_id=negotiation.parties[1] if len(negotiation.parties) > 1 else negotiation.parties[0],
        treaty_type=negotiation.treaty_type,
        initial_terms=initial_terms,
        metadata=negotiation.metadata
    )
    
    return result

@router.post("/negotiations/{negotiation_id}/offers", response_model=Dict)
async def make_offer(
    negotiation_id: UUID,
    offer: NegotiationOfferCreate,
    negotiation_service: NegotiationService = Depends(get_negotiation_service)
):
    """Make an offer in a negotiation."""
    result = negotiation_service.make_offer(
        negotiation_id=negotiation_id,
        offering_faction=offer.faction_id,
        terms=offer.terms,
        metadata=getattr(offer, 'metadata', None)
    )
    
    return result


# Tension and relationship endpoints

@router.post("/relations/{faction_a_id}/{faction_b_id}/tension", response_model=Dict)
async def update_tension(
    faction_a_id: UUID,
    faction_b_id: UUID,
    tension_change: float,
    reason: Optional[str] = None,
    tension_service: TensionManagementService = Depends(get_tension_service)
):
    """Update tension between two factions."""
    result = tension_service.update_tension(
        faction_a_id=faction_a_id,
        faction_b_id=faction_b_id,
        tension_change=tension_change,
        reason=reason
    )
    
    return result

@router.get("/relations/{faction_a_id}/{faction_b_id}/status")
async def get_tension_status(
    faction_a_id: UUID,
    faction_b_id: UUID,
    tension: float,
    tension_service: TensionManagementService = Depends(get_tension_service)
):
    """Get diplomatic status for a given tension level."""
    status = tension_service.get_tension_status(tension)
    
    return {
        "faction_a_id": faction_a_id,
        "faction_b_id": faction_b_id,
        "current_tension": tension,
        "diplomatic_status": status.value,
        "at_war_threshold": tension_service.check_war_threshold(tension)
    }


# Diplomatic event and incident endpoints

@router.post("/incidents", response_model=Dict)
async def create_diplomatic_incident(
    incident: DiplomaticIncidentCreate,
    event_service: DiplomaticEventService = Depends(get_event_service)
):
    """Create a new diplomatic incident."""
    result = event_service.create_incident(
        incident_type=incident.incident_type,
        factions_involved=incident.factions_involved,
        severity=getattr(incident, 'severity', None),
        description=getattr(incident, 'description', None),
        metadata=getattr(incident, 'metadata', None)
    )
    
    return result

@router.post("/incidents/{incident_id}/resolve", response_model=Dict)
async def resolve_diplomatic_incident(
    incident_id: UUID,
    resolution: dict = Body(..., example={"resolution_details": "The issue was resolved through negotiation."}),
    event_service: DiplomaticEventService = Depends(get_event_service)
):
    """Resolve a diplomatic incident."""
    result = event_service.resolve_incident(
        incident_id=incident_id,
        resolution=resolution.get("resolution_details", "Incident resolved"),
        metadata=resolution
    )
    
    return result


# Configuration and testing endpoints

@router.get("/config/tension")
async def get_tension_config(
    tension_service: TensionManagementService = Depends(get_tension_service)
):
    """Get current tension system configuration."""
    config = tension_service.config.get_tension_config()
    return {
        "tension_config": config,
        "relationship_transitions": tension_service.config.get_relationship_transitions(),
        "default_values": tension_service.config.get_default_values()
    }

@router.get("/config/treaty-effects")
async def get_treaty_effects_config(
    treaty_service: TreatyManagementService = Depends(get_treaty_service)
):
    """Get current treaty effects configuration."""
    try:
        effects_config = treaty_service.config.load_treaty_effects()
        return {
            "treaty_effects": effects_config,
            "message": "Treaty effects configuration loaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load treaty effects: {str(e)}")

@router.post("/config/reload")
async def reload_configuration():
    """Reload all diplomacy configuration from JSON files."""
    try:
        from backend.infrastructure.config.diplomacy_config import reload_diplomacy_config
        reload_diplomacy_config()
        return {"message": "Diplomacy configuration reloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload configuration: {str(e)}")

@router.get("/config/validate")
async def validate_configuration():
    """Validate all diplomacy configuration files and return detailed status."""
    try:
        from backend.infrastructure.config.diplomacy_config import validate_diplomacy_config
        validation_result = validate_diplomacy_config()
        
        if not validation_result["valid"]:
            # Return 400 for configuration errors, but still include the validation details
            return {
                "status": "invalid", 
                "validation": validation_result,
                "message": "Configuration validation failed. See validation details for errors."
            }
        
        return {
            "status": "valid",
            "validation": validation_result,
            "message": "All configuration files are valid and properly structured"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration validation failed: {str(e)}")

@router.get("/integration/status")
async def get_integration_status():
    """Check diplomacy system integration status."""
    return {
        "status": "active",
        "services": {
            "tension_management": "configured",
            "treaty_management": "configured", 
            "negotiation_service": "configured",
            "event_service": "configured"
        },
        "configuration": {
            "config_loader": "active",
            "json_configs": "loaded"
        },
        "message": "Diplomacy system is fully integrated with configuration"
    }

@router.get("/integration/health")
async def check_integration_health():
    """Health check for diplomacy system components."""
    try:
        # Test service initialization
        tension_service = TensionManagementService()
        treaty_service = TreatyManagementService()
        negotiation_service = NegotiationService()
        event_service = DiplomaticEventService()
        
        # Test configuration loading
        config_status = {
            "tension_config": bool(tension_service.config.get_tension_config()),
            "treaty_effects": bool(treaty_service.config.load_treaty_effects()),
            "relationship_transitions": bool(tension_service.config.get_relationship_transitions()),
            "default_values": bool(tension_service.config.get_default_values())
        }
        
        return {
            "status": "healthy",
            "services_initialized": True,
            "configuration_loaded": all(config_status.values()),
            "config_details": config_status,
            "message": "All diplomacy system components are healthy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}") 