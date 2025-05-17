from typing import TypedDict, Literal, Optional, Dict, Any
from datetime import datetime

# Define the dialogue role types
DialogueRole = Literal['user', 'system', 'assistant', 'npc']

class ConversationTurn(TypedDict):
    """Represents a single turn in a conversation with role, content, and timestamp."""
    role: DialogueRole
    content: str
    timestamp: Optional[int]  # Unix timestamp in milliseconds

class DialogueMetadata(TypedDict):
    """Metadata about a dialogue generation, including tokens and timing."""
    tokensUsed: int
    responseTimeMs: int
    model: str
    # Allow for additional fields
    additional: Dict[str, Any] 