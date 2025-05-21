"""
Utility functions for the dialogue system.

This module provides utility functions for token counting, 
relevance scoring, and information extraction.
"""

import re
from datetime import datetime
from typing import List, Dict, Any


# ============================
# Token Utilities
# ============================

def count_tokens(text: str) -> int:
    """
    Count tokens in a text string.
    This is a simple implementation - replace with more accurate tokenizer as needed.
    """
    return len(text.split())


# ============================
# Scoring System
# ============================

# Configuration for scoring weights
SCORING_WEIGHTS = {
    'recency': 0.5,
    'speaker_importance': 0.3,
    'keyword_match': 0.2
}

# Important speakers and keywords for scoring
IMPORTANT_SPEAKERS = {'user', 'npc_important'}
KEYWORDS = {'quest', 'danger', 'reward', 'secret'}


def relevance_score(entry, now: datetime = None, weights: Dict[str, float] = None) -> float:
    """
    Compute a relevance score for a ConversationEntry.
    - Recency: newer messages score higher
    - Speaker importance: certain speakers are prioritized
    - Keyword match: messages containing important keywords score higher
    
    Args:
        entry: The conversation entry to score
        now: Current time for recency calculation (default: current UTC time)
        weights: Dictionary of scoring weights (default: SCORING_WEIGHTS)
        
    Returns:
        float: A relevance score between 0.0 and 1.0
    """
    if weights is None:
        weights = SCORING_WEIGHTS
    if now is None:
        now = datetime.utcnow()

    # Recency: exponential decay based on age (in seconds)
    age_seconds = (now - entry.timestamp).total_seconds()
    recency_score = 1.0 / (1.0 + age_seconds / 3600.0)  # 1 for now, decays over hours

    # Speaker importance
    speaker_score = 1.0 if entry.speaker in IMPORTANT_SPEAKERS else 0.0

    # Keyword match
    keyword_score = 0.0
    for kw in KEYWORDS:
        if kw in entry.message.lower():
            keyword_score = 1.0
            break

    # Weighted sum
    score = (
        weights['recency'] * recency_score +
        weights['speaker_importance'] * speaker_score +
        weights['keyword_match'] * keyword_score
    )
    return score


# ============================
# Information Extraction
# ============================

def extract_key_info(message: str) -> List[Dict[str, Any]]:
    """
    Extract key information from a message using regex and rule-based patterns.
    Returns a list of extracted entities/facts/decisions.
    
    Args:
        message: The text message to extract information from
        
    Returns:
        List of extracted information as dictionaries with 'type' and 'value' keys
    """
    results = []
    
    # Extract quest names
    quest_match = re.search(r'quest\s*[:=]?\s*([\w\s]+)', message, re.IGNORECASE)
    if quest_match:
        results.append({'type': 'quest', 'value': quest_match.group(1).strip()})
    
    # Extract rewards
    reward_match = re.search(r'reward\s*[:=]?\s*([\w\s]+)', message, re.IGNORECASE)
    if reward_match:
        results.append({'type': 'reward', 'value': reward_match.group(1).strip()})
    
    # Extract decisions (yes/no)
    if re.search(r'\byes\b', message, re.IGNORECASE):
        results.append({'type': 'decision', 'value': 'yes'})
    if re.search(r'\bno\b', message, re.IGNORECASE):
        results.append({'type': 'decision', 'value': 'no'})
    
    # Extract locations
    location_match = re.search(r'location\s*[:=]?\s*([\w\s]+)', message, re.IGNORECASE)
    if location_match:
        results.append({'type': 'location', 'value': location_match.group(1).strip()})
    
    # Extract items/objects
    item_match = re.search(r'item\s*[:=]?\s*([\w\s]+)', message, re.IGNORECASE)
    if item_match:
        results.append({'type': 'item', 'value': item_match.group(1).strip()})
    
    return results 