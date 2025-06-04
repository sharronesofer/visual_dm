# Religion Infrastructure Separation Summary

## Overview
This document summarizes the separation of business logic from technical infrastructure in the religion system, following the established pattern of maintaining strict separation between `/backend/systems` (business logic) and `/backend/infrastructure` (technical functionality).

## Components Moved to Infrastructure

### 1. API Routers (`/routers/`)
**Moved from:** `backend/systems/religion/routers/`  
**Moved to:** `backend/infrastructure/religion/routers/`  
**Reason:** API endpoint definitions are technical infrastructure, not business logic.

**Files moved:**
- `religion_router.py` - FastAPI endpoints for religion CRUD operations
- `websocket_routes.py` - WebSocket endpoints for real-time updates
- `__init__.py` - Router module initialization

### 2. Data Repositories (`/repositories/`)
**Moved from:** `backend/systems/religion/repositories/`  
**Moved to:** `backend/infrastructure/religion/repositories/`  
**Reason:** Data access layer is technical infrastructure.

**Files moved:**
- `repository.py` - SQLAlchemy-based data repository
- `__init__.py` - Repository module initialization

### 3. API Schemas (`/schemas/`)
**Moved from:** `backend/systems/religion/schemas/`  
**Moved to:** `backend/infrastructure/religion/schemas/`  
**Reason:** API schemas are technical infrastructure for data serialization.

**Files moved:**
- `schemas.py` - Pydantic schemas for API endpoints
- `__init__.py` - Schema module initialization

### 4. Event Infrastructure (`/events/`)
**Moved from:** `backend/systems/religion/events/`  
**Moved to:** `backend/infrastructure/religion/events/`  
**Reason:** Event publishing and handling is technical infrastructure.

**Files moved:**
- `event_publisher.py` - Centralized event publisher
- `religion_events.py` - Event type definitions and classes
- `__init__.py` - Events module initialization

### 5. WebSocket Management (`/websocket/`)
**Moved from:** `backend/systems/religion/websocket_manager.py`  
**Moved to:** `backend/infrastructure/religion/websocket/websocket_manager.py`  
**Reason:** WebSocket communication is technical infrastructure.

**Files moved:**
- `websocket_manager.py` - Real-time WebSocket communication manager
- `__init__.py` - WebSocket module initialization

## Components Remaining in Systems (Business Logic)

### 1. Business Models (`/models/`)
**Location:** `backend/systems/religion/models/`  
**Reason:** Contains business entities and domain logic.

**Files:**
- `models.py` - Business entities, request/response models
- `exceptions.py` - Business domain exceptions
- `__init__.py` - Models module initialization

### 2. Business Services (`/services/`)
**Location:** `backend/systems/religion/services/`  
**Reason:** Contains core business logic and domain operations.

**Files:**
- `services.py` - Core religion business logic service
- `narrative_service.py` - Business logic for narrative generation
- `__init__.py` - Services module initialization

### 3. Business Utilities (`/utils/`)
**Location:** `backend/systems/religion/utils/`  
**Reason:** Contains business logic utility functions.

**Files:**
- `utils.py` - Business logic utilities
- `__init__.py` - Utils module initialization

### 4. Domain Exceptions
**Location:** `backend/systems/religion/exceptions.py`  
**Reason:** Business domain exceptions belong with business logic.

## Import Updates Made

### 1. Infrastructure Components
Updated all moved infrastructure components to import business logic from systems:

```python
# Example: In infrastructure/religion/routers/religion_router.py
from backend.systems.religion.models import CreateReligionRequest, ReligionResponse
from backend.systems.religion.services import ReligionService
from backend.systems.religion.models.exceptions import ReligionNotFoundError
```

### 2. Business Logic Components
Updated business logic components to import infrastructure from new locations:

```python
# Example: In systems/religion/services/services.py
from backend.infrastructure.religion.repositories import ReligionRepository
from backend.infrastructure.religion.events.event_publisher import get_religion_event_publisher
```

### 3. Test Files
Updated test files to import from correct locations:

```python
# Example: In tests/systems/religion/test_services.py
from backend.infrastructure.religion.repositories.repository import ReligionRepository
```

### 4. External Integration Files
Updated external files that were importing from old locations:

```python
# Example: In scripts/test_frontend_integration.py
from backend.infrastructure.religion.schemas.schemas import ReligionSchema
from backend.infrastructure.religion.websocket.websocket_manager import religion_websocket_manager
```

## Circular Import Resolution

### Issue
Initial implementation caused circular imports because:
1. Infrastructure routers imported business services
2. Business services imported infrastructure repositories
3. Infrastructure main module imported routers

### Solution
Removed routers from the main infrastructure `__init__.py` to break the circular dependency:

```python
# backend/infrastructure/religion/__init__.py
# Removed: from .routers import *
# Routers should be imported directly when needed
```

## Benefits Achieved

### 1. Clear Separation of Concerns
- **Business Logic:** Pure domain logic in `/systems/religion/`
- **Technical Infrastructure:** API, data access, events, WebSocket in `/infrastructure/religion/`

### 2. Improved Maintainability
- Changes to API endpoints don't affect business logic
- Changes to business logic don't require infrastructure changes
- Clear dependency direction: Infrastructure depends on Systems, not vice versa

### 3. Better Testability
- Business logic can be tested independently of infrastructure
- Infrastructure components can be mocked for business logic tests
- Clear boundaries for unit vs integration tests

### 4. Consistent Architecture
- Follows the same pattern as other systems in the codebase
- Maintains architectural consistency across the application

## Verification

All imports have been tested and verified to work correctly:

```bash
# Business logic imports
python -c "from systems.religion.services import ReligionService; print('Success')"

# Infrastructure imports  
python -c "from infrastructure.religion.repositories import ReligionRepository; print('Success')"
python -c "from infrastructure.religion.routers import religion_router; print('Success')"
```

## Future Considerations

1. **New Components:** Any new religion system components should follow this separation:
   - Business logic → `/backend/systems/religion/`
   - Technical infrastructure → `/backend/infrastructure/religion/`

2. **Import Guidelines:** 
   - Infrastructure can import from systems
   - Systems should not import from infrastructure (except for dependency injection)
   - Use dependency injection for infrastructure services in business logic

3. **Testing Strategy:**
   - Unit tests for business logic should mock infrastructure dependencies
   - Integration tests should test the full stack including infrastructure

This separation ensures the religion system follows clean architecture principles and maintains consistency with the rest of the codebase. 