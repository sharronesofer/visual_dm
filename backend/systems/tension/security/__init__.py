"""
Tension System Security Module

Provides security features for the tension system including:
- Authentication and authorization
- Role-based access control (RBAC)
- Rate limiting and throttling
- Audit logging
- Input validation and sanitization
- API key management

This module ensures secure access to tension system APIs and data.
"""

from .auth import TensionAuthManager, require_permission, require_role
from .rate_limiting import TensionRateLimiter, rate_limit
from .audit import TensionAuditLogger
from .validation import TensionValidator, validate_input

__all__ = [
    'TensionAuthManager',
    'require_permission',
    'require_role',
    'TensionRateLimiter', 
    'rate_limit',
    'TensionAuditLogger',
    'TensionValidator',
    'validate_input'
] 