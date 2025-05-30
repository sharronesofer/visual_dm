# Dialogue System

## Overview
This module implements the dialogue system for Visual DM, providing conversation context management, relevance scoring, information extraction, and dialogue caching. The system is designed to be flexible, extensible, and easy to integrate with other game systems.

## Architecture
The dialogue system has been modularized for improved maintainability:

- **dialogue_manager.py**: Central manager class that coordinates all dialogue functionality
  - `DialogueManager`: Main entry point for all dialogue operations
  
- **conversation.py**: Conversation history and entry management
  - `ConversationHistory`: Manages dialogue history with context windows and limits
  - `ConversationEntry`: Represents individual conversation messages
  
- **cache.py**: Caching system for performance optimization
  - `DialogueCache`: Caches dialogue responses, context, and extracted information
  
- **utils.py**: Utility functions for dialogue processing
  - `count_tokens`: Estimates token count in text
  - `relevance_score`: Scores dialogue entries for prioritization
  - `extract_key_info`: Extracts structured information from text

## Usage Example

```python
from backend.systems.dialogue import DialogueManager

# Create a dialogue manager
manager = DialogueManager(max_tokens=2048, max_messages=30)

# Add conversation entries
manager.add_message("player", "Hello there!")
manager.add_message("npc", "Greetings, traveler! Can I interest you in a quest?")
manager.add_message("player", "Tell me more about the quest.")

# Get current context (with relevance scoring)
context = manager.get_context(use_scoring=True, by_tokens=True)

# Extract information from the conversation
info = manager.extract_information()

# Save and load conversation history
manager.save_history("path/to/dialogue.json")
manager.load_history("path/to/dialogue.json")

# Clear cache when needed
manager.clear_cache()
```

## Integration Points
- Used by NPC, quest, and event systems for dynamic conversations
- Integrates with memory and rumor systems for context-aware dialogue

## Features
- **Context Management**: Manages conversation history with token and message limits
- **Relevance Scoring**: Prioritizes conversation entries based on recency, speaker importance, and keywords
- **Information Extraction**: Extracts key information from dialogue using pattern matching
- **Caching**: Improves performance by caching responses and context
- **Serialization**: Supports saving and loading conversation history to/from JSON

## Design Rationale and Best Practices
- For canonical Q&A, design rationale, and best practices, see [docs/bible_qa.md](../../../docs/bible_qa.md). 