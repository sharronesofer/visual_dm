"""
Character system - Mood models.

This module provides mood and emotional state models for characters,
supporting dynamic mood tracking and emotional responses.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.infrastructure.database import Base
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List
from uuid import UUID


class EmotionalState(Enum):
    """Enumeration of emotional states."""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    DISGUSTED = "disgusted"
    EXCITED = "excited"
    CALM = "calm"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"
    CONFUSED = "confused"
    CONTENT = "content"


class MoodIntensity(Enum):
    """Enumeration of mood intensity levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class CharacterMood(Base):
    """
    Character mood model representing current emotional state.
    
    Tracks the overall emotional state of a character including
    base mood, current modifiers, and mood history.
    """
    
    __tablename__ = 'character_moods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(String(255), nullable=False, index=True)
    base_emotional_state = Column(SQLEnum(EmotionalState), nullable=False, default=EmotionalState.CONTENT)
    base_intensity = Column(SQLEnum(MoodIntensity), nullable=False, default=MoodIntensity.MODERATE)
    current_emotional_state = Column(SQLEnum(EmotionalState), nullable=False, default=EmotionalState.CONTENT)
    current_intensity = Column(SQLEnum(MoodIntensity), nullable=False, default=MoodIntensity.MODERATE)
    stability = Column(Float, default=0.5)  # 0.0 = very unstable, 1.0 = very stable
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to mood modifiers
    modifiers = relationship("MoodModifier", back_populates="mood", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CharacterMood {self.character_id}: {self.current_emotional_state.value} ({self.current_intensity.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert mood to dictionary representation."""
        return {
            "id": self.id,
            "character_id": self.character_id,
            "base_emotional_state": self.base_emotional_state.value if self.base_emotional_state else None,
            "base_intensity": self.base_intensity.value if self.base_intensity else None,
            "current_emotional_state": self.current_emotional_state.value if self.current_emotional_state else None,
            "current_intensity": self.current_intensity.value if self.current_intensity else None,
            "stability": self.stability,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "modifiers": [modifier.to_dict() for modifier in self.modifiers] if self.modifiers else []
        }
    
    def apply_modifier(self, modifier: "MoodModifier") -> None:
        """Apply a mood modifier to update current emotional state."""
        # Simple mood modification logic - can be enhanced
        intensity_values = {
            MoodIntensity.VERY_LOW: 1,
            MoodIntensity.LOW: 2,
            MoodIntensity.MODERATE: 3,
            MoodIntensity.HIGH: 4,
            MoodIntensity.VERY_HIGH: 5
        }
        
        current_intensity_value = intensity_values.get(self.current_intensity, 3)
        modifier_intensity_value = intensity_values.get(modifier.intensity, 3)
        
        # Adjust intensity based on modifier
        if modifier.emotional_state != self.current_emotional_state:
            # Different emotion - blend or override based on intensity
            if modifier_intensity_value > current_intensity_value:
                self.current_emotional_state = modifier.emotional_state
                self.current_intensity = modifier.intensity
        else:
            # Same emotion - increase intensity
            new_intensity_value = min(5, current_intensity_value + 1)
            for intensity, value in intensity_values.items():
                if value == new_intensity_value:
                    self.current_intensity = intensity
                    break
        
        self.updated_at = datetime.utcnow()
    
    def decay_mood(self, hours_passed: float = 1.0) -> None:
        """Apply natural mood decay over time."""
        # Simple decay logic - mood gradually returns to base state
        if self.current_emotional_state != self.base_emotional_state:
            decay_rate = (1.0 - self.stability) * hours_passed * 0.1
            
            if decay_rate > 0.5:  # Significant decay
                self.current_emotional_state = self.base_emotional_state
                self.current_intensity = self.base_intensity
                self.updated_at = datetime.utcnow()


class MoodModifier(Base):
    """
    Mood modifier representing temporary emotional influences.
    
    Represents events, conditions, or circumstances that temporarily
    affect a character's emotional state.
    """
    
    __tablename__ = 'mood_modifiers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mood_id = Column(Integer, ForeignKey('character_moods.id'), nullable=False)
    emotional_state = Column(SQLEnum(EmotionalState), nullable=False)
    intensity = Column(SQLEnum(MoodIntensity), nullable=False, default=MoodIntensity.MODERATE)
    reason = Column(String(500), nullable=False)
    duration_hours = Column(Float, nullable=True)  # None = permanent until removed
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(String(10), default="true")  # Using string for compatibility
    
    # Relationship back to mood
    mood = relationship("CharacterMood", back_populates="modifiers")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.duration_hours and not self.expires_at:
            self.expires_at = self.applied_at + timedelta(hours=self.duration_hours)
    
    def __repr__(self):
        return f"<MoodModifier {self.emotional_state.value} ({self.intensity.value}): {self.reason}>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert modifier to dictionary representation."""
        return {
            "id": self.id,
            "mood_id": self.mood_id,
            "emotional_state": self.emotional_state.value if self.emotional_state else None,
            "intensity": self.intensity.value if self.intensity else None,
            "reason": self.reason,
            "duration_hours": self.duration_hours,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active
        }
    
    def is_expired(self) -> bool:
        """Check if the modifier has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def deactivate(self) -> None:
        """Deactivate the modifier."""
        self.is_active = "false"
