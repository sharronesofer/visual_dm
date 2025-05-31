# Backend Development Protocol

## Overview
This document establishes the comprehensive protocol for all backend development work, ensuring consistency, quality, and compliance with the project's architectural standards.

## Assessment and Error Resolution

### System Analysis Requirements
- **Target Systems**: Run comprehensive analysis on all systems under `/backend/systems/` and `/backend/tests/`
- **Error Detection**: When errors occur, determine whether the test or source module violates `Development_Bible.md` and correct accordingly
- **Missing Logic**: Implement missing logic in modules with direct reference to `Development_Bible.md`
- **Architecture Reference**: Reference `backend/backend_systems_inventory.md` for system architecture and API endpoints

### Analysis Tools
- Use comprehensive code search (grep/ripgrep) to identify patterns and dependencies
- Perform exhaustive searches before implementing new functionality
- Review existing implementations in `/backend/systems/*` to avoid duplication

## Structure and Organization Enforcement

### Test File Organization
- **Canonical Location**: All test files MUST reside under `/backend/tests/*`
- **Invalid Locations**: Tests located elsewhere are invalid and must be relocated
- **Cleanup Requirements**: 
  - Delete or relocate test files found in `/backend/systems/*/test(s)` directories
  - Remove empty `test(s)` folders after relocation
  - Identify and delete duplicate tests
- **Hierarchy Compliance**: Ensure all code follows canonical `/backend/systems/` organization hierarchy

### Directory Structure Standards
```
/backend/
├── systems/
│   ├── {system_name}/
│   │   ├── models/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── utils/
│   └── shared/
│       └── database/
└── tests/
    └── systems/
        └── {system_name}/
```

## Canonical Imports Enforcement

### Import Standards
- **Canonical References**: All imports MUST reference canonical implementations within `/backend/systems/*`
- **External Dependencies**: Any imports from outside `/backend/systems` (e.g., utility modules located elsewhere) must be redirected or inlined according to the canonical hierarchy
- **Orphan Elimination**: Eliminate orphan or non-canonical module dependencies
- **Format Standard**: Convert all imports to canonical `backend.systems.*` format

### Import Examples
```python
# ✅ CORRECT - Canonical imports
from backend.systems.character.models.character import Character
from backend.systems.shared.database.base import BaseRepository
from backend.systems.events.event_dispatcher import EventDispatcher

# ❌ INCORRECT - Non-canonical imports
from utils.visual.visual_model import CharacterModel
from backend.character.models import Character
from shared.database import BaseRepository
```

## Module and Function Development

### Duplication Prevention
- **Pre-Implementation Search**: Before implementing new functions or modules, perform exhaustive searches to confirm no existing implementation exists
- **Review Process**: Avoid accidental duplication by reviewing `/backend/systems/*` thoroughly
- **Inventory Reference**: Consult `backend/backend_systems_inventory.md` for existing API endpoints and functionality
- **Documentation Check**: Reference existing documentation and implementation patterns

### New Module Creation Standards

#### Architectural Compliance
- **Primary Reference**: Reference `Development_Bible.md` at `/docs/Development_Bible.md` for all architectural decisions
- **Framework Standards**: Follow FastAPI conventions strictly for routing, dependencies, and async patterns
- **Integration Requirements**: Ensure new modules are compatible with:
  - WebSocket-based communication
  - Unity (2D, runtime-generated) frontend seamless integration
  - Existing event system and data flow
- **Location Requirement**: All backend code MUST reside within `/backend/` directory structure

#### Implementation Patterns
```python
# FastAPI Router Example
from fastapi import APIRouter, Depends, HTTPException
from backend.systems.shared.database.base import get_db_session
from backend.systems.{system}.services.{service} import {Service}

router = APIRouter(prefix="/{system}", tags=["{system}"])

@router.post("/", response_model={Schema})
async def create_{entity}(
    data: {CreateSchema},
    db: AsyncSession = Depends(get_db_session),
    service: {Service} = Depends(get_{service})
):
    # Implementation with proper error handling
    pass
```

### Data and Schema Standards

