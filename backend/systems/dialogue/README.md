# Dialogue System

## Overview

The Visual DM Dialogue System provides comprehensive conversation management for NPCs and players in the game world. The system integrates deeply with all game systems to provide contextual, dynamic dialogue that reflects the current state of the world, character relationships, faction standings, ongoing quests, and regional characteristics.

**NEW: RAG Integration** - The dialogue system now includes Retrieval-Augmented Generation (RAG) capabilities to enhance responses with relevant game knowledge and lore.

## Key Features

### Core Dialogue Management
- **Conversation State Management**: Track active conversations with context preservation
- **Multi-participant Support**: Handle complex conversations with multiple characters
- **Message Types**: Support for dialogue, actions, emotes, and system messages
- **Context Preservation**: Maintain conversation history and context across interactions

### AI-Enhanced Response Generation
- **LLM Integration**: Uses advanced language models for natural dialogue generation
- **RAG Enhancement**: Retrieves relevant game knowledge to enhance response accuracy and depth
- **Character Consistency**: Maintains character voice and personality across conversations
- **Context-Aware Responses**: Incorporates all available game context into responses

### Deep System Integration
- **Quest Integration**: References quest states, progress, and provides quest-related dialogue options
- **Faction Integration**: Modifies dialogue based on faction relationships, reputation, and conflicts
- **Region Integration**: Incorporates location-specific context, weather, events, and regional characteristics
- **Memory Integration**: Remembers past conversations and character interactions
- **Rumor Integration**: Spreads and references information through the dialogue network
- **Motif Integration**: Applies thematic consistency based on location and context
- **Population Integration**: Considers demographic data for appropriate dialogue
- **Relationship Integration**: Reflects character relationships in conversation tone and content
- **War Integration**: Incorporates conflict states and wartime considerations
- **Time Integration**: Applies temporal context and time-sensitive information

### RAG (Retrieval-Augmented Generation) System
- **Knowledge Sources**: Maintains separate knowledge bases for lore, characters, locations, factions, quests, items, and events
- **Semantic Search**: Uses vector embeddings to find relevant knowledge for dialogue enhancement
- **Dynamic Enhancement**: Automatically enhances responses with retrieved information when relevant
- **Knowledge Updates**: Continuously learns from dialogue interactions to improve future responses
- **Fallback Support**: Gracefully degrades when RAG components are unavailable

## Architecture

```
DialogueSystem
├── Core Components
│   ├── LLMManager - Language model integration
│   ├── ConversationMemorySystem - Conversation state management
│   ├── InformationExtractor - Context extraction and analysis
│   ├── DialogueScorer - Response quality evaluation
│   └── EventEmitter - Event-driven integration
├── RAG Integration
│   ├── DialogueRAGIntegration - Main RAG controller
│   ├── Vector Database (ChromaDB) - Knowledge storage and retrieval
│   ├── Embedding Model - Semantic similarity calculations
│   └── Knowledge Sources - Organized game knowledge collections
├── System Integrations
│   ├── QuestIntegration - Quest state and progression
│   ├── FactionIntegration - Reputation and faction dynamics
│   ├── RegionIntegration - Geographic and environmental context
│   ├── MemoryIntegration - Persistent memory management
│   ├── RumorIntegration - Information propagation
│   ├── MotifIntegration - Thematic consistency
│   ├── PopulationIntegration - Demographic awareness
│   ├── RelationshipIntegration - Character relationships
│   ├── WarIntegration - Conflict awareness
│   └── TimeIntegration - Temporal context
└── Event System
    ├── Dialogue events
    ├── Quest progression events
    ├── Faction reputation events
    └── Memory formation events
```

## RAG Integration Details

### Knowledge Sources
The RAG system organizes knowledge into weighted categories:
- **Characters** (0.9): Character backgrounds, personalities, and histories
- **Lore** (0.8): World history, mythology, and background information
- **Quests** (0.8): Quest details, objectives, and narrative elements
- **Locations** (0.7): Geographic information and location descriptions
- **Events** (0.7): Historical and current events affecting the world
- **Factions** (0.6): Faction information, politics, and relationships
- **Items** (0.5): Item descriptions, properties, and significance

