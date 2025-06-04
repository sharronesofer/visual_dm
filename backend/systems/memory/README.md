# Memory System

## Overview
The Memory System simulates entity-level memory with relevance scoring and decay mechanics. It manages both core memories (permanent) and regular memories (which decay over time). **Enhanced with comprehensive behavioral examples and cross-system integration** as part of Task 73.

## Components

### Memory
The `Memory` class represents a single memory entity with the following features:
- Core vs. regular memory types
- Automatic decay mechanics
- Metadata tracking (creation time, last access, etc.)
- Importance scoring
- Tagging system
- Memory graph linking

### MemoryManager
The `MemoryManager` class manages collections of memories for NPCs, integrating:
- Vector database for semantic search and storage
- Summarization capabilities via LLM
- Memory reinforcement and decay mechanics
- Conversation tracking and cleanup logic
- Event system integration
- Singleton instance pattern with async initialization

### Memory Behavior Influence System (Task 73 Enhancement)
The `MemoryBehaviorInfluenceService` translates memories into behavioral changes:
- **Trust Calculations**: Analyzes past interactions to determine trust levels
- **Risk Assessment**: Uses previous experiences to evaluate threats and opportunities
- **Emotional Triggers**: Identifies memories that trigger emotional responses
- **Faction Bias**: Calculates political alignment based on historical events
- **Cross-System Integration**: Affects multiple game systems simultaneously

### Cross-System Integration (Task 73 Enhancement)
The `MemoryCrossSystemIntegrator` bridges memory-driven behavior with other systems:
- **Economic Behavior**: Price modifications, trade willingness, credit decisions
- **Faction Behavior**: Political alignment, loyalty shifts, diplomatic stance
- **Combat Behavior**: Aggression levels, flee thresholds, ally recognition
- **Social Behavior**: Conversation openness, topic preferences, rumor credibility

### Behavioral Examples Library (Task 73 Enhancement)
The `MemoryBehaviorExamples` class provides comprehensive examples of memory-driven behavior:
- **Relationship Memories**: How past interactions affect current responses
- **Event Memories**: How witnessed events influence behavior
- **Location Memories**: How places with strong memories affect behavior
- **Faction Memories**: How historical conflicts influence current tensions
- **Decision Making**: Memory-driven decision processes
- **Cross-System Integration**: Multi-system behavioral impacts

### Memory Utilities
The `memory_utils.py` file provides utility functions for:
- Storing interactions
- Updating long-term summaries
- Cleaning and summarizing memories
- Managing faction, region, and world memories
- Processing GPT-generated memories

### API Routes
The `memory_routes.py` file provides Flask routes for:
- Viewing memory entries
- Clearing memory
- Storing interactions
- Updating long-term memory
- Evaluating beliefs from memory

## Memory-Driven Behavior Examples

### Trust Calculations
Memories directly influence how NPCs trust other entities:

```python
# Example: NPC remembers being betrayed
trust_calc = await behavior_service.calculate_trust_level("player_123")
# Result: trust_level=0.2, faction_bias=-0.8, trade_willingness=0.3
```

### Risk Assessment
Past experiences shape risk perception:

```python
# Example: NPC witnessed market crash
risk_assessment = await behavior_service.assess_risk("investment_opportunity")
# Result: risk_level=0.8, investment_willingness=0.1, financial_paranoia=0.7
```

### Emotional Triggers
Traumatic or positive memories trigger emotional responses:

```python
# Example: War veteran hears battle sounds
triggers = await behavior_service.identify_emotional_triggers("combat_nearby")
# Result: emotion="fear", flee_threshold=0.7, combat_participation=0.1
```

### Cross-System Integration
Single memories can affect multiple systems:

```python
# Example: Dragon attack survivor
integrator = MemoryCrossSystemIntegrator(behavior_service)
economic_mods = await integrator.get_economic_behavior_modifications()
combat_mods = await integrator.get_combat_behavior_modifications()
# Economic: luxury_aversion=0.9, business_motivation=0.3
# Combat: dragon_phobia=1.0, protection_seeking=0.9
```

## Behavioral Categories

### 1. Relationship Memories
- **Betrayal Impact**: Trust levels drop significantly after betrayal
- **Helpful Actions**: Positive interactions increase trust and trade willingness
- **Repeated Interactions**: Consistent behavior builds long-term relationships

### 2. Event Memories
- **War Trauma**: Combat avoidance, peace advocacy, weapon aversion
- **Economic Disasters**: Risk aversion, financial paranoia, conservative trading
- **Magical Accidents**: Magic user distrust, superstition, protection seeking

### 3. Location Memories
- **Childhood Homes**: Nostalgic behavior, increased generosity, storytelling
- **Battle Sites**: Solemn respect, ritualistic behavior, historical teaching
- **Success Locations**: Increased confidence, better negotiation, mentoring

### 4. Faction Memories
- **Ancestral Feuds**: Inherited hatred, automatic hostility, honor-bound behavior
- **War Alliances**: Lasting bonds, resource sharing, military respect
- **Political Persecution**: Authority distrust, underground sympathy, resistance support

### 5. Decision Making
- **Credit Decisions**: Based on payment history and character assessment
- **Combat Intervention**: Influenced by debt of honor and personal loyalty
- **Information Sharing**: Determined by trust levels and reciprocal secrecy

