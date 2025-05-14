"""FastAPI-specific API utilities."""

from .errors import (
    APIError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    setup_error_handlers
)
from .response import APIResponse
from .versioning import VersionedAPIRouter

__all__ = [
    'APIError',
    'NotFoundError',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'RateLimitError',
    'setup_error_handlers',
    'APIResponse',
    'VersionedAPIRouter'
] 