"""
Shared Exceptions Module

This module provides common exception classes used across all systems.
"""


class BaseSystemError(Exception):
    """Base exception for all system errors"""
    pass


class NotFoundError(BaseSystemError):
    """Base exception for not found errors"""
    pass


class ValidationError(BaseSystemError):
    """Base exception for validation errors"""
    pass


class ConflictError(BaseSystemError):
    """Base exception for conflict errors"""
    pass


class RepositoryError(BaseSystemError):
    """Base exception for repository/database errors"""
    pass


class EntityNotFoundError(NotFoundError):
    """Exception raised when entity is not found"""
    pass


class EntityConflictError(ConflictError):
    """Exception raised when entity conflicts occur"""
    pass


# NPC System Exceptions
class NpcNotFoundError(NotFoundError):
    """Exception raised when NPC is not found"""
    pass


class NpcValidationError(ValidationError):
    """Exception raised when NPC validation fails"""
    pass


class NpcConflictError(ConflictError):
    """Exception raised when NPC conflicts occur"""
    pass


# Character System Exceptions
class CharacterNotFoundError(NotFoundError):
    """Exception raised when Character is not found"""
    pass


class CharacterValidationError(ValidationError):
    """Exception raised when Character validation fails"""
    pass


class CharacterConflictError(ConflictError):
    """Exception raised when Character conflicts occur"""
    pass


# Auth User System Exceptions
class Auth_UserNotFoundError(NotFoundError):
    """Exception raised when Auth User is not found"""
    pass


class Auth_UserValidationError(ValidationError):
    """Exception raised when Auth User validation fails"""
    pass


class Auth_UserConflictError(ConflictError):
    """Exception raised when Auth User conflicts occur"""
    pass


# POI System Exceptions
class PoiNotFoundError(NotFoundError):
    """Exception raised when POI is not found"""
    pass


class PoiValidationError(ValidationError):
    """Exception raised when POI validation fails"""
    pass


class PoiConflictError(ConflictError):
    """Exception raised when POI conflicts occur"""
    pass


# Religion System Exceptions
class ReligionNotFoundError(NotFoundError):
    """Exception raised when Religion is not found"""
    pass


class ReligionValidationError(ValidationError):
    """Exception raised when Religion validation fails"""
    pass


class ReligionConflictError(ConflictError):
    """Exception raised when Religion conflicts occur"""
    pass


# Region System Exceptions
class RegionNotFoundError(NotFoundError):
    """Exception raised when Region is not found"""
    pass


class RegionValidationError(ValidationError):
    """Exception raised when Region validation fails"""
    pass


class RegionConflictError(ConflictError):
    """Exception raised when Region conflicts occur"""
    pass


# Shared System Exceptions
class SharedNotFoundError(NotFoundError):
    """Exception raised when Shared is not found"""
    pass


class SharedValidationError(ValidationError):
    """Exception raised when Shared validation fails"""
    pass


class SharedConflictError(ConflictError):
    """Exception raised when Shared conflicts occur"""
    pass


# Arc System Exceptions
class ArcNotFoundError(NotFoundError):
    """Exception raised when Arc is not found"""
    pass


class ArcValidationError(ValidationError):
    """Exception raised when Arc validation fails"""
    pass


class ArcConflictError(ConflictError):
    """Exception raised when Arc conflicts occur"""
    pass


class ArcStepNotFoundError(NotFoundError):
    """Exception raised when Arc Step is not found"""
    pass


class ArcProgressionNotFoundError(NotFoundError):
    """Exception raised when Arc Progression is not found"""
    pass


class ArcCompletionNotFoundError(NotFoundError):
    """Exception raised when Arc Completion Record is not found"""
    pass


# Combat System Exceptions
class CombatNotFoundError(NotFoundError):
    """Exception raised when Combat is not found"""
    pass


class CombatValidationError(ValidationError):
    """Exception raised when Combat validation fails"""
    pass


