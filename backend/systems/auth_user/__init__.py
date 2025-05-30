"""
User authentication system package.

This package provides user authentication functionality including:
- User, Role, and Permission models
- Authentication services (token handling, password hashing)
- Character-User relationship management
- Permission validation utilities
"""

# Import key models
from .models import User, Role, Permission

# Import key authentication services
from .services import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_current_active_user
)

# Import validation utilities
from .utils import (
    # Data validation
    validate_password_strength,
    validate_username_format,
    validate_email_format,
    
    # Auth relationship management
    create_auth_relationship,
    update_auth_relationship,
    remove_auth_relationship,
    get_auth_relationship,
    
    # Permission management
    check_permission,
    add_permission,
    remove_permission,
    set_ownership,
    
    # Query functions
    get_user_characters,
    get_character_users,
    
    # Bulk operations
    bulk_create_auth_relationships,
    bulk_remove_auth_relationships,
    
    # Advanced functions
    transfer_character_ownership,
    check_multi_character_permission,
    get_permission_matrix
)

__all__ = [
    # Models
    "User", "Role", "Permission",
    
    # Authentication services
    "verify_password", "get_password_hash", "create_access_token", 
    "verify_token", "get_current_active_user",
    
    # Validation utilities
    "validate_password_strength", "validate_username_format", "validate_email_format",
    
    # Auth relationship management
    "create_auth_relationship", "update_auth_relationship", 
    "remove_auth_relationship", "get_auth_relationship",
    
    # Permission management
    "check_permission", "add_permission", "remove_permission", "set_ownership",
    
    # Query functions
    "get_user_characters", "get_character_users",
    
    # Bulk operations
    "bulk_create_auth_relationships", "bulk_remove_auth_relationships",
    
    # Advanced functions
    "transfer_character_ownership", "check_multi_character_permission", "get_permission_matrix"
] 