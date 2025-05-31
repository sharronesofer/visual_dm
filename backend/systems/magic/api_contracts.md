# Magic System API Contracts

This document defines the API contracts for the Magic System, ensuring compatibility with Unity frontend integration.

## Authentication
All endpoints require valid authentication tokens in the Authorization header.

## Base URL
```
/api/v1/magic
```

## Endpoints

### 1. Get Spells
**GET** `/spells`

Query Parameters:
- `school` (optional): Filter by magic school
- `level` (optional): Filter by spell level

Response:
```json
[
  {
    "id": "uuid",
    "name": "string",
    "school": "string",
    "level": "integer",
    "casting_time": "string",
    "range": "string", 
    "components": ["string"],
    "duration": "string",
    "description": "string",
    "higher_levels": "string|null",
    "material_components": "string|null",
    "ritual": "boolean",
    "concentration": "boolean",
    "damage_type": "string|null",
    "save_type": "string|null"
  }
]
```

### 2. Get Specific Spell
**GET** `/spells/{spell_id}`

Response: Same as individual spell object above

### 3. Get Character Spellbook
**GET** `/spellbook/{character_id}`

Response:
```json
{
  "id": "uuid",
  "character_id": "uuid", 
  "name": "string",
  "description": "string|null",
  "known_spells": [/* spell objects */],
  "prepared_spells": [/* spell objects */]
}
```

### 4. Prepare Daily Spells
**POST** `/spellbook/{character_id}/prepare`

Request Body:
```json
{
  "spell_ids": ["uuid"]
}
```

Response:
```json
{
  "message": "string",
  "prepared_count": "integer"
}
```

### 5. Cast Spell
**POST** `/spells/cast`

Request Body:
```json
{
  "spell_id": "uuid",
  "target_id": "uuid|null",
  "spell_level": "integer|null",
  "metadata": {}
}
```

Response:
```json
{
  "message": "string",
  "effect_id": "uuid|null",
  "expires_at": "string|null"
}
```

### 6. Get Spell Slots
**GET** `/spell-slots/{character_id}`

Response:
```json
[
  {
    "level": "integer",
    "total_slots": "integer", 
    "used_slots": "integer",
    "remaining_slots": "integer"
  }
]
```

### 7. Long Rest (Restore Spell Slots)
**POST** `/spell-slots/{character_id}/rest`

Response:
```json
{
  "message": "string"
}
```

### 8. Get Active Effects
**GET** `/effects/active/{character_id}`

Response:
```json
[
  {
    "id": "uuid",
    "spell_name": "string",
    "cast_at": "string",
    "expires_at": "string|null",
    "concentration": "boolean",
    "effect_data": {}
  }
]
```

### 9. Dispel Effect
**DELETE** `/effects/{effect_id}`

Response:
```json
{
  "message": "string"
}
```

## WebSocket Events

### Connection
```
ws://localhost:8000/ws/magic/{character_id}
```

### Events Sent to Client
```json
{
  "type": "spell_cast",
  "data": {
    "spell_name": "string",
    "caster_id": "uuid",
    "target_id": "uuid|null",
    "effect_id": "uuid"
  }
}
```

```json
{
  "type": "effect_expired", 
  "data": {
    "effect_id": "uuid",
    "spell_name": "string"
  }
}
```

```json
{
  "type": "spell_slots_updated",
  "data": {
    "character_id": "uuid",
    "level": "integer",
    "remaining_slots": "integer"
  }
}
```

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "detail": "string"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string", 
      "type": "string"
    }
  ]
}
```

## Unity Integration Notes

1. All UUIDs should be converted to strings for Unity compatibility
2. DateTime fields are in ISO 8601 format
3. WebSocket connection should be established on character login
4. Spell casting should trigger immediate WebSocket notifications
5. Effect expiration should be handled via WebSocket events
6. Spell slot updates should sync in real-time via WebSocket
