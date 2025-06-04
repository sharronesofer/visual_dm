# Rumor System - Business Logic

This module contains the **pure business logic** for the rumor system. All technical infrastructure has been moved to `backend.infrastructure.systems.rumor`.

## Architecture Overview

The rumor system follows clean architecture principles with complete separation of concerns:

### 🎯 Business Logic Layer (This Module)
- **Domain Models**: Pure data structures without technical dependencies
- **Business Services**: Core domain operations and validation rules  
- **Business Protocols**: Abstractions for dependency injection
- **Pure Utilities**: Calculation and logic functions

### 🔧 Technical Infrastructure Layer
- **Database Operations**: SQLAlchemy models and repositories
- **Event Dispatching**: System integration and notifications
- **Caching & Logging**: Performance and monitoring
- **API Endpoints**: FastAPI routers and schemas

## Core Business Services

### RumorBusinessService
Core business operations for rumors:

```python
from backend.systems.rumor.services import (
    RumorBusinessService, 
    CreateRumorData,
    RumorRepository,
    RumorValidationService
)

# Dependency injection setup
service = RumorBusinessService(repository, validation_service)

# Create rumor with business validation
rumor_data = CreateRumorData(
    name="Merchant's Tale",
    content="Strange lights seen near the old tower",
    originator_id="merchant_01",
    categories=["mystery", "supernatural"],
    severity="moderate"
)

rumor = service.create_rumor(rumor_data)
```

### ConsolidatedRumorBusinessService
High-level business operations:

```python
from backend.systems.rumor.services import ConsolidatedRumorBusinessService

# Advanced business operations
consolidated_service = ConsolidatedRumorBusinessService(rumor_service)

# Create rumor with intelligent defaults
rumor = consolidated_service.create_rumor_with_defaults(
    originator_id="npc_123",
    content="The king has fallen ill",
    categories=["politics", "health"]
)

# Spread with environmental considerations
success, error = consolidated_service.spread_rumor_with_environment(
    rumor_id=rumor.id,
    from_entity_id="npc_123", 
    to_entity_id="npc_456",
    location_type="tavern",
    relationship_strength=0.7
)

# Bulk operations
decay_results = consolidated_service.bulk_decay_rumors(days_since_active=3)
```

### NPCRumorBusinessService
NPC-specific rumor business logic:

```python
from backend.systems.rumor.utils import NPCRumorBusinessService, NPCDataRepository

# NPC rumor operations
npc_service = NPCRumorBusinessService(npc_repository)

# Propagate rumors between NPCs
result = npc_service.propagate_rumor_between_npcs("npc_a", "npc_b")

# Generate NPC beliefs about events
belief = npc_service.generate_npc_belief("guard_captain", {
    "summary": "Bandits attacked the caravan",
    "poi": "forest_road"
})
```

## Business Domain Models

### Core Models
```python
from backend.systems.rumor.services import RumorData, CreateRumorData, UpdateRumorData
from backend.systems.rumor.utils import NPCMemoryEntry, NPCBelief, NPCData

# Rumor domain model
rumor = RumorData(
    id=UUID("..."),
    name="Mystery at the Tower",
    content="Strange lights were seen...",
    originator_id="witness_01",
    categories=["mystery"],
    severity="moderate",
    truth_value=0.8,
    believability=0.9
)

# NPC memory and beliefs
memory = NPCMemoryEntry(
    interaction="Heard about the lights",
    timestamp="2024-01-15T10:30:00Z",
    credibility=0.7
)

belief = NPCBelief(
    belief_summary="The tower is haunted",
    accuracy="partial", 
    source="tavern_rumors",
    trust_level=3,
    heard_at="village_tavern"
)
```

## Business Logic Features

### 🧮 Rumor Mechanics
- **Truth Calculation**: Fuzzy matching between rumor content and ground truth
- **Decay Algorithms**: Time and severity-based believability reduction
- **Mutation Logic**: Content transformation during spread
- **Spread Calculations**: Environmental and relationship modifiers

### 🎭 NPC Behavior  
- **Belief Generation**: Trust-based accuracy simulation
- **Memory Management**: Rumor storage and decay for NPCs
- **Knowledge Sharing**: Trust-threshold based information exchange
- **Faction Bias**: Opinion drift based on rumor content

### 📊 Analysis & Metrics
- **Network Analysis**: Rumor spread patterns and metrics
- **Similarity Detection**: Content-based rumor matching
- **Virality Scoring**: Spread potential calculation
- **Stability Assessment**: Long-term rumor persistence

## Configuration

Business logic uses centralized configuration from:
```
data/systems/rules/rumor_config.json
```

Key configuration areas:
- **Decay Rates**: Severity-based believability reduction
- **Mutation Chances**: Content transformation probabilities  
- **Spread Mechanics**: Environmental and relationship modifiers
- **NPC Behavior**: Trust thresholds and sharing patterns

## Testing Business Logic

Business services are designed for easy unit testing:

```python
# Mock the repository protocol
class MockRumorRepository:
    def get_rumor_by_id(self, rumor_id): 
        return test_rumor_data
    
    def create_rumor(self, rumor_data):
        return rumor_data

# Test business logic in isolation
repository = MockRumorRepository()
validation_service = MockValidationService()
service = RumorBusinessService(repository, validation_service)

# Test business rules without database
result = service.create_rumor(test_data)
assert result.believability == 1.0  # Originator believes fully
```

## Migration from Legacy Code

### For Business Operations
```python
# OLD: Mixed technical and business code
from backend.systems.rumor.services.rumor_service import RumorService

# NEW: Pure business logic
from backend.systems.rumor.services import RumorBusinessService
```

### For Infrastructure Needs
```python
# Use infrastructure layer for technical operations
from backend.infrastructure.systems.rumor import (
    RumorDatabaseService,
    RumorSystem,
    ConsolidatedRumorService
)
```

## Architecture Benefits

### ✅ Clean & Testable
- Business logic has no technical dependencies
- Easy to unit test with mocked repositories
- Clear separation of concerns

### ✅ Maintainable & Extensible  
- Business rules centralized and configurable
- New features don't require infrastructure changes
- Technology swaps don't affect business logic

### ✅ Protocol-Based Design
- Repository pattern abstracts data access
- Dependency injection enables flexible configurations
- Mock-friendly interfaces for testing

---

## Related Documentation

- **[REFACTORING.md](./REFACTORING.md)** - Complete refactoring summary
- **[Technical Infrastructure](../../infrastructure/systems/rumor/)** - Database and external service integration
- **[Configuration Guide](../../../data/systems/rules/README.md)** - Centralized rules and constants

For technical infrastructure components, see `backend.infrastructure.systems.rumor`. 