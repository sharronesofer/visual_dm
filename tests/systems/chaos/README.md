# Chaos System Tests

Comprehensive test suite for the Chaos System that ensures Bible compliance and validates all implemented features.

## Overview

This test suite validates the complete chaos system implementation, including:

- **Bible Compliance**: Ensures all Development Bible requirements are met
- **Unit Tests**: Tests individual components in isolation
- **Integration Tests**: Tests component interactions and full system workflows
- **Performance Tests**: Validates system performance under various conditions

## Test Structure

```
tests/systems/chaos/
├── conftest.py                    # Test configuration and fixtures
├── test_warning_system.py         # Unit tests for warning system
├── test_narrative_moderator.py    # Unit tests for narrative moderator
├── test_chaos_manager.py          # Unit tests for chaos manager
├── test_integration.py           # Integration tests
├── run_tests.py                  # Test runner script
└── README.md                     # This file
```

## Running Tests

### Quick Start

```bash
# Run all tests
python tests/systems/chaos/run_tests.py

# Run specific test suite
python tests/systems/chaos/run_tests.py --suite unit
python tests/systems/chaos/run_tests.py --suite integration
python tests/systems/chaos/run_tests.py --suite compliance

# Run with coverage
python tests/systems/chaos/run_tests.py --coverage

# Quick run (skip slow tests)
python tests/systems/chaos/run_tests.py --quick
```

### Advanced Options

```bash
# Verbose output
python tests/systems/chaos/run_tests.py --verbose

# Parallel execution
python tests/systems/chaos/run_tests.py --parallel 4

# Stop on first failure
python tests/systems/chaos/run_tests.py --failfast

# Performance profiling
python tests/systems/chaos/run_tests.py --profile
```

### Direct pytest Usage

```bash
# Run all chaos system tests
pytest tests/systems/chaos/ -v

# Run specific test file
pytest tests/systems/chaos/test_warning_system.py -v

# Run tests with specific markers
pytest tests/systems/chaos/ -m "integration" -v
pytest tests/systems/chaos/ -m "bible_compliance" -v
pytest tests/systems/chaos/ -m "performance" -v

# Run with coverage
pytest tests/systems/chaos/ --cov=backend.systems.chaos --cov-report=html
```

## Test Categories

### Unit Tests

**File**: `test_warning_system.py`
- Tests the three-tier escalation warning system
- Validates rumor → early warning → imminent progression
- Tests warning expiration and cleanup
- Validates Bible requirement compliance

**File**: `test_narrative_moderator.py`
- Tests narrative intelligence weighting system
- Validates theme and story beat management
- Tests engagement and tension tracking
- Tests event weight calculation with narrative context

**File**: `test_chaos_manager.py`
- Tests consolidated manager architecture
- Validates component coordination and health monitoring
- Tests lifecycle management (start, stop, pause, resume)
- Tests error handling and recovery

### Integration Tests

**File**: `test_integration.py`

**Full System Integration**:
- Complete system startup and shutdown
- Component interaction validation
- Data flow between components
- Cross-component error handling

**Bible Compliance Tests**:
- Three-tier escalation system compliance
- Cascading effects compliance
- Narrative intelligence compliance
- Distribution fatigue compliance
- Temporal pressure as 6th pressure type

**Performance Tests**:
- System performance under load
- Component health monitoring performance
- Error recovery performance
- Concurrent operation handling

**End-to-End Scenarios**:
- Complete chaos event lifecycle
- Economic crisis → warning → event → cascade
- Narrative context integration throughout

## Bible Requirements Tested

### ✅ Three-Tier Escalation System
- **Rumor Phase**: Initial warnings and rumors
- **Early Warning Phase**: Clear indicators of incoming events
- **Imminent Phase**: Crisis is about to occur
- **Tests**: Escalation progression, timing, probability handling

### ✅ Cascading Effects Integration
- **Event Chains**: Economic crisis → Social unrest → Political upheaval
- **Cascade Timing**: Proper delays and severity modifiers
- **Tests**: Multi-level cascades, cascade termination, circular prevention

### ✅ Narrative Intelligence Weighting
- **Theme Management**: Critical, central, supporting, background themes
- **Dramatic Tension**: High tension reduces chaos, low tension increases it
- **Player Engagement**: Low engagement increases chaos for excitement
- **Tests**: Weight calculation, theme priorities, narrative moderation

### ✅ Distribution Fatigue Management
- **Event Clustering Prevention**: Prevents too many events too quickly
- **Fatigue Tracking**: Monitors recent event frequency
- **Tests**: Event spacing, fatigue recovery, burst prevention

