from functools import wraps
from typing import Type, Optional, Callable, Any
from flask import request, current_app
from pydantic import BaseModel, ValidationError

from .response import APIResponse

def validate_request(
    body_model: Optional[Type[BaseModel]] = None,
    query_model: Optional[Type[BaseModel]] = None,
    return_parsed: bool = True
) -> Callable:
    """Decorator to validate request data using Pydantic models."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            parsed_data = {}
            
            # Validate request body if model provided
            if body_model and request.is_json:
                try:
                    parsed_data['body'] = body_model.parse_obj(request.get_json())
                except ValidationError as e:
                    return APIResponse(
                        status_code=400,
                        error={
                            'message': 'Invalid request body',
                            'details': e.errors()
                        }
                    ).to_dict(), 400
                    
            # Validate query parameters if model provided
            if query_model:
                try:
                    parsed_data['query'] = query_model.parse_obj(dict(request.args))
                except ValidationError as e:
                    return APIResponse(
                        status_code=400,
                        error={
                            'message': 'Invalid query parameters',
                            'details': e.errors()
                        }
                    ).to_dict(), 400
            
            # Add parsed data to kwargs if requested
            if return_parsed and parsed_data:
                kwargs.update(parsed_data)
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def validate_response(model: Type[BaseModel]) -> Callable:
    """Decorator to validate response data using a Pydantic model."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # Handle tuple returns (data, status_code)
            status_code = 200
            if isinstance(result, tuple):
                data = result[0]
                status_code = result[1]
            else:
                data = result
                
            try:
                # Validate response data
                validated_data = model.parse_obj(data)
                return validated_data.dict(), status_code
            except ValidationError as e:
                current_app.logger.error(f"Response validation failed: {e.errors()}")
                return APIResponse(
                    status_code=500,
                    error={
                        'message': 'Response validation failed',
                        'details': e.errors()
                    }
                ).to_dict(), 500
                
        return decorated
    return decorator 