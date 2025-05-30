# Diplomacy System Test Strategy

## Overview

This document outlines the comprehensive testing strategy for the Visual DM's Diplomacy System. The diplomacy system manages relationships, treaties, negotiations, and diplomatic events between factions in the game. 

## System Components

The diplomacy system consists of the following components:

1. **Models** (`models.py`): Core data structures for treaties, negotiations, violations, incidents, etc.
2. **Repository** (`repository.py`): Data persistence layer using JSON file storage
3. **Services** (`services.py`): Business logic in `TensionService` and `DiplomacyService`
4. **API Endpoints** (`router.py`): FastAPI routes for diplomacy features
5. **Schemas** (`schemas.py`): Pydantic models for API validation

## Test Objectives

- Verify that diplomacy models work correctly and enforce business rules
- Ensure the repository layer correctly persists and retrieves data
- Test that services properly implement diplomacy system logic
- Validate API endpoints functionality and error handling
- Verify that Pydantic schemas correctly validate input/output data

## Test Types

### 1. Unit Tests

Unit tests focus on testing individual components in isolation, using mocks for dependencies.

#### Models Testing (`test_models.py`)
- Test object creation for all model classes
- Verify field validation and type checking
- Test model-specific business logic (e.g., treaty date validation)
- Confirm object relationships (e.g., between Treaty and TreatyViolation)

#### Repository Testing (`test_repository.py`)
- Test data persistence functions (create, get, update)
- Verify file operations and directory creation
- Test error handling for missing or invalid files
- Test serialization/deserialization of diplomatic objects

#### Services Testing (`test_services.py`)
- Test TensionService for relationship tension management
- Test DiplomacyService treaty and negotiation operations
- Verify logical operations like treaty violation handling
- Test event generation and tension calculation

#### Schemas Testing (`test_schemas.py`)
- Test schema validation for API inputs
- Verify correct conversion between API and domain models
- Test validation errors for invalid inputs
- Test schema nesting (e.g., negotiation with offers)

#### API Testing (`test_router.py`)
- Test API endpoint responses
- Verify status codes and response formats
- Test API error handling
- Verify correct service calls with expected parameters

### 2. Integration Tests (Future)

Integration tests would focus on testing interactions between components, particularly:

- Repository integration with the file system
- Services integration with repositories
- API endpoints integration with services

### 3. End-to-End Tests (Future)

E2E tests would verify complete user flows, such as:

- Creating a treaty through the API and verifying it affects faction relationships
- Treaty violations leading to sanctions and tension changes
- Multi-step negotiation processes

## Testing Tools & Framework

- **pytest**: Core testing framework
- **unittest.mock**: For mocking dependencies
- **FastAPI TestClient**: For testing API endpoints
- **pytest-cov**: For measuring test coverage (future)

## Test Data Strategy

- Use UUID generation for faction and entity IDs
- Create test fixtures for common test data
- Use meaningful test data to simulate real diplomatic scenarios
- Test edge cases with various combinations of treaty types, conditions, etc.

## Mocking Strategy

- Mock file system operations in repository tests
- Mock repositories in service tests
- Mock services in API endpoint tests
- Use patching to inject mocks at appropriate levels

## Coverage Goals

- Achieve >90% line coverage for all modules
- 100% coverage for critical business logic (treaty validation, tension calculations)
- Test all API endpoints with both valid and invalid inputs
- Test all error paths and edge cases

## Current Implementation Status

1. **Models (Completed)**: Comprehensive tests for all model classes
2. **Repository (Completed)**: Tests for data persistence operations
3. **Services (Completed)**: Tests for diplomatic operations and tension management
4. **Schemas (Completed)**: Tests for API data validation
5. **API Endpoints (Completed)**: Tests for all API routes

## Future Testing Enhancements

1. **Integration Tests**: Add tests for component interactions
2. **Performance Testing**: Test system performance with large datasets
3. **Fuzz Testing**: Test with random or malformed inputs
4. **Scenario Testing**: Test specific diplomatic scenarios end-to-end
5. **Benchmark Tests**: Establish performance baselines
6. **Test Automation**: Add to CI/CD pipeline

## Common Test Patterns

1. **Test Naming Convention**: 
   - `test_<function_name>_<scenario>` for normal cases
   - `test_<function_name>_<scenario>_error` for error cases

2. **Test Structure Pattern**:
   - Arrange: Set up test data and mocks
   - Act: Call the function being tested
   - Assert: Verify results and mock interactions

3. **Mocking Pattern**:
   - Use context managers with `patch` for clean setup/teardown
   - Use fixtures for commonly mocked dependencies
   - Return appropriate mock responses to simulate real behavior 