# Diplomacy System Infrastructure Migration Guide

## Overview

This document describes the migration of infrastructure components from the global infrastructure layer into the diplomacy system for better encapsulation and system independence.

## What Was Moved

### 1. Database Models (SQLAlchemy)

**From:** `backend/infrastructure/database/models/diplomacy_models.py`  
**To:** `backend/systems/diplomacy/db_models/diplomacy_models.py`

**Models Moved:**
- `DiplomaticRelationship`
- `Treaty`
- `Negotiation`
- `NegotiationOffer`
- `DiplomaticEvent`
- `TreatyViolation`
- `DiplomaticIncident`
- `Ultimatum`
- `Sanction`
- `Base` (as `DiplomacyBase`)

### 2. API Schemas (Pydantic)

**From:** `backend/infrastructure/schemas/diplomacy_schemas.py`  
**To:** `backend/systems/diplomacy/schemas/diplomacy_schemas.py`

**Schemas Moved:**
- Treaty schemas: `TreatyCreate`, `TreatyUpdate`, `TreatySchema`
- Negotiation schemas: `NegotiationCreate`, `NegotiationUpdate`, `NegotiationSchema`
- Event schemas: `DiplomaticEventCreate`, `DiplomaticEventSchema`
- Relationship schemas: `FactionRelationshipSchema`
- Violation schemas: `TreatyViolationCreate`, `TreatyViolationUpdate`, `TreatyViolationSchema`
- Incident schemas: `DiplomaticIncidentCreate`, `DiplomaticIncidentUpdate`, `DiplomaticIncidentSchema`
- Ultimatum schemas: `UltimatumCreate`, `UltimatumUpdate`, `UltimatumSchema`
- Sanction schemas: `SanctionCreate`, `SanctionUpdate`, `SanctionSchema`, `SanctionViolationRecord`

## Updated Import Paths

### Database Models

**Before:**
```python
from backend.infrastructure.database.models.diplomacy_models import (
    DiplomaticRelationship, Treaty, Negotiation
)
```

**After:**
```python
from backend.systems.diplomacy.db_models import (
    DiplomaticRelationship, Treaty, Negotiation
)
```

**Or from system root:**
```python
from backend.systems.diplomacy import (
    DiplomaticRelationship, DiplomacyBase
)
```

### API Schemas

**Before:**
```python
from backend.infrastructure.schemas.diplomacy_schemas import (
    TreatyCreate, TreatySchema, NegotiationCreate
)
```

**After:**
```python
from backend.systems.diplomacy.schemas import (
    TreatyCreate, TreatySchema, NegotiationCreate
)
```

**Or from system root:**
```python
from backend.systems.diplomacy import (
    TreatyCreate, TreatySchema, NegotiationCreate
)
```

## Benefits of Migration

### 1. Better Encapsulation
- Diplomacy system is now self-contained
- Reduced coupling with infrastructure layer
- Clear separation of concerns

### 2. Easier Testing
- Can test diplomacy system in isolation
- Simpler mock setups
- Better unit test coverage

### 3. Improved Maintainability
- Diplomacy-specific models and schemas are co-located
- Easier to understand system boundaries
- Simplified dependency management

### 4. System Independence
- Diplomacy system can evolve independently
- Reduced risk of breaking changes from infrastructure updates
- Clearer API contracts

## What Wasn't Changed

### 1. Repositories
- Repository pattern already properly implemented
- Repositories delegate to infrastructure layer appropriately
- No changes needed to repository interfaces

### 2. Routers
- Main router was already comprehensive (279 lines)
- Properly uses dependency injection
- API endpoints well-organized by functional area

### 3. Core Models
- Business logic models remain in `models/core_models.py`
- These are separate from database models
- Maintain clean separation between business and persistence

## Backward Compatibility

### Infrastructure Layer
The original files in the infrastructure layer should be considered **deprecated** but are temporarily maintained for compatibility:

- `backend/infrastructure/database/models/diplomacy_models.py` → Use `backend/systems/diplomacy.db_models` instead
- `backend/infrastructure/schemas/diplomacy_schemas.py` → Use `backend.systems.diplomacy.schemas` instead

### Gradual Migration
External systems can gradually migrate to use the new import paths:

1. **Phase 1:** Update new code to use diplomacy system imports
2. **Phase 2:** Update existing code during maintenance
3. **Phase 3:** Remove deprecated infrastructure files

## Verification

### Test Import Paths
```python
# Test database models
from backend.systems.diplomacy.db_models import DiplomaticRelationship, Treaty
from backend.systems.diplomacy import DiplomaticRelationship, DiplomacyBase

# Test schemas
from backend.systems.diplomacy.schemas import TreatyCreate, TreatySchema
from backend.systems.diplomacy import TreatyCreate, TreatySchema

# Test system exports
from backend.systems.diplomacy import (
    UnifiedDiplomacyService,
    DiplomaticStatus,
    TreatyType,
    DiplomaticRelationship,
    TreatyCreate
)
```

### Integration Testing
- All existing API endpoints should continue to work
- Repository operations should function correctly
- Database migrations should be unaffected

## Future Considerations

### 1. Complete Infrastructure Independence
- Consider implementing diplomacy-specific database session management
- Evaluate need for diplomacy-specific migration system
- Assess potential for dedicated diplomacy database

### 2. API Versioning
- Implement API versioning for diplomacy endpoints
- Use schemas for proper API contract management
- Consider GraphQL for complex diplomatic queries

### 3. Event-Driven Architecture
- Implement diplomacy-specific event bus
- Use events for inter-system communication
- Reduce direct coupling with other systems

## Migration Checklist

- [x] Move database models to `db_models/`
- [x] Move API schemas to `schemas/`
- [x] Update imports in schemas
- [x] Update system exports in `__init__.py`
- [x] Create migration documentation
- [ ] Update external systems to use new imports (gradual)
- [ ] Create deprecation warnings for old imports
- [ ] Remove deprecated infrastructure files (future)

## Contact

For questions about this migration or issues with the new import paths, please refer to the diplomacy system documentation or contact the development team. 