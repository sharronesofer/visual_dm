import logging
from typing import Any, Dict, Optional
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.utils.config_utils import ConfigError

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 500, payload: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self) -> Dict[str, Any]:
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

class BaseError(Exception):
    """Base error class."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__()
        self.message = message
        self.status_code = status_code

class AuthenticationError(BaseError):
    """Authentication error."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(BaseError):
    """Authorization error."""
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, status_code=403)

class ValidationError(BaseError):
    """Validation error."""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=400)

def handle_error(error):
    """Handle application errors"""
    if isinstance(error, HTTPException):
        response = {
            "error": error.description,
            "status_code": error.code
        }
    else:
        response = {
            "error": str(error),
            "status_code": 500
        }
    
    return jsonify(response), response["status_code"]

def handle_auth_error(error: BaseError) -> tuple[Dict[str, Any], int]:
    """Handle authentication and authorization errors."""
    response = {
        'error': True,
        'message': str(error.message),
        'status_code': error.status_code
    }
    logger.error(f"Auth error: {error.message}")
    return jsonify(response), error.status_code

def register_error_handlers(app: Any) -> None:
    """Register error handlers for the application"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError) -> Any:
        """Handle API errors"""
        logger.error(f"API Error: {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException) -> Any:
        """Handle HTTP errors"""
        logger.error(f"HTTP Error: {error.description}")
        response = jsonify({
            'message': error.description,
            'status_code': error.code
        })
        response.status_code = error.code
        return response

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error: SQLAlchemyError) -> Any:
        """Handle database errors"""
        logger.error(f"Database Error: {str(error)}")
        response = jsonify({
            'message': 'A database error occurred',
            'status_code': 500
        })
        response.status_code = 500
        return response

    @app.errorhandler(ConfigError)
    def handle_config_error(error: ConfigError) -> Any:
        """Handle configuration errors"""
        logger.error(f"Configuration Error: {str(error)}")
        response = jsonify({
            'message': str(error),
            'status_code': 500
        })
        response.status_code = 500
        return response

    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        return handle_auth_error(error)
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        return handle_auth_error(error)
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return handle_auth_error(error)
    
    @app.errorhandler(404)
    def handle_not_found_error(error):
        response = {
            'error': True,
            'message': 'Resource not found',
            'status_code': 404
        }
        return jsonify(response), 404
    
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        response = {
            'error': True,
            'message': 'Internal server error',
            'status_code': 500
        }
        logger.error(f"Internal server error: {str(error)}")
        return jsonify(response), 500

    @app.after_request
    def after_request(response: Any) -> Any:
        """Log all requests and responses"""
        logger.info(f"{request.method} {request.path} - {response.status_code}")
        return response 