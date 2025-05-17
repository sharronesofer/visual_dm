[![CI](https://github.com/${{ github.repository }}/actions/workflows/ci.yml/badge.svg)](https://github.com/${{ github.repository }}/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen)](#)
[![Lint](https://img.shields.io/badge/lint-passing-brightgreen)](#)
[![Security](https://img.shields.io/badge/security-passing-brightgreen)](#)

## Code Quality Badges
- **CI:** Automated build, test, and quality checks for every push and PR.
- **Coverage:** Percentage of code covered by automated tests (update with real badge if using Codecov or similar).
- **Lint:** Status of code style and static analysis checks (flake8 for Python, etc.).
- **Security:** Status of automated security scans (bandit for Python, etc.).

# Visual DM

A modern dungeon master assistant tool with advanced AI features for generating and managing game content.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development & Testing](#development--testing)
- [CI/CD Setup](#cicd-setup)
- [Language & Project Structure Policy](#language--project-structure-policy)
- [WebSocket-Only Communication Policy & Migration Guide](#websocket-only-communication-policy--migration-guide)
- [Enhanced TypeScript to Python Type Conversion](#enhanced-typescript-to-python-type-conversion)
- [Chaos Engine Integration](#chaos-engine-integration)

## Features

- Character creation and management
- Combat tracking and management
- World generation with detailed regions and maps
- Quest generation and tracking
- NPC interaction and management
- Memory system for character and world events
- Motif-based narrative engine
- Visualization tools for game elements

## Getting Started

### Prerequisites

- Python 3.11+
- Unity 2022.3 LTS or newer
- Poetry (for Python dependency management)
- Redis (optional, for caching)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/sharronesofer/visual_dm.git
cd visual_dm
```

2. Set up the Python backend:
```bash
cd backend
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Open the Unity project:
```bash
# Open Unity Hub and add the UnityClient directory as a project
```

### Running the Application

#### Backend

```bash
cd backend
poetry run uvicorn main:app --reload
```

#### Unity Client

Open the UnityClient project in Unity and press the Play button.

## Project Structure

The project is structured as a monorepo containing both the Python backend and Unity frontend:

```
Visual_DM/
├── backend/                  # Python backend
│   ├── src/                  # Source code
│   │   ├── api/              # API endpoints
│   │   ├── models/           # Data models
│   │   └── utils/            # Utilities
│   ├── tests/                # Tests
│   ├── pyproject.toml        # Poetry configuration
│   └── .flake8               # Flake8 configuration
├── UnityClient/              # Unity C# frontend
│   ├── Assets/
│   │   ├── Scripts/          # C# scripts
│   │   │   ├── UI/           # UI scripts
│   │   │   ├── Backend/      # Backend integration
│   │   │   ├── Core/         # Core systems
│   │   │   ├── Models/       # Data models
│   │   │   ├── Utils/        # Utilities
│   │   │   └── Managers/     # Manager scripts
│   │   ├── Resources/        # Unity resources
│   │   ├── Prefabs/          # Prefabs
│   │   ├── Materials/        # Materials
│   │   ├── Textures/         # Textures
│   │   └── Animations/       # Animations
│   └── .editorconfig         # C# code style
├── scripts/                  # Utility scripts
│   └── build_backend.sh      # Backend build script
├── .github/                  # GitHub configuration
│   └── workflows/            # GitHub Actions workflows
└── README.md                 # This file
```

## Development & Testing

### Python Backend

```bash
cd backend
poetry run pytest              # Run tests
poetry run black .             # Format code
poetry run flake8              # Lint code
```

### Unity Client

Unity tests can be run through the Unity Test Runner interface within the Unity Editor.

## CI/CD Setup

We use GitHub Actions for continuous integration and deployment:

- **Python Backend CI**: Runs on changes to backend code, performing linting, formatting, and tests.
- **Unity Client CI**: Runs on changes to Unity code, performing code analysis.

See the `.github/workflows` directory for detailed configurations.

## Language & Project Structure Policy

This section defines the authoritative policy for technology stack, directory organization, and development rules for Visual DM. All contributors must adhere to these standards for new development.

### Technology Stack

- **Backend:** Python 3.11+ (active code in `

# Chaos Engine Integration

## Overview

The Motif System now integrates with a dedicated Chaos Engine via the `IChaosEngine` interface, enabling bidirectional, event-driven communication. This decouples chaos logic from motif management and allows for robust, testable, and extensible system interactions.

## Key Components

- **IChaosEngine**: Interface defining the contract for chaos state management and motif event handling.
- **ChaosState**: Data contract representing the current chaos state (level, description, etc.).
- **MotifEventData**: Data contract for motif-related events sent to the Chaos Engine.
- **ChaosEngine**: Default implementation, registered at startup via `ServiceLocator`.
- **MotifPool/MotifFactory**: Use `IChaosEngine` to determine chaos state and publish motif events.

## Sequence Diagram

```
MotifPool.Rotate() --> ServiceLocator.Resolve<IChaosEngine>()
MotifPool ----> IChaosEngine.GetChaosState() : Query current chaos
MotifFactory ----> IChaosEngine.GetChaosState() : Query for chaosSource
MotifFactory ----> IChaosEngine.OnMotifEvent(MotifEventData) : Publish motif rolled event
MotifPool ----> IChaosEngine.OnMotifEvent(MotifEventData) : Publish motif rotated event
IChaosEngine ----> Updates internal ChaosState
```

## Usage Example

```csharp
// Register ChaosEngine at startup
ChaosEngineRegistration.Register();

// In MotifPool
var chaosEngine = ServiceLocator.Instance.Resolve<IChaosEngine>();
var chaos = chaosEngine.GetChaosState().ChaosLevel > 0.5f;

// In MotifFactory
var motif = new Motif(theme, lifespan, "1.0.0", chaosSource);
chaosEngine.OnMotifEvent(new MotifEventData {
    MotifTheme = motif.Theme,
    IsChaosSource = motif.ChaosSource,
    EventType = "MotifRolled",
    Context = "RollNewMotif"
});
```

## Extending the Integration

- Implement custom `IChaosEngine` logic for advanced chaos state management.
- Subscribe to motif and chaos events via the event bus for further system integration.
- Add new fields to `ChaosState` and `MotifEventData` as needed.

## Error Handling

- All integration points are wrapped in try/catch and log errors via `IntegrationLogger`.
- Fallback logic ensures system stability if the Chaos Engine is unavailable.

## Testing

- Unit and integration tests should mock `IChaosEngine` to verify motif/chaos interactions.

---

For more details, see the code in `Systems/Integration/` and `MotifSystem/` directories.