"""
Core Diplomacy Utilities

Utility classes for calculations, validations, and content generation 
for core diplomatic operations.
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from uuid import UUID, uuid4

from backend.infrastructure.config.diplomacy_config import get_diplomacy_config
from backend.systems.diplomacy.models.core_models import (
    Treaty, TreatyType, TreatyStatus, TreatyViolation, TreatyViolationType,
    Negotiation, NegotiationStatus, NegotiationOffer,
    DiplomaticEvent, DiplomaticEventType, DiplomaticStatus,
    DiplomaticIncident, DiplomaticIncidentType, DiplomaticIncidentSeverity,
    Ultimatum, UltimatumStatus,
    Sanction, SanctionType, SanctionStatus
)


class TensionCalculator:
    """Utility class for tension-related calculations using configuration values."""
    
    def __init__(self):
        """Initialize with configuration loader."""
        self.config = get_diplomacy_config()
    
    def apply_tension_decay(self, current_tension: float, hours_passed: float, 
                           decay_rate: Optional[float] = None) -> float:
        """Apply tension decay over time using configured decay rate."""
        if hours_passed <= 0:
            return current_tension
        
        # Use configured decay rate if not provided
        if decay_rate is None:
            tension_config = self.config.get_tension_config()
            decay_rate = tension_config.get("decay_rate", 0.1)
        
        decay_amount = decay_rate * hours_passed
        
        if current_tension > 0:
            return max(0, current_tension - decay_amount)
        elif current_tension < 0:
            return min(0, current_tension + decay_amount)
        
        return current_tension
    
    def calculate_new_tension(self, current_tension: float, tension_change: float,
                            min_tension: Optional[float] = None, max_tension: Optional[float] = None) -> float:
        """Calculate new tension value with configured limits applied."""
        # Use configured limits if not provided
        if min_tension is None or max_tension is None:
            tension_config = self.config.get_tension_config()
            min_tension = min_tension or tension_config.get("min_tension", -100.0)
            max_tension = max_tension or tension_config.get("max_tension", 100.0)
        
        new_tension = current_tension + tension_change
        return max(min_tension, min(max_tension, new_tension))
    
    def determine_status_from_tension(self, tension: float) -> DiplomaticStatus:
        """Determine diplomatic status based on tension level using configured thresholds."""
        transitions = self.config.get_relationship_transitions()
        
        # Use configured thresholds
        war_threshold = transitions.get("hostile_to_war", 90)
        hostile_threshold = transitions.get("neutral_to_hostile", 60)
        friendly_threshold = transitions.get("neutral_to_friendly", -40)
        alliance_threshold = transitions.get("friendly_to_alliance", -75)
        
        if tension >= war_threshold:
            return DiplomaticStatus.WAR
        elif tension >= hostile_threshold:
            return DiplomaticStatus.HOSTILE
        elif tension >= 20:  # Keep some hardcoded intermediate values for now
            return DiplomaticStatus.NEUTRAL
        elif tension >= friendly_threshold:
            return DiplomaticStatus.NEUTRAL
        elif tension >= alliance_threshold:
            return DiplomaticStatus.FRIENDLY
        else:
            return DiplomaticStatus.ALLIANCE
    
    def calculate_status_tension_change(self, old_status: Optional[DiplomaticStatus], 
                                      new_status: DiplomaticStatus, 
                                      current_tension: float) -> float:
        """Calculate tension change needed for status change using configured transitions."""
        if old_status == new_status:
            return 0
        
        transitions = self.config.get_relationship_transitions()
        
        # Map status to target tension using configured thresholds
        target_tensions = {
            DiplomaticStatus.WAR: transitions.get("hostile_to_war", 90),
            DiplomaticStatus.HOSTILE: transitions.get("neutral_to_hostile", 60),
            DiplomaticStatus.NEUTRAL: 0,
            DiplomaticStatus.FRIENDLY: transitions.get("neutral_to_friendly", -40),
            DiplomaticStatus.ALLIANCE: transitions.get("friendly_to_alliance", -75)
        }
        
        target_tension = target_tensions.get(new_status, 0)
        return target_tension - current_tension
    
    def is_war_threshold_reached(self, tension: float, war_threshold: Optional[float] = None) -> bool:
        """Check if tension has reached the configured threshold for war."""
        if war_threshold is None:
            tension_config = self.config.get_tension_config()
            war_threshold = tension_config.get("war_threshold", 100.0)
        return tension >= war_threshold
    
    def calculate_decay_amount(self, current_tension: float, hours_passed: float, decay_rate: Optional[float] = None) -> float:
        """Calculate how much tension should decay over time using configured rate."""
        if hours_passed <= 0:
            return 0.0
        
        # Use configured decay rate if not provided
        if decay_rate is None:
            tension_config = self.config.get_tension_config()
            decay_rate = tension_config.get("decay_rate", 0.1)
        
        decay_amount = decay_rate * hours_passed
        
        if current_tension > 0:
            return min(current_tension, decay_amount)
        elif current_tension < 0:
            return min(abs(current_tension), decay_amount)
        
        return 0.0
    
    def apply_tension_limits(self, tension: float, min_tension: Optional[float] = None, max_tension: Optional[float] = None) -> float:
        """Apply configured minimum and maximum limits to tension value."""
        if min_tension is None or max_tension is None:
            tension_config = self.config.get_tension_config()
            min_tension = min_tension or tension_config.get("min_tension", -100.0)
            max_tension = max_tension or tension_config.get("max_tension", 100.0)
        
        return max(min_tension, min(max_tension, tension))
    
    def should_update_status_for_tension(self, tension: float, current_status: DiplomaticStatus) -> Optional[DiplomaticStatus]:
        """Determine if diplomatic status should change based on tension using configured thresholds."""
        tension_config = self.config.get_tension_config()
        war_threshold = tension_config.get("war_threshold", 100.0)
        alliance_threshold = tension_config.get("alliance_threshold", -75.0)
        
        if tension >= war_threshold and current_status != DiplomaticStatus.WAR:
            return DiplomaticStatus.WAR
        elif tension <= alliance_threshold and current_status != DiplomaticStatus.ALLIANCE:
            return DiplomaticStatus.ALLIANCE
        
        return None
    
    def calculate_tension_for_status(self, status: DiplomaticStatus, current_tension: float) -> float:
        """Calculate appropriate tension for a given diplomatic status using configured values."""
        tension_config = self.config.get_tension_config()
        transitions = self.config.get_relationship_transitions()
        
        if status == DiplomaticStatus.WAR:
            return tension_config.get("war_threshold", 100.0)
        elif status == DiplomaticStatus.ALLIANCE:
            return tension_config.get("alliance_threshold", -75.0)
        elif status == DiplomaticStatus.HOSTILE:
            return transitions.get("neutral_to_hostile", 60)
        elif status == DiplomaticStatus.NEUTRAL:
            return current_tension / 2  # Move halfway to neutral
        elif status == DiplomaticStatus.TRUCE:
            return max(-25, current_tension - 50)  # Significant reduction
        
        return current_tension


class TreatyValidator:
    """Utility class for treaty validation and compliance checking."""
    
    def __init__(self):
        """Initialize with configuration loader."""
        self.config = get_diplomacy_config()
    
    @staticmethod
    def validate_treaty_creation(name: str, treaty_type: TreatyType, parties: List[UUID], 
                               terms: Dict, end_date: Optional[datetime]) -> Dict:
        """Validate treaty creation parameters."""
        errors = []
        
        if not name or len(name.strip()) == 0:
            errors.append("Treaty name cannot be empty")
        
        if not parties or len(parties) < 2:
            errors.append("Treaty must have at least 2 parties")
        
        if len(set(parties)) != len(parties):
            errors.append("Treaty parties must be unique")
        
        if end_date and end_date <= datetime.utcnow():
            errors.append("Treaty end date must be in the future")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def calculate_tension_impact(self, treaty_type: TreatyType) -> float:
        """Calculate tension impact of signing a treaty using configured values."""
        treaty_effects = self.config.get_treaty_type_effects(treaty_type.value.upper())
        return treaty_effects.get("tension_change", 0)
    
    def calculate_expiration_impact(self, treaty_type: TreatyType) -> float:
        """Calculate tension impact when a treaty expires using configured values."""
        treaty_effects = self.config.get_treaty_type_effects(treaty_type.value.upper())
        return treaty_effects.get("expiration_tension_impact", 0)
    
    @staticmethod
    def is_treaty_active(treaty: Treaty) -> bool:
        """Check if a treaty is currently active."""
        return (treaty.is_active and 
                (treaty.end_date is None or treaty.end_date > datetime.utcnow()))
    
    @staticmethod
    def is_treaty_expired(treaty: Treaty) -> bool:
        """Check if a treaty has expired naturally."""
        return (treaty.end_date is not None and 
                treaty.end_date <= datetime.utcnow() and
                treaty.status == TreatyStatus.ACTIVE)
    
    @staticmethod
    def can_factions_have_treaty_type(faction_a_id: UUID, faction_b_id: UUID, 
                                    treaty_type: TreatyType, existing_treaties: List[Treaty]) -> bool:
        """Check if two factions can have a specific type of treaty."""
        # Check for conflicting treaty types
        for treaty in existing_treaties:
            if not TreatyValidator.is_treaty_active(treaty):
                continue
                
            if set([faction_a_id, faction_b_id]).issubset(set(treaty.parties)):
                # Check for conflicting types
                if treaty_type == TreatyType.ALLIANCE and treaty.treaty_type == TreatyType.NON_AGGRESSION:
                    return False  # Can't have both
                if treaty_type == TreatyType.NON_AGGRESSION and treaty.treaty_type == TreatyType.ALLIANCE:
                    return False
                if treaty_type == treaty.treaty_type:
                    return False  # Can't have duplicate types
        
        return True
    
    @staticmethod
    def calculate_treaty_violation_severity(violation_type: TreatyViolationType, 
                                          evidence_strength: int, treaty_importance: int) -> int:
        """Calculate severity score for a treaty violation."""
        base_severity = {
            TreatyViolationType.BREACH_OF_TERMS: 40,
            TreatyViolationType.MILITARY_AGGRESSION: 80,
            TreatyViolationType.TRADE_VIOLATION: 30,
            TreatyViolationType.TERRITORIAL_VIOLATION: 70,
            TreatyViolationType.ESPIONAGE: 50,
            TreatyViolationType.ALLIANCE_BETRAYAL: 90,
            TreatyViolationType.RESOURCE_THEFT: 45,
            TreatyViolationType.DIPLOMATIC_INSULT: 20
        }.get(violation_type, 40)
        
        # Adjust based on evidence and treaty importance
        severity = base_severity + (evidence_strength // 10) + (treaty_importance // 5)
        
        return max(10, min(100, severity))


class NegotiationAnalyzer:
    """Utility class for negotiation analysis and decision making."""
    
    @staticmethod
    def is_high_stakes_negotiation(negotiation: Negotiation) -> bool:
        """Determine if a negotiation is high-stakes based on its characteristics."""
        if not negotiation.treaty_type:
            return False
        
        high_stakes_types = [
            TreatyType.ALLIANCE,
            TreatyType.MUTUAL_DEFENSE,
            TreatyType.PEACE,
            TreatyType.CEASEFIRE
        ]
        
        # Check if it's a high-stakes type
        if negotiation.treaty_type in high_stakes_types:
            return True
        
        # Check if it involves many parties (3+)
        if len(negotiation.parties) >= 3:
            return True
        
        # Check metadata for importance indicators
        if negotiation.metadata and negotiation.metadata.get('importance') == 'critical':
            return True
        
        return False
    
    @staticmethod
    def calculate_offer_attractiveness(offer: NegotiationOffer, recipient_faction: UUID) -> int:
        """Calculate how attractive an offer is to the recipient faction."""
        base_score = 50
        
        if not offer.terms:
            return base_score
        
        # Analyze terms for attractiveness
        terms = offer.terms
        
        # Positive factors
        if 'trade_benefits' in terms:
            base_score += 20
        if 'military_support' in terms:
            base_score += 15
        if 'resource_sharing' in terms:
            base_score += 10
        if 'technology_transfer' in terms:
            base_score += 25
        
        # Negative factors
        if 'reparations' in terms:
            base_score -= 30
        if 'territorial_concessions' in terms:
            base_score -= 25
        if 'military_restrictions' in terms:
            base_score -= 20
        
        return max(0, min(100, base_score))
    
    @staticmethod
    def should_automatically_reject_offer(offer: NegotiationOffer, faction_policies: Dict) -> bool:
        """Determine if an offer should be automatically rejected based on faction policies."""
        if not offer.terms or not faction_policies:
            return False
        
        # Check for deal-breakers
        if 'territorial_concessions' in offer.terms and faction_policies.get('never_cede_territory', False):
            return True
        
        if 'reparations' in offer.terms and offer.terms['reparations'] > faction_policies.get('max_reparations', float('inf')):
            return True
        
        if 'military_restrictions' in offer.terms and faction_policies.get('military_independence', False):
            return True
        
        return False


class IncidentAnalyzer:
    """Utility class for diplomatic incident analysis."""
    
    def __init__(self):
        """Initialize with configuration loader."""
        self.config = get_diplomacy_config()
    
    def get_default_violation_severity(self) -> int:
        """Get default violation severity from configuration."""
        defaults = self.config.get_default_values()
        return defaults.get("violation_severity", 50)
    
    def calculate_violation_tension_impact(self, severity: int, parties: List[UUID], 
                                         violator_id: UUID) -> Dict[str, int]:
        """Calculate tension impact for all parties involved in a violation."""
        # Use configured penalty values
        violation_penalties = self.config.get_violation_penalties()
        base_impact = violation_penalties.get("base_tension_impact", 25)
        
        impact = {}
        for party_id in parties:
            if party_id != violator_id:
                # Non-violator parties get negative impact (increased tension toward violator)
                impact[str(party_id)] = base_impact + (severity // 5)
            else:
                # Violator gets minimal impact on themselves
                impact[str(party_id)] = severity // 10
        
        return impact
    
    def calculate_acknowledgment_tension_change(self) -> int:
        """Get tension change when a violation is acknowledged from configuration."""
        violation_penalties = self.config.get_violation_penalties()
        return violation_penalties.get("acknowledgment_tension_reduction", -5)
    
    def calculate_resolution_severity(self, violation_severity: int) -> float:
        """Calculate resolution severity multiplier based on violation."""
        return violation_severity / 100.0
    
    def calculate_incident_tension_impact(self, incident_type: DiplomaticIncidentType, 
                                        severity: DiplomaticIncidentSeverity) -> int:
        """Calculate tension impact of a diplomatic incident using configured values."""
        incident_config = self.config.get_incident_severity_config()
        
        # Get base impact for incident type
        type_impacts = incident_config.get("type_impacts", {})
        base_impact = type_impacts.get(incident_type.value.upper(), 20)
        
        # Apply severity multiplier
        severity_multipliers = incident_config.get("severity_multipliers", {})
        multiplier = severity_multipliers.get(severity.value.upper(), 1.0)
        
        return int(base_impact * multiplier)
    
    def should_incident_escalate(self, incident: DiplomaticIncident, faction_relationship: Dict) -> bool:
        """Determine if an incident should escalate based on configuration thresholds."""
        thresholds = self.config.get_thresholds()
        escalation_threshold = thresholds.get("incident_escalation_threshold", 70)
        
        # Calculate escalation probability based on factors
        current_tension = faction_relationship.get('tension', 0)
        incident_severity = getattr(incident.severity, 'value', 1) if hasattr(incident.severity, 'value') else 1
        
        # Higher tension and severity increase escalation chance
        escalation_score = current_tension + (incident_severity * 10)
        
        return escalation_score >= escalation_threshold


class SanctionCalculator:
    """Utility class for sanction calculations."""
    
    def __init__(self):
        """Initialize with configuration loader."""
        self.config = get_diplomacy_config()
    
    def get_default_severity(self) -> int:
        """Get default sanction severity from configuration."""
        defaults = self.config.get_default_values()
        return defaults.get("sanction_severity", 50)
    
    def get_default_economic_impact(self) -> int:
        """Get default economic impact from configuration."""
        defaults = self.config.get_default_values()
        return defaults.get("economic_impact", 30)
    
    def get_default_diplomatic_impact(self) -> int:
        """Get default diplomatic impact from configuration."""
        defaults = self.config.get_default_values()
        return defaults.get("diplomatic_impact", 25)
    
    def calculate_tension_impact(self, severity: int, sanction_type: SanctionType) -> int:
        """Calculate tension impact of sanctions using configured values."""
        actions_config = self.config.get_diplomatic_actions()
        sanction_impacts = actions_config.get("sanction_impacts", {})
        
        # Get base impact for sanction type
        base_impact = sanction_impacts.get(sanction_type.value.upper(), 15)
        
        # Scale by severity
        return base_impact + (severity // 5)
    
    def calculate_event_severity(self, severity: int) -> int:
        """Calculate event severity based on sanction severity."""
        # Map sanction severity to event severity
        if severity >= 80:
            return 90
        elif severity >= 60:
            return 70
        elif severity >= 40:
            return 50
        elif severity >= 20:
            return 30
        else:
            return 10
    
    def get_incident_thresholds(self) -> Dict[str, int]:
        """Get incident threshold configuration."""
        return self.config.get_thresholds()
    
    def calculate_sanction_severity(self, sanction_type: SanctionType, 
                                  economic_impact: int, diplomatic_impact: int) -> int:
        """Calculate overall sanction severity using configured type weights."""
        actions_config = self.config.get_diplomatic_actions()
        type_weights = actions_config.get("sanction_type_weights", {})
        
        # Get weight for sanction type
        type_weight = type_weights.get(sanction_type.value.upper(), 1.0)
        
        # Calculate weighted severity
        base_severity = (economic_impact + diplomatic_impact) // 2
        weighted_severity = int(base_severity * type_weight)
        
        return max(10, min(100, weighted_severity))
    
    def calculate_sanction_effectiveness(self, sanction: Sanction, target_faction_strength: int) -> float:
        """Calculate how effective a sanction is against the target."""
        # Base effectiveness starts at sanction severity
        base_effectiveness = getattr(sanction, 'severity', 50) / 100.0
        
        # Adjust based on target strength (stronger factions are less affected)
        strength_modifier = max(0.1, 1.0 - (target_faction_strength / 200.0))
        
        # Sanction type modifiers
        type_effectiveness = {
            SanctionType.ECONOMIC: 0.8,
            SanctionType.MILITARY: 1.0,
            SanctionType.DIPLOMATIC: 0.6,
            SanctionType.TRADE: 0.9,
            SanctionType.TRAVEL: 0.4
        }
        
        sanction_type = getattr(sanction, 'sanction_type', SanctionType.ECONOMIC)
        type_modifier = type_effectiveness.get(sanction_type, 0.7)
        
        # Duration modifier (longer sanctions are more effective)
        duration_modifier = 1.0
        if hasattr(sanction, 'end_date') and sanction.end_date:
            start_date = getattr(sanction, 'start_date', datetime.utcnow())
            duration_days = (sanction.end_date - start_date).days
            duration_modifier = min(2.0, 1.0 + (duration_days / 365.0))
        
        final_effectiveness = base_effectiveness * strength_modifier * type_modifier * duration_modifier
        return max(0.0, min(1.0, final_effectiveness))


class UltimatumEvaluator:
    """Utility class for ultimatum evaluation and decision making."""
    
    @staticmethod
    def calculate_ultimatum_acceptance_probability(ultimatum: Ultimatum, 
                                                 target_faction_strength: int,
                                                 issuer_faction_strength: int) -> float:
        """Calculate the probability that an ultimatum will be accepted."""
        # Base probability depends on relative strength
        strength_ratio = issuer_faction_strength / max(target_faction_strength, 1)
        base_prob = min(0.8, strength_ratio * 0.4)
        
        # Adjust based on demands and consequences
        if ultimatum.demands:
            demand_severity = len(ultimatum.demands) * 0.1
            base_prob -= demand_severity
        
        if ultimatum.consequences:
            consequence_severity = len(ultimatum.consequences) * 0.15
            base_prob += consequence_severity
        
        # Time pressure affects acceptance
        if ultimatum.deadline:
            time_left = ultimatum.deadline - datetime.utcnow()
            if time_left.total_seconds() < 86400:  # Less than 24 hours
                base_prob += 0.2
        
        return max(0.05, min(0.95, base_prob))
    
    @staticmethod
    def calculate_ultimatum_tension_impact(ultimatum: Ultimatum, accepted: bool) -> int:
        """Calculate tension impact of ultimatum response."""
        base_impact = 30  # Issuing an ultimatum increases tension
        
        if accepted:
            # Acceptance reduces tension somewhat
            return base_impact - 15
        else:
            # Rejection significantly increases tension
            consequence_count = len(ultimatum.consequences) if ultimatum.consequences else 1
            return base_impact + (consequence_count * 10)


class DiplomaticEventGenerator:
    """Utility class for generating diplomatic events."""
    
    @staticmethod
    def generate_treaty_event(treaty: Treaty) -> DiplomaticEvent:
        """Generate an event for treaty signing."""
        return DiplomaticEvent(
            event_type=DiplomaticEventType.TREATY_SIGNED,
            factions=treaty.parties,
            description=f"Treaty '{treaty.name}' signed between factions",
            severity=40,
            public=treaty.is_public,
            related_treaty_id=treaty.id,
            metadata={
                "treaty_type": str(treaty.type),
                "treaty_name": treaty.name,
                "parties_count": len(treaty.parties)
            }
        )
    
    @staticmethod
    def generate_treaty_expiration_event(treaty: Treaty) -> DiplomaticEvent:
        """Generate an event for treaty expiration."""
        return DiplomaticEvent(
            event_type=DiplomaticEventType.TREATY_EXPIRED,
            factions=treaty.parties,
            description=f"Treaty '{treaty.name}' has expired",
            severity=30,
            public=treaty.is_public,
            related_treaty_id=treaty.id,
            metadata={
                "treaty_type": str(treaty.type),
                "treaty_name": treaty.name,
                "expiration_date": treaty.end_date.isoformat() if treaty.end_date else None
            }
        )
    
    @staticmethod
    def create_tension_change_event(faction_a_id: UUID, faction_b_id: UUID, 
                                  old_tension: float, new_tension: float, 
                                  reason: Optional[str] = None) -> DiplomaticEvent:
        """Create an event for tension changes between factions."""
        tension_change = new_tension - old_tension
        severity = min(abs(tension_change), 50)  # Cap at 50 for tension events
        
        if tension_change > 0:
            description = f"Tension increased between factions ({old_tension} → {new_tension})"
        else:
            description = f"Tension decreased between factions ({old_tension} → {new_tension})"
        
        if reason:
            description += f" due to: {reason}"
        
        return DiplomaticEvent(
            event_type=DiplomaticEventType.TENSION_CHANGE,
            factions=[faction_a_id, faction_b_id],
            description=description,
            severity=int(severity),
            public=False,  # Tension changes are usually internal
            metadata={
                "old_tension": old_tension,
                "new_tension": new_tension,
                "tension_change": tension_change,
                "reason": reason
            }
        )
    
    @staticmethod
    def create_treaty_event(treaty: Treaty, event_type: DiplomaticEventType) -> DiplomaticEvent:
        """Create a diplomatic event related to a treaty."""
        event_descriptions = {
            DiplomaticEventType.TREATY_SIGNED: f"Treaty '{treaty.name}' signed",
            DiplomaticEventType.TREATY_EXPIRED: f"Treaty '{treaty.name}' expired",
            DiplomaticEventType.TREATY_VIOLATION: f"Treaty '{treaty.name}' violated",
            DiplomaticEventType.TREATY_BREACH: f"Treaty '{treaty.name}' breached"
        }
        
        description = event_descriptions.get(event_type, f"Treaty event: {treaty.name}")
        
        severities = {
            DiplomaticEventType.TREATY_SIGNED: 40,
            DiplomaticEventType.TREATY_EXPIRED: 30,
            DiplomaticEventType.TREATY_VIOLATION: 60,
            DiplomaticEventType.TREATY_BREACH: 80
        }
        
        severity = severities.get(event_type, 40)
        
        return DiplomaticEvent(
            event_type=event_type,
            factions=treaty.parties,
            description=description,
            severity=severity,
            public=treaty.is_public,
            related_treaty_id=treaty.id,
            metadata={
                "treaty_type": str(treaty.type),
                "treaty_name": treaty.name
            }
        )
    
    @staticmethod
    def create_negotiation_event(negotiation: Negotiation, action: str) -> DiplomaticEvent:
        """Create a diplomatic event for negotiation actions."""
        parties_str = ", ".join([str(faction_id) for faction_id in negotiation.parties])
        description = f"Negotiation {action} between {parties_str}"
        
        if negotiation.treaty_type:
            description += f" for {negotiation.treaty_type} treaty"
        
        severities = {
            "started": 20,
            "concluded": 40,
            "failed": 30,
            "offer_made": 15,
            "offer_accepted": 35,
            "offer_rejected": 25
        }
        
        severity = severities.get(action, 20)
        
        return DiplomaticEvent(
            event_type=DiplomaticEventType.NEGOTIATION,
            factions=negotiation.parties,
            description=description,
            severity=severity,
            public=True,
            related_negotiation_id=negotiation.id,
            metadata={
                "action": action,
                "treaty_type": str(negotiation.treaty_type) if negotiation.treaty_type else None,
                "initiator_id": str(negotiation.initiator_id)
            }
        ) 