# Diplomacy Service Migration Guide

## Overview

The diplomacy system has been consolidated to eliminate service duplication and provide a unified interface. This guide explains how to migrate existing code to use the new architecture.

## Key Changes

### Service Consolidation

**Before:** Multiple conflicting services
- `services/core_services.py`: Full diplomatic operations
- `services/diplomacy_service.py`: Simple CRUD wrapper
- `services/services.py`: Another complete implementation

**After:** Single unified service
- `services/unified_diplomacy_service.py`: Comprehensive service with all functionality
- Legacy services now act as facades for backward compatibility

### Model Consolidation

**Before:** Conflicting model definitions
- `models/models.py`: Basic diplomatic models
- `models/core_models.py`: Comprehensive diplomatic entities  
- `models/diplomacy_model.py`: Alternative model structure

**After:** Authoritative model source
- `models/core_models.py`: Primary model definitions for all diplomatic entities
- Legacy models maintained for compatibility

## Migration Steps

### 1. Update Imports

**Old imports:**
```python
# Various old import patterns
from backend.systems.diplomacy.services.core_services import DiplomacyService
from backend.systems.diplomacy.services.diplomacy_service import DiplomacyService  
from backend.systems.diplomacy.services.services import DiplomacyService
```

**New recommended import:**
```python
# Preferred - uses unified service
from backend.systems.diplomacy import DiplomacyService

# Or explicitly import unified service
from backend.systems.diplomacy.services.unified_diplomacy_service import UnifiedDiplomacyService
```

### 2. Service Initialization

**Old patterns:**
```python
# Various initialization methods
service = DiplomacyService(repository)
service = DiplomacyService(db_session)
service = create_diplomacy_service(db_session)
```

**New unified pattern:**
```python
# Unified initialization
from backend.systems.diplomacy import create_unified_diplomacy_service

service = create_unified_diplomacy_service(repository=repo, db_session=session)
# or
service = UnifiedDiplomacyService(repository=repo, db_session=session)
```

### 3. Model Imports

**Old imports:**
```python
from backend.systems.diplomacy.models.models import DiplomacyModel
from backend.systems.diplomacy.models.diplomacy_model import DiplomacyModel
```

**New recommended imports:**
```python
# For comprehensive diplomatic operations
from backend.systems.diplomacy import Treaty, Negotiation, DiplomaticIncident

# For legacy CRUD operations (backward compatibility)
from backend.systems.diplomacy.models.diplomacy_model import DiplomacyModel
```

## API Reference

### Unified Service Capabilities

The `UnifiedDiplomacyService` provides three levels of functionality:

#### 1. Comprehensive Diplomatic Operations
Full diplomatic functionality including treaties, negotiations, incidents, etc.

```python
# Treaty management
treaty = service.create_treaty(name, treaty_type, parties, terms)
treaties = service.list_treaties(faction_id=faction_id, active_only=True)

# Negotiation management  
negotiation = service.start_negotiation(parties, initiator_id, treaty_type)
service.make_offer(negotiation_id, faction_id, terms)
service.accept_offer(negotiation_id, faction_id)

# Relationship management
relationship = service.get_faction_relationship(faction_a, faction_b)
service.update_faction_tension(faction_a, faction_b, tension_change, reason)

# Incident management
incident = service.create_diplomatic_incident(incident_type, perpetrator, victim, description)

# Treaty violations
violation = service.report_treaty_violation(treaty_id, violator_id, violation_type, description, evidence, reported_by)
violations = service.enforce_treaties_automatically()
```

#### 2. Legacy CRUD Operations
Simple entity management for backward compatibility.

```python
# Basic CRUD operations (maintains old interface)
entity = service.get_diplomacy(diplomacy_id)
entities = service.get_all_diplomacys()
entity = service.create_diplomacy(diplomacy_data)
entity = service.update_diplomacy(diplomacy_id, updates)
success = service.delete_diplomacy(diplomacy_id)
```

#### 3. Modern Async Operations
Enhanced async interface for new developments.

```python
# Modern async interface
response = await service.create_diplomacy_async(request, user_id)
response = await service.get_diplomacy_by_id_async(diplomacy_id)
```

### Service Status

Check service health and capabilities:

```python
status = service.get_service_status()
print(status['capabilities'])  # Shows available functionality
```

## Backward Compatibility

### Legacy Service Facades

All existing services continue to work as facades:

```python
# These still work but delegate to unified service
from backend.systems.diplomacy.services.diplomacy_service import DiplomacyService as LegacyCRUD
from backend.systems.diplomacy.services.services import DiplomacyService as AsyncService

legacy_service = LegacyCRUD(db_session)
async_service = AsyncService(db_session)
```

### Model Compatibility

Legacy model definitions are preserved:

```python
# Still works for basic operations
from backend.systems.diplomacy.models.diplomacy_model import DiplomacyModel
from backend.systems.diplomacy.models.models import DiplomacyEntity, DiplomacyResponse
```

## Migration Timeline

### Phase 1: Immediate (No Breaking Changes)
- All existing code continues to work unchanged
- Legacy services act as facades to unified service
- Begin updating new code to use unified service

### Phase 2: Gradual Migration (Recommended)
- Update import statements to use unified service
- Migrate complex diplomatic operations to comprehensive API
- Keep simple CRUD operations on legacy interface if needed

### Phase 3: Full Migration (Optional)
- Convert all code to use unified service directly
- Deprecate legacy facade services
- Remove duplicate model definitions

## Examples

### Before: Complex service management
```python
# Old way - multiple services needed
from backend.systems.diplomacy.services.core_services import DiplomacyService, TensionService

diplomacy_service = DiplomacyService(repository)
tension_service = TensionService(repository)

# Create treaty
treaty = diplomacy_service.create_treaty(...)
# Update relationships  
tension_service.update_faction_tension(...)
```

### After: Single unified service
```python
# New way - one service for everything
from backend.systems.diplomacy import DiplomacyService

service = DiplomacyService(repository=repository, db_session=session)

# Create treaty
treaty = service.create_treaty(...)
# Update relationships
service.update_faction_tension(...)
```

## Testing Migration

### Verification Steps

1. **Import Verification:**
   ```python
   # Test all import patterns work
   from backend.systems.diplomacy import DiplomacyService
   from backend.systems.diplomacy.services.unified_diplomacy_service import UnifiedDiplomacyService
   assert DiplomacyService == UnifiedDiplomacyService
   ```

2. **Functionality Verification:**
   ```python
   # Test service capabilities
   service = DiplomacyService()
   status = service.get_service_status()
   assert status['status'] == 'active'
   assert status['capabilities']['treaty_management'] == True
   ```

3. **Legacy Compatibility Verification:**
   ```python
   # Test legacy services still work
   from backend.systems.diplomacy.services.diplomacy_service import DiplomacyService as Legacy
   legacy = Legacy(db_session)
   entities = legacy.get_all_diplomacys()  # Should not error
   ```

## Support

For migration questions or issues:
1. Check this guide for common patterns
2. Review the unified service API documentation
3. Test legacy facade functionality before migrating
4. Use gradual migration approach to minimize risk

## Summary

The unified diplomacy service provides:
- ✅ All functionality from previous services
- ✅ Backward compatibility via facades  
- ✅ Single point of entry for diplomatic operations
- ✅ Consistent API across all diplomatic functionality
- ✅ Enhanced capabilities for new features

Migration is optional but recommended for cleaner, more maintainable code. 