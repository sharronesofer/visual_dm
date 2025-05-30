# Developer Getting Started Guide

## Prerequisites

### Required Software
- **Unity 2022.3 LTS** - Unity game engine
- **Visual Studio 2022** or **JetBrains Rider** - C# IDE
- **Python 3.11+** - Backend development
- **Git** - Version control
- **PostgreSQL 14+** - Database (for backend development)

### Recommended Tools
- **Unity Hub** - Unity version management
- **Postman** - API testing
- **pgAdmin** - PostgreSQL management
- **Visual Studio Code** - Text editor for documentation

## Initial Setup

### 1. Clone Repository
```bash
git clone [repository-url]
cd visual-dm
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 3. Database Setup
```bash
# Install PostgreSQL and create database
createdb visual_dm_dev

# Run migrations
alembic upgrade head

# Seed initial data
python scripts/seed_database.py
```

### 4. Unity Setup
```bash
# Open Unity Hub
# Add project: /path/to/visual-dm/VDM
# Open with Unity 2022.3 LTS
```

## Project Structure Overview

### Backend Structure
```
backend/
├── systems/              # Game systems (business logic)
│   ├── character/        # Character management
│   ├── combat/          # Combat mechanics
│   ├── quest/           # Quest system
│   └── ...              # Other systems
├── api/                 # API endpoints and routing
├── core/                # Core utilities and infrastructure
├── tests/               # Test suite
└── main.py             # Application entry point
```

### Frontend Structure
```
VDM/Assets/Scripts/Runtime/
├── Character/           # Character UI and frontend logic
│   ├── Models/         # DTOs matching backend
│   ├── Services/       # API communication
│   ├── UI/            # Unity UI components
│   └── Integration/   # Unity-specific integration
├── Combat/             # Combat UI and frontend logic
├── Quest/              # Quest UI and frontend logic
└── ...                 # Other systems
```

## Development Workflow

### 1. Understanding the System Architecture

Before starting development, familiarize yourself with:
- **Development Bible** (`docs/development_bible.md`) - Complete system specifications
- **Architecture Documentation** (`docs/architecture/README.md`) - High-level design
- **API Contracts** (`docs/api_contracts.md`) - Backend API specifications

### 2. Creating a New Feature

#### Step 1: Backend Development
```bash
# 1. Create or modify backend system
cd backend/systems/[system-name]/

# 2. Implement models
# Edit models.py with Pydantic models

# 3. Implement services  
# Edit services.py with business logic

# 4. Implement API endpoints
# Edit routers.py with FastAPI routes

# 5. Write tests
cd ../../tests/systems/[system-name]/
# Create comprehensive test files
```

#### Step 2: Frontend Development
```csharp
// 1. Create DTOs (Models/)
public class CharacterDto
{
    public int Id { get; set; }
    public string Name { get; set; }
    // Match backend model exactly
}

// 2. Create service layer (Services/)
public class CharacterService : BaseHttpService<CharacterDto>
{
    public async Task<CharacterDto> GetCharacterAsync(int id)
    {
        return await GetAsync($"/api/characters/{id}");
    }
}

// 3. Create UI components (UI/)
public class CharacterPanel : MonoBehaviour
{
    private CharacterService _characterService;
    
    void Start()
    {
        _characterService = ServiceLocator.Get<CharacterService>();
    }
}

// 4. Unity integration (Integration/)
public class CharacterManager : MonoBehaviour
{
    // Unity-specific lifecycle management
}
```

### 3. Testing Your Changes

#### Backend Testing
```bash
# Run all tests
pytest

# Run specific system tests
pytest tests/systems/character/

# Run with coverage
pytest --cov=backend

# Run integration tests
pytest tests/integration/
```

#### Frontend Testing
```csharp
// Create unit tests in Unity Test Runner
[Test]
public void CharacterService_GetCharacter_ReturnsValidData()
{
    // Test implementation
}

