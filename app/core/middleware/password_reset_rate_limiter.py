"""
Rate limiting middleware specifically for password reset requests.
"""

import time
from typing import Tuple, Dict, Optional
from functools import wraps
from flask import request, current_app, jsonify, g
import redis
from app.core.utils.security_logger import SecurityEventLogger

class PasswordResetRateLimiter:
    """Rate limiting implementation for password reset functionality."""
    
    def __init__(self, redis_client):
        """Initialize rate limiter with Redis connection."""
        self.redis = redis_client
        
    def _get_email_key(self, email: str) -> str:
        """Generate a unique key for email-based rate limiting."""
        return f"pwd_reset:email:{email}"
        
    def _get_ip_key(self, ip_address: Optional[str] = None) -> str:
        """Generate a unique key for IP-based rate limiting."""
        ip = ip_address or request.remote_addr or 'unknown'
        return f"pwd_reset:ip:{ip}"
        
    def check_email_rate_limit(self, email: str, max_attempts: int = 3, window: int = 3600) -> Tuple[bool, Dict]:
        """
        Check if the email has exceeded rate limits for password reset requests.
        
        Args:
            email: The email address being used for password reset
            max_attempts: Maximum number of attempts allowed per window (default: 3)
            window: Time window in seconds (default: 3600 - 1 hour)
            
        Returns:
            Tuple of (is_allowed, limit_info):
                is_allowed: True if request is allowed, False if rate limited
                limit_info: Dictionary with rate limit information
        """
        key = self._get_email_key(email)
        current_time = int(time.time())
        
        # Create a pipeline for atomic operations
        pipe = self.redis.pipeline()
        
        # Remove old requests outside the current window
        pipe.zremrangebyscore(key, 0, current_time - window)
        
        # Count requests in the current window
        pipe.zcard(key)
        
        # Add current request timestamp
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiration on the key
        pipe.expire(key, window)
        
        # Execute pipeline
        _, request_count, _, _ = pipe.execute()
        
        # Calculate reset time
        if request_count == 0:
            reset_time = current_time + window
        else:
            # Get oldest request timestamp
            oldest = self.redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                oldest_time = int(oldest[0][1])
                reset_time = oldest_time + window
            else:
                reset_time = current_time + window
                
        # Calculate remaining attempts
        remaining = max(0, max_attempts - request_count)
        
        limit_info = {
            "limit": max_attempts,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": reset_time - current_time
        }
        
        # Check if rate limit exceeded
        is_allowed = request_count < max_attempts
            
        return is_allowed, limit_info
        
    def check_ip_rate_limit(self, ip_address: Optional[str] = None, max_attempts: int = 5, window: int = 3600) -> Tuple[bool, Dict]:
        """
        Check if the IP address has exceeded rate limits for password reset requests.
        
        Args:
            ip_address: The client IP address (uses request.remote_addr if None)
            max_attempts: Maximum number of attempts allowed per window (default: 5)
            window: Time window in seconds (default: 3600 - 1 hour)
            
        Returns:
            Tuple of (is_allowed, limit_info):
                is_allowed: True if request is allowed, False if rate limited
                limit_info: Dictionary with rate limit information
        """
        key = self._get_ip_key(ip_address)
        current_time = int(time.time())
        
        # Create a pipeline for atomic operations
        pipe = self.redis.pipeline()
        
        # Remove old requests outside the current window
        pipe.zremrangebyscore(key, 0, current_time - window)
        
        # Count requests in the current window
        pipe.zcard(key)
        
        # Add current request timestamp
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiration on the key
        pipe.expire(key, window)
        
        # Execute pipeline
        _, request_count, _, _ = pipe.execute()
        
        # Calculate reset time
        if request_count == 0:
            reset_time = current_time + window
        else:
            # Get oldest request timestamp
            oldest = self.redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                oldest_time = int(oldest[0][1])
                reset_time = oldest_time + window
            else:
                reset_time = current_time + window
                
        # Calculate remaining attempts
        remaining = max(0, max_attempts - request_count)
        
        limit_info = {
            "limit": max_attempts,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": reset_time - current_time
        }
        
        # Check if rate limit exceeded
        is_allowed = request_count < max_attempts
            
        return is_allowed, limit_info

