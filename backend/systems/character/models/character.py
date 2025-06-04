from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from typing import List, Dict, Optional, Any, Union, TYPE_CHECKING
from uuid import uuid4, UUID
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator, root_validator
from dataclasses import dataclass, field
from enum import Enum
import json

# Import from the core database module
try:
    from backend.infrastructure.database import Base
except ImportError:
    # Fallback if core database is not available
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

character_skills = Table(
    'character_skills',
    Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True),
    extend_existing=True
)

class Character(Base):
    """
    Character model representing both player and non-player characters.
    Integrated with mood, goal, and relationship systems as described in the Development Bible.
    Skills are now stored as JSON data with proficiency information.
    """
    __tablename__ = 'characters'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), default=lambda: str(uuid4()), unique=True, index=True)
    name = Column(String(100), nullable=False)
    race = Column(String(50), nullable=False)
    level = Column(Integer, default=1)
    stats = Column(JSON, nullable=False)  # Stores ability scores, HP, etc.
    background = Column(String(100))
    alignment = Column(String(50))
    
    # Skills are now stored as JSON instead of separate table
    # Format: {"skill_name": {"proficient": true, "expertise": false, "bonus": 0}, ...}
    skills = Column(JSON, default=dict)  
    
    visual_data = Column(JSON, default=dict)  # Stores visual model data (CharacterModel serialized)
    notes = Column(JSON, default=list)  # Character-specific notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Character {self.name} ({self.uuid})>"

    def to_builder(self):
        """Convert this Character model to a CharacterBuilder instance for modifications."""
        from backend.systems.character.services.character_builder import CharacterBuilder
        from backend.infrastructure.config_loaders.character_config_loader import config_loader

        # Load configuration-based data
        races_config = config_loader.load_races_config()
        abilities_config = config_loader.load_abilities_config()
        skill_list = config_loader.get_skill_list()

        builder = CharacterBuilder(
            race_data=races_config, 
            ability_data=abilities_config.get("feats", {}),  # JSON still uses "feats" key for backward compatibility, but Visual DM uses "abilities" terminology
            skill_list=skill_list
        )
        builder.character_name = self.name
        
        if self.race in races_config:
            builder.selected_race = self.race
        else:
            print(f"Warning: Character race '{self.race}' not found in builder's race_data.")

        # Populate attributes
        if isinstance(self.stats, dict):
            for attr, value in self.stats.items():
                if attr.upper() in builder.attributes:
                    builder.attributes[attr.upper()] = value
                elif hasattr(builder, attr):
                    setattr(builder, attr, value)
        
        builder.level = self.level
        
        # Extract skill names from the new JSON format
        if isinstance(self.skills, dict):
            builder.selected_skills = list(self.skills.keys())
        else:
            # Fallback for legacy data
            builder.selected_skills = []
        
        return builder
    
    def get_skill_proficiency(self, skill_name: str) -> Dict[str, Any]:
        """Get proficiency information for a specific skill."""
        if not isinstance(self.skills, dict):
            return {"proficient": False, "expertise": False, "bonus": 0}
        
        return self.skills.get(skill_name, {"proficient": False, "expertise": False, "bonus": 0})
    
    def set_skill_proficiency(self, skill_name: str, proficient: bool = True, expertise: bool = False, bonus: int = 0):
        """Set proficiency information for a specific skill."""
        if not isinstance(self.skills, dict):
            self.skills = {}
        
        self.skills[skill_name] = {
            "proficient": proficient,
            "expertise": expertise,
            "bonus": bonus
        }
    
    def add_skill(self, skill_name: str, proficient: bool = True):
        """Add a skill with proficiency to the character."""
        self.set_skill_proficiency(skill_name, proficient)
    
    def remove_skill(self, skill_name: str):
        """Remove a skill from the character."""
        if isinstance(self.skills, dict) and skill_name in self.skills:
            del self.skills[skill_name]
    
    def get_proficient_skills(self) -> List[str]:
        """Get a list of all skills the character is proficient in."""
        if not isinstance(self.skills, dict):
            return []
        
        return [
            skill_name for skill_name, skill_data in self.skills.items()
            if skill_data.get("proficient", False)
        ]
    
    def get_expertise_skills(self) -> List[str]:
        """Get a list of all skills the character has expertise in."""
        if not isinstance(self.skills, dict):
            return []
        
        return [
            skill_name for skill_name, skill_data in self.skills.items()
            if skill_data.get("expertise", False)
        ]

    # Relationship System Integration
    def get_relationships(self, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all relationships for this character, optionally filtered by type."""
        from backend.systems.character.services.relationship_service import RelationshipService
        
        service = RelationshipService()
        relationships = service.get_relationships_by_source(self.uuid, relationship_type)
        return [rel.to_dict() for rel in relationships]
    
    def get_faction_relationships(self) -> List[Dict[str, Any]]:
        """Get all faction relationships for this character."""
        from backend.systems.character.services.relationship_service import RelationshipService
        from backend.systems.character.models.relationship import RelationshipType
        
        service = RelationshipService()
        relationships = service.get_relationships_by_source(
            self.uuid, 
            RelationshipType.FACTION
        )
        return [rel.to_dict() for rel in relationships]
    
    def get_character_relationships(self) -> List[Dict[str, Any]]:
        """Get all character-to-character relationships for this character."""
        from backend.systems.character.services.relationship_service import RelationshipService
        from backend.systems.character.models.relationship import RelationshipType
        
        service = RelationshipService()
        relationships = service.get_relationships_by_source(
            self.uuid, 
            RelationshipType.CHARACTER
        )
        return [rel.to_dict() for rel in relationships]
    
    def add_relationship(self, target_id: Union[str, UUID], relationship_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new relationship from this character to another entity."""
        from backend.systems.character.services.relationship_service import RelationshipService
        
        service = RelationshipService()
        relationship = service.create_relationship(
            self.uuid,
            target_id,
            relationship_type,
            data
        )
        return relationship.to_dict()
    
    # Mood System Integration
    def get_mood(self) -> Dict[str, Any]:
        """Get the character's current mood state."""
        from backend.systems.character.services.mood_service import MoodService
        
        service = MoodService()
        mood = service.get_mood(self.uuid)
        return mood.to_dict()
    
    def get_mood_description(self) -> str:
        """Get a human-readable description of the character's current mood."""
        from backend.systems.character.services.mood_service import MoodService
        
        service = MoodService()
        return service.get_mood_description(self.uuid)
    
    def update_mood(self, mood_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update the character's mood with new data."""
        from backend.systems.character.services.mood_service import MoodService
        
        service = MoodService()
        updated_mood = service.update_mood(self.uuid, mood_data)
        return updated_mood.to_dict()
    
    # Goal System Integration
    def get_goals(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all goals for this character."""
        from backend.systems.character.services.goal_service import GoalService
        
        service = GoalService()
        goals = service.get_character_goals(self.uuid, active_only)
        return [goal.to_dict() for goal in goals]
    
    def add_goal(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new goal for this character."""
        from backend.systems.character.services.goal_service import GoalService
        
        service = GoalService()
        goal = service.create_goal(self.uuid, goal_data)
        return goal.to_dict()
    
    def update_goal(self, goal_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific goal for this character."""
        from backend.systems.character.services.goal_service import GoalService
        
        service = GoalService()
        updated_goal = service.update_goal(goal_id, updates)
        return updated_goal.to_dict()

    # Visual Model Integration
    def get_visual_model(self):
        """Get the character's visual model (CharacterModel instance)."""
        from backend.systems.character.models.visual_model import CharacterModel
        
        if self.visual_data:
            return CharacterModel.from_dict(self.visual_data)
        else:
            # Create default visual model based on race
            return CharacterModel(
                race=self.race,
                base_mesh=f"base_{self.race.lower()}",
                scale={"height": 1.0, "build": 0.5}
            )
    
    def set_visual_model(self, visual_model):
        """Set the character's visual model (from CharacterModel instance)."""
        from backend.systems.character.models.visual_model import CharacterModel
        
        if isinstance(visual_model, CharacterModel):
            self.visual_data = visual_model.to_dict()
        elif isinstance(visual_model, dict):
            self.visual_data = visual_model
        else:
            raise ValueError("visual_model must be a CharacterModel instance or dict")
    
    def update_visual_appearance(self, updates: Dict[str, Any]):
        """Update specific aspects of the character's visual appearance."""
        visual_model = self.get_visual_model()
        
        if "blendshapes" in updates:
            for name, value in updates["blendshapes"].items():
                visual_model.set_blendshape(name, value)
        
        if "materials" in updates:
            for slot, material_data in updates["materials"].items():
                if isinstance(material_data, dict):
                    visual_model.assign_material(slot, material_data.get("id", "default"), 
                                               material_data.get("properties", {}))
                else:
                    visual_model.assign_material(slot, material_data)
        
        if "mesh_slots" in updates:
            for slot, mesh_id in updates["mesh_slots"].items():
                visual_model.swap_mesh(slot, mesh_id)
        
        if "scale" in updates:
            visual_model.scale.update(updates["scale"])
        
        self.set_visual_model(visual_model)

__all__ = ["Character"] 