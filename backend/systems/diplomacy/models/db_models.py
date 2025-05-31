"""
SQLAlchemy ORM Models for Diplomacy System

This module contains the database models for diplomatic entities,
replacing the file-based storage with proper database persistence.
"""

from datetime import datetime
from typing import Dict, Any, List
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum as SQLEnum, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from backend.systems.diplomacy.models import (
    DiplomaticStatus, TreatyType, TreatyStatus, NegotiationStatus,
    DiplomaticEventType, TreatyViolationType, DiplomaticIncidentType,
    DiplomaticIncidentSeverity, UltimatumStatus, SanctionType, SanctionStatus
)

# Use a simple declarative base for now
Base = declarative_base()


class DiplomaticRelationship(Base):
    """Database model for faction relationships and tension levels."""
    
    __tablename__ = "diplomatic_relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    faction_a_id = Column(UUID(as_uuid=True), nullable=False)
    faction_b_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(SQLEnum(DiplomaticStatus), default=DiplomaticStatus.NEUTRAL, nullable=False)
    trust_level = Column(Integer, default=50, nullable=False)  # 0-100
    tension_level = Column(Integer, default=0, nullable=False)  # 0-100
    last_interaction = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Ensure unique relationships (A-B is same as B-A)
    __table_args__ = (
        UniqueConstraint('faction_a_id', 'faction_b_id', name='unique_faction_relationship'),
        Index('idx_faction_relationships', 'faction_a_id', 'faction_b_id'),
        Index('idx_diplomatic_status', 'status'),
    )


class Treaty(Base):
    """Database model for formal agreements between factions."""
    
    __tablename__ = "treaties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    treaty_type = Column(SQLEnum(TreatyType), nullable=False)
    status = Column(SQLEnum(TreatyStatus), default=TreatyStatus.DRAFT, nullable=False)
    terms = Column(JSON, default=dict)
    parties = Column(JSON, nullable=False)  # List of faction UUIDs
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_public = Column(Boolean, default=True)
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey('negotiations.id'), nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    negotiation = relationship("Negotiation", back_populates="resulting_treaty")
    violations = relationship("TreatyViolation", back_populates="treaty")
    
    __table_args__ = (
        Index('idx_treaty_type', 'treaty_type'),
        Index('idx_treaty_status', 'status'),
        Index('idx_treaty_parties', 'parties'),
    )


class Negotiation(Base):
    """Database model for ongoing diplomatic negotiations."""
    
    __tablename__ = "negotiations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    parties = Column(JSON, nullable=False)  # List of faction UUIDs
    initiator_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(SQLEnum(NegotiationStatus), default=NegotiationStatus.PENDING, nullable=False)
    treaty_type = Column(SQLEnum(TreatyType), nullable=True)
    current_offer = Column(JSON, default=dict)
    offers_history = Column(JSON, default=list)
    meta_data = Column(JSON, default=dict)
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    resulting_treaty = relationship("Treaty", back_populates="negotiation", uselist=False)
    events = relationship("DiplomaticEvent", back_populates="negotiation")
    
    __table_args__ = (
        Index('idx_negotiation_status', 'status'),
        Index('idx_negotiation_initiator', 'initiator_id'),
        Index('idx_negotiation_parties', 'parties'),
    )


class DiplomaticEvent(Base):
    """Database model for historical diplomatic events."""
    
    __tablename__ = "diplomatic_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type = Column(SQLEnum(DiplomaticEventType), nullable=False)
    description = Column(Text, nullable=False)
    participants = Column(JSON, nullable=False)  # List of faction UUIDs
    event_data = Column(JSON, default=dict)
    treaty_id = Column(UUID(as_uuid=True), ForeignKey('treaties.id'), nullable=True)
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey('negotiations.id'), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_public = Column(Boolean, default=True)
    
    # Relationships
    treaty = relationship("Treaty")
    negotiation = relationship("Negotiation", back_populates="events")
    
    __table_args__ = (
        Index('idx_event_type', 'event_type'),
        Index('idx_event_timestamp', 'timestamp'),
        Index('idx_event_participants', 'participants'),
    )


