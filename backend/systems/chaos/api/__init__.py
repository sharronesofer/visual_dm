"""
Chaos System API

Provides REST API endpoints for monitoring and controlling the chaos system.
Note: These endpoints are intended for development/debugging only and should
never be exposed to players as the chaos system must remain completely hidden.
"""

from backend.systems.chaos.api.chaos_api import ChaosAPI, create_chaos_api_routes

__all__ = ['ChaosAPI', 'create_chaos_api_routes'] 