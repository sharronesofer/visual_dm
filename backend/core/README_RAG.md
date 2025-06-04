# Cross-System RAG Implementation

## Overview

This cross-system RAG (Retrieval-Augmented Generation) implementation provides centralized knowledge management and retrieval capabilities for all game systems. It enables knowledge-enhanced responses, cross-system information sharing, and intelligent content generation throughout the game world.

## Architecture

### Core Components

1. **RAG Service** (`rag_service.py`) - Centralized knowledge storage and retrieval
2. **RAG Client** (`rag_client.py`) - Standardized interface for system integration
3. **Knowledge Loader** (`knowledge_loader.py`) - Utilities for loading knowledge from various sources
4. **System Adapters** - System-specific customization and optimization

### Data Flow

```
Game Systems → RAG Client → RAG Service → Vector Database
                ↓
Knowledge Enhancement ← Query Processing ← Knowledge Retrieval
                ↓
Enhanced Responses → System-Specific Formatting → Game Output
```

## Key Features

### 1. Centralized Knowledge Management
- **Vector Database**: ChromaDB with persistent storage
- **Semantic Search**: Sentence transformer embeddings for intelligent retrieval
- **Knowledge Categories**: Organized by content type (lore, characters, quests, etc.)
- **Cross-System Access**: Any system can query knowledge from any other system

### 2. System-Specific Adapters
- **Dialogue**: Context-aware conversation enhancement
- **Quest**: Knowledge-driven quest generation and validation
- **NPC**: Personality and backstory development
- **Magic**: Rule-based spell and mechanic validation
- **Faction**: Relationship-aware content modification

### 3. Performance Optimization
- **Relevance Thresholds**: Configurable quality gates
- **Caching**: Intelligent response caching with TTL
- **Weighted Categories**: Priority-based knowledge ranking
- **Graceful Fallbacks**: Seamless operation when RAG is unavailable

### 4. Dynamic Learning
- **Conversation Analysis**: Learn from player interactions
- **Pattern Recognition**: Identify and store successful patterns
- **Real-time Updates**: Add new knowledge during gameplay
- **Quality Validation**: Confidence scoring and source tracking

## Installation & Setup

### Dependencies

```bash
pip install chromadb sentence-transformers
```

### Environment Configuration

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key

# RAG Configuration
RAG_DB_PATH=./data/rag_db
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_MAX_RESULTS=5
RAG_RELEVANCE_THRESHOLD=0.7
RAG_CONTEXT_WINDOW=2000

# Performance Settings
RAG_CACHE_ENABLED=true
RAG_CACHE_TTL=3600
RAG_BATCH_SIZE=100

# Optional: Research Enhancement
PERPLEXITY_API_KEY=your_perplexity_key
PERPLEXITY_MODEL=sonar-medium-online
```

### Initialization

```python
from backend.core.initialize_rag import initialize_cross_system_rag

# Initialize with default settings
results = await initialize_cross_system_rag()

# Initialize with custom configuration
from backend.core.rag_service import RAGConfiguration
config = RAGConfiguration()
config.relevance_threshold = 0.8
results = await initialize_cross_system_rag(config=config)
```

## Usage Examples

### Basic System Integration

```python
from backend.core.rag_client import create_rag_client

# Create a RAG client for your system
rag_client = await create_rag_client('your_system')

# Add knowledge
await rag_client.add_knowledge(
    content="Your knowledge content here",
    category="your_category",
    metadata={"source": "system_data"},
    tags=["tag1", "tag2"]
)

# Query knowledge
results = await rag_client.query(
    query="What do you know about magic spells?",
    context={"system": "magic", "user_level": "beginner"}
)

# Enhance a response
enhanced = await rag_client.enhance_response(
    base_response="Basic spell information",
    context="User asking about fire spells",
    context_data={"spell_school": "evocation"}
)
```

### Dialogue System Integration

```python
from backend.core.rag_client import create_rag_client, DialogueRAGAdapter

# Initialize dialogue RAG client
dialogue_rag = await create_rag_client('dialogue', DialogueRAGAdapter())

# Generate enhanced NPC response
response = await dialogue_rag.enhance_response(
    base_response="Hello, traveler!",
    context="NPC greeting at tavern",
    context_data={
        'npc_id': 'tavern_keeper_001',
        'location': 'rusty_anchor_tavern',
        'time_of_day': 'evening'
    }
)

