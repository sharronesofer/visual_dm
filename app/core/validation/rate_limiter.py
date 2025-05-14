"""
Rate limiter for user actions.
"""

from functools import wraps
from typing import Dict, List, Optional, Union, Callable
import time
from datetime import datetime, timedelta
from flask import request, jsonify, current_app, g
from app.core.api.error_handling.exceptions import RateLimitError

class RateLimiter:
    """Rate limiter for user actions."""
    
    def __init__(self):
        """Initialize rate limiter."""
        # Maps user_id -> action_type -> List[timestamp]
        self._request_history: Dict[str, Dict[str, List[float]]] = {}
        # Maps action_type -> (requests_allowed, period_seconds)
        self._limits: Dict[str, tuple] = {}
    
    def add_limit(self, action_type: str, max_requests: int, period_seconds: int) -> None:
        """Add a rate limit for an action type.
        
        Args:
            action_type: Type of action to limit
            max_requests: Maximum number of requests allowed in period
            period_seconds: Period in seconds for the limit
        """
        self._limits[action_type] = (max_requests, period_seconds)
    
    def is_rate_limited(self, user_id: str, action_type: str) -> tuple:
        """Check if a user is rate limited for an action type.
        
        Args:
            user_id: User ID
            action_type: Type of action to check
            
        Returns:
            Tuple of (is_limited, retry_after_seconds)
        """
        if action_type not in self._limits:
            return False, 0
        
        max_requests, period_seconds = self._limits[action_type]
        now = time.time()
        
        # Initialize history for user and action if needed
        if user_id not in self._request_history:
            self._request_history[user_id] = {}
        if action_type not in self._request_history[user_id]:
            self._request_history[user_id][action_type] = []
        
        # Get request history for user and action
        history = self._request_history[user_id][action_type]
        
        # Remove timestamps outside the period
        period_start = now - period_seconds
        history = [ts for ts in history if ts >= period_start]
        self._request_history[user_id][action_type] = history
        
        # Check if user has exceeded the limit
        if len(history) >= max_requests:
            # Calculate when the oldest request will expire
            oldest_request = min(history) if history else now
            retry_after = int(oldest_request + period_seconds - now) + 1
            return True, retry_after
        
        # User is not rate limited, add current timestamp to history
        history.append(now)
        return False, 0
    
    def clear_history(self, user_id: Optional[str] = None) -> None:
        """Clear request history.
        
        Args:
            user_id: User ID to clear history for, or None to clear all history
        """
        if user_id is None:
            self._request_history.clear()
        elif user_id in self._request_history:
            del self._request_history[user_id]

# Global rate limiter instance
rate_limiter = RateLimiter()

# Configure default limits
rate_limiter.add_limit('default', 60, 60)  # 60 requests per minute
rate_limiter.add_limit('auth', 10, 60)  # 10 auth requests per minute
rate_limiter.add_limit('movement', 20, 10)  # 20 movement requests per 10 seconds
rate_limiter.add_limit('combat', 15, 10)  # 15 combat requests per 10 seconds
rate_limiter.add_limit('purchase', 10, 60)  # 10 purchase requests per minute

def rate_limit(action_type: str = 'default'):
    """
    Decorator for rate limiting request handlers.
    
    Args:
        action_type: Type of action to rate limit
        
    Returns:
        Decorated function
    
    Usage:
        @app.route('/resources', methods=['GET'])
        @rate_limit('resource_list')
        def list_resources():
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Get user ID from context
                user_id = str(g.current_user.id) if hasattr(g, 'current_user') and g.current_user else request.remote_addr
                
                # Check if user is rate limited
                is_limited, retry_after = rate_limiter.is_rate_limited(user_id, action_type)
                if is_limited:
                    raise RateLimitError(retry_after=retry_after)
                
                return f(*args, **kwargs)
                
            except RateLimitError as e:
                current_app.logger.warning(f"Rate limit exceeded for {action_type}: {user_id}")
                return jsonify({
                    "error": e.code,
                    "message": e.message
                }), e.status_code, e.headers
                
            except Exception as e:
                current_app.logger.error(f"Rate limiting error: {str(e)}")
                return jsonify({
                    "error": "internal_error",
                    "message": "An error occurred while checking rate limits"
                }), 500
        
        return decorated
    return decorator

def dynamic_rate_limit(
    action_type_fn: Callable[[], str],
    get_user_id_fn: Optional[Callable[[], str]] = None
):
    """
    Decorator for dynamically rate limiting request handlers based on request data.
    
    Args:
        action_type_fn: Function that returns the action type based on request data
        get_user_id_fn: Optional function that returns the user ID (defaults to g.current_user.id)
        
    Returns:
        Decorated function
    
    Usage:
        @app.route('/resources/<resource_type>', methods=['GET'])
        @dynamic_rate_limit(lambda: f"resource_list_{request.view_args['resource_type']}")
        def list_resources(resource_type):
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Get action type and user ID
                action_type = action_type_fn()
                user_id = get_user_id_fn() if get_user_id_fn else (
                    str(g.current_user.id) if hasattr(g, 'current_user') and g.current_user else request.remote_addr
                )
                
                # Get rate limit for action type or use default
                if action_type not in rate_limiter._limits:
                    action_type = 'default'
                
                # Check if user is rate limited
                is_limited, retry_after = rate_limiter.is_rate_limited(user_id, action_type)
                if is_limited:
                    raise RateLimitError(retry_after=retry_after)
                
                return f(*args, **kwargs)
                
            except RateLimitError as e:
                current_app.logger.warning(f"Rate limit exceeded for {action_type}: {user_id}")
                return jsonify({
                    "error": e.code,
                    "message": e.message
                }), e.status_code, e.headers
                
            except Exception as e:
                current_app.logger.error(f"Rate limiting error: {str(e)}")
                return jsonify({
                    "error": "internal_error",
                    "message": "An error occurred while checking rate limits"
                }), 500
        
        return decorated
    return decorator 