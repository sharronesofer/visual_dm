# Architecture Refactoring Summary: Dialogue System

## Overview
Refactored the dialogue system to maintain strict separation between business logic and infrastructure concerns.

## Components Moved from `/backend/systems/dialogue` to `/backend/infrastructure/dialogue`

### 1. **Routers** (`routers/`)
- **File**: `websocket_routes.py`
- **Reason**: WebSocket endpoints and HTTP routes are infrastructure concerns
- **New Location**: `backend/infrastructure/dialogue/routers/`
- **Impact**: Updated import in `backend/main.py`

### 2. **Schemas** (`schemas/`)
- **File**: `dialogue_schemas.py`
- **Reason**: API request/response validation schemas are data transfer layer (infrastructure)
- **New Location**: `backend/infrastructure/dialogue/schemas/`
- **Impact**: Updated import in `latency_service.py`

### 3. **Events** (`events/`)
- **File**: `dialogue_events.py`
- **Reason**: Event bus integration and WebSocket communication events are infrastructure
- **New Location**: `backend/infrastructure/dialogue/events/`
- **Impact**: Updated imports in `latency_service.py` and `dialogue_system_new.py`

### 4. **Latency Service** (`services/latency_service.py`)
- **File**: `latency_service.py`
- **Reason**: Contains WebSocket management, real-time communication, and infrastructure dependencies
- **New Location**: `backend/infrastructure/dialogue/latency_service.py`
- **Impact**: Updated import in `websocket_routes.py`

### 5. **Text Utilities** (`utils/text_utils.py`)
- **File**: `text_utils.py`
- **Reason**: General text processing utilities are infrastructure utilities, not dialogue-specific business logic
- **New Location**: `backend/infrastructure/utils/text_utils.py`
- **Impact**: Updated import in `backend/systems/dialogue/utils/__init__.py`

## Components That Remained in `/backend/systems/dialogue` (Business Logic)

### 1. **Models** (`models/`)
- Business entities and domain models for dialogue
- Contains dialogue context, conversation state, and business rules

### 2. **Services** (`services/`)
- Core dialogue business logic
- Integration services with other business systems (memory, rumor, motif, etc.)
- Dialogue generation and conversation management

### 3. **Integration Files** (root level)
- `motif_integration.py` - Business logic for narrative motif tracking
- `rumor_integration.py` - Business logic for rumor system integration  
- `memory_integration.py` - Business logic for memory system integration

### 4. **Business Logic Utilities**
- `scoring.py` - Dialogue quality assessment and relevance scoring
- `extractors.py` - Information extraction for game purposes
- `utils/` - Dialogue-specific business utilities (now imports from infrastructure)

### 5. **Repositories** (`repositories/`)
- Data access layer for dialogue business entities

## Updated Import Statements

### Main Application
```python
# OLD
from backend.systems.dialogue.routers import dialogue_websocket_router

# NEW  
from backend.infrastructure.dialogue.routers import dialogue_websocket_router
```

### Latency Service
```python
# OLD
from backend.systems.dialogue.events import DialogueEventEmitter, DialogueLatencyEvent
from backend.systems.dialogue.schemas.dialogue_schemas import LatencyResponseSchema

# NEW
from backend.infrastructure.dialogue.events import DialogueEventEmitter, DialogueLatencyEvent
from backend.infrastructure.dialogue.schemas.dialogue_schemas import LatencyResponseSchema
```

### Dialogue System Services
```python
# OLD
from backend.systems.dialogue.events import DialogueEventEmitter, DialogueStartedEvent, DialogueMessageEvent, DialogueEndedEvent

# NEW
from backend.infrastructure.dialogue.events import DialogueEventEmitter, DialogueStartedEvent, DialogueMessageEvent, DialogueEndedEvent
```

### WebSocket Routes
```python
# OLD
from backend.systems.dialogue.services.latency_service import get_dialogue_latency_service

# NEW
from backend.infrastructure.dialogue.latency_service import get_dialogue_latency_service
```

### Text Utils
```python
# OLD
from .text_utils import (...)

# NEW
from backend.infrastructure.utils.text_utils import (...)
```

## New Infrastructure Module Structure

```
backend/infrastructure/dialogue/
├── __init__.py                 # Module exports
├── latency_service.py         # Real-time latency management
├── routers/
│   ├── __init__.py
│   └── websocket_routes.py    # WebSocket endpoints
├── schemas/
│   ├── __init__.py
│   └── dialogue_schemas.py    # API validation schemas
└── events/
    ├── __init__.py
    └── dialogue_events.py     # Event bus integration
```

## Benefits Achieved

1. **Clear Separation of Concerns**: Business logic is now isolated from infrastructure
2. **Better Maintainability**: Infrastructure changes don't affect business rules
3. **Improved Testability**: Business logic can be tested independently of infrastructure
4. **Architectural Consistency**: Follows the established pattern across the codebase
5. **Reduced Coupling**: Business logic no longer depends on WebSocket or API concerns

## Verification

All moved components have been tested and import correctly from their new locations:
- ✅ Router imports work in main application
- ✅ Event system integration functions correctly  
- ✅ Latency service imports and initializes properly
- ✅ Text utilities are accessible from business logic layer
- ✅ Schemas are available for API validation

## Next Steps

1. Update any remaining documentation that references old paths
2. Consider similar refactoring for other systems that may have mixed concerns
3. Add integration tests to ensure the refactored components work together correctly 