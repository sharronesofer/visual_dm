"""
Character Models
---------------
Data models representing characters and their attributes. These include the
core Character ORM model, the CharacterBuilder for character creation, and
visual models for character appearance.
"""

from backend.systems.character.models.character import Character, Skill
from backend.systems.character.models.character_builder import CharacterBuilder, generate_basic_stats
from backend.systems.character.models.visual_model import (
    MeshSlot, MaterialSlot, AnimationSlot, BlendShape, 
    VisualModel, Mesh, Material, Animation
)

__all__ = [
    'Character', 'Skill', 'CharacterBuilder', 'generate_basic_stats',
    'MeshSlot', 'MaterialSlot', 'AnimationSlot', 'BlendShape',
    'VisualModel', 'Mesh', 'Material', 'Animation'
]
