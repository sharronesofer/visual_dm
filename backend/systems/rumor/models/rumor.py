"""
Rumor system models.

This module contains the core data models for the rumor system.
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, field_validator, ConfigDict

class RumorCategory(str, Enum):
    """Categories for rumor classification."""
    POLITICAL = "political"
    PERSONAL = "personal"
    SOCIAL = "social"
    MILITARY = "military"
    ECONOMIC = "economic"
    RELIGIOUS = "religious"
    HISTORICAL = "historical"
    GOSSIP = "gossip"
    OTHER = "other"

class RumorSeverity(str, Enum):
    """Severity levels for rumors."""
    TRIVIAL = "trivial"  # Minor gossip
    MINOR = "minor"      # Interesting but not consequential
    MODERATE = "moderate"  # Could affect reputation
    MAJOR = "major"      # Could affect relationships/alliances
    CRITICAL = "critical"  # Could trigger major events

class RumorVariant(BaseModel):
    """
    Represents a specific variant/mutation of a rumor.
    
    Rumors can mutate as they spread, with each variant potentially
    diverging from the original content.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    parent_variant_id: Optional[str] = None  # ID of variant this mutated from
    entity_id: str  # ID of entity that created this variant
    mutation_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __str__(self) -> str:
        """String representation of the variant."""
        return f"Variant({self.id[:8]}): {self.content[:50]}..."

class RumorSpread(BaseModel):
    """
    Tracks the spread of a rumor to an entity, including
    which variant they heard and how much they believe it.
    """
    entity_id: str
    variant_id: str
    heard_from_entity_id: Optional[str] = None
    believability: float = 0.5  # 0.0 (totally disbelieve) to 1.0 (fully believe)
    heard_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class Rumor(BaseModel):
    """
    Represents a rumor that can spread between entities.
    
    Rumors track their variants (mutations), spread patterns,
    and maintain a truth value separate from believability.
    
    Example:
        rumor = Rumor(
            originator_id="npc_123",
            original_content="The king has fallen ill",
            categories=[RumorCategory.POLITICAL],
            severity=RumorSeverity.MAJOR,
            truth_value=0.8
        )
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    originator_id: str
    original_content: str
    categories: List[RumorCategory] = [RumorCategory.OTHER]
    severity: RumorSeverity = RumorSeverity.MINOR
    truth_value: float = 0.5  # 0.0 (totally false) to 1.0 (totally true)
    
    # Tracking spread and mutations
    variants: List[RumorVariant] = Field(default_factory=list)
    spread: List[RumorSpread] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
        
    @field_validator('truth_value')
    @classmethod
    def validate_truth_value(cls, v):
        """Ensure truth value is between 0 and 1."""
        return max(0.0, min(1.0, v))
        
    def __str__(self) -> str:
        """String representation of the rumor."""
        short_id = self.id[:8] if self.id else "unknown"
        return f"Rumor({short_id}): {self.original_content[:50]}..."
        
    def get_latest_variant_id_for_entity(self, entity_id: str) -> Optional[str]:
        """Get the most recent variant ID heard by an entity."""
        # Filter spread records for this entity
        entity_spread = [s for s in self.spread if s.entity_id == entity_id]
        
        if not entity_spread:
            return None
            
        # Get the most recent spread
        latest_spread = max(entity_spread, key=lambda s: s.heard_at)
        return latest_spread.variant_id
        
    def get_variant_by_id(self, variant_id: str) -> Optional[RumorVariant]:
        """Get a specific variant by ID."""
        for variant in self.variants:
            if variant.id == variant_id:
                return variant
        return None
        
    def get_current_content_for_entity(self, entity_id: str) -> Optional[str]:
        """Get the content of the rumor as known to a specific entity."""
        variant_id = self.get_latest_variant_id_for_entity(entity_id)
        if not variant_id:
            return None
            
        variant = self.get_variant_by_id(variant_id)
        if not variant:
            return None
            
        return variant.content
        
    def get_believability_for_entity(self, entity_id: str) -> Optional[float]:
        """Get how strongly an entity believes this rumor."""
        # Filter spread records for this entity
        entity_spread = [s for s in self.spread if s.entity_id == entity_id]
        
        if not entity_spread:
            return None
            
        # Get the most recent spread
        latest_spread = max(entity_spread, key=lambda s: s.heard_at)
        return latest_spread.believability
    
    def entity_knows_rumor(self, entity_id: str) -> bool:
        """Check if an entity has heard this rumor."""
        return any(s.entity_id == entity_id for s in self.spread)