// Create integration tests
[UnityTest]
public IEnumerator CharacterUI_DisplaysCharacterData()
{
    // Test implementation
    yield return null;
}
```

## System Development Patterns

### 1. Backend Service Pattern
```python
# services.py
class CharacterService:
    def __init__(self, character_repository: CharacterRepository):
        self.character_repository = character_repository
    
    async def get_character(self, character_id: int) -> Character:
        character = await self.character_repository.get_by_id(character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {character_id} not found")
        return character
    
    async def create_character(self, character_data: CharacterCreate) -> Character:
        # Validation and business logic
        character = Character(**character_data.dict())
        return await self.character_repository.create(character)
```

### 2. Frontend Service Pattern
```csharp
// CharacterService.cs
public class CharacterService : BaseHttpService<CharacterDto>
{
    private readonly ICacheService _cache;
    private readonly IWebSocketService _webSocket;
    
    public CharacterService(ICacheService cache, IWebSocketService webSocket)
    {
        _cache = cache;
        _webSocket = webSocket;
        
        // Subscribe to real-time updates
        _webSocket.Subscribe<CharacterUpdatedEvent>(OnCharacterUpdated);
    }
    
    public async Task<CharacterDto> GetCharacterAsync(int id)
    {
        // Check cache first
        var cached = _cache.Get<CharacterDto>($"character_{id}");
        if (cached != null) return cached;
        
        // Fetch from API
        var character = await GetAsync($"/api/characters/{id}");
        
        // Cache result
        _cache.Set($"character_{id}", character, TimeSpan.FromMinutes(5));
        
        return character;
    }
    
    private void OnCharacterUpdated(CharacterUpdatedEvent evt)
    {
        // Invalidate cache and notify UI
        _cache.Remove($"character_{evt.CharacterId}");
        EventBus.Publish(evt);
    }
}
```

### 3. UI Component Pattern
```csharp
// CharacterPanel.cs
public class CharacterPanel : MonoBehaviour
{
    [SerializeField] private Text _nameText;
    [SerializeField] private Text _levelText;
    [SerializeField] private Button _editButton;
    
    private CharacterService _characterService;
    private CharacterDto _currentCharacter;
    
    void Start()
    {
        _characterService = ServiceLocator.Get<CharacterService>();
        _editButton.onClick.AddListener(OnEditClicked);
        
        // Subscribe to character updates
        EventBus.Subscribe<CharacterUpdatedEvent>(OnCharacterUpdated);
    }
    
    public async void DisplayCharacter(int characterId)
    {
        try
        {
            _currentCharacter = await _characterService.GetCharacterAsync(characterId);
            UpdateUI();
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to load character {characterId}: {ex.Message}");
            // Show error UI
        }
    }
    
    private void UpdateUI()
    {
        _nameText.text = _currentCharacter.Name;
        _levelText.text = $"Level {_currentCharacter.Level}";
    }
    
    private void OnCharacterUpdated(CharacterUpdatedEvent evt)
    {
        if (evt.CharacterId == _currentCharacter?.Id)
        {
            // Refresh character data
            DisplayCharacter(_currentCharacter.Id);
        }
    }
    
    private void OnEditClicked()
    {
        // Open character edit dialog
        var editDialog = UIManager.OpenDialog<CharacterEditDialog>();
        editDialog.Initialize(_currentCharacter);
    }
}
```

## Common Development Tasks

### Adding a New System

1. **Backend System Creation**:
   ```bash
   # Create system directory
   mkdir backend/systems/new_system
   
   # Create standard files
   touch backend/systems/new_system/__init__.py
   touch backend/systems/new_system/models.py
   touch backend/systems/new_system/services.py
   touch backend/systems/new_system/repositories.py
   touch backend/systems/new_system/routers.py
   touch backend/systems/new_system/schemas.py
   ```

2. **Frontend System Creation**:
   ```bash
   # Create Unity system directory
   mkdir VDM/Assets/Scripts/Runtime/NewSystem
   mkdir VDM/Assets/Scripts/Runtime/NewSystem/Models
   mkdir VDM/Assets/Scripts/Runtime/NewSystem/Services
   mkdir VDM/Assets/Scripts/Runtime/NewSystem/UI
   mkdir VDM/Assets/Scripts/Runtime/NewSystem/Integration
   ```

3. **Follow Development Bible**: Reference the system specification in `docs/development_bible.md`

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new_table"

# Review generated migration
# Edit migration file if needed

# Apply migration
alembic upgrade head
```

### API Endpoint Development

```python
# routers.py
from fastapi import APIRouter, Depends, HTTPException
from .services import CharacterService
from .schemas import CharacterResponse, CharacterCreate

router = APIRouter(prefix="/api/characters", tags=["characters"])

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: int,
    character_service: CharacterService = Depends()
):
    try:
        character = await character_service.get_character(character_id)
        return CharacterResponse.from_orm(character)
    except CharacterNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")

@router.post("/", response_model=CharacterResponse)
async def create_character(
    character_data: CharacterCreate,
    character_service: CharacterService = Depends()
):
    character = await character_service.create_character(character_data)
    return CharacterResponse.from_orm(character)
```

## Debugging and Troubleshooting

### Backend Debugging
```python
# Add logging
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")

# Use debugger
import pdb; pdb.set_trace()  # Python debugger
```

### Frontend Debugging
```csharp
// Unity Console logging
Debug.Log("Info message");
Debug.LogWarning("Warning message");
Debug.LogError("Error message");

// Conditional compilation for debug builds
#if UNITY_EDITOR
    Debug.Log("Debug build message");
#endif

// Use Unity Profiler for performance analysis
Profiler.BeginSample("MyFunction");
// Your code here
Profiler.EndSample();
```

### Common Issues

1. **CORS Issues**: Ensure backend CORS settings allow Unity WebGL builds
2. **Serialization Issues**: Ensure DTOs match between backend and frontend exactly
3. **WebSocket Connection**: Check network configuration and firewall settings
4. **Database Connection**: Verify connection string and database accessibility

## Code Style and Conventions

### Backend (Python)
- Follow PEP 8 style guide
- Use type hints for all function parameters and returns
- Use async/await for all database operations
- Write docstrings for all public functions and classes

### Frontend (C#)
- Follow Unity C# style guide
- Use PascalCase for public members
- Use camelCase for private fields with underscore prefix
- Use explicit access modifiers (public, private, protected)

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-system

# Make commits with descriptive messages
git commit -m "feat(character): Add character creation service

- Implement CharacterService.CreateCharacter method
- Add validation for character data
- Include comprehensive error handling"

# Push and create pull request
git push origin feature/new-system
```

## Resources

### Documentation
- **Development Bible**: Complete system specifications
- **API Documentation**: Backend API reference
- **Unity Documentation**: Official Unity documentation
- **FastAPI Documentation**: Backend framework documentation

### Testing
- **pytest**: Python testing framework
- **Unity Test Runner**: Unity testing framework
- **Postman Collections**: API testing templates

### Tools
- **Unity Profiler**: Performance analysis
- **Unity Console**: Runtime debugging
- **pgAdmin**: Database management
- **Git**: Version control

## Getting Help

1. **Check Documentation**: Start with Development Bible and architecture docs
2. **Search Issues**: Check existing GitHub issues for similar problems
3. **Code Review**: Ask team members for code review and feedback
4. **Testing**: Write tests to verify your understanding of the system
5. **Incremental Development**: Start small and build up complexity gradually

This guide provides the foundation for developing with Visual DM's new architecture. As you become more familiar with the patterns and systems, you'll be able to contribute effectively to all areas of the project. 