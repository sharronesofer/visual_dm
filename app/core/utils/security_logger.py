"""
Utility for security event logging.
"""

import json
import logging
from datetime import datetime
from flask import request, current_app
from typing import Dict, Any, Optional

# Set up the security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

class SecurityEventLogger:
    """Class for logging security-related events."""
    
    @staticmethod
    def _get_request_context() -> Dict[str, Any]:
        """Get context information from the current request."""
        context = {
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else 'Unknown',
            'referer': request.headers.get('Referer', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path,
            'method': request.method
        }
        
        # Add user info if available
        if hasattr(request, 'user_data'):
            context['user_id'] = request.user_data.get('id')
            context['username'] = request.user_data.get('username')
        
        return context
    
    @classmethod
    def log_event(cls, event_type: str, details: Dict[str, Any], level: str = 'info') -> None:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            details: Additional details about the event
            level: Logging level (info, warning, error)
        """
        context = cls._get_request_context()
        
        event_data = {
            'event_type': event_type,
            'context': context,
            'details': details
        }
        
        # Convert to JSON string for consistent log format
        log_message = json.dumps(event_data)
        
        # Log at the appropriate level
        if level == 'warning':
            security_logger.warning(log_message)
        elif level == 'error':
            security_logger.error(log_message)
        else:
            security_logger.info(log_message)
            
        # Also log to the application logger if in debug mode
        if current_app.debug:
            current_app.logger.debug(f"Security Event: {log_message}")
    
    @classmethod
    def log_rate_limit_event(cls, 
                            limit_type: str, 
                            identifier: str, 
                            attempts: int, 
                            limit: int,
                            window: int,
                            endpoint: Optional[str] = None) -> None:
        """
        Log a rate limit event.
        
        Args:
            limit_type: Type of rate limit (e.g., 'email', 'ip')
            identifier: The identifier that was rate limited (e.g., email or IP)
            attempts: Number of attempts made
            limit: Maximum number of attempts allowed
            window: Time window in seconds
            endpoint: The endpoint that was rate limited
        """
        details = {
            'limit_type': limit_type,
            'identifier': identifier,
            'attempts': attempts,
            'limit': limit,
            'window_seconds': window,
            'endpoint': endpoint or request.path
        }
        
        cls.log_event(
            event_type='rate_limit_exceeded',
            details=details,
            level='warning'
        )
    
    @classmethod
    def log_password_reset_attempt(cls, 
                                  email: str, 
                                  success: bool, 
                                  reason: Optional[str] = None) -> None:
        """
        Log a password reset attempt.
        
        Args:
            email: The email used for password reset
            success: Whether the attempt was successful
            reason: Reason for failure if not successful
        """
        details = {
            'email': email,
            'success': success
        }
        
        if reason:
            details['reason'] = reason
            
        cls.log_event(
            event_type='password_reset_attempt',
            details=details,
            level='info' if success else 'warning'
        ) 