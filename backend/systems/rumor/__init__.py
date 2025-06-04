"""Rumor system - Business Logic with Centralized Configuration

This module contains the business logic for the rumor system, now integrated
with centralized rules configuration from backend.systems.rules.

REFACTORING COMPLETED:
- Separated business logic from technical infrastructure
- Business logic remains in backend.systems.rumor
- Technical infrastructure moved to backend.infrastructure.systems.rumor
- Resolved duplicate service implementations by creating ConsolidatedRumorBusinessService
- Fixed database integration issues with abstract repository pattern
- Eliminated hardcoded configuration values in favor of centralized rules
- Updated decay and propagation utilities to use centralized configuration
- Removed placeholder code and consolidated services

Infrastructure components are located in backend.infrastructure.systems.rumor.
"""

# Import business logic modules
from . import events
from . import services
from . import utils

# Export consolidated business service for unified access
try:
    from .services.consolidated_rumor_service import ConsolidatedRumorBusinessService
    __all__ = ["ConsolidatedRumorBusinessService", "events", "services", "utils"]
except ImportError:
    __all__ = ["events", "services", "utils"]

# Configuration integration note:
# This system now uses centralized configuration from backend.systems.rules.rules
# All rumor mechanics (decay, mutation, spread, etc.) can be tuned via JSON configuration
# without touching code. See data/systems/rules/rumor_config.json for configuration options.
