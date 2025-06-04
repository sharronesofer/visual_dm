# Quest System API Documentation

## Overview

The Quest System API provides endpoints for managing quests in the game world. This documentation reflects the current business logic alignment with corrected enum values and standardized field names.

**Base URL:** `/api/v1/quests`

**API Version:** 1.0.0  
**Last Updated:** 2025-01-16

---

## Data Models

### Quest Object

```json
{
  "id": "uuid",
  "title": "string",
  "description": "string", 
  "status": "pending|active|completed|failed|abandoned|expired",
  "difficulty": "easy|medium|hard|epic",
  "theme": "combat|exploration|social|mystery|crafting|trade|aid|knowledge|general",
  "npc_id": "uuid|null",
  "player_id": "uuid|null", 
  "location_id": "uuid|null",
  "level": "integer (1-100)",
  "steps": [QuestStep],
  "rewards": QuestReward,
  "is_main_quest": "boolean",
  "tags": ["string"],
  "properties": "object",
  "created_at": "datetime",
  "updated_at": "datetime|null",
  "expires_at": "datetime|null"
}
```

### Quest Step Object

```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "required": "boolean", 
  "order": "integer",
  "metadata": "object"
}
```

### Quest Reward Object

```json
{
  "gold": "integer (>= 0)",
  "experience": "integer (>= 0)",
  "reputation": "object",
  "items": [
    {
      "item_id": "uuid",
      "quantity": "integer"
    }
  ],
  "special": "object"
}
```

---

## Enum Values

### Quest Status

| Value | Description |
|-------|-------------|
| `pending` | Quest is available but not yet started |
| `active` | Quest is currently in progress |
| `completed` | Quest has been successfully finished |
| `failed` | Quest ended in failure |
| `abandoned` | Quest was abandoned by player |
| `expired` | Quest exceeded its time limit |

**Status Flow:**
- `pending` → `active`, `abandoned`
- `active` → `completed`, `failed`, `abandoned`, `expired`
- `completed` → (terminal state)
- `failed` → `pending` (can be retried)
- `abandoned` → `pending` (can be retried)
- `expired` → `pending` (can be retried)

### Quest Difficulty

| Value | Description | Level Range | Rewards Multiplier |
|-------|-------------|-------------|-------------------|
| `easy` | Simple tasks for beginners | 1-10 | 1.0x |
| `medium` | Standard difficulty quests | 5-20 | 1.5x |
| `hard` | Challenging quests | 15-40 | 2.0x |
| `epic` | End-game content | 30-100 | 3.0x |

### Quest Theme

| Value | Description | Typical Objectives |
|-------|-------------|-------------------|
| `combat` | Battle-focused quests | Eliminate enemies, survive encounters |
| `exploration` | Discovery and mapping | Visit locations, find secrets |
| `social` | Relationship and dialogue | Talk to NPCs, build relationships |
| `mystery` | Investigation and puzzles | Gather clues, solve puzzles |
| `crafting` | Creation and building | Create items, gather materials |
| `trade` | Commerce and economy | Buy/sell items, negotiate |
| `aid` | Helping others | Assist NPCs, deliver items |
| `knowledge` | Learning and research | Research topics, learn skills |
| `general` | Multi-purpose or misc | Complete tasks, reach goals |

---

## API Endpoints

### Create Quest

**POST** `/quests`

Creates a new quest in the system.

**Request Body:**
```json
{
  "title": "Find the Lost Artifact",
  "description": "A mysterious artifact has gone missing from the temple",
  "difficulty": "medium",
  "theme": "mystery",
  "npc_id": "550e8400-e29b-41d4-a716-446655440000",
  "location_id": "550e8400-e29b-41d4-a716-446655440001",
  "level": 5,
  "steps": [
    {
      "id": 1,
      "description": "Investigate the temple",
      "type": "investigate",
      "completed": false,
      "target_location_id": "550e8400-e29b-41d4-a716-446655440001",
      "data": {}
    }
  ],
  "rewards": {
    "gold": 150,
    "experience": 300,
    "reputation": {},
    "items": []
  },
  "is_main_quest": false,
  "tags": ["mystery", "temple"]
}
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Find the Lost Artifact",
  "description": "A mysterious artifact has gone missing from the temple",
  "status": "pending",
  "difficulty": "medium",
  "theme": "mystery",
  "npc_id": "550e8400-e29b-41d4-a716-446655440000",
  "player_id": null,
  "location_id": "550e8400-e29b-41d4-a716-446655440001",
  "level": 5,
  "steps": [...],
  "rewards": {...},
  "is_main_quest": false,
  "tags": ["mystery", "temple"],
  "properties": {},
  "created_at": "2025-01-16T12:00:00Z",
  "updated_at": null,
  "expires_at": null
}
```

### List Quests

**GET** `/quests`

Retrieves a paginated list of quests with optional filtering.

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `size` (integer, default: 50): Page size
- `status` (string): Filter by quest status
- `difficulty` (string): Filter by difficulty level
- `theme` (string): Filter by quest theme
- `npc_id` (uuid): Filter by associated NPC
- `player_id` (uuid): Filter by assigned player
- `search` (string): Search in title and description

**Example:** `GET /quests?status=pending&difficulty=medium&page=1&size=20`

**Response:** `200 OK`
```json
{
  "items": [Quest, ...],
  "total": 45,
  "page": 1,
  "size": 20,
  "has_next": true,
  "has_prev": false
}
```

### Get Quest by ID

