"""
Emotional State Models for NPCs

Tracks NPC emotional states, mood patterns, and emotional influences on behavior.
Integrates with autonomous lifecycle and decision-making systems.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.orm import relationship
from backend.infrastructure.database import UUIDMixin
from enum import Enum
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import UUID


class EmotionalState(Enum):
    """Core emotional states that affect NPC behavior"""
    JOYFUL = "joyful"
    CONTENT = "content"
    NEUTRAL = "neutral"
    MELANCHOLY = "melancholy"
    ANGRY = "angry"
    FEARFUL = "fearful"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"
    DEPRESSED = "depressed"
    HOPEFUL = "hopeful"
    BITTER = "bitter"
    LOVE_STRUCK = "love_struck"
    GRIEF_STRICKEN = "grief_stricken"
    DETERMINED = "determined"


class EmotionalTriggerType(Enum):
    """Types of events that can trigger emotional changes"""
    RELATIONSHIP_CHANGE = "relationship_change"
    GOAL_SUCCESS = "goal_success"
    GOAL_FAILURE = "goal_failure"
    ECONOMIC_CHANGE = "economic_change"
    POLITICAL_EVENT = "political_event"
    CULTURAL_EVENT = "cultural_event"
    PHYSICAL_DANGER = "physical_danger"
    SOCIAL_HUMILIATION = "social_humiliation"
    SOCIAL_TRIUMPH = "social_triumph"
    LOSS_OF_LOVED_ONE = "loss_of_loved_one"
    BETRAYAL = "betrayal"
    LOYALTY_REWARD = "loyalty_reward"
    LIFESTYLE_CHANGE = "lifestyle_change"
    SEASONAL_CHANGE = "seasonal_change"
    HEALTH_CHANGE = "health_change"


class NpcEmotionalState(UUIDMixin):
    """Current emotional state of an NPC"""
    
    __tablename__ = "npc_emotional_states"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    
    # Core emotional state
    current_emotion = Column(SQLEnum(EmotionalState), default=EmotionalState.NEUTRAL, nullable=False)
    emotion_intensity = Column(Float, default=5.0)  # 0-10 scale
    emotion_stability = Column(Float, default=5.0)  # How likely emotion is to change (0-10)
    
    # Emotional dimensions (each -10 to +10)
    happiness_level = Column(Float, default=0.0)    # Sad to Happy
    energy_level = Column(Float, default=0.0)       # Lethargic to Energetic
    stress_level = Column(Float, default=0.0)       # Calm to Stressed
    confidence_level = Column(Float, default=0.0)   # Insecure to Confident
    sociability_level = Column(Float, default=0.0)  # Withdrawn to Sociable
    optimism_level = Column(Float, default=0.0)     # Pessimistic to Optimistic
    
    # Emotional patterns
    dominant_emotions = Column(JSONB, default=list)  # List of emotions frequently experienced
    emotional_volatility = Column(Float, default=5.0)  # How quickly emotions change
    emotional_recovery_rate = Column(Float, default=5.0)  # How quickly they return to baseline
    
    # External influences
    weather_sensitivity = Column(Float, default=3.0)   # 0-10 how much weather affects mood
    social_sensitivity = Column(Float, default=5.0)    # 0-10 how much social events affect mood
    stress_tolerance = Column(Float, default=5.0)      # 0-10 resilience to stress
    
    # State tracking
    last_major_emotional_event = Column(DateTime)
    days_in_current_state = Column(Integer, default=0)
    baseline_emotion = Column(SQLEnum(EmotionalState), default=EmotionalState.NEUTRAL)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    emotional_history_summary = Column(Text)  # Brief summary of recent emotional patterns
    
    # Relationships
    npc = relationship("NpcEntity", backref="emotional_state")
    emotional_triggers = relationship("NpcEmotionalTrigger", back_populates="npc_state", cascade="all, delete-orphan")
    emotional_influences = relationship("NpcEmotionalInfluence", back_populates="npc_state", cascade="all, delete-orphan")
    
    def get_mood_description(self) -> str:
        """Get a human-readable description of the NPC's current mood"""
        intensity_desc = "slightly" if self.emotion_intensity < 3 else "moderately" if self.emotion_intensity < 7 else "intensely"
        
        mood_descriptors = {
            EmotionalState.JOYFUL: f"{intensity_desc} joyful and upbeat",
            EmotionalState.CONTENT: f"{intensity_desc} content and satisfied",
            EmotionalState.NEUTRAL: "in a balanced emotional state",
            EmotionalState.MELANCHOLY: f"{intensity_desc} melancholy and subdued",
            EmotionalState.ANGRY: f"{intensity_desc} angry and irritated",
            EmotionalState.FEARFUL: f"{intensity_desc} fearful and cautious",
            EmotionalState.EXCITED: f"{intensity_desc} excited and enthusiastic",
            EmotionalState.ANXIOUS: f"{intensity_desc} anxious and worried",
            EmotionalState.CONFIDENT: f"{intensity_desc} confident and assured",
            EmotionalState.DEPRESSED: f"{intensity_desc} depressed and dejected",
            EmotionalState.HOPEFUL: f"{intensity_desc} hopeful and optimistic",
            EmotionalState.BITTER: f"{intensity_desc} bitter and resentful",
            EmotionalState.LOVE_STRUCK: f"{intensity_desc} infatuated and romantic",
            EmotionalState.GRIEF_STRICKEN: f"{intensity_desc} grief-stricken and mournful",
            EmotionalState.DETERMINED: f"{intensity_desc} determined and focused"
        }
        
        return mood_descriptors.get(self.current_emotion, "in an undefined emotional state")
    
    def get_decision_modifiers(self) -> Dict[str, float]:
        """Get modifiers for decision-making based on emotional state"""
        modifiers = {
            "risk_taking": 0.0,
            "social_interaction": 0.0,
            "economic_decision": 0.0,
            "relationship_formation": 0.0,
            "goal_pursuit": 0.0,
            "aggression": 0.0,
            "cooperation": 0.0,
            "creativity": 0.0
        }
        
        # Base modifiers by emotion type
        emotion_effects = {
            EmotionalState.JOYFUL: {"risk_taking": 0.2, "social_interaction": 0.3, "cooperation": 0.2, "creativity": 0.2},
            EmotionalState.ANGRY: {"risk_taking": 0.3, "aggression": 0.4, "social_interaction": -0.2, "cooperation": -0.3},
            EmotionalState.FEARFUL: {"risk_taking": -0.4, "social_interaction": -0.3, "economic_decision": -0.2},
            EmotionalState.CONFIDENT: {"risk_taking": 0.2, "goal_pursuit": 0.3, "social_interaction": 0.2},
            EmotionalState.DEPRESSED: {"goal_pursuit": -0.3, "social_interaction": -0.4, "cooperation": -0.2},
            EmotionalState.EXCITED: {"risk_taking": 0.3, "creativity": 0.2, "goal_pursuit": 0.2},
            EmotionalState.ANXIOUS: {"risk_taking": -0.2, "economic_decision": -0.3, "social_interaction": -0.1},
            EmotionalState.DETERMINED: {"goal_pursuit": 0.4, "risk_taking": 0.1, "cooperation": 0.1},
            EmotionalState.BITTER: {"cooperation": -0.4, "social_interaction": -0.3, "aggression": 0.2},
            EmotionalState.HOPEFUL: {"goal_pursuit": 0.2, "cooperation": 0.2, "social_interaction": 0.1}
        }
        
        base_effects = emotion_effects.get(self.current_emotion, {})
        intensity_multiplier = self.emotion_intensity / 5.0  # Normalize to 0-2 range
        
        for modifier_type, base_effect in base_effects.items():
            modifiers[modifier_type] = base_effect * intensity_multiplier
        
        return modifiers


