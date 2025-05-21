# Refactored Events System Structure

## Directory Structure
```
backend/systems/events/
├── __init__.py                 # Main entry point, exports all public APIs 
├── README.md                   # Documentation
├── base.py                     # EventBase class
├── dispatcher.py               # EventDispatcher implementation
├── event_types.py              # All canonical event type definitions
├── middleware/                 # Event middleware components
│   ├── __init__.py
│   ├── analytics.py            # Analytics middleware
│   ├── debugging.py            # Debug middleware
│   ├── error_handler.py        # Error handling middleware
│   └── logging.py              # Logging middleware
├── utils/                      # Event utilities 
│   ├── __init__.py
│   └── manager.py              # EventManager utility class
└── tests/                      # Unit tests
    ├── test_dispatcher.py      # Tests for the dispatcher
    ├── test_manager.py         # Tests for the event manager
    └── example_usage.py        # Example usage patterns
```

## Refactoring Steps
1. Move `core/event_base.py` to `base.py`
2. Move `core/event_dispatcher.py` to `dispatcher.py`
3. Move `core/canonical_events.py` to `event_types.py`
4. Consolidate middleware files
5. Move `utils/event_utils.py` to `utils/manager.py`
6. Update imports in all files
7. Update the main `__init__.py` to export all public APIs
8. Move/consolidate tests

## Duplicate Analysis
- `core/events/test_event_dispatcher.py` and `tests/test_event_dispatcher.py` appear to be duplicates
- `core/events/test_event_bus.py` may be an older version we can eliminate
- The `legacy` directory can be removed if empty 