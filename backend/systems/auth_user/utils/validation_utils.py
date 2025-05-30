"""
Validation utilities for user-related data like passwords, usernames, and emails.
"""

import re
from typing import Optional, Tuple

def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength based on defined criteria.
    
    Args:
        password: The password string to validate
        
    Returns:
        Tuple containing:
            - Boolean indicating if the password is valid
            - Error message if invalid, None if valid
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, None

def validate_username_format(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format.
    
    Args:
        username: The username string to validate
        
    Returns:
        Tuple containing:
            - Boolean indicating if the username is valid
            - Error message if invalid, None if valid
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 30:
        return False, "Username must be at most 30 characters long"
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    return True, None

def validate_email_format(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format using regex.
    
    Args:
        email: The email string to validate
        
    Returns:
        Tuple containing:
            - Boolean indicating if the email is valid
            - Error message if invalid, None if valid
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_regex, email):
        return False, "Invalid email format"
    return True, None 