import time
from typing import List, Dict, Any, Optional, Protocol, TypedDict, Union
import asyncio
import logging
from pyee import EventEmitter
from .types import ConversationTurn, DialogueRole
from .gpt_client import GPTClient

logger = logging.getLogger(__name__)

class ContextManagerConfig(TypedDict, total=False):
    """Configuration for the conversation context manager."""
    maxTokens: Optional[int]
    maxTurns: Optional[int]
    relevanceWeights: Optional[Dict[str, float]]
    storageBackend: Optional['ContextStorageBackend']

class ContextStorageBackend(Protocol):
    """Protocol for conversation storage backends."""
    async def save(self, turns: List[ConversationTurn]) -> None:
        """Save turns to the storage backend."""
        ...
    
    async def load(self) -> List[ConversationTurn]:
        """Load turns from the storage backend."""
        ...

class InMemoryContextStorage:
    """Default in-memory storage backend (no-op for persistence)."""
    def __init__(self):
        self.turns: List[ConversationTurn] = []
    
    async def save(self, turns: List[ConversationTurn]) -> None:
        """Save turns to in-memory storage."""
        self.turns = turns.copy()
    
    async def load(self) -> List[ConversationTurn]:
        """Load turns from in-memory storage."""
        return self.turns.copy()

class ConversationContextManager(EventEmitter):
    """
    Manages conversation history, context windowing, relevance scoring, 
    extraction, and persistence for GPT dialogue.
    Emits 'contextUpdated', 'contextSaved', and 'contextLoaded' events.
    """
    
    def __init__(self, config: Optional[ContextManagerConfig] = None):
        """Initialize the context manager with configuration."""
        super().__init__()
        
        if config is None:
            config = {}
        
        # Set up configuration with defaults
        self.config = {
            'maxTokens': config.get('maxTokens', 1024),
            'maxTurns': config.get('maxTurns', 10),
            'relevanceWeights': config.get('relevanceWeights', {'recency': 1, 'semantic': 1, 'interaction': 1}),
            'storageBackend': config.get('storageBackend', InMemoryContextStorage())
        }
        
        self.turns: List[ConversationTurn] = []
        self.storage = self.config['storageBackend']
    
    def add_turn(self, role: DialogueRole, content: str) -> None:
        """
        Adds a new conversation turn and emits 'contextUpdated'.
        
        Args:
            role: The role of the speaker (user, system, assistant, npc)
            content: The content of the turn
        """
        self.turns.append({
            'role': role,
            'content': content,
            'timestamp': int(time.time() * 1000)
        })
        self.emit('contextUpdated', self.turns)
    
    def get_context(self, max_tokens: Optional[int] = None) -> List[str]:
        """
        Returns the most recent context as an array of strings, fitting within maxTokens.
        
        Args:
            max_tokens: Maximum number of tokens to include (default from config)
            
        Returns:
            List of context strings
        """
        if max_tokens is None:
            max_tokens = self.config['maxTokens']
            
        context: List[str] = []
        tokens = 0
        
        # Process turns from newest to oldest
        for turn in reversed(self.turns):
            turn_tokens = GPTClient.count_tokens(turn['content'])
            if tokens + turn_tokens > max_tokens:
                break
                
            # Add to beginning (maintain chronological order)
            context.insert(0, turn['content'])
            tokens += turn_tokens
            
        return context
    
    def get_context_by_turns(self, max_turns: Optional[int] = None) -> List[str]:
        """
        Returns the last N turns as context.
        
        Args:
            max_turns: Maximum number of turns to include (default from config)
            
        Returns:
            List of context strings from the last N turns
        """
        if max_turns is None:
            max_turns = self.config['maxTurns']
            
        return [turn['content'] for turn in self.turns[-max_turns:]]
    
    def clear_context(self) -> None:
        """Clears the conversation history and emits 'contextUpdated'."""
        self.turns = []
        self.emit('contextUpdated', self.turns)
    
    def score_relevance(self, turn: ConversationTurn, now: Optional[int] = None) -> float:
        """
        Calculates a relevance score for a turn (recency, semantic, interaction).
        
        Args:
            turn: The turn to score
            now: Current timestamp (default is current time)
            
        Returns:
            A relevance score (higher is more relevant)
        """
        if now is None:
            now = int(time.time() * 1000)
            
        # Recency: newer turns are more relevant
        timestamp = turn.get('timestamp', now)
        recency_score = 1 / (1 + (now - timestamp) / 60000)
        
        # TODO: Add semantic similarity (e.g., embedding distance)
        semantic_score = 1  # Placeholder
        
        # TODO: Add interaction type weighting
        interaction_score = 1  # Placeholder
        
        # Apply weights from config
        weights = self.config['relevanceWeights']
        return (
            weights['recency'] * recency_score +
            weights['semantic'] * semantic_score +
            weights['interaction'] * interaction_score
        )
    
    def extract_key_information(self) -> List[str]:
        """
        Extracts key information (entities, facts, goals) from the conversation.
        
        Returns:
            List of extracted information strings
        """
        # Placeholder: return all user turns for now
        # TODO: Add entity/fact extraction using NLP or plugins
        return [turn['content'] for turn in self.turns if turn['role'] == 'user']
    
    def get_all_turns(self) -> List[ConversationTurn]:
        """
        Returns all turns (for debugging/testing).
        
        Returns:
            Copy of all conversation turns
        """
        return self.turns.copy()
    
    async def save_context(self) -> None:
        """Saves the current context using the configured storage backend. Emits 'contextSaved'."""
        await self.storage.save(self.turns)
        self.emit('contextSaved', self.turns)
    
    async def load_context(self) -> None:
        """Loads context from the configured storage backend. Emits 'contextLoaded'."""
        loaded = await self.storage.load()
        self.turns = loaded.copy()
        self.emit('contextLoaded', self.turns) 