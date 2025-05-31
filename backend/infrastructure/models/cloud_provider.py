"""Cloud provider model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from backend.infrastructure.shared.database import Base

class CloudProvider(Base):
    __tablename__ = 'cloud_providers'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cleanup_entries = relationship("CleanupEntry", back_populates="provider")
    cleanup_rules = relationship("CleanupRule", back_populates="provider") 