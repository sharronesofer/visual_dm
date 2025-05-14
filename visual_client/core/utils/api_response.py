"""
Standardized API response format with consistent error handling.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
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

@dataclass
class APIError:
    """API error information."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class APIResponse:
    """Standardized API response format."""
    status: APIStatus
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    error: Optional[APIError] = None
    timestamp: datetime = datetime.now()
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def success(
        cls,
        data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'APIResponse':
        """Create a success response.
        
        Args:
            data: Response data
            metadata: Additional metadata
            
        Returns:
            APIResponse instance
        """
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
        """Create a resource created response.
        
        Args:
            data: Response data
            metadata: Additional metadata
            
        Returns:
            APIResponse instance
        """
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
        """Create an error response.
        
        Args:
            status: Error status code
            code: Error code
            message: Error message
            details: Additional error details
            
        Returns:
            APIResponse instance
        """
        return cls(
            status=status,
            error=APIError(
                code=code,
                message=message,
                details=details
            )
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary.
        
        Returns:
            Dictionary representation of response
        """
        try:
            response = {
                "status": self.status.value,
                "timestamp": self.timestamp.isoformat()
            }
            
            if self.data is not None:
                response["data"] = self.data
                
            if self.error is not None:
                response["error"] = {
                    "code": self.error.code,
                    "message": self.error.message
                }
                if self.error.details:
                    response["error"]["details"] = self.error.details
                    
            if self.metadata is not None:
                response["metadata"] = self.metadata
                
            return response
            
        except Exception as e:
            handle_component_error(
                "APIResponse",
                "to_dict",
                e,
                ErrorSeverity.ERROR
            )
            return {
                "status": APIStatus.INTERNAL_ERROR.value,
                "timestamp": datetime.now().isoformat(),
                "error": {
                    "code": "internal_error",
                    "message": "Failed to serialize response"
                }
            }
            
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIResponse':
        """Create response from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            APIResponse instance
        """
        try:
            status = APIStatus(data["status"])
            timestamp = datetime.fromisoformat(data["timestamp"])
            
            error = None
            if "error" in data:
                error = APIError(
                    code=data["error"]["code"],
                    message=data["error"]["message"],
                    details=data["error"].get("details")
                )
                
            return cls(
                status=status,
                data=data.get("data"),
                error=error,
                timestamp=timestamp,
                metadata=data.get("metadata")
            )
            
        except Exception as e:
            handle_component_error(
                "APIResponse",
                "from_dict",
                e,
                ErrorSeverity.ERROR
            )
            return cls.error(
                APIStatus.INTERNAL_ERROR,
                "invalid_response",
                "Failed to parse response"
            )
            
    def is_success(self) -> bool:
        """Check if response is successful.
        
        Returns:
            True if successful, False otherwise
        """
        return self.status.value < 400
        
    def is_error(self) -> bool:
        """Check if response is an error.
        
        Returns:
            True if error, False otherwise
        """
        return self.status.value >= 400 