"""
Shared Exceptions Module

This module provides common exception classes used across all systems.
"""


class BaseSystemError(Exception):
    """Base exception for all system errors"""
    pass


class NotFoundError(BaseSystemError):
    """Base exception for not found errors"""
    pass


class ValidationError(BaseSystemError):
    """Base exception for validation errors"""
    pass


class ConflictError(BaseSystemError):
    """Base exception for conflict errors"""
    pass


# Shared System Exceptions
class SharedNotFoundError(NotFoundError):
    """Exception raised when Shared entity is not found"""
    pass


class SharedValidationError(ValidationError):
    """Exception raised when Shared validation fails"""
    pass


class SharedConflictError(ConflictError):
    """Exception raised when Shared conflicts occur"""
    pass


# NPC System Exceptions
class NpcNotFoundError(NotFoundError):
    """Exception raised when NPC is not found"""
    pass


class NpcValidationError(ValidationError):
    """Exception raised when NPC validation fails"""
    pass


class NpcConflictError(ConflictError):
    """Exception raised when NPC conflicts occur"""
    pass


# Character System Exceptions
class CharacterNotFoundError(NotFoundError):
    """Exception raised when Character is not found"""
    pass


class CharacterValidationError(ValidationError):
    """Exception raised when Character validation fails"""
    pass


class CharacterConflictError(ConflictError):
    """Exception raised when Character conflicts occur"""
    pass


# Religion System Exceptions
class ReligionNotFoundError(NotFoundError):
    """Exception raised when Religion is not found"""
    pass


class ReligionValidationError(ValidationError):
    """Exception raised when Religion validation fails"""
    pass


class ReligionConflictError(ConflictError):
    """Exception raised when Religion conflicts occur"""
    pass


# Add more system-specific exceptions as needed
__all__ = [
    "BaseSystemError",
    "NotFoundError", 
    "ValidationError",
    "ConflictError",
    "SharedNotFoundError",
    "SharedValidationError",
    "SharedConflictError",
    "NpcNotFoundError",
    "NpcValidationError", 
    "NpcConflictError",
    "CharacterNotFoundError",
    "CharacterValidationError",
    "CharacterConflictError",
    "ReligionNotFoundError",
    "ReligionValidationError",
    "ReligionConflictError"
] 