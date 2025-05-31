"""
Models for the Diplomacy System

This module defines the core data models for the diplomacy system:
- Treaty: Represents a formal agreement between two or more factions
- Negotiation: Represents an ongoing diplomatic negotiation process
- DiplomaticEvent: Base class for all diplomatic events (treaty signing, alliance, etc.)
- DiplomaticStatus: Enum for diplomatic relationships between factions
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class DiplomaticStatus(str, Enum):
    """Status of diplomatic relations between factions."""
    ALLIANCE = "alliance"
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"  # Added for test compatibility
    RIVALRY = "rivalry"
    WAR = "war"
    TRUCE = "truce"
    HOSTILE = "hostile"


class TreatyType(str, Enum):
    """Types of treaties that can be formed between factions."""
    TRADE = "trade"
    ALLIANCE = "alliance"
    NON_AGGRESSION = "non_aggression"
    CEASEFIRE = "ceasefire"
    MUTUAL_DEFENSE = "mutual_defense"  # Added for test compatibility
    CUSTOM = "custom"


class NegotiationOffer(BaseModel):
    """An offer made during diplomatic negotiations."""
    faction_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    terms: Dict[str, Union[str, int, bool, Dict, List]] = {}
    accepted: Optional[bool] = None
    counter_offer_id: Optional[UUID] = None


class NegotiationStatus(str, Enum):
    """Status of a diplomatic negotiation."""
    PENDING = "pending"
    ACTIVE = "active"  # Added for test compatibility
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTER_OFFERED = "counter_offered"
    COMPLETED = "completed"  # Added for test compatibility
    EXPIRED = "expired"
    BREAKDOWN = "breakdown"


class Treaty(BaseModel):
    """A diplomatic treaty between two or more factions."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    type: TreatyType
    parties: List[UUID]  # Faction IDs
    terms: Dict[str, Union[str, int, bool, Dict, List]] = {}
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None  # None means indefinite
    is_active: bool = True
    is_public: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None  # Character or system ID
    negotiation_id: Optional[UUID] = None  # ID of the negotiation that led to this treaty

    @validator('parties')
    def validate_parties(cls, v):
        if not v or len(v) < 2:
            raise ValueError("Treaties must have at least 2 parties")
        return v


class Negotiation(BaseModel):
    """A diplomatic negotiation process between factions."""
    id: UUID = Field(default_factory=uuid4)
    parties: List[UUID]  # Faction IDs
    initiator_id: UUID  # Faction ID that started the negotiation
    status: NegotiationStatus = NegotiationStatus.PENDING
    offers: List[NegotiationOffer] = []
    current_offer_id: Optional[UUID] = None
    treaty_type: Optional[TreatyType] = None
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    result_treaty_id: Optional[UUID] = None  # ID of the resulting treaty, if any
    metadata: Dict[str, Union[str, int, bool, Dict, List]] = {}


class DiplomaticEventType(str, Enum):
    """Types of diplomatic events."""
    TREATY_SIGNED = "treaty_signed"
    TREATY_EXPIRED = "treaty_expired"
    TREATY_TERMINATED = "treaty_terminated"
    TREATY_BREACH = "treaty_breach"
    TREATY_VIOLATION = "treaty_violation"
    NEGOTIATION_STARTED = "negotiation_started"
    NEGOTIATION_ENDED = "negotiation_ended"
    NEGOTIATION_OFFER = "negotiation_offer"
    ALLIANCE_FORMED = "alliance_formed"
    WAR_DECLARATION = "war_declaration"
    PEACE_DECLARATION = "peace_declaration"
    INCIDENT = "diplomatic_incident"
    INCIDENT_RESOLVED = "diplomatic_incident_resolved"
    ULTIMATUM_ISSUED = "ultimatum_issued"
    ULTIMATUM_ACCEPTED = "ultimatum_accepted"
    ULTIMATUM_REJECTED = "ultimatum_rejected"
    ULTIMATUM_EXPIRED = "ultimatum_expired"
    STATUS_CHANGE = "status_change"
    TENSION_CHANGE = "tension_change"
    OTHER = "other"


class DiplomaticEvent(BaseModel):
    """Base class for all diplomatic events."""
    id: UUID = Field(default_factory=uuid4)
    event_type: DiplomaticEventType
    factions: List[UUID]  # Faction IDs involved
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    description: str
    severity: int = 0  # 0-100, higher means more impactful
    public: bool = True
    related_treaty_id: Optional[UUID] = None
    related_negotiation_id: Optional[UUID] = None
    metadata: Dict[str, Union[str, int, bool, Dict, List]] = {}
    tension_change: Dict[str, int] = {}  # Faction pair to tension change mapping


