"""
Character system - Character Builder model.

This module provides the CharacterBuilder model for character creation
and modification, following the builder pattern for flexible character construction.
"""

from typing import Dict, Any, List, Optional, Union
from backend.systems.character.core.character_builder_class import CharacterBuilder as CharacterBuilderClass


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
        builder.set_name(template["name"])
    if "race" in template:
        builder.set_race(template["race"])
    if "background" in template:
        builder.set_background(template["background"])
    if "alignment" in template:
        builder.set_alignment(template["alignment"])
    
    # Set attributes/stats
    if "attributes" in template:
        for attr, value in template["attributes"].items():
            builder.set_attribute(attr, value)
    elif "stats" in template:
        for stat, value in template["stats"].items():
            builder.set_attribute(stat, value)
    
    # Set level and experience
    if "level" in template:
        builder.set_level(template["level"])
    if "experience" in template:
        builder.set_experience(template["experience"])
    
    # Set skills
    if "skills" in template:
        for skill in template["skills"]:
            if isinstance(skill, str):
                builder.add_skill(skill)
            elif isinstance(skill, dict):
                builder.add_skill(skill.get("name", ""), skill.get("ranks", 1))
    
    # Set equipment
    if "equipment" in template:
        for item in template["equipment"]:
            if isinstance(item, str):
                builder.add_equipment(item)
            elif isinstance(item, dict):
                builder.add_equipment(item.get("name", ""), item.get("quantity", 1))
    
    # Set notes
    if "notes" in template:
        for note in template["notes"]:
            builder.add_note(note)
    
    return builder