# Cross-system knowledge query
knowledge = await dialogue_rag.cross_system_query(
    query="What quests are available here?",
    systems=['quest', 'faction', 'location'],
    context={'location_id': 'tavern_area'}
)
```

### Quest System Integration

```python
from backend.systems.quest.rag_adapter import get_quest_rag_service

# Get quest RAG service
quest_rag = await get_quest_rag_service()

# Generate quest suggestions
suggestions = await quest_rag.generate_quest_suggestions(
    location_id="forest_clearing",
    difficulty="medium",
    quest_type="exploration"
)

# Enhance quest description
enhanced_desc = await quest_rag.enhance_quest_description(
    base_description="Find the lost artifact",
    quest_type="fetch",
    context={
        'location_id': 'ancient_ruins',
        'faction_id': 'scholars_guild'
    }
)
```

### NPC System Integration

```python
from backend.infrastructure.rag_adapters.npc_rag_adapter import get_npc_rag_service

# Get NPC RAG service
npc_rag = await get_npc_rag_service()

# Enhance NPC personality
personality = await npc_rag.enhance_npc_personality(
    base_personality={'traits': ['friendly', 'cautious']},
    npc_type='merchant',
    location_context={'region': 'trade_district', 'wealth_level': 'high'}
)

# Generate backstory
backstory = await npc_rag.generate_npc_backstory(
    npc_data={
        'name': 'Elena Brightforge',
        'profession': 'blacksmith',
        'id': 'blacksmith_001'
    },
    location_id='crafting_quarter'
)
```

## System-Specific Features

### Dialogue System
- **Context-Aware Enhancement**: NPCs reference relevant world knowledge
- **Conversation Learning**: Extract insights from player interactions
- **Cross-System Integration**: Access quest, faction, and location data
- **Personality Consistency**: Maintain character voice across interactions

### Quest System
- **Dynamic Generation**: Create quests based on world state and lore
- **Validation**: Ensure quest logic aligns with established rules
- **Progression Tracking**: Learn from completed quests to improve future ones
- **Location Awareness**: Generate location-appropriate objectives

### NPC System
- **Personality Development**: Create rich, consistent character personalities
- **Backstory Generation**: Generate lore-appropriate character histories
- **Behavior Learning**: Adapt NPC behavior based on successful patterns
- **Dialogue Integration**: Provide knowledge for conversation systems

### Magic System
- **Rule Validation**: Ensure spells follow established magical laws
- **Effect Generation**: Create consistent magical effects and descriptions
- **Balance Checking**: Validate spell power and limitations
- **Lore Integration**: Connect spells to world mythology and rules

## Knowledge Categories

### Core Categories
- **lore**: World history, mythology, and background information (weight: 0.8)
- **characters**: Character descriptions, relationships, and histories (weight: 0.9)
- **locations**: Geographic information, landmarks, and area descriptions (weight: 0.7)
- **factions**: Organization structures, goals, and relationships (weight: 0.6)
- **quests**: Quest patterns, objectives, and narrative elements (weight: 0.8)
- **items**: Equipment, artifacts, and material descriptions (weight: 0.5)
- **events**: Historical and current events affecting the world (weight: 0.7)

### System-Specific Categories
- **magic**: Spells, magical rules, and arcane knowledge (weight: 0.7)
- **rules**: Game mechanics and system constraints (weight: 0.9)
- **dialogue**: Conversation patterns and response templates (weight: 0.8)
- **npcs**: Character archetypes and behavior patterns (weight: 0.8)
- **rumors**: Information propagation and gossip networks (weight: 0.5)
- **memory**: Interaction history and character memories (weight: 0.7)

## Performance Considerations

### Optimization Strategies
1. **Relevance Thresholds**: Set appropriate confidence minimums
2. **Result Limits**: Control the number of retrieved entries
3. **Caching**: Enable caching for frequently accessed knowledge
4. **Batch Processing**: Load knowledge in batches for efficiency

### Monitoring
```python
# Get system statistics
from backend.core.initialize_rag import get_rag_status

