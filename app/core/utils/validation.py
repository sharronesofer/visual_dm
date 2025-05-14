"""
Validation utilities for request data.
"""

from functools import wraps
from flask import request, jsonify
from jsonschema import validate, ValidationError

def validate_request(schema):
    """Decorator to validate request JSON data against a schema.
    
    Args:
        schema: JSON schema to validate against
        
    Returns:
        Decorated function that validates request data
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                if not data and schema.get('required'):
                    return jsonify({'error': 'No JSON data provided'}), 400
                    
                validate(instance=data or {}, schema=schema)
                return f(*args, **kwargs)
            except ValidationError as e:
                return jsonify({'error': str(e)}), 400
        return decorated_function
    return decorator 