"""
Main dialogue manager module.

This module provides the central DialogueManager class that 
coordinates all dialogue-related functionality.
"""

from typing import List, Dict, Any, Optional

from backend.systems.dialogue.conversation import ConversationHistory
from backend.systems.dialogue.cache import DialogueCache
from backend.systems.dialogue.utils import relevance_score


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
        # Clear cached context since it's now changed
        self.cache.context_cache.clear()
        
    def get_context(self, use_scoring: bool = True, by_tokens: bool = True) -> List[Dict[str, Any]]:
        """
        Get the current context window as a list of dictionaries.
        
        Args:
            use_scoring: If True, use relevance_score to prioritize entries
            by_tokens: If True, limit by token count; otherwise by message count
            
        Returns:
            List of conversation entries as dictionaries
        """
        # Generate a cache key based on parameters
        cache_key = f"context_{use_scoring}_{by_tokens}"
        
        # Check if we have this context cached
        cached_context = self.cache.get_cached_context(cache_key)
        if cached_context:
            return cached_context
        
        # Generate the context
        scoring_fn = relevance_score if use_scoring else None
        entries = self.history.get_context_window(scoring_fn=scoring_fn, by_tokens=by_tokens)
        context = [e.to_dict() for e in entries]
        
        # Cache and return the context
        self.cache.cache_context(cache_key, context)
        return context
        
    def extract_information(self) -> List[Dict[str, Any]]:
        """Extract key information from the conversation history."""
        # Check if we have cached information
        cache_key = "extraction"
        cached_extraction = self.cache.get_cached_extraction(cache_key)
        if cached_extraction:
            return cached_extraction
            
        # Extract information
        self.history.extract_key_info()
        
        # Cache and return the information
        self.cache.cache_extraction(cache_key, self.history.extracted_info)
        return self.history.extracted_info
        
    def save_history(self, filepath: str):
        """Save the conversation history to a file."""
        self.history.save(filepath)
        
    def load_history(self, filepath: str):
        """Load conversation history from a file."""
        self.history = ConversationHistory.load(filepath)
        # Clear cache since history has changed
        self.clear_cache()
        
    def clear_cache(self):
        """Clear all caches."""
        self.cache.clear() 