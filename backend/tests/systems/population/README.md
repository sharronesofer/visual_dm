# Population System Tests

This directory contains comprehensive tests for the Population System located in `/backend/systems/population/`.

## Test Files

- **test_imports.py**: Verifies all population system modules can be correctly imported.
- **test_models.py**: Tests data models including enums, configurations, population objects, and event models.
- **test_utils.py**: Tests utility functions for growth rate calculations, state transitions, and timeline projections.
- **test_events.py**: Tests event types, event data models, and integration with the event dispatcher system.
- **test_service.py**: Tests the PopulationService class including initialization, population management, and special operations.
- **test_router.py**: Tests API endpoints including request validation, routing, and integration with the service layer.
- **test_integration.py**: Tests the entire population system, validating interactions between modules and full lifecycle operations.

## Testing Approach

The testing strategy follows a layered approach, starting with unit tests for individual components and progressing to integration tests for the complete system:

### Unit Tests

1. **Models (test_models.py)**
   - Validation of enum values
   - Model initialization with default and custom values
   - Type checking and validation
   - Model methods and property calculations

2. **Utilities (test_utils.py)**
   - Growth rate calculations
   - Population state transitions
   - Population timeline estimations
   - Target population calculations
   - Edge cases and boundary conditions

3. **Events (test_events.py)**
   - Event model construction and validation
   - Event handler functionality
   - Event dispatcher integration
   - Event registration

4. **Service (test_service.py)**
   - Service initialization
   - CRUD operations for POI populations
   - Monthly growth calculations
   - State transition handling
   - Special event handling (wars, catastrophes)
   - Population repopulation

5. **Router (test_router.py)**
   - API endpoint validation
   - Request/response formatting
   - Error handling
   - Input validation
   - Service layer integration

### Integration Tests (test_integration.py)

- Full lifecycle testing (normal → declining → abandoned → ruins → repopulating → normal)
- Cross-module interaction
- Event propagation
- Monthly update process
- Configuration application
- Growth formula verification with the service

## Test Coverage

The tests aim to cover:

- Normal operations and happy paths
- Edge cases and boundary conditions
- Error handling and validation
- State transitions
- Event emission and handling
- Configuration changes
- Population growth mechanics
- API request/response validation

## Running Tests

To run all population system tests:

```bash
pytest backend/tests/systems/population
```

To run a specific test file:

```bash
pytest backend/tests/systems/population/test_models.py
```

To run with coverage:

```bash
pytest backend/tests/systems/population --cov=backend.systems.population
```

## Key Test Fixtures

- **Mock Event Dispatcher**: For isolated testing of event handling
- **Populated Service**: Pre-configured service with test data
- **Test App/Client**: For API endpoint testing
- **Mock Population Service**: For isolating router tests from service implementation

## Testing Standards

All tests follow these standards:

- Clear test method names describing what is being tested
- Detailed docstrings explaining test purpose
- Proper assertions with descriptive failure messages
- Isolation of dependencies through mocking
- Comprehensive coverage of edge cases
- Validation of state before and after operations 