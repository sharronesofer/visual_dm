"""
Memory Saliency Scoring System.

This module provides functions to calculate and manage memory importance
and saliency scores based on various factors.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from backend.systems.memory.memory_categories import MemoryCategory, get_category_info


def calculate_initial_importance(
    memory_content: str,
    memory_type: str = "regular",
    categories: Optional[List[str]] = None
) -> float:
    """
    Calculate the initial importance score for a new memory.
    
    Args:
        memory_content: The text content of the memory
        memory_type: Type of memory ('core' or 'regular')
        categories: List of memory categories
        
    Returns:
        Initial importance score between 0.0 and 1.0
    """
    # Base importance
    if memory_type == "core":
        base_importance = 1.0
    else:
        base_importance = 0.5
    
    # Content-based modifiers
    content_lower = memory_content.lower()
    content_modifiers = 0.0
    
    # Emotional intensity keywords increase importance
    emotional_keywords = ['love', 'hate', 'fear', 'joy', 'anger', 'surprise', 'disgust', 'trust']
    emotional_count = sum(1 for word in emotional_keywords if word in content_lower)
    content_modifiers += emotional_count * 0.1
    
    # Action keywords increase importance
    action_keywords = ['killed', 'died', 'betrayed', 'saved', 'discovered', 'learned', 'achieved']
    action_count = sum(1 for word in action_keywords if word in content_lower)
    content_modifiers += action_count * 0.15
    
    # Length modifier (longer memories might be more detailed/important)
    length_modifier = min(len(memory_content) / 1000, 0.2)
    
    # Category-based modifiers
    category_modifier = 0.0
    if categories:
        for cat_str in categories:
            try:
                category = MemoryCategory(cat_str)
                cat_info = get_category_info(category)
                category_modifier = max(category_modifier, cat_info.default_importance - 0.5)
            except (ValueError, KeyError):
                continue
    
    # Combine all factors
    final_importance = base_importance + content_modifiers + length_modifier + category_modifier
    
    # Clamp to valid range
    return max(0.0, min(1.0, final_importance))


def calculate_memory_saliency(memory_data: Dict[str, Any]) -> float:
    """
    Calculate the current saliency (relevance) score of a memory.
    
    Args:
        memory_data: Dictionary containing memory information
        
    Returns:
        Current saliency score between 0.0 and 1.0
    """
    # Base importance
    importance = memory_data.get('importance', 0.5)
    
    # Time decay factor
    created_at = memory_data.get('created_at')
    if created_at:
        try:
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_diff = datetime.now() - created_time.replace(tzinfo=None)
            days_old = time_diff.total_seconds() / (24 * 3600)
            
            # Decay modifier from category
            decay_modifier = memory_data.get('decay_modifier', 1.0)
            
            # Calculate decay (exponential decay)
            if memory_data.get('memory_type') == 'core' or memory_data.get('is_permanent'):
                time_decay = 1.0  # Core memories don't decay
            else:
                time_decay = math.exp(-days_old * 0.1 * decay_modifier)
        except (ValueError, TypeError):
            time_decay = 1.0
    else:
        time_decay = 1.0
    
    # Access frequency boost
    access_count = memory_data.get('access_count', 0)
    access_boost = min(access_count * 0.05, 0.3)  # Cap at 0.3
    
    # Recent access boost
    last_accessed = memory_data.get('last_accessed')
    recent_access_boost = 0.0
    if last_accessed:
        try:
            last_access_time = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
            hours_since_access = (datetime.now() - last_access_time.replace(tzinfo=None)).total_seconds() / 3600
            if hours_since_access < 24:
                recent_access_boost = 0.2 * (1 - hours_since_access / 24)
        except (ValueError, TypeError):
            pass
    
    # Calculate final saliency
    saliency = importance * time_decay + access_boost + recent_access_boost
    
    # Clamp to valid range
    return max(0.0, min(1.0, saliency))


def calculate_memory_relevance(memory_data: Dict[str, Any], context: str) -> float:
    """
    Calculate how relevant a memory is to a given context.
    
    Args:
        memory_data: Dictionary containing memory information
        context: The context to evaluate relevance against
        
    Returns:
        Relevance score between 0.0 and 1.0
    """
    content = memory_data.get('content', '').lower()
    context_lower = context.lower()
    
    # Simple keyword matching (could be enhanced with semantic similarity)
    context_words = set(context_lower.split())
    content_words = set(content.split())
    
    # Calculate word overlap
    common_words = context_words.intersection(content_words)
    if not context_words:
        return 0.0
    
    word_overlap = len(common_words) / len(context_words)
    
    # Category relevance
    categories = memory_data.get('categories', [])
    category_boost = 0.0
    
    # Boost for certain categories based on context
    if 'combat' in context_lower and any(cat in ['trauma', 'skill', 'achievement'] for cat in categories):
        category_boost += 0.2
    elif 'conversation' in context_lower and any(cat in ['conversation', 'relationship'] for cat in categories):
        category_boost += 0.2
    elif 'location' in context_lower and 'location' in categories:
        category_boost += 0.2
    
    # Base saliency influences relevance
    base_saliency = calculate_memory_saliency(memory_data)
    
    # Combine factors
    relevance = (word_overlap * 0.6) + (category_boost * 0.2) + (base_saliency * 0.2)
    
    return max(0.0, min(1.0, relevance))


def update_memory_importance(memory_data: Dict[str, Any], importance_delta: float) -> Dict[str, Any]:
    """
    Update a memory's importance score.
    
    Args:
        memory_data: Dictionary containing memory information
        importance_delta: Change in importance (can be positive or negative)
        
    Returns:
        Updated memory data
    """
    current_importance = memory_data.get('importance', 0.5)
    new_importance = current_importance + importance_delta
    
    # Clamp to valid range
    memory_data['importance'] = max(0.0, min(1.0, new_importance))
    
    # Update metadata
    if 'metadata' not in memory_data:
        memory_data['metadata'] = {}
    
    if 'importance_updates' not in memory_data['metadata']:
        memory_data['metadata']['importance_updates'] = []
    
    memory_data['metadata']['importance_updates'].append({
        'timestamp': datetime.now().isoformat(),
        'delta': importance_delta,
        'new_value': memory_data['importance']
    })
    
    return memory_data


def get_memory_decay_rate(memory_data: Dict[str, Any]) -> float:
    """
    Get the decay rate for a memory based on its properties.
    
    Args:
        memory_data: Dictionary containing memory information
        
    Returns:
        Decay rate (higher = faster decay)
    """
    # Core memories don't decay
    if memory_data.get('memory_type') == 'core' or memory_data.get('is_permanent'):
        return 0.0
    
    # Base decay rate
    base_decay = 0.1
    
    # Category-specific modifier
    decay_modifier = memory_data.get('decay_modifier', 1.0)
    
    # Importance affects decay (more important = slower decay)
    importance = memory_data.get('importance', 0.5)
    importance_factor = 1.0 - (importance * 0.5)
    
    # Access frequency affects decay (more accessed = slower decay)
    access_count = memory_data.get('access_count', 0)
    access_factor = 1.0 / (1.0 + access_count * 0.1)
    
    return base_decay * decay_modifier * importance_factor * access_factor


def should_memory_expire(memory_data: Dict[str, Any], threshold: float = 0.1) -> bool:
    """
    Determine if a memory should be expired based on its saliency.
    
    Args:
        memory_data: Dictionary containing memory information
        threshold: Minimum saliency to keep memory (default 0.1)
        
    Returns:
        True if memory should be expired
    """
    # Core memories never expire
    if memory_data.get('memory_type') == 'core' or memory_data.get('is_permanent'):
        return False
    
    # Check current saliency
    current_saliency = calculate_memory_saliency(memory_data)
    
    return current_saliency < threshold
