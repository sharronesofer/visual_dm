"""
This module defines the canonical memory categories and utility functions for
memory categorization in the Visual DM memory system.
"""

from enum import Enum
from typing import List, Dict, Optional, Set, Any

class MemoryCategory(str, Enum):
    """Canonical memory categories."""
    # Personal categories
    PERSONAL = "personal"
    TRAUMA = "trauma" 
    ACCOMPLISHMENT = "accomplishment"
    RELATIONSHIP = "relationship"
    IDENTITY = "identity"
    
    # World event categories
    WAR = "war"
    CATASTROPHE = "catastrophe"
    POLITICS = "politics"
    CELEBRATION = "celebration"
    DISCOVERY = "discovery"
    
    # Narrative categories
    ARC = "arc"
    QUEST = "quest"
    SECRET = "secret"
    RUMOR = "rumor"
    PROPHECY = "prophecy"
    
    # Social categories
    FACTION = "faction"
    ALLIANCE = "alliance"
    BETRAYAL = "betrayal"
    RIVALRY = "rivalry"
    FRIENDSHIP = "friendship"
    
    # Location categories
    LOCATION = "location"
    POI = "poi"
    REGION = "region"
    HOME = "home"
    JOURNEY = "journey"
    
    # Combat categories
    COMBAT = "combat"
    VICTORY = "victory"
    DEFEAT = "defeat"
    INJURY = "injury"
    DEATH = "death"
    
    # Other categories
    RELIGION = "religion"
    ECONOMY = "economy"
    CUSTOM = "custom"


class MemoryCategoryMetadata:
    """Metadata for memory categories."""
    
    _category_metadata: Dict[MemoryCategory, Dict[str, Any]] = {
        MemoryCategory.PERSONAL: {
            "display_name": "Personal Memory",
            "description": "Personal experience or reflection",
            "decay_modifier": 0.8,  # Slows decay for personal memories
            "importance_modifier": 1.2  # Increases importance of personal memories
        },
        MemoryCategory.TRAUMA: {
            "display_name": "Traumatic Memory",
            "description": "Negative, impactful experience",
            "decay_modifier": 0.5,  # Traumatic memories decay much slower
            "importance_modifier": 1.5  # Traumatic memories have higher importance
        },
        MemoryCategory.WAR: {
            "display_name": "War Memory",
            "description": "Conflict or large-scale violence",
            "decay_modifier": 0.7,  # War memories decay slower
            "importance_modifier": 1.3  # War memories have higher importance
        },
        MemoryCategory.ARC: {
            "display_name": "Narrative Arc",
            "description": "Significant narrative moment",
            "decay_modifier": 0.6,  # Arc memories decay slower
            "importance_modifier": 1.4  # Arc memories have higher importance
        },
        # Default values for other categories if not explicitly defined
        "_default": {
            "display_name": "",  # Will be auto-generated from enum name
            "description": "General memory category",
            "decay_modifier": 1.0,  # No modification to decay
            "importance_modifier": 1.0  # No modification to importance
        }
    }
    
    @classmethod
    def get_metadata(cls, category: MemoryCategory) -> Dict[str, Any]:
        """Get metadata for a specific category."""
        if category in cls._category_metadata:
            metadata = cls._category_metadata[category].copy()
        else:
            metadata = cls._category_metadata["_default"].copy()
            # Generate display name from enum if not explicitly defined
            metadata["display_name"] = category.name.title().replace('_', ' ')
            
        return metadata
    
    @classmethod
    def get_decay_modifier(cls, category: MemoryCategory) -> float:
        """Get decay modifier for a specific category."""
        return cls.get_metadata(category).get("decay_modifier", 1.0)
    
    @classmethod
    def get_importance_modifier(cls, category: MemoryCategory) -> float:
        """Get importance modifier for a specific category."""
        return cls.get_metadata(category).get("importance_modifier", 1.0)


def categorize_memory_content(content: str) -> Set[MemoryCategory]:
    """
    Automatically categorize memory content based on keywords and context.
    
    This is a simple rule-based implementation. In a production environment,
    this would likely use an LLM or ML model for more accurate categorization.
    
    Args:
        content: The memory content text
        
    Returns:
        A set of MemoryCategory values
    """
    content_lower = content.lower()
    categories = set()
    
    # Personal memory checks
    if any(word in content_lower for word in ["i feel", "i think", "i believe", "my thoughts"]):
        categories.add(MemoryCategory.PERSONAL)
    
    # Trauma checks
    if any(word in content_lower for word in ["afraid", "terrified", "hurt", "pain", "trauma"]):
        categories.add(MemoryCategory.TRAUMA)
    
    # War checks
    if any(word in content_lower for word in ["war", "battle", "fight", "conflict", "army"]):
        categories.add(MemoryCategory.WAR)
        categories.add(MemoryCategory.COMBAT)
    
    # Quest/arc checks
    if any(word in content_lower for word in ["quest", "mission", "task", "adventure"]):
        categories.add(MemoryCategory.QUEST)
        
    # Faction checks
    if any(word in content_lower for word in ["faction", "guild", "group", "organization"]):
        categories.add(MemoryCategory.FACTION)
    
    # Location checks
    if any(word in content_lower for word in ["city", "town", "village", "place", "location"]):
        categories.add(MemoryCategory.LOCATION)
    
    # Religion checks
    if any(word in content_lower for word in ["god", "deity", "pray", "worship", "faith"]):
        categories.add(MemoryCategory.RELIGION)
    
    # Default to PERSONAL if no categories detected
    if not categories:
        categories.add(MemoryCategory.PERSONAL)
    
    return categories

def apply_category_modifiers(base_importance: float, base_decay_rate: float, 
                            categories: List[MemoryCategory]) -> Dict[str, float]:
    """
    Apply category-specific modifiers to importance and decay rate.
    
    Args:
        base_importance: Base importance value
        base_decay_rate: Base decay rate value
        categories: List of MemoryCategory values
        
    Returns:
        Dictionary with modified importance and decay_rate
    """
    if not categories:
        return {"importance": base_importance, "decay_rate": base_decay_rate}
        
    # Apply modifiers from all categories
    importance_modifier = 1.0
    decay_modifier = 1.0
    
    for category in categories:
        importance_modifier *= MemoryCategoryMetadata.get_importance_modifier(category)
        decay_modifier *= MemoryCategoryMetadata.get_decay_modifier(category)
    
    # Cap modifiers to prevent extreme values
    importance_modifier = min(max(importance_modifier, 0.5), 2.0)
    decay_modifier = min(max(decay_modifier, 0.1), 1.5)
    
    return {
        "importance": base_importance * importance_modifier,
        "decay_rate": base_decay_rate * decay_modifier
    } 