# Package Reference Updates

This document details package reference updates performed as part of Task #718, Subtask 3.

## Unity Package Updates

Added the following packages to `VDM/Packages/manifest.json`:

1. **Code Coverage Tools**
   - Added `com.unity.testtools.codecoverage` v1.2.4 to provide code coverage metrics for tests
   - This enhances test reporting and helps identify under-tested areas of code

2. **Performance Testing Framework**
   - Added performance testing framework to testables array
   - Enables proper performance testing in the Unity codebase

## Backend Package Updates

Updated `backend/pyproject.toml` with the following changes:

1. **Added Missing Production Dependencies**
   - `websockets` (>=12.0.0,<13.0.0): Required for WebSocket communication
   - `python-dotenv` (>=1.0.1,<2.0.0): For environment variable management
   - `alembic` (>=1.13.2,<2.0.0): Database migration tool for SQLAlchemy
   - `psycopg2-binary` (>=2.9.9,<3.0.0): PostgreSQL adapter
   - `chromadb` (>=0.4.22,<0.5.0): Vector database for semantic search

2. **Consolidated Test Dependencies**
   - Moved test dependencies from a separate dev group into main dependencies
   - Added version constraints to ensure compatibility
   - Includes: pytest-asyncio, pytest-cov, pytest-mock, httpx

3. **Standardized Version Specifications**
   - Applied consistent version range formats (>=x.y.z,<x+1.0.0)
   - Ensures upper bounds to prevent breaking changes from major version upgrades
   - Makes dependency management more predictable

## Verification

These changes ensure all necessary packages are available for:
- Running test suites
- Measuring code coverage
- Performance testing
- Database migrations and operations
- Backend API and WebSocket functionality

The updates address missing dependencies that were causing import errors in tests and provide a more comprehensive set of development tools. 