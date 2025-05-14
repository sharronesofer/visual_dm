# Server-Side Validation Framework

This directory contains a comprehensive framework for validating user actions on the server side. It is designed to ensure that all data received from clients is properly validated before being processed or stored in the database.

## Features

- **Type Validation**: Validate that values are of the correct data type (string, number, boolean, etc.)
- **Constraint Validation**: Validate that values meet specific constraints (min/max length, min/max value, etc.)
- **Schema Validation**: Validate that objects conform to a specific schema
- **Rate Limiting**: Prevent abuse by limiting the number of requests per user
- **Transaction Support**: Ensure ACID properties for critical operations
- **Security Measures**: Prevent replay attacks and request tampering
- **Ownership Validation**: Ensure that users can only access their own resources
- **Common Action Validation**: Validate common game actions like movement, purchases, combat, etc.

## Core Components

- **validators.py**: Basic validators for different data types
- **middleware.py**: Middleware for validating requests
- **rate_limiter.py**: Rate limiting functionality
- **transaction.py**: Transaction management
- **security.py**: Security measures
- **helpers.py**: Helpers for validating common game actions

## Usage Examples

### Basic Validation

```python
from app.core.validation.validators import (
    StringValidator, NumberValidator, BooleanValidator,
    validate_request_data
)

# Define a validation schema
SCHEMA = {
    'name': StringValidator('name', min_length=3, max_length=50),
    'age': NumberValidator('age', min_value=0, is_integer=True),
    'is_active': BooleanValidator('is_active', required=False)
}

# Validate data
try:
    validate_request_data(SCHEMA, data)
except ValidationError as e:
    # Handle validation error
    return jsonify({
        'error': e.message,
        'details': e.details
    }), 400
```

### Middleware-Based Validation

```python
from app.core.validation.middleware import validate_json, validate_query_params

@app.route('/resources', methods=['POST'])
@validate_json({
    'name': StringValidator('name', min_length=3, max_length=50),
    'value': NumberValidator('value', min_value=0)
})
def create_resource():
    # Request data is guaranteed to be valid here
    data = g.validated_data
    # ...
```

### Rate Limiting

```python
from app.core.validation.rate_limiter import rate_limit

@app.route('/actions', methods=['POST'])
@rate_limit('action_create')
def create_action():
    # This endpoint is rate limited
    # ...
```

### Transaction Support

```python
from app.core.validation.transaction import transaction

@app.route('/critical-operation', methods=['POST'])
@transaction('critical_operation')
def critical_operation():
    # All database operations here are within a transaction
    # ...
```

### Security Measures

```python
from app.core.validation.security import require_signature

@app.route('/secure-endpoint', methods=['POST'])
@require_signature({'action', 'data'})
def secure_endpoint():
    # Request is guaranteed to have a valid signature
    # ...
```

### Comprehensive Validation Example

```python
@app.route('/players/<int:player_id>/movement', methods=['POST'])
@jwt_required()
@validate_json(MOVEMENT_VALIDATOR_SCHEMA)
@rate_limit('movement')
@transaction('player_movement')
def move_player(player_id):
    # This endpoint is protected, validated, rate limited, and transactional
    # ...
```

## Best Practices

1. **Use the Framework Consistently**: Apply validation to all endpoints that accept user input
2. **Validate Early**: Validate input as early as possible in the request lifecycle
3. **Be Specific**: Use specific validators rather than generic ones
4. **Provide Helpful Error Messages**: Ensure that error messages are clear and helpful
5. **Separate Validation Logic**: Keep validation logic separate from business logic
6. **Transaction Safety**: Use transactions for critical operations
7. **Rate Limit Appropriately**: Apply rate limits to all endpoints
8. **Security First**: Apply security measures to all sensitive endpoints

## Integration with Exception Handling

This validation framework integrates with the project's error handling system. When validation fails, specific exceptions are raised that are then caught by the error handling middleware and converted to appropriate HTTP responses.

## Maintenance and Extension

- Add new validators to `validators.py` as needed
- Add new middleware to `middleware.py` for specific validation scenarios
- Update rate limits in `rate_limiter.py` as required
- Add new security measures to `security.py` as needed 