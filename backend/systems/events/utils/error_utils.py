"""
Error handling utilities for the Visual DM game client.
"""

import logging
from typing import Optional, Dict, Any

# Configure logging
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScreenError(Exception):
    """Custom exception for screen-related errors."""
    pass

# ValidationError class REMOVED - Should use the one from backend.core.exceptions
# class ValidationError(Exception):
#     """Custom exception for validation errors."""
#     pass

def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Handle errors with logging and context.
    
    Args:
        error: The exception that occurred
        context: Optional context information
    """
    try:
        error_msg = f"Error: {str(error)}"
        if context:
            error_msg += f"\nContext: {context}"
        logger.error(error_msg)
    except Exception as e:
        logger.error(f"Error in error handling: {str(e)}") 