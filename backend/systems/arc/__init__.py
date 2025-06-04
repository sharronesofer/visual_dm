"""
Arc System - Business Logic

This module contains the business logic for narrative arcs in the game.
Technical infrastructure (repositories, routers, schemas) has been moved to backend.infrastructure.
"""

# Business logic services
from .services.arc import ArcManager
from .services.arc_generator import ArcGenerator
from .services.player_arc_manager import PlayerArcManager
from .services.progression_tracker import ProgressionTracker
from .services.quest_integration_service import QuestIntegrationService

# Domain models
from .models.arc import Arc, ArcModel, ArcType, ArcStatus, ArcPriority
from .models.arc_step import ArcStep, ArcStepModel, ArcStepType, ArcStepStatus
from .models.arc_progression import ArcProgression, ArcProgressionModel, ProgressionMethod
from .models.arc_completion_record import ArcCompletionRecord, ArcCompletionRecordModel, ArcCompletionResult

# Business rules
from .business_rules import (
    validate_arc_business_rules,
    validate_narrative_text,
    validate_arc_progression_rules
)

__all__ = [
    # Services
    'ArcManager',
    'ArcGenerator',
    'PlayerArcManager',
    'ProgressionTracker',
    'QuestIntegrationService',
    
    # Models
    'Arc',
    'ArcModel',
    'ArcType',
    'ArcStatus',
    'ArcPriority',
    'ArcStep',
    'ArcStepModel',
    'ArcStepType',
    'ArcStepStatus',
    'ArcProgression',
    'ArcProgressionModel',
    'ProgressionMethod',
    'ArcCompletionRecord',
    'ArcCompletionRecordModel',
    'ArcCompletionResult',
    
    # Business rules
    'validate_arc_business_rules',
    'validate_narrative_text',
    'validate_arc_progression_rules'
]
