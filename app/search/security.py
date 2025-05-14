"""Security components for search functionality."""

from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta

from app.core.utils.security_utils import verify_token, get_current_user
from app.core.models.user import User
from app.core.middleware.rate_limiter import RateLimiter
from .config import SEARCH_SETTINGS

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "search:read": "Read-only access to search functionality",
        "search:write": "Write access to search functionality (indexing)",
        "search:admin": "Administrative access to search functionality"
    }
)

class SearchPermissions:
    """Search-specific permissions."""
    READ = "search:read"
    WRITE = "search:write"
    ADMIN = "search:admin"

class SearchSecurityError(Exception):
    """Base class for search security errors."""
    pass

class SearchAuthenticationError(SearchSecurityError):
    """Raised when authentication fails."""
    pass

class SearchAuthorizationError(SearchSecurityError):
    """Raised when authorization fails."""
    pass

class SearchRateLimitError(SearchSecurityError):
    """Raised when rate limit is exceeded."""
    pass

class SearchSecurityConfig:
    """Security configuration for search functionality."""
    
    def __init__(self):
        """Initialize security configuration."""
        self.rate_limiter = RateLimiter(
            redis_client=SEARCH_SETTINGS['redis_client'],
            key_prefix="search_rate_limit",
            default_limit=SEARCH_SETTINGS.get('rate_limit', 100),
            default_window=SEARCH_SETTINGS.get('rate_limit_window', 3600)
        )
        
        # Rate limit configurations for different operations
        self.rate_limits = {
            "search": {
                "limit": SEARCH_SETTINGS.get('search_rate_limit', 100),
                "window": SEARCH_SETTINGS.get('search_rate_limit_window', 60)
            },
            "suggest": {
                "limit": SEARCH_SETTINGS.get('suggest_rate_limit', 200),
                "window": SEARCH_SETTINGS.get('suggest_rate_limit_window', 60)
            },
            "index": {
                "limit": SEARCH_SETTINGS.get('index_rate_limit', 50),
                "window": SEARCH_SETTINGS.get('index_rate_limit_window', 3600)
            },
            "bulk": {
                "limit": SEARCH_SETTINGS.get('bulk_rate_limit', 10),
                "window": SEARCH_SETTINGS.get('bulk_rate_limit_window', 3600)
            }
        }

async def get_current_user_permissions(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> List[str]:
    """Get current user's permissions from token.
    
    Args:
        security_scopes: Required security scopes
        token: JWT token
        
    Returns:
        List of permission strings
        
    Raises:
        HTTPException: If authentication fails
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # Verify token and get user
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
            
        # Get permissions from token
        permissions = payload.get("permissions", [])
        
        # Check required scopes
        for scope in security_scopes.scopes:
            if scope not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
                
        return permissions
        
    except (JWTError, ValidationError):
        raise credentials_exception

def check_search_permissions(required_permissions: List[str]):
    """Decorator to check search permissions.
    
    Args:
        required_permissions: List of required permissions
        
    Returns:
        Dependency callable
    """
    async def check_permissions(
        permissions: List[str] = Depends(get_current_user_permissions)
    ) -> bool:
        for permission in required_permissions:
            if permission not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission}"
                )
        return True
    return check_permissions

class SearchRateLimiter:
    """Rate limiter for search operations."""
    
    def __init__(self, operation: str):
        """Initialize rate limiter for specific operation."""
        self.operation = operation
        self.config = SearchSecurityConfig()
        
    async def check_rate_limit(
        self,
        user: User = Depends(get_current_user)
    ) -> bool:
        """Check if request is within rate limits.
        
        Args:
            user: Current user
            
        Returns:
            True if request is allowed
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        rate_limit = self.config.rate_limits[self.operation]
        
        # Get rate limit key based on user ID or IP
        identifier = f"{self.operation}:{user.id if user else 'anonymous'}"
        
        is_limited, headers = self.config.rate_limiter.is_rate_limited(
            identifier,
            rate_limit['limit'],
            rate_limit['window']
        )
        
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    **headers,
                    "Retry-After": str(rate_limit['window'])
                }
            )
            
        return True

# Dependency instances for different operations
search_rate_limiter = SearchRateLimiter("search")
suggest_rate_limiter = SearchRateLimiter("suggest")
index_rate_limiter = SearchRateLimiter("index")
bulk_rate_limiter = SearchRateLimiter("bulk")

# Permission check dependencies
require_search_read = check_search_permissions([SearchPermissions.READ])
require_search_write = check_search_permissions([SearchPermissions.WRITE])
require_search_admin = check_search_permissions([SearchPermissions.ADMIN]) 