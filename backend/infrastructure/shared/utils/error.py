"""Shared error utilities."""

class AuthorizationError(Exception):
    """Authorization error."""

class ValidationError(Exception):
    """Validation error."""

class NotFoundError(Exception):
    """Resource not found error."""

class DatabaseError(Exception):
    """Database operation error."""

class ConfigurationError(Exception):
    """Configuration error."""

class BusinessLogicError(Exception):
    """Business logic validation error."""

class TensionError(Exception):
    """Tension calculation or management error."""

class GenerationError(Exception):
    """World generation or content generation error."""

__all__ = [
    "AuthorizationError",
    "ValidationError", 
    "NotFoundError",
    "DatabaseError",
    "ConfigurationError",
    "BusinessLogicError",
    "TensionError",
    "GenerationError"
]
