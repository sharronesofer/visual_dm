"""
Quest System Module

This module provides quest-related functionality including business logic, 
models, and utilities according to the Development Bible standards.

Business Logic: Located in backend/systems/quest/
Infrastructure: Located in backend/infrastructure/ (cache, config, database)
"""

# Export business logic from systems (Bible-compliant location)
from .models import (
    # Core data structures
    QuestData,
    QuestStepData,
    QuestRewardData,
    QuestChainData,
    QuestChainProgressData,
    LocationData,
    PlayerHomeData,
    CreateQuestData,
    UpdateQuestData,
    
    # Enums
    QuestStatus,
    QuestDifficulty,
    QuestTheme,
    ChainType,
    
    # Enum aliases for backward compatibility
    QuestStatusEnum,
    QuestDifficultyEnum,
    QuestThemeEnum,
    ChainTypeEnum,
    
    # Protocol interfaces
    QuestRepository,
    QuestValidationService,
    QuestGenerationService
)

from .services import (
    # Core business services
    QuestBusinessService,
)

from .generator import (
    # Quest generation services
    QuestGeneratorService,
    QuestGenerator,  # Alias for backward compatibility
)

from .exceptions import (
    # Exception classes
    QuestSystemError,
    QuestNotFoundError,
    QuestValidationError,
    QuestStatusError,
    QuestChainError,
    QuestGenerationError,
    QuestTemplateError,
    QuestDifficultyError,
    QuestCacheError,
    QuestConflictError,
    QuestDependencyError,
    QuestAccessError,
    
    # Convenience functions
    quest_not_found,
    quest_validation_failed,
    quest_status_invalid,
    quest_chain_invalid,
    quest_generation_failed
)

__all__ = [
    # Core data structures
    'QuestData',
    'QuestStepData',
    'QuestRewardData',
    'QuestChainData',
    'QuestChainProgressData',
    'LocationData',
    'PlayerHomeData',
    'CreateQuestData',
    'UpdateQuestData',
    
    # Business Services
    'QuestBusinessService',
    'QuestGeneratorService',
    'QuestGenerator',  # Alias for backward compatibility
    
    # Enums
    'QuestStatus',
    'QuestDifficulty',
    'QuestTheme',
    'ChainType',
    
    # Enum aliases for backward compatibility
    'QuestStatusEnum',
    'QuestDifficultyEnum',
    'QuestThemeEnum',
    'ChainTypeEnum',
    
    # Protocol interfaces
    'QuestRepository',
    'QuestValidationService',
    'QuestGenerationService',
    
    # Exception classes
    'QuestSystemError',
    'QuestNotFoundError',
    'QuestValidationError',
    'QuestStatusError',
    'QuestChainError',
    'QuestGenerationError',
    'QuestTemplateError',
    'QuestDifficultyError',
    'QuestCacheError',
    'QuestConflictError',
    'QuestDependencyError',
    'QuestAccessError',
    
    # Convenience functions
    'quest_not_found',
    'quest_validation_failed',
    'quest_status_invalid',
    'quest_chain_invalid',
    'quest_generation_failed'
]
