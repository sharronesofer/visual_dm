"""
Crisis Management Database Adapter

Handles all database operations for diplomatic crisis management including 
crisis detection, escalation tracking, and resolution management.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from backend.systems.diplomacy.models.crisis_models import (
    DiplomaticCrisis, CrisisResolutionAttempt, CrisisIntervention,
    CrisisEscalationTrigger, CrisisImpactAssessment,
    CrisisType, CrisisEscalationLevel, CrisisStatus, ResolutionType, InterventionType
)
from backend.infrastructure.databases.diplomacy import (
    DiplomaticCrisis as DBCrisis,
    CrisisResolutionAttempt as DBResolutionAttempt,
    CrisisIntervention as DBIntervention,
    CrisisEscalationTrigger as DBEscalationTrigger,
    CrisisImpactAssessment as DBImpactAssessment,
    DiplomaticRelationship,
    DiplomaticIncident,
    DiplomaticEvent,
    Ultimatum,
    Sanction,
    Treaty,
    Negotiation
)
from backend.systems.diplomacy.models.core_models import (
    DiplomaticStatus, DiplomaticIncidentSeverity, DiplomaticEventType, TreatyViolation,
    NegotiationStatus, UltimatumStatus
)


class CrisisDatabaseAdapter:
    """Database adapter for crisis management operations."""
    
    def __init__(self, db_session: Session):
        """Initialize the adapter with a database session."""
        self.db = db_session
    
    # === Crisis CRUD Operations ===
    
    def create_crisis(self, crisis: DiplomaticCrisis) -> DiplomaticCrisis:
        """Create a new crisis in the database."""
        db_crisis = DBCrisis(
            id=crisis.id,
            crisis_type=crisis.crisis_type,
            title=crisis.title,
            description=crisis.description,
            primary_factions=crisis.primary_factions,
            affected_factions=crisis.affected_factions or [],
            status=crisis.status,
            escalation_level=crisis.escalation_level,
            severity_score=crisis.severity_score,
            root_causes=crisis.root_causes or [],
            created_at=crisis.created_at or datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expected_duration=crisis.expected_duration,
            economic_impact=crisis.economic_impact,
            political_impact=crisis.political_impact,
            military_impact=crisis.military_impact,
            stability_impact=crisis.stability_impact,
            public_awareness=crisis.public_awareness,
            international_attention=crisis.international_attention
        )
        
        self.db.add(db_crisis)
        self.db.commit()
        self.db.refresh(db_crisis)
        
        return self._db_crisis_to_model(db_crisis)
    
    def get_crisis_by_id(self, crisis_id: UUID) -> Optional[DiplomaticCrisis]:
        """Get a crisis by ID."""
        db_crisis = self.db.query(DBCrisis).filter(DBCrisis.id == crisis_id).first()
        return self._db_crisis_to_model(db_crisis) if db_crisis else None
    
    def update_crisis(self, crisis_id: UUID, updates: Dict) -> Optional[DiplomaticCrisis]:
        """Update a crisis with the provided updates."""
        db_crisis = self.db.query(DBCrisis).filter(DBCrisis.id == crisis_id).first()
        if not db_crisis:
            return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(db_crisis, key):
                setattr(db_crisis, key, value)
        
        db_crisis.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_crisis)
        
        return self._db_crisis_to_model(db_crisis)
    
    def get_active_crises(self) -> List[DiplomaticCrisis]:
        """Get all active crises."""
        db_crises = self.db.query(DBCrisis).filter(
            DBCrisis.status.in_([CrisisStatus.DEVELOPING, CrisisStatus.ACTIVE, CrisisStatus.ESCALATING])
        ).all()
        
        return [self._db_crisis_to_model(db_crisis) for db_crisis in db_crises]
    
    def get_crises_by_faction(self, faction_id: UUID) -> List[DiplomaticCrisis]:
        """Get crises involving a specific faction."""
        db_crises = self.db.query(DBCrisis).filter(
            or_(
                DBCrisis.primary_factions.contains([str(faction_id)]),
                DBCrisis.affected_factions.contains([str(faction_id)])
            )
        ).all()
        
        return [self._db_crisis_to_model(db_crisis) for db_crisis in db_crises]
    
    # === Crisis Detection Queries ===
    
    def get_high_tension_relationships(self, tension_threshold: int = 80) -> List[DiplomaticRelationship]:
        """Get relationships with tension above threshold."""
        return self.db.query(DiplomaticRelationship).filter(
            DiplomaticRelationship.tension_level >= tension_threshold
        ).all()
    
    def get_existing_crisis_for_factions(self, faction_ids: List[UUID]) -> Optional[DBCrisis]:
        """Check if there's already an active crisis involving these factions."""
        faction_str_list = [str(fid) for fid in faction_ids]
        
        return self.db.query(DBCrisis).filter(
            and_(
                DBCrisis.status.in_([CrisisStatus.DEVELOPING, CrisisStatus.ACTIVE, CrisisStatus.ESCALATING]),
                or_(
                    DBCrisis.primary_factions.contains(faction_str_list),
                    DBCrisis.primary_factions.contains(faction_str_list[::-1])  # Reverse order
                )
            )
        ).first()
    
    def get_recent_major_incidents(self, days: int = 30) -> List[DiplomaticIncident]:
        """Get recent major diplomatic incidents."""
        recent_cutoff = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(DiplomaticIncident).filter(
            and_(
                DiplomaticIncident.severity.in_([
                    DiplomaticIncidentSeverity.MAJOR, 
                    DiplomaticIncidentSeverity.CRITICAL
                ]),
                DiplomaticIncident.created_at >= recent_cutoff,
                DiplomaticIncident.resolved == False
            )
        ).all()
    
    def get_failed_negotiations(self, days: int = 14) -> List[Negotiation]:
        """Get recently failed high-stakes negotiations."""
        recent_cutoff = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(Negotiation).filter(
            and_(
                Negotiation.status.in_([NegotiationStatus.BREAKDOWN, NegotiationStatus.REJECTED]),
                Negotiation.updated_at >= recent_cutoff
            )
        ).all()
    
    def get_major_treaty_violations(self, severity_threshold: int = 80) -> List[TreatyViolation]:
        """Get unresolved major treaty violations."""
        return self.db.query(TreatyViolation).filter(
            and_(
                TreatyViolation.severity >= severity_threshold,
                TreatyViolation.resolved == False
            )
        ).all()
    
    def get_crisis_ultimatums(self) -> List[Ultimatum]:
        """Get rejected or expired ultimatums that could trigger crises."""
        return self.db.query(Ultimatum).filter(
            Ultimatum.status.in_([UltimatumStatus.REJECTED, UltimatumStatus.EXPIRED])
        ).all()
    
    def get_treaty_by_id(self, treaty_id: UUID) -> Optional[Treaty]:
        """Get a treaty by ID."""
        return self.db.query(Treaty).filter(Treaty.id == treaty_id).first()
    
    # === Resolution Attempt Operations ===
    
    def create_resolution_attempt(self, resolution: CrisisResolutionAttempt) -> CrisisResolutionAttempt:
        """Create a new crisis resolution attempt."""
        db_resolution = DBResolutionAttempt(
            id=resolution.id,
            crisis_id=resolution.crisis_id,
            resolution_type=resolution.resolution_type,
            title=resolution.title,
            description=resolution.description,
            proposed_by=resolution.proposed_by,
            supported_by=resolution.supported_by or [],
            opposed_by=resolution.opposed_by or [],
            success_probability=resolution.success_probability,
            expected_duration=resolution.expected_duration,
            resource_requirements=resolution.resource_requirements or {},
            implementation_steps=resolution.implementation_steps or [],
            success_conditions=resolution.success_conditions or [],
            risks=resolution.risks or [],
            created_at=resolution.created_at or datetime.utcnow(),
            status=resolution.status,
            actual_outcome=resolution.actual_outcome,
            lessons_learned=resolution.lessons_learned or []
        )
        
        self.db.add(db_resolution)
        self.db.commit()
        self.db.refresh(db_resolution)
        
        return self._db_resolution_to_model(db_resolution)
    
    def get_resolution_attempts_for_crisis(self, crisis_id: UUID) -> List[CrisisResolutionAttempt]:
        """Get all resolution attempts for a crisis."""
        db_resolutions = self.db.query(DBResolutionAttempt).filter(
            DBResolutionAttempt.crisis_id == crisis_id
        ).order_by(desc(DBResolutionAttempt.created_at)).all()
        
        return [self._db_resolution_to_model(db_res) for db_res in db_resolutions]
    
    # === Impact Assessment Operations ===
    
    def create_impact_assessment(self, assessment: CrisisImpactAssessment) -> CrisisImpactAssessment:
        """Create a new crisis impact assessment."""
        db_assessment = DBImpactAssessment(
            id=assessment.id,
            crisis_id=assessment.crisis_id,
            assessor_faction=assessment.assessor_faction,
            assessment_date=assessment.assessment_date or datetime.utcnow(),
            economic_impact=assessment.economic_impact,
            political_impact=assessment.political_impact,
            military_impact=assessment.military_impact,
            social_impact=assessment.social_impact,
            escalation_risk=assessment.escalation_risk,
            spillover_risk=assessment.spillover_risk,
            resolution_probability=assessment.resolution_probability,
            recommended_actions=assessment.recommended_actions or [],
            priority_interventions=assessment.priority_interventions or [],
            resource_allocation=assessment.resource_allocation or {},
            confidence_level=assessment.confidence_level,
            external_factors=assessment.external_factors or []
        )
        
        self.db.add(db_assessment)
        self.db.commit()
        self.db.refresh(db_assessment)
        
        return self._db_assessment_to_model(db_assessment)
    
    def get_assessments_for_crisis(self, crisis_id: UUID) -> List[CrisisImpactAssessment]:
        """Get all impact assessments for a crisis."""
        db_assessments = self.db.query(DBImpactAssessment).filter(
            DBImpactAssessment.crisis_id == crisis_id
        ).order_by(desc(DBImpactAssessment.assessment_date)).all()
        
        return [self._db_assessment_to_model(db_ass) for db_ass in db_assessments]
    
    # === Escalation Trigger Operations ===
    
    def create_escalation_trigger(self, trigger: CrisisEscalationTrigger) -> CrisisEscalationTrigger:
        """Create a new escalation trigger record."""
        db_trigger = DBEscalationTrigger(
            id=trigger.id,
            crisis_id=trigger.crisis_id,
            trigger_type=trigger.trigger_type,
            trigger_description=trigger.trigger_description,
            severity_increase=trigger.severity_increase,
            probability=trigger.probability,
            detected_at=trigger.detected_at or datetime.utcnow(),
            related_event_id=trigger.related_event_id,
            faction_responsible=trigger.faction_responsible,
            escalation_factors=trigger.escalation_factors or [],
            mitigation_options=trigger.mitigation_options or []
        )
        
        self.db.add(db_trigger)
        self.db.commit()
        self.db.refresh(db_trigger)
        
        return self._db_trigger_to_model(db_trigger)
    
    def get_triggers_for_crisis(self, crisis_id: UUID) -> List[CrisisEscalationTrigger]:
        """Get escalation triggers for a crisis."""
        db_triggers = self.db.query(DBEscalationTrigger).filter(
            DBEscalationTrigger.crisis_id == crisis_id
        ).order_by(desc(DBEscalationTrigger.detected_at)).all()
        
        return [self._db_trigger_to_model(db_trigger) for db_trigger in db_triggers]
    
    # === Model Conversion Methods ===
    
    def _db_crisis_to_model(self, db_crisis: DBCrisis) -> DiplomaticCrisis:
        """Convert database crisis to domain model."""
        return DiplomaticCrisis(
            id=db_crisis.id,
            crisis_type=db_crisis.crisis_type,
            title=db_crisis.title,
            description=db_crisis.description,
            primary_factions=[UUID(fid) for fid in db_crisis.primary_factions],
            affected_factions=[UUID(fid) for fid in (db_crisis.affected_factions or [])],
            status=db_crisis.status,
            escalation_level=db_crisis.escalation_level,
            severity_score=db_crisis.severity_score,
            root_causes=db_crisis.root_causes or [],
            created_at=db_crisis.created_at,
            updated_at=db_crisis.updated_at,
            resolved_at=db_crisis.resolved_at,
            expected_duration=db_crisis.expected_duration,
            actual_duration=db_crisis.actual_duration,
            economic_impact=db_crisis.economic_impact,
            political_impact=db_crisis.political_impact,
            military_impact=db_crisis.military_impact,
            stability_impact=db_crisis.stability_impact,
            public_awareness=db_crisis.public_awareness,
            international_attention=db_crisis.international_attention,
            resolution_summary=db_crisis.resolution_summary
        )
    
    def _db_resolution_to_model(self, db_resolution: DBResolutionAttempt) -> CrisisResolutionAttempt:
        """Convert database resolution attempt to domain model."""
        return CrisisResolutionAttempt(
            id=db_resolution.id,
            crisis_id=db_resolution.crisis_id,
            resolution_type=db_resolution.resolution_type,
            title=db_resolution.title,
            description=db_resolution.description,
            proposed_by=db_resolution.proposed_by,
            supported_by=[UUID(fid) for fid in (db_resolution.supported_by or [])],
            opposed_by=[UUID(fid) for fid in (db_resolution.opposed_by or [])],
            success_probability=db_resolution.success_probability,
            expected_duration=db_resolution.expected_duration,
            resource_requirements=db_resolution.resource_requirements or {},
            implementation_steps=db_resolution.implementation_steps or [],
            success_conditions=db_resolution.success_conditions or [],
            risks=db_resolution.risks or [],
            created_at=db_resolution.created_at,
            status=db_resolution.status,
            executed_at=db_resolution.executed_at,
            completed_at=db_resolution.completed_at,
            actual_outcome=db_resolution.actual_outcome,
            lessons_learned=db_resolution.lessons_learned or []
        )
    
    def _db_assessment_to_model(self, db_assessment: DBImpactAssessment) -> CrisisImpactAssessment:
        """Convert database impact assessment to domain model."""
        return CrisisImpactAssessment(
            id=db_assessment.id,
            crisis_id=db_assessment.crisis_id,
            assessor_faction=db_assessment.assessor_faction,
            assessment_date=db_assessment.assessment_date,
            economic_impact=db_assessment.economic_impact,
            political_impact=db_assessment.political_impact,
            military_impact=db_assessment.military_impact,
            social_impact=db_assessment.social_impact,
            escalation_risk=db_assessment.escalation_risk,
            spillover_risk=db_assessment.spillover_risk,
            resolution_probability=db_assessment.resolution_probability,
            recommended_actions=db_assessment.recommended_actions or [],
            priority_interventions=db_assessment.priority_interventions or [],
            resource_allocation=db_assessment.resource_allocation or {},
            confidence_level=db_assessment.confidence_level,
            external_factors=db_assessment.external_factors or []
        )
    
    def _db_trigger_to_model(self, db_trigger: DBEscalationTrigger) -> CrisisEscalationTrigger:
        """Convert database escalation trigger to domain model."""
        return CrisisEscalationTrigger(
            id=db_trigger.id,
            crisis_id=db_trigger.crisis_id,
            trigger_type=db_trigger.trigger_type,
            trigger_description=db_trigger.trigger_description,
            severity_increase=db_trigger.severity_increase,
            probability=db_trigger.probability,
            detected_at=db_trigger.detected_at,
            related_event_id=db_trigger.related_event_id,
            faction_responsible=db_trigger.faction_responsible,
            escalation_factors=db_trigger.escalation_factors or [],
            mitigation_options=db_trigger.mitigation_options or []
        ) 