"""
Faction Relationship Tracker

This service provides comprehensive tracking of faction relationships including:
- Historical interaction records
- Trust evolution over time
- Diplomatic incident tracking
- Reputation system
- Relationship trajectory analysis

Pure business logic implementation.
"""

from typing import Dict, List, Optional, Any, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class InteractionType(Enum):
    """Types of faction interactions"""
    ALLIANCE_PROPOSAL = "alliance_proposal"
    ALLIANCE_ACCEPTANCE = "alliance_acceptance"
    ALLIANCE_REJECTION = "alliance_rejection"
    TREATY_SIGNED = "treaty_signed"
    TREATY_VIOLATED = "treaty_violated"
    TRADE_AGREEMENT = "trade_agreement"
    MILITARY_SUPPORT = "military_support"
    BETRAYAL = "betrayal"
    DIPLOMATIC_INSULT = "diplomatic_insult"
    TERRITORIAL_DISPUTE = "territorial_dispute"
    RESOURCE_CONFLICT = "resource_conflict"
    CULTURAL_EXCHANGE = "cultural_exchange"
    HUMANITARIAN_AID = "humanitarian_aid"
    ESPIONAGE_DETECTED = "espionage_detected"
    BORDER_INCIDENT = "border_incident"
    SUCCESSION_SUPPORT = "succession_support"
    MEDIATION_ATTEMPT = "mediation_attempt"

class RelationshipTrend(Enum):
    """Trends in faction relationships"""
    RAPIDLY_IMPROVING = "rapidly_improving"
    IMPROVING = "improving" 
    STABLE = "stable"
    DECLINING = "declining"
    RAPIDLY_DECLINING = "rapidly_declining"
    VOLATILE = "volatile"

class TrustCategory(Enum):
    """Categories of trust between factions"""
    ABSOLUTE_TRUST = "absolute_trust"      # 0.9+
    HIGH_TRUST = "high_trust"              # 0.7-0.9
    MODERATE_TRUST = "moderate_trust"      # 0.5-0.7
    LOW_TRUST = "low_trust"                # 0.3-0.5
    DISTRUST = "distrust"                  # 0.1-0.3
    DEEP_MISTRUST = "deep_mistrust"        # 0.0-0.1

@dataclass
class InteractionRecord:
    """Record of a specific interaction between factions"""
    interaction_id: UUID
    timestamp: datetime
    interaction_type: InteractionType
    initiator_faction_id: UUID
    target_faction_id: UUID
    
    # Interaction details
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    outcome: str = "pending"
    
    # Impact on relationship
    trust_impact: float = 0.0      # -1.0 to +1.0
    reputation_impact: float = 0.0  # -1.0 to +1.0
    tension_impact: float = 0.0    # -1.0 to +1.0
    
    # Metadata
    severity: float = 0.5          # 0.0 to 1.0 (how significant this interaction was)
    witnesses: List[UUID] = field(default_factory=list)  # Other factions that observed
    consequences: List[str] = field(default_factory=list)
    
    # System data
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrustEvolution:
    """Tracks how trust between two factions has evolved over time"""
    faction_a_id: UUID
    faction_b_id: UUID
    
    # Current trust levels (mutual - each faction's trust of the other)
    a_trusts_b: float = 0.5        # A's trust in B
    b_trusts_a: float = 0.5        # B's trust in A
    
    # Historical trust data points
    trust_history: List[Tuple[datetime, float, float]] = field(default_factory=list)  # (timestamp, a_trusts_b, b_trusts_a)
    
    # Trust metrics
    trust_volatility: float = 0.0   # How much trust fluctuates
    peak_trust: float = 0.5         # Highest trust ever achieved
    lowest_trust: float = 0.5       # Lowest trust ever recorded
    trust_recovery_rate: float = 0.1 # How quickly trust recovers from negative events
    
    # Factors affecting trust
    trust_modifiers: Dict[str, float] = field(default_factory=dict)
    baseline_compatibility: float = 0.5  # Fundamental compatibility between factions

