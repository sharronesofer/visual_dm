from typing import Type, Dict, Any, Optional
from flask import current_app, request
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError
import traceback

from .response import APIResponse
from .models import ErrorDetail

class APIError(Exception):
    """Base exception class for API errors."""
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "BAD_REQUEST",
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        self.field = field

class NotFoundError(APIError):
    """Resource not found error."""
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            **kwargs
        )

class ValidationError(APIError):
    """Request validation error."""
    def __init__(self, message: str = "Validation error", **kwargs):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            **kwargs
        )

class AuthenticationError(APIError):
    """Authentication error."""
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_REQUIRED",
            **kwargs
        )

class AuthorizationError(APIError):
    """Authorization error."""
    def __init__(self, message: str = "Permission denied", **kwargs):
        super().__init__(
            message=message,
            status_code=403,
            error_code="PERMISSION_DENIED",
            **kwargs
        )

class RateLimitError(APIError):
    """Rate limit exceeded error."""
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            **kwargs
        )

def register_error_handlers(app):
    """Register error handlers for the Flask application."""
    
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        """Handle custom API errors."""
        error_detail = ErrorDetail(
            code=error.error_code,
            message=error.message,
            field=error.field,
            details=error.details
        )
        
        return APIResponse(
            status_code=error.status_code,
            error=error_detail.dict()
        ).to_dict(), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        """Handle Pydantic validation errors."""
        error_detail = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": error.errors()}
        )
        
        return APIResponse(
            status_code=400,
            error=error_detail.dict()
        ).to_dict(), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        """Handle Werkzeug HTTP exceptions."""
        error_detail = ErrorDetail(
            code=error.name.upper().replace(' ', '_'),
            message=error.description
        )
        
        return APIResponse(
            status_code=error.code,
            error=error_detail.dict()
        ).to_dict(), error.code

    @app.errorhandler(Exception)
    def handle_generic_error(error: Exception):
        """Handle all other unhandled exceptions."""
        # Log the full error with traceback
        current_app.logger.error(
            f"Unhandled error: {str(error)}\n"
            f"Traceback: {''.join(traceback.format_tb(error.__traceback__))}"
        )
        
        error_detail = ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred"
        )
        
        # Include error details in development
        if current_app.debug:
            error_detail.details = {
                "error": str(error),
                "traceback": traceback.format_exc()
            }
        
        return APIResponse(
            status_code=500,
            error=error_detail.dict()
        ).to_dict(), 500 