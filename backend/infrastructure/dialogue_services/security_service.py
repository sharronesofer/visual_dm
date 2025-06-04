"""
Dialogue System Security Service

This module provides comprehensive security services for the dialogue system including
JWT token validation, rate limiting, authorization, and content sanitization.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
import jwt
import bleach
from collections import defaultdict, deque

from backend.infrastructure.shared.exceptions import (
    DialogueSecurityError,
    DialogueRateLimitError,
    DialogueAuthorizationError
)

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Configuration for dialogue security settings"""
    
    def __init__(self):
        self.jwt_secret_key = "your-secret-key"  # Should be from environment
        self.jwt_algorithm = "HS256"
        self.jwt_expiration_hours = 24
        
        # Rate limiting settings
        self.rate_limit_requests_per_minute = 60
        self.rate_limit_window_minutes = 1
        self.rate_limit_burst_allowance = 10
        
        # Content security settings
        self.max_message_length = 2000
        self.allowed_html_tags = []  # No HTML allowed in messages
        self.blocked_content_patterns = [
            # Add patterns for inappropriate content
        ]
        
        # WebSocket security settings
        self.max_connections_per_user = 5
        self.connection_timeout_minutes = 30


class RateLimiter:
    """Rate limiting service for dialogue interactions"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.user_requests: Dict[str, deque] = defaultdict(deque)
        self.user_connections: Dict[str, List[str]] = defaultdict(list)
    
    def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user is within rate limits
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: True if within limits, False if rate limited
        """
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.config.rate_limit_window_minutes)
        
        # Clean old requests
        user_queue = self.user_requests[user_id]
        while user_queue and user_queue[0] < window_start:
            user_queue.popleft()
        
        # Check if under limit
        if len(user_queue) >= self.config.rate_limit_requests_per_minute:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False
        
        # Add current request
        user_queue.append(now)
        return True
    
    def check_connection_limit(self, user_id: str, connection_id: str) -> bool:
        """
        Check if user is within connection limits
        
        Args:
            user_id: User identifier
            connection_id: WebSocket connection identifier
            
        Returns:
            bool: True if within limits, False if too many connections
        """
        connections = self.user_connections[user_id]
        
        # Remove the connection if it already exists (reconnection)
        if connection_id in connections:
            connections.remove(connection_id)
        
        # Check connection limit
        if len(connections) >= self.config.max_connections_per_user:
            logger.warning(f"Connection limit exceeded for user {user_id}")
            return False
        
        # Add connection
        connections.append(connection_id)
        return True
    
    def remove_connection(self, user_id: str, connection_id: str):
        """Remove a connection from tracking"""
        if user_id in self.user_connections:
            connections = self.user_connections[user_id]
            if connection_id in connections:
                connections.remove(connection_id)


class ContentSanitizer:
    """Content sanitization and validation service"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def sanitize_message_content(self, content: str) -> str:
        """
        Sanitize message content
        
        Args:
            content: Raw message content
            
        Returns:
            str: Sanitized content
            
        Raises:
            DialogueSecurityError: If content violates security policies
        """
        if not content or not isinstance(content, str):
            raise DialogueSecurityError("Invalid message content")
        
        # Check length limits
        if len(content) > self.config.max_message_length:
            raise DialogueSecurityError(f"Message exceeds maximum length of {self.config.max_message_length}")
        
        # Remove HTML tags
        sanitized = bleach.clean(content, tags=self.config.allowed_html_tags, strip=True)
        
        # Check for blocked patterns
        content_lower = sanitized.lower()
        for pattern in self.config.blocked_content_patterns:
            if pattern in content_lower:
                logger.warning(f"Blocked content pattern detected: {pattern}")
                raise DialogueSecurityError("Message content violates security policies")
        
        return sanitized.strip()
    
    def validate_conversation_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize conversation data
        
        Args:
            data: Raw conversation data
            
        Returns:
            Dict[str, Any]: Validated and sanitized data
        """
        validated = {}
        
        # Validate required fields
        required_fields = ['player_id', 'npc_id']
        for field in required_fields:
            if field not in data:
                raise DialogueSecurityError(f"Missing required field: {field}")
            validated[field] = str(data[field])
        
        # Validate optional fields
        if 'interaction_type' in data:
            interaction_type = str(data['interaction_type']).lower()
            allowed_types = ['casual', 'trading', 'quest', 'combat', 'information']
            if interaction_type not in allowed_types:
                raise DialogueSecurityError(f"Invalid interaction type: {interaction_type}")
            validated['interaction_type'] = interaction_type
        
        # Sanitize context data
        if 'context' in data and isinstance(data['context'], dict):
            validated['context'] = self._sanitize_context_data(data['context'])
        
        return validated
    
    def _sanitize_context_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize context data recursively"""
        sanitized = {}
        
        for key, value in context.items():
            if isinstance(value, str):
                # Sanitize string values
                sanitized[key] = bleach.clean(value, tags=[], strip=True)[:500]  # Limit length
            elif isinstance(value, (int, float, bool)):
                # Allow basic types
                sanitized[key] = value
            elif isinstance(value, dict):
                # Recursively sanitize nested dicts
                sanitized[key] = self._sanitize_context_data(value)
            elif isinstance(value, list):
                # Sanitize lists (limited depth)
                sanitized[key] = [item for item in value if isinstance(item, (str, int, float, bool))][:10]
        
        return sanitized


class JWTTokenValidator:
    """JWT token validation service"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Dict[str, Any]: Decoded token payload
            
        Raises:
            DialogueAuthorizationError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.config.jwt_secret_key,
                algorithms=[self.config.jwt_algorithm]
            )
            
            # Check expiration
            if 'exp' in payload:
                exp_timestamp = payload['exp']
                if datetime.utcnow().timestamp() > exp_timestamp:
                    raise DialogueAuthorizationError("Token has expired")
            
            # Validate required claims
            required_claims = ['user_id', 'iat']
            for claim in required_claims:
                if claim not in payload:
                    raise DialogueAuthorizationError(f"Missing required claim: {claim}")
            
            return payload
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {str(e)}")
            raise DialogueAuthorizationError("Invalid authentication token")
    
    def extract_token_from_headers(self, headers: Dict[str, str]) -> Optional[str]:
        """
        Extract JWT token from headers
        
        Args:
            headers: Request headers
            
        Returns:
            Optional[str]: JWT token if found
        """
        auth_header = headers.get('Authorization') or headers.get('authorization')
        if not auth_header:
            return None
        
        # Expect "Bearer <token>" format
        parts = auth_header.split(' ')
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]


