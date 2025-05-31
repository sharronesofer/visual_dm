# Backend Systems Inventory - Updated Hybrid Architecture

**Updated:** 2025-01-18
**Architecture:** Hybrid (Business Logic + Infrastructure Separation)
**Total Python Files:** 982

## Architecture Overview

Our hybrid architecture separates concerns into two main areas:

### Business Logic Systems (/backend/systems/)
Domain-specific components that implement game mechanics and business rules:
- **Shared Domain Components:** models, repositories, schemas, rules (package level)
- **System-Specific Implementations:** Individual game systems with specialized logic

### Infrastructure Components (/backend/infrastructure/)
Technical concerns and platform services:
- **Technical Services:** Authentication, data access, analytics, storage
- **Integration Layer:** External services, events, shared utilities

## Systems Overview (Business Logic)

| System | Type | Models | Services | Repositories | Routers | Schemas | Tests | Total Files |
|--------|------|--------|----------|--------------|---------|---------|-------|-------------|
| **Domain Systems** |
| character | Game Domain | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~47 |
| npc | Game Domain | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~24 |
| quest | Game Domain | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~17 |
| faction | Game Domain | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~24 |
| item | Game Domain | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~14 |
| location | Game Domain | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~19 |
| world | Game Domain | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~26 |
| market | Game Domain | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~44 |
| **Gameplay Systems** |
| combat | Game Mechanics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~31 |
| crafting | Game Mechanics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~34 |
| dialogue | Game Mechanics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~27 |
| diplomacy | Game Mechanics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~24 |
| economy | Game Mechanics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~44 |
| equipment | Game Mechanics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~14 |
| inventory | Game Mechanics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~16 |
| loot | Game Mechanics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~25 |
| magic | Game Mechanics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~14 |
| **Simulation Systems** |
| world_generation | World Building | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~14 |
| world_state | World Building | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~26 |
| population | World Building | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~13 |
| region | World Building | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~19 |
| poi | World Building | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~23 |
| **Special Systems** |
| arc | Narrative | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~26 |
| chaos | Dynamic Events | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~38 |
| memory | AI/Context | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~29 |
| motif | Theme/Style | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~19 |
| religion | Cultural | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~21 |
| rumor | Information | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~19 |
| tension_war | Conflict | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~14 |
| time | Temporal | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ~15 |
| **Shared Components** |
| models | Domain Models | ✅ | - | - | - | - | ✅ | ~50 |
| repositories | Data Access | - | ✅ | ✅ | - | - | ✅ | ~40 |
| schemas | API Contracts | - | - | - | - | ✅ | ✅ | ~35 |
| rules | Business Rules | - | ✅ | - | - | - | ✅ | ~25 |

## Infrastructure Overview (/backend/infrastructure/)

| Component | Type | Models | Services | Purpose | Total Files |
|-----------|------|--------|----------|---------|-------------|
| **Technical Services** |
| analytics | Monitoring | ✅ | ✅ | Performance/usage tracking | ~13 |
| auth_user | Authentication | ✅ | ✅ | User auth & authorization | ~21 |
| storage | Data Storage | ✅ | ✅ | File/blob storage mgmt | ~14 |
| **Data & Integration** |
| data | Data Management | ✅ | ✅ | Core data operations | ~22 |
| events | Event System | ✅ | ✅ | Event sourcing/handling | ~73 |
| integration | External APIs | ✅ | ✅ | Third-party integrations | ~14 |
| **LLM System** |
| llm | AI/LLM Services | ✅ | ✅ | Hybrid LLM architecture | ~37 |
| **Utilities** |
| services | Core Services | ✅ | ✅ | Platform services | ~40 |
| shared | Shared Utilities | ✅ | ✅ | Common infrastructure | ~36 |

## Key Architectural Benefits

### 1. **Hybrid Domain Organization**
- **Shared Components:** Common domain models, repositories, schemas, and rules at the systems package level
- **Specialized Implementations:** System-specific logic within individual system directories
- **Clean Boundaries:** Clear separation between business logic and infrastructure

### 2. **Infrastructure Separation**
- **Technical Concerns:** Authentication, analytics, storage moved to infrastructure
- **Platform Services:** Event handling, integrations, shared utilities properly categorized
- **Scalability:** Infrastructure can be scaled independently of business logic

### 3. **LLM Integration**
- **Hybrid Architecture:** Local Ollama models + cloud fallbacks
- **Performance Optimized:** <2s response times, 80%+ cache hit rates
- **Multi-Provider Support:** Ollama, OpenAI, Anthropic, Perplexity
- **Context-Aware:** Different models for different content types

### 4. **Code Reuse & Maintainability**
- **Reduced Duplication:** Shared domain components prevent code repetition
- **Consistent Patterns:** Standardized approach across all systems
- **Easy Testing:** Clear boundaries make unit testing straightforward
- **Documentation:** Self-documenting structure through organization

## Import Patterns

### Business Logic Imports
```python
# Domain models (shared)
from backend.systems.models import Character, Quest, Faction

# System-specific components
from backend.systems.character.services import CharacterService
from backend.systems.quest.repositories import QuestRepository

# Infrastructure when needed
from backend.infrastructure.auth_user.services import AuthService
from backend.infrastructure.llm.services import LLMService
```

### Infrastructure Imports
```python
# Infrastructure components
from backend.infrastructure.analytics.services import AnalyticsService
from backend.infrastructure.events.services import EventService

# Cross-boundary to business logic (when appropriate)
from backend.systems.models import Character
from backend.systems.character.services import CharacterService
```

## Migration Status

✅ **Completed:**
- Directory restructuring (systems vs infrastructure)
- Import path updates (338 files updated)
- Development Bible canonical model update
- LLM hybrid architecture implementation

🔄 **In Progress:**
- Systems inventory documentation update
- Test coverage validation
- Performance optimization

📋 **Next Steps:**
- Final integration testing
- Documentation finalization
- Playtesting preparation (Task #58)

## Quality Metrics

- **Test Coverage:** Target ≥90% for all components
- **Import Compliance:** 100% canonical imports
- **Architecture Compliance:** All components follow hybrid model
- **Performance:** LLM <2s response times, 5 concurrent users
- **Maintainability:** Clear separation of concerns

This hybrid architecture provides the best of both worlds: shared domain components for code reuse and consistency, while maintaining clear system boundaries and separation of technical infrastructure from business logic.