class NpcEmotionalTrigger(UUIDMixin):
    """Records of emotional triggers and their effects on NPCs"""
    
    __tablename__ = "npc_emotional_triggers"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    emotional_state_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_emotional_states.id"), nullable=False)
    
    trigger_type = Column(SQLEnum(EmotionalTriggerType), nullable=False)
    trigger_description = Column(Text, nullable=False)
    trigger_severity = Column(Float, default=5.0)  # 1-10 intensity of the trigger
    
    # Emotional impact
    previous_emotion = Column(SQLEnum(EmotionalState))
    resulting_emotion = Column(SQLEnum(EmotionalState), nullable=False)
    emotion_change_magnitude = Column(Float, default=0.0)  # How much emotion changed
    
    # Context
    related_entity_id = Column(String(100))  # ID of person/faction/object that caused trigger
    related_entity_type = Column(String(50))  # "npc", "faction", "event", etc.
    location = Column(String(255))
    
    # Persistence
    expected_duration_days = Column(Integer, default=1)
    actual_duration_days = Column(Integer)
    emotional_recovery_time = Column(Integer)  # Days to return to baseline
    
    # Metadata
    occurred_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    trigger_metadata = Column(JSONB, default=dict)
    
    # Relationships
    npc_state = relationship("NpcEmotionalState", back_populates="emotional_triggers")
    
    def is_resolved(self) -> bool:
        """Check if this emotional trigger has been resolved"""
        return self.resolved_at is not None
    
    def days_since_trigger(self) -> int:
        """Calculate days since this trigger occurred"""
        return (datetime.utcnow() - self.occurred_at).days