class TreatyViolationType(str, Enum):
    """Types of treaty violations."""
    TERRITORIAL_INTRUSION = "territorial_intrusion"
    TRADE_EMBARGO = "trade_embargo"
    TRADE_RESTRICTION = "trade_restriction"  # Added for test compatibility
    MILITARY_BUILDUP = "military_buildup"
    MILITARY_AGGRESSION = "military_aggression"  # Added for test compatibility
    BROKEN_PROMISE = "broken_promise"
    ATTACKED_ALLY = "attacked_ally"
    ESPIONAGE = "espionage"
    SUPPORTED_ENEMY = "supported_enemy"
    REFUSED_TRIBUTE = "refused_tribute"
    BROKEN_TERMS = "broken_terms"
    OTHER = "other"


class TreatyViolation(BaseModel):
    """A record of a treaty violation."""
    id: UUID = Field(default_factory=uuid4)
    treaty_id: UUID  # The treaty that was violated
    violator_id: UUID  # Faction ID that violated the treaty
    violation_type: TreatyViolationType
    description: str
    evidence: Dict[str, Union[str, int, bool, Dict, List]] = {}  # Proof or context of violation
    reported_by: UUID  # Faction ID that reported the violation
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: int = 50  # 0-100, higher means more severe violation
    acknowledged: bool = False  # Whether the violator has acknowledged the violation
    resolved: bool = False  # Whether the violation has been resolved
    resolution_details: Optional[str] = None  # How the violation was resolved, if applicable


class DiplomaticIncidentType(str, Enum):
    """Types of diplomatic incidents."""
    BORDER_DISPUTE = "border_dispute"
    ESPIONAGE = "espionage"
    INSULT = "insult"
    VERBAL_INSULT = "verbal_insult"  # Added for test compatibility
    ASSASSINATION = "assassination"
    KIDNAPPING = "kidnapping"
    TRADE_DISPUTE = "trade_dispute"
    MILITARY_THREAT = "military_threat"
    SABOTAGE = "sabotage"
    POPULATION_INTERFERENCE = "population_interference"
    TREATY_VIOLATION = "treaty_violation"
    PROXY_CONFLICT = "proxy_conflict"
    RELIGIOUS_DISPUTE = "religious_dispute"
    CULTURAL_OFFENSE = "cultural_offense"
    TERRITORY_CLAIM = "territory_claim"
    RESOURCE_DISPUTE = "resource_dispute"
    REFUSED_DEMAND = "refused_demand"
    PIRACY = "piracy"
    THEFT = "theft"
    OTHER = "other"


class DiplomaticIncidentSeverity(str, Enum):
    """Severity levels for diplomatic incidents."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class DiplomaticIncident(BaseModel):
    """A diplomatic incident between factions, which may affect relations."""
    id: UUID = Field(default_factory=uuid4)
    incident_type: DiplomaticIncidentType
    perpetrator_id: UUID  # Faction that caused the incident
    victim_id: UUID  # Faction that was affected by the incident
    description: str
    evidence: Dict[str, Union[str, int, bool, Dict, List]] = {}  # Context or proof
    severity: DiplomaticIncidentSeverity = DiplomaticIncidentSeverity.MODERATE
    tension_impact: int = 20  # How much tension increases (0-100)
    public: bool = True  # Whether the incident is publicly known
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    witnessed_by: List[UUID] = []  # Other factions that witnessed the incident
    related_event_id: Optional[UUID] = None  # Related diplomatic event, if any
    related_treaty_id: Optional[UUID] = None  # Related treaty, if any
    resolved: bool = False  # Whether the incident has been resolved
    resolution_details: Optional[str] = None  # How the incident was resolved, if applicable
    resolution_date: Optional[datetime] = None  # When the incident was resolved


class UltimatumStatus(str, Enum):
    """Status of an ultimatum."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Ultimatum(BaseModel):
    """An ultimatum issued by one faction to another with demands and consequences."""
    id: UUID = Field(default_factory=uuid4)
    issuer_id: UUID  # Faction issuing the ultimatum
    recipient_id: UUID  # Faction receiving the ultimatum
    demands: Dict[str, Union[str, int, bool, Dict, List]] = {}  # What is being demanded
    consequences: Dict[str, Union[str, int, bool, Dict, List]] = {}  # What happens if demands are not met
    status: UltimatumStatus = UltimatumStatus.PENDING
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    deadline: datetime  # When a response is required by
    response_date: Optional[datetime] = None  # When the recipient responded
    justification: str  # Explanation of why the ultimatum is being issued
    public: bool = True  # Whether the ultimatum is publicly known
    witnessed_by: List[UUID] = []  # Other factions that were informed of the ultimatum
    related_incident_id: Optional[UUID] = None  # Related diplomatic incident, if any
    related_treaty_id: Optional[UUID] = None  # Related treaty, if any
    related_event_id: Optional[UUID] = None  # Related diplomatic event, if any
    tension_change_on_issue: int = 20  # How much tension increases just from issuing
    tension_change_on_accept: int = -10  # How much tension changes if accepted
    tension_change_on_reject: int = 40  # How much tension increases if rejected


