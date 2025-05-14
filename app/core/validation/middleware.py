"""
Middleware for handling validation of incoming requests.
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional
from flask import request, jsonify, current_app, g
from app.core.api.error_handling.exceptions import ValidationError
from app.core.validation.validators import validate_request_data

def validate_json(schema: Dict[str, Any]):
    """
    Decorator for validating JSON request data.
    
    Args:
        schema: Dictionary of field validators
        
    Returns:
        Decorated function
    
    Usage:
        @app.route('/resource', methods=['POST'])
        @validate_json({
            'name': StringValidator('name', min_length=3, max_length=50),
            'age': NumberValidator('age', min_value=0, is_integer=True)
        })
        def create_resource():
            # Request data is guaranteed to be valid here
            data = request.get_json()
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Ensure request has JSON data
                if not request.is_json:
                    raise ValidationError(
                        message="Request must be JSON",
                        details=[{"field": "content-type", "message": "Content-Type must be application/json"}]
                    )
                
                # Get and validate request data
                data = request.get_json(force=True)
                if data is None:
                    raise ValidationError(
                        message="Invalid JSON",
                        details=[{"field": "body", "message": "Request body must be valid JSON"}]
                    )
                
                # Validate data against schema
                validate_request_data(schema, data)
                
                # Store validated data in request context
                g.validated_data = data
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                current_app.logger.warning(f"Validation error: {e.message}")
                return jsonify({
                    "error": e.code,
                    "message": e.message,
                    "details": e.details
                }), e.status_code
                
            except Exception as e:
                current_app.logger.error(f"Validation middleware error: {str(e)}")
                return jsonify({
                    "error": "internal_error",
                    "message": "An error occurred while validating the request"
                }), 500
        
        return decorated
    return decorator

def validate_query_params(schema: Dict[str, Any]):
    """
    Decorator for validating query parameters.
    
    Args:
        schema: Dictionary of field validators
        
    Returns:
        Decorated function
    
    Usage:
        @app.route('/resources', methods=['GET'])
        @validate_query_params({
            'page': NumberValidator('page', required=False, min_value=1, is_integer=True),
            'limit': NumberValidator('limit', required=False, min_value=1, max_value=100, is_integer=True)
        })
        def list_resources():
            # Query parameters are guaranteed to be valid here
            args = request.args
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Convert query params to a dict
                params = {}
                for key in request.args:
                    params[key] = request.args.get(key)
                
                # Validate params against schema
                validate_request_data(schema, params)
                
                # Store validated params in request context
                g.validated_params = params
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                current_app.logger.warning(f"Query parameter validation error: {e.message}")
                return jsonify({
                    "error": e.code,
                    "message": e.message,
                    "details": e.details
                }), e.status_code
                
            except Exception as e:
                current_app.logger.error(f"Query parameter validation error: {str(e)}")
                return jsonify({
                    "error": "internal_error",
                    "message": "An error occurred while validating the request"
                }), 500
        
        return decorated
    return decorator

def validate_request_context(validation_fn: Callable[[], Optional[ValidationError]]):
    """
    Decorator for validating request context.
    Useful for validating relationships between different parts of the request
    or for validating against data from a database.
    
    Args:
        validation_fn: Function that performs validation and returns a ValidationError on failure
        
    Returns:
        Decorated function
    
    Usage:
        @app.route('/resources/<int:resource_id>', methods=['PUT'])
        @validate_json({
            'name': StringValidator('name', min_length=3, max_length=50)
        })
        @validate_request_context(lambda: validate_resource_ownership())
        def update_resource(resource_id):
            # Request data is valid and user owns the resource
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Perform validation
                error = validation_fn()
                if error:
                    return jsonify({
                        "error": error.code,
                        "message": error.message,
                        "details": error.details
                    }), error.status_code
                
                return f(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"Context validation error: {str(e)}")
                return jsonify({
                    "error": "internal_error",
                    "message": "An error occurred while validating the request context"
                }), 500
        
        return decorated
    return decorator 