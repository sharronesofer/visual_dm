"""Utils for quest system - Business Logic Utilities Only"""

# All technical utilities have been moved to backend/infrastructure/utils/
# This module now contains only pure business logic utilities

# Quest business logic utilities
class QuestBusinessUtils:
    """Pure business logic utilities for quests"""
    
    @staticmethod
    def calculate_quest_priority_score(quest_data: dict) -> float:
        """Calculate priority score based on business rules"""
        base_score = 1.0
        
        # Higher level quests have higher priority
        level_multiplier = 1.0 + (quest_data.get('level', 1) - 1) * 0.1
        
        # Difficulty affects priority
        difficulty_multipliers = {
            'easy': 1.0,
            'medium': 1.2,
            'hard': 1.5,
            'epic': 2.0
        }
        difficulty_multiplier = difficulty_multipliers.get(quest_data.get('difficulty', 'medium'), 1.0)
        
        # NPC importance affects priority
        npc_importance = quest_data.get('npc_importance', 1)
        importance_multiplier = 1.0 + (npc_importance - 1) * 0.2
        
        return base_score * level_multiplier * difficulty_multiplier * importance_multiplier
    
    @staticmethod
    def validate_quest_step_order(steps: list) -> bool:
        """Validate that quest steps are in proper order"""
        if not steps:
            return True
        
        for i, step in enumerate(steps):
            if step.get('order', i) != i:
                return False
        return True
    
    @staticmethod
    def calculate_estimated_completion_time(quest_data: dict) -> int:
        """Calculate estimated completion time in minutes based on business rules"""
        base_time = 30  # 30 minutes base
        
        # Add time based on number of steps
        steps_count = len(quest_data.get('steps', []))
        step_time = steps_count * 15  # 15 minutes per step
        
        # Add time based on difficulty
        difficulty_time = {
            'easy': 0,
            'medium': 15,
            'hard': 30,
            'epic': 60
        }.get(quest_data.get('difficulty', 'medium'), 15)
        
        return base_time + step_time + difficulty_time


__all__ = [
    "QuestBusinessUtils"
]
