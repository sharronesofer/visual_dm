"""
Authentication middleware for protecting API endpoints.
"""

from functools import wraps
from typing import List, Optional, Union, Callable
from flask import request, current_app, g
from werkzeug.local import LocalProxy

from app.core.utils.api_response import ErrorResponse
from app.core.auth.jwt_manager import JWTManager, TokenExpiredError, InvalidTokenError
from app.core.models.user import User

# Current user proxy
current_user = LocalProxy(lambda: getattr(g, 'current_user', None))

def get_token_from_header() -> Optional[str]:
    """Extract JWT token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[1]

def authenticate_request() -> Optional[User]:
    """
    Authenticate request using JWT token.
    
    Returns:
        User object if authentication successful, None otherwise
    """
    token = get_token_from_header()
    if not token:
        return None

    try:
        jwt_manager: JWTManager = current_app.extensions["jwt_manager"]
        claims = jwt_manager.decode_token(token, verify_type="access")
        
        # Check if token is blacklisted
        if User.is_token_blacklisted(token):
            return None
            
        # Get user and verify existence
        user_id = claims["sub"]
        user = User.get_by_id(user_id)
        if not user:
            return None
            
        # Store user in request context
        g.current_user = user
        return user
        
    except (TokenExpiredError, InvalidTokenError):
        return None
    except Exception as e:
        current_app.logger.error(f"Authentication failed: {str(e)}")
        return None

def login_required(f: Callable) -> Callable:
    """
    Decorator to require authentication for an endpoint.
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function that checks for authentication
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = authenticate_request()
        if not user:
            return ErrorResponse(
                "Authentication required",
                status_code=401
            ).to_dict(), 401
        return f(*args, **kwargs)
    return decorated

def roles_required(*roles: str) -> Callable:
    """
    Decorator to require specific roles for an endpoint.
    
    Args:
        *roles: Role names required
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            user = authenticate_request()
            if not user:
                return ErrorResponse(
                    "Authentication required",
                    status_code=401
                ).to_dict(), 401
                
            # Check if user has any of the required roles
            if not any(role in user.roles for role in roles):
                return ErrorResponse(
                    "Insufficient permissions",
                    status_code=403
                ).to_dict(), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def roles_accepted(*roles: str) -> Callable:
    """
    Decorator to accept any of the specified roles for an endpoint.
    
    Args:
        *roles: Accepted role names
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            user = authenticate_request()
            if not user:
                return ErrorResponse(
                    "Authentication required",
                    status_code=401
                ).to_dict(), 401
                
            # Check if user has any of the accepted roles
            if not set(roles).intersection(user.roles):
                return ErrorResponse(
                    "Insufficient permissions",
                    status_code=403
                ).to_dict(), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def permission_required(permission: str) -> Callable:
    """
    Decorator to require a specific permission for an endpoint.
    
    Args:
        permission: Required permission name
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            user = authenticate_request()
            if not user:
                return ErrorResponse(
                    "Authentication required",
                    status_code=401
                ).to_dict(), 401
                
            # Check if user has the required permission
            if not user.has_permission(permission):
                return ErrorResponse(
                    "Insufficient permissions",
                    status_code=403
                ).to_dict(), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def permissions_accepted(*permissions: str) -> Callable:
    """
    Decorator to accept any of the specified permissions for an endpoint.
    
    Args:
        *permissions: Accepted permission names
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            user = authenticate_request()
            if not user:
                return ErrorResponse(
                    "Authentication required",
                    status_code=401
                ).to_dict(), 401
                
            # Check if user has any of the accepted permissions
            if not any(user.has_permission(perm) for perm in permissions):
                return ErrorResponse(
                    "Insufficient permissions",
                    status_code=403
                ).to_dict(), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator 