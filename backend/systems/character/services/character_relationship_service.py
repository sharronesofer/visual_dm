"""
Character Relationship Service

Manages relationships between characters and NPCs, including:
- Relationship tracking and scoring
- Faction-based relationships
- Loyalty and trust calculations
- Relationship history and events
"""

from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime
from enum import Enum
import logging
from dataclasses import dataclass

# Business logic imports
from backend.systems.character.models.character import Character
from backend.infrastructure.database_services.character_relationship_repository import CharacterRelationshipRepository
from backend.infrastructure.shared.exceptions import NotFoundError, RepositoryError

logger = logging.getLogger(__name__)


class RelationshipTier(Enum):
    """Relationship tiers matching Task 63 specifications"""
    STRANGER = "stranger"           # 0.0-0.2: +50% markup, limited access
    ACQUAINTANCE = "acquaintance"   # 0.2-0.4: +25% markup, standard access  
    FRIEND = "friend"               # 0.4-0.6: Standard pricing, expanded access
    CLOSE_FRIEND = "close_friend"   # 0.6-0.8: -15% discount, rare item access
    TRUSTED_ALLY = "trusted_ally"   # 0.8-1.0: -25% discount, full access


class RelationshipType(Enum):
    """Types of relationships"""
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    ROMANTIC = "romantic"
    RIVAL = "rival"
    ENEMY = "enemy"
    FAMILY = "family"
    PROFESSIONAL = "professional"
    MENTOR = "mentor"
    STUDENT = "student"


@dataclass
class RelationshipMemory:
    """Individual memory affecting relationship"""
    memory_id: str
    interaction_type: str
    impact: float  # -1.0 to 1.0
    timestamp: datetime
    description: str
    importance: int = 1  # 1-10 scale
    decay_rate: float = 0.95  # How quickly this memory fades


@dataclass
class CharacterRelationship:
    """Complete relationship data between character and NPC"""
    character_id: str
    npc_id: UUID
    trust_level: float = 0.3  # 0.0-1.0 scale
    relationship_type: RelationshipType = RelationshipType.NEUTRAL
    relationship_tier: RelationshipTier = RelationshipTier.STRANGER
    total_interactions: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0
    last_interaction: Optional[datetime] = None
    memories: List[RelationshipMemory] = None
    faction_modifier: float = 0.0  # Additional modifier from faction relations
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.memories is None:
            self.memories = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        
        # Update tier based on trust level
        self._update_relationship_tier()
    
    def _update_relationship_tier(self):
        """Update relationship tier based on trust level"""
        if self.trust_level >= 0.8:
            self.relationship_tier = RelationshipTier.TRUSTED_ALLY
        elif self.trust_level >= 0.6:
            self.relationship_tier = RelationshipTier.CLOSE_FRIEND
        elif self.trust_level >= 0.4:
            self.relationship_tier = RelationshipTier.FRIEND
        elif self.trust_level >= 0.2:
            self.relationship_tier = RelationshipTier.ACQUAINTANCE
        else:
            self.relationship_tier = RelationshipTier.STRANGER
    
    def add_memory(self, memory: RelationshipMemory):
        """Add a new relationship memory"""
        self.memories.append(memory)
        self.total_interactions += 1
        
        if memory.impact > 0:
            self.positive_interactions += 1
        elif memory.impact < 0:
            self.negative_interactions += 1
        
        self.last_interaction = memory.timestamp
        self.updated_at = datetime.utcnow()
        
        # Update trust based on memory impact
        self._update_trust_from_memory(memory)
        self._update_relationship_tier()
    
    def _update_trust_from_memory(self, memory: RelationshipMemory):
        """Update trust level based on new memory"""
        # Weight the impact by importance and existing trust
        weighted_impact = memory.impact * (memory.importance / 10.0)
        
        # Recent interactions have more impact
        recency_factor = 1.0  # Could be enhanced with time-based scaling
        
        # Apply the trust change
        trust_change = weighted_impact * recency_factor * 0.1  # Scale factor
        self.trust_level = max(0.0, min(1.0, self.trust_level + trust_change))
    
    def decay_memories(self, days_passed: int = 1):
        """Apply memory decay over time"""
        for memory in self.memories:
            # Memories decay over time
            decay_factor = memory.decay_rate ** days_passed
            memory.impact *= decay_factor
            
            # Remove memories that have decayed to insignificance
            if abs(memory.impact) < 0.01:
                self.memories.remove(memory)
        
        # Recalculate trust based on remaining memories
        self._recalculate_trust_from_memories()
        self._update_relationship_tier()
    
    def _recalculate_trust_from_memories(self):
        """Recalculate trust level from current memories"""
        if not self.memories:
            self.trust_level = 0.3  # Base neutral trust
            return
        
        # Calculate weighted average of memories
        total_weighted_impact = 0.0
        total_weight = 0.0
        
        for memory in self.memories:
            weight = memory.importance / 10.0
            total_weighted_impact += memory.impact * weight
            total_weight += weight
        
        if total_weight > 0:
            average_impact = total_weighted_impact / total_weight
            # Convert impact to trust (0.3 base + impact adjustment)
            self.trust_level = max(0.0, min(1.0, 0.3 + average_impact * 0.7))
        else:
            self.trust_level = 0.3
    
    def get_barter_access_level(self) -> str:
        """Get barter access level based on relationship tier"""
        access_mapping = {
            RelationshipTier.STRANGER: "limited",
            RelationshipTier.ACQUAINTANCE: "standard", 
            RelationshipTier.FRIEND: "expanded",
            RelationshipTier.CLOSE_FRIEND: "rare",
            RelationshipTier.TRUSTED_ALLY: "full"
        }
        return access_mapping.get(self.relationship_tier, "limited")


