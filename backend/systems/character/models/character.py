from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from typing import List, Dict, Optional, Any, Union
from uuid import uuid4, UUID
# Assuming Base is available from backend.core.database or a similar central place
# For example: from backend.core.database import Base
# If Base is defined in backend_backup/app/models/base.py, that needs to be handled.
# For now, I'll assume a placeholder Base or it needs to be imported correctly.

# Placeholder for Base if its actual import path is unknown
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

character_skills = Table(
    'character_skills',
    Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

class Character(Base):
    """
    Character model representing both player and non-player characters.
    Integrated with mood, goal, and relationship systems as described in the Development Bible.
    """
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), default=lambda: str(uuid4()), unique=True, index=True)
    name = Column(String(100), nullable=False)
    race = Column(String(50), nullable=False)
    level = Column(Integer, default=1)
    stats = Column(JSON, nullable=False)  # Stores ability scores, HP, etc.
    background = Column(String(100))
    alignment = Column(String(50))
    # equipment = Column(JSON, default=list)  # REMOVED: Inventory is now managed by Inventory/InventoryItem
    skills = relationship('Skill', secondary=character_skills, backref='characters')
    notes = Column(JSON, default=list)  # Character-specific notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Fields from CharacterBuilder that might be missing and could be added:
    # attributes_json = Column(JSON) # Or expand stats to include all attributes
    # xp = Column(Integer, default=0)
    # hp = Column(Integer) # This might be part of 'stats' JSON
    # mp = Column(Integer) # This might be part of 'stats' JSON
    # gold = Column(Integer, default=0)
    # faction_affiliations: Managed by Relationship model
    # reputation: Managed by Relationship model or a direct field
    # ... other fields from CharacterBuilder.finalize() output

    def __repr__(self):
        return f"<Character {self.name} ({self.uuid})>"

    def to_builder(self):
        from backend.systems.character.core.character_builder_class import CharacterBuilder, RACES_DATA, FEATS_LIST # Assuming FEATS_LIST is what builder uses
        # Assuming SKILL_LIST is defined in character_builder_class or accessible
        # For now, let's fetch all skill names from the DB as a list for the builder.
        # This might need refinement based on where CharacterBuilder expects its skill_list from.
        from backend.core.database import get_db_session # Temporary for fetching skills
        db_session = next(get_db_session())
        all_skills_from_db = [s.name for s in db_session.query(Skill.name).all()]
        db_session.close()

        # Initialize builder with necessary static data
        # Ensure RACES_DATA and FEATS_LIST are correctly loaded in CharacterBuilder or passed appropriately
        builder = CharacterBuilder(race_data=RACES_DATA, feat_data=FEATS_LIST, skill_list=all_skills_from_db)

        builder.character_name = self.name
        if self.race in builder.race_data:
            builder.selected_race = self.race
        else:
            print(f"Warning: Character race '{self.race}' not found in builder's race_data.")

        # Populate attributes
        if isinstance(self.stats, dict):
            for attr, value in self.stats.items():
                if attr.upper() in builder.attributes: # Builder uses uppercase keys like STR, DEX
                    builder.attributes[attr.upper()] = value
                # Also handle direct stat fields if they were on builder (hp, mp, ac, xp, level)
                elif hasattr(builder, attr):
                    setattr(builder, attr, value)
        
        builder.level = self.level
        # if hasattr(self, 'xp'): builder.xp = self.xp # If Character ORM has xp
        # if hasattr(self, 'gold'): builder.gold = self.gold # If Character ORM has gold
        # Note: HP, MP, AC are usually derived in builder.finalize(), 
        # so not setting them directly unless the builder expects it.

        # Populate skills (names)
        builder.selected_skills = [skill.name for skill in self.skills]

        # Populate feats (names)
        # This assumes feats are stored in a way that can be retrieved and matched to builder.feat_data keys
        # If Character.feats is a relationship to a Feat model similar to Skill:
        # builder.selected_feats = [feat.name for feat in self.feats_relationship] # Assuming feats_relationship
        # For now, if feats are stored as a list of names in self.stats or another field:
        # if isinstance(self.stats.get('feats'), list):
        #    builder.selected_feats = [f for f in self.stats['feats'] if f in builder.feat_data]

        # Starter kit is usually applied during initial creation, not typically reverse-populated this way.
        # If needed, specific equipment/gold from inventory could be mapped back if the builder needs it.

        # Alignment, background, notes if they exist on Character ORM and builder has fields for them
        if hasattr(self, 'alignment') and hasattr(builder, 'alignment'): # builder doesn't have alignment field
             pass # builder.alignment = self.alignment
        if hasattr(self, 'background') and hasattr(builder, 'background'): # builder doesn't have background
             pass # builder.background = self.background
        # Notes: builder doesn't have a direct notes field. Could be part of some other dict.

        return builder

    # Relationship System Integration
    def get_relationships(self, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all relationships for this character, optionally filtered by type.
        
        Args:
            relationship_type: Optional filter by relationship type
            
        Returns:
            List of relationship dictionaries
        """
        from backend.systems.character import get_relationship_service
        
        relationships = get_relationship_service().get_relationships_by_source(self.uuid, relationship_type)
        return [rel.to_dict() for rel in relationships]
    
    def get_faction_relationships(self) -> List[Dict[str, Any]]:
        """
        Get all faction relationships for this character.
        
        Returns:
            List of faction relationship dictionaries
        """
        from backend.systems.character import get_relationship_service
        from backend.systems.character.models.relationship import RelationshipType
        
        relationships = get_relationship_service().get_relationships_by_source(
            self.uuid, 
            RelationshipType.FACTION
        )
        return [rel.to_dict() for rel in relationships]
    
    def get_character_relationships(self) -> List[Dict[str, Any]]:
        """
        Get all character-to-character relationships for this character.
        
        Returns:
            List of character relationship dictionaries
        """
        from backend.systems.character import get_relationship_service
        from backend.systems.character.models.relationship import RelationshipType
        
        relationships = get_relationship_service().get_relationships_by_source(
            self.uuid, 
            RelationshipType.CHARACTER
        )
        return [rel.to_dict() for rel in relationships]
    
    def add_relationship(self, 
                        target_id: Union[str, UUID], 
                        relationship_type: str, 
                        data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new relationship from this character to another entity.
        
        Args:
            target_id: UUID of the target entity
            relationship_type: Type of relationship to create
            data: Relationship-specific data
            
        Returns:
            Dictionary representation of the created relationship
        """
        from backend.systems.character import get_relationship_service
        
        relationship = get_relationship_service().create_relationship(
            self.uuid,
            target_id,
            relationship_type,
            data
        )
        return relationship.to_dict()
    
    # Mood System Integration
    def get_mood(self) -> Dict[str, Any]:
        """
        Get the character's current mood state.
        
        Returns:
            Dictionary with mood information
        """
        from backend.systems.character import get_mood_service
        
        mood = get_mood_service().get_mood(self.uuid)
        return mood.to_dict()
    
    def get_mood_description(self) -> str:
        """
        Get a text description of the character's current mood.
        
        Returns:
            String description like "extremely angry" or "mildly happy"
        """
        from backend.systems.character import get_mood_service
        
        return get_mood_service().get_mood_description(self.uuid)
    
    def add_mood_modifier(self, 
                         emotional_state: str, 
                         intensity: str, 
                         reason: str, 
                         duration_hours: Optional[float] = None) -> Dict[str, Any]:
        """
        Add a mood modifier to this character.
        
        Args:
            emotional_state: The emotion being affected
            intensity: How strongly the modifier affects the mood
            reason: Description of what caused this modifier
            duration_hours: How long the modifier lasts (None = permanent)
            
        Returns:
            Dictionary representation of the created modifier
        """
        from backend.systems.character import get_mood_service
        
        modifier = get_mood_service().add_mood_modifier(
            self.uuid,
            emotional_state,
            intensity,
            reason,
            duration_hours
        )
        return modifier.to_dict() if modifier else {}
    
    # Goal System Integration
    def get_goals(self, 
                status: Optional[str] = None, 
                goal_type: Optional[str] = None, 
                priority: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get goals for this character, optionally filtered.
        
        Args:
            status: Filter by goal status
            goal_type: Filter by goal type
            priority: Filter by goal priority
            
        Returns:
            List of goal dictionaries
        """
        from backend.systems.character import get_goal_service
        
        goals = get_goal_service().get_character_goals(
            self.uuid,
            goal_type=goal_type,
            status=status,
            priority=priority
        )
        return [goal.to_dict() for goal in goals]
    
    def add_goal(self, 
               description: str, 
               goal_type: str = None, 
               priority: str = None, 
               metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a new goal to this character.
        
        Args:
            description: Description of the goal
            goal_type: Type of goal (narrative, personal, etc.)
            priority: Priority level (low, medium, high, critical)
            metadata: Additional goal metadata
            
        Returns:
            Dictionary representation of the created goal
        """
        from backend.systems.character import get_goal_service
        
        goal = get_goal_service().add_goal(
            self.uuid,
            description,
            goal_type=goal_type,
            priority=priority,
            metadata=metadata
        )
        return goal.to_dict()
    
    def get_active_goals(self) -> List[Dict[str, Any]]:
        """
        Get all active goals for this character.
        
        Returns:
            List of active goal dictionaries
        """
        from backend.systems.character import get_goal_service
        
        goals = get_goal_service().get_active_goals(self.uuid)
        return [goal.to_dict() for goal in goals]
    
    def get_highest_priority_goals(self, 
                                 status: str = "active", 
                                 limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the highest priority goals for this character.
        
        Args:
            status: Filter by goal status
            limit: Maximum number of goals to return
            
        Returns:
            List of goal dictionaries
        """
        from backend.systems.character import get_goal_service
        
        goals = get_goal_service().get_highest_priority_goals(
            self.uuid,
            status=status,
            limit=limit
        )
        return [goal.to_dict() for goal in goals]
    
    # Memory System Integration
    def get_memories(self, 
                   categories: Optional[List[str]] = None, 
                   min_relevance: float = 0.0, 
                   core_only: bool = False, 
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get memories for this character, optionally filtered.
        
        Args:
            categories: Filter by categories
            min_relevance: Minimum relevance threshold
            core_only: Only include core memories
            limit: Maximum number of memories to return
            
        Returns:
            List of memory dictionaries
        """
        from backend.systems.character import get_memory_manager
        
        memory_manager = get_memory_manager().for_entity(self.uuid)
        memories = memory_manager.query_memories(
            categories=categories,
            min_relevance=min_relevance,
            core_only=core_only,
            limit=limit
        )
        return [memory.to_dict() for memory in memories]
    
    def add_memory(self, 
                 content: str, 
                 relevance: float = 1.0, 
                 is_core: bool = False, 
                 metadata: Optional[Dict[str, Any]] = None, 
                 categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Add a new memory to this character.
        
        Args:
            content: The memory content
            relevance: Initial relevance score
            is_core: Whether this is a core memory
            metadata: Additional memory metadata
            categories: Categories for this memory
            
        Returns:
            Dictionary representation of the created memory
        """
        from backend.systems.character import get_memory_manager
        
        memory_manager = get_memory_manager().for_entity(self.uuid)
        memory = memory_manager.add_memory(
            content,
            relevance=relevance,
            is_core=is_core,
            metadata=metadata,
            categories=categories
        )
        return memory.to_dict()
    
    def get_memory_summary(self, 
                        categories: Optional[List[str]] = None, 
                        min_relevance: float = 0.5, 
                        max_memories: int = 10) -> str:
        """
        Get a formatted summary of this character's memories for GPT context.
        
        Args:
            categories: Filter by categories
            min_relevance: Minimum relevance threshold
            max_memories: Maximum number of memories to include
            
        Returns:
            Formatted memory summary string
        """
        from backend.systems.character import get_memory_manager
        
        memory_manager = get_memory_manager().for_entity(self.uuid)
        return memory_manager.generate_memory_summary(
            categories=categories,
            min_relevance=min_relevance,
            max_memories=max_memories
        )

class Skill(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    ability = Column(String(50))  # Associated ability score
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Skill {self.name}>"

__all__ = ["Character", "Skill"] 