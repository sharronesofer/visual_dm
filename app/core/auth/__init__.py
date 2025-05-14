"""
Authentication module initialization.
"""

from functools import wraps
from flask import request, jsonify, current_app
from app.core.utils.error_utils import AuthenticationError

def login_required(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            # Extract token
            token_type, token = auth_header.split(' ')
            if token_type.lower() != 'bearer':
                raise AuthenticationError('Invalid token type')
            
            # Verify token
            if not current_app.config.get('TESTING', False):
                # In production, verify the token
                # This is just a placeholder - implement your actual token verification
                pass
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    return decorated_function
