"""Custom exceptions for the Visual DM application."""

class InvalidUsage(Exception):
    """Exception raised for invalid usage of application features.
    
    Attributes:
        message -- explanation of the error
        status_code -- HTTP status code
    """
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(Exception):
    """Exception raised for authentication related errors.
    
    Attributes:
        message -- explanation of the error
        status_code -- HTTP status code
    """
    def __init__(self, message, status_code=401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ResourceNotFound(Exception):
    """Exception raised when a requested resource is not found.
    
    Attributes:
        message -- explanation of the error
        status_code -- HTTP status code
    """
    def __init__(self, message, status_code=404):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(Exception):
    """Exception raised for validation errors.
    
    Attributes:
        message -- explanation of the error
        status_code -- HTTP status code
    """
    def __init__(self, message, status_code=422):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseError(Exception):
    """Exception raised for database related errors.
    
    Attributes:
        message -- explanation of the error
        status_code -- HTTP status code
    """
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ExternalServiceError(Exception):
    """Exception raised for errors from external services (Firebase, OpenAI, etc).
    
    Attributes:
        message -- explanation of the error
        status_code -- HTTP status code
    """
    def __init__(self, message, status_code=503):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message) 