class CharacterRelationshipService:
    """Service for managing character-NPC relationships with pure business logic"""
    
    def __init__(self, character_relationship_repository: CharacterRelationshipRepository):
        """Initialize the relationship service with repository dependency"""
        self.repository = character_relationship_repository
        self._relationship_cache = {}  # In-memory cache for performance
    
    def get_relationship(self, character_id: str, npc_id: UUID) -> CharacterRelationship:
        """Get or create relationship between character and NPC"""
        cache_key = f"{character_id}:{npc_id}"
        
        # Check cache first
        if cache_key in self._relationship_cache:
            return self._relationship_cache[cache_key]
        
        # Try to load from repository
        relationship = self._load_relationship_from_storage(character_id, npc_id)
        
        if not relationship:
            # Create new relationship if none exists
            relationship = self._create_new_relationship(character_id, npc_id)
        
        # Cache the relationship
        self._relationship_cache[cache_key] = relationship
        
        return relationship
    
    def _create_new_relationship(self, character_id: str, npc_id: UUID) -> CharacterRelationship:
        """Create a new relationship with default values"""
        return CharacterRelationship(
            character_id=character_id,
            npc_id=npc_id,
            trust_level=0.3,  # Neutral starting trust
            relationship_type=RelationshipType.NEUTRAL,
            relationship_tier=RelationshipTier.STRANGER
        )
    
    def _load_relationship_from_storage(self, character_id: str, npc_id: UUID) -> Optional[CharacterRelationship]:
        """Load relationship data from repository"""
        try:
            relationship_data = self.repository.get_relationship_data(character_id, npc_id)
            if relationship_data:
                # Convert stored data back to CharacterRelationship object
                # This would include deserializing memories and other complex fields
                return self._deserialize_relationship_data(relationship_data)
            return None
        except RepositoryError as e:
            logger.error(f"Error loading relationship: {e}")
            return None
    
    def _deserialize_relationship_data(self, data: Dict[str, Any]) -> CharacterRelationship:
        """Convert stored data to CharacterRelationship object"""
        # Implementation would deserialize the stored relationship data
        # For now, return a basic relationship
        return CharacterRelationship(
            character_id=data.get('character_id', ''),
            npc_id=UUID(data.get('npc_id', '00000000-0000-0000-0000-000000000000')),
            trust_level=data.get('trust_level', 0.3),
            relationship_type=RelationshipType(data.get('relationship_type', 'neutral')),
            total_interactions=data.get('total_interactions', 0),
            positive_interactions=data.get('positive_interactions', 0),
            negative_interactions=data.get('negative_interactions', 0)
        )
    
    def update_relationship(self, character_id: str, npc_id: UUID, 
                          interaction_type: str, impact: float, 
                          description: str = "", importance: int = 5) -> CharacterRelationship:
        """
        Update relationship based on an interaction.
        
        Args:
            character_id: Character UUID
            npc_id: NPC UUID
            interaction_type: Type of interaction (e.g., 'trade', 'conversation', 'quest')
            impact: Impact on relationship (-1.0 to 1.0)
            description: Description of the interaction
            importance: Importance level (1-10)
        
        Returns:
            Updated CharacterRelationship
        """
        relationship = self.get_relationship(character_id, npc_id)
        
        # Create memory of this interaction
        memory = RelationshipMemory(
            memory_id=f"{character_id}:{npc_id}:{datetime.utcnow().isoformat()}",
            interaction_type=interaction_type,
            impact=impact,
            timestamp=datetime.utcnow(),
            description=description,
            importance=importance
        )
        
        # Add memory to relationship
        relationship.add_memory(memory)
        
        # Apply faction modifiers
        faction_modifier = self.apply_faction_modifier(character_id, npc_id, None, None)
        relationship.faction_modifier = faction_modifier
        
        # Save updated relationship
        try:
            self._save_relationship(relationship)
            self.repository.commit()
        except RepositoryError as e:
            logger.error(f"Error saving relationship: {e}")
            self.repository.rollback()
            raise
        
        return relationship
    
    def _save_relationship(self, relationship: CharacterRelationship):
        """Save relationship to repository"""
        # Convert relationship to storable format
        relationship_data = self._serialize_relationship_data(relationship)
        self.repository.save_relationship_data(
            relationship.character_id, 
            relationship.npc_id, 
            relationship_data
        )
    
    def _serialize_relationship_data(self, relationship: CharacterRelationship) -> Dict[str, Any]:
        """Convert CharacterRelationship to storable data"""
        return {
            'character_id': relationship.character_id,
            'npc_id': str(relationship.npc_id),
            'trust_level': relationship.trust_level,
            'relationship_type': relationship.relationship_type.value,
            'relationship_tier': relationship.relationship_tier.value,
            'total_interactions': relationship.total_interactions,
            'positive_interactions': relationship.positive_interactions,
            'negative_interactions': relationship.negative_interactions,
            'last_interaction': relationship.last_interaction.isoformat() if relationship.last_interaction else None,
            'faction_modifier': relationship.faction_modifier,
            'created_at': relationship.created_at.isoformat() if relationship.created_at else None,
            'updated_at': relationship.updated_at.isoformat() if relationship.updated_at else None,
            'memories': [self._serialize_memory(memory) for memory in relationship.memories]
        }
    
    def _serialize_memory(self, memory: RelationshipMemory) -> Dict[str, Any]:
        """Convert RelationshipMemory to storable data"""
        return {
            'memory_id': memory.memory_id,
            'interaction_type': memory.interaction_type,
            'impact': memory.impact,
            'timestamp': memory.timestamp.isoformat(),
            'description': memory.description,
            'importance': memory.importance,
            'decay_rate': memory.decay_rate
        }
    
    def get_trust_level(self, character_id: str, npc_id: UUID) -> float:
        """
        Get trust level between character and NPC.
        
        Returns:
            Trust level from 0.0 to 1.0
        """
        relationship = self.get_relationship(character_id, npc_id)
        return relationship.trust_level
    
    def get_relationship_tier(self, character_id: str, npc_id: UUID) -> RelationshipTier:
        """
        Get relationship tier for barter access calculations.
        
        Returns:
            RelationshipTier enum value
        """
        relationship = self.get_relationship(character_id, npc_id)
        return relationship.relationship_tier
    
    def apply_faction_modifier(self, character_id: str, npc_id: UUID, 
                             character_faction_id: Optional[str], 
                             npc_faction_id: Optional[str]) -> float:
        """
        Calculate faction-based relationship modifier.
        
        Args:
            character_id: Character UUID
            npc_id: NPC UUID  
            character_faction_id: Character's faction (if None, will be looked up)
            npc_faction_id: NPC's faction (if None, will be looked up)
        
        Returns:
            Faction modifier (-0.5 to 0.5)
        """
        # Get faction IDs if not provided
        if character_faction_id is None:
            character_faction_id = self.repository.get_character_faction_id(character_id)
        
        if npc_faction_id is None:
            npc_faction_id = self.repository.get_npc_faction_id(npc_id)
        
        # No modifier if either has no faction
        if not character_faction_id or not npc_faction_id:
            return 0.0
        
        # Same faction gets bonus
        if character_faction_id == npc_faction_id:
            return 0.3
        
        # Check faction relationships
        faction_status = self.repository.get_faction_relationship_status(character_faction_id, npc_faction_id)
        
        modifier_map = {
            "allied": 0.2,
            "friendly": 0.1,
            "neutral": 0.0,
            "hostile": -0.2,
            "at_war": -0.5
        }
        
        return modifier_map.get(faction_status, 0.0)
    
    def process_barter_interaction(self, character_id: str, npc_id: UUID, 
                                 trade_successful: bool, trade_value_ratio: float,
                                 trade_fairness: str = "fair") -> CharacterRelationship:
        """
        Process a barter interaction and update relationship.
        
        Args:
            character_id: Character UUID
            npc_id: NPC UUID
            trade_successful: Whether trade was completed
            trade_value_ratio: Ratio of value (1.0 = fair, >1.0 = player got good deal)
            trade_fairness: "generous", "fair", "harsh", "exploitative"
        
        Returns:
            Updated relationship
        """
        # Calculate impact based on trade outcome
        impact = 0.0
        interaction_type = "trade"
        description = f"Trade: {trade_fairness}"
        
        if trade_successful:
            # Base positive impact for successful trade
            impact = 0.1
            
            # Adjust based on fairness
            fairness_modifiers = {
                "generous": 0.3,   # Player gave good deal to NPC
                "fair": 0.0,       # No modifier
                "harsh": -0.2,     # Player took advantage
                "exploitative": -0.4  # Player really took advantage
            }
            
            impact += fairness_modifiers.get(trade_fairness, 0.0)
            
            # Adjust based on value ratio
            if trade_value_ratio > 1.2:  # Player got very good deal
                impact -= 0.1
            elif trade_value_ratio < 0.8:  # NPC got very good deal
                impact += 0.1
                
        else:
            # Failed trade has small negative impact
            impact = -0.05
            description = "Failed trade attempt"
        
        return self.update_relationship(
            character_id=character_id,
            npc_id=npc_id,
            interaction_type=interaction_type,
            impact=impact,
            description=description,
            importance=3  # Trade interactions are moderately important
        )
    
    def get_all_character_relationships(self, character_id: str) -> List[CharacterRelationship]:
        """Get all relationships for a character"""
        try:
            relationships_data = self.repository.get_character_relationships_data(character_id)
            return [self._deserialize_relationship_data(data) for data in relationships_data]
        except RepositoryError as e:
            logger.error(f"Error fetching character relationships: {e}")
            return []
    
    def decay_relationships(self, days_passed: int = 1):
        """Apply time-based decay to all cached relationships"""
        for relationship in self._relationship_cache.values():
            relationship.decay_memories(days_passed)
            self._save_relationship(relationship)
    
    def get_relationship_summary(self, character_id: str, npc_id: UUID) -> Dict[str, Any]:
        """
        Get a summary of the relationship for display purposes.
        
        Returns:
            Dictionary with relationship summary information
        """
        relationship = self.get_relationship(character_id, npc_id)
        
        return {
            "trust_level": relationship.trust_level,
            "relationship_type": relationship.relationship_type.value,
            "relationship_tier": relationship.relationship_tier.value,
            "total_interactions": relationship.total_interactions,
            "positive_interactions": relationship.positive_interactions,
            "negative_interactions": relationship.negative_interactions,
            "last_interaction": relationship.last_interaction.isoformat() if relationship.last_interaction else None,
            "faction_modifier": relationship.faction_modifier,
            "barter_access_level": relationship.get_barter_access_level(),
            "recent_memories": [
                {
                    "type": memory.interaction_type,
                    "impact": memory.impact,
                    "description": memory.description,
                    "timestamp": memory.timestamp.isoformat()
                }
                for memory in sorted(relationship.memories, key=lambda m: m.timestamp, reverse=True)[:5]
            ]
        }


def get_character_relationship_service(character_relationship_repository: CharacterRelationshipRepository) -> CharacterRelationshipService:
    """Factory function for creating CharacterRelationshipService with repository dependency"""
    return CharacterRelationshipService(character_relationship_repository) 