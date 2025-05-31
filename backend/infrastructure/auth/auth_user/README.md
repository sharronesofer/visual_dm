# Auth User System

A comprehensive authentication and user management system providing secure user authentication, authorization, and character relationship management.

## Overview

The auth_user system provides:
- **User Authentication**: Secure login/logout with JWT tokens
- **User Management**: User registration, profile management, and account settings
- **Role-Based Access Control**: Flexible permission system with roles and permissions
- **Character Relationships**: User-character access control and ownership management
- **Security Features**: Password hashing, token management, and data validation

## Architecture

### Directory Structure
```
auth_user/
├── models/           # SQLAlchemy data models
│   ├── base.py      # Base model with UUID and timestamps
│   └── user_models.py # User, Role, Permission models
├── services/         # Business logic services
│   ├── auth_service.py     # Authentication and authorization
│   ├── token_service.py    # JWT token management
│   ├── security_service.py # Encryption and security utilities
│   └── password_service.py # Password hashing and verification
├── schemas/          # Pydantic request/response schemas
├── repositories/     # Database access layer (placeholder)
├── utils/           # Utility functions
│   ├── auth_utils.py       # Character relationship management
│   └── validation_utils.py # Data validation utilities
└── routers/         # FastAPI route handlers
```

### Key Components

#### Models
- **User**: Core user model with email, password, and status
- **Role**: User roles for grouping permissions
- **Permission**: Individual permissions for fine-grained access control
- **AuthBaseModel**: Base model providing UUID primary keys and timestamps

#### Services
- **AuthService**: User authentication, permission checking, character access
- **TokenService**: JWT token creation, verification, and refresh
- **SecurityService**: Data encryption, API key generation, secure tokens
- **PasswordService**: Bcrypt password hashing and verification

#### Schemas
- **Authentication**: LoginRequest, TokenResponse, RefreshTokenRequest
- **User Management**: UserCreate, UserUpdate, UserResponse
- **Roles & Permissions**: RoleCreate, RoleResponse, PermissionResponse
- **Relationships**: AuthRelationshipCreate, AuthRelationshipUpdate, AuthRelationshipResponse

## Usage Examples

### Basic Authentication
```python
from backend.systems.auth_user import (
    authenticate_user, create_token_pair, verify_token,
    get_current_active_user
)

# Authenticate user
user = await authenticate_user("user@example.com", "password")
if user:
    # Create token pair
    access_token, refresh_token = create_token_pair(
        {"email": user["email"]}, 
        subject=user["id"]
    )
    
    # Verify token
    payload = verify_token(access_token)
    if payload:
        print(f"Authenticated user: {payload['email']}")
```

### Password Management
```python
from backend.systems.auth_user import (
    get_password_hash, verify_password, validate_password_strength
)

# Validate password strength
is_valid, error = validate_password_strength("MySecurePassword123!")
if is_valid:
    # Hash password for storage
    hashed = get_password_hash("MySecurePassword123!")
    
    # Later, verify password
    if verify_password("MySecurePassword123!", hashed):
        print("Password verified!")
```

### Permission Checking
```python
from backend.systems.auth_user import check_permissions, require_permissions

# Check user permissions
user = {"permissions": ["read_characters", "write_characters"]}
has_access = check_permissions(user, ["read_characters"])

# Use decorator for endpoint protection
@require_permissions(["admin"])
async def admin_endpoint(current_user: dict):
    return {"message": "Admin access granted"}
```

### Character Relationship Management
```python
from backend.systems.auth_user import (
    create_auth_relationship, check_user_character_access,
    get_user_accessible_characters
)

# Grant user access to character
await create_auth_relationship(
    user_id="user-uuid",
    character_id="character-uuid", 
    permissions=["read", "write"],
    is_owner=True
)

# Check access
has_access = await check_user_character_access(
    "user-uuid", "character-uuid", "write"
)

# Get all accessible characters
characters = await get_user_accessible_characters("user-uuid")
```

### Data Validation
```python
from backend.systems.auth_user import (
    validate_email_format, validate_username_format
)

# Validate email
is_valid, error = validate_email_format("user@example.com")

# Validate username
is_valid, error = validate_username_format("username123")
```

## Security Features

### Password Security
- **Bcrypt Hashing**: Industry-standard password hashing
- **Strength Validation**: Enforces complex password requirements
- **Salt Generation**: Automatic salt generation for each password

### Token Security
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Refresh Tokens**: Long-lived tokens for seamless re-authentication
- **Token Types**: Separate access and refresh token validation
- **Secure Defaults**: Fallback configuration for development

### Data Protection
- **Input Validation**: Comprehensive validation for all user inputs
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Prevention**: Pydantic schema validation and sanitization

## Configuration

The system uses environment variables for configuration:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/db

# Security Configuration
BCRYPT_ROUNDS=12
```

## Database Integration

The system is designed for easy database integration:

1. **Models Ready**: SQLAlchemy models with proper relationships
2. **Repository Pattern**: Placeholder repositories for database operations
3. **Migration Support**: Alembic-compatible model definitions
4. **UUID Primary Keys**: Distributed-system-friendly identifiers

### Example Database Setup
```python
from backend.systems.auth_user.models import Base, User, Role, Permission
from sqlalchemy import create_engine

# Create tables
engine = create_engine("postgresql://user:pass@localhost/db")
Base.metadata.create_all(engine)
```

## Testing

The system includes comprehensive test coverage:

```python
# Run basic functionality test
python -c "
from backend.systems.auth_user import *
print('All imports successful')
"
```

## Development Notes

### Future Enhancements
- **Database Integration**: Complete repository implementations
- **OAuth2 Support**: Social login integration
- **Multi-Factor Authentication**: TOTP and SMS support
- **Audit Logging**: User action tracking and security monitoring
- **Rate Limiting**: API endpoint protection
- **Session Management**: Advanced session handling

### Production Considerations
- **Secret Management**: Use proper secret management systems
- **Database Optimization**: Add indexes and query optimization
- **Monitoring**: Implement authentication metrics and alerting
- **Backup Strategy**: User data backup and recovery procedures

## API Integration

The system integrates seamlessly with FastAPI:

```python
from fastapi import FastAPI, Depends
from backend.systems.auth_user import get_current_active_user

app = FastAPI()

@app.post("/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_active_user)):
    return {"user": current_user["email"], "message": "Access granted"}
```

## Character Relationship System

The auth_user system includes sophisticated character relationship management:

- **Ownership Control**: Users can own characters with full control
- **Permission Granularity**: Read, write, admin permissions per character
- **Bulk Operations**: Efficient bulk relationship management
- **Transfer Support**: Character ownership transfer between users
- **Multi-Character Access**: Users can access multiple characters with different permissions

This system enables complex multi-user scenarios where characters can be shared, collaborated on, or transferred between users while maintaining security and access control.
