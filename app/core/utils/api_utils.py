import logging
from typing import Any, Dict, Optional, Union, List
from flask import jsonify, request
from marshmallow import Schema, ValidationError
from app.utils.error_handlers import APIError, ValidationError as AppValidationError

logger = logging.getLogger(__name__)

class APIResponse:
    """Standard API response wrapper"""
    
    def __init__(
        self,
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None
    ) -> None:
        self.data = data
        self.message = message
        self.status_code = status_code
        self.meta = meta or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format"""
        return {
            'data': self.data,
            'message': self.message,
            'status_code': self.status_code,
            'meta': self.meta
        }
    
    def to_json(self) -> Any:
        """Convert response to JSON format"""
        return jsonify(self.to_dict()), self.status_code

def validate_request(schema: Schema) -> Dict[str, Any]:
    """Validate request data against a schema"""
    try:
        # Get request data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # Validate data
        validated_data = schema.load(data)
        logger.debug(f"Request validation successful: {validated_data}")
        return validated_data
        
    except ValidationError as e:
        logger.warning(f"Request validation failed: {str(e)}")
        raise AppValidationError(
            message="Invalid request data",
            payload={'errors': e.messages}
        )
    except Exception as e:
        logger.error(f"Unexpected error during request validation: {str(e)}")
        raise APIError(
            message="Failed to validate request data",
            status_code=500
        )

def paginate_query(
    query: Any,
    page: int = 1,
    per_page: int = 10,
    max_per_page: int = 100
) -> Dict[str, Any]:
    """Paginate a SQLAlchemy query"""
    try:
        # Validate pagination parameters
        page = max(1, page)
        per_page = min(max_per_page, max(1, per_page))
        
        # Execute paginated query
        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Build pagination metadata
        meta = {
            'page': page,
            'per_page': per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
        
        logger.debug(f"Query paginated successfully: {meta}")
        return {
            'items': paginated.items,
            'meta': meta
        }
        
    except Exception as e:
        logger.error(f"Failed to paginate query: {str(e)}")
        raise APIError(
            message="Failed to paginate results",
            status_code=500
        )

def format_error_response(
    error: Exception,
    status_code: int = 500,
    include_traceback: bool = False
) -> Any:
    """Format error response"""
    error_data = {
        'message': str(error),
        'status_code': status_code
    }
    
    if include_traceback and hasattr(error, '__traceback__'):
        import traceback
        error_data['traceback'] = traceback.format_tb(error.__traceback__)
    
    logger.error(f"Error response: {error_data}")
    return jsonify(error_data), status_code

def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    meta: Optional[Dict[str, Any]] = None
) -> Any:
    """Format success response"""
    response = APIResponse(
        data=data,
        message=message,
        status_code=status_code,
        meta=meta
    )
    logger.debug(f"Success response: {response.to_dict()}")
    return response.to_json() 