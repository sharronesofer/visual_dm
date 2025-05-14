"""
JWT token management and authentication.
"""

import jwt
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from flask import current_app

class JWTError(Exception):
    """Base exception for JWT-related errors."""
    pass

class TokenExpiredError(JWTError):
    """Exception raised when token has expired."""
    pass

class InvalidTokenError(JWTError):
    """Exception raised when token is invalid."""
    pass

class JWTManager:
    """JWT token management."""

    def __init__(
        self,
        secret_key: str,
        access_token_expires: int = 3600,  # 1 hour
        refresh_token_expires: int = 2592000,  # 30 days
        algorithm: str = "HS256"
    ) -> None:
        """
        Initialize JWT manager.

        Args:
            secret_key: Secret key for token signing
            access_token_expires: Access token expiration time in seconds
            refresh_token_expires: Refresh token expiration time in seconds
            algorithm: JWT signing algorithm
        """
        self.secret_key = secret_key
        self.access_token_expires = access_token_expires
        self.refresh_token_expires = refresh_token_expires
        self.algorithm = algorithm

    def _create_token(
        self,
        user_id: str,
        token_type: str,
        expires_delta: timedelta,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a JWT token.

        Args:
            user_id: User identifier
            token_type: Type of token (access or refresh)
            expires_delta: Token expiration time
            additional_claims: Additional claims to include in token

        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        claims = {
            "sub": str(user_id),
            "type": token_type,
            "iat": now,
            "exp": now + expires_delta
        }

        if additional_claims:
            claims.update(additional_claims)

        try:
            return jwt.encode(
                claims,
                self.secret_key,
                algorithm=self.algorithm
            )
        except Exception as e:
            current_app.logger.error(f"Failed to create token: {str(e)}")
            raise JWTError("Failed to create token") from e

    def create_access_token(
        self,
        user_id: str,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create an access token.

        Args:
            user_id: User identifier
            additional_claims: Additional claims to include in token

        Returns:
            Access token string
        """
        return self._create_token(
            user_id,
            "access",
            timedelta(seconds=self.access_token_expires),
            additional_claims
        )

    def create_refresh_token(
        self,
        user_id: str,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a refresh token.

        Args:
            user_id: User identifier
            additional_claims: Additional claims to include in token

        Returns:
            Refresh token string
        """
        return self._create_token(
            user_id,
            "refresh",
            timedelta(seconds=self.refresh_token_expires),
            additional_claims
        )

    def create_token_pair(
        self,
        user_id: str,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Create both access and refresh tokens.

        Args:
            user_id: User identifier
            additional_claims: Additional claims to include in tokens

        Returns:
            Tuple of (access_token, refresh_token)
        """
        access_token = self.create_access_token(user_id, additional_claims)
        refresh_token = self.create_refresh_token(user_id, additional_claims)
        return access_token, refresh_token

    def decode_token(
        self,
        token: str,
        verify_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decode and verify a JWT token.

        Args:
            token: JWT token string
            verify_type: Optional token type to verify

        Returns:
            Token claims

        Raises:
            TokenExpiredError: If token has expired
            InvalidTokenError: If token is invalid
        """
        try:
            claims = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Verify token type if specified
            if verify_type and claims.get("type") != verify_type:
                raise InvalidTokenError(
                    f"Invalid token type. Expected {verify_type}"
                )

            return claims

        except jwt.ExpiredSignatureError as e:
            raise TokenExpiredError("Token has expired") from e
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError("Invalid token") from e
        except Exception as e:
            current_app.logger.error(f"Failed to decode token: {str(e)}")
            raise JWTError("Failed to decode token") from e

    def refresh_access_token(
        self,
        refresh_token: str,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new access token using refresh token.

        Args:
            refresh_token: Refresh token string
            additional_claims: Additional claims to include in new token

        Returns:
            New access token string

        Raises:
            TokenExpiredError: If refresh token has expired
            InvalidTokenError: If refresh token is invalid
        """
        claims = self.decode_token(refresh_token, verify_type="refresh")
        
        # Create new access token with original user ID
        return self.create_access_token(
            claims["sub"],
            additional_claims or claims
        )

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return claims.

    Args:
        token: JWT token string

    Returns:
        Token claims

    Raises:
        JWTError: If token is invalid or expired
    """
    jwt_manager: JWTManager = current_app.jwt_manager
    return jwt_manager.decode_token(token, verify_type="access") 