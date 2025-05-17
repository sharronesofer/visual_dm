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