"""
Unified API response format for all endpoints with comprehensive error handling and pagination support.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field
from enum import Enum

DataT = TypeVar('DataT')

class APIStatus(Enum):
    """API response status codes."""
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503

class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")

class PaginationMetadata(BaseModel):
    """Pagination metadata."""
    page: int = Field(1, description="Current page number")
    per_page: int = Field(20, description="Items per page")
    total_pages: int = Field(1, description="Total number of pages")
    total_items: int = Field(0, description="Total number of items")
    has_next: bool = Field(False, description="Whether there is a next page")
    has_prev: bool = Field(False, description="Whether there is a previous page")
    next_page: Optional[int] = Field(None, description="Next page number if available")
    prev_page: Optional[int] = Field(None, description="Previous page number if available")

class APIResponse(BaseModel, Generic[DataT]):
    """Standard API response format for all endpoints."""
    status: int = Field(..., description="HTTP status code")
    data: Optional[DataT] = Field(None, description="Response data")
    error: Optional[ErrorDetail] = Field(None, description="Error details if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    pagination: Optional[PaginationMetadata] = Field(None, description="Pagination metadata if applicable")

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        
    def is_success(self) -> bool:
        """Check if response indicates success."""
        return 200 <= self.status < 300
        
    def is_error(self) -> bool:
        """Check if response indicates error."""
        return self.status >= 400

    @classmethod
    def success(cls, 
                data: Optional[DataT] = None, 
                status_code: int = APIStatus.SUCCESS.value, 
                metadata: Optional[Dict[str, Any]] = None,
                pagination: Optional[PaginationMetadata] = None) -> 'APIResponse[DataT]':
        """Create a success response."""
        return cls(
            status=status_code,
            data=data,
            metadata=metadata or {},
            pagination=pagination
        )

    @classmethod
    def error(cls,
              message: str, 
              status_code: int = APIStatus.BAD_REQUEST.value, 
              error_code: str = "ERROR",
              details: Optional[Dict[str, Any]] = None,
              request_id: Optional[str] = None,
              metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create an error response."""
        error = ErrorDetail(
            code=error_code,
            message=message,
            details=details,
            request_id=request_id
        )
        return cls(
            status=status_code,
            error=error,
            metadata=metadata or {}
        )

    @classmethod
    def created(cls,
                data: Optional[DataT] = None,
                metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 201 Created response."""
        return cls.success(data, status_code=APIStatus.CREATED.value, metadata=metadata)

    @classmethod
    def accepted(cls,
                message: str = "Request accepted for processing",
                metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 202 Accepted response."""
        return cls.success(
            data={"message": message}, 
            status_code=APIStatus.ACCEPTED.value, 
            metadata=metadata
        )

    @classmethod
    def no_content(cls) -> 'APIResponse[DataT]':
        """Create a 204 No Content response."""
        return cls(status=APIStatus.NO_CONTENT.value)

    @classmethod
    def paginated(cls,
                  data: List[DataT],
                  page: int,
                  per_page: int,
                  total_items: int,
                  metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[List[DataT]]':
        """Create a paginated response."""
        total_pages = (total_items + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        pagination = PaginationMetadata(
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total_items=total_items,
            has_next=has_next,
            has_prev=has_prev,
            next_page=page + 1 if has_next else None,
            prev_page=page - 1 if has_prev else None
        )
        
        return cls.success(
            data=data,
            pagination=pagination,
            metadata=metadata
        )

    @classmethod
    def bad_request(cls,
                   message: str,
                   details: Optional[Dict[str, Any]] = None,
                   request_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 400 Bad Request response."""
        return cls.error(
            message=message,
            status_code=APIStatus.BAD_REQUEST.value,
            error_code="BAD_REQUEST",
            details=details,
            request_id=request_id,
            metadata=metadata
        )

    @classmethod
    def unauthorized(cls,
                    message: str = "Authentication required",
                    request_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 401 Unauthorized response."""
        return cls.error(
            message=message,
            status_code=APIStatus.UNAUTHORIZED.value,
            error_code="UNAUTHORIZED",
            request_id=request_id,
            metadata=metadata
        )

    @classmethod
    def forbidden(cls,
                 message: str = "Permission denied",
                 request_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 403 Forbidden response."""
        return cls.error(
            message=message,
            status_code=APIStatus.FORBIDDEN.value,
            error_code="FORBIDDEN",
            request_id=request_id,
            metadata=metadata
        )

    @classmethod
    def not_found(cls,
                  message: str = "Resource not found",
                  request_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 404 Not Found response."""
        return cls.error(
            message=message,
            status_code=APIStatus.NOT_FOUND.value,
            error_code="NOT_FOUND",
            request_id=request_id,
            metadata=metadata
        )

    @classmethod
    def conflict(cls,
                message: str,
                details: Optional[Dict[str, Any]] = None,
                request_id: Optional[str] = None,
                metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 409 Conflict response."""
        return cls.error(
            message=message,
            status_code=APIStatus.CONFLICT.value,
            error_code="CONFLICT",
            details=details,
            request_id=request_id,
            metadata=metadata
        )

    @classmethod
    def unprocessable_entity(cls,
                           message: str,
                           details: Optional[Dict[str, Any]] = None,
                           request_id: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 422 Unprocessable Entity response."""
        return cls.error(
            message=message,
            status_code=APIStatus.UNPROCESSABLE_ENTITY.value,
            error_code="UNPROCESSABLE_ENTITY",
            details=details,
            request_id=request_id,
            metadata=metadata
        )

    @classmethod
    def too_many_requests(cls,
                         message: str = "Rate limit exceeded",
                         retry_after: Optional[int] = None,
                         request_id: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 429 Too Many Requests response."""
        details = {"retry_after": retry_after} if retry_after is not None else None
        return cls.error(
            message=message,
            status_code=APIStatus.TOO_MANY_REQUESTS.value,
            error_code="TOO_MANY_REQUESTS",
            details=details,
            request_id=request_id,
            metadata=metadata
        )

    @classmethod
    def server_error(cls,
                    message: str = "Internal server error",
                    request_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 500 Internal Server Error response."""
        return cls.error(
            message=message,
            status_code=APIStatus.INTERNAL_ERROR.value,
            error_code="SERVER_ERROR",
            request_id=request_id,
            metadata=metadata
        )

    @classmethod
    def service_unavailable(cls,
                          message: str = "Service temporarily unavailable",
                          retry_after: Optional[int] = None,
                          request_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> 'APIResponse[DataT]':
        """Create a 503 Service Unavailable response."""
        details = {"retry_after": retry_after} if retry_after is not None else None
        return cls.error(
            message=message,
            status_code=APIStatus.SERVICE_UNAVAILABLE.value,
            error_code="SERVICE_UNAVAILABLE",
            details=details,
            request_id=request_id,
            metadata=metadata
        ) 