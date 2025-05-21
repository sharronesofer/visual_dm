"""
Utility functions for authentication and validation.
"""

from .validation_utils import (
    validate_password_strength,
    validate_username_format,
    validate_email_format
)

from .auth_utils import (
    # Basic relationship management
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
    get_permission_matrix,
    
    # New admin access functions
    check_admin_access,
    
    # New relationship group functions
    create_relationship_group,
    get_relationship_group_members,
    add_to_relationship_group,
    
    # New history and API functions
    get_relationship_history,
    validate_api_key_access,
    generate_character_api_key,
    
    # New cache-related functions
    cache_user_permissions,
    lookup_cached_permission,
    invalidate_permission_cache
)

__all__ = [
    # Validation utils
    'validate_password_strength',
    'validate_username_format',
    'validate_email_format',
    
    # Basic relationship management
    'create_auth_relationship',
    'update_auth_relationship',
    'remove_auth_relationship',
    'get_auth_relationship',
    
    # Permission management
    'check_permission',
    'add_permission',
    'remove_permission',
    'set_ownership',
    
    # Query functions
    'get_user_characters',
    'get_character_users',
    
    # Bulk operations
    'bulk_create_auth_relationships',
    'bulk_remove_auth_relationships',
    
    # Advanced functions
    'transfer_character_ownership',
    'check_multi_character_permission',
    'get_permission_matrix',
    
    # New admin access functions
    'check_admin_access',
    
    # New relationship group functions
    'create_relationship_group',
    'get_relationship_group_members',
    'add_to_relationship_group',
    
    # New history and API functions
    'get_relationship_history',
    'validate_api_key_access',
    'generate_character_api_key',
    
    # New cache-related functions
    'cache_user_permissions',
    'lookup_cached_permission',
    'invalidate_permission_cache'
] 