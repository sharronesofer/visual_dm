"""
Tension System API Package

Provides REST and WebSocket endpoints for the tension system.
"""

from .tension_router import router as tension_router

__all__ = ['tension_router'] 