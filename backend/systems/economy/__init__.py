"""
Economy System - Business Logic Only

This module contains only the business logic for the economy system.
Infrastructure components (routers, database services, websockets, migrations, deployment)
have been moved to backend/infrastructure/ per architectural guidelines.
"""

# Business logic imports only
from . import events
from . import models
from . import services
from . import utils

# Note: The following have been moved to backend/infrastructure/:
# - routers -> backend/infrastructure/api/economy/
# - database_service -> backend/infrastructure/database/economy/
# - websocket_events -> backend/infrastructure/websocket/economy/
# - migrations -> backend/infrastructure/migrations/economy/
# - deployment -> backend/infrastructure/deployment/economy/

# Note: Removed empty stub directories:
# - repositories (was empty, no implementation)
# - schemas (was empty, no implementation)
# - market_service (was stub redirect)
# - economy_manager (was stub redirect)
# - resource_service (was stub redirect)

# Services
from backend.systems.economy.services.economy_manager import EconomyManager
from backend.systems.economy.services.unified_economy_service import (
    UnifiedEconomyService,
    create_unified_economy_service
)
from backend.systems.economy.services.advanced_economy_service import AdvancedEconomyService

# Integration interfaces for cross-system communication
from backend.systems.economy.services.integration_interfaces import (
    NPCSystemInterface,
    FactionSystemInterface, 
    RegionSystemInterface,
    DefaultNPCSystemInterface,
    DefaultFactionSystemInterface,
    DefaultRegionSystemInterface,
    SystemIntegrationManager,
    get_integration_manager,
    set_integration_manager
)