### ✅ Consolidated Manager Architecture
- **Single Coordination Point**: ChaosManager coordinates all subsystems
- **Health Monitoring**: Tracks component health and system status
- **Error Handling**: Graceful degradation and recovery
- **Tests**: Component coordination, health checks, lifecycle management

### ✅ Temporal Pressure Support
- **6th Pressure Type**: Temporal pressure monitoring and events
- **Temporal Events**: Time-based chaos events and anomalies
- **Integration**: Full integration with other pressure types
- **Tests**: Temporal pressure detection, temporal event processing

## Test Data and Fixtures

### Configuration
- `test_config`: Optimized configuration for fast test execution
- `integration_config`: Configuration for integration testing
- Performance thresholds and timing configurations

### Mock Data
- `sample_pressure_data`: Realistic pressure source data
- `sample_narrative_context`: Narrative themes and engagement data
- `sample_cascade_data`: Cascade relationship definitions
- `sample_event_data`: Event definitions with impact data

### Helper Utilities
- `ChaosTestHelper`: Common test operations and assertions
- `ErrorSimulator`: Utilities for simulating error conditions
- Mock external systems for isolated testing

## Performance Benchmarks

The test suite includes performance benchmarks to ensure the system meets operational requirements:

- **Event Processing**: < 0.5 seconds per event
- **Health Checks**: < 0.1 seconds per check
- **Status Updates**: < 0.2 seconds per update
- **Narrative Updates**: < 0.3 seconds per update
- **Cascade Processing**: < 1.0 seconds per cascade
- **System Startup**: < 5.0 seconds
- **System Shutdown**: < 2.0 seconds

## Test Markers

Use pytest markers to run specific test categories:

```bash
# Bible compliance tests only
pytest -m "bible_compliance"

# Integration tests only
pytest -m "integration"

# Performance tests only
pytest -m "performance"

# Skip slow tests
pytest -m "not slow"
```

## Coverage Requirements

The test suite maintains comprehensive coverage:

- **Minimum Coverage**: 90% line coverage
- **Critical Path Coverage**: 100% for Bible compliance features
- **Error Path Coverage**: All error conditions tested
- **Integration Coverage**: All component interactions tested

Run with coverage reporting:
```bash
python tests/systems/chaos/run_tests.py --coverage
```

Coverage reports are generated in `tests/coverage_html/index.html`.

## Debugging Tests

### Verbose Output
```bash
python tests/systems/chaos/run_tests.py --verbose
```

### Running Single Tests
```bash
pytest tests/systems/chaos/test_warning_system.py::TestWarningSystemInitialization::test_warning_system_creation -v
```

### Debug Mode
```bash
pytest tests/systems/chaos/ --pdb  # Drop into debugger on failure
pytest tests/systems/chaos/ -s     # Don't capture output
```

### Logging
Tests use reduced logging (WARNING level) by default. To see more:
```python
# In test file
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Common Issues and Solutions

### Async Test Issues
- **Problem**: Tests hanging or not completing
- **Solution**: Check `conftest.py` async setup, ensure proper cleanup

### Mock Issues
- **Problem**: Mocks not working as expected
- **Solution**: Verify mock placement, check async vs sync methods

### Performance Test Failures
- **Problem**: Performance tests failing on slower systems
- **Solution**: Adjust thresholds in `performance_thresholds` fixture

### Import Errors
- **Problem**: Cannot import chaos system modules
- **Solution**: Ensure PYTHONPATH includes project root, check module structure

## Contributing to Tests

When adding new features to the chaos system:

1. **Add Unit Tests**: Test the component in isolation
2. **Add Integration Tests**: Test interaction with other components
3. **Update Bible Compliance**: If feature affects compliance
4. **Add Performance Tests**: If feature affects performance
5. **Update Documentation**: Update this README with new tests

### Test Naming Convention
- `test_<component>_<functionality>`
- `test_integration_<scenario>`
- `test_bible_compliance_<requirement>`
- `test_performance_<aspect>`

### Test Organization
- One test class per major functionality area
- Clear, descriptive test method names
- Comprehensive docstrings explaining what is being tested
- Setup and teardown as needed

## Continuous Integration

These tests are designed to run in CI/CD environments:

```yaml
# Example CI configuration
test_chaos_system:
  script:
    - python tests/systems/chaos/run_tests.py --coverage --parallel 4
    - python tests/systems/chaos/run_tests.py --suite compliance
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Summary

This comprehensive test suite ensures the chaos system meets all Development Bible requirements while maintaining high performance and reliability. Regular execution of these tests validates system integrity and compliance throughout development. 