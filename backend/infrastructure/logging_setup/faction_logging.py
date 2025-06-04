"""
Faction System Logging Setup - Technical Infrastructure

Centralized logging configuration for faction-related services.
Extracted from various faction services.
"""

import logging
import sys
from typing import Optional


def setup_faction_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    include_timestamp: bool = True
) -> logging.Logger:
    """
    Set up logging for faction services
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        include_timestamp: Whether to include timestamp in logs
        
    Returns:
        Configured logger for faction services
    """
    if format_string is None:
        if include_timestamp:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            format_string = "%(name)s - %(levelname)s - %(message)s"
    
    # Get faction logger
    logger = logging.getLogger("faction")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create handler if not exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))
        
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger


def get_faction_logger(service_name: str) -> logging.Logger:
    """
    Get a logger for a specific faction service
    
    Args:
        service_name: Name of the faction service
        
    Returns:
        Logger instance for the service
    """
    return logging.getLogger(f"faction.{service_name}")


# Pre-configured loggers for common faction services
succession_logger = get_faction_logger("succession")
territory_logger = get_faction_logger("territory")
expansion_logger = get_faction_logger("expansion")
diplomacy_logger = get_faction_logger("diplomacy")
alliance_logger = get_faction_logger("alliance")
relationship_logger = get_faction_logger("relationship")
reputation_logger = get_faction_logger("reputation")
membership_logger = get_faction_logger("membership")
influence_logger = get_faction_logger("influence") 