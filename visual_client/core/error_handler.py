"""
Error handling utilities for component managers.
"""

from enum import Enum
import logging
from typing import Any, Optional, Callable

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Severity levels for component errors."""
    LOW = "low"  # Non-critical errors that don't affect functionality
    MEDIUM = "medium"  # Errors that degrade functionality but don't break it
    HIGH = "high"  # Errors that break functionality but allow recovery
    CRITICAL = "critical"  # Errors that require immediate attention

def handle_component_error(
    error: Exception,
    component_name: str,
    severity: ErrorSeverity,
    context: Optional[dict] = None,
    recovery_action: Optional[Callable[[], Any]] = None
) -> None:
    """
    Handle errors in component operations with appropriate logging and recovery.
    
    Args:
        error: The exception that occurred
        component_name: Name of the component where the error occurred
        severity: Severity level of the error
        context: Additional context about the error
        recovery_action: Optional function to attempt error recovery
    """
    error_msg = f"{component_name} error: {str(error)}"
    if context:
        error_msg += f" Context: {context}"
    
    if severity == ErrorSeverity.LOW:
        logger.warning(error_msg)
    elif severity == ErrorSeverity.MEDIUM:
        logger.error(error_msg)
    elif severity == ErrorSeverity.HIGH:
        logger.critical(error_msg)
    elif severity == ErrorSeverity.CRITICAL:
        logger.critical(f"CRITICAL: {error_msg}")
        
    if recovery_action:
        try:
            recovery_action()
            logger.info(f"Recovery action for {component_name} completed successfully")
        except Exception as recovery_error:
            logger.error(f"Recovery action for {component_name} failed: {str(recovery_error)}")
            raise 