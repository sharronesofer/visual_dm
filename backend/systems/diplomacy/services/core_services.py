"""
Core Diplomacy Services

High-level service functions for diplomatic operations including
tension management, treaty operations, negotiations, and events.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID, uuid4
import random

from backend.infrastructure.config.diplomacy_config import get_diplomacy_config
from backend.infrastructure.utils.diplomacy.core_utils import (
    TensionCalculator, TreatyValidator, NegotiationAnalyzer, 
    IncidentAnalyzer, SanctionCalculator, UltimatumEvaluator,
    DiplomaticEventGenerator
)
from backend.systems.diplomacy.models.core_models import (
    Treaty, TreatyType, TreatyStatus, TreatyViolation, TreatyViolationType,
    Negotiation, NegotiationStatus, NegotiationOffer,
    DiplomaticEvent, DiplomaticEventType, DiplomaticStatus,
    DiplomaticIncident, DiplomaticIncidentType, DiplomaticIncidentSeverity,
    Ultimatum, UltimatumStatus,
    Sanction, SanctionType, SanctionStatus
)


class TensionManagementService:
    """Service for managing diplomatic tension between factions."""
    
    def __init__(self):
        """Initialize with configuration and utilities."""
        self.config = get_diplomacy_config()
        self.calculator = TensionCalculator()
    
    def update_tension(self, faction_a_id: UUID, faction_b_id: UUID, 
                      tension_change: float, reason: Optional[str] = None,
                      metadata: Optional[Dict] = None) -> Dict:
        """
        Update tension between two factions.
        
        Args:
            faction_a_id: First faction UUID
            faction_b_id: Second faction UUID  
            tension_change: Amount to change tension (+/-)
            reason: Optional reason for tension change
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with updated tension and status information
        """
        # This would integrate with actual faction relationship storage
        # For now, return a structured response based on configuration
        
        # Get current tension (would be from database in real implementation)
        current_tension = 0  # Placeholder
        
        # Calculate new tension using configured limits
        new_tension = self.calculator.calculate_new_tension(current_tension, tension_change)
        
        # Determine if status should change
        new_status = self.calculator.determine_status_from_tension(new_tension)
        
        # Create tension change event
        event = DiplomaticEventGenerator.create_tension_change_event(
            faction_a_id, faction_b_id, current_tension, new_tension, reason
        )
        
        return {
            "old_tension": current_tension,
            "new_tension": new_tension,
            "tension_change": tension_change,
            "new_status": new_status,
            "reason": reason,
            "event_id": event.id,
            "metadata": metadata or {}
        }
    
    def apply_decay(self, faction_relationships: List[Dict], hours_passed: float) -> List[Dict]:
        """
        Apply tension decay to multiple faction relationships.
        
        Args:
            faction_relationships: List of relationship dictionaries
            hours_passed: Hours since last decay application
            
        Returns:
            Updated list of relationships with decayed tension
        """
        updated_relationships = []
        
        for relationship in faction_relationships:
            current_tension = relationship.get('tension', 0)
            new_tension = self.calculator.apply_tension_decay(current_tension, hours_passed)
            
            updated_relationship = relationship.copy()
            updated_relationship['tension'] = new_tension
            updated_relationship['last_decay'] = datetime.utcnow()
            
            updated_relationships.append(updated_relationship)
        
        return updated_relationships
    
    def get_tension_status(self, tension: float) -> DiplomaticStatus:
        """Get diplomatic status for a given tension level."""
        return self.calculator.determine_status_from_tension(tension)
    
    def check_war_threshold(self, tension: float) -> bool:
        """Check if tension has reached war threshold using configured values."""
        return self.calculator.is_war_threshold_reached(tension)


class TreatyManagementService:
    """Service for managing treaties and related operations."""
    
    def __init__(self):
        """Initialize with configuration and utilities."""
        self.config = get_diplomacy_config()
        self.validator = TreatyValidator()
    
    def create_treaty(self, name: str, treaty_type: TreatyType, parties: List[UUID],
                     terms: Dict, end_date: Optional[datetime] = None,
                     metadata: Optional[Dict] = None) -> Dict:
        """
        Create a new treaty between factions.
        
        Args:
            name: Treaty name
            treaty_type: Type of treaty
            parties: List of faction UUIDs
            terms: Treaty terms dictionary
            end_date: Optional expiration date
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with treaty creation results
        """
        # Validate treaty parameters
        validation = self.validator.validate_treaty_creation(name, treaty_type, parties, terms, end_date)
        
        if not validation["is_valid"]:
            return {
                "success": False,
                "errors": validation["errors"],
                "treaty": None
            }
        
        # Calculate tension impact using configured values
        tension_impact = self.validator.calculate_tension_impact(treaty_type)
        
        # Create treaty object
        treaty = Treaty(
            id=uuid4(),
            name=name,
            treaty_type=treaty_type,
            parties=parties,
            terms=terms,
            status=TreatyStatus.DRAFT,
            created_date=datetime.utcnow(),
            end_date=end_date,
            is_active=False,
            metadata=metadata or {}
        )
        
        # Generate creation event
        event = DiplomaticEventGenerator.generate_treaty_event(treaty)
        
        return {
            "success": True,
            "treaty": treaty,
            "tension_impact": tension_impact,
            "event_id": event.id,
            "errors": []
        }
    
    def activate_treaty(self, treaty_id: UUID, activation_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Activate a treaty and apply its effects.
        
        Args:
            treaty_id: ID of the treaty to activate
            activation_date: Optional activation date (defaults to now)
            
        Returns:
            Activation result with effect details
        """
        # Implementation would activate the treaty in the database
        # For now, returning expected structure with configuration-based effects
        
        if activation_date is None:
            activation_date = datetime.utcnow()
        
        # In a real implementation, this would fetch from database
        # For now, we'll create a mock treaty to demonstrate the effects system
        from backend.systems.diplomacy.models.core_models import Treaty, TreatyType, TreatyStatus
        
        mock_treaty = Treaty(\
            id=treaty_id,\
            name="Sample Treaty",\
            treaty_type=TreatyType.ALLIANCE,\
            parties=[uuid4(), uuid4()],  # Mock faction IDs\
            terms={"mutual_defense": True, "trade_agreement": True},\
            status=TreatyStatus.ACTIVE,\
            creation_date=datetime.utcnow(),\
            activation_date=activation_date\
        )\
        
        # Apply treaty effects using configuration
        effects_result = apply_treaty_effects(mock_treaty, mock_treaty.parties)\
        
        # Generate diplomatic event
        event_generator = DiplomaticEventGenerator()
        activation_event = event_generator.generate_treaty_activation_event(\
            treaty=mock_treaty,\
            factions_involved=mock_treaty.parties\
        )\
        
        return {\
            "success": True,\
            "treaty_id": treaty_id,\
            "activation_date": activation_date.isoformat(),\
            "event_id": activation_event.id,\
            "effects_applied": effects_result,\
            "message": f"Treaty {mock_treaty.name} activated successfully with {len(effects_result['effects_applied'])} effects applied"\
        }\
    
    def expire_treaty(self, treaty_id: UUID, reason: Optional[str] = None, \
                     expiration_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Expire a treaty and remove its effects.
        
        Args:
            treaty_id: ID of the treaty to expire
            reason: Optional reason for expiration
            expiration_date: Optional expiration date (defaults to now)
            
        Returns:
            Expiration result with removed effects details
        """
        if expiration_date is None:
            expiration_date = datetime.utcnow()
        
        if reason is None:
            reason = "Treaty expired naturally"
        
        # In a real implementation, this would fetch from database
        # For now, we'll create a mock treaty to demonstrate the effects removal
        from backend.systems.diplomacy.models.core_models import Treaty, TreatyType, TreatyStatus
        
        mock_treaty = Treaty(\
            id=treaty_id,\
            name="Sample Treaty",\
            treaty_type=TreatyType.ALLIANCE,\
            parties=[uuid4(), uuid4()],  # Mock faction IDs\
            terms={"mutual_defense": True, "trade_agreement": True},\
            status=TreatyStatus.EXPIRED,\
            creation_date=datetime.utcnow() - timedelta(days=365),\
            activation_date=datetime.utcnow() - timedelta(days=365),\
            expiration_date=expiration_date\
        )\
        
        # Remove treaty effects using configuration
        removal_result = remove_treaty_effects(mock_treaty, mock_treaty.parties)\
        
        # Calculate tension impact from treaty expiration
        calculator = TensionCalculator()
        tension_impact = calculator.calculate_treaty_expiration_impact(\
            treaty_type=mock_treaty.treaty_type,\
            parties=mock_treaty.parties,\
            reason=reason\
        )\
        
        # Generate diplomatic event
        event_generator = DiplomaticEventGenerator()
        expiration_event = event_generator.generate_treaty_expiration_event(\
            treaty=mock_treaty,\
            factions_involved=mock_treaty.parties,\
            reason=reason\
        )\
        
        return {\
            "success": True,\
            "treaty_id": treaty_id,\
            "expiration_date": expiration_date.isoformat(),\
            "reason": reason,\
            "tension_impact": tension_impact,\
            "event_id": expiration_event.id,\
            "effects_removed": removal_result,\
            "message": f"Treaty expired with {len(removal_result['effects_removed'])} effects removed"\
        }


class NegotiationService:
    """Service for managing diplomatic negotiations."""
    
    def __init__(self):
        """Initialize with configuration and utilities."""
        self.config = get_diplomacy_config()
        self.analyzer = NegotiationAnalyzer()
    
    def start_negotiation(self, initiator_id: UUID, target_id: UUID, 
                         treaty_type: Optional[TreatyType] = None,
                         initial_terms: Optional[Dict] = None,
                         metadata: Optional[Dict] = None) -> Dict:
        """
        Start a new negotiation between factions.
        
        Args:
            initiator_id: Faction starting the negotiation
            target_id: Target faction
            treaty_type: Optional type of treaty being negotiated
            initial_terms: Optional initial terms
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with negotiation creation results
        """
        negotiation = Negotiation(
            id=uuid4(),
            parties=[initiator_id, target_id],
            status=NegotiationStatus.INITIATED,
            treaty_type=treaty_type,
            created_date=datetime.utcnow(),
            current_terms=initial_terms or {},
            metadata=metadata or {}
        )
        
        # Determine if this is high-stakes
        is_high_stakes = self.analyzer.is_high_stakes_negotiation(negotiation)
        
        # Generate negotiation event
        event = DiplomaticEventGenerator.create_negotiation_event(negotiation, "initiated")
        
        return {
            "success": True,
            "negotiation": negotiation,
            "is_high_stakes": is_high_stakes,
            "event_id": event.id
        }
    
    def make_offer(self, negotiation_id: UUID, offering_faction: UUID,
                  terms: Dict, metadata: Optional[Dict] = None) -> Dict:
        """
        Make an offer in an ongoing negotiation.
        
        Args:
            negotiation_id: Negotiation UUID
            offering_faction: Faction making the offer
            terms: Offer terms
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with offer creation results
        """
        offer = NegotiationOffer(
            id=uuid4(),
            negotiation_id=negotiation_id,
            offering_faction=offering_faction,
            terms=terms,
            created_date=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Calculate attractiveness (would use actual recipient data)
        attractiveness = self.analyzer.calculate_offer_attractiveness(offer, offering_faction)
        
        return {
            "success": True,
            "offer": offer,
            "attractiveness_score": attractiveness
        }


class DiplomaticEventService:
    """Service for managing diplomatic events and incidents."""
    
    def __init__(self):
        """Initialize with configuration and utilities."""
        self.config = get_diplomacy_config()
        self.incident_analyzer = IncidentAnalyzer()
    
    def create_incident(self, incident_type: DiplomaticIncidentType,
                       factions_involved: List[UUID],
                       severity: Optional[DiplomaticIncidentSeverity] = None,
                       description: Optional[str] = None,
                       metadata: Optional[Dict] = None) -> Dict:
        """
        Create a new diplomatic incident.
        
        Args:
            incident_type: Type of incident
            factions_involved: List of faction UUIDs
            severity: Optional severity level (defaults to configured value)
            description: Optional incident description
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with incident creation results
        """
        # Use configured default severity if not provided
        if severity is None:
            defaults = self.config.get_default_values()
            severity_value = defaults.get("incident_severity", "MODERATE")
            severity = DiplomaticIncidentSeverity(severity_value)
        
        incident = DiplomaticIncident(
            id=uuid4(),
            incident_type=incident_type,
            factions_involved=factions_involved,
            severity=severity,
            description=description or f"{incident_type.value} incident",
            created_date=datetime.utcnow(),
            is_resolved=False,
            metadata=metadata or {}
        )
        
        # Calculate tension impact using configured values
        tension_impact = self.incident_analyzer.calculate_incident_tension_impact(incident_type, severity)
        
        return {
            "success": True,
            "incident": incident,
            "tension_impact": tension_impact,
            "requires_escalation": False  # Would be calculated based on context
        }
    
    def resolve_incident(self, incident_id: UUID, resolution: str,
                        metadata: Optional[Dict] = None) -> Dict:
        """
        Resolve a diplomatic incident.
        
        Args:
            incident_id: Incident UUID
            resolution: Resolution description
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with resolution results
        """
        resolution_event = DiplomaticEvent(
            id=uuid4(),
            event_type=DiplomaticEventType.INCIDENT_RESOLVED,
            description=f"Incident {incident_id} resolved: {resolution}",
            factions_involved=[],
            created_date=datetime.utcnow(),
            severity=30,
            metadata={"incident_id": str(incident_id), "resolution": resolution}
        )
        
        return {
            "success": True,
            "incident_id": incident_id,
            "resolution": resolution,
            "resolution_date": datetime.utcnow(),
            "event_id": resolution_event.id
        }

def load_treaty_effects_from_config() -> Dict[str, Dict[str, Any]]:
    """Load treaty effects configuration from JSON file."""
    config = get_diplomacy_config()
    return config.get_config_value("data/systems/diplomacy/treaty_effects.json", {})

def apply_treaty_effects(treaty: Treaty, faction_ids: List[UUID]) -> Dict[str, Any]:
    """
    Apply treaty effects to the involved factions based on configuration.
    
    Args:
        treaty: The treaty being activated
        faction_ids: List of faction IDs involved in the treaty
        
    Returns:
        Dictionary of applied effects and their results
    """
    effects_config = load_treaty_effects_from_config()
    
    # Get effects for this treaty type
    treaty_type_str = treaty.treaty_type.value if hasattr(treaty.treaty_type, 'value') else str(treaty.treaty_type)
    treaty_effects = effects_config.get(treaty_type_str, {})
    
    applied_effects = {
        "treaty_id": treaty.id,
        "treaty_type": treaty_type_str,
        "effects_applied": [],
        "faction_changes": {}
    }
    
    for faction_id in faction_ids:
        faction_changes = {
            "faction_id": faction_id,
            "changes": []
        }
        
        # Apply economic effects
        if "economic" in treaty_effects:
            economic_effects = treaty_effects["economic"]
            for effect_type, effect_value in economic_effects.items():
                if effect_type == "trade_bonus":
                    faction_changes["changes"].append({
                        "type": "economic",
                        "effect": "trade_bonus",
                        "value": effect_value,
                        "description": f"Trade bonus of {effect_value}% from {treaty_type_str} treaty"
                    })
                elif effect_type == "resource_bonus":
                    for resource, bonus in effect_value.items():
                        faction_changes["changes"].append({
                            "type": "economic",
                            "effect": "resource_bonus",
                            "resource": resource,
                            "value": bonus,
                            "description": f"{resource} production bonus of {bonus}% from treaty"
                        })
        
        # Apply military effects
        if "military" in treaty_effects:
            military_effects = treaty_effects["military"]
            for effect_type, effect_value in military_effects.items():
                if effect_type == "defense_bonus":
                    faction_changes["changes"].append({
                        "type": "military",
                        "effect": "defense_bonus",
                        "value": effect_value,
                        "description": f"Defense bonus of {effect_value}% from {treaty_type_str} treaty"
                    })
                elif effect_type == "shared_vision":
                    if effect_value:
                        faction_changes["changes"].append({
                            "type": "military",
                            "effect": "shared_vision",
                            "value": True,
                            "description": "Shared vision with treaty partners"
                        })
        
        # Apply diplomatic effects
        if "diplomatic" in treaty_effects:
            diplomatic_effects = treaty_effects["diplomatic"]
            for effect_type, effect_value in diplomatic_effects.items():
                if effect_type == "tension_modifier":
                    faction_changes["changes"].append({
                        "type": "diplomatic",
                        "effect": "tension_modifier",
                        "value": effect_value,
                        "description": f"Tension changes modified by {effect_value}% with treaty partners"
                    })
                elif effect_type == "reputation_bonus":
                    faction_changes["changes"].append({
                        "type": "diplomatic",
                        "effect": "reputation_bonus",
                        "value": effect_value,
                        "description": f"Reputation bonus of {effect_value} from treaty"
                    })
        
        applied_effects["faction_changes"][str(faction_id)] = faction_changes
        applied_effects["effects_applied"].extend([change["effect"] for change in faction_changes["changes"]])
    
    # Remove duplicates from effects_applied
    applied_effects["effects_applied"] = list(set(applied_effects["effects_applied"]))
    
    return applied_effects

def remove_treaty_effects(treaty: Treaty, faction_ids: List[UUID]) -> Dict[str, Any]:
    """
    Remove treaty effects when a treaty expires or is dissolved.
    
    Args:
        treaty: The treaty being ended
        faction_ids: List of faction IDs that were involved
        
    Returns:
        Dictionary of removed effects
    """
    # This essentially reverses the apply_treaty_effects logic
    effects_config = load_treaty_effects_from_config()
    
    treaty_type_str = treaty.treaty_type.value if hasattr(treaty.treaty_type, 'value') else str(treaty.treaty_type)
    treaty_effects = effects_config.get(treaty_type_str, {})
    
    removed_effects = {
        "treaty_id": treaty.id,
        "treaty_type": treaty_type_str,
        "effects_removed": [],
        "faction_changes": {}
    }
    
    for faction_id in faction_ids:
        faction_changes = {
            "faction_id": faction_id,
            "changes": []
        }
        
        # Remove economic effects (reverse bonuses)
        if "economic" in treaty_effects:
            economic_effects = treaty_effects["economic"]
            for effect_type, effect_value in economic_effects.items():
                if effect_type == "trade_bonus":
                    faction_changes["changes"].append({
                        "type": "economic",
                        "effect": "remove_trade_bonus",
                        "value": -effect_value,
                        "description": f"Removed trade bonus of {effect_value}% from ended {treaty_type_str} treaty"
                    })
                elif effect_type == "resource_bonus":
                    for resource, bonus in effect_value.items():
                        faction_changes["changes"].append({
                            "type": "economic",
                            "effect": "remove_resource_bonus",
                            "resource": resource,
                            "value": -bonus,
                            "description": f"Removed {resource} production bonus of {bonus}% from ended treaty"
                        })
        
        # Remove military effects
        if "military" in treaty_effects:
            military_effects = treaty_effects["military"]
            for effect_type, effect_value in military_effects.items():
                if effect_type == "defense_bonus":
                    faction_changes["changes"].append({
                        "type": "military",
                        "effect": "remove_defense_bonus",
                        "value": -effect_value,
                        "description": f"Removed defense bonus of {effect_value}% from ended {treaty_type_str} treaty"
                    })
                elif effect_type == "shared_vision":
                    if effect_value:
                        faction_changes["changes"].append({
                            "type": "military",
                            "effect": "remove_shared_vision",
                            "value": False,
                            "description": "Removed shared vision with former treaty partners"
                        })
        
        # Remove diplomatic effects
        if "diplomatic" in treaty_effects:
            diplomatic_effects = treaty_effects["diplomatic"]
            for effect_type, effect_value in diplomatic_effects.items():
                if effect_type == "tension_modifier":
                    faction_changes["changes"].append({
                        "type": "diplomatic",
                        "effect": "remove_tension_modifier",
                        "value": 0,  # Reset to normal
                        "description": f"Removed tension modifier from ended treaty"
                    })
                elif effect_type == "reputation_bonus":
                    faction_changes["changes"].append({
                        "type": "diplomatic",
                        "effect": "remove_reputation_bonus",
                        "value": -effect_value,
                        "description": f"Removed reputation bonus of {effect_value} from ended treaty"
                    })
        
        removed_effects["faction_changes"][str(faction_id)] = faction_changes
        removed_effects["effects_removed"].extend([change["effect"] for change in faction_changes["changes"]])
    
    # Remove duplicates from effects_removed
    removed_effects["effects_removed"] = list(set(removed_effects["effects_removed"]))
    
    return removed_effects

def load_diplomatic_events_from_config() -> Dict[str, Any]:
    """Load diplomatic events configuration from JSON file."""
    config = get_diplomacy_config()
    return config.get_config_value("data/systems/diplomacy/diplomatic_events_config.json", {})

def trigger_diplomatic_event(event_type: str, factions_involved: List[UUID], 
                           region_id: Optional[UUID] = None, 
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Trigger a diplomatic event using configuration-based parameters.
    
    Args:
        event_type: Type of diplomatic event to trigger
        factions_involved: List of faction IDs involved
        region_id: Optional region where the event occurs
        metadata: Optional additional event metadata
        
    Returns:
        Dictionary with event details and effects
    """
    events_config = load_diplomatic_events_from_config()
    
    # Get configuration for this event type
    event_config = events_config.get("event_types", {}).get(event_type, {})
    
    if not event_config:
        # Return a basic event if no configuration found
        return {
            "success": False,
            "error": f"No configuration found for event type: {event_type}",
            "available_events": list(events_config.get("event_types", {}).keys())
        }
    
    # Create the diplomatic event
    event = DiplomaticEvent(
        id=uuid4(),
        event_type=DiplomaticEventType[event_type] if hasattr(DiplomaticEventType, event_type) else DiplomaticEventType.OTHER,
        description=event_config.get("description", f"Diplomatic event: {event_type}"),
        factions_involved=factions_involved,
        created_date=datetime.utcnow(),
        severity=event_config.get("base_severity", 50),
        metadata={
            "region_id": str(region_id) if region_id else None,
            "event_type": event_type,
            **(metadata or {})
        }
    )
    
    # Calculate tension impacts based on configuration
    tension_calculator = TensionCalculator()
    tension_changes = {}
    
    # Apply configured tension modifiers
    tension_config = event_config.get("tension_impact", {})
    base_impact = tension_config.get("base_change", 0)
    impact_per_faction = tension_config.get("per_faction_modifier", 1.0)
    
    # Calculate pairwise tension changes for involved factions
    for i, faction_a in enumerate(factions_involved):
        for faction_b in factions_involved[i+1:]:
            faction_pair = f"{faction_a}_{faction_b}"
            calculated_impact = base_impact * impact_per_faction
            
            # Apply severity modifiers from configuration
            severity_multiplier = events_config.get("severity_modifiers", {}).get(str(event.severity), 1.0)
            final_impact = calculated_impact * severity_multiplier
            
            tension_changes[faction_pair] = {
                "old_tension": 50,  # Mock current tension
                "change": final_impact,
                "new_tension": max(0, min(100, 50 + final_impact)),
                "reason": event.description
            }
    
    # Generate automatic consequences based on configuration
    consequences = []
    auto_consequences = event_config.get("automatic_consequences", [])
    
    for consequence in auto_consequences:
        consequence_result = {
            "type": consequence.get("type", "unknown"),
            "description": consequence.get("description", "Automatic consequence triggered"),
            "severity": consequence.get("severity", "medium"),
            "applies_to": consequence.get("applies_to", "all_factions")
        }
        
        # Apply faction-specific consequences
        if consequence_result["applies_to"] == "all_factions":
            consequence_result["affected_factions"] = factions_involved
        elif consequence_result["applies_to"] == "initiator" and factions_involved:
            consequence_result["affected_factions"] = [factions_involved[0]]
        elif consequence_result["applies_to"] == "target" and len(factions_involved) > 1:
            consequence_result["affected_factions"] = [factions_involved[1]]
        
        consequences.append(consequence_result)
    
    # Check for escalation triggers
    escalation_check = events_config.get("escalation_triggers", {})
    requires_escalation = False
    escalation_reason = None
    
    if event.severity >= escalation_check.get("severity_threshold", 80):
        requires_escalation = True
        escalation_reason = "Event severity exceeds threshold"
    elif len(factions_involved) >= escalation_check.get("faction_count_threshold", 5):
        requires_escalation = True
        escalation_reason = "Too many factions involved"
    
    return {
        "success": True,
        "event": {
            "id": event.id,
            "type": event_type,
            "description": event.description,
            "factions_involved": factions_involved,
            "severity": event.severity,
            "created_date": event.created_date.isoformat(),
            "region_id": region_id,
            "metadata": event.metadata
        },
        "tension_impact": tension_changes,
        "consequences": consequences,
        "requires_escalation": requires_escalation,
        "escalation_reason": escalation_reason,
        "message": f"Diplomatic event '{event_type}' triggered successfully with {len(consequences)} automatic consequences"
    }

def process_event_chain(initial_event_type: str, factions_involved: List[UUID],
                       region_id: Optional[UUID] = None) -> Dict[str, Any]:
    """
    Process a chain of diplomatic events based on configuration.
    
    Args:
        initial_event_type: The triggering event type
        factions_involved: List of faction IDs involved
        region_id: Optional region where events occur
        
    Returns:
        Dictionary with all triggered events in the chain
    """
    events_config = load_diplomatic_events_from_config()
    event_chains = events_config.get("event_chains", {})
    
    processed_events = []
    current_event_type = initial_event_type
    chain_depth = 0
    max_chain_depth = 5  # Prevent infinite loops
    
    while current_event_type and chain_depth < max_chain_depth:
        # Trigger the current event
        event_result = trigger_diplomatic_event(
            event_type=current_event_type,
            factions_involved=factions_involved,
            region_id=region_id,
            metadata={"chain_depth": chain_depth, "initial_event": initial_event_type}
        )
        
        if not event_result["success"]:
            break
            
        processed_events.append(event_result)
        
        # Check for chain continuation
        chain_config = event_chains.get(current_event_type, {})
        next_events = chain_config.get("triggers", [])
        
        # Simple logic: trigger first applicable event in chain
        current_event_type = None
        for next_event in next_events:
            trigger_chance = next_event.get("probability", 1.0)
            if random.random() <= trigger_chance:
                current_event_type = next_event.get("event_type")
                break
        
        chain_depth += 1
    
    # Calculate cumulative effects
    total_tension_changes = {}
    all_consequences = []
    escalation_events = []
    
    for event_result in processed_events:
        # Merge tension changes
        for faction_pair, changes in event_result.get("tension_impact", {}).items():
            if faction_pair in total_tension_changes:
                total_tension_changes[faction_pair]["change"] += changes["change"]
                total_tension_changes[faction_pair]["new_tension"] = max(
                    0, min(100, total_tension_changes[faction_pair]["old_tension"] + total_tension_changes[faction_pair]["change"])
                )
            else:
                total_tension_changes[faction_pair] = changes.copy()
        
        # Collect consequences
        all_consequences.extend(event_result.get("consequences", []))
        
        # Track escalation events
        if event_result.get("requires_escalation"):
            escalation_events.append({
                "event_id": event_result["event"]["id"],
                "reason": event_result.get("escalation_reason")
            })
    
    return {
        "success": True,
        "chain_length": len(processed_events),
        "events": processed_events,
        "cumulative_effects": {
            "tension_changes": total_tension_changes,
            "consequences": all_consequences,
            "escalations": escalation_events
        },
        "message": f"Event chain completed with {len(processed_events)} events triggered"
    }