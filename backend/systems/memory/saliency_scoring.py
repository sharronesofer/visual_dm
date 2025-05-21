"""
This module handles memory importance and saliency scoring.
It determines how significant memories are for an NPC's identity and decision-making.
"""

import re
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple

# Saliency scoring parameters
DEFAULT_BASE_DECAY_RATE = 0.05  # Default decay rate per day
DEFAULT_MEMORY_HALFLIFE = 30   # Default 30-day half-life for general memories
DEFAULT_MIN_IMPORTANCE = 0.2   # Minimum importance value for any memory
DEFAULT_MAX_IMPORTANCE = 0.95  # Maximum importance to prevent perfect 1.0

# Initial saliency scores for different memory types
INITIAL_SALIENCY = {
    "core": 0.9,          # Core identity memories
    "trauma": 0.85,       # Traumatic experiences
    "accomplishment": 0.8, # Major accomplishments
    "relationship": 0.75, # Important relationship events
    "regular": 0.6,       # Standard memories
    "mundane": 0.4,       # Everyday occurrences
}

# Half-life modifiers for different memory types (in days)
HALFLIFE_MODIFIERS = {
    "core": 3650,         # Core memories decay very slowly (10 years)
    "trauma": 1825,       # Trauma persists (5 years)
    "accomplishment": 365, # Accomplishments remembered for about a year
    "relationship": 180,  # Relationship events for ~6 months
    "regular": 30,        # Regular memories for a month
    "mundane": 7,         # Mundane memories forgotten quickly
}


def calculate_memory_saliency(
    memory: Dict[str, Any],
    current_time: Optional[datetime] = None
) -> float:
    """
    Calculate the current saliency (importance adjusted for recency) of a memory.
    
    Args:
        memory: The memory object to calculate saliency for
        current_time: Current time reference (defaults to now)
        
    Returns:
        Saliency score between 0.0 and 1.0
    """
    # Use current time if not provided
    if current_time is None:
        current_time = datetime.now()
    
    # Get memory creation time
    creation_time_str = memory.get("created_at", "")
    if not creation_time_str:
        return DEFAULT_MIN_IMPORTANCE
    
    try:
        creation_time = datetime.fromisoformat(creation_time_str)
    except (ValueError, TypeError):
        # If parsing fails, fall back to using current time (minimal decay)
        creation_time = current_time
    
    # Calculate age in days
    age_days = (current_time - creation_time).total_seconds() / (60 * 60 * 24)
    
    # Get base importance
    importance = memory.get("importance", 0.5)
    
    # Determine memory type for half-life calculation
    memory_type = memory.get("memory_type", "regular")
    categories = memory.get("categories", [])
    
    # Override memory type based on categories if present
    if "core" in categories:
        memory_type = "core"
    elif "trauma" in categories:
        memory_type = "trauma"
    elif "accomplishment" in categories:
        memory_type = "accomplishment"
    elif "relationship" in categories:
        memory_type = "relationship"
    elif memory_type == "regular" and "mundane" in categories:
        memory_type = "mundane"
    
    # Get half-life based on memory type
    halflife = HALFLIFE_MODIFIERS.get(memory_type, DEFAULT_MEMORY_HALFLIFE)
    
    # Calculate decay factor
    decay_rate = DEFAULT_BASE_DECAY_RATE
    decay_factor = math.exp(-decay_rate * age_days / halflife)
    
    # Calculate final saliency
    saliency = importance * decay_factor
    
    # Consider memory access count (boost saliency for frequently accessed memories)
    access_count = memory.get("access_count", 0)
    access_boost = min(0.2, 0.02 * access_count)  # Max 0.2 boost from access
    
    # Apply access boost
    saliency += access_boost
    
    # Ensure saliency stays within bounds
    return max(DEFAULT_MIN_IMPORTANCE, min(DEFAULT_MAX_IMPORTANCE, saliency))


