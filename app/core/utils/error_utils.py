"""
Error utilities for managing application errors.
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Exception raised for validation errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class DatabaseError(Exception):
    """Exception raised for database errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(Exception):
    """Exception raised for authentication errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class AuthorizationError(Exception):
    """Exception raised for authorization errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ResourceNotFoundError(Exception):
    """Exception raised when a resource is not found."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class BusinessLogicError(Exception):
    """Exception raised for business logic errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class TensionError(Exception):
    pass

class GenerationError(Exception):
    pass

# Alias for backward compatibility
NotFoundError = ResourceNotFoundError

def handle_error(error: Exception) -> Dict[str, Any]:
    """Handle application errors and return appropriate response."""
    try:
        if isinstance(error, ValidationError):
            logger.warning(f"Validation error: {error.message}")
            return {
                'error': 'validation_error',
                'message': error.message,
                'details': error.details
            }
        elif isinstance(error, DatabaseError):
            logger.error(f"Database error: {error.message}")
            return {
                'error': 'database_error',
                'message': error.message,
                'details': error.details
            }
        elif isinstance(error, AuthenticationError):
            logger.warning(f"Authentication error: {error.message}")
            return {
                'error': 'authentication_error',
                'message': error.message,
                'details': error.details
            }
        elif isinstance(error, AuthorizationError):
            logger.warning(f"Authorization error: {error.message}")
            return {
                'error': 'authorization_error',
                'message': error.message,
                'details': error.details
            }
        elif isinstance(error, ResourceNotFoundError):
            logger.warning(f"Resource not found: {error.message}")
            return {
                'error': 'resource_not_found',
                'message': error.message,
                'details': error.details
            }
        elif isinstance(error, BusinessLogicError):
            logger.error(f"Business logic error: {error.message}")
            return {
                'error': 'business_logic_error',
                'message': error.message,
                'details': error.details
            }
        else:
            logger.error(f"Unexpected error: {str(error)}")
            return {
                'error': 'unexpected_error',
                'message': 'An unexpected error occurred',
                'details': {'original_error': str(error)}
            }
    except Exception as e:
        logger.critical(f"Error handling failed: {str(e)}")
        return {
            'error': 'error_handling_failed',
            'message': 'Failed to handle error',
            'details': {'original_error': str(error), 'handling_error': str(e)}
        } 