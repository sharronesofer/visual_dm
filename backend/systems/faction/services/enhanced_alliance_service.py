"""
Enhanced Alliance Service

This service extends the base alliance functionality with advanced diplomacy features:
- Multi-party alliance negotiations
- Dynamic treaty term generation based on faction personalities
- Comprehensive relationship tracking and history
- Complex negotiation workflows

Pure business logic implementation.
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from backend.systems.faction.models.alliance import (
    AllianceModel, BetrayalEvent, AllianceEntity, BetrayalEntity,
    AllianceType, AllianceStatus, BetrayalReason,
    CreateAllianceRequest, UpdateAllianceRequest
)


class NegotiationPhase(Enum):
    """Phases of alliance negotiation"""
    PROPOSAL = "proposal"
    COUNTER_PROPOSAL = "counter_proposal"
    TERMS_DISCUSSION = "terms_discussion"
    FINAL_REVIEW = "final_review"
    RATIFICATION = "ratification"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED = "expired"


class NegotiationStance(Enum):
    """Faction stances during negotiation"""
    EAGER = "eager"            # Wants the alliance badly
    INTERESTED = "interested"  # Open to discussion
    CAUTIOUS = "cautious"      # Willing but careful
    RELUCTANT = "reluctant"    # Needs convincing
    HOSTILE = "hostile"        # Strongly opposed


@dataclass
class NegotiationPosition:
    """A faction's position in alliance negotiations"""
    faction_id: UUID
    faction_name: str
    stance: NegotiationStance
    priority_terms: List[str]
    deal_breakers: List[str]
    concessions_offered: Dict[str, Any]
    demands: Dict[str, Any]
    trust_requirements: float
    minimum_benefit_threshold: float
    negotiation_flexibility: float  # 0.0 to 1.0
    time_pressure: float = 0.0  # How urgently they need this alliance


@dataclass
class AllianceTerms:
    """Comprehensive alliance terms structure"""
    # Core alliance details
    alliance_name: str
    alliance_type: str
    duration_months: Optional[int] = None  # None = indefinite
    auto_renew: bool = False
    
    # Military terms
    mutual_defense: bool = False
    offensive_coordination: bool = False
    military_support_level: float = 0.0  # 0.0 to 1.0
    shared_intelligence: bool = False
    joint_military_exercises: bool = False
    
    # Economic terms
    trade_preferences: bool = False
    resource_sharing: Dict[str, float] = field(default_factory=dict)
    economic_support_level: float = 0.0
    shared_infrastructure: bool = False
    joint_economic_projects: bool = False
    
    # Diplomatic terms
    diplomatic_coordination: bool = False
    shared_embassies: bool = False
    cultural_exchange: bool = False
    joint_diplomatic_missions: bool = False
    
    # Territorial terms
    territory_access: Dict[str, List[str]] = field(default_factory=dict)
    shared_borders: bool = False
    territorial_guarantees: bool = False
    
    # Special provisions
    exit_clauses: List[str] = field(default_factory=list)
    review_schedule: Optional[str] = None
    dispute_resolution: str = "negotiation"
    penalty_clauses: Dict[str, Any] = field(default_factory=dict)
    
    # Conditional terms
    activation_triggers: List[str] = field(default_factory=list)
    suspension_conditions: List[str] = field(default_factory=list)


@dataclass
class MultiPartyNegotiation:
    """Manages multi-party alliance negotiations"""
    negotiation_id: UUID
    initiator_id: UUID
    participating_factions: List[UUID]
    
    current_phase: NegotiationPhase
    current_terms: AllianceTerms
    faction_positions: Dict[UUID, NegotiationPosition]
    
    negotiation_history: List[Dict[str, Any]] = field(default_factory=list)
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Negotiation state
    rounds_completed: int = 0
    max_rounds: int = 10
    consensus_threshold: float = 0.75  # % of factions that must agree
    
    # External factors
    external_pressures: Dict[str, Any] = field(default_factory=dict)
    time_sensitive_factors: List[str] = field(default_factory=list)