**GET** `/quests/{quest_id}`

Retrieves detailed information for a specific quest.

**Path Parameters:**
- `quest_id` (uuid): Quest identifier

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Find the Lost Artifact",
  "status": "active",
  "difficulty": "medium",
  "theme": "mystery",
  // ... full quest object
}
```

### Update Quest

**PATCH** `/quests/{quest_id}`

Updates specific fields of an existing quest.

**Path Parameters:**
- `quest_id` (uuid): Quest identifier

**Request Body:**
```json
{
  "status": "active",
  "difficulty": "hard",
  "description": "Updated description"
}
```

**Response:** `200 OK` - Returns updated quest object

### Quest Actions

**POST** `/quests/actions`

Performs actions on quests (accept, abandon, complete, etc.).

**Request Body:**
```json
{
  "quest_id": "123e4567-e89b-12d3-a456-426614174000",
  "player_id": "550e8400-e29b-41d4-a716-446655440002",
  "action": "accept",
  "reason": "optional reason for action"
}
```

**Valid Actions:**
- `accept`: Accept a pending quest (changes status to `active`)
- `abandon`: Abandon an active quest (changes status to `abandoned`)
- `complete`: Mark quest as completed (changes status to `completed`)
- `fail`: Mark quest as failed (changes status to `failed`)

**Response:** `200 OK` - Returns updated quest object

### Update Quest Step

**POST** `/quests/steps/update`

Updates the completion status of a quest step.

**Request Body:**
```json
{
  "quest_id": "123e4567-e89b-12d3-a456-426614174000",
  "step_id": 1,
  "completed": true,
  "player_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Response:** `200 OK` - Returns updated quest object

### Quest Statistics

**GET** `/quests/statistics`

Retrieves quest system statistics.

**Response:** `200 OK`
```json
{
  "total_quests": 150,
  "by_status": {
    "pending": 45,
    "active": 67,
    "completed": 32,
    "failed": 4,
    "abandoned": 2,
    "expired": 0
  },
  "by_difficulty": {
    "easy": 40,
    "medium": 65,
    "hard": 35,
    "epic": 10
  },
  "by_theme": {
    "combat": 25,
    "exploration": 30,
    "mystery": 20,
    "social": 15,
    "crafting": 12,
    "trade": 8,
    "aid": 18,
    "knowledge": 10,
    "general": 12
  }
}
```

### Delete Quest

**DELETE** `/quests/{quest_id}`

Permanently removes a quest from the system.

**Path Parameters:**
- `quest_id` (uuid): Quest identifier

**Response:** `204 No Content`

---

## Error Responses

### Validation Errors

**422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["body", "difficulty"],
      "msg": "Difficulty must be one of: ['easy', 'medium', 'hard', 'epic']",
      "type": "value_error"
    }
  ]
}
```

### Not Found

**404 Not Found**
```json
{
  "detail": "Quest not found"
}
```

### Server Error

**500 Internal Server Error**
```json
{
  "detail": "Internal server error"
}
```

---

## Migration Notes

### Breaking Changes (v1.0.0)

1. **Enum Value Updates:**
   - Status values changed from `['available', 'offered', 'in-progress', ...]` to `['pending', 'active', 'completed', 'failed', 'abandoned', 'expired']`
   - Theme values: removed `'gathering'`, added `'general'`

2. **Field Name Changes:**
   - `giver_id` → `npc_id`
   - `quest_status` → `status`
   - `experience_points` → `experience`

3. **Step Structure Changes:**
   - `step_number` → `id`
   - `step_type` → removed (now in metadata)
   - Added `title`, `required`, `order` fields

### Backward Compatibility

Legacy field names are preserved in the `properties` field for existing data:
```json
{
  "properties": {
    "legacy_quest_type": "SIDE",
    "legacy_requirements": {...},
    "migration_date": "2025-01-16T12:00:00Z"
  }
}
```

---

## Configuration

Quest system behavior is configured via JSON files in `/data/systems/quest/`:

- `quest_config.json`: Core system configuration
- `quest_templates.json`: Quest generation templates  
- `quest_schema.json`: JSON schema validation

See individual files for detailed configuration options.

---

## Rate Limits

- Quest creation: 10 requests/minute per user
- Quest updates: 30 requests/minute per user
- Quest listing: 100 requests/minute per user

---

## Authentication

All endpoints require valid authentication. Include the bearer token in the Authorization header:

```
Authorization: Bearer your-jwt-token-here
```

---

## Examples

### Complete Quest Workflow

1. **Create Quest:**
   ```bash
   POST /quests
   {
     "title": "Rescue the Villagers",
     "difficulty": "medium",
     "theme": "aid"
   }
   ```

2. **Accept Quest:**
   ```bash
   POST /quests/actions
   {
     "quest_id": "...",
     "player_id": "...",
     "action": "accept"
   }
   ```

3. **Complete Steps:**
   ```bash
   POST /quests/steps/update
   {
     "quest_id": "...",
     "step_id": 1,
     "completed": true
   }
   ```

4. **Complete Quest:**
   ```bash
   POST /quests/actions
   {
     "quest_id": "...",
     "action": "complete"
   }
   ```

### Filtering Examples

- Get pending combat quests: `GET /quests?status=pending&theme=combat`
- Get player's active quests: `GET /quests?player_id=xxx&status=active`
- Search for artifact quests: `GET /quests?search=artifact`

---

For additional support or questions, please refer to the [Development Bible](../Development_Bible.md) or contact the development team. 