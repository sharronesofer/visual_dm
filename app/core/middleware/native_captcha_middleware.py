"""
Middleware for native client CAPTCHA validation.

This middleware enforces CAPTCHA validation for authentication endpoints 
when accessed by native clients (Unity, mobile, desktop).
"""

from functools import wraps
from flask import request, jsonify, current_app
from app.core.services.native_captcha import native_captcha_service

def require_native_captcha(view_func):
    """
    Decorator for requiring native CAPTCHA validation on authentication endpoints.
    
    This middleware validates a CAPTCHA response provided in the request body
    before allowing access to the protected endpoint. It works with the
    native_captcha_service to handle different CAPTCHA types.
    
    Args:
        view_func: The Flask view function to decorate
            
    Returns:
        Decorated function that validates CAPTCHA before proceeding
    
    Usage:
        @app.route('/api/v1/auth/register', methods=['POST'])
        @require_native_captcha
        def register():
            # Request is guaranteed to have a valid CAPTCHA response
            # ...
    """
    @wraps(view_func)
    def decorated(*args, **kwargs):
        # Skip CAPTCHA validation in test environment (if configured)
        if current_app.config.get('TESTING') and current_app.config.get('SKIP_CAPTCHA_IN_TESTS', False):
            return view_func(*args, **kwargs)
            
        # Check if this is a JSON request
        if not request.is_json:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request must contain JSON data'
            }), 400
            
        # Get CAPTCHA data from JSON request
        data = request.get_json()
        challenge_id = data.get('captcha_challenge_id')
        captcha_response = data.get('captcha_response')
        client_id = data.get('client_id')  # Optional but useful for rate limiting
        
        # Validate CAPTCHA data presence
        if not challenge_id or captcha_response is None:
            return jsonify({
                'error': 'captcha_required',
                'message': 'CAPTCHA challenge ID and response are required'
            }), 400
            
        # Validate CAPTCHA with service
        is_valid, result = native_captcha_service.validate_captcha(
            challenge_id=challenge_id,
            response=captcha_response,
            client_id=client_id
        )
        
        if not is_valid:
            # Handle different error types
            if result.get('error') == 'rate_limited':
                return jsonify({
                    'error': 'rate_limited',
                    'message': result.get('message', 'Rate limit exceeded'),
                    'retry_after': result.get('retry_after', 300)
                }), 429
            elif result.get('error') == 'expired':
                return jsonify({
                    'error': 'captcha_expired',
                    'message': 'CAPTCHA challenge has expired, please request a new one'
                }), 400
            elif result.get('error') == 'max_attempts':
                return jsonify({
                    'error': 'captcha_max_attempts',
                    'message': 'Maximum attempt limit reached, please request a new CAPTCHA'
                }), 400
            else:
                return jsonify({
                    'error': 'invalid_captcha',
                    'message': result.get('message', 'Invalid CAPTCHA response'),
                    'attempts_remaining': result.get('attempts_remaining')
                }), 400
                
        # CAPTCHA is valid, proceed to the view function
        return view_func(*args, **kwargs)
        
    return decorated

# Alias for consistent naming with other middleware
native_captcha_required = require_native_captcha 