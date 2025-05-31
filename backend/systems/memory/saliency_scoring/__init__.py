"""Saliency_Scoring for memory system"""

from typing import Any, Dict, Optional
from backend.systems.memory.utils.saliency_scoring import calculate_memory_saliency

def calculate_initial_importance(memory_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> float:
    """
    Calculate the initial importance score for a memory.
    
    Args:
        memory_data: The memory data to score
        context: Optional context for scoring
        
    Returns:
        A score between 0.0 and 1.0 indicating importance
    """
    # Basic importance calculation logic
    base_score = 0.5
    
    # Adjust based on memory type
    if memory_data.get('type') == 'critical':
        base_score += 0.3
    elif memory_data.get('type') == 'mundane':
        base_score -= 0.2
    
    # Adjust based on emotional intensity
    emotional_intensity = memory_data.get('emotional_intensity', 0.0)
    base_score += emotional_intensity * 0.2
    
    # Ensure score is within bounds
    return max(0.0, min(1.0, base_score))

__all__ = ['calculate_initial_importance', 'calculate_memory_saliency']

