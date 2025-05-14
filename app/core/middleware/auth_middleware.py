"""
Authentication middleware for protecting routes.
"""

from functools import wraps
from flask import request, jsonify, current_app, g
from app.core.services.auth_service import AuthService
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.services.access_control_service import access_control_service

def require_auth(f):
    """
    Decorator to require authentication for routes.
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            return jsonify({'message': 'This is a protected route'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Get session token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Missing or invalid session token'}), 401
            
            session_token = auth_header.split(' ')[1]
            
            # Validate session and get user
            user, session = AuthService.validate_session(session_token)
            
            # Store user and session in request context
            g.current_user = user
            g.current_session = session
            
            return f(*args, **kwargs)
            
        except AuthenticationError as e:
            return jsonify({'error': str(e)}), 401
        except Exception as e:
            current_app.logger.error(f"Authentication middleware error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 500
    
    return decorated

def require_role(*roles):
    """
    Decorator to require specific roles for routes.
    Must be used after @require_auth.
    
    Usage:
        @app.route('/admin')
        @require_auth
        @require_role('admin')
        def admin_route():
            return jsonify({'message': 'This is an admin route'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Check if user has required role using access_control_service
                user = g.current_user
                if not user or not any(user.role and user.role.name == role for role in roles):
                    raise AuthorizationError('Insufficient permissions')
                return f(*args, **kwargs)
            except AuthorizationError as e:
                return jsonify({'error': str(e)}), 403
            except Exception as e:
                current_app.logger.error(f"Role authorization error: {str(e)}")
                return jsonify({'error': 'Authorization failed'}), 500
        return decorated
    return decorator

def require_permission(permission):
    """
    Decorator to require a specific permission for routes (middleware-level).
    Must be used after @require_auth.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                user = g.current_user
                if not user or not access_control_service.has_permission(user, permission):
                    raise AuthorizationError(f'Insufficient permissions: {permission}')
                return f(*args, **kwargs)
            except AuthorizationError as e:
                return jsonify({'error': str(e)}), 403
            except Exception as e:
                current_app.logger.error(f"Permission authorization error: {str(e)}")
                return jsonify({'error': 'Authorization failed'}), 500
        return decorated
    return decorator 