"""
Security mechanisms for preventing replay attacks and request tampering.
"""

from functools import wraps
import time
import hmac
import hashlib
import base64
import json
from typing import Any, Dict, Optional, Set, Tuple
from flask import request, jsonify, current_app, g
from app.core.api.error_handling.exceptions import UnauthorizedError, ValidationError

class NonceManager:
    """Manager for tracking and validating nonces."""
    
    def __init__(self, expiration_seconds: int = 300, max_size: int = 10000):
        """Initialize nonce manager.
        
        Args:
            expiration_seconds: Number of seconds a nonce is valid for
            max_size: Maximum number of nonces to store
        """
        self.expiration_seconds = expiration_seconds
        self.max_size = max_size
        self.nonces: Dict[str, float] = {}
    
    def validate_nonce(self, nonce: str, timestamp: float) -> bool:
        """Validate a nonce.
        
        Args:
            nonce: Nonce to validate
            timestamp: Timestamp of the nonce
            
        Returns:
            True if nonce is valid, False otherwise
        """
        # Check if nonce exists
        if nonce in self.nonces:
            return False
        
        # Check if nonce is expired
        current_time = time.time()
        if current_time - timestamp > self.expiration_seconds:
            return False
        
        # Store nonce
        self.nonces[nonce] = timestamp
        
        # Clean up expired nonces
        if len(self.nonces) > self.max_size:
            self._cleanup()
        
        return True
    
    def _cleanup(self):
        """Clean up expired nonces."""
        current_time = time.time()
        expired_nonces = []
        
        # Find expired nonces
        for nonce, timestamp in self.nonces.items():
            if current_time - timestamp > self.expiration_seconds:
                expired_nonces.append(nonce)
        
        # Remove expired nonces
        for nonce in expired_nonces:
            del self.nonces[nonce]

# Global nonce manager
nonce_manager = NonceManager()

def generate_signature(api_key: str, secret: str, data: Dict[str, Any], timestamp: float) -> str:
    """
    Generate a request signature.
    
    Args:
        api_key: API key
        secret: Secret key
        data: Request data
        timestamp: Request timestamp
        
    Returns:
        Base64-encoded signature
    """
    # Create message string
    message = f"{api_key}:{timestamp}:{json.dumps(data, sort_keys=True)}"
    
    # Create signature
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Return base64-encoded signature
    return base64.b64encode(signature).decode('utf-8')

def verify_request_signature(request_data: Dict[str, Any], required_fields: Optional[Set[str]] = None) -> None:
    """
    Verify a request signature.
    
    Args:
        request_data: Request data
        required_fields: Set of fields that must be present in the request
            
    Raises:
        ValidationError: If validation fails
    """
    # Check for required fields
    if required_fields:
        missing_fields = required_fields - set(request_data.keys())
        if missing_fields:
            raise ValidationError(
                message="Missing required fields",
                details=[{"field": field, "message": "Field is required"} for field in missing_fields]
            )
    
    # Check for signature fields
    signature_fields = {'api_key', 'timestamp', 'nonce', 'signature'}
    missing_fields = signature_fields - set(request_data.keys())
    if missing_fields:
        raise ValidationError(
            message="Missing security fields",
            details=[{"field": field, "message": "Field is required"} for field in missing_fields]
        )
    
    # Extract signature fields
    api_key = request_data['api_key']
    timestamp = float(request_data['timestamp'])
    nonce = request_data['nonce']
    signature = request_data['signature']
    
    # Create payload without signature
    payload = {k: v for k, v in request_data.items() if k != 'signature'}
    
    # Validate timestamp
    current_time = time.time()
    if abs(current_time - timestamp) > 300:  # 5 minutes
        raise UnauthorizedError(message="Request timestamp is invalid")
    
    # Validate nonce
    if not nonce_manager.validate_nonce(nonce, timestamp):
        raise UnauthorizedError(message="Request nonce is invalid or has been used before")
    
    # Get secret for API key
    # TODO: Implement API key lookup service
    secret = current_app.config.get('API_SECRET', 'default_secret')
    
    # Verify signature
    expected_signature = generate_signature(api_key, secret, payload, timestamp)
    if not hmac.compare_digest(signature, expected_signature):
        raise UnauthorizedError(message="Request signature is invalid")

def require_signature(required_fields: Optional[Set[str]] = None):
    """
    Decorator for requiring a valid request signature.
    
    Args:
        required_fields: Set of fields that must be present in the request
        
    Returns:
        Decorated function
    
    Usage:
        @app.route('/secure', methods=['POST'])
        @require_signature({'action', 'data'})
        def secure_endpoint():
            # Request is guaranteed to have a valid signature
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Get request data
                if request.is_json:
                    data = request.get_json(force=True) or {}
                else:
                    data = dict(request.args)
                
                # Verify signature
                verify_request_signature(data, required_fields)
                
                return f(*args, **kwargs)
                
            except (ValidationError, UnauthorizedError) as e:
                current_app.logger.warning(f"Signature validation error: {e.message}")
                return jsonify({
                    "error": e.code,
                    "message": e.message,
                    "details": e.details if hasattr(e, 'details') else None
                }), e.status_code, getattr(e, 'headers', {})
                
            except Exception as e:
                current_app.logger.error(f"Signature validation error: {str(e)}")
                return jsonify({
                    "error": "internal_error",
                    "message": "An error occurred while validating the request signature"
                }), 500
        
        return decorated
    return decorator 