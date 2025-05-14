"""
Authentication service for user registration, login, and session management.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from uuid import uuid4
from flask import current_app
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from app.core.database import db
from app.core.models.user import User
from app.core.models.session import Session
from app.core.models.role import Role
from app.core.utils.email import send_verification_email, send_password_reset_email
from app.core.utils.security import generate_token
from app.core.exceptions import (
    AuthenticationError,
    ValidationError,
    UserNotFoundError,
    InvalidTokenError
)

class AuthService:
    """Service for handling user authentication and session management."""
    
    @staticmethod
    def register_user(
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role_name: str = 'user'
    ) -> User:
        """
        Register a new user.
        
        Args:
            username: Unique username
            email: User's email address
            password: User's password
            first_name: Optional first name
            last_name: Optional last name
            role_name: Role name (default: 'user')
            
        Returns:
            Newly created User object
            
        Raises:
            ValidationError: If username or email already exists
        """
        try:
            # Get default role
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                raise ValidationError(f"Role '{role_name}' does not exist")
            
            # Create verification token
            verification_token = generate_token()
            
            # Create user
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                verification_token=verification_token
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Send verification email
            send_verification_email(user.email, verification_token)
            
            return user
            
        except IntegrityError as e:
            db.session.rollback()
            if 'username' in str(e):
                raise ValidationError("Username already exists")
            if 'email' in str(e):
                raise ValidationError("Email already exists")
            raise ValidationError("Failed to create user")
    
    @staticmethod
    def authenticate_user(
        username_or_email: str,
        password: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[User, Session]:
        """
        Authenticate a user and create a new session.
        
        Args:
            username_or_email: Username or email to authenticate
            password: User's password
            device_info: Optional device information
            ip_address: Optional IP address
            
        Returns:
            Tuple of (User, Session)
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Find user
        user = User.query.filter(
            (User.username == username_or_email) |
            (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            raise AuthenticationError("Invalid username/email or password")
        
        if not user.is_active:
            raise AuthenticationError("Account is inactive")
        
        # Create session
        session_token = str(uuid4())
        session = Session(
            user=user,
            token=session_token,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        # Update user's last login
        user.update_last_login()
        
        db.session.add(session)
        db.session.commit()
        
        return user, session
    
    @staticmethod
    def verify_email(token: str) -> User:
        """
        Verify a user's email address.
        
        Args:
            token: Verification token
            
        Returns:
            Verified User object
            
        Raises:
            InvalidTokenError: If token is invalid
        """
        user = User.query.filter_by(verification_token=token).first()
        if not user:
            raise InvalidTokenError("Invalid verification token")
            
        if user.verify_email(token):
            return user
        raise InvalidTokenError("Failed to verify email")
    
    @staticmethod
    def initiate_password_reset(email: str) -> None:
        """
        Initiate the password reset process for a user.
        
        Args:
            email: User's email address
            
        Raises:
            UserNotFoundError: If no user exists with the given email
        """
        user = User.query.filter_by(email=email).first()
        if not user:
            raise UserNotFoundError("No user found with this email address")
        
        reset_token = generate_token()
        user.set_reset_token(reset_token)
        
        send_password_reset_email(user.email, reset_token)
    
    @staticmethod
    def reset_password(token: str, new_password: str) -> User:
        """
        Reset a user's password using a reset token.
        
        Args:
            token: Password reset token
            new_password: New password to set
            
        Returns:
            Updated User object
            
        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        user = User.query.filter_by(reset_token=token).first()
        if not user:
            raise InvalidTokenError("Invalid reset token")
        
        if not user.check_reset_token(token):
            raise InvalidTokenError("Reset token has expired")
        
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        return user
    
    @staticmethod
    def invalidate_session(session_token: str) -> None:
        """
        Invalidate a user session.
        
        Args:
            session_token: Session token to invalidate
            
        Raises:
            InvalidTokenError: If session token is invalid
        """
        session = Session.query.filter_by(token=session_token).first()
        if not session:
            raise InvalidTokenError("Invalid session token")
        
        session.invalidate()
    
    @staticmethod
    def get_active_session(session_token: str) -> Optional[Session]:
        """
        Get an active session by its token.
        
        Args:
            session_token: Session token to look up
            
        Returns:
            Session object if found and valid, None otherwise
        """
        session = Session.query.filter_by(token=session_token, is_active=True).first()
        if session and session.is_valid():
            session.update_last_accessed()
            return session
        return None 