status = await get_rag_status()
print(f"Total entries: {status['total_entries']}")
print(f"Active systems: {status['systems']}")
```

### Performance Tuning
```python
# Custom configuration for performance
config = RAGConfiguration()
config.relevance_threshold = 0.8  # Higher quality threshold
config.max_results = 3           # Fewer results for speed
config.cache_ttl = 7200          # Longer cache duration
```

## Troubleshooting

### Common Issues

1. **RAG Not Initializing**
   - Check ChromaDB and sentence-transformers installation
   - Verify database path permissions
   - Review environment variable configuration

2. **Poor Quality Results**
   - Adjust relevance threshold
   - Review knowledge entry quality
   - Check category weights configuration

3. **Performance Issues**
   - Enable caching
   - Reduce max_results
   - Optimize batch processing

4. **Memory Usage**
   - Monitor vector database size
   - Implement knowledge cleanup routines
   - Consider embedding model size

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed RAG logging
import os
os.environ['DEBUG'] = 'true'
```

## Extension Points

### Custom Adapters
```python
from backend.core.rag_client import SystemRAGAdapter

class CustomRAGAdapter(SystemRAGAdapter):
    def __init__(self):
        super().__init__("custom_system")
    
    async def preprocess_query(self, query: str, context: Dict[str, Any]) -> str:
        # Custom query preprocessing
        return enhanced_query
    
    async def postprocess_response(self, response: RAGResponse, context: Dict[str, Any]) -> RAGResponse:
        # Custom response formatting
        return response
    
    def get_relevant_categories(self, context: Dict[str, Any]) -> List[str]:
        # Custom category selection
        return categories
```

### Knowledge Loaders
```python
from backend.core.knowledge_loader import KnowledgeLoader

loader = KnowledgeLoader()
await loader.initialize()

# Load from custom format
results = await loader.load_from_custom_format(
    file_path="custom_data.format",
    system="custom_system",
    category="custom_category"
)
```

## Best Practices

### Knowledge Management
1. **Quality Over Quantity**: Focus on relevant, high-quality entries
2. **Consistent Categorization**: Use standardized category names
3. **Rich Metadata**: Include useful context in metadata fields
4. **Regular Cleanup**: Remove outdated or irrelevant knowledge

### System Integration
1. **Graceful Degradation**: Always provide fallbacks when RAG is unavailable
2. **Context Awareness**: Include relevant context in queries
3. **Performance Monitoring**: Track response times and quality metrics
4. **User Experience**: Ensure RAG enhances rather than delays responses

### Development Workflow
1. **Test Incrementally**: Verify each integration step
2. **Monitor Performance**: Track system resource usage
3. **Validate Knowledge**: Ensure knowledge accuracy and relevance
4. **Document Patterns**: Record successful integration patterns

## Future Enhancements

### Planned Features
- **Semantic Clustering**: Group related knowledge automatically
- **Temporal Awareness**: Consider time-based relevance in queries
- **Multi-Modal Support**: Support for image and audio knowledge
- **Advanced Learning**: Machine learning-based knowledge extraction
- **Federation**: Distributed RAG across multiple services

### Integration Opportunities
- **Player Behavior Analysis**: Learn from player interaction patterns
- **Content Generation**: AI-assisted content creation using RAG
- **Quality Assurance**: Automated content validation and suggestions
- **Analytics**: Knowledge usage and effectiveness tracking

---

For more information, see the individual system documentation and the main project README.

# Cross-System RAG Integration

A comprehensive Retrieval-Augmented Generation (RAG) system that enables intelligent, knowledge-enhanced responses across all game systems in Visual DM.

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file in the `backend/` directory with the following configuration:

```bash
# RAG System Configuration
RAG_DB_PATH=./data/chroma_db
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_MAX_RESULTS=10
RAG_CONFIDENCE_THRESHOLD=0.3

# AI API Keys (add your actual keys)
ANTHROPIC_API_KEY=your_anthropic_key_here
# OPENAI_API_KEY=your_openai_key_here  # Optional
# PERPLEXITY_API_KEY=your_perplexity_key_here  # Optional for research features

# Application Settings
DEBUG=true
LOG_LEVEL=info

# Database Settings  
DATABASE_URL=sqlite:///./data/game.db
MONGODB_URL=mongodb://localhost:27017/visual_dm
```

### 3. Initialize RAG System
```python
# Run this once to set up the RAG system
from backend.core.initialize_rag import initialize_cross_system_rag

await initialize_cross_system_rag()
```

### 4. Test the System
```python
from backend.core.rag_client import quick_query

# Test a simple query
results = await quick_query("dialogue", "Tell me about dragons")
print(f"Found {len(results)} relevant knowledge entries")
``` 