class SanctionType(str, Enum):
    """Types of diplomatic sanctions that can be imposed."""
    TRADE_EMBARGO = "trade_embargo"
    ECONOMIC = "economic"  # Added for test compatibility
    DIPLOMATIC = "diplomatic"  # Added for test compatibility
    TRAVEL_BAN = "travel_ban"
    ASSET_FREEZE = "asset_freeze"
    MILITARY_EMBARGO = "military_embargo"
    RESOURCE_RESTRICTION = "resource_restriction"
    DIPLOMATIC_EXPULSION = "diplomatic_expulsion"
    TECHNOLOGY_RESTRICTION = "technology_restriction"
    ECONOMIC_BLOCKADE = "economic_blockade"
    TREATY_SUSPENSION = "treaty_suspension"
    CUSTOM = "custom"


class SanctionStatus(str, Enum):
    """Status of diplomatic sanctions."""
    ACTIVE = "active"
    PAUSED = "paused"
    LIFTED = "lifted"
    EXPIRED = "expired"
    VIOLATED = "violated"


class Sanction(BaseModel):
    """A diplomatic sanction imposed by one faction on another."""
    id: UUID = Field(default_factory=uuid4)
    imposer_id: UUID  # Faction imposing the sanction
    target_id: UUID  # Faction targeted by the sanction
    sanction_type: SanctionType
    description: str
    status: SanctionStatus = SanctionStatus.ACTIVE
    justification: str
    imposed_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None  # When the sanction ends (if not indefinite)
    lifted_date: Optional[datetime] = None  # When the sanction was lifted (if applicable)
    conditions_for_lifting: Dict[str, Union[str, int, bool, Dict, List]] = {}  # Conditions that must be met to lift the sanction
    severity: int = 50  # 0-100, how severe the sanction is
    economic_impact: int = 50  # 0-100, estimated economic impact on target
    diplomatic_impact: int = 50  # 0-100, estimated diplomatic impact
    enforcement_measures: Dict[str, Union[str, int, bool, Dict, List]] = {}  # How the sanction is enforced
    supporting_factions: List[UUID] = []  # Other factions supporting this sanction
    opposing_factions: List[UUID] = []  # Factions opposing this sanction
    violations: List[Dict] = []  # Records of sanction violations
    is_public: bool = True  # Whether this sanction is publicly announced


class TreatyStatus(str, Enum):
    """Status of a treaty"""
    DRAFT = "draft"
    PROPOSED = "proposed"
    NEGOTIATING = "negotiating"
    PENDING_RATIFICATION = "pending_ratification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    VIOLATED = "violated"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class FactionRelationship(BaseModel):
    """Represents the diplomatic relationship between two factions"""
    id: UUID = Field(default_factory=uuid4)
    faction_a_id: UUID
    faction_b_id: UUID
    status: DiplomaticStatus = DiplomaticStatus.NEUTRAL
    trust_level: int = 50  # 0-100, how much faction A trusts faction B
    influence_level: int = 50  # 0-100, how much influence faction A has over faction B
    trade_volume: int = 0  # Economic relationship strength
    military_cooperation: int = 0  # 0-100, level of military cooperation
    cultural_exchange: int = 0  # 0-100, level of cultural exchange
    border_tension: int = 0  # 0-100, tension level at shared borders
    historical_grievances: List[str] = []  # Past conflicts or issues
    shared_interests: List[str] = []  # Common goals or interests
    active_treaties: List[UUID] = []  # Treaties currently in effect
    recent_events: List[UUID] = []  # Recent diplomatic events
    relationship_modifiers: Dict[str, Union[str, int, bool, Dict, List]] = {}  # Special modifiers affecting the relationship
    last_interaction_date: Optional[datetime] = None
    relationship_trend: str = "stable"  # "improving", "deteriorating", "stable"
    public_opinion_a_to_b: int = 50  # 0-100, how faction A's population views faction B
    public_opinion_b_to_a: int = 50  # 0-100, how faction B's population views faction A
    diplomatic_immunity_level: int = 0  # 0-100, level of diplomatic protections
    trade_agreements: List[Dict] = []  # Active trade agreements
    intelligence_sharing: int = 0  # 0-100, level of intelligence cooperation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict()        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        } 