class CombatConflictError(ConflictError):
    """Exception raised when Combat conflicts occur"""
    pass


class CombatSessionNotFoundError(NotFoundError):
    """Exception raised when Combat Session is not found"""
    pass


class CombatActionNotFoundError(NotFoundError):
    """Exception raised when Combat Action is not found"""
    pass


class CombatParticipantNotFoundError(NotFoundError):
    """Exception raised when Combat Participant is not found"""
    pass


# Rumor System Exceptions
class RumorNotFoundError(NotFoundError):
    """Exception raised when Rumor is not found"""
    pass


class RumorValidationError(ValidationError):
    """Exception raised when Rumor validation fails"""
    pass


class RumorConflictError(ConflictError):
    """Exception raised when Rumor conflicts occur"""
    pass


# LLM System Exceptions
class LlmNotFoundError(NotFoundError):
    """Exception raised when LLM is not found"""
    pass


class LlmValidationError(ValidationError):
    """Exception raised when LLM validation fails"""
    pass


class LlmConflictError(ConflictError):
    """Exception raised when LLM conflicts occur"""
    pass


# Dialogue System Exceptions
class DialogueNotFoundError(NotFoundError):
    """Exception raised when Dialogue is not found"""
    pass


class DialogueValidationError(ValidationError):
    """Exception raised when Dialogue validation fails"""
    pass


class DialogueConflictError(ConflictError):
    """Exception raised when Dialogue conflicts occur"""
    pass


# Analytics System Exceptions
class AnalyticsNotFoundError(NotFoundError):
    """Exception raised when Analytics is not found"""
    pass


class AnalyticsValidationError(ValidationError):
    """Exception raised when Analytics validation fails"""
    pass


class AnalyticsConflictError(ConflictError):
    """Exception raised when Analytics conflicts occur"""
    pass


# Events System Exceptions
class EventsNotFoundError(NotFoundError):
    """Exception raised when Events is not found"""
    pass


class EventsValidationError(ValidationError):
    """Exception raised when Events validation fails"""
    pass


class EventsConflictError(ConflictError):
    """Exception raised when Events conflicts occur"""
    pass


# Add more system-specific exceptions as needed
__all__ = [
    "BaseSystemError",
    "NotFoundError", 
    "ValidationError",
    "ConflictError",
    "RepositoryError",
    "EntityNotFoundError",
    "EntityConflictError",
    "NpcNotFoundError",
    "NpcValidationError", 
    "NpcConflictError",
    "CharacterNotFoundError",
    "CharacterValidationError",
    "CharacterConflictError",
    "Auth_UserNotFoundError",
    "Auth_UserValidationError",
    "Auth_UserConflictError",
    "PoiNotFoundError",
    "PoiValidationError",
    "PoiConflictError",
    "ReligionNotFoundError",
    "ReligionValidationError",
    "ReligionConflictError",
    "RegionNotFoundError",
    "RegionValidationError",
    "RegionConflictError",
    "SharedNotFoundError",
    "SharedValidationError",
    "SharedConflictError",
    "ArcNotFoundError",
    "ArcValidationError",
    "ArcConflictError",
    "ArcStepNotFoundError",
    "ArcProgressionNotFoundError",
    "ArcCompletionNotFoundError",
    "CombatNotFoundError",
    "CombatValidationError",
    "CombatConflictError",
    "CombatSessionNotFoundError",
    "CombatActionNotFoundError",
    "CombatParticipantNotFoundError",
    "RumorNotFoundError",
    "RumorValidationError",
    "RumorConflictError",
    "LlmNotFoundError",
    "LlmValidationError",
    "LlmConflictError",
    "DialogueNotFoundError",
    "DialogueValidationError",
    "DialogueConflictError",
    "AnalyticsNotFoundError",
    "AnalyticsValidationError",
    "AnalyticsConflictError",
    "EventsNotFoundError",
    "EventsValidationError",
    "EventsConflictError",
] 