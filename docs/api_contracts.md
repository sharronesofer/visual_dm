# Visual DM API Contracts Specification

## Overview

This document defines the comprehensive API contracts between the Unity frontend client and the Python FastAPI backend for the Visual DM project. The API follows RESTful principles for CRUD operations and uses WebSocket connections for real-time updates.

**Base URL**: `http://localhost:8000` (development)

## Authentication & Security

### JWT Authentication
All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints
```http
POST /auth/login
POST /auth/register  
POST /auth/logout
GET /auth/me
POST /auth/refresh
```

## Core API Systems

### 1. Combat System (`/combat`)

**Endpoints:**
- `POST /combat/state` - Create new combat instance
- `GET /combat/state/{combat_id}` - Get combat state
- `PUT /combat/state/{combat_id}` - Update combat state
- `DELETE /combat/state/{combat_id}` - End combat instance
- `GET /combat/states` - List all active combats

**DTOs:**
```csharp
public class CombatStateDTO
{
    [JsonPropertyName("combat_id")]
    public string CombatId { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } // "active", "ended", "paused"
    
    [JsonPropertyName("participants")]
    public List<CombatParticipantDTO> Participants { get; set; }
    
    [JsonPropertyName("current_turn")]
    public int CurrentTurn { get; set; }
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
}

public class CombatParticipantDTO
{
    [JsonPropertyName("character_id")]
    public string CharacterId { get; set; }
    
    [JsonPropertyName("initiative")]
    public int Initiative { get; set; }
    
    [JsonPropertyName("hit_points")]
    public int HitPoints { get; set; }
    
    [JsonPropertyName("max_hit_points")]
    public int MaxHitPoints { get; set; }
    
    [JsonPropertyName("position")]
    public Vector2DTO Position { get; set; }
    
    [JsonPropertyName("status_effects")]
    public List<StatusEffectDTO> StatusEffects { get; set; }
}
```

### 2. Character System (`/characters`)

**Endpoints:**
- `POST /characters` - Create character
- `GET /characters/{character_id}` - Get character by ID
- `GET /characters/by-game-id/{character_id}` - Get by game ID
- `PUT /characters/{character_id}` - Update character
- `DELETE /characters/{character_id}` - Soft delete character
- `GET /characters` - Search/list characters with filters
- `POST /characters/{character_id}/experience` - Grant XP
- `POST /characters/{character_id}/skills` - Increase skill
- `POST /characters/{character_id}/abilities` - Add ability
- `GET /characters/{character_id}/progression` - Get progression history

**DTOs:**
```csharp
public class CharacterDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("character_id")]
    [Required]
    public string CharacterId { get; set; }
    
    [JsonPropertyName("character_name")]
    [Required]
    public string CharacterName { get; set; }
    
    [JsonPropertyName("race")]
    [Required]
    public string Race { get; set; }
    
    [JsonPropertyName("level")]
    public int Level { get; set; } = 1;
    
    [JsonPropertyName("experience_points")]
    public int ExperiencePoints { get; set; } = 0;
    
    [JsonPropertyName("attributes")]
    public CharacterAttributesDTO Attributes { get; set; }
    
    [JsonPropertyName("skills")]
    public Dictionary<string, int> Skills { get; set; }
    
    [JsonPropertyName("abilities")]
    public List<string> Abilities { get; set; }
    
    [JsonPropertyName("background")]
    public string Background { get; set; }
    
    [JsonPropertyName("personality")]
    public string Personality { get; set; }
    
    [JsonPropertyName("alignment")]
    public string Alignment { get; set; }
    
    [JsonPropertyName("hit_points")]
    public int HitPoints { get; set; }
    
    [JsonPropertyName("max_hit_points")]
    public int MaxHitPoints { get; set; }
    
    [JsonPropertyName("is_active")]
    public bool IsActive { get; set; } = true;
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
    
    [JsonPropertyName("updated_at")]
    public DateTime UpdatedAt { get; set; }
}

public class CharacterAttributesDTO
{
    [JsonPropertyName("strength")]
    [Range(-3, 5)]
    public int Strength { get; set; }
    
    [JsonPropertyName("dexterity")]
    [Range(-3, 5)]
    public int Dexterity { get; set; }
    
    [JsonPropertyName("constitution")]
    [Range(-3, 5)]
    public int Constitution { get; set; }
    
    [JsonPropertyName("intelligence")]
    [Range(-3, 5)]
    public int Intelligence { get; set; }
    
    [JsonPropertyName("wisdom")]
    [Range(-3, 5)]
    public int Wisdom { get; set; }
    
    [JsonPropertyName("charisma")]
    [Range(-3, 5)]
    public int Charisma { get; set; }
}
```

