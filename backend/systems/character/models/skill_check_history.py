"""
Skill Check History Models
-------------------------
Database models for logging skill check history, progression tracking,
and analytics for the noncombat skills system.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

Base = declarative_base()

class SkillCheckHistory(Base):
    """
    Logs all skill checks made by characters for analytics and progression tracking.
    """
    __tablename__ = 'skill_check_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Campaign session
    
    # Basic skill check info
    skill_name = Column(String(50), nullable=False, index=True)
    dc = Column(Integer, nullable=True)
    base_roll = Column(JSON, nullable=False)  # Can be int or list for advantage
    skill_modifier = Column(Integer, nullable=False)
    final_modifiers = Column(Integer, nullable=False, default=0)
    total_roll = Column(Integer, nullable=False)
    
    # Results
    success = Column(Boolean, nullable=True)
    degree_of_success = Column(Integer, nullable=False, default=0)
    critical_success = Column(Boolean, nullable=False, default=False)
    critical_failure = Column(Boolean, nullable=False, default=False)
    advantage_type = Column(String(20), nullable=False, default='normal')
    
    # Context
    description = Column(Text, nullable=True)
    environmental_conditions = Column(JSON, nullable=True)  # List of condition strings
    character_level = Column(Integer, nullable=False)
    
    # Analytics data
    roll_duration_ms = Column(Integer, nullable=True)  # Time taken to make decision
    difficulty_category = Column(String(20), nullable=True)  # 'easy', 'medium', etc.
    skill_check_type = Column(String(20), nullable=False, default='standard')  # standard, opposed, group, etc.
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    character_progression = relationship("CharacterSkillProgression", back_populates="skill_checks")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_skill_char_date', 'character_id', 'skill_name', 'created_at'),
        Index('idx_session_skill', 'session_id', 'skill_name'),
        Index('idx_success_rate', 'skill_name', 'success', 'dc'),
    )

class CharacterSkillProgression(Base):
    """
    Tracks skill progression and improvement over time for characters.
    """
    __tablename__ = 'character_skill_progression'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    skill_name = Column(String(50), nullable=False, index=True)
    
    # Current skill state
    current_level = Column(Integer, nullable=False)
    is_proficient = Column(Boolean, nullable=False, default=False)
    has_expertise = Column(Boolean, nullable=False, default=False)
    skill_bonus = Column(Integer, nullable=False, default=0)
    
    # Progression tracking
    total_checks = Column(Integer, nullable=False, default=0)
    successful_checks = Column(Integer, nullable=False, default=0)
    critical_successes = Column(Integer, nullable=False, default=0)
    critical_failures = Column(Integer, nullable=False, default=0)
    
    # Difficulty statistics
    avg_dc_attempted = Column(Float, nullable=True)
    highest_dc_success = Column(Integer, nullable=True)
    success_rate_by_dc = Column(JSON, nullable=True)  # Dict[str, float] - dc_range: success_rate
    
    # Recent performance (last 20 checks)
    recent_success_rate = Column(Float, nullable=True)
    recent_avg_roll = Column(Float, nullable=True)
    improvement_trend = Column(String(20), nullable=True)  # 'improving', 'stable', 'declining'
    
    # Milestone tracking
    first_check_date = Column(DateTime, nullable=True)
    last_check_date = Column(DateTime, nullable=True, index=True)
    milestones_achieved = Column(JSON, nullable=True)  # List of milestone names
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skill_checks = relationship("SkillCheckHistory", back_populates="character_progression")
    
    # Constraints
    __table_args__ = (
        Index('idx_char_skill_unique', 'character_id', 'skill_name', unique=True),
        Index('idx_skill_progression', 'skill_name', 'recent_success_rate', 'total_checks'),
    )

class SocialRelationship(Base):
    """
    Tracks social relationships between characters and NPCs.
    Persists attitude changes from social interactions.
    """
    __tablename__ = 'social_relationships'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    npc_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Relationship state
    current_attitude = Column(Integer, nullable=False, default=0)  # -100 to +100
    relationship_type = Column(String(30), nullable=True)  # 'stranger', 'acquaintance', 'friend', etc.
    trust_level = Column(Integer, nullable=False, default=0)  # 0-100
    reputation_modifier = Column(Integer, nullable=False, default=0)
    
    # Interaction history summary
    total_interactions = Column(Integer, nullable=False, default=0)
    successful_persuasions = Column(Integer, nullable=False, default=0)
    failed_deceptions = Column(Integer, nullable=False, default=0)
    intimidation_attempts = Column(Integer, nullable=False, default=0)
    
    # Important events
    major_events = Column(JSON, nullable=True)  # List of significant interaction outcomes
    last_interaction_type = Column(String(30), nullable=True)
    last_interaction_outcome = Column(String(20), nullable=True)  # 'success', 'failure', 'critical_success', etc.
    
    # Context
    first_meeting_location = Column(String(100), nullable=True)
    relationship_notes = Column(Text, nullable=True)
    
    # Timestamps
    first_met = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_interaction = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        Index('idx_char_npc_unique', 'character_id', 'npc_id', unique=True),
        Index('idx_attitude_tracking', 'character_id', 'current_attitude', 'last_interaction'),
    )

class SkillCheckSession(Base):
    """
    Groups skill checks into gameplay sessions for analytics.
    """
    __tablename__ = 'skill_check_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    dm_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Session info
    session_name = Column(String(100), nullable=True)
    session_type = Column(String(30), nullable=True)  # 'exploration', 'social', 'investigation', etc.
    location = Column(String(100), nullable=True)
    
    # Session statistics
    total_skill_checks = Column(Integer, nullable=False, default=0)
    unique_skills_used = Column(JSON, nullable=True)  # List of skill names
    average_dc = Column(Float, nullable=True)
    overall_success_rate = Column(Float, nullable=True)
    
    # Environmental factors
    dominant_conditions = Column(JSON, nullable=True)  # Most common environmental conditions
    difficulty_distribution = Column(JSON, nullable=True)  # Count by difficulty level
    
    # Timestamps
    session_start = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    session_end = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class SkillSynergy(Base):
    """
    Tracks skill synergy usage and effectiveness.
    """
    __tablename__ = 'skill_synergies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Synergy info
    primary_skill = Column(String(50), nullable=False, index=True)
    synergy_skills = Column(JSON, nullable=False)  # List of skills that provided synergy
    synergy_bonus = Column(Integer, nullable=False)
    
    # Context
    skill_check_id = Column(UUID(as_uuid=True), ForeignKey('skill_check_history.id'), nullable=False)
    was_beneficial = Column(Boolean, nullable=False)  # Did the synergy help achieve success?
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    skill_check = relationship("SkillCheckHistory")
    
    # Constraints
    __table_args__ = (
        Index('idx_synergy_analysis', 'primary_skill', 'was_beneficial', 'synergy_bonus'),
    )

class EnvironmentalImpact(Base):
    """
    Tracks how environmental conditions affect skill check outcomes.
    """
    __tablename__ = 'environmental_impacts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_check_id = Column(UUID(as_uuid=True), ForeignKey('skill_check_history.id'), nullable=False)
    
    # Environmental data
    condition_name = Column(String(50), nullable=False, index=True)
    modifier_value = Column(Integer, nullable=False)
    condition_category = Column(String(30), nullable=False)  # 'lighting', 'weather', 'terrain', etc.
    
    # Impact analysis
    would_have_succeeded_without = Column(Boolean, nullable=True)  # If condition was neutral
    would_have_failed_without = Column(Boolean, nullable=True)
    impact_significance = Column(String(20), nullable=True)  # 'critical', 'major', 'minor', 'none'
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    skill_check = relationship("SkillCheckHistory")
    
    # Constraints
    __table_args__ = (
        Index('idx_environmental_analysis', 'condition_name', 'impact_significance', 'modifier_value'),
    )

# Analytics Views (these would be created as database views)
class SkillCheckAnalytics:
    """
    Helper class for analytics queries.
    This provides methods for common analytics operations.
    """
    
    @staticmethod
    def get_character_skill_summary(character_id: str, skill_name: str = None) -> Dict[str, Any]:
        """Get skill usage summary for a character."""
        # This would contain complex queries for analytics
        pass
    
    @staticmethod
    def get_session_analytics(session_id: str) -> Dict[str, Any]:
        """Get analytics for a specific session."""
        pass
    
    @staticmethod
    def get_environmental_impact_report(conditions: List[str]) -> Dict[str, Any]:
        """Analyze impact of specific environmental conditions."""
        pass
    
    @staticmethod
    def get_skill_synergy_effectiveness() -> Dict[str, Any]:
        """Analyze which skill synergies are most effective."""
        pass

# Database setup utilities
def create_indexes():
    """Create additional indexes for performance."""
    # This would contain SQL for creating performance indexes
    pass

def create_analytics_views():
    """Create database views for common analytics queries."""
    # This would contain SQL for creating analytics views
    pass 