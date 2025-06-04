"""
Shared infrastructure models used across systems
"""

from .character import Character  # Keep Character for infrastructure compatibility
from .models import SharedBaseModel, SharedEntity, SharedModel, CreateSharedRequest, UpdateSharedRequest, SharedResponse  # Import from models.py where they're actually defined

# Note: Skill has been moved to backend.systems.character.models.character 
# to follow the development bible's clean separation of concerns

__all__ = ["Character", "SharedBaseModel", "SharedEntity", "SharedModel", "CreateSharedRequest", "UpdateSharedRequest", "SharedResponse"] 