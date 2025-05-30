"""Common FastAPI dependencies."""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from .config import settings
from .security import verify_password
from ..database import get_db
# Placeholder - you'll need to adjust imports based on your actual User model
# from ..models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# This is a placeholder - in a real application, you'd have a User model
# and authenticate against your database
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Optional[dict]:
    """
    Get the current user based on the JWT token
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        User object if authentication is successful
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # This is a placeholder - in a real app, you'd query the database
    # user = db.query(User).filter(User.username == username).first()
    # if user is None:
    #     raise credentials_exception
    
    # For demo purposes, we'll just return a dict
    user = {"username": username, "is_active": True}
    
    return user

def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Get the current active user
    
    Args:
        current_user: Current user object
        
    Returns:
        User object if the user is active
        
    Raises:
        HTTPException: If the user is inactive
    """
    # In a real app, you'd check user.is_active
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 