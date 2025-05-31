"""
Core Error Classes
-----------------
Custom exception classes for the backend systems.
Provides standardized error handling across all backend modules.
"""

from typing import Optional, Any, Dict

class BaseError(Exception):
    """Base exception class for all custom errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.details = details or {}

class ValidationError(BaseError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field
        self.value = value

class NotFoundError(BaseError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, identifier: Any = None, details: Optional[Dict[str, Any]] = None):
        if identifier is not None:
            message = f"{resource} with identifier '{identifier}' not found"
        else:
            message = f"{resource} not found"
        super().__init__(message, "NOT_FOUND", details)
        self.resource = resource
        self.identifier = identifier

class DatabaseError(BaseError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", details)
        self.operation = operation

class AuthorizationError(BaseError):
    """Raised when user lacks permission for an operation."""
    
    def __init__(self, message: str = "Access denied", resource: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", details)
        self.resource = resource

class AuthenticationError(BaseError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)

class ConfigurationError(BaseError):
    """Raised when system configuration is invalid."""
    
    def __init__(self, message: str, setting: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.setting = setting

class ExternalServiceError(BaseError):
    """Raised when external service calls fail."""
    
    def __init__(self, message: str, service: Optional[str] = None, status_code: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)
        self.service = service
        self.status_code = status_code

class BusinessLogicError(BaseError):
    """Raised when business logic rules are violated."""
    
    def __init__(self, message: str, rule: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "BUSINESS_LOGIC_ERROR", details)
        self.rule = rule

class ConcurrencyError(BaseError):
    """Raised when concurrent operations conflict."""
    
    def __init__(self, message: str = "Concurrent modification detected",
                 resource: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONCURRENCY_ERROR", details)
        self.resource = resource

__all__ = [
    "BaseError",
    "ValidationError", 
    "NotFoundError",
    "DatabaseError",
    "AuthorizationError",
    "AuthenticationError",
    "ConfigurationError",
    "ExternalServiceError",
    "BusinessLogicError",
    "ConcurrencyError"
] 