@dataclass
class RelationshipSummary:
    """Comprehensive summary of relationship between two factions"""
    faction_a_id: UUID
    faction_b_id: UUID
    faction_a_name: str
    faction_b_name: str
    
    # Current status
    current_trust_level: TrustCategory
    mutual_trust_score: float  # Average of both directions
    relationship_trend: RelationshipTrend
    diplomatic_status: str
    
    # Historical context
    relationship_duration: int  # Days since first interaction
    total_interactions: int
    positive_interactions: int
    negative_interactions: int
    
    # Predictions
    predicted_trajectory: RelationshipTrend
    alliance_probability: float
    conflict_probability: float
    stability_score: float
    
    # Optional fields with defaults
    last_interaction_date: Optional[datetime] = None
    most_significant_positive_event: Optional[InteractionRecord] = None
    most_significant_negative_event: Optional[InteractionRecord] = None
    turning_points: List[InteractionRecord] = field(default_factory=list)


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
        """Get diplomatic status between two factions"""
        ...


class RelationshipDataStore(Protocol):
    """Protocol for relationship data persistence"""
    
    def store_interaction(self, interaction: InteractionRecord) -> None:
        """Store an interaction record"""
        ...
    
    def get_interactions(self, faction_a_id: UUID, faction_b_id: UUID) -> List[InteractionRecord]:
        """Get interaction history between two factions"""
        ...
    
    def store_trust_evolution(self, trust_data: TrustEvolution) -> None:
        """Store trust evolution data"""
        ...
    
    def get_trust_evolution(self, faction_a_id: UUID, faction_b_id: UUID) -> Optional[TrustEvolution]:
        """Get trust evolution data"""
        ...


