# Entity Management System

The Entity Management System is a core component of Visual DM that handles the creation, manipulation, and relationships between various entities in the game world, such as characters, locations, items, and more.

## Overview

The system consists of two main components:

1. **Unity Entity Manager**: A C# component that manages entities in the Unity frontend.
2. **Backend Entity Service**: A Python FastAPI service that maintains the database of entities and provides synchronization over WebSockets.

The system supports:
- Dynamic entity creation and modification
- Relationships between entities
- Queries and filtering
- Real-time synchronization between frontend and backend
- Type-based entity categorization

## Architecture

```
┌───────────────────┐      WebSocket       ┌───────────────────┐
│                   │◄─────Connection─────►│                   │
│  Unity Frontend   │                      │   Python Backend  │
│  (EntityManager)  │                      │  (EntityService)  │
│                   │                      │                   │
└───────────────────┘                      └───────────────────┘
        │                                          │
        │                                          │
        ▼                                          ▼
┌───────────────────┐                     ┌───────────────────┐
│   Unity Entities  │                     │ Backend Entities  │
│ - CharacterEntity │                     │ - Entity DB       │
│ - LocationEntity  │                     │ - Relationships   │
│ - ItemEntity      │                     │ - Queries         │
└───────────────────┘                     └───────────────────┘
```

## Key Features

### Entity Types

The system supports various entity types, defined in `data/builders/entity_types.json`. Default types include:

- **Characters**: NPCs, players, creatures
- **Locations**: Cities, dungeons, shops
- **Items**: Weapons, armor, consumables
- **Factions**: Organizations, guilds, groups
- **Quests**: Missions, objectives
- **Events**: Scheduled happenings, triggered events

### Relationships

Entities can form relationships with each other as defined in `data/builders/relationship_types.json`. Examples include:

- **Knows**: Character knows another character or location
- **Located At**: Entity is located at a location
- **Owns**: Character owns an item
- **Member Of**: Character is a member of a faction
- **Allied With**: Faction is allied with another faction
- **Hostile To**: Faction is hostile to another faction

### Queries

The system supports complex queries to find entities based on:

- Type
- Properties
- Name (partial matching)
- Relationships with other entities

### WebSocket Communication

The frontend and backend communicate via a WebSocket connection that provides:

- Real-time entity updates
- Entity creation/deletion notifications
- Relationship changes
- Query results

## Unity Implementation

### Core Classes

#### `EntityManager`

A singleton MonoBehaviour that manages all entities in the Unity application:

```csharp
// Located at VDM/Assets/Scripts/VisualDM/Systems/EntityManager.cs

public class EntityManager : MonoBehaviour
{
    // Create a new entity
    public T CreateEntity<T>(string id, Action<T> configure = null) where T : Entity, new() { ... }
    
    // Get an entity by ID
    public Entity GetEntity(string id) { ... }
    
    // Update an existing entity
    public T UpdateEntity<T>(string id, Action<T> update) where T : Entity { ... }
    
    // Delete an entity
    public bool DeleteEntity(string id) { ... }
    
    // Find entities by various criteria
    public IEnumerable<Entity> FindEntities(Func<Entity, bool> predicate) { ... }
    
    // Create relationship between entities
    public EntityRelationship CreateRelationship(string sourceId, string targetId, string type) { ... }
    
    // Find relationships
    public IEnumerable<EntityRelationship> GetRelationshipsForEntity(string entityId) { ... }
}
```

#### `Entity`

Base class for all entity types:

```csharp
// Located at VDM/Assets/Scripts/VisualDM/Data/Entity.cs

public class Entity
{
    // Basic properties
    public string Id { get; }
    public string Name { get; set; }
    public string Description { get; set; }
    public string EntityType { get; set; }
    
    // Custom properties
    public object GetProperty(string name) { ... }
    public void SetProperty(string name, object value) { ... }
    
    // Events
    public event Action<Entity, string, object, object> OnPropertyChanged;
}
```

#### `EntityWebSocketClient`

Handles synchronization with the backend:

```csharp
// Located at VDM/Assets/Scripts/VisualDM/Systems/EntityWebSocketClient.cs

public class EntityWebSocketClient : MonoBehaviour
{
    // Connect to the backend
    public async void Connect() { ... }
    
    // Subscribe to entity updates
    public async Task SubscribeToEntity(string entityId) { ... }
    
    // Query entities
    public async Task QueryEntities(Dictionary<string, object> query) { ... }
    
    // Update an entity
    public async Task UpdateEntity(string entityId, object entityData) { ... }
    
    // Events for receiving updates
    public event Action<string, JObject> OnEntityCreated;
    public event Action<string, JObject> OnEntityUpdated;
    public event Action<string> OnEntityDeleted;
}
```

### Entity Types

The system includes specialized entity classes for different types:

- `CharacterEntity`: For characters, NPCs
- `LocationEntity`: For game locations
- `ItemEntity`: For items, weapons, etc.

### Usage Examples

```csharp
// Get the entity manager
var entityManager = EntityManager.Instance;

// Create a character
var character = entityManager.CreateEntity<CharacterEntity>("hero1", c => {
    c.Name = "Hero";
    c.Description = "The main protagonist";
    c.SetProperty("level", 1);
});

// Create a location
var location = entityManager.CreateEntity<LocationEntity>("town1", l => {
    l.Name = "Starting Town";
    l.Description = "A small town where the adventure begins";
});

// Create relationship (hero is at the town)
entityManager.CreateRelationship("hero1", "town1", "located_at");

// Find all entities at the town
var entitiesAtTown = entityManager.FindEntities(e => 
    entityManager.HasRelationship(e.Id, "town1", "located_at"));
```

