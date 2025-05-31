"""
Security services for authentication.

This module provides functions for encryption, decryption, and secure token generation.
"""

import secrets
import string
from typing import Optional
import base64
import hashlib

def encrypt_data(data: str, key: Optional[str] = None) -> str:
    """
    Encrypt sensitive data.
    
    Args:
        data: String data to encrypt
        key: Optional encryption key (if None, uses default approach)
        
    Returns:
        Encrypted string
        
    Note:
        This is a placeholder implementation. In production, use proper
        encryption libraries like cryptography or Fernet.
    """
    # TODO: Implement proper encryption using cryptography library
    # Example implementation would be:
    # from cryptography.fernet import Fernet
    # if key is None:
    #     key = get_encryption_key()
    # f = Fernet(key)
    # return f.encrypt(data.encode()).decode()
    
    # Placeholder: just base64 encode for now
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """
    Decrypt sensitive data.
    
    Args:
        encrypted_data: Encrypted string
        key: Optional decryption key (if None, uses default approach)
        
    Returns:
        Decrypted string
        
    Note:
        This is a placeholder implementation. In production, use proper
        encryption libraries like cryptography or Fernet.
    """
    # TODO: Implement proper decryption using cryptography library
    # Example implementation would be:
    # from cryptography.fernet import Fernet
    # if key is None:
    #     key = get_encryption_key()
    # f = Fernet(key)
    # return f.decrypt(encrypted_data.encode()).decode()
    
    # Placeholder: just base64 decode for now
    try:
        return base64.b64decode(encrypted_data.encode()).decode()
    except Exception:
        return encrypted_data

def generate_api_key(length: int = 40) -> str:
    """
    Generate a secure API key.
    
    Args:
        length: Length of the API key (default: 40)
        
    Returns:
        Secure random API key string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token (URL-safe).
    
    Args:
        length: Length of the token in bytes (default: 32)
        
    Returns:
        Secure random token string
    """
    return secrets.token_urlsafe(length)

def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
    """
    Create a hash of sensitive data for comparison purposes.
    
    Args:
        data: Data to hash
        salt: Optional salt (if None, generates one)
        
    Returns:
        Hashed string with salt prepended
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Combine salt and data
    salted_data = salt + data
    
    # Create hash
    hash_obj = hashlib.sha256(salted_data.encode())
    hashed = hash_obj.hexdigest()
    
    # Return salt + hash for storage
    return f"{salt}:{hashed}"

def verify_hashed_data(data: str, hashed_data: str) -> bool:
    """
    Verify data against its hash.
    
    Args:
        data: Original data to verify
        hashed_data: Stored hash with salt
        
    Returns:
        True if data matches hash, False otherwise
    """
    try:
        salt, stored_hash = hashed_data.split(':', 1)
        
        # Recreate hash with same salt
        salted_data = salt + data
        hash_obj = hashlib.sha256(salted_data.encode())
        computed_hash = hash_obj.hexdigest()
        
        # Constant-time comparison
        return secrets.compare_digest(stored_hash, computed_hash)
    except (ValueError, TypeError):
        return False 