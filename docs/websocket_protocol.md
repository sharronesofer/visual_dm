# WebSocket Protocol Specification

## Overview
This document describes the canonical protocol for all WebSocket communications between the backend and frontend. It includes message format, endpoint details, versioning, and test coverage.

---

## WebSocket Endpoint

- **URL:** `/ws/metrics/stream`
- **Protocol:** FastAPI WebSocket
- **Purpose:** Real-time metrics streaming and message-based requests

### Example Connection (Python)
```python
import websockets
import asyncio
import json

async def main():
    uri = "ws://localhost:8000/ws/metrics/stream"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "type": "ping",
            "payload": {},
            "timestamp": "2024-01-01T00:00:00Z",
            "requestId": "1",
            "version": "1.0"
        }))
        response = await websocket.recv()
        print(response)

asyncio.run(main())
```

---

## Message Envelope

All messages must conform to the following structure:

| Field      | Type   | Required | Description                                 |
|------------|--------|----------|---------------------------------------------|
| type       | str    | Yes      | Message type (e.g., `ping`, `metrics_update`)|
| payload    | object | Yes      | Message payload (type-specific)             |
| timestamp  | str    | Yes      | ISO 8601 UTC timestamp                      |
| requestId  | str    | Yes      | Unique request identifier                   |
| version    | str    | Yes      | Protocol version (e.g., `1.0`)              |

### Example Message
```json
{
  "type": "metrics_update",
  "payload": {"value": 42},
  "timestamp": "2024-01-01T00:00:00Z",
  "requestId": "abc123",
  "version": "1.0"
}
```

---

## Error Handling

- All errors are returned as messages with `type: "error"` and a `message` field in the payload.
- Example:
```json
{
  "type": "error",
  "payload": {"message": "Invalid message format"},
  "timestamp": "2024-01-01T00:00:01Z",
  "requestId": "abc123",
  "version": "1.0"
}
```

---

## Test Coverage & Strategy

- **Unit Tests:**
  - Pydantic model validation and serialization (see `test_websocket_schema.py`)
  - WebSocket handler logic, error handling, and disconnects (see `test_websocket_service.py`)
- **Integration Tests:**
  - End-to-end WebSocket connection, valid/invalid message handling (see `test_websocket_endpoint.py`)
- **Coverage:**
  - All message types, error cases, and connection events are covered
  - Minimum 85% coverage for all WebSocket-related code
- **How to Run:**
  - `pytest --cov`

---

## Troubleshooting
- Ensure all messages conform to the envelope structure
- Check server logs for error messages
- Use provided test cases as reference for valid/invalid scenarios

---

## Extensibility
- Add new message types by extending the schema and handler logic
- Maintain backward compatibility by versioning the protocol

---

## See Also
- `Development_Bible.md` for architectural rationale and extension guidelines
- Backend test files for implementation details

## Message Envelope
All WebSocket messages MUST conform to the following envelope structure:

```json
{
  "version": "1.0",
  "type": "<string>",
  "payload": <object>,
  "timestamp": "<ISO8601 UTC string>",
  "requestId": "<string, optional>"
}
```

- `version` (string): Protocol version. Required. Allows for future breaking changes.
- `type` (string): Message type identifier (e.g., "metrics_update", "auth_request", "error"). Required.
- `payload` (object): Message-specific data. Required. Structure depends on `type`.
- `timestamp` (string): ISO8601 UTC timestamp of message creation. Required.
- `requestId` (string): Optional. Used to correlate requests and responses, especially for RPC or error handling.

## Canonical Message Types
- `metrics_update`: Real-time metrics data stream
- `auth_request`: Client authentication request
- `auth_response`: Server authentication response
- `error`: Error message
- `heartbeat`: Keep-alive ping/pong
- `ai_message`: Message from AI backend (e.g., gpt_rumor_server)
- `custom`: For future extensibility

### Example: Metrics Update
```json
{
  "version": "1.0",
  "type": "metrics_update",
  "payload": {
    "metricName": "active_users",
    "value": 1234
  },
  "timestamp": "2024-06-01T12:00:00Z"
}
```

### Example: Error
```json
{
  "version": "1.0",
  "type": "error",
  "payload": {
    "code": 401,
    "message": "Unauthorized: Invalid token."
  },
  "timestamp": "2024-06-01T12:00:01Z",
  "requestId": "abc-123"
}
```

## Versioning
- The `version` field MUST be present in every message.
- Breaking changes require incrementing the major version.
- Clients and servers MUST reject messages with unsupported versions.

## Extensibility
- New message types MUST be documented here and implemented in both backend and frontend type definitions.
- The `payload` object MAY contain nested objects, arrays, or primitives as required by the message type.
- Unknown message types SHOULD be logged and ignored, not cause connection termination.

## Error Handling
- All error messages MUST use the `error` type and include a `code` and `message` in the payload.
- Errors related to a specific request MUST include the `requestId`.

## Security
- All authentication messages MUST use the `auth_request` and `auth_response` types.
- Sensitive data MUST NOT be sent in plaintext; use secure tokens and HTTPS/WSS.

## Implementation Notes
- All timestamps MUST be in UTC and ISO8601 format.
- All field names are lowerCamelCase.
- All messages MUST be valid UTF-8 JSON.

## References
- [RFC 6455: The WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [ISO 8601 Date and Time Format](https://en.wikipedia.org/wiki/ISO_8601)
- [OWASP WebSocket Security](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html) 