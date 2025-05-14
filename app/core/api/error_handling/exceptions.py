"""Custom exceptions for the API."""

from typing import Any, Dict, List, Optional
from enum import Enum

class ErrorCode(str, Enum):
    """API error codes."""
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    RATE_LIMITED = "rate_limited"
    INVALID_VERSION = "invalid_version"
    DEPRECATED_VERSION = "deprecated_version"
    INTERNAL_ERROR = "internal_error"
    BAD_REQUEST = "bad_request"
    CONFLICT = "conflict"
    DEPENDENCY_ERROR = "dependency_error"
    INVALID_STATE = "invalid_state"
    RESOURCE_LOCKED = "resource_locked"
    QUOTA_EXCEEDED = "quota_exceeded"

class APIError(Exception):
    """Base exception for API errors."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[List[Dict[str, Any]]] = None,
        status_code: int = 500,
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize API error.
        
        Args:
            code: Error code
            message: Error message
            details: Additional error details
            status_code: HTTP status code
            headers: Additional response headers
        """
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or []
        self.status_code = status_code
        self.headers = headers or {}

class ValidationError(APIError):
    """Validation error."""
    
    def __init__(
        self,
        message: str = "Invalid request parameters",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        """Initialize validation error.
        
        Args:
            message: Error message
            details: Validation error details
        """
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            status_code=400
        )

class NotFoundError(APIError):
    """Resource not found error."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None
    ):
        """Initialize not found error.
        
        Args:
            resource_type: Type of resource not found
            resource_id: ID of resource not found
            message: Custom error message
        """
        message = message or f"{resource_type} with ID {resource_id} not found"
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=message,
            status_code=404
        )

class AlreadyExistsError(APIError):
    """Resource already exists error."""
    
    def __init__(
        self,
        resource_type: str,
        identifier: str,
        message: Optional[str] = None
    ):
        """Initialize already exists error.
        
        Args:
            resource_type: Type of resource
            identifier: Resource identifier
            message: Custom error message
        """
        message = message or f"{resource_type} with identifier {identifier} already exists"
        super().__init__(
            code=ErrorCode.ALREADY_EXISTS,
            message=message,
            status_code=409
        )

class UnauthorizedError(APIError):
    """Unauthorized error."""
    
    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        """Initialize unauthorized error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            details=details,
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"}
        )

class ForbiddenError(APIError):
    """Forbidden error."""
    
    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        """Initialize forbidden error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=message,
            details=details,
            status_code=403
        )

class RateLimitError(APIError):
    """Rate limit exceeded error."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = 60
    ):
        """Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds until retry is allowed
        """
        super().__init__(
            code=ErrorCode.RATE_LIMITED,
            message=message,
            status_code=429,
            headers={"Retry-After": str(retry_after)}
        )

class VersionError(APIError):
    """API version error."""
    
    def __init__(
        self,
        message: str,
        version: str,
        is_deprecated: bool = False
    ):
        """Initialize version error.
        
        Args:
            message: Error message
            version: API version
            is_deprecated: Whether version is deprecated
        """
        code = ErrorCode.DEPRECATED_VERSION if is_deprecated else ErrorCode.INVALID_VERSION
        super().__init__(
            code=code,
            message=message,
            status_code=410 if is_deprecated else 400
        )

class DependencyError(APIError):
    """Dependency error."""
    
    def __init__(
        self,
        message: str,
        dependencies: List[Dict[str, Any]]
    ):
        """Initialize dependency error.
        
        Args:
            message: Error message
            dependencies: List of unmet dependencies
        """
        super().__init__(
            code=ErrorCode.DEPENDENCY_ERROR,
            message=message,
            details=dependencies,
            status_code=424
        )

class InvalidStateError(APIError):
    """Invalid state error."""
    
    def __init__(
        self,
        message: str,
        current_state: str,
        allowed_states: List[str]
    ):
        """Initialize invalid state error.
        
        Args:
            message: Error message
            current_state: Current resource state
            allowed_states: List of allowed states
        """
        super().__init__(
            code=ErrorCode.INVALID_STATE,
            message=message,
            details=[{
                "current_state": current_state,
                "allowed_states": allowed_states
            }],
            status_code=409
        )

class ResourceLockedError(APIError):
    """Resource locked error."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        lock_holder: str,
        message: Optional[str] = None
    ):
        """Initialize resource locked error.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            lock_holder: Entity holding the lock
            message: Custom error message
        """
        message = message or f"{resource_type} {resource_id} is locked by {lock_holder}"
        super().__init__(
            code=ErrorCode.RESOURCE_LOCKED,
            message=message,
            details=[{
                "resource_type": resource_type,
                "resource_id": resource_id,
                "lock_holder": lock_holder
            }],
            status_code=423
        )

class QuotaExceededError(APIError):
    """Quota exceeded error."""
    
    def __init__(
        self,
        quota_type: str,
        current_usage: int,
        limit: int,
        reset_time: Optional[int] = None
    ):
        """Initialize quota exceeded error.
        
        Args:
            quota_type: Type of quota exceeded
            current_usage: Current usage value
            limit: Quota limit
            reset_time: Unix timestamp when quota resets
        """
        message = f"{quota_type} quota exceeded ({current_usage}/{limit})"
        headers = {}
        if reset_time:
            headers["X-RateLimit-Reset"] = str(reset_time)
            
        super().__init__(
            code=ErrorCode.QUOTA_EXCEEDED,
            message=message,
            details=[{
                "quota_type": quota_type,
                "current_usage": current_usage,
                "limit": limit,
                "reset_time": reset_time
            }],
            status_code=429,
            headers=headers
        ) 