### RAG Enhancement Process
1. **Context Analysis**: Extract key topics and entities from dialogue context
2. **Knowledge Retrieval**: Search relevant knowledge sources using semantic similarity
3. **Relevance Filtering**: Apply confidence thresholds and weighting
4. **Response Enhancement**: Use LLM to naturally integrate retrieved knowledge
5. **Quality Assessment**: Evaluate enhancement confidence and success

### RAG Configuration
- **Embedding Model**: all-MiniLM-L6-v2 (lightweight, fast semantic embeddings)
- **Vector Database**: ChromaDB (persistent vector storage)
- **Relevance Threshold**: 0.7 (configurable minimum similarity)
- **Max Retrieved Items**: 3-5 (prevents information overload)
- **Fallback Support**: Graceful degradation when components unavailable

## Integration Examples

### Quest-Aware Dialogue
```python
# Character can reference available and active quests
enhanced_context = quest_integration.add_quest_context_to_dialogue(
    context, character_id="npc_blacksmith", player_id="player_123"
)
# Result: "I have a task that needs doing: Retrieve the Lost Hammer"
```

### Faction-Influenced Responses  
```python
# Dialogue changes based on faction reputation
response = faction_integration.get_faction_specific_responses(
    character_id="guard_captain", 
    faction_context={"reputation": {"standing": "friendly"}}
)
# Result: "Welcome, friend. How can our faction assist you?"
```

### RAG-Enhanced Knowledge
```python
# Automatic knowledge retrieval and integration
rag_result = rag_integration.enhance_dialogue_response(
    base_response="The ancient ruins are dangerous.",
    dialogue_context=context,
    character_id="wise_elder"
)
# Result: "The ancient ruins of Eldergloom are dangerous. Legend speaks of 
#          mysterious artifacts from a forgotten civilization hidden within."
```

### Regional Context
```python
# Location-specific dialogue with environmental awareness
enhanced_context = region_integration.add_region_context_to_dialogue(
    context, location_id="merchants_quarter"
)
# Result includes weather, local events, political climate, and economic status
```

## Dependencies

### Required Packages
- `backend.systems.llm` - Language model integration
- `backend.systems.memory` - Conversation memory management  
- `backend.systems.quests` - Quest system integration
- `backend.systems.factions` - Faction management
- `backend.systems.regions` - Geographic systems
- `backend.systems.motif` - Thematic consistency

### Optional RAG Dependencies
- `chromadb` - Vector database for knowledge storage
- `sentence-transformers` - Semantic embedding generation
- `numpy` - Vector operations (usually included with other packages)

### Installation
```bash
# Core dialogue system (required)
pip install backend-dialogue-system

# RAG enhancement (optional)
pip install chromadb sentence-transformers

# System integrations (as needed)
pip install backend-quest-system backend-faction-system backend-region-system
```

## Configuration

### Basic Configuration
```python
dialogue_system = DialogueSystem({
    "enable_rag": True,  # Enable RAG enhancement
    "rag_threshold": 0.7,  # Minimum relevance threshold
    "max_context_length": 2000,  # Maximum context size
    "enable_faction_integration": True,
    "enable_quest_integration": True,
    "enable_region_integration": True
})
```

### RAG Configuration
```python
rag_integration = DialogueRAGIntegration(
    embedding_model_name="all-MiniLM-L6-v2",
    vector_db_path="./data/dialogue_knowledge",
    enable_fallback=True
)
```

## Performance Considerations

### RAG System Performance
- **Embedding Generation**: ~50ms per query (cached for repeated queries)
- **Vector Search**: ~10-20ms per knowledge source
- **LLM Enhancement**: ~200-500ms (depends on model and response length)
- **Total RAG Overhead**: ~300-600ms (when knowledge is found and used)

### Optimization Strategies
- **Knowledge Caching**: Cache frequently accessed knowledge
- **Batch Processing**: Process multiple dialogue requests together
- **Selective Enhancement**: Only enhance high-importance dialogues
- **Threshold Tuning**: Adjust relevance thresholds for performance vs. quality

### Fallback Behavior
- **No RAG Dependencies**: System operates normally without RAG enhancement
- **No Knowledge Found**: Falls back to base LLM response
- **RAG Errors**: Logs errors and continues with unenhanced response
- **Performance Issues**: Automatic timeout and fallback after 3 seconds

