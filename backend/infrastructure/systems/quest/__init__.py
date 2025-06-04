"""
Quest Infrastructure Module

Provides technical infrastructure components for the quest system including:
- API routing and HTTP endpoints
- Data access repositories and database operations  
- Cross-system integration and event handling
- Technical utilities and infrastructure services

This module is separated from business logic in backend.systems.quest
"""

# API Infrastructure
from .api.quest_router import router as quest_router
from .api.journal_router import router as journal_router

# Repository Infrastructure  
from .repositories import QuestRepository
from .repositories.npc_quest_repository import NPCQuestRepository

# Integration Infrastructure
from .integration.quest_integration import QuestIntegration

__all__ = [
    # API Components
    "quest_router",
    "journal_router",
    
    # Repository Components
    "QuestRepository", 
    "NPCQuestRepository",
    
    # Integration Components
    "QuestIntegration"
] 