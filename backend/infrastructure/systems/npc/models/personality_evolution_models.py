"""
Dynamic Personality Evolution Models

Tracks how NPC personalities change over time based on experiences,
allowing for organic character development and LLM-driven attribute changes.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.orm import relationship
from backend.infrastructure.database import UUIDMixin
from enum import Enum
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import UUID


class PersonalityChangeType(Enum):
    """Types of personality changes"""
    GRADUAL_SHIFT = "gradual_shift"
    TRAUMATIC_CHANGE = "traumatic_change"  
    LIFE_STAGE_EVOLUTION = "life_stage_evolution"
    RELATIONSHIP_INFLUENCE = "relationship_influence"
    CULTURAL_ADAPTATION = "cultural_adaptation"
    PROFESSIONAL_DEVELOPMENT = "professional_development"
    CRISIS_RESPONSE = "crisis_response"
    SUCCESS_ADAPTATION = "success_adaptation"


class NpcPersonalityEvolution(UUIDMixin):
    """Tracks personality changes over time"""
    
    __tablename__ = "npc_personality_evolution"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    
    # Change tracking
    change_type = Column(SQLEnum(PersonalityChangeType), nullable=False)
    change_description = Column(Text, nullable=False)
    change_magnitude = Column(Float, default=1.0)  # 0.1-5.0, how significant the change
    
    # Personality attributes affected (before/after values)
    attributes_changed = Column(JSONB, default=dict)  # {"hidden_resilience": {"from": 5, "to": 7}}
    trigger_event_id = Column(String(100))  # Reference to the event that caused change
    trigger_event_type = Column(String(50))  # "goal_completion", "relationship_change", etc.
    
    # Change context
    life_stage_at_change = Column(String(50))
    age_at_change = Column(Integer)
    social_context = Column(Text)  # Who/what influenced the change
    
    # Change mechanics
    change_probability = Column(Float, default=0.1)  # Calculated probability this change would occur
    change_resistance = Column(Float, default=5.0)   # How much the NPC resisted this change
    adaptation_period_days = Column(Integer, default=30)  # How long to fully adapt
    
    # Status
    is_complete = Column(Boolean, default=False)
    progress_percentage = Column(Float, default=0.0)  # 0-100, how much change has occurred
    
    # Metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    last_progression = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    npc = relationship("NpcEntity", backref="personality_changes")
    
    def calculate_daily_progression(self, base_rate: float = 0.05) -> float:
        """Calculate how much personality change should progress today"""
        if self.is_complete:
            return 0.0
        
        # Faster progression for smaller changes, slower for major changes
        magnitude_factor = 1.0 / max(0.5, self.change_magnitude)
        resistance_factor = 1.0 / max(0.5, self.change_resistance / 5.0)
        
        daily_rate = base_rate * magnitude_factor * resistance_factor
        return min(daily_rate * 100, 100 - self.progress_percentage)
    
    def get_current_attribute_values(self) -> Dict[str, float]:
        """Get the current interpolated values of changing attributes"""
        if self.is_complete:
            return {attr: changes["to"] for attr, changes in self.attributes_changed.items()}
        
        # Interpolate between from/to based on progress
        progress_ratio = self.progress_percentage / 100.0
        current_values = {}
        
        for attr, changes in self.attributes_changed.items():
            from_val = changes["from"]
            to_val = changes["to"]
            current_val = from_val + (to_val - from_val) * progress_ratio
            current_values[attr] = current_val
        
        return current_values


class NpcPersonalitySnapshot(UUIDMixin):
    """Periodic snapshots of NPC personality for tracking evolution"""
    
    __tablename__ = "npc_personality_snapshots"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    
    # Snapshot data
    snapshot_date = Column(DateTime, default=datetime.utcnow)
    npc_age_at_snapshot = Column(Integer)
    life_stage_at_snapshot = Column(String(50))
    
    # All personality attributes at this point in time
    personality_attributes = Column(JSONB, default=dict)  # All hidden_ attributes
    emotional_baseline = Column(String(50))  # Baseline emotional state
    
    # Context at time of snapshot
    major_goals = Column(JSONB, default=list)  # Active goals at this time
    key_relationships = Column(JSONB, default=list)  # Important relationships
    life_events_summary = Column(Text)  # Brief summary of recent events
    
    # Snapshot metadata
    snapshot_type = Column(String(50), default="periodic")  # "periodic", "milestone", "crisis"
    triggered_by = Column(String(100))  # What caused this snapshot
    
    # Relationships
    npc = relationship("NpcEntity", backref="personality_snapshots")


class NpcMemoryEvolution(UUIDMixin):
    """Enhanced memory system that learns and adapts"""
    
    __tablename__ = "npc_memory_evolution"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    
    # Memory details
    memory_category = Column(String(50), nullable=False)  # "interaction", "lesson", "pattern", "preference"
    memory_content = Column(Text, nullable=False)
    memory_importance = Column(Float, default=5.0)  # 1-10
    
    # Learning aspects
    learned_from_entity_id = Column(String(100))  # Who/what they learned from
    learned_from_entity_type = Column(String(50))  # "npc", "player", "event", "experience"
    learning_context = Column(Text)  # Situation where learning occurred
    
    # Memory strength and recall
    recall_count = Column(Integer, default=0)
    last_recalled = Column(DateTime)
    memory_strength = Column(Float, default=10.0)  # Starts strong, fades over time
    
    # Behavioral impact
    behavior_modifications = Column(JSONB, default=dict)  # How this memory changes behavior
    decision_weight = Column(Float, default=1.0)  # How much this influences decisions
    
    # Pattern recognition
    similar_situations_count = Column(Integer, default=0)  # How many similar situations encountered
    pattern_confidence = Column(Float, default=0.0)  # Confidence in recognizing this pattern
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_reinforced = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    npc = relationship("NpcEntity", backref="learned_memories")
    
    def reinforce_memory(self, reinforcement_strength: float = 1.0):
        """Strengthen this memory through repetition or recall"""
        self.recall_count += 1
        self.last_recalled = datetime.utcnow()
        self.last_reinforced = datetime.utcnow()
        
        # Strengthen memory but with diminishing returns
        max_strength = 10.0
        current_ratio = self.memory_strength / max_strength
        reinforcement_effect = reinforcement_strength * (1.0 - current_ratio) * 0.5
        
        self.memory_strength = min(max_strength, self.memory_strength + reinforcement_effect)
    
    def fade_memory(self, days_passed: int, base_fade_rate: float = 0.02):
        """Fade memory over time"""
        # Important memories fade slower
        importance_factor = self.memory_importance / 10.0
        fade_resistance = importance_factor * 0.5
        
        actual_fade_rate = base_fade_rate * (1.0 - fade_resistance)
        fade_amount = days_passed * actual_fade_rate
        
        self.memory_strength = max(0.0, self.memory_strength - fade_amount)


class NpcCrisisResponse(UUIDMixin):
    """Tracks how NPCs respond to crises and disasters"""
    
    __tablename__ = "npc_crisis_responses"
    __table_args__ = {'extend_existing': True}
    
    npc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("npc_entities.id"), nullable=False, index=True)
    
    # Crisis details
    crisis_type = Column(String(50), nullable=False)  # "war", "plague", "famine", "economic_collapse", "natural_disaster"
    crisis_description = Column(Text, nullable=False)
    crisis_severity = Column(Float, default=5.0)  # 1-10
    crisis_duration_days = Column(Integer, default=30)
    
    # NPC's response
    response_type = Column(String(50), nullable=False)  # "flee", "fight", "hide", "adapt", "help_others", "exploit"
    response_description = Column(Text)
    response_effectiveness = Column(Float, default=5.0)  # How well their response worked
    
    # Personality factors that influenced response
    key_personality_factors = Column(JSONB, default=list)  # Which hidden attributes mattered most
    emotional_state_during = Column(String(50))  # Emotional state during crisis
    
    # Outcomes and learning
    personal_losses = Column(JSONB, default=list)  # What they lost
    personal_gains = Column(JSONB, default=list)   # What they gained
    lessons_learned = Column(Text)  # What they learned from this experience
    
    # Long-term impact
    personality_changes_triggered = Column(JSONB, default=list)  # Which attributes changed
    new_goals_formed = Column(JSONB, default=list)  # Goals created from this experience
    relationship_changes = Column(JSONB, default=dict)  # How relationships changed
    
    # Status
    crisis_start_date = Column(DateTime, nullable=False)
    crisis_end_date = Column(DateTime)
    response_completed = Column(Boolean, default=False)
    recovery_completed = Column(Boolean, default=False)
    
    # Relationships
    npc = relationship("NpcEntity", backref="crisis_responses") 