### 3. Quest System (`/quests`)

**Endpoints:**
- `POST /quests` - Create quest
- `GET /quests/{quest_id}` - Get quest details
- `PUT /quests/{quest_id}` - Update quest
- `DELETE /quests/{quest_id}` - Delete quest
- `GET /quests` - List quests with filters
- `POST /quests/{quest_id}/progress` - Update quest progress
- `POST /quests/{quest_id}/complete` - Complete quest

**DTOs:**
```csharp
public class QuestDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("title")]
    [Required]
    public string Title { get; set; }
    
    [JsonPropertyName("description")]
    [Required]
    public string Description { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } // "available", "active", "completed", "failed"
    
    [JsonPropertyName("objectives")]
    public List<QuestObjectiveDTO> Objectives { get; set; }
    
    [JsonPropertyName("rewards")]
    public QuestRewardsDTO Rewards { get; set; }
    
    [JsonPropertyName("prerequisites")]
    public List<string> Prerequisites { get; set; }
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
}
```

### 4. Time System (`/time`)

**Endpoints:**
- `GET /time/current` - Get current game time
- `POST /time/advance` - Advance time
- `GET /time/calendar` - Get calendar information
- `POST /time/pause` - Pause time advancement
- `POST /time/resume` - Resume time advancement

**DTOs:**
```csharp
public class GameTimeDTO
{
    [JsonPropertyName("year")]
    public int Year { get; set; }
    
    [JsonPropertyName("month")]
    public int Month { get; set; }
    
    [JsonPropertyName("day")]
    public int Day { get; set; }
    
    [JsonPropertyName("hour")]
    public int Hour { get; set; }
    
    [JsonPropertyName("minute")]
    public int Minute { get; set; }
    
    [JsonPropertyName("is_paused")]
    public bool IsPaused { get; set; }
    
    [JsonPropertyName("time_scale")]
    public float TimeScale { get; set; }
}
```

### 5. Region System (`/regions`)

**Endpoints:**
- `GET /regions` - List all regions
- `GET /regions/{region_id}` - Get region details
- `POST /regions` - Create region
- `PUT /regions/{region_id}` - Update region
- `GET /regions/{region_id}/population` - Get region population
- `GET /regions/{region_id}/economy` - Get economic data

**DTOs:**
```csharp
public class RegionDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("name")]
    [Required]
    public string Name { get; set; }
    
    [JsonPropertyName("type")]
    public string Type { get; set; } // "urban", "rural", "wilderness"
    
    [JsonPropertyName("population")]
    public int Population { get; set; }
    
    [JsonPropertyName("coordinates")]
    public CoordinatesDTO Coordinates { get; set; }
    
    [JsonPropertyName("biome")]
    public string Biome { get; set; }
    
    [JsonPropertyName("resources")]
    public Dictionary<string, float> Resources { get; set; }
    
    [JsonPropertyName("settlements")]
    public List<SettlementDTO> Settlements { get; set; }
}
```

### 6. World Generation System (`/world-generation`)

**Endpoints:**
- `POST /world-generation/generate` - Generate world
- `GET /world-generation/parameters` - Get generation parameters
- `POST /world-generation/parameters` - Set generation parameters
- `GET /world-generation/progress` - Get generation progress
- `POST /world-generation/preview` - Generate preview

