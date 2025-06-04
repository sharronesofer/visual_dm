"""
Text processing utilities for dialogue systems.

This module provides utility functions for text processing, token counting,
and information extraction used by the dialogue system.
"""

import re
from typing import List, Dict, Any


def count_tokens(text: str) -> int:
    """
    Count approximate tokens in text.
    
    This is a simple approximation that counts words and punctuation.
    For more accurate token counting, integrate with a proper tokenizer.
    
    Args:
        text: Input text to count tokens for
        
    Returns:
        Approximate token count
    """
    if not text:
        return 0
    
    # Simple approximation: split on whitespace and count
    # This is a rough estimate - real tokenizers are more sophisticated
    words = text.split()
    
    # Add extra tokens for punctuation
    punctuation_count = len(re.findall(r'[.!?;:,]', text))
    
    return len(words) + punctuation_count


def extract_key_info(text: str) -> List[Dict[str, Any]]:
    """
    Extract key information from dialogue text.
    
    This is a basic implementation that extracts simple patterns.
    For more sophisticated extraction, integrate with NLP libraries.
    
    Args:
        text: Input text to extract information from
        
    Returns:
        List of extracted information dictionaries
    """
    if not text:
        return []
    
    extracted = []
    
    # Extract mentions of names (capitalized words)
    names = re.findall(r'\b[A-Z][a-z]+\b', text)
    for name in names:
        extracted.append({
            'type': 'name',
            'value': name,
            'context': text
        })
    
    # Extract locations (words after "in", "at", "to")
    locations = re.findall(r'\b(?:in|at|to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
    for location in locations:
        extracted.append({
            'type': 'location',
            'value': location,
            'context': text
        })
    
    # Extract emotions/feelings (basic sentiment words)
    emotions = re.findall(r'\b(happy|sad|angry|excited|worried|afraid|confused|surprised)\b', text.lower())
    for emotion in emotions:
        extracted.append({
            'type': 'emotion',
            'value': emotion,
            'context': text
        })
    
    return extracted


def format_dialogue_response(response: str, speaker: str = None) -> str:
    """
    Format a dialogue response with proper speaker attribution.
    
    Args:
        response: The dialogue response text
        speaker: Optional speaker name/ID
        
    Returns:
        Formatted dialogue response
    """
    if not response:
        return ""
    
    if speaker:
        return f"{speaker}: {response}"
    else:
        return response


def validate_conversation_data(data: Dict[str, Any]) -> bool:
    """
    Validate conversation data structure.
    
    Args:
        data: Conversation data to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    required_fields = ['conversation_id', 'participants']
    for field in required_fields:
        if field not in data:
            return False
    
    # Validate participants is a list or dict
    participants = data['participants']
    if not isinstance(participants, (list, dict)):
        return False
    
    return True 