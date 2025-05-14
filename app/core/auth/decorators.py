from functools import wraps
from typing import Optional, Union, Callable, List

from flask import request, current_app, g
import jwt

from ..api.response import APIResponse

def get_token_from_header() -> Optional[str]:
    """Extract JWT token from Authorization header."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    return auth_header.split(' ')[1]

def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def require_auth(f: Callable) -> Callable:
    """Decorator to require valid authentication for an endpoint."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return APIResponse.unauthorized().to_dict(), 401
            
        try:
            payload = decode_token(token)
            g.current_user = payload
        except ValueError as e:
            return APIResponse.unauthorized(str(e)).to_dict(), 401
            
        return f(*args, **kwargs)
    return decorated

def require_role(role: Union[str, List[str]]) -> Callable:
    """Decorator to require specific role(s) for an endpoint."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            required_roles = [role] if isinstance(role, str) else role
            user_roles = g.current_user.get('roles', [])
            
            if not any(r in user_roles for r in required_roles):
                return APIResponse.forbidden(
                    f"Required role(s): {', '.join(required_roles)}"
                ).to_dict(), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def require_permission(permission: Union[str, List[str]]) -> Callable:
    """Decorator to require specific permission(s) for an endpoint."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            required_permissions = [permission] if isinstance(permission, str) else permission
            user_permissions = g.current_user.get('permissions', [])
            
            if not any(p in user_permissions for p in required_permissions):
                return APIResponse.forbidden(
                    f"Required permission(s): {', '.join(required_permissions)}"
                ).to_dict(), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def optional_auth(f: Callable) -> Callable:
    """Decorator to optionally authenticate a request."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if token:
            try:
                payload = decode_token(token)
                g.current_user = payload
            except ValueError:
                g.current_user = None
        else:
            g.current_user = None
            
        return f(*args, **kwargs)
    return decorated 