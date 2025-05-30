# Backend Structure

This document outlines the new structure of the backend codebase, reorganized for clarity and maintainability.

## Directory Structure

```
backend/
├── api/                    # API layer
│   ├── routers/            # FastAPI route definitions
│   ├── websockets/         # WebSocket handlers 
│   └── middleware/         # API middleware (auth, logging, etc.)
│
├── core/                   # Core functionality
│   ├── database/           # Database connection and management
│   ├── config/             # Application configuration
│   └── logger/             # Logging setup and utilities
│
├── systems/                # Game systems (domain logic)
│   ├── memory/             # Memory system
│   ├── rumor/              # Rumor system
│   ├── world_state/        # World state system
│   ├── time/               # Time system and calendar 
│   ├── character/          # Character system (NPCs and players)
│   ├── faction/            # Faction system
│   ├── inventory/          # Inventory system
│   ├── quest/              # Quest and story arc system
│   └── ...                 # Other game systems
│
├── utils/                  # Shared utilities
│   ├── format/             # Formatting utilities
│   ├── validation/         # Validation utilities 
│   └── helpers/            # General helper functions
│
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
│
├── docs/                   # Documentation
│   ├── api/                # API documentation 
│   └── systems/            # System documentation
│
├── config/                 # Configuration files
│   ├── development.py      # Development environment config
│   └── production.py       # Production environment config
│
└── main.py                 # Application entry point
```

## System Structure

Each system in the `systems/` directory follows a consistent structure:

```
systems/<system_name>/
├── models/                 # Data models and domain objects
├── services/               # Business logic and operations
├── repositories/           # Data persistence
├── schemas/                # API schemas (request/response models)
├── utils/                  # System-specific utilities
└── README.md               # System documentation
```

## System Dependencies

Systems interact with each other primarily through:

1. **Events System** - Most systems communicate via the Events System, which allows loose coupling
2. **Direct Dependencies** - Some services directly depend on other services
3. **World State** - Many systems read from or write to the World State system

## Migration Status

This structure represents the target architecture. The codebase is currently in the process of migration from its previous structure. Some files may still need import adjustments or further refactoring.

## Guidelines for New Code

When adding new code:

1. Identify which system it belongs to
2. Follow the standard directory structure
3. Use the Events System for cross-system communication when possible
4. Document your code and update the system README as needed 