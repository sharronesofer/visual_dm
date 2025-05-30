import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Union
from dialogue.scoring import relevance_score
from dialogue.extractors import extract_key_info

# Utility for token counting (stub, replace with actual tokenizer as needed)
def count_tokens(text: str) -> int:
    return len(text.split())

class ConversationEntry:
    def __init__(self, speaker: str, message: str, timestamp: Optional[datetime] = None, metadata: Optional[Dict[str, Any]] = None):
        self.speaker = speaker
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'speaker': self.speaker,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ConversationEntry':
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
        """Add a new conversation entry and enforce window limits."""
        entry = ConversationEntry(speaker, message, metadata=metadata)
        self.entries.append(entry)
        self._enforce_limits()

    def _enforce_limits(self):
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
        Default is dialogue.extractors.extract_key_info.
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

    # Extension points for advanced features (summarization, DB persistence, etc.)

# Example usage:
# history = ConversationHistory()
# history.add_entry('user', 'Hello!')
# window = history.get_context_window(scoring_fn=relevance_score, by_tokens=True)
# history.extract_key_info() 
