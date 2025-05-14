"""
Standardized API response format and error handling utilities.
"""

import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from flask import jsonify
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

class APIStatus(Enum):
    """API response status codes."""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503

class ErrorCode(Enum):
    """Standard error codes for API responses."""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_CONFLICT = "resource_conflict"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INVALID_REQUEST = "invalid_request"
    DATABASE_ERROR = "database_error"

@dataclass
class APIError:
    """API error information."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        error_dict = {
            "code": self.code,
            "message": self.message
        }
        if self.details:
            error_dict["details"] = self.details
        return error_dict

class APIResponse:
    """Standardized API response format."""
    
    def __init__(
        self,
        status: APIStatus,
        data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        error: Optional[APIError] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize API response.
        
        Args:
            status: Response status code
            data: Response data (for successful responses)
            error: Error information (for error responses)
            metadata: Additional metadata
        """
        self.status = status
        self.data = data
        self.error = error
        self.timestamp = datetime.utcnow()
        self.metadata = metadata or {}

    @classmethod
    def success(
        cls,
        data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'APIResponse':
        """Create a success response."""
        return cls(
            status=APIStatus.SUCCESS,
            data=data,
            metadata=metadata
        )

    @classmethod
    def created(
        cls,
        data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'APIResponse':
        """Create a resource created response."""
        return cls(
            status=APIStatus.CREATED,
            data=data,
            metadata=metadata
        )

    @classmethod
    def error(
        cls,
        status: APIStatus,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> 'APIResponse':
        """Create an error response."""
        return cls(
            status=status,
            error=APIError(
                code=code,
                message=message,
                details=details
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format."""
        try:
            response = {
                "status": self.status.value,
                "timestamp": self.timestamp.isoformat()
            }

            if self.data is not None:
                response["data"] = self.data

            if self.error is not None:
                response["error"] = self.error.to_dict()

            if self.metadata:
                response["metadata"] = self.metadata

            return response

        except Exception as e:
            logger.error(f"Failed to serialize response: {str(e)}")
            return {
                "status": APIStatus.INTERNAL_ERROR.value,
                "timestamp": datetime.utcnow().isoformat(),
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR.value,
                    "message": "Failed to serialize response"
                }
            }

    def to_response(self) -> Any:
        """Convert to Flask response with appropriate status code."""
        return jsonify(self.to_dict()), self.status.value

def create_validation_error(
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> APIResponse:
    """Create a validation error response."""
    return APIResponse.error(
        status=APIStatus.BAD_REQUEST,
        code=ErrorCode.VALIDATION_ERROR.value,
        message=message,
        details=details
    )

def create_not_found_error(
    resource_type: str,
    resource_id: str
) -> APIResponse:
    """Create a not found error response."""
    return APIResponse.error(
        status=APIStatus.NOT_FOUND,
        code=ErrorCode.RESOURCE_NOT_FOUND.value,
        message=f"{resource_type} with id '{resource_id}' not found",
        details={"resource_type": resource_type, "resource_id": resource_id}
    )

def create_unauthorized_error(
    message: str = "Authentication required"
) -> APIResponse:
    """Create an unauthorized error response."""
    return APIResponse.error(
        status=APIStatus.UNAUTHORIZED,
        code=ErrorCode.AUTHENTICATION_ERROR.value,
        message=message
    )

def create_forbidden_error(
    message: str = "Insufficient permissions"
) -> APIResponse:
    """Create a forbidden error response."""
    return APIResponse.error(
        status=APIStatus.FORBIDDEN,
        code=ErrorCode.AUTHORIZATION_ERROR.value,
        message=message
    )

def create_conflict_error(
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> APIResponse:
    """Create a conflict error response."""
    return APIResponse.error(
        status=APIStatus.CONFLICT,
        code=ErrorCode.RESOURCE_CONFLICT.value,
        message=message,
        details=details
    )

def create_rate_limit_error(
    message: str = "Rate limit exceeded"
) -> APIResponse:
    """Create a rate limit exceeded error response."""
    return APIResponse.error(
        status=APIStatus.TOO_MANY_REQUESTS,
        code=ErrorCode.RATE_LIMIT_EXCEEDED.value,
        message=message
    )

def create_internal_error(
    message: str = "An unexpected error occurred",
    details: Optional[Dict[str, Any]] = None
) -> APIResponse:
    """Create an internal server error response."""
    return APIResponse.error(
        status=APIStatus.INTERNAL_ERROR,
        code=ErrorCode.INTERNAL_ERROR.value,
        message=message,
        details=details
    ) 