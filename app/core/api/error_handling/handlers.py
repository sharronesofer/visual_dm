"""FastAPI error handlers."""

import logging
from typing import Any, Dict, Optional, Type, Union
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from pydantic import ValidationError as PydanticValidationError

from .exceptions import APIError, ErrorCode
from ..responses import APIResponse

logger = logging.getLogger(__name__)

def format_validation_error(error: Union[RequestValidationError, PydanticValidationError]) -> Dict[str, Any]:
    """Format validation error details.
    
    Args:
        error: Validation error
        
    Returns:
        Formatted error details
    """
    details = []
    for err in error.errors():
        field = ".".join(str(loc) for loc in err["loc"])
        details.append({
            "field": field,
            "error": err["msg"],
            "type": err["type"]
        })
    return {
        "code": ErrorCode.VALIDATION_ERROR,
        "message": "Request validation failed",
        "details": details
    }

def format_http_error(status_code: int, detail: str) -> Dict[str, Any]:
    """Format HTTP error response.
    
    Args:
        status_code: HTTP status code
        detail: Error detail
        
    Returns:
        Formatted error details
    """
    code_map = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
        429: ErrorCode.RATE_LIMITED,
        500: ErrorCode.INTERNAL_ERROR
    }
    
    return {
        "code": code_map.get(status_code, ErrorCode.INTERNAL_ERROR),
        "message": detail
    }

def setup_error_handlers(app: FastAPI) -> None:
    """Set up FastAPI error handlers.
    
    Args:
        app: FastAPI application
    """
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, error: APIError) -> JSONResponse:
        """Handle custom API errors.
        
        Args:
            request: FastAPI request
            error: API error
            
        Returns:
            JSON response with error details
        """
        logger.error(
            f"API error: {error.code} - {error.message}",
            extra={
                "request_id": request.state.request_id,
                "path": request.url.path,
                "method": request.method,
                "error_details": error.details
            }
        )
        
        response = APIResponse(
            error={
                "code": error.code,
                "message": error.message,
                "details": error.details
            }
        )
        
        return JSONResponse(
            status_code=error.status_code,
            content=response.dict(),
            headers=error.headers
        )
    
    @app.exception_handler(RequestValidationError)
    @app.exception_handler(PydanticValidationError)
    async def validation_error_handler(
        request: Request,
        error: Union[RequestValidationError, PydanticValidationError]
    ) -> JSONResponse:
        """Handle request validation errors.
        
        Args:
            request: FastAPI request
            error: Validation error
            
        Returns:
            JSON response with validation error details
        """
        logger.warning(
            "Validation error",
            extra={
                "request_id": request.state.request_id,
                "path": request.url.path,
                "method": request.method,
                "errors": error.errors()
            }
        )
        
        response = APIResponse(error=format_validation_error(error))
        return JSONResponse(
            status_code=400,
            content=response.dict()
        )
    
    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, error: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions.
        
        Args:
            request: FastAPI request
            error: HTTP exception
            
        Returns:
            JSON response with error details
        """
        logger.error(
            f"HTTP error {error.status_code}: {error.detail}",
            extra={
                "request_id": request.state.request_id,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        response = APIResponse(error=format_http_error(error.status_code, error.detail))
        return JSONResponse(
            status_code=error.status_code,
            content=response.dict(),
            headers=getattr(error, "headers", None)
        )
    
    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, error: Exception) -> JSONResponse:
        """Handle unhandled exceptions.
        
        Args:
            request: FastAPI request
            error: Unhandled exception
            
        Returns:
            JSON response with error details
        """
        logger.exception(
            "Unhandled error",
            extra={
                "request_id": request.state.request_id,
                "path": request.url.path,
                "method": request.method,
                "error_type": type(error).__name__
            }
        )
        
        response = APIResponse(
            error={
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "An unexpected error occurred"
            }
        )
        
        return JSONResponse(
            status_code=500,
            content=response.dict()
        ) 