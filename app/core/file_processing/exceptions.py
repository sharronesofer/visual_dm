"""Custom exceptions for the concurrent file processing system."""

class FileProcessingError(Exception):
    """Base exception for all file processing errors."""
    pass

class FileOperationError(FileProcessingError):
    """Exception raised when a file operation fails."""
    def __init__(self, operation_type, path, message, cause=None):
        self.operation_type = operation_type
        self.path = path
        self.cause = cause
        super().__init__(f"{operation_type} operation failed for {path}: {message}")

class QueueFullError(FileProcessingError):
    """Exception raised when operation queue is full."""
    pass

class InvalidOperationError(FileProcessingError):
    """Exception raised when operation parameters are invalid."""
    pass

class OperationCancelledError(FileProcessingError):
    """Exception raised when an operation is cancelled."""
    pass

class OperationTimeoutError(FileProcessingError):
    """Exception raised when an operation times out."""
    pass

class RetryExhaustedError(FileProcessingError):
    """Exception raised when all retry attempts are exhausted."""
    def __init__(self, operation_id, max_retries, last_error=None):
        self.operation_id = operation_id
        self.max_retries = max_retries
        self.last_error = last_error
        super().__init__(
            f"Operation {operation_id} failed after {max_retries} retries. "
            f"Last error: {last_error}"
        ) 