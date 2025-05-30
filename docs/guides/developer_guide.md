# Visual DM Developer Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Development Setup](#development-setup)
4. [Backend Development](#backend-development)
5. [Unity Development](#unity-development)
6. [API Development](#api-development)
7. [Testing Guidelines](#testing-guidelines)
8. [Deployment](#deployment)
9. [Contributing](#contributing)
10. [Standards and Best Practices](#standards-and-best-practices)

## Overview

Visual DM is a comprehensive tabletop RPG companion built with a modular architecture. The system consists of a FastAPI backend, Unity frontend, and various supporting services.

### Tech Stack
- **Backend**: Python 3.9+, FastAPI, Pydantic, SQLAlchemy
- **Frontend**: Unity 2022.3 LTS, C#, Mirror Networking
- **AI Services**: Anthropic Claude, OpenAI GPT, Perplexity
- **Database**: SQLite (development), PostgreSQL (production)
- **Testing**: pytest, Unity Test Runner
- **CI/CD**: GitHub Actions, Docker

### Key Design Principles
- **Modularity**: Each system is self-contained with clear interfaces
- **Testability**: All components have comprehensive test coverage
- **Extensibility**: Plugin architecture supports custom content
- **Performance**: Optimized for real-time multiplayer gameplay
- **Reliability**: Robust error handling and recovery mechanisms

## Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Unity Client  │    │  FastAPI Backend │    │   AI Services   │
│                 │────│                 │────│                 │
│  - Game Logic   │    │  - API Endpoints │    │  - Claude API   │
│  - UI/UX        │    │  - Business Logic│    │  - GPT API      │
│  - Networking   │    │  - Data Storage  │    │  - Perplexity   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Backend Architecture
```
backend/
├── systems/           # Domain-specific systems
│   ├── character/     # Character management
│   ├── combat/        # Combat mechanics
│   ├── quest/         # Quest system
│   └── ...
├── core/              # Core services
│   ├── database/      # Database connections
│   ├── config/        # Configuration
│   └── events/        # Event system
├── api/               # API layer
└── tests/             # Test suite
```

### Unity Architecture
```
VDM/Assets/Scripts/
├── Services/          # Backend communication
├── Systems/           # Game systems
├── UI/                # User interface
├── Data/              # Data models
├── Networking/        # Multiplayer
└── Tests/             # Unit tests
```

## Development Setup

### Prerequisites
```bash
# Required software
- Python 3.9+
- Unity 2022.3 LTS
- Git
- Docker (optional)
- Node.js 16+ (for tooling)
```

### Environment Setup
```bash
# Clone repository
git clone https://github.com/visualdm/visual-dm.git
cd visual-dm

# Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Environment configuration
cp .env.example .env
# Edit .env with your API keys and settings
```

### Database Setup
```bash
# Development database
cd backend
python scripts/init_database.py

# Run migrations
alembic upgrade head
```

### Running Development Servers
```bash
# Backend (Terminal 1)
cd backend
python main.py

# Unity (Unity Editor)
# Open VDM project in Unity
# Open Bootstrap scene
# Press Play
```

## Backend Development

### System Structure
Each backend system follows this pattern:
```
systems/<system_name>/
├── models/            # Data models
├── services/          # Business logic
├── repositories/      # Data access
├── schemas/           # API schemas
├── routers/           # API endpoints
├── utils/             # System utilities
└── tests/             # System tests
```

### Creating a New System
```bash
# Use the system generator
python scripts/generate_system.py new_system_name

# Or manually create structure
mkdir -p backend/systems/new_system/{models,services,repositories,schemas,routers,utils,tests}
```

### Code Examples

#### Model Definition
```python
# backend/systems/character/models/character.py
from sqlalchemy import Column, Integer, String, JSON
from backend.core.database.base import BaseModel

class Character(BaseModel):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    attributes = Column(JSON, nullable=False)
    
    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}')>"
```

#### Service Implementation
```python
# backend/systems/character/services/character_service.py
from typing import List, Optional
from ..models.character import Character
from ..repositories.character_repository import CharacterRepository

class CharacterService:
    def __init__(self, repository: CharacterRepository):
        self.repository = repository
    
    async def create_character(self, character_data: dict) -> Character:
        character = Character(**character_data)
        return await self.repository.create(character)
    
    async def get_character(self, character_id: int) -> Optional[Character]:
        return await self.repository.get_by_id(character_id)
```

#### API Router
```python
# backend/systems/character/routers/character_router.py
from fastapi import APIRouter, Depends, HTTPException
from ..schemas.character_schemas import CharacterCreate, CharacterResponse
from ..services.character_service import CharacterService

router = APIRouter(prefix="/characters", tags=["characters"])

@router.post("/", response_model=CharacterResponse)
async def create_character(
    character_data: CharacterCreate,
    service: CharacterService = Depends()
):
    return await service.create_character(character_data.dict())
```

### Event System Usage
```python
# Publishing events
from backend.core.events import get_event_dispatcher

dispatcher = get_event_dispatcher()
await dispatcher.publish("character.created", {
    "character_id": character.id,
    "timestamp": datetime.utcnow()
})

# Subscribing to events
@dispatcher.subscribe("character.created")
async def handle_character_created(event_data: dict):
    # Handle the event
    pass
```

## Unity Development

### Project Structure
```
VDM/Assets/Scripts/
├── Bootstrap/         # Game initialization
├── Services/          # Backend services
│   ├── HTTPClient.cs
│   ├── WebSocketManager.cs
│   └── CharacterService.cs
├── Systems/           # Game systems
│   ├── Character/
│   ├── Combat/
│   └── UI/
├── Data/              # Data models and DTOs
├── Networking/        # Mirror networking
└── Tests/             # Unit tests
```

### Service Implementation Example
```csharp
// VDM/Assets/Scripts/Services/CharacterService.cs
using System.Threading.Tasks;
using UnityEngine;

public class CharacterService : MonoBehaviour
{
    [SerializeField] private HTTPClient httpClient;
    
    public async Task<CharacterData> CreateCharacter(CharacterCreateRequest request)
    {
        var response = await httpClient.PostAsync<CharacterData>(
            "/characters", 
            request
        );
        return response;
    }
    
    public async Task<CharacterData> GetCharacter(int characterId)
    {
        return await httpClient.GetAsync<CharacterData>($"/characters/{characterId}");
    }
}
```

### Data Model Example
```csharp
// VDM/Assets/Scripts/Data/CharacterData.cs
[System.Serializable]
public class CharacterData
{
    public int id;
    public string name;
    public CharacterAttributes attributes;
    
    [System.Serializable]
    public class CharacterAttributes
    {
        public int strength;
        public int dexterity;
        public int intelligence;
        // Range: -3 to +5 as per Development Bible
    }
}
```

### Testing in Unity
```csharp
// VDM/Assets/Scripts/Tests/CharacterServiceTests.cs
using NUnit.Framework;
using UnityEngine.TestTools;
using System.Collections;

public class CharacterServiceTests
{
    private CharacterService characterService;
    
    [SetUp]
    public void Setup()
    {
        characterService = new GameObject().AddComponent<CharacterService>();
    }
    
    [UnityTest]
    public IEnumerator CreateCharacter_ValidData_ReturnsCharacter()
    {
        var request = new CharacterCreateRequest { name = "Test Character" };
        var task = characterService.CreateCharacter(request);
        
        yield return new WaitUntil(() => task.IsCompleted);
        
        Assert.IsNotNull(task.Result);
        Assert.AreEqual("Test Character", task.Result.name);
    }
}
```

## API Development

### API Design Principles
- **RESTful**: Follow REST conventions for resource endpoints
- **Consistent**: Uniform response formats and error handling
- **Versioned**: Support API versioning for backward compatibility
- **Documented**: Comprehensive OpenAPI documentation
- **Secure**: Authentication and authorization on all endpoints

### Endpoint Patterns
```python
# CRUD operations for resources
GET    /api/v1/characters           # List characters
POST   /api/v1/characters           # Create character
GET    /api/v1/characters/{id}      # Get character
PUT    /api/v1/characters/{id}      # Update character
DELETE /api/v1/characters/{id}      # Delete character

# Sub-resources
GET    /api/v1/characters/{id}/equipment
POST   /api/v1/characters/{id}/equipment

# Actions
POST   /api/v1/characters/{id}/advance    # Advance character
POST   /api/v1/combat/initiative          # Roll initiative
```

### Response Format Standards
```python
# Success response
{
    "success": true,
    "data": { ... },
    "metadata": {
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }
}

# Error response
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid character attributes",
        "details": {
            "field": "strength",
            "value": 10,
            "constraint": "must be between -3 and 5"
        }
    }
}
```

### WebSocket Events
```python
# Event format
{
    "event_type": "character.updated",
    "data": { ... },
    "timestamp": "2024-01-01T00:00:00Z",
    "session_id": "uuid-here"
}

# Common event types
- "time.advanced"
- "character.created"
- "character.updated"
- "quest.completed"
- "combat.initiated"
```

## Testing Guidelines

### Backend Testing

#### Unit Tests
```python
# backend/systems/character/tests/test_character_service.py
import pytest
from unittest.mock import Mock
from ..services.character_service import CharacterService

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def character_service(mock_repository):
    return CharacterService(mock_repository)

@pytest.mark.asyncio
async def test_create_character(character_service, mock_repository):
    # Arrange
    character_data = {"name": "Test Character"}
    mock_repository.create.return_value = Mock(id=1, name="Test Character")
    
    # Act
    result = await character_service.create_character(character_data)
    
    # Assert
    assert result.id == 1
    assert result.name == "Test Character"
    mock_repository.create.assert_called_once()
```

#### Integration Tests
```python
# backend/tests/integration/test_character_api.py
import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_create_character_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/characters", json={
            "name": "Test Character",
            "attributes": {"strength": 2, "dexterity": 1}
        })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Character"
```

### Unity Testing
```csharp
// Headless Unity testing
Unity.exe -batchmode -runTests -testPlatform playmode -testResults results.xml
```

### Test Coverage
```bash
# Backend coverage
pytest --cov=backend --cov-report=html backend/tests/

# Minimum coverage requirements
- Unit tests: 90%+
- Integration tests: 80%+
- E2E tests: Core workflows
```

## Deployment

### Development Deployment
```bash
# Docker Compose for local development
docker-compose -f docker-compose.dev.yml up

# Manual deployment
python backend/main.py  # Backend
# Unity editor for frontend
```

### Production Deployment
```bash
# Build Unity client
Unity.exe -batchmode -buildTarget StandaloneWindows64 -buildPath builds/

# Deploy backend
docker build -t visualdm-backend .
docker run -p 8000:8000 visualdm-backend

# Or use provided deployment scripts
./scripts/deploy_production.sh
```

### Environment Configuration
```bash
# Production environment variables
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@localhost/visualdm
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=your_key_here
LOG_LEVEL=info
DEBUG=false
```

## Contributing

### Development Workflow
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes**: Follow coding standards
4. **Write tests**: Ensure good coverage
5. **Submit PR**: Include description and testing notes

### Code Review Process
- All changes require review from core team member
- Automated tests must pass
- Code coverage must meet minimum thresholds
- Documentation must be updated for user-facing changes

### Issue Reporting
Use GitHub issues with appropriate labels:
- `bug`: Something isn't working
- `feature`: New feature request
- `enhancement`: Improve existing feature
- `documentation`: Documentation needs

## Standards and Best Practices

### Python Code Standards
```python
# Follow PEP 8
# Use type hints
def create_character(name: str, attributes: Dict[str, int]) -> Character:
    pass

# Async/await for I/O operations
async def save_character(character: Character) -> None:
    await repository.save(character)

# Error handling
try:
    result = await some_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### C# Code Standards
```csharp
// Follow Microsoft C# conventions
// Use async/await for network operations
public async Task<CharacterData> GetCharacterAsync(int id)
{
    return await httpClient.GetAsync<CharacterData>($"/characters/{id}");
}

// Proper error handling
try
{
    var character = await characterService.GetCharacterAsync(id);
    return character;
}
catch (HttpRequestException ex)
{
    Debug.LogError($"Failed to get character: {ex.Message}");
    throw;
}
```

### Database Guidelines
- Use migrations for schema changes
- Follow naming conventions (snake_case for tables/columns)
- Index frequently queried columns
- Use foreign keys for referential integrity

### Security Best Practices
- Validate all input data
- Use parameterized queries
- Implement proper authentication/authorization
- Store sensitive data securely
- Regular security updates

### Performance Guidelines
- Profile critical paths
- Use caching for frequently accessed data
- Optimize database queries
- Implement pagination for large datasets
- Monitor memory usage

---

This developer guide provides the foundation for contributing to Visual DM. For specific implementation details, refer to the Development Bible and system documentation. 