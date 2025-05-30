# Visual DM Architecture Documentation

## Overview

Visual DM follows a modular, event-driven architecture that ensures clean separation between frontend Unity client and backend Python services. The architecture is designed to support scalable development, comprehensive testing, and easy maintenance.

## Architecture Principles

### 1. Frontend-Backend Alignment
The Unity frontend structure mirrors the backend systems architecture exactly:

```
VDM/Assets/Scripts/Runtime/     ←→     backend/systems/
├── Analytics/                  ←→     ├── analytics/
├── Character/                  ←→     ├── character/
├── Combat/                     ←→     ├── combat/
└── ...                         ←→     └── ...
```

### 2. Separation of Concerns
- **Models/**: Data Transfer Objects (DTOs) matching backend API schemas
- **Services/**: HTTP/WebSocket communication with backend
- **UI/**: Unity UI components and controllers
- **Integration/**: Unity-specific MonoBehaviour/ScriptableObject integration

### 3. Event-Driven Communication
- Loose coupling through centralized event system
- WebSocket real-time updates mapped to Unity events
- Cross-system communication via event bus

### 4. Service Layer Pattern
- HTTP services for CRUD operations
- WebSocket handlers for real-time features
- Caching for offline/performance optimization
- Error handling and retry mechanisms

## System Architecture Layers

### Backend Layer (FastAPI + Python)
- **API Layer**: RESTful endpoints with FastAPI
- **Service Layer**: Business logic and data processing
- **Repository Layer**: Data persistence and retrieval
- **Event System**: Cross-system communication
- **WebSocket Layer**: Real-time event broadcasting

### Frontend Layer (Unity + C#)
- **UI Layer**: Unity UI components and visual presentation
- **Service Layer**: Backend communication and caching
- **Integration Layer**: Unity-specific system integration
- **Event Layer**: Unity event system integration

## Core Systems

### Foundation Systems (Implement First)
1. **Data System**: Core data infrastructure and synchronization
2. **Events System**: Event bus and communication framework
3. **Time System**: Game time progression and scheduling

### Core Game Systems
1. **Character System**: Character creation, progression, and management
2. **Combat System**: Turn-based combat mechanics and visualization
3. **Quest System**: Quest tracking, generation, and completion
4. **Faction System**: Organization management and politics

### World Systems
1. **WorldGeneration System**: Procedural world creation
2. **Region System**: Geographic area management
3. **WorldState System**: Global state persistence and tracking

### Social & Narrative Systems
1. **Dialogue System**: Conversation trees and NPC interactions
2. **NPC System**: Non-player character behavior and management
3. **Memory System**: Character relationships and history
4. **Rumor System**: Information propagation networks

### Economic Systems
1. **Economy System**: Trade, markets, and economic simulation
2. **Inventory System**: Item storage and organization
3. **Crafting System**: Item creation and modification
4. **Equipment System**: Gear management and customization

### Advanced Systems
1. **Magic System**: Spellcasting and magical mechanics
2. **Religion System**: Deity worship and religious systems
3. **Diplomacy System**: Inter-faction relationships
4. **Analytics System**: Performance monitoring and metrics

## Communication Patterns

### Frontend to Backend
```csharp
// HTTP Service Pattern
public class CharacterService : BaseHttpService<CharacterDto>
{
    public async Task<CharacterDto> GetCharacterAsync(int id)
    {
        return await GetAsync($"/api/characters/{id}");
    }
}

// WebSocket Handler Pattern  
public class CharacterWebSocketHandler : BaseWebSocketHandler
{
    protected override void HandleMessage(WebSocketMessage message)
    {
        if (message.Type == "character_updated")
        {
            // Update local cache and trigger UI refresh
            EventBus.Publish(new CharacterUpdatedEvent(message.Data));
        }
    }
}
```

### Cross-System Integration
```csharp
// Event-driven communication
public class QuestSystem : MonoBehaviour
{
    void Start()
    {
        EventBus.Subscribe<CharacterLevelUpEvent>(OnCharacterLevelUp);
    }
    
    private void OnCharacterLevelUp(CharacterLevelUpEvent evt)
    {
        // Check for level-based quest unlocks
        CheckQuestRequirements(evt.Character);
    }
}
```

## Data Flow Architecture

### 1. User Input → Frontend
User interactions trigger Unity UI events

### 2. Frontend → Backend  
Service layer sends HTTP requests or WebSocket messages

### 3. Backend Processing
Business logic processes requests and updates state

### 4. Backend → Frontend
WebSocket broadcasts real-time updates to subscribed clients

### 5. Frontend Updates
UI components refresh based on received data

## Performance Considerations

### Caching Strategy
- **Client-side caching**: Reduce API calls for frequently accessed data
- **Intelligent invalidation**: Update cache based on WebSocket events
- **Offline support**: Local storage for critical game state

### Resource Management
- **Asset streaming**: Dynamic loading of visual assets
- **Memory optimization**: Efficient Unity object lifecycle management
- **Background processing**: Non-blocking operations for heavy computations

## Security Architecture

### Authentication Flow
1. User credentials → Backend authentication
2. JWT token issued with expiration
3. Token included in all API requests
4. Automatic token refresh handling

### Data Validation
- **Frontend validation**: Immediate user feedback
- **Backend validation**: Authoritative data integrity
- **Schema compliance**: Ensure data matches expected formats

## Development Workflow

### 1. System Development
- Reference Development Bible for requirements
- Implement backend business logic first
- Create corresponding frontend services and UI
- Write comprehensive tests for all layers

### 2. Integration Testing
- Unit tests for individual components
- Integration tests for system communication
- End-to-end tests for complete user workflows
- Performance testing under realistic load

### 3. Documentation
- API documentation with examples
- System interaction diagrams
- Developer guides for each system
- User guides for end-user features

## Deployment Architecture

### Development Environment
- Local FastAPI backend server
- Unity editor for frontend development
- PostgreSQL database for persistence
- WebSocket connections for real-time features

### Production Environment  
- Containerized FastAPI backend
- Built Unity client application
- Cloud database with backup/recovery
- Load balancing for scalable WebSocket connections

## Monitoring and Observability

### Performance Monitoring
- API response time tracking
- Frontend frame rate monitoring
- Memory usage analysis
- Network communication metrics

### Error Tracking
- Centralized logging system
- Error aggregation and alerting
- Performance bottleneck identification
- User experience monitoring

## Migration Strategy

The architecture supports incremental migration from the old structure:

1. **Foundation Phase**: Migrate core systems (Data, Events, Time)
2. **Core Phase**: Migrate primary gameplay systems
3. **Feature Phase**: Add advanced systems and UI polish
4. **Optimization Phase**: Performance tuning and monitoring
5. **Documentation Phase**: Complete user and developer documentation

This architecture ensures maintainable, scalable, and testable code that supports the complex requirements of Visual DM while providing a clear path for future development and feature additions. 