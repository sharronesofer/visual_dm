"""
Dialogue System for Visual DM

This module provides a comprehensive system for managing conversation histories,
dialogue context, information extraction, and caching.
"""

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

__all__ = [
    'DialogueManager',
    'ConversationHistory',
    'ConversationEntry',
    'DialogueCache',
    'count_tokens',
    'relevance_score',
    'extract_key_info',
    'SCORING_WEIGHTS',
    'IMPORTANT_SPEAKERS',
    'KEYWORDS',
]
