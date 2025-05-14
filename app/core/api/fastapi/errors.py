"""FastAPI error handling utilities."""

from typing import Dict, Any, Optional, Type
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import traceback

class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

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

def setup_error_handlers(app: FastAPI) -> None:
    """Set up FastAPI error handlers."""
    
    @app.exception_handler(APIError)
    async def handle_api_error(request: Request, error: APIError) -> JSONResponse:
        """Handle custom API errors."""
        error_detail = ErrorDetail(
            code=error.error_code,
            message=error.message,
            field=error.field,
            details=error.details
        )
        
        return JSONResponse(
            status_code=error.status_code,
            content={
                "status": error.status_code,
                "error": error_detail.dict(exclude_none=True),
                "path": request.url.path
            }
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        error: RequestValidationError
    ) -> JSONResponse:
        """Handle FastAPI/Pydantic validation errors."""
        error_detail = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": error.errors()}
        )
        
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "error": error_detail.dict(exclude_none=True),
                "path": request.url.path
            }
        )

    @app.exception_handler(Exception)
    async def handle_generic_error(request: Request, error: Exception) -> JSONResponse:
        """Handle all other unhandled exceptions."""
        # Log the full error with traceback
        app.logger.error(
            f"Unhandled error: {str(error)}\n"
            f"Traceback: {''.join(traceback.format_tb(error.__traceback__))}"
        )
        
        error_detail = ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred"
        )
        
        # Include error details in development
        if app.debug:
            error_detail.details = {
                "error": str(error),
                "traceback": traceback.format_exc()
            }
        
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "error": error_detail.dict(exclude_none=True),
                "path": request.url.path
            }
        ) 