## Backend Implementation

### Key Components

#### Entity Service

The `EntityService` class provides the core functionality:

```python
# Located at backend/services/entity_service.py

class EntityService:
    # Entity CRUD operations
    async def create_entity(self, entity_data: EntityCreate) -> Entity: ...
    async def get_entity(self, entity_id: str) -> Optional[Entity]: ...
    async def update_entity(self, entity_id: str, entity_data: EntityUpdate) -> Optional[Entity]: ...
    async def delete_entity(self, entity_id: str) -> bool: ...
    
    # Relationship operations
    async def create_relationship(self, relationship_data: EntityRelationshipCreate) -> Optional[EntityRelationship]: ...
    async def get_relationships_for_entity(self, entity_id: str) -> List[EntityRelationship]: ...
    
    # Query operations
    async def query_entities(self, query: EntityQuery) -> List[Entity]: ...
    async def get_entity_graph(self, center_entity_id: str, max_depth: int = 2) -> EntityGraph: ...
    
    # WebSocket operations
    async def connect_client(self, websocket: WebSocket) -> None: ...
    async def subscribe_to_entity(self, entity_id: str, websocket: WebSocket) -> bool: ...
```

#### API Endpoints

The API provides REST endpoints and WebSocket connections:

```python
# Located at backend/api/v1/entity_api.py

# REST endpoints
@router.get("/")
async def list_entities(...): ...

@router.post("/")
async def create_entity(...): ...

@router.get("/{entity_id}")
async def get_entity(...): ...

# WebSocket endpoint (in main.py)
@app.websocket("/api/v1/entities/ws")
async def websocket_endpoint(websocket: WebSocket): ...
```

### Data Models

The system uses Pydantic models for data validation:

```python
# Located at backend/models/entity.py

class Entity(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class EntityRelationship(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any]
```

### Configuration Files

Entity and relationship types are defined in JSON configuration files:

- `data/builders/entity_types.json`: Defines the types of entities
- `data/builders/relationship_types.json`: Defines the types of relationships

## WebSocket Protocol

### Message Format

Messages between the client and server follow this format:

```json
{
  "action": "action_name",
  "entity_id": "optional_entity_id",
  "data": {
    // Action-specific data
  }
}
```

### Actions

Available actions include:

- `subscribe`: Subscribe to entity updates
- `unsubscribe`: Unsubscribe from entity updates
- `query`: Query entities
- `create`: Create a new entity
- `update`: Update an existing entity
- `delete`: Delete an entity
- `create_relationship`: Create a relationship

### Events

The server sends events in this format:

```json
{
  "event": "event_name",
  "entity_id": "optional_entity_id",
  "data": {
    // Event-specific data
  }
}
```

Event types include:

- `entity_created`: A new entity was created
- `entity_updated`: An entity was updated
- `entity_deleted`: An entity was deleted
- `relationship_created`: A new relationship was created
- `relationship_updated`: A relationship was updated
- `relationship_deleted`: A relationship was deleted
- `query_results`: Results from a query

## Usage Examples

### Backend (Python)

```python
from backend.services.entity_service import get_entity_service
from backend.models.entity import EntityCreate

# Get the entity service
entity_service = get_entity_service()

# Create a character
character_data = EntityCreate(
    name="Hero",
    description="The main protagonist",
    type="character",
    properties={
        "level": 1,
        "health": 100
    }
)
character = await entity_service.create_entity(character_data)

# Create a location
location_data = EntityCreate(
    name="Starting Town",
    description="A small town where the adventure begins",
    type="location",
    properties={
        "population": 500
    }
)
location = await entity_service.create_entity(location_data)

# Create a relationship
relationship_data = EntityRelationshipCreate(
    source_id=character.id,
    target_id=location.id,
    type="located_at",
    properties={
        "permanent": False
    }
)
relationship = await entity_service.create_relationship(relationship_data)

# Query entities
query = EntityQuery(
    type="character",
    related_to=location.id,
    relationship_type="located_at"
)
results = await entity_service.query_entities(query)
```

### Unity (C#)

```csharp
// Get the WebSocket client
var client = EntityWebSocketClient.Instance;

// Connect to the backend
client.Connect();

// Create a character
var characterData = new Dictionary<string, object>
{
    { "name", "Hero" },
    { "description", "The main protagonist" },
    { "type", "character" },
    { "properties", new Dictionary<string, object>
        {
            { "level", 1 },
            { "health", 100 }
        }
    }
};

// Send the creation request
await client.SendMessage(new
{
    action = "create",
    data = characterData
});

// Subscribe to an entity
await client.SubscribeToEntity("entity_id");

// Query entities
var query = new Dictionary<string, object>
{
    { "type", "character" },
    { "related_to", "location_id" },
    { "relationship_type", "located_at" }
};
await client.QueryEntities(query);
```

## Future Enhancements

- Persistent storage for entities (currently in-memory)
- Advanced visualization of entity relationships
- Entity templates and inheritance
- Entity history and versioning
- Entity permissions and access control

## Conclusion

The Entity Management System provides a flexible foundation for managing game world data in Visual DM. Its modular design allows for easy extension with new entity types and relationships, while the WebSocket communication ensures real-time synchronization between the frontend and backend. 