class FactionRelationshipTracker:
    """Service for comprehensive faction relationship tracking - pure business logic"""
    
    def __init__(self, 
                 faction_data_provider: FactionDataProvider,
                 diplomacy_data_provider: DiplomacyDataProvider,
                 relationship_data_store: RelationshipDataStore):
        """Initialize the relationship tracker"""
        self.faction_data_provider = faction_data_provider
        self.diplomacy_data_provider = diplomacy_data_provider
        self.relationship_data_store = relationship_data_store
        
        # Configuration
        self.config = {
            "trust_decay_rate": 0.001,  # Daily trust decay without interaction
            "trust_volatility_threshold": 0.2,  # Threshold for volatile relationships
            "significant_event_threshold": 0.3,  # Minimum impact to be "significant"
            "relationship_analysis_period_days": 90,  # Period for trend analysis
            "max_trust_change_per_event": 0.2,  # Maximum trust change from single event
            "baseline_trust_recovery_days": 30,  # Days to recover from trust loss
        }
    
    def record_interaction(self, 
                          initiator_id: UUID,
                          target_id: UUID,
                          interaction_type: InteractionType,
                          description: str,
                          context: Optional[Dict[str, Any]] = None,
                          trust_impact: float = 0.0,
                          reputation_impact: float = 0.0,
                          severity: float = 0.5) -> InteractionRecord:
        """
        Record a new interaction between factions
        
        Args:
            initiator_id: Faction that initiated the interaction
            target_id: Faction that was the target of the interaction
            interaction_type: Type of interaction
            description: Human-readable description
            context: Additional context data
            trust_impact: Impact on trust (-1.0 to +1.0)
            reputation_impact: Impact on reputation (-1.0 to +1.0)
            severity: How significant this event was (0.0 to 1.0)
            
        Returns:
            Created interaction record
        """
        # Create interaction record
        interaction = InteractionRecord(
            interaction_id=uuid4(),
            timestamp=datetime.utcnow(),
            interaction_type=interaction_type,
            initiator_faction_id=initiator_id,
            target_faction_id=target_id,
            description=description,
            context=context or {},
            trust_impact=max(-1.0, min(1.0, trust_impact)),
            reputation_impact=max(-1.0, min(1.0, reputation_impact)),
            severity=max(0.0, min(1.0, severity))
        )
        
        # Calculate tension impact based on interaction type
        interaction.tension_impact = self._calculate_tension_impact(interaction_type, trust_impact)
        
        # Determine consequences
        interaction.consequences = self._determine_interaction_consequences(interaction)
        
        # Store the interaction
        self.relationship_data_store.store_interaction(interaction)
        
        # Update trust evolution
        self._update_trust_evolution(initiator_id, target_id, interaction)
        
        return interaction

    def get_relationship_summary(self, faction_a_id: UUID, faction_b_id: UUID) -> RelationshipSummary:
        """
        Get comprehensive relationship summary between two factions
        
        Args:
            faction_a_id: First faction ID
            faction_b_id: Second faction ID
            
        Returns:
            Comprehensive relationship summary
        """
        # Get faction data
        faction_a = self.faction_data_provider.get_faction_by_id(faction_a_id)
        faction_b = self.faction_data_provider.get_faction_by_id(faction_b_id)
        
        if not faction_a or not faction_b:
            raise ValueError(f"One or both factions not found")
        
        # Get interaction history
        interactions = self.relationship_data_store.get_interactions(faction_a_id, faction_b_id)
        
        # Get trust evolution data
        trust_data = self.relationship_data_store.get_trust_evolution(faction_a_id, faction_b_id)
        if not trust_data:
            trust_data = self._initialize_trust_evolution(faction_a_id, faction_b_id)
        
        # Calculate current trust level
        mutual_trust = (trust_data.a_trusts_b + trust_data.b_trusts_a) / 2.0
        trust_category = self._categorize_trust_level(mutual_trust)
        
        # Analyze interactions
        positive_interactions = sum(1 for i in interactions if i.trust_impact > 0)
        negative_interactions = sum(1 for i in interactions if i.trust_impact < 0)
        
        # Get diplomatic status
        diplomatic_status = self.diplomacy_data_provider.get_diplomatic_status(faction_a_id, faction_b_id)
        
        # Calculate relationship duration
        if interactions:
            first_interaction = min(interactions, key=lambda x: x.timestamp)
            relationship_duration = (datetime.utcnow() - first_interaction.timestamp).days
            last_interaction_date = max(interactions, key=lambda x: x.timestamp).timestamp
        else:
            relationship_duration = 0
            last_interaction_date = None
        
        # Analyze trends and predictions
        relationship_trend = self._analyze_relationship_trend(interactions, trust_data)
        predicted_trajectory = self._predict_relationship_trajectory(interactions, trust_data)
        alliance_probability = self._calculate_alliance_probability(faction_a_id, faction_b_id, trust_data)
        conflict_probability = self._calculate_conflict_probability(faction_a_id, faction_b_id, trust_data)
        stability_score = self._calculate_stability_score(trust_data, interactions)
        
        # Find significant events
        significant_positive = max(
            (i for i in interactions if i.trust_impact > self.config["significant_event_threshold"]),
            key=lambda x: x.trust_impact,
            default=None
        )
        significant_negative = min(
            (i for i in interactions if i.trust_impact < -self.config["significant_event_threshold"]),
            key=lambda x: x.trust_impact,
            default=None
        )
        
        # Identify turning points
        turning_points = self._identify_turning_points(interactions, trust_data)
        
        return RelationshipSummary(
            faction_a_id=faction_a_id,
            faction_b_id=faction_b_id,
            faction_a_name=faction_a.get("name", "Unknown"),
            faction_b_name=faction_b.get("name", "Unknown"),
            current_trust_level=trust_category,
            mutual_trust_score=mutual_trust,
            relationship_trend=relationship_trend,
            diplomatic_status=diplomatic_status,
            relationship_duration=relationship_duration,
            total_interactions=len(interactions),
            positive_interactions=positive_interactions,
            negative_interactions=negative_interactions,
            predicted_trajectory=predicted_trajectory,
            alliance_probability=alliance_probability,
            conflict_probability=conflict_probability,
            stability_score=stability_score,
            last_interaction_date=last_interaction_date,
            most_significant_positive_event=significant_positive,
            most_significant_negative_event=significant_negative,
            turning_points=turning_points
        )

    def get_faction_reputation(self, faction_id: UUID) -> Dict[str, Any]:
        """
        Calculate faction's overall reputation based on all relationships
        
        Args:
            faction_id: Faction to analyze
            
        Returns:
            Reputation analysis
        """
        faction = self.faction_data_provider.get_faction_by_id(faction_id)
        if not faction:
            raise ValueError(f"Faction {faction_id} not found")
        
        # This would need to aggregate data from all relationships
        # For now, return a basic structure
        return {
            "faction_id": faction_id,
            "faction_name": faction.get("name", "Unknown"),
            "overall_reputation": 0.5,  # Placeholder
            "trustworthiness": 0.5,     # Placeholder
            "reliability": 0.5,         # Placeholder
            "diplomatic_standing": "neutral",
            "notable_alliances": [],
            "notable_conflicts": [],
            "reputation_trends": {
                "direction": "stable",
                "recent_change": 0.0
            }
        }

    def analyze_diplomatic_network(self, faction_ids: List[UUID]) -> Dict[str, Any]:
        """
        Analyze the diplomatic network among multiple factions
        
        Args:
            faction_ids: List of faction IDs to analyze
            
        Returns:
            Network analysis including clusters, tensions, influence
        """
        if len(faction_ids) < 2:
            return {"error": "Need at least 2 factions for network analysis"}
        
        # Build relationship matrix
        relationship_matrix = {}
        for i, faction_a in enumerate(faction_ids):
            for faction_b in faction_ids[i+1:]:
                trust_data = self.relationship_data_store.get_trust_evolution(faction_a, faction_b)
                if trust_data:
                    mutual_trust = (trust_data.a_trusts_b + trust_data.b_trusts_a) / 2.0
                else:
                    mutual_trust = 0.5  # Default neutral trust
                
                relationship_matrix[(faction_a, faction_b)] = mutual_trust
        
        # Analyze network structure
        alliance_clusters = self._identify_alliance_clusters(faction_ids, relationship_matrix)
        tension_hotspots = self._identify_tension_hotspots(faction_ids, relationship_matrix)
        influence_rankings = self._calculate_diplomatic_influence(faction_ids, relationship_matrix)
        
        return {
            "analyzed_factions": faction_ids,
            "relationship_matrix": {f"{k[0]}_{k[1]}": v for k, v in relationship_matrix.items()},
            "alliance_clusters": alliance_clusters,
            "tension_hotspots": tension_hotspots,
            "influence_rankings": influence_rankings,
            "network_stability": self._calculate_network_stability(relationship_matrix),
            "conflict_risk": self._assess_network_conflict_risk(relationship_matrix)
        }

    def _get_relationship_key(self, faction_a_id: UUID, faction_b_id: UUID) -> Tuple[UUID, UUID]:
        """Get consistent relationship key regardless of order"""
        return (min(faction_a_id, faction_b_id), max(faction_a_id, faction_b_id))

    def _initialize_trust_evolution(self, faction_a_id: UUID, faction_b_id: UUID) -> TrustEvolution:
        """Initialize trust evolution data for a new relationship"""
        # Get faction attributes for compatibility calculation
        attrs_a = self.faction_data_provider.get_faction_hidden_attributes(faction_a_id)
        attrs_b = self.faction_data_provider.get_faction_hidden_attributes(faction_b_id)
        
        # Calculate baseline compatibility
        baseline_compatibility = self._calculate_personality_compatibility(attrs_a, attrs_b)
        
        # Initialize with neutral trust, adjusted by compatibility
        initial_trust = 0.5 + (baseline_compatibility - 0.5) * 0.2
        
        trust_data = TrustEvolution(
            faction_a_id=faction_a_id,
            faction_b_id=faction_b_id,
            a_trusts_b=initial_trust,
            b_trusts_a=initial_trust,
            baseline_compatibility=baseline_compatibility,
            peak_trust=initial_trust,
            lowest_trust=initial_trust
        )
        
        # Add initial history point
        trust_data.trust_history.append((datetime.utcnow(), initial_trust, initial_trust))
        
        # Store the initialized data
        self.relationship_data_store.store_trust_evolution(trust_data)
        
        return trust_data

    def _calculate_personality_compatibility(self, attrs_a: Dict[str, int], attrs_b: Dict[str, int]) -> float:
        """Calculate compatibility based on personality attributes"""
        # Similar to alliance service compatibility calculation
        norm_a = {k: v/10.0 for k, v in attrs_a.items()}
        norm_b = {k: v/10.0 for k, v in attrs_b.items()}
        
        # Calculate compatibility for key traits
        integrity_compat = 1.0 - abs(norm_a.get('hidden_integrity', 0.5) - norm_b.get('hidden_integrity', 0.5))
        pragmatism_compat = 1.0 - abs(norm_a.get('hidden_pragmatism', 0.5) - norm_b.get('hidden_pragmatism', 0.5))
        discipline_compat = 1.0 - abs(norm_a.get('hidden_discipline', 0.5) - norm_b.get('hidden_discipline', 0.5))
        
        # Ambition differences can be complementary
        ambition_diff = abs(norm_a.get('hidden_ambition', 0.5) - norm_b.get('hidden_ambition', 0.5))
        ambition_compat = 0.8 if ambition_diff > 0.3 else 1.0 - ambition_diff
        
        # Weight the compatibility scores
        overall_compatibility = (
            integrity_compat * 0.35 +
            pragmatism_compat * 0.25 +
            discipline_compat * 0.25 +
            ambition_compat * 0.15
        )
        
        return max(0.0, min(1.0, overall_compatibility))

    def _update_trust_evolution(self, initiator_id: UUID, target_id: UUID, interaction: InteractionRecord):
        """Update trust evolution based on new interaction"""
        trust_data = self.relationship_data_store.get_trust_evolution(initiator_id, target_id)
        if not trust_data:
            trust_data = self._initialize_trust_evolution(initiator_id, target_id)
        
        # Calculate trust change
        trust_change = min(self.config["max_trust_change_per_event"], abs(interaction.trust_impact))
        if interaction.trust_impact < 0:
            trust_change = -trust_change
        
        # Apply trust change (mutual but potentially asymmetric)
        if initiator_id == trust_data.faction_a_id:
            # A initiated action toward B, so B's trust in A changes more
            trust_data.b_trusts_a += trust_change
            trust_data.a_trusts_b += trust_change * 0.5  # Partial reciprocal effect
        else:
            # B initiated action toward A
            trust_data.a_trusts_b += trust_change
            trust_data.b_trusts_a += trust_change * 0.5
        
        # Clamp trust values
        trust_data.a_trusts_b = max(0.0, min(1.0, trust_data.a_trusts_b))
        trust_data.b_trusts_a = max(0.0, min(1.0, trust_data.b_trusts_a))
        
        # Update peak/lowest trust
        current_max = max(trust_data.a_trusts_b, trust_data.b_trusts_a)
        current_min = min(trust_data.a_trusts_b, trust_data.b_trusts_a)
        
        trust_data.peak_trust = max(trust_data.peak_trust, current_max)
        trust_data.lowest_trust = min(trust_data.lowest_trust, current_min)
        
        # Add to history
        trust_data.trust_history.append((
            datetime.utcnow(),
            trust_data.a_trusts_b,
            trust_data.b_trusts_a
        ))
        
        # Calculate volatility
        if len(trust_data.trust_history) > 5:
            recent_values = [max(h[1], h[2]) for h in trust_data.trust_history[-5:]]
            trust_data.trust_volatility = self._calculate_variance(recent_values)
        
        # Store updated data
        self.relationship_data_store.store_trust_evolution(trust_data)

    def _categorize_trust_level(self, trust_score: float) -> TrustCategory:
        """Categorize trust score into trust category"""
        if trust_score >= 0.9:
            return TrustCategory.ABSOLUTE_TRUST
        elif trust_score >= 0.7:
            return TrustCategory.HIGH_TRUST
        elif trust_score >= 0.5:
            return TrustCategory.MODERATE_TRUST
        elif trust_score >= 0.3:
            return TrustCategory.LOW_TRUST
        elif trust_score >= 0.1:
            return TrustCategory.DISTRUST
        else:
            return TrustCategory.DEEP_MISTRUST

    def _analyze_relationship_trend(self, interactions: List[InteractionRecord], trust_data: TrustEvolution) -> RelationshipTrend:
        """Analyze current relationship trend"""
        if len(trust_data.trust_history) < 3:
            return RelationshipTrend.STABLE
        
        # Look at recent trust changes
        recent_period = datetime.utcnow() - timedelta(days=self.config["relationship_analysis_period_days"])
        recent_history = [h for h in trust_data.trust_history if h[0] >= recent_period]
        
        if len(recent_history) < 2:
            return RelationshipTrend.STABLE
        
        # Calculate trend
        first_avg = (recent_history[0][1] + recent_history[0][2]) / 2
        last_avg = (recent_history[-1][1] + recent_history[-1][2]) / 2
        
        change = last_avg - first_avg
        
        # Check volatility
        if trust_data.trust_volatility > self.config["trust_volatility_threshold"]:
            return RelationshipTrend.VOLATILE
        
        # Determine trend direction
        if change > 0.15:
            return RelationshipTrend.RAPIDLY_IMPROVING
        elif change > 0.05:
            return RelationshipTrend.IMPROVING
        elif change < -0.15:
            return RelationshipTrend.RAPIDLY_DECLINING
        elif change < -0.05:
            return RelationshipTrend.DECLINING
        else:
            return RelationshipTrend.STABLE

    def _predict_relationship_trajectory(self, interactions: List[InteractionRecord], trust_data: TrustEvolution) -> RelationshipTrend:
        """Predict future relationship trajectory"""
        # Simple prediction based on current trend and baseline compatibility
        current_trend = self._analyze_relationship_trend(interactions, trust_data)
        
        # Factor in baseline compatibility for prediction
        if trust_data.baseline_compatibility > 0.7:
            # High compatibility tends toward improvement
            if current_trend in [RelationshipTrend.DECLINING, RelationshipTrend.RAPIDLY_DECLINING]:
                return RelationshipTrend.IMPROVING  # Recovery likely
        elif trust_data.baseline_compatibility < 0.3:
            # Low compatibility tends toward decline
            if current_trend in [RelationshipTrend.IMPROVING, RelationshipTrend.RAPIDLY_IMPROVING]:
                return RelationshipTrend.DECLINING  # Temporary improvement
        
        return current_trend

    def _calculate_alliance_probability(self, faction_a_id: UUID, faction_b_id: UUID, trust_data: TrustEvolution) -> float:
        """Calculate probability of alliance formation"""
        mutual_trust = (trust_data.a_trusts_b + trust_data.b_trusts_a) / 2.0
        
        # Base probability from trust level
        base_prob = max(0.0, (mutual_trust - 0.5) * 1.5)
        
        # Adjust for compatibility
        compatibility_bonus = trust_data.baseline_compatibility * 0.3
        
        # Adjust for stability (volatile relationships less likely to ally)
        stability_factor = max(0.5, 1.0 - trust_data.trust_volatility)
        
        alliance_probability = (base_prob + compatibility_bonus) * stability_factor
        
        return max(0.0, min(1.0, alliance_probability))

    def _calculate_conflict_probability(self, faction_a_id: UUID, faction_b_id: UUID, trust_data: TrustEvolution) -> float:
        """Calculate probability of conflict"""
        mutual_trust = (trust_data.a_trusts_b + trust_data.b_trusts_a) / 2.0
        
        # Base probability from low trust
        base_prob = max(0.0, (0.3 - mutual_trust) * 2.0)
        
        # Increase with volatility
        volatility_factor = trust_data.trust_volatility * 1.5
        
        # Adjust for compatibility (incompatible factions more likely to conflict)
        incompatibility_factor = (1.0 - trust_data.baseline_compatibility) * 0.4
        
        conflict_probability = base_prob + volatility_factor + incompatibility_factor
        
        return max(0.0, min(1.0, conflict_probability))

    def _calculate_stability_score(self, trust_data: TrustEvolution, interactions: List[InteractionRecord]) -> float:
        """Calculate relationship stability score"""
        # Base stability from low volatility
        volatility_stability = max(0.0, 1.0 - trust_data.trust_volatility * 2.0)
        
        # Stability from consistent trust levels
        trust_range = trust_data.peak_trust - trust_data.lowest_trust
        range_stability = max(0.0, 1.0 - trust_range)
        
        # Stability from baseline compatibility
        compatibility_stability = trust_data.baseline_compatibility
        
        # Average the factors
        overall_stability = (volatility_stability + range_stability + compatibility_stability) / 3.0
        
        return max(0.0, min(1.0, overall_stability))

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    def _calculate_tension_impact(self, interaction_type: InteractionType, trust_impact: float) -> float:
        """Calculate tension impact based on interaction type"""
        tension_multipliers = {
            InteractionType.BETRAYAL: 2.0,
            InteractionType.TREATY_VIOLATED: 1.8,
            InteractionType.DIPLOMATIC_INSULT: 1.5,
            InteractionType.TERRITORIAL_DISPUTE: 1.7,
            InteractionType.RESOURCE_CONFLICT: 1.4,
            InteractionType.ESPIONAGE_DETECTED: 1.6,
            InteractionType.BORDER_INCIDENT: 1.3,
            InteractionType.MILITARY_SUPPORT: -0.8,
            InteractionType.HUMANITARIAN_AID: -0.5,
            InteractionType.CULTURAL_EXCHANGE: -0.3,
            InteractionType.TRADE_AGREEMENT: -0.4,
        }
        
        multiplier = tension_multipliers.get(interaction_type, 1.0)
        return trust_impact * multiplier

    def _determine_interaction_consequences(self, interaction: InteractionRecord) -> List[str]:
        """Determine consequences of an interaction"""
        consequences = []
        
        if interaction.trust_impact > 0.3:
            consequences.append("Strengthened diplomatic ties")
        elif interaction.trust_impact < -0.3:
            consequences.append("Damaged diplomatic relations")
        
        if interaction.severity > 0.7:
            consequences.append("Regional diplomatic impact")
        
        # Type-specific consequences
        if interaction.interaction_type == InteractionType.BETRAYAL:
            consequences.extend(["Trust penalty with other factions", "Reputation damage"])
        elif interaction.interaction_type == InteractionType.ALLIANCE_PROPOSAL:
            consequences.append("Formal diplomatic process initiated")
        
        return consequences

    def _identify_turning_points(self, interactions: List[InteractionRecord], trust_data: TrustEvolution) -> List[InteractionRecord]:
        """Identify major turning points in the relationship"""
        turning_points = []
        
        # Find interactions with high impact
        for interaction in interactions:
            if abs(interaction.trust_impact) > self.config["significant_event_threshold"]:
                turning_points.append(interaction)
        
        # Sort by impact magnitude and take top events
        turning_points.sort(key=lambda x: abs(x.trust_impact), reverse=True)
        return turning_points[:5]  # Top 5 turning points

    def _identify_alliance_clusters(self, faction_ids: List[UUID], relationship_matrix: Dict) -> List[Dict[str, Any]]:
        """Identify alliance clusters in the diplomatic network"""
        # Simplified clustering based on high trust relationships
        clusters = []
        high_trust_threshold = 0.7
        
        # Find pairs with high mutual trust
        allied_pairs = []
        for (faction_a, faction_b), trust in relationship_matrix.items():
            if trust >= high_trust_threshold:
                allied_pairs.append((faction_a, faction_b))
        
        # Group connected pairs into clusters
        # This is a simplified implementation
        processed = set()
        for faction_a, faction_b in allied_pairs:
            if faction_a not in processed and faction_b not in processed:
                cluster = {
                    "members": [faction_a, faction_b],
                    "average_trust": relationship_matrix[(faction_a, faction_b)],
                    "cluster_strength": "strong" if relationship_matrix[(faction_a, faction_b)] > 0.8 else "moderate"
                }
                clusters.append(cluster)
                processed.add(faction_a)
                processed.add(faction_b)
        
        return clusters

    def _identify_tension_hotspots(self, faction_ids: List[UUID], relationship_matrix: Dict) -> List[Dict[str, Any]]:
        """Identify tension hotspots in the diplomatic network"""
        hotspots = []
        low_trust_threshold = 0.3
        
        for (faction_a, faction_b), trust in relationship_matrix.items():
            if trust <= low_trust_threshold:
                hotspots.append({
                    "factions": [faction_a, faction_b],
                    "trust_level": trust,
                    "tension_level": "high" if trust < 0.1 else "moderate",
                    "conflict_risk": self._calculate_conflict_probability(faction_a, faction_b, 
                                                                        TrustEvolution(faction_a, faction_b))
                })
        
        return sorted(hotspots, key=lambda x: x["trust_level"])

    def _calculate_diplomatic_influence(self, faction_ids: List[UUID], relationship_matrix: Dict) -> Dict[str, float]:
        """Calculate diplomatic influence ranking for each faction"""
        influence_scores = {}
        
        for faction_id in faction_ids:
            # Calculate influence based on average trust from others
            trust_scores = []
            for (faction_a, faction_b), trust in relationship_matrix.items():
                if faction_a == faction_id:
                    trust_scores.append(trust)
                elif faction_b == faction_id:
                    trust_scores.append(trust)
            
            if trust_scores:
                influence_scores[str(faction_id)] = sum(trust_scores) / len(trust_scores)
            else:
                influence_scores[str(faction_id)] = 0.5
        
        return influence_scores

    def _calculate_network_stability(self, relationship_matrix: Dict) -> float:
        """Calculate overall network stability"""
        if not relationship_matrix:
            return 1.0
        
        trust_values = list(relationship_matrix.values())
        mean_trust = sum(trust_values) / len(trust_values)
        variance = self._calculate_variance(trust_values)
        
        # High mean trust and low variance = high stability
        stability = mean_trust * (1.0 - variance)
        return max(0.0, min(1.0, stability))

    def _assess_network_conflict_risk(self, relationship_matrix: Dict) -> float:
        """Assess overall conflict risk in the network"""
        if not relationship_matrix:
            return 0.0
        
        low_trust_relationships = sum(1 for trust in relationship_matrix.values() if trust < 0.3)
        total_relationships = len(relationship_matrix)
        
        conflict_risk = low_trust_relationships / total_relationships
        return max(0.0, min(1.0, conflict_risk)) 