class NpcEmotionalInfluence(UUIDMixin):
    """Ongoing influences on NPC emotional state (relationships, conditions, etc.)"""
    
    __tablename__ = "npc_emotional_influences"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    emotional_state_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_emotional_states.id"), nullable=False)
    
    influence_type = Column(String(50), nullable=False)  # "relationship", "health", "weather", "economic"
    influence_source = Column(String(100), nullable=False)  # ID or name of source
    influence_description = Column(Text)
    
    # Influence effects
    happiness_modifier = Column(Float, default=0.0)
    energy_modifier = Column(Float, default=0.0)
    stress_modifier = Column(Float, default=0.0)
    confidence_modifier = Column(Float, default=0.0)
    sociability_modifier = Column(Float, default=0.0)
    optimism_modifier = Column(Float, default=0.0)
    
    # Influence properties
    influence_strength = Column(Float, default=1.0)  # 0-5 multiplier
    is_temporary = Column(Boolean, default=True)
    duration_days = Column(Integer)
    decay_rate = Column(Float, default=0.1)  # How quickly influence weakens
    
    # Status
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_applied = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    npc_state = relationship("NpcEmotionalState", back_populates="emotional_influences")
    
    def calculate_current_strength(self) -> float:
        """Calculate current influence strength accounting for decay"""
        if not self.is_active:
            return 0.0
        
        days_active = (datetime.utcnow() - self.started_at).days
        if self.is_temporary and days_active >= (self.duration_days or 7):
            return 0.0
        
        # Apply decay
        decay_factor = max(0.1, 1.0 - (days_active * self.decay_rate))
        return self.influence_strength * decay_factor
    
    def apply_to_emotional_dimensions(self, emotional_state: NpcEmotionalState) -> Dict[str, float]:
        """Apply this influence to emotional dimensions"""
        current_strength = self.calculate_current_strength()
        
        return {
            "happiness_level": self.happiness_modifier * current_strength,
            "energy_level": self.energy_modifier * current_strength,
            "stress_level": self.stress_modifier * current_strength,
            "confidence_level": self.confidence_modifier * current_strength,
            "sociability_level": self.sociability_modifier * current_strength,
            "optimism_level": self.optimism_modifier * current_strength
        }


class NpcEmotionalMemory(UUIDMixin):
    """Long-term emotional memories that affect personality and behavior"""
    
    __tablename__ = "npc_emotional_memories"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    
    memory_type = Column(String(50), nullable=False)  # "trauma", "joy", "betrayal", "triumph"
    memory_description = Column(Text, nullable=False)
    memory_intensity = Column(Float, default=5.0)  # 1-10, how emotionally significant
    
    # Associated emotions
    primary_emotion = Column(SQLEnum(EmotionalState), nullable=False)
    secondary_emotions = Column(JSONB, default=list)  # List of additional emotions
    
    # Memory context
    related_entities = Column(JSONB, default=list)  # NPCs, factions, places involved
    memory_location = Column(String(255))
    memory_tags = Column(JSONB, default=list)  # Tags for categorization
    
    # Memory strength and persistence
    memory_clarity = Column(Float, default=10.0)  # How clearly remembered (10 = perfect, 0 = forgotten)
    emotional_charge = Column(Float, default=5.0)  # How emotionally affecting (0-10)
    recall_frequency = Column(Integer, default=0)  # How often this memory is recalled
    
    # Behavioral impact
    triggers_on = Column(JSONB, default=list)  # Situations that bring up this memory
    behavioral_effects = Column(JSONB, default=dict)  # How this memory affects behavior
    
    # Metadata
    occurred_at = Column(DateTime, nullable=False)
    last_recalled = Column(DateTime)
    memory_metadata = Column(JSONB, default=dict)
    
    def fade_memory(self, days_passed: int, base_fade_rate: float = 0.01):
        """Fade memory clarity over time"""
        fade_amount = days_passed * base_fade_rate * (1.0 - self.emotional_charge / 10.0)
        self.memory_clarity = max(0.0, self.memory_clarity - fade_amount)
    
    def recall_memory(self):
        """Record that this memory was recalled"""
        self.recall_frequency += 1
        self.last_recalled = datetime.utcnow()
        
        # Recalling a memory slightly increases its clarity
        clarity_boost = min(1.0, self.emotional_charge / 10.0)
        self.memory_clarity = min(10.0, self.memory_clarity + clarity_boost) 