# Context Management System

The Context Management System provides robust tools for managing conversation history, context windowing (by message or token count), relevance scoring, and key information extraction for dynamic dialogue systems.

## Features
- Conversation history data structure with serialization and persistence
- Configurable context windowing (sliding window by message or token count)
- Relevance scoring for prioritizing important exchanges
- Key information extraction using regex and rule-based patterns
- Integration points for custom scoring and extraction logic
- **Token-based windowing for precise context control**
- **Direct integration with scoring and extraction modules**

## Usage

### Basic Example
```python
from dialogue.context_manager import ConversationHistory
from dialogue.scoring import relevance_score
from dialogue.extractors import extract_key_info

# Create a conversation history
history = ConversationHistory(max_messages=10, max_tokens=100)
history.add_entry('user', 'Hello!')
history.add_entry('npc', 'Greetings, adventurer!')
history.add_entry('user', 'Tell me about the quest: Dragon Hunt')

# Get the current context window (most recent messages)
window = history.get_context_window()

# Get the most relevant messages using a scoring function
relevant_window = history.get_context_window(scoring_fn=lambda e: relevance_score(e))

# Get a context window limited by token count
window_by_tokens = history.get_context_window(by_tokens=True)

# Extract key information from all messages
history.extract_key_info()  # Uses extract_key_info by default
print(history.extracted_info)

# Save and load history
history.save('history.json')
loaded = ConversationHistory.load('history.json')
```

## Configuration
- `max_tokens`: Maximum number of tokens to keep in the context window (enforced in both windowing and entry limits)
- `max_messages`: Maximum number of messages to keep in the context window
- Scoring weights and important keywords/speakers can be configured in `dialogue/scoring.py`
- Use a custom tokenizer for more accurate token counting if needed

## Extension Points
- **Custom Relevance Scoring:** Pass a custom `scoring_fn` to `get_context_window()`
- **Custom Extraction:** Pass a custom `extractor_fn` to `extract_key_info()`
- **Persistence:** Use `save()` and `load()` methods for file-based storage; extend for database support
- **Advanced Features:** Add summarization, advanced NLP extraction, or database persistence by subclassing `ConversationHistory`

## Advanced Usage
- **Token-based Context:** Use `get_context_window(by_tokens=True)` for precise control over prompt size for LLMs
- **Integration with GPT:** Use the context window as input for prompt construction
- **Batch Extraction:** Run `extract_key_info()` after batch updates to keep extracted info up to date

## Testing
Unit and integration tests are provided in `tests/dialogue/test_context_manager.py`.

## Integration
- Designed to integrate with GPT-driven dialogue systems for prompt construction
- Can be extended to support advanced NLP extraction, context summarization, and more

## Future Improvements
- Improved tokenization using LLM-compatible libraries
- Advanced NLP-based key information extraction
- Context summarization for long conversations 