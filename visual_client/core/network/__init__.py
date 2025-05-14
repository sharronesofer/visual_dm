"""
Network communication for the Visual DM game client.
"""

from .config import (
    BACKEND_URL,
    ENDPOINTS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
)

__all__ = [
    'BACKEND_URL',
    'ENDPOINTS',
    'REQUEST_TIMEOUT',
    'MAX_RETRIES',
]
