"""
Character system - Character Builder model.

This module provides the CharacterBuilder model for character creation
and modification, following the builder pattern for flexible character construction.
"""

from typing import Dict, Any, List, Optional, Union
from backend.systems.character.services.character_builder import CharacterBuilder as CharacterBuilderClass


# Re-export the CharacterBuilder class for compatibility
CharacterBuilder = CharacterBuilderClass


def create_character_builder() -> CharacterBuilder:
    """
    Factory function to create a new CharacterBuilder instance.
    
    Returns:
        New CharacterBuilder instance
    """
    return CharacterBuilder()


def create_character_builder_from_template(template: Dict[str, Any]) -> CharacterBuilder:
    """
    Create a CharacterBuilder from a template dictionary.
    
    Args:
        template: Dictionary containing character template data
        
    Returns:
        CharacterBuilder instance populated with template data
    """
    builder = CharacterBuilder()
    
    # Set basic character data from template
    if "name" in template:
        builder.character_name = template["name"]
    if "race" in template:
        builder.set_race(template["race"])
    if "background" in template:
        # Background is not directly supported in the current builder
        pass
    if "alignment" in template:
        # Alignment is set in finalize() method, not directly settable
        pass
    
    # Set attributes/stats
    if "attributes" in template:
        for attr, value in template["attributes"].items():
            builder.assign_attribute(attr, value)
    elif "stats" in template:
        for stat, value in template["stats"].items():
            builder.assign_attribute(stat, value)
    
    # Set level
    if "level" in template:
        builder.level = template["level"]
    if "experience" in template:
        # Experience is calculated in finalize(), not directly settable
        pass
    
    # Set skills
    if "skills" in template:
        for skill in template["skills"]:
            if isinstance(skill, str):
                builder.assign_skill(skill)
            elif isinstance(skill, dict):
                # The canonical builder doesn't support skill ranks
                builder.assign_skill(skill.get("name", ""))
    
    # Set equipment via starter kit
    if "equipment" in template or "starter_kit" in template:
        starter_kit = template.get("starter_kit")
        if starter_kit:
            try:
                builder.apply_starter_kit(starter_kit)
            except ValueError:
                # Starter kit not found, skip
                pass
    
    # Notes are not supported in the canonical builder
    
    return builder
