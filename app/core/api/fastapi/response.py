"""FastAPI response models."""

from datetime import datetime
from typing import Any, Dict, Generic, Optional, TypeVar, Union
from pydantic import BaseModel, Field

DataT = TypeVar('DataT')

class APIResponse(BaseModel, Generic[DataT]):
    """Standard API response format for all endpoints."""
    status: int = Field(..., description="HTTP status code")
    data: Optional[DataT] = Field(None, description="Response data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

    @classmethod
    def success(cls, data: Optional[DataT] = None, 
                status_code: int = 200, 
                metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a success response."""
        return cls(
            status=status_code,
            data=data,
            metadata=metadata or {}
        )

    @classmethod
    def error(cls, message: str, 
              status_code: int = 400, 
              error_code: Optional[str] = None,
              details: Optional[Dict[str, Any]] = None,
              metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create an error response."""
        error = {
            "message": message,
            "code": error_code or "ERROR",
        }
        if details:
            error["details"] = details
            
        return cls(
            status=status_code,
            error=error,
            metadata=metadata or {}
        )

    @classmethod
    def created(cls, data: Optional[DataT] = None,
                metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 201 Created response."""
        return cls.success(data, status_code=201, metadata=metadata)

    @classmethod
    def not_found(cls, message: str = "Resource not found",
                  metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 404 Not Found response."""
        return cls.error(message, status_code=404, error_code="NOT_FOUND", metadata=metadata)

    @classmethod
    def bad_request(cls, message: str,
                   details: Optional[Dict[str, Any]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 400 Bad Request response."""
        return cls.error(message, status_code=400, error_code="BAD_REQUEST", details=details, metadata=metadata)

    @classmethod
    def unauthorized(cls, message: str = "Authentication required",
                    metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 401 Unauthorized response."""
        return cls.error(message, status_code=401, error_code="UNAUTHORIZED", metadata=metadata)

    @classmethod
    def forbidden(cls, message: str = "Permission denied",
                 metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 403 Forbidden response."""
        return cls.error(message, status_code=403, error_code="FORBIDDEN", metadata=metadata)

    @classmethod
    def conflict(cls, message: str,
                details: Optional[Dict[str, Any]] = None,
                metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 409 Conflict response."""
        return cls.error(message, status_code=409, error_code="CONFLICT", details=details, metadata=metadata)

    @classmethod
    def server_error(cls, message: str = "Internal server error",
                    metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 500 Internal Server Error response."""
        return cls.error(message, status_code=500, error_code="SERVER_ERROR", metadata=metadata) 