class AuthorizationService:
    """Authorization service for dialogue interactions"""
    
    def __init__(self):
        self.user_permissions_cache: Dict[str, Dict[str, Any]] = {}
    
    async def check_conversation_permission(
        self, 
        user_id: str, 
        npc_id: str, 
        interaction_type: str = 'casual'
    ) -> bool:
        """
        Check if user has permission to interact with NPC
        
        Args:
            user_id: User identifier
            npc_id: NPC identifier
            interaction_type: Type of interaction
            
        Returns:
            bool: True if authorized
        """
        # TODO: Implement actual permission checking logic
        # This could involve:
        # - Checking faction relationships
        # - Verifying quest requirements
        # - Checking location access
        # - Validating character level/status
        
        # For now, return True (implement actual logic based on game rules)
        logger.info(f"Checking conversation permission for user {user_id} with NPC {npc_id}")
        return True
    
    async def check_npc_availability(self, npc_id: str) -> bool:
        """
        Check if NPC is available for conversation
        
        Args:
            npc_id: NPC identifier
            
        Returns:
            bool: True if available
        """
        # TODO: Implement NPC availability checking
        # This could involve:
        # - Checking if NPC is alive
        # - Verifying location proximity
        # - Checking time-based availability
        # - Validating quest states
        
        logger.info(f"Checking NPC availability for {npc_id}")
        return True


class DialogueSecurityService:
    """Main security service for dialogue system"""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.rate_limiter = RateLimiter(self.config)
        self.content_sanitizer = ContentSanitizer(self.config)
        self.token_validator = JWTTokenValidator(self.config)
        self.authorization_service = AuthorizationService()
    
    async def validate_websocket_connection(
        self, 
        headers: Dict[str, str],
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Validate WebSocket connection for security
        
        Args:
            headers: Connection headers
            connection_id: WebSocket connection identifier
            
        Returns:
            Dict[str, Any]: User context if valid
            
        Raises:
            DialogueAuthorizationError: If authentication fails
            DialogueRateLimitError: If rate limited
        """
        # Extract and validate JWT token
        token = self.token_validator.extract_token_from_headers(headers)
        if not token:
            raise DialogueAuthorizationError("Missing authentication token")
        
        user_payload = self.token_validator.validate_token(token)
        user_id = user_payload['user_id']
        
        # Check rate limits
        if not self.rate_limiter.check_rate_limit(user_id):
            raise DialogueRateLimitError("Rate limit exceeded")
        
        # Check connection limits
        if not self.rate_limiter.check_connection_limit(user_id, connection_id):
            raise DialogueRateLimitError("Too many connections")
        
        logger.info(f"WebSocket connection validated for user {user_id}")
        return {
            'user_id': user_id,
            'user_payload': user_payload,
            'connection_id': connection_id
        }
    
    async def validate_message_security(
        self, 
        user_id: str,
        message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate message for security compliance
        
        Args:
            user_id: User sending the message
            message_data: Raw message data
            
        Returns:
            Dict[str, Any]: Validated and sanitized message data
        """
        # Check rate limits
        if not self.rate_limiter.check_rate_limit(user_id):
            raise DialogueRateLimitError("Message rate limit exceeded")
        
        # Sanitize content
        if 'content' in message_data:
            message_data['content'] = self.content_sanitizer.sanitize_message_content(
                message_data['content']
            )
        
        # Validate conversation data
        validated_data = self.content_sanitizer.validate_conversation_data(message_data)
        
        # Check conversation permissions
        if 'npc_id' in validated_data:
            authorized = await self.authorization_service.check_conversation_permission(
                user_id=user_id,
                npc_id=validated_data['npc_id'],
                interaction_type=validated_data.get('interaction_type', 'casual')
            )
            if not authorized:
                raise DialogueAuthorizationError("Not authorized to interact with this NPC")
        
        return validated_data
    
    def cleanup_connection(self, user_id: str, connection_id: str):
        """Clean up connection tracking"""
        self.rate_limiter.remove_connection(user_id, connection_id)


def create_dialogue_security_service(config: Optional[SecurityConfig] = None) -> DialogueSecurityService:
    """Factory function to create dialogue security service"""
    return DialogueSecurityService(config) 