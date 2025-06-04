"""
Game Time System Logging Adapter

Provides logging functionality for the game time system business logic.
This is technical infrastructure that isolates logging concerns from business logic.
"""

import logging
from typing import Optional


def get_time_manager_logger() -> logging.Logger:
    """Get logger for TimeManager business logic."""
    return logging.getLogger("backend.systems.game_time.services.time_manager")


def get_weather_service_logger() -> logging.Logger:
    """Get logger for WeatherService business logic."""
    return logging.getLogger("backend.systems.game_time.services.weather_service")


def get_game_time_system_logger(module_name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for any game time system component.
    
    Args:
        module_name: Optional specific module name, defaults to generic game_time logger
        
    Returns:
        Logger instance for the specified module
    """
    if module_name:
        return logging.getLogger(f"backend.systems.game_time.{module_name}")
    return logging.getLogger("backend.systems.game_time") 