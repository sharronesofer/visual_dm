# Magic System Tests

This directory contains tests for the Visual DM magic system, which provides subtle narrative influences to the game world through hidden mechanics.

## Test Organization

Tests are organized by component:

- `test_models.py`: Tests for the magic system data models
- `test_repositories.py`: Tests for the magic system repositories
- `test_services.py`: Tests for the magic service layer logic
- `test_router.py`: Tests for the magic API endpoints
- `test_utils.py`: Tests for the utility functions
- `test_integration.py`: Cross-component integration tests

## Testing Strategy

The magic system is designed as a background narrative influence system without direct player manipulation. 
The testing strategy focuses on:

1. **Model validation**: Ensuring data models are correctly defined and validated
2. **Repository operations**: Testing CRUD operations for magic entities
3. **Service layer logic**: Verifying business logic around magical effects and knowledge
4. **API endpoints**: Testing the limited read-only API surface
5. **Event emission**: Ensuring the system correctly emits events
6. **Magical influences**: Testing the generation and analysis of narrative magical influences
7. **Background processing**: Verifying the tick processing logic for magical effects

## Key Test Cases

- Spell creation, retrieval, and validation
- Spellbook management and character magic knowledge
- Spell effect application, duration management, and expiration
- Magical influence generation and analysis
- API endpoint validation and error handling
- Event dispatching for magical occurrences
- Integration with time system for spell effect durations

## Mocking Strategy

Tests use the following mocking approaches:

- Database access is mocked using SQLAlchemy in-memory databases
- Event dispatcher calls are mocked to verify correct emission
- Integration with other systems (e.g., characters, time) uses mock objects

## Running Tests

To run all magic system tests:

```bash
pytest backend/tests/systems/magic/
```

To run specific test files:

```bash
pytest backend/tests/systems/magic/test_services.py
```

## Coverage Goals

- Aim for at least 85% test coverage across all magic system files
- 100% coverage for critical paths (effect processing, duration management)
- Complete coverage of API endpoints and error conditions 