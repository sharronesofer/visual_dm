"""
Quest System Exceptions

Business logic exceptions for the quest system according to the Development Bible standards.
"""

from typing import Dict, Any, Optional


class QuestSystemError(Exception):
    """Base exception for quest system errors"""
    
    def __init__(self, message: str, error_code: str = "QUEST_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class QuestNotFoundError(QuestSystemError):
    """Quest not found error"""
    
    def __init__(self, quest_id: str, message: str = None):
        self.quest_id = quest_id
        message = message or f"Quest {quest_id} not found"
        super().__init__(message, "QUEST_NOT_FOUND", {"quest_id": quest_id})


class QuestValidationError(QuestSystemError):
    """Quest validation error"""
    
    def __init__(self, message: str, validation_errors: Optional[Dict[str, Any]] = None):
        self.validation_errors = validation_errors or {}
        super().__init__(message, "QUEST_VALIDATION_ERROR", {"validation_errors": validation_errors})


class QuestStatusError(QuestSystemError):
    """Quest status error"""
    
    def __init__(self, current_status: str, attempted_status: str, message: str = None):
        self.current_status = current_status
        self.attempted_status = attempted_status
        message = message or f"Invalid status transition from {current_status} to {attempted_status}"
        super().__init__(message, "QUEST_STATUS_ERROR", {
            "current_status": current_status,
            "attempted_status": attempted_status
        })


class QuestChainError(QuestSystemError):
    """Quest chain error"""
    
    def __init__(self, chain_id: str, message: str, chain_errors: Optional[Dict[str, Any]] = None):
        self.chain_id = chain_id
        self.chain_errors = chain_errors or {}
        super().__init__(message, "QUEST_CHAIN_ERROR", {
            "chain_id": chain_id,
            "chain_errors": chain_errors
        })


class QuestGenerationError(QuestSystemError):
    """Quest generation error"""
    
    def __init__(self, message: str, generation_context: Optional[Dict[str, Any]] = None):
        self.generation_context = generation_context or {}
        super().__init__(message, "QUEST_GENERATION_ERROR", {"context": generation_context})


class QuestTemplateError(QuestSystemError):
    """Quest template error"""
    
    def __init__(self, template_id: str, message: str, template_errors: Optional[Dict[str, Any]] = None):
        self.template_id = template_id
        self.template_errors = template_errors or {}
        super().__init__(message, "QUEST_TEMPLATE_ERROR", {
            "template_id": template_id,
            "template_errors": template_errors
        })


class QuestDifficultyError(QuestSystemError):
    """Quest difficulty calculation error"""
    
    def __init__(self, message: str, difficulty_context: Optional[Dict[str, Any]] = None):
        self.difficulty_context = difficulty_context or {}
        super().__init__(message, "QUEST_DIFFICULTY_ERROR", {"context": difficulty_context})


class QuestCacheError(QuestSystemError):
    """Quest cache error"""
    
    def __init__(self, message: str, cache_key: Optional[str] = None):
        self.cache_key = cache_key
        super().__init__(message, "QUEST_CACHE_ERROR", {"cache_key": cache_key})


class QuestConflictError(QuestSystemError):
    """Quest conflict error (e.g., duplicate titles)"""
    
    def __init__(self, message: str, conflict_details: Optional[Dict[str, Any]] = None):
        self.conflict_details = conflict_details or {}
        super().__init__(message, "QUEST_CONFLICT_ERROR", {"conflict": conflict_details})


class QuestDependencyError(QuestSystemError):
    """Quest dependency error"""
    
    def __init__(self, message: str, dependency_details: Optional[Dict[str, Any]] = None):
        self.dependency_details = dependency_details or {}
        super().__init__(message, "QUEST_DEPENDENCY_ERROR", {"dependencies": dependency_details})


class QuestAccessError(QuestSystemError):
    """Quest access error (permissions, assignments)"""
    
    def __init__(self, message: str, access_details: Optional[Dict[str, Any]] = None):
        self.access_details = access_details or {}
        super().__init__(message, "QUEST_ACCESS_ERROR", {"access": access_details})


# Convenience functions for raising common exceptions
def quest_not_found(quest_id: str) -> QuestNotFoundError:
    """Create a quest not found error"""
    return QuestNotFoundError(quest_id)


def quest_validation_failed(message: str, errors: Dict[str, Any] = None) -> QuestValidationError:
    """Create a quest validation error"""
    return QuestValidationError(message, errors)


def quest_status_invalid(current: str, attempted: str) -> QuestStatusError:
    """Create a quest status error"""
    return QuestStatusError(current, attempted)


def quest_chain_invalid(chain_id: str, message: str, errors: Dict[str, Any] = None) -> QuestChainError:
    """Create a quest chain error"""
    return QuestChainError(chain_id, message, errors)


def quest_generation_failed(message: str, context: Dict[str, Any] = None) -> QuestGenerationError:
    """Create a quest generation error"""
    return QuestGenerationError(message, context) 