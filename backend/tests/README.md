# Backend Test Suite

## Overview
This directory contains automated tests for the backend Python services of Visual DM, covering:
- Unit tests (models, services, utilities)
- Integration tests (API endpoints, database, service interactions)
- WebSocket tests (real-time server, event delivery)
- Performance tests (load, stress, endurance)
- Security tests (auth, permissions, input validation)

## Directory Structure
- `unit/` — Unit tests for core modules
- `api/` — Integration tests for REST API endpoints
- `services/` — Integration tests for backend services
- `websocket/` — Async tests for WebSocket server
- `performance/` — Load and stress tests (Locust)
- `security/` — Security and permission tests

## Running Tests
- **Unit/Integration/Security/WebSocket:**
  ```bash
  cd backend
  pip install -r requirements-test.txt
  pytest --cov=backend
  ```
- **Performance (Locust):**
  ```bash
  cd backend/tests/performance
  locust -f locustfile.py
  ```

## Coverage Reporting
- Generates HTML and XML coverage reports with `pytest-cov`.
- Minimum coverage threshold: 80% (configurable in `pytest.ini`).

## Adding New Tests
- Place new tests in the appropriate subdirectory.
- Use descriptive test function names and docstrings.
- Mock external dependencies for unit tests.

## CI Integration
- All tests are run automatically in CI/CD pipeline.
- Pipeline fails on test or coverage failure.

## Additional Tools
- Static analysis: `bandit` for security, `flake8` for style.
- See `requirements-test.txt` for all test dependencies. 