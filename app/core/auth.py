"""
Authentication utilities with comprehensive error handling.
"""

import logging
from functools import wraps
from typing import Optional, Dict, Any, Callable
from flask import request, jsonify, current_app
from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import FirebaseError
from app.core.utils.error_utils import (
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
    AuthorizationError
)
from app.core.utils.auth_utils import require_permission

# Configure logging
logger = logging.getLogger(__name__)

class AuthError(AuthenticationError):
    """Base class for authentication errors."""
    def __init__(self, message: str, error_code: str, status_code: int = 401):
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code
        self.details = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'error': self.message,
            'error_code': self.error_code,
            'status_code': self.status_code,
            'details': self.details
        }

class InvalidTokenError(AuthError):
    """Error for invalid or malformed tokens."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='INVALID_TOKEN',
            status_code=401
        )
        if details:
            self.details = details

class TokenExpiredError(AuthError):
    """Error for expired tokens."""
    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            message=message,
            error_code='TOKEN_EXPIRED',
            status_code=401
        )

class AuthorizationError(AuthError):
    """Error for insufficient permissions."""
    def __init__(self, message: str, required_permissions: Optional[List[str]] = None):
        super().__init__(
            message=message,
            error_code='INSUFFICIENT_PERMISSIONS',
            status_code=403
        )
        if required_permissions:
            self.details['required_permissions'] = required_permissions

def login_required(f: Callable) -> Callable:
    """
    Decorator to require authentication for a route.
    
    Args:
        f: The route function to decorate
        
    Returns:
        The decorated function
        
    Raises:
        InvalidTokenError: If the token is invalid
        TokenExpiredError: If the token has expired
        AuthenticationError: For other authentication errors
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                logger.warning("No authorization header provided")
                raise InvalidTokenError("No authorization header provided")
            
            # Extract token
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                logger.warning("Malformed authorization header")
                raise InvalidTokenError("Malformed authorization header")
            
            # Verify token
            try:
                decoded_token = firebase_auth.verify_id_token(token)
                request.user = decoded_token
                logger.info(f"User authenticated: {decoded_token.get('uid')}")
            except firebase_auth.InvalidIdTokenError:
                logger.warning("Invalid token provided")
                raise InvalidTokenError("Invalid token")
            except firebase_auth.ExpiredIdTokenError:
                logger.warning("Token has expired")
                raise TokenExpiredError()
            except FirebaseError as e:
                logger.error(f"Firebase authentication error: {str(e)}")
                raise AuthenticationError(
                    message="Firebase authentication error",
                    details={"error": str(e)}
                )
            
            return f(*args, **kwargs)
            
        except (InvalidTokenError, TokenExpiredError, AuthenticationError) as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify(e.to_dict()), e.status_code
            
        except Exception as e:
            logger.error(f"Unexpected authentication error: {str(e)}")
            return jsonify({
                'error': 'An unexpected error occurred during authentication',
                'error_code': 'AUTHENTICATION_ERROR',
                'status_code': 500,
                'details': {'error': str(e)}
            }), 500
            
    return decorated_function

def require_permission(permission: str) -> Callable:
    """
    Decorator to require specific permissions for a route.
    
    Args:
        permission: The required permission
        
    Returns:
        The decorated function
        
    Raises:
        AuthorizationError: If the user lacks the required permission
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if not hasattr(request, 'user'):
                    raise AuthenticationError("User not authenticated")
                
                user_permissions = request.user.get('permissions', [])
                if permission not in user_permissions:
                    logger.warning(
                        f"User {request.user.get('uid')} lacks required permission: {permission}"
                    )
                    raise AuthorizationError(
                        "Insufficient permissions",
                        required_permissions=[permission]
                    )
                
                return f(*args, **kwargs)
                
            except AuthorizationError as e:
                logger.error(f"Authorization error: {str(e)}")
                return jsonify(e.to_dict()), e.status_code
                
            except Exception as e:
                logger.error(f"Unexpected authorization error: {str(e)}")
                return jsonify({
                    'error': 'An unexpected error occurred during authorization',
                    'error_code': 'AUTHORIZATION_ERROR',
                    'status_code': 500,
                    'details': {'error': str(e)}
                }), 500
                
        return decorated_function
    return decorator 

# Example usage for developers:
# @require_permission('manage_users')
# def admin_only_route():
#     ... 