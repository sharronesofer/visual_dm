# Test Coverage Improvement Roadmap

## Phase 1: Critical Infrastructure Fixes (Week 1-2)

### Priority 1: Pydantic V2 Migration
**Impact**: High - Fixing 25+ deprecation warnings, stabilizing test execution

#### Specific Tasks:
1. **Update Validator Decorators** (2-3 days)
   ```python
   # Replace ALL instances of:
   from pydantic import validator
   @validator('field_name')
   
   # With:
   from pydantic import field_validator
   @field_validator('field_name')
   ```
   
   **Files to Fix**:
   - `systems/inventory/schemas.py` (10+ validators)
   - `systems/motif/models/*.py`
   - `systems/rumor/models/*.py`
   - `systems/world_state/models/*.py`
   - All other Pydantic models with `@validator`

2. **Update Config Classes** (1-2 days)
   ```python
   # Replace:
   class Config:
       orm_mode = True
       schema_extra = {...}
   
   # With:
   from pydantic import ConfigDict
   model_config = ConfigDict(from_attributes=True, json_schema_extra={...})
   ```

3. **Test Migration Impact** (1 day)
   - Run subset of tests after each file migration
   - Verify no new validation errors introduced

### Priority 2: Database Relationship Fixes
**Impact**: High - Enabling integration tests, resolving SQLAlchemy errors

#### Specific Tasks:
1. **Fix Foreign Key Constraints** (2-3 days)
   - `equipment.character_id` relationship errors
   - `factions` table relationship mapping
   - Review all `relationship()` definitions

2. **Standardize Base Models** (1-2 days)
   - Consolidate multiple `declarative_base()` instances
   - Create single source of truth for database models
   - Update imports across all systems

3. **Fix Async Session Management** (1-2 days)
   - Standardize `get_async_db()` usage
   - Fix async generator vs iterator issues
   - Update test fixtures for async database sessions

### Priority 3: Service Constructor Standardization
**Impact**: Medium-High - Enabling service layer tests

#### Specific Tasks:
1. **MoodService Constructor** (1 day)
   ```python
   # Current error: unexpected keyword argument 'db_session'
   # Fix: Standardize constructor signature
   ```

2. **Repository Pattern Consistency** (2-3 days)
   - Standardize all repository constructors
   - Implement missing repository methods
   - Create base repository class

3. **Dependency Injection Framework** (2-3 days)
   - Choose consistent DI approach (constructor injection vs service locator)
   - Update all service classes
   - Create DI container for tests

## Phase 2: Core System Implementations (Week 3-4)

### Priority 1: Missing Repository Methods
**Impact**: High - Enabling core business logic tests

#### Region System:
```python
class RegionRepository:
    def get_region(self, region_id: str) -> Optional[Region]: # MISSING
    def save_region(self, region: Region) -> bool: # MISSING  
    def get_all_regions(self) -> List[Region]: # MISSING
    def get_region_at_coordinates(self, x: int, y: int) -> Optional[Region]: # MISSING
```

#### World State System:
```python
class WorldStateManager:
    def set_state_bulk(self, states: Dict) -> None: # MISSING
    def create_snapshot(self, name: str) -> str: # MISSING
    def get_state_at_time(self, key: str, timestamp: datetime) -> Any: # MISSING
```

### Priority 2: Model Attribute Completion
**Impact**: Medium - Fixing attribute errors in tests

#### Time System:
```python
class CalendarData:
    def days_per_month(self) -> int: # MISSING
    def months_per_year(self) -> int: # MISSING  
    def get_days_in_month(self, month: int) -> int: # MISSING
```

#### Rumor System:
```python
class Rumor:
    def get_most_believed_variant(self) -> RumorVariant: # MISSING
    def set_believability_for_entity(self, entity_id: str, value: float) -> None: # MISSING
```

### Priority 3: Event System Integration
**Impact**: Medium-High - Enabling cross-system communication tests

1. **Fix Event Type Inheritance Issues**
   - Test classes incorrectly inheriting from EventBase
   - Missing proper event type definitions

2. **Complete Event Dispatcher Integration**
   - Fix singleton pattern conflicts
   - Standardize event subscription patterns

## Phase 3: API Endpoint Testing (Week 5-6)

### Priority 1: High-Impact Endpoints
**Current Coverage**: 0-25% across most endpoints

