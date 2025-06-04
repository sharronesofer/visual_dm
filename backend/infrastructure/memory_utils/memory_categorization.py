"""
Memory Categories for the memory system.

This module defines the different types of memories that can be stored
and provides categorization functionality.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class MemoryCategory(Enum):
    """Categories for different types of memories."""
    
    # Core memory types
    CORE = "core"                   # Permanent memories that don't decay
    BELIEF = "belief"               # Character beliefs and values
    IDENTITY = "identity"           # Core identity and personality traits
    
    # Interaction memories
    INTERACTION = "interaction"     # Direct interactions with other entities
    CONVERSATION = "conversation"   # Dialogue and communication
    RELATIONSHIP = "relationship"   # Relationship status and history
    
    # Event memories
    EVENT = "event"                 # Significant events witnessed or experienced
    ACHIEVEMENT = "achievement"     # Personal accomplishments
    TRAUMA = "trauma"               # Traumatic or highly emotional events
    
    # Knowledge memories
    KNOWLEDGE = "knowledge"         # Factual information learned
    SKILL = "skill"                 # Skills and abilities acquired
    SECRET = "secret"               # Confidential or sensitive information
    
    # Environmental memories
    LOCATION = "location"           # Places visited or known
    FACTION = "faction"             # Information about factions
    WORLD_STATE = "world_state"     # General world information
    
    # Meta memories
    SUMMARY = "summary"             # Summarized collections of other memories
    TOUCHSTONE = "touchstone"       # Particularly significant memories


class MemoryCategoryInfo(BaseModel):
    """Information about a memory category."""
    
    category: MemoryCategory
    display_name: str
    description: str
    default_importance: float
    decay_modifier: float
    is_permanent: bool = False


# Category configuration
MEMORY_CATEGORY_CONFIG: Dict[MemoryCategory, MemoryCategoryInfo] = {
    MemoryCategory.CORE: MemoryCategoryInfo(
        category=MemoryCategory.CORE,
        display_name="Core Memory",
        description="Fundamental memories that define the character",
        default_importance=1.0,
        decay_modifier=0.0,
        is_permanent=True
    ),
    MemoryCategory.BELIEF: MemoryCategoryInfo(
        category=MemoryCategory.BELIEF,
        display_name="Belief",
        description="Character beliefs, values, and convictions",
        default_importance=0.9,
        decay_modifier=0.1,
        is_permanent=True
    ),
    MemoryCategory.IDENTITY: MemoryCategoryInfo(
        category=MemoryCategory.IDENTITY,
        display_name="Identity",
        description="Core aspects of character identity",
        default_importance=0.95,
        decay_modifier=0.05,
        is_permanent=True
    ),
    MemoryCategory.INTERACTION: MemoryCategoryInfo(
        category=MemoryCategory.INTERACTION,
        display_name="Interaction",
        description="Direct interactions with other entities",
        default_importance=0.7,
        decay_modifier=1.0
    ),
    MemoryCategory.CONVERSATION: MemoryCategoryInfo(
        category=MemoryCategory.CONVERSATION,
        display_name="Conversation",
        description="Dialogue and verbal exchanges",
        default_importance=0.6,
        decay_modifier=1.2
    ),
    MemoryCategory.RELATIONSHIP: MemoryCategoryInfo(
        category=MemoryCategory.RELATIONSHIP,
        display_name="Relationship",
        description="Information about relationships with others",
        default_importance=0.8,
        decay_modifier=0.8
    ),
    MemoryCategory.EVENT: MemoryCategoryInfo(
        category=MemoryCategory.EVENT,
        display_name="Event",
        description="Significant events witnessed or experienced",
        default_importance=0.75,
        decay_modifier=0.9
    ),
    MemoryCategory.ACHIEVEMENT: MemoryCategoryInfo(
        category=MemoryCategory.ACHIEVEMENT,
        display_name="Achievement",
        description="Personal accomplishments and successes",
        default_importance=0.85,
        decay_modifier=0.7
    ),
    MemoryCategory.TRAUMA: MemoryCategoryInfo(
        category=MemoryCategory.TRAUMA,
        display_name="Trauma",
        description="Traumatic or highly emotional experiences",
        default_importance=0.95,
        decay_modifier=0.3
    ),
    MemoryCategory.KNOWLEDGE: MemoryCategoryInfo(
        category=MemoryCategory.KNOWLEDGE,
        display_name="Knowledge",
        description="Factual information and learned knowledge",
        default_importance=0.6,
        decay_modifier=1.1
    ),
    MemoryCategory.SKILL: MemoryCategoryInfo(
        category=MemoryCategory.SKILL,
        display_name="Skill",
        description="Skills and abilities acquired",
        default_importance=0.8,
        decay_modifier=0.5
    ),
    MemoryCategory.SECRET: MemoryCategoryInfo(
        category=MemoryCategory.SECRET,
        display_name="Secret",
        description="Confidential or sensitive information",
        default_importance=0.9,
        decay_modifier=0.6
    ),
    MemoryCategory.LOCATION: MemoryCategoryInfo(
        category=MemoryCategory.LOCATION,
        display_name="Location",
        description="Information about places and locations",
        default_importance=0.5,
        decay_modifier=1.3
    ),
    MemoryCategory.FACTION: MemoryCategoryInfo(
        category=MemoryCategory.FACTION,
        display_name="Faction",
        description="Information about factions and organizations",
        default_importance=0.7,
        decay_modifier=1.0
    ),
    MemoryCategory.WORLD_STATE: MemoryCategoryInfo(
        category=MemoryCategory.WORLD_STATE,
        display_name="World State",
        description="General information about the world",
        default_importance=0.6,
        decay_modifier=1.2
    ),
    MemoryCategory.SUMMARY: MemoryCategoryInfo(
        category=MemoryCategory.SUMMARY,
        display_name="Summary",
        description="Summarized collections of other memories",
        default_importance=0.8,
        decay_modifier=0.4
    ),
    MemoryCategory.TOUCHSTONE: MemoryCategoryInfo(
        category=MemoryCategory.TOUCHSTONE,
        display_name="Touchstone",
        description="Particularly significant and formative memories",
        default_importance=1.0,
        decay_modifier=0.2
    ),
}


def get_category_info(category: MemoryCategory) -> MemoryCategoryInfo:
    """Get information about a memory category."""
    return MEMORY_CATEGORY_CONFIG[category]


def get_all_categories() -> List[MemoryCategory]:
    """Get all available memory categories."""
    return list(MemoryCategory)


def get_permanent_categories() -> List[MemoryCategory]:
    """Get categories that represent permanent memories."""
    return [cat for cat, info in MEMORY_CATEGORY_CONFIG.items() if info.is_permanent]


def get_decay_categories() -> List[MemoryCategory]:
    """Get categories that decay over time."""
    return [cat for cat, info in MEMORY_CATEGORY_CONFIG.items() if not info.is_permanent]


def categorize_memory_content(content: str) -> MemoryCategory:
    """
    Attempt to automatically categorize memory content.
    This is a simple implementation - could be enhanced with AI/ML.
    """
    content_lower = content.lower()
    
    # Check for keywords to determine category
    if any(word in content_lower for word in ['belief', 'believe', 'value', 'principle']):
        return MemoryCategory.BELIEF
    
    if any(word in content_lower for word in ['identity', 'who i am', 'my nature', 'myself']):
        return MemoryCategory.IDENTITY
    
    if any(word in content_lower for word in ['said', 'told', 'spoke', 'conversation', 'talk']):
        return MemoryCategory.CONVERSATION
    
    if any(word in content_lower for word in ['relationship', 'friend', 'enemy', 'ally', 'rival']):
        return MemoryCategory.RELATIONSHIP
    
    if any(word in content_lower for word in ['achieved', 'accomplished', 'succeeded', 'won']):
        return MemoryCategory.ACHIEVEMENT
    
    if any(word in content_lower for word in ['traumatic', 'terrible', 'horrific', 'devastating']):
        return MemoryCategory.TRAUMA
    
    if any(word in content_lower for word in ['learned', 'discovered', 'found out', 'knowledge']):
        return MemoryCategory.KNOWLEDGE
    
    if any(word in content_lower for word in ['skill', 'ability', 'technique', 'learned to']):
        return MemoryCategory.SKILL
    
    if any(word in content_lower for word in ['secret', 'confidential', 'hidden', 'whispered']):
        return MemoryCategory.SECRET
    
    if any(word in content_lower for word in ['place', 'location', 'area', 'region', 'city']):
        return MemoryCategory.LOCATION
    
    if any(word in content_lower for word in ['faction', 'guild', 'organization', 'group']):
        return MemoryCategory.FACTION
    
    # Default to interaction for most memories
    return MemoryCategory.INTERACTION


def apply_category_modifiers(memory_data: Dict[str, Any], category: MemoryCategory) -> Dict[str, Any]:
    """
    Apply category-specific modifiers to a memory.
    
    Args:
        memory_data: The memory data dictionary
        category: The memory category to apply modifiers for
        
    Returns:
        Modified memory data with category-specific adjustments
    """
    if category not in MEMORY_CATEGORY_CONFIG:
        return memory_data
    
    category_info = MEMORY_CATEGORY_CONFIG[category]
    
    # Apply default importance if not set
    if memory_data.get('importance') is None:
        memory_data['importance'] = category_info.default_importance
    
    # Apply decay modifier
    memory_data['decay_modifier'] = category_info.decay_modifier
    
    # Mark as permanent if category is permanent
    if category_info.is_permanent:
        memory_data['is_permanent'] = True
        memory_data['memory_type'] = 'core'
    
    # Add category metadata
    if 'metadata' not in memory_data:
        memory_data['metadata'] = {}
    
    memory_data['metadata']['category_info'] = {
        'display_name': category_info.display_name,
        'description': category_info.description,
        'is_permanent': category_info.is_permanent
    }
    
    return memory_data
