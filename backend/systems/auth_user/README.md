# Auth User System

This system provides authentication and user management functionality for the application.

## Structure

The system is organized into the following directories:

- **models/**: Database models for users, roles, and permissions
- **services/**: Business logic for authentication, password management, and token handling
- **utils/**: Utility functions for validation and other common operations
- **repositories/**: Database access and operations (to be implemented)
- **schemas/**: Pydantic models for request/response validation (to be implemented)
- **routers/**: API endpoints and route handlers (to be implemented)

## Key Features

- JWT-based authentication
- Password hashing and verification
- User roles and permissions
- Input validation for user data

## Usage

To authenticate a user in FastAPI endpoints:

```python
from fastapi import Depends
from backend.systems.auth_user import get_current_active_user

@router.get("/protected-endpoint")
async def protected_endpoint(current_user = Depends(get_current_active_user)):
    return {"message": f"Hello, {current_user['email']}"}
```

### Authentication Flow

1. User credentials are validated
2. JWT tokens are issued upon successful authentication
3. Subsequent requests include the JWT token in the Authorization header
4. Protected endpoints use the `get_current_active_user` dependency

### User Model

The `User` model includes:
- Email and password hash
- Active status
- Relationships with roles
- Password reset capabilities

## Future Improvements

- Implement refresh tokens
- Add social authentication providers
- Add rate limiting for authentication attempts
- Implement proper encryption for sensitive data