# Protocols for dependency injection

class FactionDataProvider(Protocol):
    """Protocol for accessing faction data"""
    
    def get_faction_by_id(self, faction_id: UUID) -> Optional[Dict[str, Any]]:
        """Get faction data by ID"""
        ...
    
    def get_faction_hidden_attributes(self, faction_id: UUID) -> Dict[str, int]:
        """Get faction's hidden attributes"""
        ...


class DiplomacyDataProvider(Protocol):
    """Protocol for accessing diplomacy data"""
    
    def get_diplomatic_status(self, faction_a_id: UUID, faction_b_id: UUID) -> str:
        """Get diplomatic status between factions"""
        ...
    
    def get_treaty_type(self, faction_a_id: UUID, faction_b_id: UUID) -> Optional[str]:
        """Get treaty type between factions"""
        ...


class ConfigurationProvider(Protocol):
    """Protocol for accessing configuration"""
    
    def get_negotiation_config(self) -> Dict[str, Any]:
        """Get negotiation configuration"""
        ...


class EnhancedAllianceService:
    """Enhanced service for complex alliance negotiations and management - pure business logic"""
    
    def __init__(self, 
                 faction_data_provider: FactionDataProvider,
                 diplomacy_data_provider: Optional[DiplomacyDataProvider] = None,
                 config_provider: Optional[ConfigurationProvider] = None):
        """Initialize the enhanced alliance service"""
        self.faction_data_provider = faction_data_provider
        self.diplomacy_data_provider = diplomacy_data_provider
        self.config_provider = config_provider
        
        # Track active negotiations
        self.active_negotiations: Dict[UUID, MultiPartyNegotiation] = {}
        
        # Configuration for enhanced features
        self.negotiation_config = {
            "default_negotiation_duration_days": 30,
            "max_negotiation_rounds": 15,
            "consensus_threshold": 0.75,
            "minimum_participants": 2,
            "maximum_participants": 8,
            "trust_threshold_for_complex_terms": 0.6,
            "personality_weight_in_negotiations": 0.4
        }
        
        # Override with config provider if available
        if self.config_provider:
            provider_config = self.config_provider.get_negotiation_config()
            self.negotiation_config.update(provider_config)
    
    def initiate_multi_party_alliance(self, 
                                    initiator_id: UUID,
                                    target_faction_ids: List[UUID],
                                    alliance_type: str = "military",
                                    proposed_terms: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initiate a multi-party alliance negotiation - business logic only
        
        Args:
            initiator_id: Faction starting the negotiation
            target_faction_ids: List of factions to invite
            alliance_type: Type of alliance to propose
            proposed_terms: Initial terms proposed by initiator
            
        Returns:
            Dict with negotiation details and initial responses
        """
        # Business rules validation
        all_faction_ids = [initiator_id] + target_faction_ids
        if len(all_faction_ids) < self.negotiation_config["minimum_participants"]:
            return {"error": "Not enough participants for alliance"}
        
        if len(all_faction_ids) > self.negotiation_config["maximum_participants"]:
            return {"error": "Too many participants for single alliance"}
        
        # Validate all factions exist
        factions = {}
        for faction_id in all_faction_ids:
            faction_data = self.faction_data_provider.get_faction_by_id(faction_id)
            if not faction_data:
                return {"error": f"Faction {faction_id} not found"}
            factions[faction_id] = faction_data
        
        # Business logic: Generate initial alliance terms
        alliance_terms = self._generate_initial_alliance_terms(
            alliance_type, initiator_id, target_faction_ids, proposed_terms
        )
        
        # Business logic: Create negotiation
        negotiation_id = uuid4()
        negotiation = MultiPartyNegotiation(
            negotiation_id=negotiation_id,
            initiator_id=initiator_id,
            participating_factions=all_faction_ids,
            current_phase=NegotiationPhase.PROPOSAL,
            current_terms=alliance_terms,
            faction_positions={},
            deadline=datetime.utcnow() + timedelta(
                days=self.negotiation_config["default_negotiation_duration_days"]
            )
        )
        
        # Business logic: Evaluate each faction's position
        for faction_id in all_faction_ids:
            position = self._evaluate_faction_negotiation_position(
                faction_id, all_faction_ids, alliance_type, alliance_terms
            )
            negotiation.faction_positions[faction_id] = position
        
        # Business logic: Generate initial responses
        initial_responses = self._generate_initial_faction_responses(negotiation)
        
        # Store negotiation
        self.active_negotiations[negotiation_id] = negotiation
        
        # Business logic: Create event log
        self._log_negotiation_event(negotiation, "negotiation_initiated", {
            "initiator": str(initiator_id),
            "targets": [str(fid) for fid in target_faction_ids],
            "alliance_type": alliance_type
        })
        
        return {
            "negotiation_id": str(negotiation_id),
            "status": "initiated",
            "current_phase": negotiation.current_phase.value,
            "participants": [str(fid) for fid in all_faction_ids],
            "deadline": negotiation.deadline.isoformat(),
            "initial_responses": initial_responses,
            "terms_summary": self._serialize_alliance_terms(alliance_terms)
        }

    def advance_negotiation(self, negotiation_id: UUID, 
                          faction_id: UUID,
                          action: str,
                          parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Advance a negotiation based on faction action - business logic only
        
        Args:
            negotiation_id: ID of the negotiation
            faction_id: Faction taking the action
            action: Type of action to take
            parameters: Action-specific parameters
            
        Returns:
            Dict with negotiation update results
        """
        if negotiation_id not in self.active_negotiations:
            return {"error": "Negotiation not found"}
        
        negotiation = self.active_negotiations[negotiation_id]
        
        # Business rules: Validate faction participation
        if faction_id not in negotiation.participating_factions:
            return {"error": "Faction not part of this negotiation"}
        
        # Business rules: Check if negotiation is still active
        if negotiation.current_phase in [NegotiationPhase.COMPLETED, 
                                       NegotiationPhase.REJECTED, 
                                       NegotiationPhase.EXPIRED]:
            return {"error": "Negotiation is no longer active"}
        
        # Business logic: Process the action
        action_result = self._process_negotiation_action(
            negotiation, faction_id, action, parameters
        )
        
        if "error" in action_result:
            return action_result
        
        # Business logic: Check for phase transitions
        self._evaluate_phase_transition(negotiation)
        
        # Business logic: Update negotiation state
        negotiation.rounds_completed += 1
        
        # Business logic: Check for completion conditions
        success_probability = self._calculate_negotiation_success_probability(negotiation)
        
        return {
            "negotiation_id": str(negotiation_id),
            "action_result": action_result,
            "current_phase": negotiation.current_phase.value,
            "rounds_completed": negotiation.rounds_completed,
            "success_probability": success_probability,
            "available_actions": self._get_available_actions(negotiation, faction_id)
        }

    def get_negotiation_status(self, negotiation_id: UUID) -> Dict[str, Any]:
        """
        Get current status of a negotiation - business logic only
        
        Args:
            negotiation_id: ID of the negotiation
            
        Returns:
            Dict with negotiation status
        """
        if negotiation_id not in self.active_negotiations:
            return {"error": "Negotiation not found"}
        
        negotiation = self.active_negotiations[negotiation_id]
        
        # Business logic: Calculate time remaining
        time_remaining = None
        if negotiation.deadline:
            remaining = negotiation.deadline - datetime.utcnow()
            time_remaining = remaining.total_seconds() if remaining.total_seconds() > 0 else 0
        
        # Business logic: Get faction stances
        faction_stances = {
            str(faction_id): position.stance.value
            for faction_id, position in negotiation.faction_positions.items()
        }
        
        return {
            "negotiation_id": str(negotiation_id),
            "current_phase": negotiation.current_phase.value,
            "time_remaining_seconds": time_remaining,
            "participants": [str(fid) for fid in negotiation.participating_factions],
            "faction_stances": faction_stances,
            "rounds_completed": negotiation.rounds_completed,
            "max_rounds": negotiation.max_rounds,
            "success_probability": self._calculate_negotiation_success_probability(negotiation),
            "terms_summary": self._serialize_alliance_terms(negotiation.current_terms)
        }

    def list_active_negotiations(self, faction_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """
        List active negotiations, optionally filtered by faction - business logic only
        
        Args:
            faction_id: Optional faction ID to filter by
            
        Returns:
            List of negotiation summaries
        """
        negotiations = []
        
        for neg_id, negotiation in self.active_negotiations.items():
            # Business logic: Filter by faction if specified
            if faction_id and faction_id not in negotiation.participating_factions:
                continue
            
            # Business logic: Only include active negotiations
            if negotiation.current_phase in [NegotiationPhase.COMPLETED, 
                                           NegotiationPhase.REJECTED, 
                                           NegotiationPhase.EXPIRED]:
                continue
            
            negotiations.append({
                "negotiation_id": str(neg_id),
                "current_phase": negotiation.current_phase.value,
                "participants": [str(fid) for fid in negotiation.participating_factions],
                "alliance_type": negotiation.current_terms.alliance_type,
                "deadline": negotiation.deadline.isoformat() if negotiation.deadline else None,
                "rounds_completed": negotiation.rounds_completed
            })
        
        return negotiations

    # Private business logic methods
    
    def _generate_initial_alliance_terms(self, alliance_type: str, 
                                       initiator_id: UUID,
                                       target_faction_ids: List[UUID],
                                       proposed_terms: Optional[Dict[str, Any]] = None) -> AllianceTerms:
        """Generate initial alliance terms based on business rules"""
        # Business logic: Basic terms based on alliance type
        terms = AllianceTerms(
            alliance_name=f"{alliance_type.title()} Alliance",
            alliance_type=alliance_type,
            duration_months=None,  # Default to indefinite
            auto_renew=False
        )
        
        # Business rules: Apply type-specific defaults
        if alliance_type == "military":
            terms.mutual_defense = True
            terms.military_support_level = 0.5
            terms.shared_intelligence = True
        elif alliance_type == "economic":
            terms.trade_preferences = True
            terms.economic_support_level = 0.6
            terms.shared_infrastructure = True
        elif alliance_type == "diplomatic":
            terms.diplomatic_coordination = True
            terms.cultural_exchange = True
            terms.shared_embassies = True
        
        # Business logic: Apply proposed terms overrides
        if proposed_terms:
            for key, value in proposed_terms.items():
                if hasattr(terms, key):
                    setattr(terms, key, value)
        
        return terms
    
    def _evaluate_faction_negotiation_position(self, faction_id: UUID,
                                             all_faction_ids: List[UUID],
                                             alliance_type: str,
                                             terms: AllianceTerms) -> NegotiationPosition:
        """Evaluate a faction's negotiation position based on business rules"""
        faction_data = self.faction_data_provider.get_faction_by_id(faction_id)
        if not faction_data:
            # Fallback business logic for missing faction
            return NegotiationPosition(
                faction_id=faction_id,
                faction_name=f"Faction_{faction_id}",
                stance=NegotiationStance.CAUTIOUS,
                priority_terms=[],
                deal_breakers=[],
                concessions_offered={},
                demands={},
                trust_requirements=0.5,
                minimum_benefit_threshold=0.3,
                negotiation_flexibility=0.5
            )
        
        # Business logic: Get hidden attributes for personality analysis
        hidden_attrs = self.faction_data_provider.get_faction_hidden_attributes(faction_id)
        
        # Business rules: Determine stance based on attributes
        stance = self._determine_negotiation_stance(hidden_attrs, alliance_type)
        
        # Business rules: Determine priorities and deal breakers
        priority_terms = self._determine_priority_terms(hidden_attrs, alliance_type)
        deal_breakers = self._determine_deal_breakers(hidden_attrs, alliance_type)
        
        # Business rules: Calculate negotiation metrics
        trust_requirements = self._calculate_trust_requirements(hidden_attrs)
        flexibility = self._calculate_negotiation_flexibility(hidden_attrs)
        benefit_threshold = self._calculate_benefit_threshold(hidden_attrs)
        
        return NegotiationPosition(
            faction_id=faction_id,
            faction_name=faction_data.get("name", f"Faction_{faction_id}"),
            stance=stance,
            priority_terms=priority_terms,
            deal_breakers=deal_breakers,
            concessions_offered={},
            demands={},
            trust_requirements=trust_requirements,
            minimum_benefit_threshold=benefit_threshold,
            negotiation_flexibility=flexibility
        )
    
    def _generate_initial_faction_responses(self, negotiation: MultiPartyNegotiation) -> Dict[str, Any]:
        """Generate initial faction responses based on business rules"""
        responses = {}
        
        for faction_id, position in negotiation.faction_positions.items():
            response = self._generate_faction_response(negotiation, faction_id)
            responses[str(faction_id)] = response
        
        return responses
    
    def _generate_faction_response(self, negotiation: MultiPartyNegotiation, faction_id: UUID) -> Dict[str, Any]:
        """Generate a faction's response based on business rules"""
        position = negotiation.faction_positions[faction_id]
        
        # Business logic: Response based on stance
        if position.stance == NegotiationStance.EAGER:
            return {"response": "accept", "message": "We are very interested in this alliance"}
        elif position.stance == NegotiationStance.INTERESTED:
            return {"response": "counter_proposal", "message": "We're interested but have some concerns"}
        elif position.stance == NegotiationStance.CAUTIOUS:
            return {"response": "request_details", "message": "We need more information before proceeding"}
        elif position.stance == NegotiationStance.RELUCTANT:
            return {"response": "conditional_interest", "message": "We might consider under certain conditions"}
        else:  # HOSTILE
            return {"response": "reject", "message": "We are not interested in this alliance"}
    
    def _serialize_alliance_terms(self, terms: AllianceTerms) -> Dict[str, Any]:
        """Serialize alliance terms for business logic consumption"""
        return {
            "alliance_name": terms.alliance_name,
            "alliance_type": terms.alliance_type,
            "duration_months": terms.duration_months,
            "auto_renew": terms.auto_renew,
            "military_terms": {
                "mutual_defense": terms.mutual_defense,
                "offensive_coordination": terms.offensive_coordination,
                "military_support_level": terms.military_support_level,
                "shared_intelligence": terms.shared_intelligence,
                "joint_military_exercises": terms.joint_military_exercises
            },
            "economic_terms": {
                "trade_preferences": terms.trade_preferences,
                "resource_sharing": terms.resource_sharing,
                "economic_support_level": terms.economic_support_level,
                "shared_infrastructure": terms.shared_infrastructure,
                "joint_economic_projects": terms.joint_economic_projects
            },
            "diplomatic_terms": {
                "diplomatic_coordination": terms.diplomatic_coordination,
                "shared_embassies": terms.shared_embassies,
                "cultural_exchange": terms.cultural_exchange,
                "joint_diplomatic_missions": terms.joint_diplomatic_missions
            }
        }
    
    def _log_negotiation_event(self, negotiation: MultiPartyNegotiation, event_type: str, data: Dict[str, Any]):
        """Log negotiation event with business logic"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "phase": negotiation.current_phase.value,
            "round": negotiation.rounds_completed,
            "data": data
        }
        negotiation.negotiation_history.append(event)
    
    def _calculate_negotiation_success_probability(self, negotiation: MultiPartyNegotiation) -> float:
        """Calculate success probability based on business rules"""
        if not negotiation.faction_positions:
            return 0.0
        
        # Business logic: Average stance scores
        stance_scores = {
            NegotiationStance.EAGER: 1.0,
            NegotiationStance.INTERESTED: 0.8,
            NegotiationStance.CAUTIOUS: 0.5,
            NegotiationStance.RELUCTANT: 0.2,
            NegotiationStance.HOSTILE: 0.0
        }
        
        total_score = sum(stance_scores[pos.stance] for pos in negotiation.faction_positions.values())
        max_score = len(negotiation.faction_positions)
        
        return total_score / max_score if max_score > 0 else 0.0
    
    def _process_negotiation_action(self, negotiation: MultiPartyNegotiation,
                                  faction_id: UUID, action: str,
                                  parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process negotiation action with business rules"""
        # Business logic placeholder - would contain complex action processing
        return {"status": "processed", "action": action}
    
    def _evaluate_phase_transition(self, negotiation: MultiPartyNegotiation):
        """Evaluate if negotiation should transition phases - business logic"""
        # Business logic placeholder for phase transitions
        pass
    
    def _get_available_actions(self, negotiation: MultiPartyNegotiation, faction_id: UUID) -> List[str]:
        """Get available actions for faction based on business rules"""
        # Business logic placeholder
        return ["propose_terms", "accept_terms", "reject_terms", "request_modification"]
    
    # Business logic helper methods for faction analysis
    
    def _determine_negotiation_stance(self, hidden_attrs: Dict[str, int], alliance_type: str) -> NegotiationStance:
        """Determine negotiation stance based on business rules"""
        ambition = hidden_attrs.get("hidden_ambition", 5)
        pragmatism = hidden_attrs.get("hidden_pragmatism", 5)
        
        if ambition >= 8 and pragmatism >= 6:
            return NegotiationStance.EAGER
        elif pragmatism >= 7:
            return NegotiationStance.INTERESTED
        elif pragmatism >= 4:
            return NegotiationStance.CAUTIOUS
        elif ambition <= 3:
            return NegotiationStance.RELUCTANT
        else:
            return NegotiationStance.HOSTILE
    
    def _determine_priority_terms(self, hidden_attrs: Dict[str, int], alliance_type: str) -> List[str]:
        """Determine priority terms based on business rules"""
        priorities = []
        
        ambition = hidden_attrs.get("hidden_ambition", 5)
        discipline = hidden_attrs.get("hidden_discipline", 5)
        
        if ambition >= 7:
            priorities.append("offensive_coordination")
        if discipline >= 6:
            priorities.append("mutual_defense")
        
        return priorities
    
    def _determine_deal_breakers(self, hidden_attrs: Dict[str, int], alliance_type: str) -> List[str]:
        """Determine deal breakers based on business rules"""
        deal_breakers = []
        
        integrity = hidden_attrs.get("hidden_integrity", 5)
        
        if integrity >= 8:
            deal_breakers.append("offensive_coordination_against_innocents")
        
        return deal_breakers
    
    def _calculate_trust_requirements(self, hidden_attrs: Dict[str, int]) -> float:
        """Calculate trust requirements based on business rules"""
        integrity = hidden_attrs.get("hidden_integrity", 5)
        return 0.3 + (integrity / 20.0)  # 0.3 to 0.8 range
    
    def _calculate_negotiation_flexibility(self, hidden_attrs: Dict[str, int]) -> float:
        """Calculate negotiation flexibility based on business rules"""
        pragmatism = hidden_attrs.get("hidden_pragmatism", 5)
        discipline = hidden_attrs.get("hidden_discipline", 5)
        
        return (pragmatism + (10 - discipline)) / 20.0  # 0.0 to 1.0 range
    
    def _calculate_benefit_threshold(self, hidden_attrs: Dict[str, int]) -> float:
        """Calculate minimum benefit threshold based on business rules"""
        ambition = hidden_attrs.get("hidden_ambition", 5)
        return 0.1 + (ambition / 25.0)  # 0.1 to 0.5 range


def create_enhanced_alliance_service(
    faction_data_provider: FactionDataProvider,
    diplomacy_data_provider: Optional[DiplomacyDataProvider] = None,
    config_provider: Optional[ConfigurationProvider] = None
) -> EnhancedAllianceService:
    """Factory function to create enhanced alliance service"""
    return EnhancedAllianceService(
        faction_data_provider, 
        diplomacy_data_provider, 
        config_provider
    ) 