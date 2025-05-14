"""FastAPI response and error handling utilities."""

from typing import Generic, TypeVar, Optional, Dict, Any, Union
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.responses import JSONResponse

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standard API response structure."""
    success: bool
    message: str
    data: Optional[T] = None

    @classmethod
    def success(cls, data: T = None, message: str = "Operation successful"):
        """Create a success response."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def created(cls, data: T = None, message: str = "Resource created successfully"):
        """Create a response for successfully created resources."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error(cls, message: str = "An error occurred", data: Any = None):
        """Create an error response."""
        return cls(success=False, message=message, data=data)


class APIError(HTTPException):
    """Base API error class that extends FastAPI's HTTPException."""
    
    def __init__(
        self, 
        detail: str = "An unexpected error occurred", 
        status_code: int = 500,
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize the API error with detail message and status code."""
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundError(APIError):
    """Resource not found error."""
    
    def __init__(
        self, 
        detail: str = "Resource not found",
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize with 404 status code."""
        super().__init__(status_code=404, detail=detail, headers=headers)


class ValidationError(APIError):
    """Input validation error."""
    
    def __init__(
        self, 
        detail: str = "Invalid input data",
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize with 400 status code."""
        super().__init__(status_code=400, detail=detail, headers=headers)


class AuthenticationError(APIError):
    """Authentication error."""
    
    def __init__(
        self, 
        detail: str = "Authentication failed",
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize with 401 status code."""
        super().__init__(status_code=401, detail=detail, headers=headers)


class AuthorizationError(APIError):
    """Authorization error."""
    
    def __init__(
        self, 
        detail: str = "Insufficient permissions",
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize with 403 status code."""
        super().__init__(status_code=403, detail=detail, headers=headers)


class RateLimitError(APIError):
    """Rate limit exceeded error."""
    
    def __init__(
        self, 
        detail: str = "Rate limit exceeded",
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize with 429 status code."""
        super().__init__(status_code=429, detail=detail, headers=headers)


def create_error_response(error: Union[APIError, Exception]) -> JSONResponse:
    """Create a standardized error response from various error types."""
    if isinstance(error, APIError):
        status_code = error.status_code
        detail = error.detail
    else:
        status_code = 500
        detail = str(error)
    
    return JSONResponse(
        status_code=status_code,
        content=APIResponse.error(message=detail).dict()
    ) 