#### Authentication Endpoints:
- `/auth/login` - Currently failing
- `/auth/token/verify` - Database relationship errors
- `/auth/protected` - Permission testing

#### Core Business Logic Endpoints:
- `/population/*` - Type validation errors  
- `/motif/*` - Repository configuration errors
- `/region/*` - Missing service methods

### Priority 2: Systematic API Testing Strategy
1. **Create FastAPI Test Client Templates**
2. **Standardize Authentication for Tests** 
3. **Create Database Fixtures for API Tests**
4. **Implement Response Schema Validation**

## Phase 4: Service Layer Completion (Week 7-8)

### Priority 1: Business Logic Implementation
**Current Coverage**: 30-40% service layer

#### Character System Services:
- Fix MoodService dependency injection
- Complete GoalService implementation  
- Resolve RelationshipService module structure

#### World Generation Services:
- Implement missing WorldGenerator components
- Complete POI generation logic
- Fix biome utility functions

### Priority 2: Integration Test Fixes
1. **Async Session Management**
2. **Mock Strategy Standardization**
3. **Test Database Setup/Teardown**

## Phase 5: Coverage Optimization (Week 9-12)

### Target Coverage Goals:
- **Models/Schemas**: 85%+ (currently ~80%)
- **API Endpoints**: 70%+ (currently ~20%)
- **Services**: 75%+ (currently ~35%)
- **Utils**: 70%+ (currently ~50%)
- **Overall**: 75%+ (currently ~35-40%)

### Measurement Strategy:
1. **Automated Coverage Reporting**
   - Set up coverage reporting in CI/CD
   - Coverage badges and trend tracking
   - Fail builds below coverage thresholds

2. **Coverage Analysis Tools**
   - Line coverage analysis
   - Branch coverage analysis  
   - Function coverage analysis

## Implementation Timeline

### Week 1-2: Foundation (Critical Infrastructure)
- [ ] Pydantic V2 migration (3-4 days)
- [ ] Database relationship fixes (3-4 days)  
- [ ] Service constructor standardization (2-3 days)

### Week 3-4: Core Systems
- [ ] Missing repository method implementation (4-5 days)
- [ ] Model attribute completion (2-3 days)
- [ ] Event system integration fixes (2-3 days)

### Week 5-6: API Layer
- [ ] High-impact endpoint testing (3-4 days)
- [ ] API testing framework setup (2-3 days)
- [ ] Authentication and security testing (2-3 days)

### Week 7-8: Service Layer
- [ ] Business logic completion (4-5 days)
- [ ] Integration test stabilization (3-4 days)

### Week 9-12: Optimization
- [ ] Coverage monitoring setup (1-2 days)
- [ ] Systematic gap analysis and filling (ongoing)
- [ ] Performance optimization (ongoing)

## Success Metrics

### Technical Metrics:
- **Test Pass Rate**: >90% (currently ~50%)
- **Coverage**: >75% overall (currently ~35-40%)
- **Build Time**: <5 minutes (currently ~1.5 minutes)
- **Test Execution Time**: <60 seconds (currently ~87 seconds)

### Quality Metrics:
- **Zero Critical Syntax Errors** (currently 6+ fixed)
- **Zero Pydantic Deprecation Warnings** (currently 25+)
- **Zero Database Relationship Errors** (currently multiple)
- **<10 Test Failures** (currently 823 failures)

## Risk Mitigation

### High-Risk Areas:
1. **Database Schema Changes** - Could break existing functionality
2. **Event System Changes** - Could affect cross-system communication
3. **API Breaking Changes** - Could affect frontend integration

### Mitigation Strategies:
1. **Feature Flagging** - Gradual rollout of changes
2. **Comprehensive Regression Testing** - Before each phase
3. **Staged Deployment** - Development → Staging → Production
4. **Rollback Plans** - For each major change

## Next Steps

### Immediate Actions (This Week):
1. Start Pydantic V2 migration with inventory schemas
2. Create database relationship mapping audit
3. Begin service constructor standardization  
4. Set up automated coverage monitoring

### Resource Requirements:
- **Developer Time**: 2-3 weeks full-time equivalent
- **Code Review Time**: 0.5 weeks
- **Testing Time**: 1 week
- **Documentation Time**: 0.5 weeks 