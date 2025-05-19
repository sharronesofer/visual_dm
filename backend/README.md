# Visual DM Backend

This is the backend service for the Visual DM project, providing RESTful API endpoints and game logic.

## Directory Structure

- `/src` - Main source code
  - `/api` - API endpoints and related code
    - `/v1` - Legacy API endpoints
    - `/v2` - FastAPI-based endpoints
  - `/core` - Core application functionality
  - `/db` - Database models and access
  - `/services` - Business logic services
  - `/domain` - Game domain modules
  - `/utils` - Utility functions
- `/scripts` - Utility scripts and tools
- `/tests` - Test suite
- `/docs` - Documentation
- `/configs` - Configuration files

## Getting Started

1. Install dependencies:
```bash
poetry install
```

2. Run the API server:
```bash
uvicorn src.app:app --reload
```

3. Run the game application:
```bash
python src/main.py
```

## API Documentation

API documentation is available at `/api/docs` when the server is running.

## Development

This project uses Poetry for dependency management and pytest for testing.

## Migration Notes

This project has recently undergone restructuring to clean up the codebase. See `docs/README_MIGRATION.md` for details.
