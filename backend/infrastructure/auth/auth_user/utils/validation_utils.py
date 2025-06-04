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
    if not password or not isinstance(password, str):
        return False, "Password cannot be empty"
    
    # Check length constraints
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
        
    if len(password) > 128:  # Prevent extremely long passwords
        return False, "Password cannot exceed 128 characters"
    
    # Check character requirements
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak patterns
    if re.search(r"(.)\1{4,}", password):  # 5+ consecutive repeated characters
        return False, "Password cannot contain more than 4 consecutive identical characters"
    
    # Check for keyboard patterns (simple check)
    keyboard_patterns = ["qwerty", "asdfgh", "zxcvbn", "123456", "password", "admin"]
    password_lower = password.lower()
    for pattern in keyboard_patterns:
        if pattern in password_lower:
            return False, f"Password cannot contain common patterns like '{pattern}'"
    
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
    Validate email format using comprehensive regex and additional checks.
    
    Args:
        email: The email string to validate
        
    Returns:
        Tuple containing:
            - Boolean indicating if the email is valid
            - Error message if invalid, None if valid
    """
    if not email or not isinstance(email, str):
        return False, "Email cannot be empty"
    
    # Basic length checks
    if len(email) < 5:  # Minimum: a@b.c
        return False, "Email is too short"
    if len(email) > 254:  # RFC 5321 limit
        return False, "Email is too long"
    
    # Enhanced email regex with stricter validation
    email_regex = r"^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$"
    
    if not re.match(email_regex, email):
        return False, "Invalid email format"
    
    # Additional validation checks
    local_part, domain_part = email.rsplit('@', 1)
    
    # Local part validation
    if len(local_part) > 64:  # RFC 5321 limit
        return False, "Email local part is too long"
    if local_part.startswith('.') or local_part.endswith('.'):
        return False, "Email local part cannot start or end with a dot"
    if '..' in local_part:
        return False, "Email local part cannot contain consecutive dots"
    
    # Domain part validation
    if len(domain_part) > 253:  # RFC 5321 limit
        return False, "Email domain part is too long"
    if domain_part.startswith('-') or domain_part.endswith('-'):
        return False, "Email domain cannot start or end with a hyphen"
    if '..' in domain_part:
        return False, "Email domain cannot contain consecutive dots"
    
    # Check for valid TLD (at least 2 characters)
    if '.' not in domain_part or len(domain_part.split('.')[-1]) < 2:
        return False, "Email domain must have a valid top-level domain"
    
    return True, None 