## Usage

```python
from backend.systems.memory import Memory, MemoryManager
from backend.systems.memory.services.memory_behavior_influence import MemoryBehaviorInfluenceService
from backend.systems.memory.services.cross_system_integration import MemoryCrossSystemIntegrator

# Create a memory manager for an NPC
manager = await MemoryManager.get_instance(
    npc_id="npc123",
    short_term_db=short_term_collection, 
    long_term_db=long_term_collection,
    event_dispatcher=event_dispatcher
)

# Add memories
memory = Memory(
    content="Met the player in the tavern",
    importance=0.7,
    associated_entities=["player123"],
    decay_rate=0.1,
    tags=["player", "meeting", "tavern"],
    type_="regular",
    npc_id="npc123"
)
manager.add_memory(memory)

# Analyze behavioral impact
behavior_service = MemoryBehaviorInfluenceService(manager)
trust_calc = await behavior_service.calculate_trust_level("player123")
risk_assessment = await behavior_service.assess_risk("trade_deal")

# Get cross-system modifications
integrator = MemoryCrossSystemIntegrator(behavior_service)
economic_mods = await integrator.get_economic_behavior_modifications()
faction_mods = await integrator.get_faction_behavior_modifications(["red_hawks", "blue_company"])

# Store interactions
manager.store_interaction("The player asked about the quest", {"region": "tavern"})

# Retrieve relevant memories
memories = manager.query_memories("player tavern", 5)

# Generate a summary
summary = manager.update_long_term_summary()
```

## Behavioral Documentation Generation

Generate comprehensive documentation of all behavioral examples:

```python
from backend.systems.memory.utils.behavioral_examples import MemoryBehaviorExamples

# Generate full documentation
documentation = MemoryBehaviorExamples.generate_behavior_documentation()

# Get examples by category
relationship_examples = MemoryBehaviorExamples.get_relationship_memory_examples()
event_examples = MemoryBehaviorExamples.get_event_memory_examples()

# Get examples by system
economy_examples = MemoryBehaviorExamples.get_examples_by_system("economy")
combat_examples = MemoryBehaviorExamples.get_examples_by_system("combat")

# Get examples by memory type
trauma_examples = MemoryBehaviorExamples.get_examples_by_memory_category("trauma")
achievement_examples = MemoryBehaviorExamples.get_examples_by_memory_category("achievement")
```

## Integration
The Memory System integrates with the Event System through:
- `MemoryCreatedEvent`
- `MemoryDecayedEvent`
- `MemoryReinforcedEvent`

**Enhanced Integration (Task 73):**
- **Economy System**: Price modifications, trade willingness, credit decisions
- **Faction System**: Political alignment, loyalty shifts, diplomatic stance
- **Combat System**: Aggression levels, flee thresholds, ally recognition
- **Social System**: Conversation openness, topic preferences, rumor credibility
- **Quest System**: Quest offering likelihood, information sharing
- **Dialogue System**: Response variations based on memory-driven trust and emotion

These events allow other systems to react to memory changes and maintain loose coupling.

## Features

- Entity-local memory management (memories are never directly shared)
- Core memories that don't decay over time
- Regular memories with decay mechanics
- Memory categorization for analytics
- JSON-based persistence organized by entity
- GPT summarization for narrative generation
- Async API for better performance
- Singleton pattern for centralized management
- **Memory-driven behavioral modifications** (Task 73)
- **Cross-system integration** (Task 73)
- **Comprehensive behavioral examples** (Task 73)
- **Trust calculation algorithms** (Task 73)
- **Risk assessment based on past experiences** (Task 73)
- **Emotional trigger identification** (Task 73)
- **Faction bias calculation** (Task 73)

## Key Components

- Memory objects with metadata, categories, and relevance scores
- Memory decay mechanisms to simulate forgetting
- Contextual relationships between memories (memory graphs)
- Event emission for memory operations
- Vector DB integration for semantic search
- **Behavioral influence algorithms** (Task 73)
- **Cross-system behavior modification** (Task 73)
- **Comprehensive example library** (Task 73)

## Integration Points

- Provides memory context for dialogue and narrative generation
- Integrates with the Events System for capturing significant events
- Supports NPCs' ability to recall and respond to past interactions
- Firebase integration for persistent storage
- **Economy System**: Memory-driven pricing and trade behavior
- **Faction System**: Historical event influence on political alignment
- **Combat System**: Past trauma affecting combat behavior
- **Social System**: Trust-based conversation and relationship dynamics
- **Quest System**: Memory-influenced quest generation and completion
- **Dialogue System**: Context-aware responses based on memory analysis

## Testing

Comprehensive test coverage includes:
- Behavioral example validation
- Cross-system integration testing
- Memory behavior influence algorithms
- Trust calculation accuracy
- Risk assessment functionality
- Emotional trigger identification
- Faction bias calculation

Run tests with:
```bash
python -m pytest tests/systems/memory/test_behavioral_examples.py -v
python -m pytest tests/systems/memory/test_memory_behavior_influence.py -v
python -m pytest tests/systems/memory/test_cross_system_integration.py -v
```

Refer to the Development Bible for detailed design documentation.