def calculate_initial_importance(
    memory_content: str,
    memory_type: str = "regular",
    categories: List[str] = None
) -> float:
    """
    Calculate the initial importance of a memory based on content and type.
    
    Args:
        memory_content: The content of the memory
        memory_type: Type of memory (core, regular, etc.)
        categories: List of categories the memory belongs to
        
    Returns:
        Importance score between 0.0 and 1.0
    """
    if categories is None:
        categories = []
    
    # Start with base importance based on memory type
    base_importance = INITIAL_SALIENCY.get(memory_type, 0.6)
    
    # Adjust importance based on categories
    category_boost = 0.0
    high_importance_categories = ["trauma", "accomplishment", "identity", "relationship"]
    for category in categories:
        if category in high_importance_categories:
            category_boost += 0.05
    
    # Cap category boost at 0.2
    category_boost = min(0.2, category_boost)
    
    # Content-based analysis (simple keyword matching)
    content_importance = 0.0
    
    # Check for emotional content
    emotional_terms = [
        "love", "hate", "fear", "joy", "sadness", "anger", "grief", 
        "ecstatic", "devastated", "heartbroken", "elated", "terrified"
    ]
    if any(term in memory_content.lower() for term in emotional_terms):
        content_importance += 0.1
    
    # Check for life-changing events
    life_events = [
        "birth", "death", "marriage", "divorce", "promotion", "fired", 
        "graduated", "moved", "first", "last", "betrayed", "saved"
    ]
    if any(term in memory_content.lower() for term in life_events):
        content_importance += 0.15
    
    # Check for intensity indicators
    intensity_terms = [
        "never", "always", "forever", "extremely", "absolutely", 
        "completely", "utterly", "profoundly", "deeply"
    ]
    if any(term in memory_content.lower() for term in intensity_terms):
        content_importance += 0.05
    
    # Final importance calculation
    importance = base_importance + category_boost + content_importance
    
    # Ensure importance stays within bounds
    return max(DEFAULT_MIN_IMPORTANCE, min(DEFAULT_MAX_IMPORTANCE, importance))


def calculate_memory_relevance(
    query_context: str,
    memory_content: str,
    memory_categories: List[str] = None
) -> float:
    """
    Calculate the semantic relevance of a memory to the current context.
    
    Args:
        query_context: The current context or query
        memory_content: The content of the memory
        memory_categories: Categories the memory belongs to
        
    Returns:
        Relevance score between 0.0 and 1.0
    """
    if memory_categories is None:
        memory_categories = []
        
    # Simple keyword matching for relevance (in production, would use embeddings)
    query_words = set(re.findall(r'\b\w+\b', query_context.lower()))
    memory_words = set(re.findall(r'\b\w+\b', memory_content.lower()))
    
    # Calculate word overlap
    if not query_words:
        return 0.5  # Default mid-relevance for empty queries
    
    word_overlap = len(query_words.intersection(memory_words)) / len(query_words)
    
    # Add category relevance
    category_terms = []
    for category in memory_categories:
        category_terms.extend(category.split('_'))
    
    category_overlap = 0.0
    if category_terms:
        category_matches = sum(1 for word in query_words if word in category_terms)
        category_overlap = category_matches / len(category_terms)
    
    # Combine scores with weights
    relevance = (word_overlap * 0.7) + (category_overlap * 0.3)
    
    # Ensure relevance stays within bounds
    return max(0.0, min(1.0, relevance))


def rank_memories_by_relevance(
    query_context: str,
    memories: List[Dict[str, Any]],
    consider_saliency: bool = True
) -> List[Tuple[Dict[str, Any], float]]:
    """
    Rank memories by their relevance to the current context.
    
    Args:
        query_context: The current context or query
        memories: List of memories to rank
        consider_saliency: Whether to consider memory saliency in ranking
        
    Returns:
        List of (memory, score) tuples, sorted by decreasing relevance
    """
    ranked_memories = []
    
    for memory in memories:
        content = memory.get("content", "")
        categories = memory.get("categories", [])
        
        # Calculate base relevance
        relevance = calculate_memory_relevance(query_context, content, categories)
        
        # Adjust score with saliency if requested
        if consider_saliency:
            saliency = calculate_memory_saliency(memory)
            # Combined score with more weight on relevance
            score = (relevance * 0.7) + (saliency * 0.3)
        else:
            score = relevance
        
        ranked_memories.append((memory, score))
    
    # Sort by score in descending order
    return sorted(ranked_memories, key=lambda x: x[1], reverse=True) 