"""SQLAlchemy models for cloud cost monitoring system."""

from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CloudProvider(Base):
    """Cloud service provider (AWS, GCP, Azure)."""
    __tablename__ = 'cloud_providers'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    api_credentials = Column(JSON, nullable=False)  # Encrypted credentials
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cost_entries = relationship("CostEntry", back_populates="provider")
    resources = relationship("CloudResource", back_populates="provider")

class CostEntry(Base):
    """Individual cost entry from a cloud provider."""
    __tablename__ = 'cost_entries'

    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey('cloud_providers.id'), nullable=False)
    service_name = Column(String(100), nullable=False)
    resource_id = Column(String(200))
    cost_amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)  # ISO currency code
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    tags = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    provider = relationship("CloudProvider", back_populates="cost_entries")

class CloudResource(Base):
    """Cloud resource (e.g., VM, database, storage bucket)."""
    __tablename__ = 'cloud_resources'

    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey('cloud_providers.id'), nullable=False)
    resource_id = Column(String(200), nullable=False)
    resource_type = Column(String(100), nullable=False)
    name = Column(String(200))
    region = Column(String(50))
    tags = Column(JSON, default={})
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    provider = relationship("CloudProvider", back_populates="resources")
    cleanup_entries = relationship("CleanupEntry", back_populates="resource")

class Budget(Base):
    """Cost budget for a specific scope."""
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)  # ISO currency code
    period = Column(Enum('monthly', 'quarterly', 'yearly', name='budget_period'), nullable=False)
    scope_type = Column(Enum('project', 'team', 'service', name='budget_scope'), nullable=False)
    scope_id = Column(String(100), nullable=False)
    alert_thresholds = Column(JSON, default=[80.0, 90.0, 100.0])  # Percentage thresholds
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    alerts = relationship("BudgetAlert", back_populates="budget")

class BudgetAlert(Base):
    """Alert generated when budget threshold is exceeded."""
    __tablename__ = 'budget_alerts'

    id = Column(Integer, primary_key=True)
    budget_id = Column(Integer, ForeignKey('budgets.id'), nullable=False)
    threshold = Column(Float, nullable=False)  # Percentage threshold that triggered alert
    current_usage = Column(Float, nullable=False)
    percentage_used = Column(Float, nullable=False)
    alert_time = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(100))

    # Relationships
    budget = relationship("Budget", back_populates="alerts")

class CleanupEntry(Base):
    """Resource cleanup recommendation and tracking."""
    __tablename__ = 'cleanup_entries'

    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('cloud_resources.id'), nullable=False)
    reason = Column(String(500), nullable=False)
    estimated_savings = Column(Float)  # Estimated monthly cost savings
    status = Column(
        Enum('identified', 'notified', 'approved', 'cleaned', 'failed', 'exempted',
             name='cleanup_status'),
        nullable=False,
        default='identified'
    )
    identified_at = Column(DateTime, default=datetime.utcnow)
    notified_at = Column(DateTime)
    approved_at = Column(DateTime)
    approved_by = Column(String(100))
    cleaned_at = Column(DateTime)
    exemption_reason = Column(String(500))

    # Relationships
    resource = relationship("CloudResource", back_populates="cleanup_entries")

class CleanupRule(Base):
    """Cleanup rule for identifying resources to clean up."""
    __tablename__ = 'cleanup_rules'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    provider_id = Column(Integer, ForeignKey('cloud_providers.id'), nullable=False)
    resource_type = Column(String(100), nullable=False)
    conditions = Column(JSON, nullable=False)
    action = Column(String(50), nullable=False)  # e.g., 'notify', 'stop', 'terminate'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    provider = relationship("CloudProvider") 