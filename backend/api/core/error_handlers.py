"""
Error Handling Middleware

This module provides consistent error handling for the API.
"""

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import traceback
import uuid

# Configure logger
logger = logging.getLogger(__name__)

# Error code mappings
ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    408: "request_timeout",
    409: "conflict",
    422: "validation_error",
    429: "too_many_requests",
    500: "internal_server_error",
    501: "not_implemented",
    503: "service_unavailable"
}

class ErrorResponseGenerator:
    """Utility class to generate consistent error responses"""
    
    @staticmethod
    def create_error_response(
        status_code: int,
        error_message: str,
        error_detail: Optional[Union[List[Dict[str, Any]], Dict[str, Any], str]] = None,
        error_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            status_code: HTTP status code
            error_message: Human-readable error message
            error_detail: Additional error details
            error_code: Custom error code
            
        Returns:
            Error response dictionary
        """
        if error_code is None:
            error_code = ERROR_CODES.get(status_code, "unknown_error")
            
        error_type = status_code // 100
        if error_type == 4:
            error_class = "ClientError"
        elif error_type == 5:
            error_class = "ServerError"
        else:
            error_class = "Error"
            
        response = {
            "error": error_class,
            "error_code": error_code,
            "message": error_message,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if error_detail:
            response["details"] = error_detail
            
        return response


def setup_error_handlers(app: FastAPI):
    """
    Set up global error handlers for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle standard HTTP exceptions"""
        status_code = exc.status_code
        error_message = str(exc.detail)
        
        # Generate a unique error ID for server errors
        error_id = None
        if status_code >= 500:
            error_id = str(uuid.uuid4())
            logger.error(
                f"HTTP error {status_code} (ID: {error_id}): {error_message}\n"
                f"URL: {request.method} {request.url}"
            )
        
        response = ErrorResponseGenerator.create_error_response(
            status_code=status_code,
            error_message=error_message
        )
        
        if error_id:
            response["error_id"] = error_id
            
        return JSONResponse(
            status_code=status_code,
            content=response
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        status_code = 422
        error_message = "Request validation error"
        
        # Format validation errors
        detail = []
        for error in exc.errors():
            error_entry = {
                "field": ".".join([str(loc) for loc in error["loc"][1:]]) if len(error["loc"]) > 1 else "",
                "type": error["type"],
                "message": error["msg"]
            }
            detail.append(error_entry)
            
        response = ErrorResponseGenerator.create_error_response(
            status_code=status_code,
            error_message=error_message,
            error_detail=detail,
            error_code="validation_error"
        )
        
        return JSONResponse(
            status_code=status_code,
            content=response
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors"""
        status_code = 422
        error_message = "Data validation error"
        
        # Format validation errors
        detail = []
        for error in exc.errors():
            error_entry = {
                "field": ".".join([str(loc) for loc in error["loc"]]),
                "type": error["type"],
                "message": error["msg"]
            }
            detail.append(error_entry)
            
        response = ErrorResponseGenerator.create_error_response(
            status_code=status_code,
            error_message=error_message,
            error_detail=detail,
            error_code="validation_error"
        )
        
        return JSONResponse(
            status_code=status_code,
            content=response
        )
    
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Handle any unhandled exceptions"""
        status_code = 500
        error_message = "Internal server error"
        
        # Generate a unique error ID for tracking
        error_id = str(uuid.uuid4())
        
        # Format traceback
        tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        
        # Log the error with complete details
        logger.error(
            f"Unhandled exception (ID: {error_id}):\n"
            f"URL: {request.method} {request.url}\n"
            f"Exception: {str(exc)}\n"
            f"Traceback:\n{tb_str}"
        )
        
        # In production, we don't want to expose the actual error
        response = ErrorResponseGenerator.create_error_response(
            status_code=status_code,
            error_message=error_message,
            error_code="internal_server_error"
        )
        
        # Add error ID for reference
        response["error_id"] = error_id
        
        return JSONResponse(
            status_code=status_code,
            content=response
        ) 