# Task 42 Action Plan: Backend Development Protocol

## 🎯 Immediate Actions Required

### 1. Fix Import Issues (457 total)

**File**: `/Users/Sharrone/Dreamforge/backend/systems/economy/__init__.py`
**Line**: 18
**Change**: 
```python
# From:
from .economy_manager import EconomyManager

# To:
from backend.systems.economy_manager import EconomyManager
```

**File**: `/Users/Sharrone/Dreamforge/backend/systems/economy/__init__.py`
**Line**: 19
**Change**: 
```python
# From:
from .routers.shop_router import router as shop_router

# To:
from backend.systems.routers.shop_router import router as shop_router
```

**File**: `/Users/Sharrone/Dreamforge/backend/systems/economy/__init__.py`
**Line**: 20
**Change**: 
```python
# From:
from .routers.economy_router import router as economy_router

# To:
from backend.systems.routers.economy_router import router as economy_router
```

**File**: `/Users/Sharrone/Dreamforge/backend/systems/economy/__init__.py`
**Line**: 23
**Change**: 
```python
# From:
from .models import (

# To:
from backend.systems.models import (
```

**File**: `/Users/Sharrone/Dreamforge/backend/systems/economy/__init__.py`
**Line**: 37
**Change**: 
```python
# From:
from .services import (

# To:
from backend.systems.services import (
```

### 2. Relocate Test Files (41 issues)
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_river_generator.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_world_manager.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_biome_utils.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_coastline_utils.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_components.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_world_generation_utils.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_service_utils.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_optimized_worldgen.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_router.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_modding_system.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_poi_generator.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_regional_features.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_elevation_utils.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_resource_utils.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_continent_repository.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_world_utils.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_world_generator.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_seed_loader.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_config.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_worldgen_routes.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_api.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_events.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_worldgen_routes_endpoints.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_initialize_modding.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_continent_service.py` to appropriate `/backend/tests/systems/` directory
- Move `/Users/Sharrone/Dreamforge/backend/tests/test_settlement_service.py` to appropriate `/backend/tests/systems/` directory

### 3. Remove Duplicate Tests
- Remove duplicate `test_utils_comprehensive.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/poi/test_utils_comprehensive.py, /Users/Sharrone/Dreamforge/backend/tests/systems/region/test_utils_comprehensive.py
- Remove duplicate `test_quest_integration.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/dialogue/test_quest_integration.py, /Users/Sharrone/Dreamforge/backend/tests/systems/quest/test_quest_integration.py
- Remove duplicate `test_utils.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/dialogue/test_utils.py, /Users/Sharrone/Dreamforge/backend/tests/systems/inventory/test_utils.py
- Remove duplicate `test_utils_comprehensive.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/poi/test_utils_comprehensive.py, /Users/Sharrone/Dreamforge/backend/tests/systems/inventory/test_utils_comprehensive.py
- Remove duplicate `test_optimized_worldgen.py` from: /Users/Sharrone/Dreamforge/backend/tests/test_optimized_worldgen.py, /Users/Sharrone/Dreamforge/backend/tests/systems/world_state/test_optimized_worldgen.py
- Remove duplicate `test_world_utils.py` from: /Users/Sharrone/Dreamforge/backend/tests/test_world_utils.py, /Users/Sharrone/Dreamforge/backend/tests/systems/world_state/test_world_utils.py
- Remove duplicate `test_services.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/poi/test_services.py, /Users/Sharrone/Dreamforge/backend/tests/systems/arc/test_services.py
- Remove duplicate `test_repositories.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/auth_user/unit/test_repositories.py, /Users/Sharrone/Dreamforge/backend/tests/systems/arc/test_repositories.py
- Remove duplicate `test_quest_integration.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/dialogue/test_quest_integration.py, /Users/Sharrone/Dreamforge/backend/tests/systems/arc/test_quest_integration.py
- Remove duplicate `test_routers.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/region/test_routers.py, /Users/Sharrone/Dreamforge/backend/tests/systems/arc/test_routers.py
- Remove duplicate `test_integration.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/crafting/test_integration.py, /Users/Sharrone/Dreamforge/backend/tests/systems/arc/test_integration.py
- Remove duplicate `test_utils.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/dialogue/test_utils.py, /Users/Sharrone/Dreamforge/backend/tests/systems/analytics/test_utils.py
- Remove duplicate `test_models.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/arc/test_models.py, /Users/Sharrone/Dreamforge/backend/tests/systems/analytics/test_models.py
- Remove duplicate `test_schemas.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/crafting/test_schemas.py, /Users/Sharrone/Dreamforge/backend/tests/systems/analytics/test_schemas.py
- Remove duplicate `test_event_integration.py` from: /Users/Sharrone/Dreamforge/backend/tests/systems/world_state/test_event_integration.py, /Users/Sharrone/Dreamforge/backend/tests/systems/analytics/test_event_integration.py

## 📋 Next Tasks (43-53)

### Task 43: Extract API Contracts
- Parse all 438 endpoints
- Generate OpenAPI 3.0 specification
- Include request/response schemas, error codes, versioning

### Task 44: Identify Incomplete Endpoints
- Audit API implementations against contracts
- Document missing functionality
- Prioritize based on Unity frontend dependencies

### Task 45: Create Mock Data Fixtures
- Generate realistic JSON fixtures for all endpoints
- Include edge cases and error responses
- Organize by system for maintainability

### Task 46-49: Mock Server and Unity Integration
- Build Flask/JSON Server for development
- Generate C# DTOs for Unity
- Implement MockClient for frontend testing
- Create Unity test scenes

### Task 50-53: Arc Engine and Integration
- Implement core arc functions
- Add comprehensive testing
- Replace mocks with real implementations
- Run full integration testing

## 🛠️ Implementation Commands

### Fix Imports
```bash
# Run canonical import fixes
python backend/fix_canonical_imports.py

# Verify no relative imports remain
grep -r "from \.\." backend/systems/
```

### Organize Tests
```bash
# Move misplaced tests
python backend/organize_test_files.py

# Remove duplicates
python backend/remove_duplicate_tests.py
```

### Validate Structure
```bash
# Run comprehensive tests
pytest --cov=backend.systems --cov-report=html

# Check compliance
python backend/validate_development_bible.py
```

---

**Status**: Ready for implementation
**Next**: Execute action plan and proceed to Task 43
