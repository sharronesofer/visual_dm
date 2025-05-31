"""
Religion system exceptions

Custom exceptions for the religion system.
"""

from backend.infrastructure.shared.exceptions import BaseSystemError


class ReligionError(BaseSystemError):
    """Base exception for religion system"""
    pass


class ReligionNotFoundError(ReligionError):
    """Exception raised when a religion is not found"""
    
    def __init__(self, religion_id=None, name=None):
        if religion_id:
            message = f"Religion with ID {religion_id} not found"
        elif name:
            message = f"Religion with name '{name}' not found"
        else:
            message = "Religion not found"
        super().__init__(message)


class ReligionValidationError(ReligionError):
    """Exception raised when religion validation fails"""
    pass


class ReligionConflictError(ReligionError):
    """Exception raised when religion conflicts exist"""
    pass


class ReligionPermissionError(ReligionError):
    """Exception raised when permission is denied for religion operations"""
    pass 