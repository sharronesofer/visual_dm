"""
Pure business logic validation utilities for the quest system.
No external dependencies - only pure functions and business rules.
"""

from typing import Dict, List, Optional, Any
from ..models import QuestStatus, QuestDifficulty, QuestTheme, Quest, QuestStep


def validate_status_transition(from_status: QuestStatus, to_status: QuestStatus) -> bool:
    """
    Validate if a quest status transition is allowed based on business rules.
    
    Args:
        from_status: Current quest status
        to_status: Target quest status
        
    Returns:
        True if transition is valid, False otherwise
    """
    valid_transitions = {
        QuestStatus.PENDING: [QuestStatus.ACTIVE, QuestStatus.ABANDONED],
        QuestStatus.ACTIVE: [
            QuestStatus.COMPLETED, 
            QuestStatus.FAILED, 
            QuestStatus.ABANDONED, 
            QuestStatus.EXPIRED
        ],
        QuestStatus.COMPLETED: [],  # Terminal state
        QuestStatus.FAILED: [QuestStatus.PENDING],  # Can retry
        QuestStatus.ABANDONED: [QuestStatus.PENDING],  # Can retry  
        QuestStatus.EXPIRED: [QuestStatus.PENDING],  # Can retry
    }
    
    allowed_next_states = valid_transitions.get(from_status, [])
    return to_status in allowed_next_states


def validate_quest_level_for_difficulty(level: int, difficulty: QuestDifficulty) -> bool:
    """
    Validate if quest level is appropriate for the difficulty.
    
    Args:
        level: Quest level
        difficulty: Quest difficulty
        
    Returns:
        True if level is appropriate for difficulty
    """
    level_ranges = {
        QuestDifficulty.EASY: (1, 10),
        QuestDifficulty.MEDIUM: (5, 20), 
        QuestDifficulty.HARD: (15, 40),
        QuestDifficulty.EPIC: (30, 100)
    }
    
    min_level, max_level = level_ranges.get(difficulty, (1, 100))
    return min_level <= level <= max_level


def calculate_quest_complexity_score(quest: Quest) -> int:
    """
    Calculate a complexity score for a quest based on business rules.
    
    Args:
        quest: Quest to analyze
        
    Returns:
        Complexity score from 1-10
    """
    score = 1
    
    # Base difficulty scoring
    difficulty_scores = {
        QuestDifficulty.EASY: 1,
        QuestDifficulty.MEDIUM: 3,
        QuestDifficulty.HARD: 6,
        QuestDifficulty.EPIC: 8
    }
    score += difficulty_scores.get(quest.difficulty, 1)
    
    # Add complexity for number of steps
    if quest.steps:
        step_count = len(quest.steps)
        if step_count > 5:
            score += 2
        elif step_count > 2:
            score += 1
    
    # Add complexity for multi-step dependencies
    if quest.steps:
        required_steps = sum(1 for step in quest.steps if step.required)
        if required_steps >= len(quest.steps):  # All steps required
            score += 1
    
    # Theme-based complexity adjustments
    complex_themes = [QuestTheme.MYSTERY, QuestTheme.SOCIAL, QuestTheme.KNOWLEDGE]
    if quest.theme in complex_themes:
        score += 1
    
    # Cap at 10
    return min(score, 10)


def validate_quest_rewards(rewards: Dict[str, Any], difficulty: QuestDifficulty) -> List[str]:
    """
    Validate quest rewards are appropriate for difficulty level.
    
    Args:
        rewards: Quest rewards dictionary
        difficulty: Quest difficulty
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Minimum reward thresholds by difficulty
    min_rewards = {
        QuestDifficulty.EASY: {'gold': 10, 'experience': 25},
        QuestDifficulty.MEDIUM: {'gold': 50, 'experience': 100},
        QuestDifficulty.HARD: {'gold': 150, 'experience': 300},
        QuestDifficulty.EPIC: {'gold': 500, 'experience': 1000}
    }
    
    min_threshold = min_rewards.get(difficulty, min_rewards[QuestDifficulty.EASY])
    
    # Check gold rewards
    gold = rewards.get('gold', 0)
    if gold < min_threshold['gold']:
        errors.append(f"Gold reward too low for {difficulty.value} difficulty. "
                     f"Minimum: {min_threshold['gold']}, got: {gold}")
    
    # Check experience rewards
    exp = rewards.get('experience', 0)
    if exp < min_threshold['experience']:
        errors.append(f"Experience reward too low for {difficulty.value} difficulty. "
                     f"Minimum: {min_threshold['experience']}, got: {exp}")
    
    return errors


def validate_quest_steps_order(steps: List[QuestStep]) -> List[str]:
    """
    Validate quest steps have proper ordering and structure.
    
    Args:
        steps: List of quest steps
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if not steps:
        return errors
    
    # Check for duplicate IDs
    step_ids = [step.id for step in steps]
    if len(step_ids) != len(set(step_ids)):
        errors.append("Duplicate step IDs found")
    
    # Check for proper order sequence
    orders = [step.order for step in steps]
    expected_orders = list(range(1, len(steps) + 1))
    if sorted(orders) != expected_orders:
        errors.append(f"Step orders should be consecutive starting from 1. "
                     f"Expected: {expected_orders}, got: {sorted(orders)}")
    
    # Check that at least one step is required
    required_steps = [step for step in steps if step.required]
    if not required_steps:
        errors.append("At least one step must be required")
    
    return errors


def calculate_reward_multiplier(difficulty: QuestDifficulty) -> float:
    """
    Calculate reward multiplier based on difficulty.
    
    Args:
        difficulty: Quest difficulty
        
    Returns:
        Multiplier for rewards (1.0x to 3.0x)
    """
    multipliers = {
        QuestDifficulty.EASY: 1.0,
        QuestDifficulty.MEDIUM: 1.5,
        QuestDifficulty.HARD: 2.0,
        QuestDifficulty.EPIC: 3.0
    }
    return multipliers.get(difficulty, 1.0)


def is_quest_completable(quest: Quest) -> bool:
    """
    Check if a quest can be completed based on its current state.
    
    Args:
        quest: Quest to check
        
    Returns:
        True if quest can be completed
    """
    # Must be active
    if quest.status != QuestStatus.ACTIVE:
        return False
    
    # All required steps must be completed
    if quest.steps:
        required_steps = [step for step in quest.steps if step.required]
        completed_required = [step for step in required_steps if step.completed]
        return len(completed_required) == len(required_steps)
    
    # If no steps, quest is completable
    return True


def get_theme_typical_objectives(theme: QuestTheme) -> List[str]:
    """
    Get typical objective types for a quest theme.
    
    Args:
        theme: Quest theme
        
    Returns:
        List of typical objective types
    """
    theme_objectives = {
        QuestTheme.COMBAT: ["eliminate", "defeat", "survive", "protect"],
        QuestTheme.EXPLORATION: ["discover", "visit", "map", "scout", "find"],
        QuestTheme.SOCIAL: ["talk", "negotiate", "befriend", "persuade"],
        QuestTheme.MYSTERY: ["investigate", "gather_clues", "solve", "uncover"],
        QuestTheme.CRAFTING: ["create", "gather_materials", "craft", "build"],
        QuestTheme.TRADE: ["buy", "sell", "negotiate", "transport", "deliver"],
        QuestTheme.AID: ["help", "assist", "heal", "rescue", "support"],
        QuestTheme.KNOWLEDGE: ["research", "learn", "study", "teach", "document"],
        QuestTheme.GENERAL: ["complete", "finish", "accomplish", "achieve"]
    }
    return theme_objectives.get(theme, []) 