def password_reset_rate_limit(f):
    """
    Decorator to apply rate limiting to password reset endpoints.
    
    Limits:
    - 3 attempts per email address per hour
    - 5 attempts per IP address per hour
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Initialize rate limiter if it doesn't exist
        if not hasattr(current_app, 'pwd_reset_limiter'):
            redis_client = redis.from_url(
                current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            )
            current_app.pwd_reset_limiter = PasswordResetRateLimiter(redis_client)
        
        # Get request data
        data = request.get_json(force=True) if request.is_json else {}
        email = data.get('email')
        ip_address = request.remote_addr
        
        # Skip rate limiting if no email provided (invalid request anyway)
        if not email:
            return f(*args, **kwargs)
        
        # Check IP-based rate limit first
        ip_allowed, ip_info = current_app.pwd_reset_limiter.check_ip_rate_limit(
            ip_address=ip_address, 
            max_attempts=5,  # 5 attempts per hour per IP
            window=3600      # 1 hour window
        )
        
        if not ip_allowed:
            # Log the rate limit event
            SecurityEventLogger.log_rate_limit_event(
                limit_type='ip',
                identifier=ip_address,
                attempts=ip_info['limit'] - ip_info['remaining'],
                limit=ip_info['limit'],
                window=3600,
                endpoint=request.path
            )
            
            current_app.logger.warning(f"Password reset rate limit exceeded for IP: {ip_address}")
            # Set rate limit headers
            headers = {
                'X-RateLimit-Limit': str(ip_info['limit']),
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(ip_info['reset']),
                'Retry-After': str(ip_info['retry_after'])
            }
            
            return jsonify({
                'error': 'Too many password reset requests',
                'message': f"Rate limit exceeded. Please try again later.",
                'retry_after': ip_info['retry_after']
            }), 429, headers
            
        # Then check email-based rate limit
        email_allowed, email_info = current_app.pwd_reset_limiter.check_email_rate_limit(
            email=email,
            max_attempts=3,  # 3 attempts per hour per email
            window=3600      # 1 hour window
        )
        
        if not email_allowed:
            # Log the rate limit event
            SecurityEventLogger.log_rate_limit_event(
                limit_type='email',
                identifier=email,
                attempts=email_info['limit'] - email_info['remaining'],
                limit=email_info['limit'],
                window=3600,
                endpoint=request.path
            )
            
            current_app.logger.warning(f"Password reset rate limit exceeded for email: {email}")
            # Set rate limit headers
            headers = {
                'X-RateLimit-Limit': str(email_info['limit']),
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(email_info['reset']),
                'Retry-After': str(email_info['retry_after'])
            }
            
            return jsonify({
                'error': 'Too many password reset requests',
                'message': f"Rate limit exceeded for this account. Please try again later.",
                'retry_after': email_info['retry_after']
            }), 429, headers
        
        # Store rate limit info in g for the view to use
        g.rate_limit_info = {
            'email': email_info,
            'ip': ip_info
        }
        
        # Log successful attempt (close to limit)
        if email_info['remaining'] <= 1 or ip_info['remaining'] <= 1:
            SecurityEventLogger.log_password_reset_attempt(
                email=email,
                success=True,
                reason=f"Approaching rate limit: {email_info['remaining']}/{email_info['limit']} attempts remaining"
            )
        
        # If we get here, request is allowed
        response = f(*args, **kwargs)
        
        # Add rate limit headers to the response
        if isinstance(response, tuple):
            body, status, *rest = response
            headers = rest[0] if rest else {}
            
            # Add the lower of the two remaining values
            remaining = min(email_info['remaining'], ip_info['remaining'])
            reset = max(email_info['reset'], ip_info['reset'])
            
            headers.update({
                'X-RateLimit-Limit': str(email_info['limit']),  # Email limit is more restrictive
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset)
            })
            
            return body, status, headers
        
        return response
    
    return decorated_function 