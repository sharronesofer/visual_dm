"""
DEPRECATED: This module has been refactored into multiple modules for better maintainability.

Please use the following imports instead:
- from backend.systems.dialogue.dialogue_manager import DialogueManager 
- from backend.systems.dialogue.conversation import ConversationHistory, ConversationEntry
- from backend.systems.dialogue.cache import DialogueCache
- from backend.systems.dialogue.utils import count_tokens, relevance_score, extract_key_info

See the respective modules for more details.
"""

# Re-export symbols for backward compatibility 
# but issue a deprecation warning when imported

import warnings
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Union

from backend.systems.dialogue.dialogue_manager import DialogueManager
from backend.systems.dialogue.conversation import ConversationHistory, ConversationEntry
from backend.systems.dialogue.cache import DialogueCache
from backend.systems.dialogue.utils import (
    count_tokens,
    relevance_score,
    extract_key_info,
    SCORING_WEIGHTS,
    IMPORTANT_SPEAKERS,
    KEYWORDS,
)

warnings.warn(
    "The dialogue_system module is deprecated. Please import directly from "
    "backend.systems.dialogue.dialogue_manager, conversation, cache, or utils modules.",
    DeprecationWarning,
    stacklevel=2
)

# The rest of this file is kept for backward compatibility but is deprecated
# Please use the modularized version instead

# Original code follows - DEPRECATED

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


# ============================
# Caching System
# ============================

class DialogueCache:
    """
    Cache for dialogue data to improve performance and reduce redundant processing.
    """
    def __init__(self):
        self.response_cache = {}
        self.context_cache = {}
        self.extraction_cache = {}
    
    def get_cached_response(self, key: str) -> Optional[str]:
        """Get a cached response if available."""
        return self.response_cache.get(key)
    
    def cache_response(self, key: str, response: str):
        """Cache a response for future use."""
        self.response_cache[key] = response
    
    def clear(self):
        """Clear all caches."""
        self.response_cache.clear()
        self.context_cache.clear()
        self.extraction_cache.clear()


# ============================
# Conversation Context Management
# ============================

class ConversationEntry:
    """
    Represents a single entry in a conversation history.
    """
    def __init__(self, speaker: str, message: str, timestamp: Optional[datetime] = None, metadata: Optional[Dict[str, Any]] = None):
        self.speaker = speaker
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for serialization."""
        return {
            'speaker': self.speaker,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ConversationEntry':
        """Create an entry from a dictionary."""
        return ConversationEntry(
            speaker=data['speaker'],
            message=data['message'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )


class ConversationHistory:
    """
    Manages conversation history, context windowing (by message or token count),
    relevance scoring, and key information extraction for dialogue systems.
    """
    def __init__(self, max_tokens: int = 2048, max_messages: int = 50):
        self.entries: List[ConversationEntry] = []
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.extracted_info: List[Dict[str, Any]] = []

    def add_entry(self, speaker: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a new conversation entry and enforce window limits.
        
        Args:
            speaker: ID or name of the entity speaking
            message: The content of the message
            metadata: Optional metadata about the conversation entry
        """
        entry = ConversationEntry(speaker, message, metadata=metadata)
        self.entries.append(entry)
        self._enforce_limits()

    def _enforce_limits(self):
        """Enforce message count and token count limits."""
        # Enforce message count limit
        if len(self.entries) > self.max_messages:
            self.entries = self.entries[-self.max_messages:]
        
        # Enforce token limit (approximate)
        total_tokens = 0
        limited_entries = []
        for entry in reversed(self.entries):
            tokens = count_tokens(entry.message)
            if total_tokens + tokens > self.max_tokens:
                break
            limited_entries.insert(0, entry)
            total_tokens += tokens
        self.entries = limited_entries

    def get_context_window(self, scoring_fn: Optional[Callable[[ConversationEntry], float]] = None, by_tokens: bool = False) -> List[ConversationEntry]:
        """
        Return the current context window, optionally sorted by relevance.
        If by_tokens is True, limit by token count; otherwise by message count.
        
        Args:
            scoring_fn: Optional function to score and sort entries by relevance
            by_tokens: If True, limit by token count; otherwise by message count
            
        Returns:
            List of conversation entries within the context window
        """
        entries = self.entries
        if scoring_fn:
            entries = sorted(entries, key=scoring_fn, reverse=True)
        
        if by_tokens:
            total_tokens = 0
            window = []
            for entry in entries:
                tokens = count_tokens(entry.message)
                if total_tokens + tokens > self.max_tokens:
                    break
                window.append(entry)
                total_tokens += tokens
            return window
        else:
            return entries[-self.max_messages:]

    def extract_key_info(self, extractor_fn: Optional[Callable[[str], List[Dict[str, Any]]]] = None):
        """
        Extract key information from all entries using the provided extractor function.
        Default is extract_key_info from this module.
        
        Args:
            extractor_fn: Optional custom extractor function
        """
        extractor = extractor_fn or extract_key_info
        for entry in self.entries:
            info = extractor(entry.message)
            self.extracted_info.extend(info)

    def to_json(self) -> str:
        """Serialize conversation history to JSON."""
        return json.dumps([e.to_dict() for e in self.entries])

    @staticmethod
    def from_json(data: str) -> 'ConversationHistory':
        """Create a conversation history from JSON string."""
        entries = json.loads(data)
        history = ConversationHistory()
        history.entries = [ConversationEntry.from_dict(e) for e in entries]
        return history

    def save(self, filepath: str):
        """Save conversation history to a file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())

    @staticmethod
    def load(filepath: str) -> 'ConversationHistory':
        """Load conversation history from a file."""
        with open(filepath, 'r') as f:
            data = f.read()
        return ConversationHistory.from_json(data)


# ============================
# Main Dialogue Manager
# ============================

class DialogueManager:
    """
    Central manager for all dialogue-related functionality.
    Provides a unified interface to conversation history, scoring, extraction, and caching.
    """
    
    def __init__(self, max_tokens: int = 2048, max_messages: int = 50):
        self.history = ConversationHistory(max_tokens=max_tokens, max_messages=max_messages)
        self.cache = DialogueCache()
        
    def add_message(self, speaker: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the conversation history."""
        self.history.add_entry(speaker, message, metadata=metadata)
        
    def get_context(self, use_scoring: bool = True, by_tokens: bool = True) -> List[Dict[str, Any]]:
        """
        Get the current context window as a list of dictionaries.
        
        Args:
            use_scoring: If True, use relevance_score to prioritize entries
            by_tokens: If True, limit by token count; otherwise by message count
            
        Returns:
            List of conversation entries as dictionaries
        """
        scoring_fn = relevance_score if use_scoring else None
        entries = self.history.get_context_window(scoring_fn=scoring_fn, by_tokens=by_tokens)
        return [e.to_dict() for e in entries]
        
    def extract_information(self) -> List[Dict[str, Any]]:
        """Extract key information from the conversation history."""
        self.history.extract_key_info()
        return self.history.extracted_info
        
    def save_history(self, filepath: str):
        """Save the conversation history to a file."""
        self.history.save(filepath)
        
    def load_history(self, filepath: str):
        """Load conversation history from a file."""
        self.history = ConversationHistory.load(filepath)
        
    def clear_cache(self):
        """Clear all caches."""
        self.cache.clear()


# Example usage:
# manager = DialogueManager()
# manager.add_message('player', 'Hello there!')
# manager.add_message('npc', 'Greetings, traveler! Can I interest you in a quest?')
# context = manager.get_context()
# info = manager.extract_information() 