"""
Time Provider Utilities

This module provides time-related utilities and adapters for business logic.
Separates time operations from business logic for easier testing and dependency injection.
"""

from datetime import datetime
from typing import Protocol

from backend.systems.magic.services.magic_combat_service import TimeProvider


class SystemTimeProvider(TimeProvider):
    """Standard time provider using system time"""
    
    def get_current_time(self) -> datetime:
        """Get current system time"""
        return datetime.now()


class FixedTimeProvider(TimeProvider):
    """Fixed time provider for testing"""
    
    def __init__(self, fixed_time: datetime):
        self._fixed_time = fixed_time
    
    def get_current_time(self) -> datetime:
        """Get fixed time"""
        return self._fixed_time
    
    def set_time(self, new_time: datetime):
        """Update the fixed time"""
        self._fixed_time = new_time


def create_system_time_provider() -> SystemTimeProvider:
    """Factory function to create system time provider"""
    return SystemTimeProvider()

def create_fixed_time_provider(fixed_time: datetime) -> FixedTimeProvider:
    """Factory function to create fixed time provider for testing"""
    return FixedTimeProvider(fixed_time) 