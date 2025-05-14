"""
Authentication utilities.
"""

import logging
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.core.config import Config
from app.core.utils.error_handlers import AuthenticationError, AuthorizationError, ValidationError, handle_auth_error
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .base_manager import BaseManager
from app.core.database import db
from app.core.models.user import User
from app.core.models.role import Role

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthManager(BaseManager):
    """Manager for authentication and authorization"""
    
    def __init__(self):
        super().__init__()
        self.pwd_context = pwd_context
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate a password hash."""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token and return its payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise ValidationError("Invalid token")

    def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get the current user from a JWT token."""
        payload = self.verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Get token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                raise AuthenticationError("No authorization header")
            
            # Verify token
            token = auth_header.split(" ")[1]
            auth_manager = AuthManager()
            payload = auth_manager.verify_token(token)
            
            # Add user info to request context
            request.user = payload
            
            return f(*args, **kwargs)
            
        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            raise AuthenticationError("Authentication failed")
    
    return decorated

def require_role(roles: list):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Check if user is authenticated
                if not hasattr(request, 'user'):
                    raise AuthenticationError("User not authenticated")
                
                # Check if user has required role
                user_roles = request.user.get('roles', [])
                if not any(role in user_roles for role in roles):
                    raise AuthorizationError("Insufficient permissions")
                
                return f(*args, **kwargs)
                
            except AuthenticationError as e:
                logger.warning(f"Authentication failed: {str(e)}")
                raise
            except AuthorizationError as e:
                logger.warning(f"Authorization failed: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error during authorization: {str(e)}")
                raise AuthorizationError("Authorization failed")
        
        return decorated
    return decorator

def get_current_user() -> Dict[str, Any]:
    """Get current authenticated user"""
    try:
        if not hasattr(request, 'user'):
            raise AuthenticationError("User not authenticated")
        return request.user
    except Exception as e:
        logger.error(f"Failed to get current user: {str(e)}")
        raise

def create_admin_user(username: str, email: str, password: str) -> Optional[User]:
    """
    Create an admin user.
    
    Args:
        username: The admin username
        email: The admin email
        password: The admin password
        
    Returns:
        User: The created admin user or None if creation fails
    """
    try:
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            logger.error("Admin user already exists")
            return None
        
        # Get admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator role')
            db.session.add(admin_role)
            db.session.commit()
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            role=admin_role
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        logger.info(f"Admin user {username} created successfully")
        return admin
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        db.session.rollback()
        raise

def verify_password(user: User, password: str) -> bool:
    """
    Verify a user's password.
    
    Args:
        user: The user to verify
        password: The password to check
        
    Returns:
        bool: True if password is correct, False otherwise
    """
    try:
        return user.check_password(password)
    except Exception as e:
        logger.error(f"Failed to verify password: {str(e)}")
        return False

def get_user_by_email(email: str) -> Optional[User]:
    """
    Get a user by their email.
    
    Args:
        email: The user's email
        
    Returns:
        User: The user if found, None otherwise
    """
    try:
        return User.query.filter_by(email=email).first()
    except Exception as e:
        logger.error(f"Failed to get user by email: {str(e)}")
        return None

def get_user_by_username(username: str) -> Optional[User]:
    """
    Get a user by their username.
    
    Args:
        username: The username to look up
        
    Returns:
        User: The user if found, None otherwise
    """
    try:
        return User.query.filter_by(username=username).first()
    except Exception as e:
        logger.error(f"Failed to get user by username: {str(e)}")
        return None

def has_permission(user, permission_name: str) -> bool:
    """Check if the user has a specific permission via their role."""
    if hasattr(user, 'has_permission'):
        return user.has_permission(permission_name)
    return False

def require_permission(permission: str):
    """Decorator to require a specific permission for a route."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user'):
                raise AuthenticationError("User not authenticated")
            user = request.user
            if not has_permission(user, permission):
                raise AuthorizationError(f"Insufficient permissions: {permission}")
            return f(*args, **kwargs)
        return decorated
    return decorator 