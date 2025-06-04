"""
Espionage Services Module

This module provides all the business services for the Economic Espionage System.
Services are organized by responsibility and can be used independently or together
to implement complex espionage scenarios.
"""

# Core orchestration service
from .espionage_service import EspionageService

# Specialized services for different aspects of espionage
from .operation_service import EspionageOperationService
from .agent_service import EspionageAgentService

# Intelligence and Network services to be implemented
# TODO: Implement these services when needed
# from .intelligence_service import EconomicIntelligenceService
# from .network_service import SpyNetworkService
# from .espionage_engine import EspionageEngine


__all__ = [
    'EspionageService',
    'EspionageOperationService', 
    'EspionageAgentService',
    # TODO: Add these when implemented
    # 'EconomicIntelligenceService',
    # 'SpyNetworkService', 
    # 'EspionageEngine'
] 