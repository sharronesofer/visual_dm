"""Religion system exceptions"""

from uuid import UUID


class ReligionError(Exception):
    """Base exception for religion system errors"""
    pass


class ReligionNotFoundError(ReligionError):
    """Raised when a religion is not found"""
    
    def __init__(self, religion_id: UUID):
        self.religion_id = religion_id
        super().__init__(f"Religion with ID {religion_id} not found")


class ReligionValidationError(ReligionError):
    """Raised when religion data validation fails"""
    pass


class ReligionConflictError(ReligionError):
    """Raised when there's a conflict with religion operations"""
    pass


class ReligionPermissionError(ReligionError):
    """Raised when user lacks permission for religion operations"""
    pass 