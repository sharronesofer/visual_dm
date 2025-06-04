"""
Magic System Infrastructure

Infrastructure layer for the canonical MP-based magic system.
Provides database models, API router, and adapters for the business logic in backend.systems.magic.
"""

# Database models for magic system
from .models import models

# Services (re-exports from business layer)
from . import services

# Canonical API router
from .router import magic_router

__all__ = [
    'models',
    'services', 
    'magic_router'
] 