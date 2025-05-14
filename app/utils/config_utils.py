import os
from dotenv import load_dotenv

load_dotenv()

class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass

def get_config(key: str, default=None):
    """Get configuration value from environment variables"""
    return os.getenv(key, default)

def get_bool_config(key: str, default=False):
    """Get boolean configuration value from environment variables"""
    value = os.getenv(key, str(default))
    return value.lower() in ('true', '1', 'yes', 'y') 