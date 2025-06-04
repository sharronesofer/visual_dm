"""
Authentication System Base Module

This module provides base classes and utilities for the authentication system.
"""

import uuid
from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin

from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Any, Dict

# Create declarative base for auth models

class AuthBaseModel(Base):
    """
    Base model for authentication-related entities.
    
    Provides common functionality for User, Role, Permission models.
    """
    __abstract__ = True
    
    # Primary key field
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    # Common timestamp fields
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(), 
        nullable=False
    )
    
    # Common status field
    is_active = Column(Boolean, default=True, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
    
    def update(self, **kwargs) -> None:
        """Update model attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        class_name = self.__class__.__name__
        if hasattr(self, 'id'):
            return f"<{class_name}(id={self.id})>"
        elif hasattr(self, 'name'):
            return f"<{class_name}(name={self.name})>"
        else:
            return f"<{class_name}()>"

__all__ = ["AuthBaseModel", "Base"] 