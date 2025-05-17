# Visual DM RESTful API Endpoints

This document outlines the RESTful API endpoints for the Visual DM application. All endpoints follow RESTful principles and use consistent response formats.

## Base URL Structure

```
/api/v1/[resource]
```

## Authentication

Authentication is required for most endpoints using JWT Bearer tokens:

```
Authorization: Bearer <token>
```

## Response Format

All responses follow a standardized format:

**Success Response:**
```json
{
  "data": <response_data>,
  "meta": {}
}
```

**Error Response:**
```json
{
  "error": "ErrorType",
  "error_code": "error_code",
  "message": "Human-readable error message",
  "details": [
    {
      "field": "field_name",
      "message": "Specific error for this field"
    }
  ]
}
```

## Pagination

List endpoints support pagination with the following query parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

Paginated responses include pagination metadata:
```json
{
  "data": {
    "items": [...],
    "total": 42,
    "page": 1,
    "page_size": 20,
    "next_page": "/api/v1/resource?page=2&page_size=20",
    "prev_page": null
  },
  "meta": {}
}
```

## Filtering and Sorting

List endpoints support:
- `q`: General search query
- `sort`: Field to sort by (prefix with `-` for descending order)
- `fields`: Comma-separated list of fields to include
- `expand`: Comma-separated list of relations to expand

## HTTP Methods

The API follows standard HTTP method semantics:
- `GET`: Retrieve resources
- `POST`: Create resources
- `PUT`: Replace resources
- `PATCH`: Partially update resources
- `DELETE`: Remove resources

## API Endpoints

### Characters

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/characters` | List all characters |
| GET | `/api/v1/characters/{id}` | Get a specific character |
| POST | `/api/v1/characters` | Create a new character |
| PUT | `/api/v1/characters/{id}` | Update a character |
| PATCH | `/api/v1/characters/{id}` | Partially update a character |
| DELETE | `/api/v1/characters/{id}` | Delete a character |

### Campaigns

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/campaigns` | List all campaigns |
| GET | `/api/v1/campaigns/{id}` | Get a specific campaign |
| POST | `/api/v1/campaigns` | Create a new campaign |
| PUT | `/api/v1/campaigns/{id}` | Update a campaign |
| PATCH | `/api/v1/campaigns/{id}` | Partially update a campaign |
| DELETE | `/api/v1/campaigns/{id}` | Delete a campaign |
| GET | `/api/v1/campaigns/{id}/sessions` | List all sessions for a campaign |
| POST | `/api/v1/campaigns/{id}/sessions` | Create a new session for a campaign |

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/sessions` | List all sessions |
| GET | `/api/v1/sessions/{id}` | Get a specific session |
| PUT | `/api/v1/sessions/{id}` | Update a session |
| PATCH | `/api/v1/sessions/{id}` | Partially update a session |
| DELETE | `/api/v1/sessions/{id}` | Delete a session |

### Combat

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/combats` | List all combats |
| GET | `/api/v1/combats/{id}` | Get a specific combat |
| POST | `/api/v1/combats` | Create a new combat |
| PUT | `/api/v1/combats/{id}` | Update a combat |
| PATCH | `/api/v1/combats/{id}` | Partially update a combat |
| DELETE | `/api/v1/combats/{id}` | Delete a combat |
| GET | `/api/v1/combats/{id}/participants` | List all participants in a combat |
| POST | `/api/v1/combats/{id}/participants` | Add a participant to a combat |
| POST | `/api/v1/combats/{id}/start` | Start a combat |
| POST | `/api/v1/combats/{id}/end` | End a combat |
| POST | `/api/v1/combats/{id}/next` | Move to next turn |

### NPCs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/npcs` | List all NPCs |
| GET | `/api/v1/npcs/{id}` | Get a specific NPC |
| POST | `/api/v1/npcs` | Create a new NPC |
| PUT | `/api/v1/npcs/{id}` | Update an NPC |
| PATCH | `/api/v1/npcs/{id}` | Partially update an NPC |
| DELETE | `/api/v1/npcs/{id}` | Delete an NPC |

### Monsters

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/monsters` | List all monsters |
| GET | `/api/v1/monsters/{id}` | Get a specific monster |
| POST | `/api/v1/monsters` | Create a new monster |
| PUT | `/api/v1/monsters/{id}` | Update a monster |
| PATCH | `/api/v1/monsters/{id}` | Partially update a monster |
| DELETE | `/api/v1/monsters/{id}` | Delete a monster |

### Maps

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/maps` | List all maps |
| GET | `/api/v1/maps/{id}` | Get a specific map |
| POST | `/api/v1/maps` | Create a new map |
| PUT | `/api/v1/maps/{id}` | Update a map |
| PATCH | `/api/v1/maps/{id}` | Partially update a map |
| DELETE | `/api/v1/maps/{id}` | Delete a map |
| GET | `/api/v1/maps/{id}/tokens` | List all tokens on a map |
| POST | `/api/v1/maps/{id}/tokens` | Add a token to a map |

### Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/items` | List all items |
| GET | `/api/v1/items/{id}` | Get a specific item |
| POST | `/api/v1/items` | Create a new item |
| PUT | `/api/v1/items/{id}` | Update an item |
| PATCH | `/api/v1/items/{id}` | Partially update an item |
| DELETE | `/api/v1/items/{id}` | Delete an item |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user profile |
| PATCH | `/api/v1/users/me` | Update current user profile |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login with username/password |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/logout` | Logout (invalidate current token) |

## Status Codes

The API uses standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error 