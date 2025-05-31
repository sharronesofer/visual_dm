"""Cleanup models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base

class CleanupEntry(Base):
    __tablename__ = 'cleanup_entries'

    id = Column(Integer, primary_key=True)
    resource_id = Column(String, nullable=False)
    provider_id = Column(Integer, ForeignKey('cloud_providers.id'), nullable=False)
    resource_type = Column(String, nullable=False)
    last_accessed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    estimated_cost = Column(Float, nullable=True)
    is_cleaned = Column(Boolean, default=False)
    cleaned_at = Column(DateTime, nullable=True)
    cleanup_reason = Column(String, nullable=True)
    
    # Relationships
    provider = relationship("CloudProvider", back_populates="cleanup_entries")
    rule = relationship("CleanupRule", back_populates="entries")
    rule_id = Column(Integer, ForeignKey('cleanup_rules.id'), nullable=True)

class CleanupRule(Base):
    __tablename__ = 'cleanup_rules'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    provider_id = Column(Integer, ForeignKey('cloud_providers.id'), nullable=False)
    idle_threshold_days = Column(Integer, nullable=False)
    cost_threshold = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship("CloudProvider", back_populates="cleanup_rules")
    entries = relationship("CleanupEntry", back_populates="rule") 