class TreatyViolation(Base):
    """Database model for treaty breach records."""
    
    __tablename__ = "treaty_violations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    treaty_id = Column(UUID(as_uuid=True), ForeignKey('treaties.id'), nullable=False)
    violator_id = Column(UUID(as_uuid=True), nullable=False)
    violation_type = Column(SQLEnum(TreatyViolationType), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict)
    reported_by = Column(UUID(as_uuid=True), nullable=False)
    severity = Column(Integer, default=50, nullable=False)  # 0-100
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(UUID(as_uuid=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved = Column(Boolean, default=False)
    resolution_details = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    treaty = relationship("Treaty", back_populates="violations")
    
    __table_args__ = (
        Index('idx_violation_treaty', 'treaty_id'),
        Index('idx_violation_violator', 'violator_id'),
        Index('idx_violation_type', 'violation_type'),
        Index('idx_violation_resolved', 'resolved'),
    )


class DiplomaticIncident(Base):
    """Database model for conflict and incident tracking."""
    
    __tablename__ = "diplomatic_incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    incident_type = Column(SQLEnum(DiplomaticIncidentType), nullable=False)
    perpetrator_id = Column(UUID(as_uuid=True), nullable=False)
    victim_id = Column(UUID(as_uuid=True), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict)
    severity = Column(SQLEnum(DiplomaticIncidentSeverity), default=DiplomaticIncidentSeverity.MODERATE)
    tension_impact = Column(Integer, default=20)
    public = Column(Boolean, default=True)
    witnessed_by = Column(JSON, default=list)  # List of faction UUIDs
    related_event_id = Column(UUID(as_uuid=True), nullable=True)
    related_treaty_id = Column(UUID(as_uuid=True), ForeignKey('treaties.id'), nullable=True)
    resolved = Column(Boolean, default=False)
    resolution_details = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_incident_type', 'incident_type'),
        Index('idx_incident_perpetrator', 'perpetrator_id'),
        Index('idx_incident_victim', 'victim_id'),
        Index('idx_incident_severity', 'severity'),
        Index('idx_incident_resolved', 'resolved'),
    )


class Ultimatum(Base):
    """Database model for diplomatic ultimatum records."""
    
    __tablename__ = "ultimatums"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    issuer_id = Column(UUID(as_uuid=True), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), nullable=False)
    demands = Column(JSON, nullable=False)
    consequences = Column(JSON, nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(UltimatumStatus), default=UltimatumStatus.PENDING, nullable=False)
    justification = Column(Text, nullable=False)
    public = Column(Boolean, default=True)
    witnessed_by = Column(JSON, default=list)  # List of faction UUIDs
    related_incident_id = Column(UUID(as_uuid=True), nullable=True)
    related_treaty_id = Column(UUID(as_uuid=True), ForeignKey('treaties.id'), nullable=True)
    related_event_id = Column(UUID(as_uuid=True), nullable=True)
    response_justification = Column(Text, nullable=True)
    tension_change_on_issue = Column(Integer, default=20)
    tension_change_on_accept = Column(Integer, default=-10)
    tension_change_on_reject = Column(Integer, default=40)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_ultimatum_issuer', 'issuer_id'),
        Index('idx_ultimatum_recipient', 'recipient_id'),
        Index('idx_ultimatum_status', 'status'),
        Index('idx_ultimatum_deadline', 'deadline'),
    )


class Sanction(Base):
    """Database model for economic and diplomatic sanctions."""
    
    __tablename__ = "sanctions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    imposer_id = Column(UUID(as_uuid=True), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)
    sanction_type = Column(SQLEnum(SanctionType), nullable=False)
    status = Column(SQLEnum(SanctionStatus), default=SanctionStatus.ACTIVE, nullable=False)
    description = Column(Text, nullable=False)
    justification = Column(Text, nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    lifted_date = Column(DateTime(timezone=True), nullable=True)
    conditions_for_lifting = Column(JSON, default=dict)
    severity = Column(Integer, default=50)  # 0-100
    economic_impact = Column(Integer, default=50)  # 0-100
    diplomatic_impact = Column(Integer, default=50)  # 0-100
    enforcement_measures = Column(JSON, default=dict)
    supporting_factions = Column(JSON, default=list)  # List of faction UUIDs
    opposing_factions = Column(JSON, default=list)  # List of faction UUIDs
    violations = Column(JSON, default=list)  # List of violation records
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_sanction_imposer', 'imposer_id'),
        Index('idx_sanction_target', 'target_id'),
        Index('idx_sanction_type', 'sanction_type'),
        Index('idx_sanction_status', 'status'),
    ) 