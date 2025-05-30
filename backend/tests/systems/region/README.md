# Region System Tests

This directory contains tests for the modules in the `/backend/systems/region` directory. The region system is responsible for managing geographical divisions of the game world, their properties, and relationships.

## Test Structure

- `test_schemas.py`: Tests for data models/schemas (validation, serialization/deserialization)
- `test_repository.py`: Tests for data access layer (CRUD operations)
- `test_service.py`: Tests for business logic and service layer functionality
- `test_router.py`: Tests for FastAPI endpoints
- `test_utils.py`: Tests for utility functions
- `test_worldgen.py`: Tests for world generation functionality
- `test_continent.py`: Tests for continent generation functionality
- `test_region_gen.py`: Tests for region generation functionality
- `test_mapping.py`: Tests for coordinate mapping functionality
- `test_tension.py`: Tests for tension management functionality
- `test_integration.py`: Integration tests for the entire region system

## Testing Strategies

### Schemas Testing Strategy
- Validate that schemas enforce correct data types and constraints
- Test serialization/deserialization
- Test optional vs. required fields
- Test validation of linked/dependent fields

### Repository Testing Strategy
- Test CRUD operations (create, read, update, delete)
- Test error handling for file operations
- Test edge cases (empty data, malformed data)
- Mock filesystem to avoid actual file operations

### Service Testing Strategy
- Test world initialization with different parameters
- Test region and continent retrieval
- Test coordinate mapping
- Mock repository layer to isolate tests
- Test error handling for edge cases
- Test integration with the data registry

### Router Testing Strategy
- Test API endpoints with different inputs
- Test status codes and response payloads
- Test error responses
- Mock service layer to isolate tests

### World Generation Testing Strategy
- Test deterministic generation with fixed seeds
- Test generation of continents, regions with constraints
- Test biome distribution and adjacency rules
- Test persistence and loading of generated world data
- Verify geographic consistency (adjacency, etc.)
- Test performance with reasonable timeouts

### Mapping Testing Strategy
- Test coordinate conversions (region to lat/lon)
- Test edge cases and boundary conditions
- Validate consistency with canonical world origin

### Tension Testing Strategy
- Test tension calculations between regions/factions
- Test tension decay mechanics
- Test thresholds for states (alliance, rivalry, war)
- Test triggers for state transitions

## Mocking Guidelines

- Use pytest fixtures for common test data
- Mock file operations using either unittest.mock or pytest-mock
- Use dependency injection to replace real implementations with mocks
- Create fixtures for common world/region/continent data

## Integration Testing

Integration tests should verify that the entire region system works together properly, including:
- World generation → region storage → API access
- Tension management and faction relationships
- Coordinate mapping and weather simulation
- Region neighboring and adjacency

## Metrics to Track

- Test coverage (aim for >80%)
- Test execution time (particularly for world generation)
- Number of failed tests over time

## Running Tests

```bash
# Run all region system tests
pytest tests/backend/systems/region/

# Run specific test file
pytest tests/backend/systems/region/test_service.py

# Run tests with coverage report
pytest tests/backend/systems/region/ --cov=backend.systems.region
``` 