**DTOs:**
```csharp
public class WorldGenerationParametersDTO
{
    [JsonPropertyName("seed")]
    public int Seed { get; set; }
    
    [JsonPropertyName("world_size")]
    public Vector2IntDTO WorldSize { get; set; }
    
    [JsonPropertyName("biome_settings")]
    public BiomeSettingsDTO BiomeSettings { get; set; }
    
    [JsonPropertyName("region_count")]
    [Range(1, 1000)]
    public int RegionCount { get; set; }
    
    [JsonPropertyName("settlement_density")]
    [Range(0.0f, 1.0f)]
    public float SettlementDensity { get; set; }
}
```

### 7. Population System (`/population`)

**Endpoints:**
- `GET /population/demographics` - Get demographic data
- `GET /population/migration` - Get migration patterns
- `POST /population/update` - Update population data
- `GET /population/growth` - Get growth statistics

### 8. Arc System (`/arcs`)

**Endpoints:**
- `GET /arcs` - List narrative arcs
- `POST /arcs` - Create arc
- `GET /arcs/{arc_id}` - Get arc details
- `PUT /arcs/{arc_id}` - Update arc
- `POST /arcs/{arc_id}/progress` - Progress arc

### 9. Motif System (`/motifs`)

**Endpoints:**
- `GET /motifs` - List motifs
- `POST /motifs` - Create motif
- `GET /motifs/{motif_id}` - Get motif details
- `PUT /motifs/{motif_id}` - Update motif

### 10. Relationship System (`/relationships`)

**Endpoints:**
- `GET /relationships` - List relationships
- `POST /relationships` - Create relationship
- `GET /relationships/{relationship_id}` - Get relationship
- `PUT /relationships/{relationship_id}` - Update relationship
- `DELETE /relationships/{relationship_id}` - Delete relationship

### 11. Economy System (`/economy`)

**Endpoints:**
- `GET /economy/markets` - Get market data
- `GET /economy/trade-routes` - Get trade routes
- `POST /economy/transactions` - Record transaction
- `GET /economy/prices` - Get item prices

### 12. Inventory System (`/inventory`)

**Endpoints:**
- `GET /inventory/{character_id}` - Get character inventory
- `POST /inventory/{character_id}/items` - Add item to inventory
- `PUT /inventory/{character_id}/items/{item_id}` - Update item
- `DELETE /inventory/{character_id}/items/{item_id}` - Remove item

## WebSocket Real-Time API (`/ws`)

The WebSocket endpoint provides real-time updates for:

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Message Format
All WebSocket messages use this format:
```json
{
  "type": "message_type",
  "data": { /* message-specific data */ },
  "timestamp": "2025-01-29T12:00:00Z",
  "id": "unique_message_id"
}
```

### Message Types

#### Time Updates
```json
{
  "type": "time_update",
  "data": {
    "current_time": {
      "year": 1024,
      "month": 3,
      "day": 15,
      "hour": 14,
      "minute": 30
    },
    "time_scale": 1.0,
    "is_paused": false
  }
}
```

#### Combat Updates
```json
{
  "type": "combat_update", 
  "data": {
    "combat_id": "combat_123",
    "event": "turn_change",
    "current_participant": "character_456",
    "updated_state": { /* CombatStateDTO */ }
  }
}
```

#### Character Updates
```json
{
  "type": "character_update",
  "data": {
    "character_id": "char_123",
    "changes": {
      "hit_points": 25,
      "experience_points": 1500,
      "level": 3
    }
  }
}
```

#### Quest Updates
```json
{
  "type": "quest_update",
  "data": {
    "quest_id": "quest_789",
    "status": "completed",
    "objectives_completed": ["objective_1", "objective_2"]
  }
}
```

#### Region Events
```json
{
  "type": "region_event",
  "data": {
    "region_id": "region_101",
    "event_type": "population_change",
    "details": {
      "new_population": 5420,
      "change": 50,
      "reason": "migration"
    }
  }
}
```

## Unity Client Integration Patterns

