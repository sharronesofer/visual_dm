"""
Core configuration module for the backend.
"""

import os
from typing import Any, Dict

class Config:
    """Basic configuration class."""
    
    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(self, key, default)

# Global config instance
config = Config() 