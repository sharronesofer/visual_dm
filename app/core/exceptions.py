"""
Custom exceptions for the application.
"""

class BaseError(Exception):
    """Base exception class."""
    def __init__(self, message: str = None):
        self.message = message
        super().__init__(self.message)

class ValidationError(BaseError):
    """Raised when input validation fails."""
    pass

class AuthenticationError(BaseError):
    """Raised when authentication fails."""
    pass

class AuthorizationError(BaseError):
    """Raised when user lacks required permissions."""
    pass

class UserNotFoundError(BaseError):
    """Raised when a user cannot be found."""
    pass

class InvalidTokenError(BaseError):
    """Raised when a token is invalid or expired."""
    pass

class SessionError(BaseError):
    """Raised when there are issues with user sessions."""
    pass

class EmailError(BaseError):
    """Raised when there are issues sending emails."""
    pass

class DatabaseError(BaseError):
    """Raised when database operations fail."""
    pass

class ConfigurationError(BaseError):
    """Raised when there are configuration issues."""
    pass

class VersionControlError(Exception):
    """Exception raised for version control related errors."""
    pass

class FactionNotFoundError(Exception):
    """Raised when a faction cannot be found."""
    pass

class InvalidRelationshipError(Exception):
    """Raised when attempting to create or modify an invalid faction relationship."""
    pass

class DuplicateFactionError(Exception):
    """Raised when attempting to create a faction with a name that already exists."""
    pass

class WorldStateError(Exception):
    """Raised when an error occurs during world state operations."""
    pass 