### HTTP Client Usage
```csharp
// Example service implementation
public class CharacterServiceClient : BaseHTTPClient
{
    protected override string GetClientName() => "CharacterService";
    
    public void CreateCharacter(CharacterCreateDTO character, Action<CharacterDTO> onSuccess, Action<string> onError)
    {
        StartCoroutine(PostRequestCoroutine("/characters", character, (success, response) =>
        {
            if (success)
            {
                var characterDto = SafeDeserialize<CharacterDTO>(response);
                onSuccess?.Invoke(characterDto);
            }
            else
            {
                onError?.Invoke(response);
            }
        }));
    }
}
```

### WebSocket Integration
```csharp
public class WebSocketManager : MonoBehaviour
{
    private WebSocket webSocket;
    
    // Event system for message routing
    public event Action<TimeUpdateDTO> OnTimeUpdate;
    public event Action<CombatUpdateDTO> OnCombatUpdate;
    public event Action<CharacterUpdateDTO> OnCharacterUpdate;
    
    private void HandleMessage(string message)
    {
        var webSocketMessage = JsonUtility.FromJson<WebSocketMessage>(message);
        
        switch (webSocketMessage.type)
        {
            case "time_update":
                var timeUpdate = JsonUtility.FromJson<TimeUpdateDTO>(webSocketMessage.data);
                OnTimeUpdate?.Invoke(timeUpdate);
                break;
                
            case "combat_update":
                var combatUpdate = JsonUtility.FromJson<CombatUpdateDTO>(webSocketMessage.data);
                OnCombatUpdate?.Invoke(combatUpdate);
                break;
                
            case "character_update":
                var characterUpdate = JsonUtility.FromJson<CharacterUpdateDTO>(webSocketMessage.data);
                OnCharacterUpdate?.Invoke(characterUpdate);
                break;
        }
    }
}
```

## Data Transfer Object Standards

### Serialization Attributes
All DTOs use consistent JSON serialization:
```csharp
[JsonPropertyName("snake_case_property")]
public string CamelCaseProperty { get; set; }
```

### Validation Attributes
```csharp
[Required]
[StringLength(100, MinimumLength = 1)]
[Range(-3, 5)]
[EmailAddress]
[Url]
```

### Common Base Types
```csharp
public class Vector2DTO
{
    [JsonPropertyName("x")]
    public float X { get; set; }
    
    [JsonPropertyName("y")]
    public float Y { get; set; }
}

public class Vector2IntDTO
{
    [JsonPropertyName("x")]
    public int X { get; set; }
    
    [JsonPropertyName("y")]
    public int Y { get; set; }
}

public class CoordinatesDTO
{
    [JsonPropertyName("latitude")]
    public double Latitude { get; set; }
    
    [JsonPropertyName("longitude")]
    public double Longitude { get; set; }
}
```

## Error Handling

### HTTP Error Responses
```json
{
  "detail": "Error message",
  "error_code": "CHARACTER_NOT_FOUND",
  "timestamp": "2025-01-29T12:00:00Z"
}
```

### HTTP Status Codes
- `200 OK` - Successful GET/PUT
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation errors
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Unity Error Handling
```csharp
protected void HandleErrorResponse(string response, Action<string> onError)
{
    try
    {
        var errorDto = JsonUtility.FromJson<ErrorResponseDTO>(response);
        onError?.Invoke(errorDto.Detail);
    }
    catch
    {
        onError?.Invoke("Unknown error occurred");
    }
}
```

## Performance Considerations

### Pagination
List endpoints support pagination:
```http
GET /characters?page=1&per_page=10
```

Response includes metadata:
```json
{
  "items": [ /* list of items */ ],
  "total": 150,
  "page": 1,
  "per_page": 10,
  "pages": 15
}
```

### Caching Headers
Responses include appropriate cache headers:
```http
Cache-Control: max-age=300
ETag: "abc123"
Last-Modified: Wed, 29 Jan 2025 12:00:00 GMT
```

### Rate Limiting
API includes rate limiting:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1643472000
```

## Development & Testing

### Mock Server
Unity includes mock server implementation for development and testing.

### API Documentation
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

### Health Checks
- Backend health: `GET /health`
- Service-specific health: `GET /{service}/health`

---

This API contract serves as the definitive specification for Unity-Backend communication in the Visual DM project. All client implementations should conform to these contracts to ensure proper integration and data consistency. 