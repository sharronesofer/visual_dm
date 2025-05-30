"""
Faction goal models for the Visual DM system.

This module defines the models for faction goals, which are objectives that factions
pursue over time. Goals track progress and completion, and influence faction behavior.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.systems.faction.models.faction import Base


class FactionGoal(Base):
    """
    Represents a goal for a faction.
    
    Faction goals are long-term objectives that influence faction behavior,
    diplomacy, and resource allocation.
    """
    __tablename__ = 'faction_goals'
    
    id = Column(Integer, primary_key=True)
    faction_id = Column(Integer, ForeignKey('factions.id'), nullable=False)
    
    # Goal details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # conquest, economic, political, etc.
    priority = Column(Integer, default=1)  # 1-10, higher = more important
    
    # Progress tracking
    progress = Column(Float, default=0.0)  # 0-100%
    status = Column(String(50), default="active")  # active, completed, failed, abandoned
    
    # Success/completion criteria
    completion_criteria = Column(JSON, default=dict)
    
    # Rewards upon completion
    rewards = Column(JSON, default=dict)
    
    # Failure conditions
    failure_criteria = Column(JSON, default=dict)
    
    # Penalties upon failure
    penalties = Column(JSON, default=dict)
    
    # Dependencies on other goals
    dependencies = Column(JSON, default=list)  # List of other goal IDs
    
    # Targets (if any)
    targets = Column(JSON, default=dict)  # E.g., target faction ID, region ID, etc.
    
    # Task tracking
    steps = Column(JSON, default=list)  # List of steps to achieve the goal
    
    # Metadata and history
    metadata = Column(JSON, default=dict)
    history = Column(JSON, default=lambda: [])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    faction = relationship('Faction', backref='goals')
    
    def __repr__(self):
        return f"<FactionGoal(id={self.id}, faction_id={self.faction_id}, title='{self.title}', status='{self.status}', progress={self.progress})>"
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "faction_id": self.faction_id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "priority": self.priority,
            "progress": self.progress,
            "status": self.status,
            "completion_criteria": self.completion_criteria,
            "rewards": self.rewards,
            "failure_criteria": self.failure_criteria,
            "penalties": self.penalties,
            "dependencies": self.dependencies,
            "targets": self.targets,
            "steps": self.steps,
            "metadata": self.metadata,
            "history": self.history,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None
        } 