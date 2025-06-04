"""
SQLAlchemy database models for the diplomacy system.

These models define the database schema for diplomatic entities.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from backend.systems.diplomacy.models.core_models import (
    DiplomaticStatus, TreatyType, TreatyStatus, NegotiationStatus,
    DiplomaticEventType, TreatyViolationType, DiplomaticIncidentType,
    DiplomaticIncidentSeverity, UltimatumStatus, SanctionType, SanctionStatus
)

Base = declarative_base()


class DiplomaticRelationship(Base):
    """SQLAlchemy model for diplomatic relationships between factions."""
    
    __tablename__ = "diplomatic_relationships"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    faction_a_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    faction_b_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    status = Column(SQLEnum(DiplomaticStatus), nullable=False, default=DiplomaticStatus.NEUTRAL)
    trust_level = Column(Integer, nullable=False, default=50)  # 0-100
    tension_level = Column(Integer, nullable=False, default=0)  # -100 to 100
    last_interaction = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Treaty(Base):
    """SQLAlchemy model for treaties."""
    
    __tablename__ = "treaties"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    treaty_type = Column(SQLEnum(TreatyType), nullable=False)
    status = Column(SQLEnum(TreatyStatus), nullable=False, default=TreatyStatus.DRAFT)
    terms = Column(JSON, nullable=True)
    parties = Column(ARRAY(String), nullable=False)  # Array of faction UUIDs as strings
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_public = Column(Boolean, nullable=False, default=True)
    negotiation_id = Column(PGUUID(as_uuid=True), nullable=True)
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Negotiation(Base):
    """SQLAlchemy model for negotiations."""
    
    __tablename__ = "negotiations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    parties = Column(ARRAY(String), nullable=False)  # Array of faction UUIDs as strings
    initiator_id = Column(PGUUID(as_uuid=True), nullable=False)
    status = Column(SQLEnum(NegotiationStatus), nullable=False, default=NegotiationStatus.ACTIVE)
    current_offer_id = Column(PGUUID(as_uuid=True), nullable=True)
    treaty_type = Column(SQLEnum(TreatyType), nullable=True)
    end_date = Column(DateTime, nullable=True)
    result_treaty_id = Column(PGUUID(as_uuid=True), nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class NegotiationOffer(Base):
    """SQLAlchemy model for negotiation offers."""
    
    __tablename__ = "negotiation_offers"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    negotiation_id = Column(PGUUID(as_uuid=True), ForeignKey("negotiations.id"), nullable=False)
    faction_id = Column(PGUUID(as_uuid=True), nullable=False)
    terms = Column(JSON, nullable=True)
    accepted = Column(Boolean, nullable=True)
    counter_offer_id = Column(PGUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    negotiation = relationship("Negotiation", backref="offers")


class DiplomaticEvent(Base):
    """SQLAlchemy model for diplomatic events."""
    
    __tablename__ = "diplomatic_events"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type = Column(SQLEnum(DiplomaticEventType), nullable=False)
    factions = Column(ARRAY(String), nullable=False)  # Array of faction UUIDs as strings
    description = Column(Text, nullable=False)
    severity = Column(Integer, nullable=False, default=0)
    public = Column(Boolean, nullable=False, default=True)
    related_treaty_id = Column(PGUUID(as_uuid=True), nullable=True)
    related_negotiation_id = Column(PGUUID(as_uuid=True), nullable=True)
    meta_data = Column(JSON, nullable=True)
    tension_change = Column(JSON, nullable=True)  # Dict mapping faction pairs to tension changes
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TreatyViolation(Base):
    """SQLAlchemy model for treaty violations."""
    
    __tablename__ = "treaty_violations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    treaty_id = Column(PGUUID(as_uuid=True), ForeignKey("treaties.id"), nullable=False)
    violator_id = Column(PGUUID(as_uuid=True), nullable=False)
    violation_type = Column(SQLEnum(TreatyViolationType), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=True)
    reported_by = Column(PGUUID(as_uuid=True), nullable=False)
    severity = Column(Integer, nullable=False, default=50)
    acknowledged = Column(Boolean, nullable=False, default=False)
    resolved = Column(Boolean, nullable=False, default=False)
    resolution_details = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    treaty = relationship("Treaty", backref="violations")


class DiplomaticIncident(Base):
    """SQLAlchemy model for diplomatic incidents."""
    
    __tablename__ = "diplomatic_incidents"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    incident_type = Column(SQLEnum(DiplomaticIncidentType), nullable=False)
    perpetrator_id = Column(PGUUID(as_uuid=True), nullable=False)
    victim_id = Column(PGUUID(as_uuid=True), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=True)
    severity = Column(SQLEnum(DiplomaticIncidentSeverity), nullable=False, default=DiplomaticIncidentSeverity.MODERATE)
    tension_impact = Column(Integer, nullable=False, default=20)
    public = Column(Boolean, nullable=False, default=True)
    witnessed_by = Column(ARRAY(String), nullable=True)  # Array of faction UUIDs as strings
    related_event_id = Column(PGUUID(as_uuid=True), nullable=True)
    related_treaty_id = Column(PGUUID(as_uuid=True), nullable=True)
    resolved = Column(Boolean, nullable=False, default=False)
    resolution_details = Column(Text, nullable=True)
    resolution_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Ultimatum(Base):
    """SQLAlchemy model for ultimatums."""
    
    __tablename__ = "ultimatums"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    issuer_id = Column(PGUUID(as_uuid=True), nullable=False)
    recipient_id = Column(PGUUID(as_uuid=True), nullable=False)
    demands = Column(JSON, nullable=True)
    consequences = Column(JSON, nullable=True)
    status = Column(SQLEnum(UltimatumStatus), nullable=False, default=UltimatumStatus.PENDING)
    deadline = Column(DateTime, nullable=False)
    response_date = Column(DateTime, nullable=True)
    justification = Column(Text, nullable=False)
    public = Column(Boolean, nullable=False, default=True)
    witnessed_by = Column(ARRAY(String), nullable=True)  # Array of faction UUIDs as strings
    related_incident_id = Column(PGUUID(as_uuid=True), nullable=True)
    related_treaty_id = Column(PGUUID(as_uuid=True), nullable=True)
    related_event_id = Column(PGUUID(as_uuid=True), nullable=True)
    tension_change_on_issue = Column(Integer, nullable=False, default=20)
    tension_change_on_accept = Column(Integer, nullable=False, default=-10)
    tension_change_on_reject = Column(Integer, nullable=False, default=40)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Sanction(Base):
    """SQLAlchemy model for sanctions."""
    
    __tablename__ = "sanctions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    imposer_id = Column(PGUUID(as_uuid=True), nullable=False)
    target_id = Column(PGUUID(as_uuid=True), nullable=False)
    sanction_type = Column(SQLEnum(SanctionType), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(SanctionStatus), nullable=False, default=SanctionStatus.ACTIVE)
    justification = Column(Text, nullable=False)
    imposed_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    lifted_date = Column(DateTime, nullable=True)
    conditions_for_lifting = Column(JSON, nullable=True)
    severity = Column(Integer, nullable=False, default=50)
    economic_impact = Column(Integer, nullable=False, default=50)
    diplomatic_impact = Column(Integer, nullable=False, default=50)
    enforcement_measures = Column(JSON, nullable=True)
    supporting_factions = Column(ARRAY(String), nullable=True)  # Array of faction UUIDs as strings
    opposing_factions = Column(ARRAY(String), nullable=True)  # Array of faction UUIDs as strings
    violations = Column(JSON, nullable=True)  # Array of violation records
    is_public = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow) 