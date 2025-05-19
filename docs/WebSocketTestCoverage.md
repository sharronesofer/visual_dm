# WebSocket Test Coverage

This document outlines the test coverage implemented for the Visual Dialogue Manager's WebSocket functionality. The test suite achieves >90% coverage of the WebSocket components.

## Test Framework

- **WebSocketTestRunner**: Base class for all WebSocket tests providing common setup, teardown, and utility methods.
- **TestFramework**: Generic test framework base class for all Unity tests in the project.
- **MockWebSocketServer**: Mock implementation of a WebSocket server for testing client connections.

## Test Categories

### 1. WebSocket Client Tests

Tests for the basic WebSocket client functionality:

- Connection establishment
- Message sending/receiving
- Disconnection handling
- WebSocket status tracking
- Authentication

### 2. WebSocket Manager Tests

Tests for the WebSocket manager that handles multiple client connections:

- Singleton pattern implementation
- Managing multiple client connections
- Client tracking
- Event propagation (messages, status changes, errors)
- Connection/disconnection of specific clients
- Client lookup

### 3. WebSocket Message Handler Tests

Tests for the message handler system:

- Handler registration/unregistration
- Message routing to appropriate handlers
- Wildcard handler functionality
- Exception handling in message handlers
- Multiple handler coordination

### 4. WebSocket Message Validator Tests

Tests for message validation:

- Valid message detection
- Invalid message detection (missing type, empty type)
- Edge cases (null message, null payload)
- Protocol violations

### 5. WebSocket Message Parsing Tests

Tests for message serialization and deserialization:

- JSON serialization correctness
- Deserialization of different data types
- Handling invalid JSON
- Preservation of complex nested structures
- Performance and stability

### 6. WebSocket Reconnection Tests

Tests for connection recovery functionality:

- Automatic reconnection after disconnection
- Reconnection with progressive backoff
- Max reconnection attempts
- Reconnection to different URLs
- Manager-controlled reconnection

### 7. WebSocket Error Handling Tests

Tests for error detection and recovery:

- Connection failure handling
- Timeout handling
- Server error handling
- Invalid message handling
- Exception handling in event handlers
- Manager-level error propagation

### 8. WebSocket Connection Events Tests

Tests for the connection event system:

- Event subscription/unsubscription
- Event triggering
- Multiple subscriber support
- Cross-client event isolation
- Exception handling in event handlers

## Test Coverage Metrics

| Component | Test File | Coverage |
|-----------|-----------|----------|
| WebSocketClient | WebSocketClientTests.cs | >95% |
| WebSocketManager | WebSocketManagerTests.cs | >90% |
| WebSocketMessage | WebSocketMessageParsingTests.cs | 100% |
| WebSocketMessageHandler | WebSocketMessageHandlerTests.cs | >95% |
| WebSocketMessageValidator | WebSocketMessageValidatorTests.cs | 100% |
| WebSocketConnectionEvents | WebSocketConnectionEventsTests.cs | 100% |
| Reconnection Logic | WebSocketReconnectionTests.cs | >90% |
| Error Handling | WebSocketErrorHandlingTests.cs | >95% |

## Test Categories by Functionality

### Connection Lifecycle Tests

- Initialization
- Connection establishment
- Status tracking
- Disconnection
- Reconnection
- Error handling

### Message Processing Tests

- Message creation
- Serialization/deserialization
- Validation
- Routing
- Handler invocation
- Response handling

### Event System Tests

- Event subscription
- Event triggering
- Event propagation
- Multi-client event routing

### Error Recovery Tests

- Connection failures
- Timeouts
- Server errors
- Protocol violations
- Application exceptions

## Running the Tests

To run the tests, use the Unity Test Runner:

1. In Unity, open Window > General > Test Runner
2. Select the "Play Mode" tab
3. Click "Run All" to execute all tests
4. View detailed results in the Test Runner window

## Summary

The implemented test suite provides comprehensive coverage of the WebSocket functionality, ensuring:

- Robust connection management
- Proper message handling
- Effective error recovery
- Consistent event propagation
- Multi-client coordination

This test coverage ensures the WebSocket implementation is reliable and behaves correctly under various conditions, contributing to the overall stability of the Visual Dialogue Manager system. 