"""
Shared database base components for business logic systems.

This module provides the base database classes and utilities that business logic
systems need.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

# Create the base class for all models
Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields for all tables."""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Provide aliases for compatibility
UUIDMixin = BaseModel
TimestampMixin = BaseModel
GUID = UUID

__all__ = [
    'Base', 
    'BaseModel', 
    'UUIDMixin', 
    'TimestampMixin', 
    'GUID'
] 