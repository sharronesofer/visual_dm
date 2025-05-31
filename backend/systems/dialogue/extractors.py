"""
Dialogue Extractors Module

This module provides functions for extracting key information from dialogue text.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime


def extract_key_info(text: str) -> List[Dict[str, Any]]:
    """
    Extract key information from dialogue text.
    
    Args:
        text: The dialogue text to analyze
        
    Returns:
        List of dictionaries containing extracted information
    """
    extracted_info = []
    
    # Extract names (capitalized words that might be names)
    names = re.findall(r'\b[A-Z][a-z]+\b', text)
    if names:
        extracted_info.append({
            'type': 'names',
            'content': list(set(names)),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Extract locations (words after "in", "at", "to", etc.)
    location_patterns = [
        r'\b(?:in|at|to|from|near)\s+([A-Z][a-zA-Z\s]+?)(?:\s|$|[,.!?])',
        r'\b([A-Z][a-zA-Z\s]*(?:City|Town|Village|Castle|Keep|Tower|Forest|Mountain|River|Lake))\b'
    ]
    locations = []
    for pattern in location_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        locations.extend(matches)
    
    if locations:
        extracted_info.append({
            'type': 'locations',
            'content': list(set(locations)),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Extract emotions/sentiments (basic keywords)
    emotion_keywords = [
        'happy', 'sad', 'angry', 'excited', 'worried', 'afraid', 'confident',
        'nervous', 'surprised', 'disappointed', 'grateful', 'frustrated'
    ]
    emotions = []
    for emotion in emotion_keywords:
        if re.search(r'\b' + emotion + r'\b', text, re.IGNORECASE):
            emotions.append(emotion)
    
    if emotions:
        extracted_info.append({
            'type': 'emotions',
            'content': emotions,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Extract actions (verbs in past tense or present)
    action_patterns = [
        r'\b(\w+ed)\b',  # Past tense verbs
        r'\b(go|goes|went|come|comes|came|take|takes|took|give|gives|gave|see|sees|saw|say|says|said)\b'
    ]
    actions = []
    for pattern in action_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        actions.extend(matches)
    
    if actions:
        extracted_info.append({
            'type': 'actions',
            'content': list(set(actions)),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Extract objects/items (nouns that might be items)
    item_keywords = [
        'sword', 'shield', 'armor', 'potion', 'scroll', 'book', 'key', 'coin',
        'gold', 'silver', 'gem', 'ring', 'amulet', 'staff', 'wand', 'bow',
        'arrow', 'dagger', 'helmet', 'boots', 'cloak', 'bag', 'chest'
    ]
    items = []
    for item in item_keywords:
        if re.search(r'\b' + item + r's?\b', text, re.IGNORECASE):
            items.append(item)
    
    if items:
        extracted_info.append({
            'type': 'items',
            'content': items,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return extracted_info


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities from text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary with entity types as keys and lists of entities as values
    """
    entities = {
        'persons': [],
        'locations': [],
        'organizations': [],
        'items': []
    }
    
    # Simple pattern-based extraction
    # In a real implementation, you might use spaCy or similar NLP library
    
    # Extract person names (capitalized words)
    person_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    entities['persons'] = list(set(person_names))
    
    # Extract locations
    location_patterns = [
        r'\b([A-Z][a-zA-Z\s]*(?:City|Town|Village|Castle|Keep|Tower|Forest|Mountain|River|Lake))\b',
        r'\bthe\s+([A-Z][a-zA-Z\s]+?)(?:\s|$|[,.!?])'
    ]
    for pattern in location_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities['locations'].extend(matches)
    
    entities['locations'] = list(set(entities['locations']))
    
    return entities


def extract_dialogue_metadata(text: str) -> Dict[str, Any]:
    """
    Extract metadata from dialogue text.
    
    Args:
        text: The dialogue text
        
    Returns:
        Dictionary containing metadata about the dialogue
    """
    metadata = {
        'word_count': len(text.split()),
        'character_count': len(text),
        'sentence_count': len(re.findall(r'[.!?]+', text)),
        'question_count': text.count('?'),
        'exclamation_count': text.count('!'),
        'has_quotes': '"' in text or "'" in text,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return metadata


def extract_conversation_turns(text: str) -> List[Dict[str, str]]:
    """
    Extract conversation turns from formatted dialogue text.
    
    Args:
        text: Dialogue text with speaker indicators
        
    Returns:
        List of conversation turns with speaker and content
    """
    turns = []
    
    # Pattern for "Speaker: Content" format
    pattern = r'^([A-Za-z\s]+):\s*(.+)$'
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = re.match(pattern, line)
        if match:
            speaker = match.group(1).strip()
            content = match.group(2).strip()
            turns.append({
                'speaker': speaker,
                'content': content,
                'timestamp': datetime.utcnow().isoformat()
            })
    
    return turns 