"""
Disease System Database Models

SQLAlchemy ORM models for the disease system database tables.
Uses string types for configuration values that are validated against JSON config.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates

Base = declarative_base()


class Disease(Base):
    """Disease table model"""
    __tablename__ = "diseases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    disease_type = Column(String(50), nullable=False, index=True)  # Validated against JSON config
    status = Column(String(20), nullable=False, default="active", index=True)
    
    # Disease characteristics
    mortality_rate = Column(Float, nullable=False, default=0.1)
    transmission_rate = Column(Float, nullable=False, default=0.3)
    incubation_days = Column(Integer, nullable=False, default=3)
    recovery_days = Column(Integer, nullable=False, default=7)
    immunity_duration_days = Column(Integer, nullable=False, default=365)
    
    # Environmental factors
    crowding_factor = Column(Float, nullable=False, default=1.5)
    hygiene_factor = Column(Float, nullable=False, default=1.3)
    healthcare_factor = Column(Float, nullable=False, default=0.7)
    
    # Population targeting
    targets_young = Column(Boolean, nullable=False, default=False)
    targets_old = Column(Boolean, nullable=False, default=False)
    targets_weak = Column(Boolean, nullable=False, default=False)
    
    # Additional properties stored as JSON
    properties = Column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    outbreaks = relationship("DiseaseOutbreak", back_populates="disease")

    @validates('mortality_rate', 'transmission_rate')
    def validate_rates(self, key, value):
        """Validate rate values are between 0 and 1"""
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"{key} must be between 0.0 and 1.0")
        return value

    @validates('incubation_days', 'recovery_days')
    def validate_days(self, key, value):
        """Validate day values are positive"""
        if value <= 0:
            raise ValueError(f"{key} must be positive")
        return value

    def __repr__(self):
        return f"<Disease(id={self.id}, name='{self.name}', type='{self.disease_type}')>"


class DiseaseOutbreak(Base):
    """Disease outbreak table model"""
    __tablename__ = "disease_outbreaks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    disease_id = Column(UUID(as_uuid=True), ForeignKey("diseases.id"), nullable=False)
    region_id = Column(UUID(as_uuid=True), index=True)  # Optional region reference
    population_id = Column(UUID(as_uuid=True), index=True)  # Optional population reference
    
    # Outbreak status
    stage = Column(String(20), nullable=False, default="emerging", index=True)  # Validated against JSON config
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Current statistics
    infected_count = Column(Integer, nullable=False, default=1)
    recovered_count = Column(Integer, nullable=False, default=0)
    deceased_count = Column(Integer, nullable=False, default=0)
    immune_count = Column(Integer, nullable=False, default=0)
    
    # Environmental modifiers
    environmental_factors = Column(JSON, nullable=False, default=dict)
    
    # Timestamps
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Additional properties stored as JSON
    properties = Column(JSON, nullable=False, default=dict)

    # Relationships
    disease = relationship("Disease", back_populates="outbreaks")
    impacts = relationship("DiseaseImpact", back_populates="outbreak")
    interventions = relationship("DiseaseIntervention", back_populates="outbreak")

    @validates('infected_count', 'recovered_count', 'deceased_count', 'immune_count')
    def validate_counts(self, key, value):
        """Validate count values are non-negative"""
        if value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value

    def __repr__(self):
        return f"<DiseaseOutbreak(id={self.id}, disease_id={self.disease_id}, stage='{self.stage}')>"


class DiseaseImpact(Base):
    """Disease impact tracking table model"""
    __tablename__ = "disease_impacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    outbreak_id = Column(UUID(as_uuid=True), ForeignKey("disease_outbreaks.id"), nullable=False)
    
    # Impact details
    impact_type = Column(String(50), nullable=False, index=True)  # economic, social, political
    impact_data = Column(JSON, nullable=False)
    severity_level = Column(Integer, nullable=False)  # 1-10 scale
    affected_systems = Column(JSON, nullable=False, default=list)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    outbreak = relationship("DiseaseOutbreak", back_populates="impacts")

    @validates('severity_level')
    def validate_severity(self, key, value):
        """Validate severity level is between 1 and 10"""
        if not (1 <= value <= 10):
            raise ValueError("severity_level must be between 1 and 10")
        return value

    def __repr__(self):
        return f"<DiseaseImpact(id={self.id}, outbreak_id={self.outbreak_id}, type='{self.impact_type}')>"


class DiseaseIntervention(Base):
    """Disease intervention tracking table model"""
    __tablename__ = "disease_interventions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    outbreak_id = Column(UUID(as_uuid=True), ForeignKey("disease_outbreaks.id"), nullable=False)
    
    # Intervention details
    intervention_type = Column(String(50), nullable=False, index=True)  # Validated against JSON config (treatment types)
    intervention_quality = Column(Float, nullable=False, default=0.5)  # 0.0-1.0
    effectiveness_score = Column(Float, nullable=False, default=0.0)  # 0.0-1.0
    cost_per_person = Column(Float, nullable=False, default=0.0)
    people_treated = Column(Integer, nullable=False, default=0)
    success_rate = Column(Float, nullable=False, default=0.0)  # 0.0-1.0
    
    # Timing
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    outbreak = relationship("DiseaseOutbreak", back_populates="interventions")

    @validates('intervention_quality', 'effectiveness_score', 'success_rate')
    def validate_rates(self, key, value):
        """Validate rate values are between 0 and 1"""
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"{key} must be between 0.0 and 1.0")
        return value

    @validates('people_treated')
    def validate_people_treated(self, key, value):
        """Validate people treated is non-negative"""
        if value < 0:
            raise ValueError("people_treated cannot be negative")
        return value

    @validates('cost_per_person')
    def validate_cost(self, key, value):
        """Validate cost is non-negative"""
        if value < 0:
            raise ValueError("cost_per_person cannot be negative")
        return value

    def __repr__(self):
        return f"<DiseaseIntervention(id={self.id}, outbreak_id={self.outbreak_id}, type='{self.intervention_type}')>"


# Index definitions for better query performance
from sqlalchemy import Index

# Create indexes for common query patterns
Index('idx_diseases_type_status', Disease.disease_type, Disease.status)
Index('idx_outbreaks_region_active', DiseaseOutbreak.region_id, DiseaseOutbreak.is_active)
Index('idx_outbreaks_stage_active', DiseaseOutbreak.stage, DiseaseOutbreak.is_active)
Index('idx_impacts_type_severity', DiseaseImpact.impact_type, DiseaseImpact.severity_level)
Index('idx_interventions_type_started', DiseaseIntervention.intervention_type, DiseaseIntervention.started_at) 