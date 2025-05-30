# Equipment System Tests

This directory contains tests for the `/backend/systems/equipment` module, which handles equipment-related functionality including:

- Equipment models and database operations
- Durability management, damage, and repair
- Set bonus calculation and management
- Item identification
- Equipment inventory integration
- API endpoints through FastAPI router

## Test Organization

The test files follow a structured approach to cover all major components of the equipment system:

- `test_models.py` - Tests for data models (Equipment, EquipmentSet, EquipmentDurabilityLog)
- `test_durability_utils.py` - Tests for durability calculation, damage, repair, and stat adjustments
- `test_set_bonus_utils.py` - Tests for equipment set bonus calculations and management
- `test_service.py` - Tests for the EquipmentService class that provides core business logic
- `test_router.py` - Tests for FastAPI router endpoints to ensure proper API behavior
- `test_identify_item_utils.py` - Tests for item identification functionality

## Test Coverage Goals

These tests aim to achieve comprehensive coverage of the equipment system:

- **Data Layer**: Verify correct model initialization, serialization, and relationships
- **Business Logic**: Ensure calculations for durability, set bonuses, and identification work correctly
- **API Layer**: Validate that endpoints handle requests/responses and errors properly
- **Integration**: Test interactions with other systems like inventory, events, and economy

## Running Tests

Run all equipment tests with pytest:

```bash
# Run from project root
pytest backend/tests/systems/equipment

# Run a specific test file
pytest backend/tests/systems/equipment/test_models.py

# Run with coverage reporting
pytest backend/tests/systems/equipment --cov=backend.systems.equipment
```

## Test Fixtures and Mocking

These tests use several common fixtures and mocking strategies:

- **Database Session Mocking**: Tests use mock DB sessions to avoid real database operations
- **Event Dispatcher Mocking**: Tests verify correct events are emitted without depending on the event system
- **Item Data Mocking**: Tests provide mock item data based on game item structure
- **Inventory System Mocking**: Tests simulate inventory operations for equipment-inventory interactions

## Test Design Principles

1. **Isolated Tests**: Each test focuses on a specific component and avoids dependencies
2. **Parameterized Tests**: Uses pytest.mark.parametrize for testing multiple scenarios efficiently
3. **Edge Cases**: Tests include boundary conditions like broken equipment and partial set bonuses
4. **Mock Verification**: Tests verify that mocked components are called with correct parameters
5. **Event Validation**: Tests confirm that appropriate events are published when equipment changes

## Mocking Strategy

The equipment system tests use various mocking approaches to isolate components:

1. **Database Session Mocking**:
   - Using `unittest.mock.patch` to mock the SQLAlchemy session
   - Pytest fixtures like `mock_db_session` provide consistent mocking

2. **Event Dispatcher Mocking**:
   - Testing event emission without triggering real event handlers
   - Using `mock_event_dispatcher` fixture to capture and verify events

3. **Model Factory Functions**:
   - Creating test instances of models with predefined test data
   - Using fixtures to provide reusable test data

4. **Dependency Isolation**:
   - Mocking imports of external systems
   - Using parametrized tests to cover multiple scenarios

## Testing Edge Cases

The test suite aims to cover edge cases including:

- Equipment with zero durability
- Invalid or non-existent equipment sets
- Incomplete set bonuses
- Database errors and exception handling
- Permission validation
- API input validation

Each test file includes detailed test cases for normal operation and edge cases. 