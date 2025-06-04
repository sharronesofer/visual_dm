"""
Quest API Infrastructure Module

Provides HTTP routing and API layer components for the quest system.
This module contains technical infrastructure concerns separated from business logic.
"""

from .quest_router import router as quest_router
from .journal_router import router as journal_router

__all__ = [
    "quest_router",
    "journal_router"
] 