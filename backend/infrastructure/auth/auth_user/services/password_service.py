"""
Password management services for authentication.

This module provides functions for hashing, verifying, and managing user passwords.
"""

from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """
    Password service class providing password hashing and verification functionality.
    """
    
    def __init__(self):
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: The plaintext password to verify
            hashed_password: The password hash to compare against
            
        Returns:
            True if the password matches the hash, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def hash_password(self, password: str) -> str:
        """
        Generate a password hash using bcrypt.
        
        Args:
            password: The plaintext password to hash
            
        Returns:
            Securely hashed password string
        """
        return self.pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: The plaintext password to verify
        hashed_password: The password hash to compare against
        
    Returns:
        True if the password matches the hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a password hash using bcrypt.
    
    Args:
        password: The plaintext password to hash
        
    Returns:
        Securely hashed password string
    """
    return pwd_context.hash(password) 