#### JSON Schema Management
- **Template Storage**: Use `.json` files for modding templates or structured modular data (e.g., biomes, land types)
- **Location Standard**: Place all JSON schemas in `/data/builders/` directory
- **Pydantic Integration**: Create corresponding Pydantic models for all JSON schemas in appropriate system
- **Validation Implementation**: Implement comprehensive validation for all data inputs and API endpoints

#### Schema Examples
```python
# Pydantic Model with Validation
from pydantic import BaseModel, validator
from typing import Optional, List

class {Entity}Schema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v.strip()

    class Config:
        orm_mode = True
```

## Quality and Integration Standards

### Coverage and Testing Requirements
- **Coverage Target**: Achieve ≥90% test coverage for all modified/new components
- **Compatibility Verification**: Verify cross-system compatibility and communication
- **Contract Compliance**: Ensure API endpoints match established contracts and schemas
- **Frontend Integration**: Test WebSocket compatibility and JSON serialization for Unity frontend

### Testing Standards
```python
# Test Example with Proper Coverage
import pytest
from backend.systems.{system}.services.{service} import {Service}

class Test{Service}:
    @pytest.fixture
    async def service(self, db_session):
        return {Service}(db_session)
    
    async def test_create_{entity}_success(self, service, sample_data):
        # Test implementation with assertions
        result = await service.create_{entity}(sample_data)
        assert result is not None
        assert result.id is not None
        # Additional assertions...
    
    async def test_create_{entity}_validation_error(self, service):
        # Test error scenarios
        with pytest.raises(ValidationError):
            await service.create_{entity}({})
```

### Documentation and Maintenance
- **Documentation Updates**: Update relevant documentation and API specifications
- **Organization Standards**: Maintain clean, logical file and function organization
- **Error Handling**: Implement comprehensive error handling and logging
- **Scalability Design**: Ensure code is structured for future expansion and scalability

## Implementation Autonomy Directive

### Decision Making Authority
- **Full Control**: Assume full control over structural and implementation decisions within protocol bounds
- **No User Dependencies**: Never require user clarification or input for technical implementation details
- **Direct Implementation**: Implement changes directly and iterate until completion
- **Tool Utilization**: Utilize all available CLI tools, code search, file operations, and testing utilities as needed

### Completion Standards
- **Iteration Requirement**: Continue refining implementation until all tests pass and coverage targets are met
- **Compatibility Maintenance**: Maintain compatibility with existing systems and preserve API contracts unless explicitly updating them
- **Quality Assurance**: Ensure all implementations meet or exceed established quality standards

### Implementation Workflow
1. **Analysis Phase**: Comprehensive system analysis and gap identification
2. **Planning Phase**: Detailed implementation plan with dependencies mapped
3. **Implementation Phase**: Direct code implementation following all standards
4. **Testing Phase**: Comprehensive test implementation and validation
5. **Integration Phase**: Cross-system integration testing and validation
6. **Documentation Phase**: Update all relevant documentation and specifications

## Reference Documents

### Primary Standards
- **Development Bible**: `/docs/Development_Bible.md` - Primary architectural and implementation standard
- **System Inventory**: `backend/backend_systems_inventory.md` - System architecture and API endpoints reference
- **Development Protocol**: `backend/backend_development_protocol.md` - This document
- **API Contracts**: `api_contracts.yaml` - API specification and contracts (when available)

### Supporting Documentation
- **Task Management**: Task Master tasks and subtasks for implementation tracking
- **Test Documentation**: Comprehensive test expectations and validation requirements
- **Integration Guides**: Cross-system integration patterns and requirements

## Compliance Verification

### Pre-Implementation Checklist
- [ ] Development Bible requirements reviewed and understood
- [ ] Existing system inventory checked for duplicates
- [ ] Canonical import patterns identified
- [ ] Test location compliance verified
- [ ] Integration requirements mapped

### Post-Implementation Checklist
- [ ] All tests pass with ≥90% coverage
- [ ] Canonical import structure followed
- [ ] No duplicate functionality created
- [ ] Documentation updated
- [ ] Integration testing completed
- [ ] API contracts maintained or properly updated

---

*This protocol serves as the definitive guide for all backend development activities and must be followed strictly to ensure project consistency, quality, and successful integration.* 