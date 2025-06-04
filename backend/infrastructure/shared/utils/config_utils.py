"""
Configuration utilities for the shared utils module.
"""

import os
import secrets
from typing import Dict, Any

def get_config() -> Dict[str, Any]:
    """Get configuration settings.
    
    Returns:
        Dict containing configuration settings
    """
    # Get secret key securely
    secret_key = os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            raise ValueError("SECRET_KEY must be set in production environment")
        else:
            secret_key = secrets.token_urlsafe(32)
            print("WARNING: Using generated secret key for development")
    
    # Basic configuration - extend as needed
    return {
        'debug': os.getenv("DEBUG", "false").lower() == "true",
        'log_level': os.getenv("LOG_LEVEL", "INFO"),
        'database_url': os.getenv("DATABASE_URL", "sqlite:///app.db"),
        'secret_key': secret_key,
        'max_connections': int(os.getenv("MAX_CONNECTIONS", "100")),
        'timeout': int(os.getenv("TIMEOUT", "30"))
    }

def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific configuration setting.
    
    Args:
        key: Configuration key to retrieve
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    config = get_config()
    return config.get(key, default)

def update_config(updates: Dict[str, Any]) -> None:
    """Update configuration settings.
    
    Args:
        updates: Dictionary of settings to update
    """
    # In a real implementation, this would persist changes
    # For now, this is a placeholder
    pass 