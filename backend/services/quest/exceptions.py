"""
Quest System Exception Classes
Provides standardized exceptions for consistent error handling across the quest system.
"""

from typing import Optional, Dict, Any


class QuestSystemError(Exception):
    """Base exception for all quest system errors"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "QUEST_SYSTEM_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class QuestNotFoundError(QuestSystemError):
    """Raised when a quest cannot be found"""
    
    def __init__(self, quest_id: str, message: str = None):
        default_message = f"Quest with ID '{quest_id}' not found"
        super().__init__(
            message or default_message,
            error_code="QUEST_NOT_FOUND",
            details={"quest_id": quest_id}
        )


class QuestValidationError(QuestSystemError):
    """Raised when quest data fails validation"""
    
    def __init__(self, validation_errors: Dict[str, Any], message: str = None):
        default_message = "Quest data validation failed"
        super().__init__(
            message or default_message,
            error_code="QUEST_VALIDATION_ERROR",
            details={"validation_errors": validation_errors}
        )


class QuestStatusError(QuestSystemError):
    """Raised when quest status transition is invalid"""
    
    def __init__(self, current_status: str, target_status: str, message: str = None):
        default_message = f"Cannot transition quest from '{current_status}' to '{target_status}'"
        super().__init__(
            message or default_message,
            error_code="QUEST_STATUS_ERROR",
            details={
                "current_status": current_status,
                "target_status": target_status
            }
        )


class QuestAccessError(QuestSystemError):
    """Raised when user doesn't have permission to access/modify quest"""
    
    def __init__(self, quest_id: str, player_id: str, action: str, message: str = None):
        default_message = f"Player '{player_id}' cannot perform '{action}' on quest '{quest_id}'"
        super().__init__(
            message or default_message,
            error_code="QUEST_ACCESS_ERROR",
            details={
                "quest_id": quest_id,
                "player_id": player_id,
                "action": action
            }
        )


class QuestStepError(QuestSystemError):
    """Raised when quest step operations fail"""
    
    def __init__(self, quest_id: str, step_id: int, message: str = None):
        default_message = f"Quest step '{step_id}' operation failed for quest '{quest_id}'"
        super().__init__(
            message or default_message,
            error_code="QUEST_STEP_ERROR",
            details={
                "quest_id": quest_id,
                "step_id": step_id
            }
        )


class QuestGenerationError(QuestSystemError):
    """Raised when quest generation fails"""
    
    def __init__(self, context: Dict[str, Any] = None, message: str = None):
        default_message = "Failed to generate quest"
        super().__init__(
            message or default_message,
            error_code="QUEST_GENERATION_ERROR",
            details={"generation_context": context or {}}
        )


class QuestConfigurationError(QuestSystemError):
    """Raised when quest configuration is invalid or missing"""
    
    def __init__(self, config_issue: str, message: str = None):
        default_message = f"Quest configuration error: {config_issue}"
        super().__init__(
            message or default_message,
            error_code="QUEST_CONFIG_ERROR",
            details={"config_issue": config_issue}
        )


class QuestDependencyError(QuestSystemError):
    """Raised when quest dependencies are not satisfied"""
    
    def __init__(self, quest_id: str, missing_dependencies: list, message: str = None):
        default_message = f"Quest '{quest_id}' has unsatisfied dependencies: {missing_dependencies}"
        super().__init__(
            message or default_message,
            error_code="QUEST_DEPENDENCY_ERROR",
            details={
                "quest_id": quest_id,
                "missing_dependencies": missing_dependencies
            }
        )


class QuestExpiredError(QuestSystemError):
    """Raised when attempting to operate on an expired quest"""
    
    def __init__(self, quest_id: str, expiry_date: str, message: str = None):
        default_message = f"Quest '{quest_id}' expired on {expiry_date}"
        super().__init__(
            message or default_message,
            error_code="QUEST_EXPIRED_ERROR",
            details={
                "quest_id": quest_id,
                "expiry_date": expiry_date
            }
        )


class QuestLimitError(QuestSystemError):
    """Raised when quest limits are exceeded"""
    
    def __init__(self, limit_type: str, limit_value: int, current_value: int, message: str = None):
        default_message = f"Quest {limit_type} limit exceeded: {current_value}/{limit_value}"
        super().__init__(
            message or default_message,
            error_code="QUEST_LIMIT_ERROR",
            details={
                "limit_type": limit_type,
                "limit_value": limit_value,
                "current_value": current_value
            }
        )


class QuestChainError(QuestSystemError):
    """Raised when quest chain operations fail"""
    
    def __init__(self, chain_id: str, operation: str, message: str = None):
        default_message = f"Quest chain '{chain_id}' operation '{operation}' failed"
        super().__init__(
            message or default_message,
            error_code="QUEST_CHAIN_ERROR",
            details={
                "chain_id": chain_id,
                "operation": operation
            }
        )


class QuestTemplateError(QuestSystemError):
    """Raised when quest template operations fail"""
    
    def __init__(self, template_id: str = None, message: str = None):
        default_message = f"Quest template error" + (f" for template '{template_id}'" if template_id else "")
        super().__init__(
            message or default_message,
            error_code="QUEST_TEMPLATE_ERROR",
            details={"template_id": template_id} if template_id else {}
        )


class QuestDifficultyError(QuestSystemError):
    """Raised when quest difficulty calculation fails"""
    
    def __init__(self, calculation_context: Dict[str, Any] = None, message: str = None):
        default_message = "Quest difficulty calculation failed"
        super().__init__(
            message or default_message,
            error_code="QUEST_DIFFICULTY_ERROR",
            details={"calculation_context": calculation_context or {}}
        )


class QuestCacheError(QuestSystemError):
    """Raised when quest cache operations fail"""
    
    def __init__(self, cache_operation: str, message: str = None):
        default_message = f"Quest cache operation '{cache_operation}' failed"
        super().__init__(
            message or default_message,
            error_code="QUEST_CACHE_ERROR",
            details={"cache_operation": cache_operation}
        )


# Convenience functions for common error scenarios
def quest_not_found(quest_id: str) -> QuestNotFoundError:
    """Factory function for quest not found errors"""
    return QuestNotFoundError(quest_id)


def quest_validation_failed(validation_errors: Dict[str, Any]) -> QuestValidationError:
    """Factory function for validation errors"""
    return QuestValidationError(validation_errors)


def quest_status_invalid(current_status: str, target_status: str) -> QuestStatusError:
    """Factory function for status transition errors"""
    return QuestStatusError(current_status, target_status)


def quest_chain_invalid(chain_id: str, operation: str) -> QuestChainError:
    """Factory function for chain errors"""
    return QuestChainError(chain_id, operation)


def quest_generation_failed(context: Dict[str, Any] = None) -> QuestGenerationError:
    """Factory function for generation errors"""
    return QuestGenerationError(context)


# Legacy aliases for backward compatibility
invalid_status_transition = quest_status_invalid
quest_access_denied = QuestAccessError 