## Usage Examples

### Starting a Conversation with Full Integration
```python
# Initialize dialogue system
dialogue_system = DialogueSystem({"enable_rag": True})

# Start conversation
conversation_id = dialogue_system.start_conversation(
    participants={"npc_merchant": "merchant", "player_1": "customer"},
    location_id="market_square",
    metadata={"context": "shopping", "time_of_day": "afternoon"}
)

# Send player message
dialogue_system.send_message(
    conversation_id=conversation_id,
    sender_id="player_1", 
    content="Do you have any work for me?"
)

# Generate enhanced NPC response
response = dialogue_system.generate_response(
    conversation_id=conversation_id,
    responder_id="npc_merchant",
    target_id="player_1"
)

# Response will include:
# - Quest opportunities (if any)
# - Faction-aware tone
# - Regional context (market conditions, local events)
# - RAG-enhanced knowledge about available work
# - Character-consistent personality
```

### Adding Knowledge to RAG System
```python
# Add lore knowledge
dialogue_system.rag_integration.add_knowledge_to_rag(
    content="The Crimson Banner was a legendary mercenary company known for their honor.",
    source_type="lore",
    metadata={
        "topic": "mercenary_companies",
        "importance": "medium",
        "era": "recent_history"
    }
)

# Add character knowledge
dialogue_system.rag_integration.add_knowledge_to_rag(
    content="Captain Sarah leads the city guard with unwavering dedication to justice.",
    source_type="characters", 
    metadata={
        "character_id": "captain_sarah",
        "role": "guard_captain",
        "personality_traits": ["honorable", "dedicated", "just"]
    }
)
```

### Checking RAG System Status
```python
# Get comprehensive status
status = dialogue_system.rag_integration.get_rag_system_status()
print(f"RAG Available: {status['available']}")
print(f"Knowledge Sources: {len(status['knowledge_sources'])}")

for source, info in status['knowledge_sources'].items():
    print(f"  {source}: {info['document_count']} documents")
```

## Troubleshooting

### Common Issues

**RAG Not Enhancing Responses**
- Check if `chromadb` and `sentence-transformers` are installed
- Verify knowledge base has been populated with relevant content
- Lower `relevance_threshold` to allow more knowledge matches
- Check logs for RAG-related errors

**Performance Issues**
- Reduce `max_retrieved_items` for faster knowledge retrieval
- Increase `relevance_threshold` to reduce processing overhead
- Consider using a smaller embedding model
- Enable RAG caching if available

**Integration Errors**
- Verify all required system dependencies are available
- Check that character, faction, and location IDs exist in respective systems
- Review integration service configurations
- Monitor logs for specific integration failures

**Knowledge Quality Issues**
- Review and curate knowledge content for accuracy
- Add more specific metadata for better retrieval
- Adjust knowledge source weights based on importance
- Use knowledge validation tools to identify issues

### Debugging RAG Issues
```python
# Test RAG retrieval directly
retrieved = dialogue_system.rag_integration.retrieve_relevant_information(
    query="guard captain duties",
    context={},
    max_items=5,
    threshold=0.5
)

print(f"Found {len(retrieved['items'])} relevant items")
for item in retrieved['items']:
    print(f"  Relevance: {item['relevance_score']:.2f}")
    print(f"  Content: {item['content'][:100]}...")
```

### Logging Configuration
```python
import logging

# Enable detailed dialogue system logging
logging.getLogger('backend.systems.dialogue').setLevel(logging.DEBUG)

# Enable RAG-specific logging  
logging.getLogger('backend.systems.dialogue.rag_integration').setLevel(logging.INFO)
```

## Performance Monitoring

The dialogue system provides detailed metrics for monitoring RAG performance:

- **Enhancement Rate**: Percentage of responses enhanced by RAG
- **Average Confidence**: Mean confidence score of RAG enhancements
- **Response Times**: Timing breakdown of dialogue generation steps
- **Knowledge Utilization**: Usage statistics for different knowledge sources
- **Error Rates**: RAG failures and fallback incidents

Access metrics through the system analytics integration or via direct system queries. 