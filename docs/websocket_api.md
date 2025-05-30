# Visual DM WebSocket API Documentation

This document describes the standardized WebSocket API for the Visual DM system, which enables real-time communication between the Unity client and the FastAPI backend.

## Table of Contents

1. [Overview](#overview)
2. [Connection](#connection)
3. [Message Format](#message-format)
4. [Authentication](#authentication)
5. [Subscriptions](#subscriptions)
6. [Heartbeat](#heartbeat)
7. [Request-Response Pattern](#request-response-pattern)
8. [Events](#events)
9. [Error Handling](#error-handling)
10. [Message Types Reference](#message-types-reference)
11. [Examples](#examples)

## Overview

The Visual DM WebSocket API provides a standardized way for clients to communicate with the server in real-time. It supports:

- Authentication
- Subscriptions to specific topics
- Real-time events
- Request-response interactions
- Heartbeat monitoring
- Error handling

All communication follows a standardized message format to ensure consistency and reliability.

## Connection

### Endpoint

The WebSocket API is accessible at the following endpoint:

```
ws://{server_address}/ws/v1/ws
```

For secure connections (recommended for production):

```
wss://{server_address}/ws/v1/ws
```

### Query Parameters

The WebSocket connection accepts the following optional query parameters:

- `client_id`: A unique identifier for the client
- `client_type`: Type of client (e.g., "player", "admin", "observer")
- `version`: Protocol version (default: "1.0")

Example connection URL:

```
ws://localhost:8000/ws/v1/ws?client_id=player123&client_type=player&version=1.0
```

## Message Format

All messages follow a standardized envelope format with the following structure:

```json
{
  "type": "string",          // Message type identifier
  "message_id": "string",    // Unique message ID (UUID)
  "timestamp": "string",     // ISO8601 UTC timestamp
  "payload": {},             // Message-specific data
  // Additional fields based on message type
}
```

### Common Message Types

- `request`: Client requests to the server
- `response`: Server responses to client requests
- `event`: Server-initiated events
- `subscribe`/`unsubscribe`: Subscription management
- `auth`: Authentication messages
- `ping`/`pong`: Heartbeat messages

## Authentication

Authentication is required for most operations. The client must authenticate after establishing the WebSocket connection.

### Authentication Flow

1. Client connects to the WebSocket endpoint
2. Server sends a `connection_established` message
3. Client sends an `auth` message with credentials
4. Server responds with success/failure
5. If successful, the connection is now authenticated

### Authentication Message

```json
{
  "type": "auth",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:56Z",
  "payload": {
    "token": "jwt_token_here",
    // OR
    "player_id": "player_123"
  }
}
```

### Authentication Response

```json
{
  "type": "response",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:57Z",
  "correlation_id": "original_message_id",
  "success": true,
  "payload": {
    "session_id": "session_uuid"
  }
}
```

## Subscriptions

Clients can subscribe to specific topics to receive events related to those topics.

### Subscription Message

```json
{
  "type": "subscribe",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:56Z",
  "topics": ["game_events", "chat:global"]
}
```

### Unsubscription Message

```json
{
  "type": "unsubscribe",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:56Z",
  "topics": ["chat:global"]
}
```

### Subscription Response

```json
{
  "type": "response",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:57Z",
  "correlation_id": "original_message_id",
  "success": true,
  "payload": {
    "topics": ["game_events", "chat:global"],
    "action": "subscribe"
  }
}
```

### Common Topics

- `game_events`: General game events
- `chat:global`: Global chat messages
- `chat:private:{user_id}`: Private chat messages
- `map_updates`: Map-related updates
- `player_updates`: Player-related updates
- `npc_updates`: NPC-related updates

## Heartbeat

Heartbeat messages ensure the connection remains active and detect disconnections.

### Ping (Client → Server)

```json
{
  "type": "ping",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:56Z",
  "payload": {
    "client_time": "2023-08-01T12:34:56Z"
  }
}
```

### Pong (Server → Client)

```json
{
  "type": "pong",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:57Z",
  "correlation_id": "ping_message_id",
  "payload": {
    "server_time": "2023-08-01T12:34:57Z"
  }
}
```

## Request-Response Pattern

For operations requiring a response, use the request-response pattern.

### Request (Client → Server)

```json
{
  "type": "get_game_state",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:56Z",
  "payload": {
    "game_id": "game_123"
  },
  "requires_response": true
}
```

### Response (Server → Client)

```json
{
  "type": "response",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:57Z",
  "correlation_id": "request_message_id",
  "success": true,
  "payload": {
    "game_id": "game_123",
    "state": "active",
    "turn": 5,
    "active_player": "player_1"
  }
}
```

## Events

Events are server-initiated messages that notify clients about changes or occurrences.

### Event Message

```json
{
  "type": "event",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:56Z",
  "event_id": "event_uuid",
  "category": "npc_action",
  "payload": {
    "entity_id": "npc_123",
    "action": "move",
    "position": {"x": 10, "y": 0, "z": 5}
  }
}
```

### Common Event Categories

- `game_state`: Game state changes
- `player_action`: Player action events
- `npc_action`: NPC action events
- `map_update`: Map update events
- `chat`: Chat message events
- `system`: System-level events

## Error Handling

Errors are communicated through response messages with `success: false`.

### Error Response

```json
{
  "type": "response",
  "message_id": "uuid",
  "timestamp": "2023-08-01T12:34:57Z",
  "correlation_id": "request_message_id",
  "success": false,
  "error": "Error message describing the issue",
  "payload": {}
}
```

### Common Error Types

- Authentication failures
- Invalid message format
- Missing required fields
- Operation-specific errors
- Resource not found
- Permission denied

## Message Types Reference

### Core Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| `auth` | Client → Server | Authentication request |
| `response` | Server → Client | Response to a request |
| `event` | Server → Client | Server-initiated event notification |
| `subscribe` | Client → Server | Subscribe to topics |
| `unsubscribe` | Client → Server | Unsubscribe from topics |
| `ping` | Client → Server | Heartbeat request |
| `pong` | Server → Client | Heartbeat response |
| `error` | Server → Client | Error notification |

### Game-Specific Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| `get_game_state` | Client → Server | Request game state |
| `update_game_state` | Client → Server | Update game state |
| `get_player_info` | Client → Server | Request player information |
| `update_player` | Client → Server | Update player information |
| `game_action` | Client → Server | Perform a game action |
| `player_action` | Client → Server | Perform a player action |
| `get_map` | Client → Server | Request map data |
| `update_map` | Client → Server | Update map data |
| `chat_message` | Client → Server | Send a chat message |

## Examples

### Complete Authentication Flow

1. **Client connects to WebSocket endpoint**

2. **Server sends connection established message**
   ```json
   {
     "type": "connection_established",
     "message_id": "srv-123456",
     "timestamp": "2023-08-01T12:34:56Z",
     "payload": {
       "connection_id": "conn-123456",
       "server_time": "2023-08-01T12:34:56Z",
       "features": ["authentication", "subscriptions", "heartbeats", "events", "request-response"]
     }
   }
   ```

3. **Client sends authentication request**
   ```json
   {
     "type": "auth",
     "message_id": "client-123456",
     "timestamp": "2023-08-01T12:34:57Z",
     "payload": {
       "token": "valid_token_123456"
     }
   }
   ```

4. **Server responds with authentication result**
   ```json
   {
     "type": "response",
     "message_id": "srv-123457",
     "timestamp": "2023-08-01T12:34:58Z",
     "correlation_id": "client-123456",
     "success": true,
     "payload": {
       "session_id": "session-123456"
     }
   }
   ```

### Subscription and Event Flow

1. **Client subscribes to topics**
   ```json
   {
     "type": "subscribe",
     "message_id": "client-123457",
     "timestamp": "2023-08-01T12:35:00Z",
     "topics": ["game_events", "chat:global"]
   }
   ```

2. **Server confirms subscription**
   ```json
   {
     "type": "response",
     "message_id": "srv-123458",
     "timestamp": "2023-08-01T12:35:01Z",
     "correlation_id": "client-123457",
     "success": true,
     "payload": {
       "topics": ["game_events", "chat:global"],
       "action": "subscribe"
     }
   }
   ```

3. **Server sends an event on a subscribed topic**
   ```json
   {
     "type": "event",
     "message_id": "srv-123459",
     "timestamp": "2023-08-01T12:36:00Z",
     "event_id": "evt-123456",
     "category": "chat",
     "payload": {
       "channel": "global",
       "content": "Hello everyone!",
       "sender": "player_456",
       "sender_type": "player"
     }
   }
   ```

### Request-Response Example

1. **Client requests game state**
   ```json
   {
     "type": "get_game_state",
     "message_id": "client-123458",
     "timestamp": "2023-08-01T12:37:00Z",
     "payload": {
       "game_id": "game_123"
     }
   }
   ```

2. **Server responds with game state**
   ```json
   {
     "type": "response",
     "message_id": "srv-123460",
     "timestamp": "2023-08-01T12:37:01Z",
     "correlation_id": "client-123458",
     "success": true,
     "payload": {
       "game_id": "game_123",
       "state": "active",
       "turn": 5,
       "active_player": "player_1",
       "timestamp": "2023-08-01T12:37:01Z"
     }
   }
   ```

### Error Example

1. **Client sends invalid request**
   ```json
   {
     "type": "invalid_operation",
     "message_id": "client-123459",
     "timestamp": "2023-08-01T12:38:00Z",
     "payload": {}
   }
   ```

2. **Server responds with error**
   ```json
   {
     "type": "response",
     "message_id": "srv-123461",
     "timestamp": "2023-08-01T12:38:01Z",
     "correlation_id": "client-123459",
     "success": false,
     "error": "Unsupported message type: invalid_operation",
     "payload": {}
   }
   ```

## WebSocket Client Implementation in Unity

For Unity clients, implement the WebSocketManager component to handle connections, message serialization/deserialization, authentication, subscriptions, and reconnection logic.

Key features of the Unity implementation:

- Automatic reconnection with exponential backoff
- Message queue for handling offline operations
- Event-based architecture for easy integration
- Typed callbacks for different message types
- Subscription management
- Authentication state management

See the `WebSocketManager.cs` in the Unity project for implementation details. 