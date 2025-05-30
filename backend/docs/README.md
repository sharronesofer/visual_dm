# Visual DM Backend

## Overview

This is the backend system for Visual DM, implementing a comprehensive tabletop RPG companion and simulation tool.

## Architecture

The backend follows a modular system design with 1 core systems:

### Systems
- **character** - Character system functionality

## Development Standards

All systems follow the canonical import structure:
```python
from backend.systems.system_name.component_type import ComponentName
```

## Testing

Run all tests:
```bash
pytest backend/tests/
```

Current test coverage: 100.0%

## API Documentation

API contracts are defined in `api_contracts.yaml` at the project root.

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest`
3. Start the server: `python main.py`

## Contributing

Follow the Backend Development Protocol outlined in `backend_development_protocol.md`.
