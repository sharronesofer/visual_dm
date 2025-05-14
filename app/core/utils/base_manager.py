"""
Base manager class for utility managers.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class BaseManager:
    """Base class for utility managers."""
    
    def __init__(self):
        """Initialize the base manager."""
        self.logger = logger
    
    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """Log an error message."""
        if error:
            self.logger.error(f"{message}: {str(error)}")
        else:
            self.logger.error(message)
    
    def log_info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)
    
    def handle_error(self, error: Exception, message: str) -> None:
        """Handle and log an error."""
        self.log_error(message, error)
        raise error 