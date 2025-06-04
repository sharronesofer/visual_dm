"""
Crisis Management Service

This service provides comprehensive diplomatic crisis management capabilities:
- Crisis detection algorithms based on diplomatic events and relationship tensions
- Escalation state machines for crisis progression
- Resolution pathway decision trees
- Impact assessment and consequence tracking
- Integration with existing diplomatic systems

This is the pure business logic layer that delegates technical operations to infrastructure.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

from backend.systems.diplomacy.models.crisis_models import (
    DiplomaticCrisis, CrisisResolutionAttempt, CrisisIntervention,
    CrisisEscalationTrigger, CrisisImpactAssessment,
    CrisisType, CrisisEscalationLevel, CrisisStatus, ResolutionType, InterventionType
)
from backend.systems.diplomacy.models.core_models import (
    DiplomaticStatus, DiplomaticIncidentSeverity, DiplomaticEventType, TreatyViolation,
    NegotiationStatus, UltimatumStatus
)

# Import infrastructure components
from backend.infrastructure.databases.diplomacy.crisis_database_adapter import CrisisDatabaseAdapter
from backend.infrastructure.utils.diplomacy.crisis_utils import (
    CrisisDetectionUtils, CrisisEscalationCalculator, CrisisResolutionAnalyzer,
    CrisisImpactCalculator, CrisisContentGenerator
)

logger = logging.getLogger(__name__)


class CrisisDetectionEngine:
    """Engine for detecting emerging diplomatic crises."""
    
    def __init__(self, db_adapter: CrisisDatabaseAdapter):
        self.db_adapter = db_adapter
        
    def detect_emerging_crises(self) -> List[DiplomaticCrisis]:
        """Scan for emerging crises based on various indicators."""
        potential_crises = []
        
        # Check for tension threshold breaches
        potential_crises.extend(self._detect_tension_threshold_crises())
        
        # Check for cascading incident patterns
        potential_crises.extend(self._detect_cascading_incident_crises())
        
        # Check for failed negotiations leading to crises
        potential_crises.extend(self._detect_negotiation_breakdown_crises())
        
        # Check for treaty violations escalating to crises
        potential_crises.extend(self._detect_treaty_violation_crises())
        
        # Check for ultimatum-driven crises
        potential_crises.extend(self._detect_ultimatum_crises())
        
        return potential_crises
    
    def _detect_tension_threshold_crises(self) -> List[DiplomaticCrisis]:
        """Detect crises based on relationship tension levels."""
        crises = []
        
        # Find relationships with extremely high tension
        high_tension_relationships = self.db_adapter.get_high_tension_relationships(tension_threshold=80)
        
        for rel in high_tension_relationships:
            # Check if this relationship already has an active crisis
            faction_ids = [rel.faction_a_id, rel.faction_b_id]
            existing_crisis = self.db_adapter.get_existing_crisis_for_factions(faction_ids)
            
            if not existing_crisis:
                crisis = self._create_tension_based_crisis(rel)
                crises.append(crisis)
        
        return crises
    
    def _detect_cascading_incident_crises(self) -> List[DiplomaticCrisis]:
        """Detect crises from cascading diplomatic incidents."""
        crises = []
        
        # Look for multiple major incidents between same factions in short time
        major_incidents = self.db_adapter.get_recent_major_incidents(days=30)
        
        # Group incidents by faction pairs
        faction_pair_incidents = {}
        for incident in major_incidents:
            pair_key = tuple(sorted([str(incident.perpetrator_id), str(incident.victim_id)]))
            if pair_key not in faction_pair_incidents:
                faction_pair_incidents[pair_key] = []
            faction_pair_incidents[pair_key].append(incident)
        
        # Create crises for faction pairs with multiple major incidents
        for pair_key, incidents in faction_pair_incidents.items():
            if CrisisDetectionUtils.count_cascading_incidents(incidents):
                crisis = self._create_incident_cascade_crisis(pair_key, incidents)
                crises.append(crisis)
        
        return crises
    
    def _detect_negotiation_breakdown_crises(self) -> List[DiplomaticCrisis]:
        """Detect crises from failed high-stakes negotiations."""
        crises = []
        
        # Look for recently failed critical negotiations
        failed_negotiations = self.db_adapter.get_failed_negotiations(days=14)
        
        for negotiation in failed_negotiations:
            # Check if this was a high-stakes negotiation
            if CrisisDetectionUtils.is_high_stakes_negotiation(negotiation):
                crisis = self._create_negotiation_breakdown_crisis(negotiation)
                crises.append(crisis)
        
        return crises
    
    def _detect_treaty_violation_crises(self) -> List[DiplomaticCrisis]:
        """Detect crises from serious treaty violations."""
        crises = []
        
        # Look for unresolved major treaty violations
        major_violations = self.db_adapter.get_major_treaty_violations(severity_threshold=80)
        
        for violation in major_violations:
            # Check if violation has led to crisis
            treaty = self.db_adapter.get_treaty_by_id(violation.treaty_id)
            if treaty and CrisisDetectionUtils.should_violation_create_crisis(violation, treaty):
                crisis = self._create_treaty_violation_crisis(violation, treaty)
                crises.append(crisis)
        
        return crises
    
    def _detect_ultimatum_crises(self) -> List[DiplomaticCrisis]:
        """Detect crises from ultimatum situations."""
        crises = []
        
        # Look for rejected or expired ultimatums
        crisis_ultimatums = self.db_adapter.get_crisis_ultimatums()
        
        for ultimatum in crisis_ultimatums:
            crisis = self._create_ultimatum_crisis(ultimatum)
            crises.append(crisis)
        
        return crises
    
    def _create_tension_based_crisis(self, relationship) -> DiplomaticCrisis:
        """Create a crisis based on high relationship tension."""
        return DiplomaticCrisis(
            crisis_type=CrisisType.BORDER_DISPUTE,  # Default type, can be refined
            title=CrisisDetectionUtils.create_crisis_title(CrisisType.BORDER_DISPUTE, [relationship.faction_a_id, relationship.faction_b_id]),
            description=CrisisContentGenerator.generate_crisis_description(CrisisType.BORDER_DISPUTE, [relationship.faction_a_id, relationship.faction_b_id]),
            primary_factions=[relationship.faction_a_id, relationship.faction_b_id],
            affected_factions=[],
            status=CrisisStatus.DEVELOPING,
            escalation_level=CrisisEscalationLevel.MODERATE,
            severity_score=60,
            root_causes=CrisisContentGenerator.generate_root_causes(CrisisType.BORDER_DISPUTE),
            economic_impact=30,
            political_impact=40,
            military_impact=25,
            stability_impact=35,
            public_awareness=50,
            international_attention=30
        )
    
    def _create_incident_cascade_crisis(self, faction_pair: Tuple[str, str], incidents: List) -> DiplomaticCrisis:
        """Create a crisis based on cascading incidents."""
        faction_ids = [UUID(faction_pair[0]), UUID(faction_pair[1])]
        
        return DiplomaticCrisis(
            crisis_type=CrisisType.DIPLOMATIC_INCIDENT,
            title=CrisisDetectionUtils.create_crisis_title(CrisisType.DIPLOMATIC_INCIDENT, faction_ids),
            description=f"Cascading diplomatic incidents between factions requiring crisis intervention",
            primary_factions=faction_ids,
            affected_factions=[],
            status=CrisisStatus.ACTIVE,
            escalation_level=CrisisEscalationLevel.HIGH,
            severity_score=75,
            root_causes=["Multiple unresolved incidents", "Escalating tensions", "Diplomatic breakdown"],
            economic_impact=20,
            political_impact=60,
            military_impact=30,
            stability_impact=50,
            public_awareness=70,
            international_attention=40
        )
    
    def _create_negotiation_breakdown_crisis(self, negotiation) -> DiplomaticCrisis:
        """Create a crisis based on failed negotiations."""
        return DiplomaticCrisis(
            crisis_type=CrisisType.ALLIANCE_BREAKDOWN,
            title=CrisisDetectionUtils.create_crisis_title(CrisisType.ALLIANCE_BREAKDOWN, negotiation.parties),
            description="Critical negotiation failure threatening regional stability",
            primary_factions=negotiation.parties,
            affected_factions=[],
            status=CrisisStatus.DEVELOPING,
            escalation_level=CrisisEscalationLevel.MODERATE,
            severity_score=55,
            root_causes=["Negotiation breakdown", "Irreconcilable differences", "Failed diplomacy"],
            economic_impact=25,
            political_impact=70,
            military_impact=15,
            stability_impact=45,
            public_awareness=40,
            international_attention=50
        )
    
    def _create_treaty_violation_crisis(self, violation: TreatyViolation, treaty) -> DiplomaticCrisis:
        """Create a crisis based on treaty violations."""
        return DiplomaticCrisis(
            crisis_type=CrisisType.TERRITORIAL_DISPUTE,
            title=f"Treaty Violation Crisis",
            description=f"Serious treaty violation requiring crisis-level diplomatic intervention",
            primary_factions=treaty.parties,
            affected_factions=[],
            status=CrisisStatus.ACTIVE,
            escalation_level=CrisisEscalationLevel.HIGH,
            severity_score=80,
            root_causes=["Treaty violation", "Legal disputes", "Trust breakdown"],
            economic_impact=35,
            political_impact=75,
            military_impact=40,
            stability_impact=60,
            public_awareness=60,
            international_attention=70
        )
    
    def _create_ultimatum_crisis(self, ultimatum) -> DiplomaticCrisis:
        """Create a crisis based on ultimatum situations."""
        return DiplomaticCrisis(
            crisis_type=CrisisType.MILITARY_STANDOFF,
            title="Ultimatum Crisis",
            description="Rejected ultimatum leading to potential military confrontation",
            primary_factions=[ultimatum.issuer_id, ultimatum.recipient_id],
            affected_factions=[],
            status=CrisisStatus.ESCALATING,
            escalation_level=CrisisEscalationLevel.CRITICAL,
            severity_score=85,
            root_causes=["Ultimatum rejection", "Failed coercion", "Escalating demands"],
            economic_impact=40,
            political_impact=60,
            military_impact=80,
            stability_impact=70,
            public_awareness=80,
            international_attention=90
        )


class CrisisEscalationEngine:
    """Engine for managing crisis escalation."""
    
    def __init__(self, db_adapter: CrisisDatabaseAdapter):
        self.db_adapter = db_adapter
    
    def evaluate_escalation_triggers(self, crisis: DiplomaticCrisis) -> List[CrisisEscalationTrigger]:
        """Evaluate potential escalation triggers for a crisis."""
        triggers = []
        
        # Check various escalation factors
        triggers.extend(self._evaluate_military_triggers(crisis))
        triggers.extend(self._evaluate_economic_triggers(crisis))
        triggers.extend(self._evaluate_third_party_triggers(crisis))
        triggers.extend(self._evaluate_timeline_triggers(crisis))
        
        return triggers
    
    def process_escalation(self, crisis: DiplomaticCrisis, trigger: CrisisEscalationTrigger) -> DiplomaticCrisis:
        """Process an escalation trigger and update crisis."""
        if not CrisisEscalationCalculator.should_trigger_escalate(trigger):
            return crisis
        
        # Calculate new escalation level
        new_escalation_level = CrisisEscalationCalculator.calculate_new_escalation_level(crisis, trigger)
        
        # Update crisis
        crisis.escalation_level = new_escalation_level
        crisis.severity_score = min(100, crisis.severity_score + trigger.severity_increase)
        crisis.updated_at = datetime.utcnow()
        
        # Record the escalation trigger
        trigger.crisis_id = crisis.id
        self.db_adapter.create_escalation_trigger(trigger)
        
        return crisis
    
    def evaluate_de_escalation_opportunities(self, crisis: DiplomaticCrisis) -> List[str]:
        """Evaluate opportunities for de-escalation."""
        opportunities = []
        
        # Look for potential mediators
        potential_mediators = self._find_potential_mediators(crisis)
        if potential_mediators:
            opportunities.append("Third-party mediation available")
        
        # Check for mutual interests
        if crisis.crisis_type in [CrisisType.TRADE_WAR, CrisisType.RESOURCE_CONFLICT]:
            opportunities.append("Economic interdependence as de-escalation factor")
        
        # Timeline-based opportunities
        if crisis.created_at:
            days_active = (datetime.utcnow() - crisis.created_at).days
            if days_active >= 7:
                opportunities.append("Crisis fatigue may enable compromise")
        
        return opportunities
    
    def _evaluate_military_triggers(self, crisis: DiplomaticCrisis) -> List[CrisisEscalationTrigger]:
        """Evaluate military-related escalation triggers."""
        triggers = []
        
        if crisis.crisis_type in [CrisisType.BORDER_DISPUTE, CrisisType.MILITARY_STANDOFF]:
            trigger = CrisisEscalationTrigger(
                crisis_id=crisis.id,
                trigger_type="military_buildup",
                trigger_description="Military forces mobilizing near crisis zone",
                severity_increase=15,
                probability=30,
                escalation_factors=["Military preparation", "Strategic positioning"],
                mitigation_options=["Demilitarized zones", "Military observers"]
            )
            triggers.append(trigger)
        
        return triggers
    
    def _evaluate_economic_triggers(self, crisis: DiplomaticCrisis) -> List[CrisisEscalationTrigger]:
        """Evaluate economic-related escalation triggers."""
        triggers = []
        
        if crisis.crisis_type == CrisisType.TRADE_WAR:
            trigger = CrisisEscalationTrigger(
                crisis_id=crisis.id,
                trigger_type="economic_sanctions",
                trigger_description="New economic sanctions imposed",
                severity_increase=10,
                probability=40,
                escalation_factors=["Economic pressure", "Trade disruption"],
                mitigation_options=["Trade talks", "Economic cooperation"]
            )
            triggers.append(trigger)
        
        return triggers
    
    def _evaluate_third_party_triggers(self, crisis: DiplomaticCrisis) -> List[CrisisEscalationTrigger]:
        """Evaluate third-party escalation triggers."""
        triggers = []
        
        # General third-party intervention risk
        trigger = CrisisEscalationTrigger(
            crisis_id=crisis.id,
            trigger_type="third_party_involvement",
            trigger_description="Third party taking sides in crisis",
            severity_increase=12,
            probability=25,
            escalation_factors=["Alliance obligations", "Regional interests"],
            mitigation_options=["Neutral mediation", "International oversight"]
        )
        triggers.append(trigger)
        
        return triggers
    
    def _evaluate_timeline_triggers(self, crisis: DiplomaticCrisis) -> List[CrisisEscalationTrigger]:
        """Evaluate time-based escalation triggers."""
        triggers = []
        
        if crisis.created_at:
            days_active = (datetime.utcnow() - crisis.created_at).days
            
            if days_active >= 30:
                trigger = CrisisEscalationTrigger(
                    crisis_id=crisis.id,
                    trigger_type="prolonged_crisis",
                    trigger_description="Crisis duration exceeding stability thresholds",
                    severity_increase=8,
                    probability=50,
                    escalation_factors=["Crisis fatigue", "Hardened positions"],
                    mitigation_options=["Deadline negotiations", "International pressure"]
                )
                triggers.append(trigger)
        
        return triggers
    
    def _find_potential_mediators(self, crisis: DiplomaticCrisis) -> List[UUID]:
        """Find potential mediators for crisis de-escalation."""
        # This would use actual faction data in a real implementation
        # For now, return empty list as we don't have faction relationship data
        return []


class CrisisResolutionEngine:
    """Engine for generating and managing crisis resolution attempts."""
    
    def __init__(self, db_adapter: CrisisDatabaseAdapter):
        self.db_adapter = db_adapter
    
    def generate_resolution_pathways(self, crisis: DiplomaticCrisis) -> List[CrisisResolutionAttempt]:
        """Generate potential resolution pathways for a crisis."""
        pathways = []
        
        # Generate different types of resolution attempts
        pathways.append(self._create_diplomatic_mediation_pathway(crisis))
        pathways.append(self._create_economic_incentives_pathway(crisis))
        pathways.append(self._create_arbitration_pathway(crisis))
        pathways.append(self._create_face_saving_pathway(crisis))
        
        # Add international pressure for high-profile crises
        if crisis.international_attention > 60:
            pathways.append(self._create_international_pressure_pathway(crisis))
        
        # Calculate success probabilities
        for pathway in pathways:
            pathway.success_probability = CrisisResolutionAnalyzer.calculate_resolution_success_probability(pathway, crisis)
        
        return pathways
    
    def _create_diplomatic_mediation_pathway(self, crisis: DiplomaticCrisis) -> CrisisResolutionAttempt:
        """Create a diplomatic mediation resolution pathway."""
        return CrisisResolutionAttempt(
            crisis_id=crisis.id,
            resolution_type=ResolutionType.DIPLOMATIC_MEDIATION,
            title="Neutral Mediation",
            description="Engage neutral third-party mediators to facilitate dialogue",
            proposed_by=crisis.primary_factions[0],  # First faction proposes
            implementation_steps=[
                "Identify neutral mediators",
                "Establish mediation framework",
                "Conduct mediated discussions",
                "Draft resolution agreement"
            ],
            success_conditions=[
                "All parties agree to mediation",
                "Neutral mediator accepted",
                "Framework agreement reached"
            ],
            risks=[
                "Mediator bias concerns",
                "Process delays",
                "Failed negotiations"
            ],
            expected_duration=timedelta(days=30)
        )
    
    def _create_economic_incentives_pathway(self, crisis: DiplomaticCrisis) -> CrisisResolutionAttempt:
        """Create an economic incentives resolution pathway."""
        return CrisisResolutionAttempt(
            crisis_id=crisis.id,
            resolution_type=ResolutionType.ECONOMIC_INCENTIVES,
            title="Economic Cooperation Package",
            description="Resolve crisis through economic incentives and cooperation",
            proposed_by=crisis.primary_factions[0],
            implementation_steps=[
                "Assess economic interests",
                "Design incentive package",
                "Negotiate terms",
                "Implement agreements"
            ],
            success_conditions=[
                "Mutual economic benefit identified",
                "Resource commitments secured",
                "Implementation timeline agreed"
            ],
            risks=[
                "Economic conditions change",
                "Insufficient resources",
                "Unequal benefits"
            ],
            expected_duration=timedelta(days=45)
        )
    
    def _create_arbitration_pathway(self, crisis: DiplomaticCrisis) -> CrisisResolutionAttempt:
        """Create an arbitration resolution pathway."""
        return CrisisResolutionAttempt(
            crisis_id=crisis.id,
            resolution_type=ResolutionType.ARBITRATION,
            title="International Arbitration",
            description="Submit dispute to binding international arbitration",
            proposed_by=crisis.primary_factions[0],
            implementation_steps=[
                "Select arbitration panel",
                "Define arbitration scope",
                "Present cases",
                "Implement decision"
            ],
            success_conditions=[
                "Arbitrators agreed upon",
                "Binding commitment given",
                "Decision accepted"
            ],
            risks=[
                "Unfavorable ruling",
                "Enforcement challenges",
                "Process legitimacy questions"
            ],
            expected_duration=timedelta(days=60)
        )
    
    def _create_face_saving_pathway(self, crisis: DiplomaticCrisis) -> CrisisResolutionAttempt:
        """Create a face-saving compromise pathway."""
        return CrisisResolutionAttempt(
            crisis_id=crisis.id,
            resolution_type=ResolutionType.FACE_SAVING_COMPROMISE,
            title="Face-Saving Compromise",
            description="Structured compromise allowing all parties to claim success",
            proposed_by=crisis.primary_factions[0],
            implementation_steps=[
                "Identify core interests",
                "Design mutual concessions",
                "Create positive narratives",
                "Implement gradually"
            ],
            success_conditions=[
                "Core interests protected",
                "Public narratives aligned",
                "Implementation schedule agreed"
            ],
            risks=[
                "Narrative breakdown",
                "Public rejection",
                "Implementation failures"
            ],
            expected_duration=timedelta(days=35)
        )
    
    def _create_international_pressure_pathway(self, crisis: DiplomaticCrisis) -> CrisisResolutionAttempt:
        """Create an international pressure resolution pathway."""
        return CrisisResolutionAttempt(
            crisis_id=crisis.id,
            resolution_type=ResolutionType.INTERNATIONAL_PRESSURE,
            title="International Pressure Campaign",
            description="Mobilize international pressure for crisis resolution",
            proposed_by=crisis.primary_factions[0],
            implementation_steps=[
                "Build international coalition",
                "Coordinate pressure campaign",
                "Apply diplomatic sanctions",
                "Negotiate under pressure"
            ],
            success_conditions=[
                "Broad international support",
                "Effective pressure applied",
                "Face-saving exit provided"
            ],
            risks=[
                "Insufficient international support",
                "Counterproductive effects",
                "Coalition fragmentation"
            ],
            expected_duration=timedelta(days=50)
        )


class CrisisManagementService:
    """Main service for diplomatic crisis management."""
    
    def __init__(self, db_adapter: CrisisDatabaseAdapter):
        self.db_adapter = db_adapter
        self.detection_engine = CrisisDetectionEngine(db_adapter)
        self.escalation_engine = CrisisEscalationEngine(db_adapter)
        self.resolution_engine = CrisisResolutionEngine(db_adapter)
    
    def scan_for_crises(self) -> List[DiplomaticCrisis]:
        """Scan for emerging crises and create them if needed."""
        potential_crises = self.detection_engine.detect_emerging_crises()
        
        created_crises = []
        for crisis in potential_crises:
            created_crisis = self.create_crisis(crisis)
            created_crises.append(created_crisis)
        
        return created_crises
    
    def create_crisis(self, crisis: DiplomaticCrisis) -> DiplomaticCrisis:
        """Create a new crisis in the system."""
        # Validate crisis data
        if not crisis.id:
            crisis.id = uuid4()
        
        if not crisis.created_at:
            crisis.created_at = datetime.utcnow()
        
        if not crisis.updated_at:
            crisis.updated_at = datetime.utcnow()
        
        # Set default values if missing
        if crisis.severity_score is None:
            crisis.severity_score = 50
        
        if not crisis.root_causes:
            crisis.root_causes = CrisisContentGenerator.generate_root_causes(crisis.crisis_type)
        
        # Save to database
        return self.db_adapter.create_crisis(crisis)
    
    def get_active_crises(self) -> List[DiplomaticCrisis]:
        """Get all currently active crises."""
        return self.db_adapter.get_active_crises()
    
    def get_crises_by_faction(self, faction_id: UUID) -> List[DiplomaticCrisis]:
        """Get crises involving a specific faction."""
        return self.db_adapter.get_crises_by_faction(faction_id)
    
    def get_crisis_by_id(self, crisis_id: UUID) -> Optional[DiplomaticCrisis]:
        """Get a specific crisis by ID."""
        return self.db_adapter.get_crisis_by_id(crisis_id)
    
    def update_crisis_escalation(self, crisis_id: UUID) -> DiplomaticCrisis:
        """Evaluate and process crisis escalation."""
        crisis = self.get_crisis_by_id(crisis_id)
        if not crisis:
            raise ValueError(f"Crisis {crisis_id} not found")
        
        # Evaluate escalation triggers
        triggers = self.escalation_engine.evaluate_escalation_triggers(crisis)
        
        # Process each trigger
        for trigger in triggers:
            crisis = self.escalation_engine.process_escalation(crisis, trigger)
        
        # Update crisis in database
        updates = {
            'escalation_level': crisis.escalation_level,
            'severity_score': crisis.severity_score,
            'updated_at': crisis.updated_at
        }
        
        return self.db_adapter.update_crisis(crisis_id, updates)
    
    def create_resolution_attempt(self, resolution: CrisisResolutionAttempt) -> CrisisResolutionAttempt:
        """Create a new resolution attempt for a crisis."""
        if not resolution.id:
            resolution.id = uuid4()
        
        if not resolution.created_at:
            resolution.created_at = datetime.utcnow()
        
        return self.db_adapter.create_resolution_attempt(resolution)
    
    def generate_resolution_pathways(self, crisis_id: UUID) -> List[CrisisResolutionAttempt]:
        """Generate potential resolution pathways for a crisis."""
        crisis = self.get_crisis_by_id(crisis_id)
        if not crisis:
            raise ValueError(f"Crisis {crisis_id} not found")
        
        return self.resolution_engine.generate_resolution_pathways(crisis)
    
    def generate_crisis_impact_assessment(self, crisis_id: UUID, 
                                         assessor_faction: Optional[UUID] = None) -> CrisisImpactAssessment:
        """Generate a comprehensive impact assessment for a crisis."""
        crisis = self.get_crisis_by_id(crisis_id)
        if not crisis:
            raise ValueError(f"Crisis {crisis_id} not found")
        
        # Use first primary faction as assessor if not specified
        if not assessor_faction:
            assessor_faction = crisis.primary_factions[0]
        
        assessment = CrisisImpactAssessment(
            crisis_id=crisis_id,
            assessor_faction=assessor_faction,
            economic_impact=CrisisImpactCalculator.calculate_economic_impact(crisis, assessor_faction),
            political_impact=CrisisImpactCalculator.calculate_political_impact(crisis, assessor_faction),
            military_impact=CrisisImpactCalculator.calculate_military_impact(crisis, assessor_faction),
            social_impact=CrisisImpactCalculator.calculate_social_impact(crisis, assessor_faction),
            escalation_risk=CrisisEscalationCalculator.calculate_escalation_risk(crisis),
            spillover_risk=CrisisImpactCalculator.calculate_spillover_risk(crisis),
            resolution_probability=CrisisResolutionAnalyzer.calculate_resolution_probability(crisis),
            recommended_actions=CrisisResolutionAnalyzer.generate_recommended_actions(crisis),
            priority_interventions=CrisisResolutionAnalyzer.generate_priority_interventions(crisis),
            confidence_level=85  # Base confidence level
        )
        
        return self.db_adapter.create_impact_assessment(assessment) 