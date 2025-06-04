"""
Quest System Services - Pure Business Logic

This module provides business logic services for the quest system
according to the Development Bible standards.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from .models import (
    QuestData,
    QuestStepData,
    QuestRewardData,
    CreateQuestData,
    UpdateQuestData,
    QuestStatus,
    QuestDifficulty,
    QuestTheme,
    QuestRepository,
    QuestValidationService,
    QuestGenerationService
)

# Business Logic Exceptions
class QuestNotFoundError(Exception):
    """Quest not found error"""
    pass

class QuestValidationError(Exception):
    """Quest validation error"""
    pass

class QuestConflictError(Exception):
    """Quest conflict error"""
    pass


class QuestBusinessService:
    """Service class for quest business logic - pure business rules"""
    
    def __init__(self, 
                 quest_repository: QuestRepository,
                 validation_service: QuestValidationService,
                 generation_service: Optional[QuestGenerationService] = None):
        self.quest_repository = quest_repository
        self.validation_service = validation_service
        self.generation_service = generation_service
        
        # Business configuration
        self.config = {
            'max_active_quests_per_player': 10,
            'quest_expiry_days': 30,
            'auto_cleanup_completed_quests_days': 7,
            'max_abandoned_quests_memory': 5,
            'default_quest_level': 1,
            'min_quest_level': 1,
            'max_quest_level': 100
        }

    def create_quest(
        self, 
        create_data: CreateQuestData,
        user_id: Optional[UUID] = None
    ) -> QuestData:
        """Create a new quest with business validation"""
        # Convert to dict for validation
        quest_data_dict = {
            'title': create_data.title,
            'description': create_data.description,
            'difficulty': create_data.difficulty.value,
            'theme': create_data.theme.value,
            'npc_id': create_data.npc_id,
            'location_id': create_data.location_id,
            'level': create_data.level,
            'steps': create_data.steps,
            'rewards': create_data.rewards,
            'properties': create_data.properties,
            'expires_at': create_data.expires_at.isoformat() if create_data.expires_at else None
        }
        
        # Comprehensive validation and sanitization
        validated_data = self.validation_service.validate_quest_data(quest_data_dict)
        
        # Business rule: Check for existing quest with same title
        existing_quest = self.quest_repository.get_quest_by_title(validated_data['title'])
        if existing_quest:
            raise QuestConflictError(f"Quest with title '{validated_data['title']}' already exists")
        
        # Business rule: Validate level constraints
        level = validated_data.get('level', self.config['default_quest_level'])
        if level < self.config['min_quest_level'] or level > self.config['max_quest_level']:
            raise QuestValidationError(f"Quest level must be between {self.config['min_quest_level']} and {self.config['max_quest_level']}")
        
        # Business rule: Process and validate steps
        steps = []
        if validated_data.get('steps'):
            validated_steps = self.validation_service.validate_quest_steps(validated_data['steps'])
            for i, step_data in enumerate(validated_steps):
                step = QuestStepData(
                    id=step_data.get('id', i + 1),
                    title=step_data['title'],
                    description=step_data['description'],
                    completed=False,
                    required=step_data.get('required', True),
                    order=step_data.get('order', i),
                    metadata=step_data.get('metadata', {})
                )
                steps.append(step)
        
        # Business rule: Process and validate rewards
        rewards_data = validated_data.get('rewards', {})
        if rewards_data:
            validated_rewards = self.validation_service.validate_quest_rewards(rewards_data)
            rewards = QuestRewardData(
                gold=validated_rewards.get('gold', 0),
                experience=validated_rewards.get('experience', 0),
                reputation=validated_rewards.get('reputation', {}),
                items=validated_rewards.get('items', []),
                special=validated_rewards.get('special', {})
            )
        else:
            # Generate default rewards based on difficulty and level
            if self.generation_service:
                difficulty_enum = QuestDifficulty(validated_data.get('difficulty', 'medium'))
                rewards = self.generation_service.generate_quest_rewards(difficulty_enum, level)
            else:
                rewards = QuestRewardData()
        
        # Create business entity with validated data
        quest_entity = QuestData(
            id=uuid4(),
            title=validated_data['title'],
            description=validated_data['description'],
            status=QuestStatus.PENDING,
            difficulty=QuestDifficulty(validated_data.get('difficulty', 'medium')),
            theme=QuestTheme(validated_data.get('theme', 'general')),
            npc_id=validated_data.get('npc_id'),
            player_id=None,  # Set when quest is assigned
            location_id=validated_data.get('location_id'),
            level=level,
            steps=steps,
            rewards=rewards,
            properties=validated_data.get('properties', {}),
            created_at=datetime.utcnow(),
            expires_at=datetime.fromisoformat(validated_data['expires_at']) if validated_data.get('expires_at') else None
        )
        
        # Business rule: Add user tracking if provided
        if user_id:
            quest_entity.properties = quest_entity.properties or {}
            quest_entity.properties['created_by'] = str(user_id)
        
        # Persist via repository
        return self.quest_repository.create_quest(quest_entity)

    def get_quest_by_id(self, quest_id: UUID) -> Optional[QuestData]:
        """Get quest by ID"""
        return self.quest_repository.get_quest_by_id(quest_id)

    def update_quest(
        self, 
        quest_id: UUID, 
        update_data: UpdateQuestData
    ) -> QuestData:
        """Update existing quest with business rules"""
        # Business rule: Quest must exist
        entity = self.quest_repository.get_quest_by_id(quest_id)
        if not entity:
            raise QuestNotFoundError(f"Quest {quest_id} not found")
        
        # Apply updates with business validation
        update_fields = update_data.get_fields()
        if update_fields:
            # Business rule: Validate status transitions
            if 'status' in update_fields:
                new_status = QuestStatus(update_fields['status'])
                if not self._is_valid_status_transition(entity.status, new_status):
                    raise QuestValidationError(f"Invalid status transition from {entity.status.value} to {new_status.value}")
                entity.status = new_status
            
            # Business rule: Update other fields
            for field, value in update_fields.items():
                if field != 'status' and hasattr(entity, field):
                    if field in ['difficulty', 'theme']:
                        # Convert string to enum
                        enum_class = QuestDifficulty if field == 'difficulty' else QuestTheme
                        setattr(entity, field, enum_class(value))
                    else:
                        setattr(entity, field, value)
            
            entity.updated_at = datetime.utcnow()
        
        return self.quest_repository.update_quest(entity)

    def delete_quest(self, quest_id: UUID) -> bool:
        """Delete quest with business rules"""
        # Business rule: Quest must exist
        entity = self.quest_repository.get_quest_by_id(quest_id)
        if not entity:
            raise QuestNotFoundError(f"Quest {quest_id} not found")
        
        # Business rule: Cannot delete active quests assigned to players
        if entity.player_id and entity.status == QuestStatus.ACTIVE:
            raise QuestValidationError("Cannot delete active quest assigned to a player")
        
        return self.quest_repository.delete_quest(quest_id)

    def list_quests(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[QuestData], int]:
        """List quests with pagination and filtering"""
        return self.quest_repository.list_quests(page, size, status, search)

    def get_quest_statistics(self) -> Dict[str, Any]:
        """Get quest statistics"""
        return self.quest_repository.get_quest_statistics()

    def assign_quest_to_player(self, quest_id: UUID, player_id: str) -> QuestData:
        """Business logic: Assign quest to player"""
        quest = self.quest_repository.get_quest_by_id(quest_id)
        if not quest:
            raise QuestNotFoundError(f"Quest {quest_id} not found")
        
        # Business rule: Quest must be pending
        if quest.status != QuestStatus.PENDING:
            raise QuestValidationError(f"Quest must be pending to assign to player")
        
        # Business rule: Check player quest limits
        player_quests = self.quest_repository.get_player_quests(player_id, "active")
        if len(player_quests) >= self.config['max_active_quests_per_player']:
            raise QuestValidationError(f"Player has reached maximum active quests limit")
        
        # Assign quest
        quest.player_id = player_id
        quest.status = QuestStatus.ACTIVE
        quest.updated_at = datetime.utcnow()
        
        return self.quest_repository.update_quest(quest)

    def complete_quest_step(self, quest_id: UUID, step_id: int, player_id: str) -> QuestData:
        """Business logic: Complete a quest step"""
        quest = self.quest_repository.get_quest_by_id(quest_id)
        if not quest:
            raise QuestNotFoundError(f"Quest {quest_id} not found")
        
        # Business rule: Quest must be assigned to this player
        if quest.player_id != player_id:
            raise QuestValidationError("Quest is not assigned to this player")
        
        # Business rule: Quest must be active
        if quest.status != QuestStatus.ACTIVE:
            raise QuestValidationError("Quest must be active to complete steps")
        
        # Complete the step
        if not quest.complete_step(step_id):
            raise QuestValidationError(f"Step {step_id} not found in quest")
        
        # Check if quest is now complete
        if quest.is_completed():
            quest.status = QuestStatus.COMPLETED
        
        quest.updated_at = datetime.utcnow()
        
        return self.quest_repository.update_quest(quest)

    def abandon_quest(self, quest_id: UUID, player_id: str, reason: str = "player_choice") -> QuestData:
        """Business logic: Abandon a quest"""
        quest = self.quest_repository.get_quest_by_id(quest_id)
        if not quest:
            raise QuestNotFoundError(f"Quest {quest_id} not found")
        
        # Business rule: Quest must be assigned to this player
        if quest.player_id != player_id:
            raise QuestValidationError("Quest is not assigned to this player")
        
        # Business rule: Quest must be active
        if quest.status != QuestStatus.ACTIVE:
            raise QuestValidationError("Only active quests can be abandoned")
        
        # Abandon quest
        quest.status = QuestStatus.ABANDONED
        quest.properties = quest.properties or {}
        quest.properties['abandon_reason'] = reason
        quest.properties['abandoned_at'] = datetime.utcnow().isoformat()
        quest.updated_at = datetime.utcnow()
        
        return self.quest_repository.update_quest(quest)

    def get_player_quests(self, player_id: str, status: Optional[str] = None) -> List[QuestData]:
        """Get quests for a specific player"""
        return self.quest_repository.get_player_quests(player_id, status)

    def get_available_quests_for_player(self, player_id: str, location_id: Optional[str] = None) -> List[QuestData]:
        """Business logic: Get available quests for a player"""
        # Get pending quests
        if location_id:
            available_quests = self.quest_repository.get_location_quests(location_id, "pending")
        else:
            all_quests, _ = self.quest_repository.list_quests(status="pending")
            available_quests = all_quests
        
        # Business rule: Filter out expired quests
        current_time = datetime.utcnow()
        valid_quests = []
        for quest in available_quests:
            if quest.expires_at and quest.expires_at < current_time:
                continue
            valid_quests.append(quest)
        
        return valid_quests

    def generate_quest_for_npc(self, npc_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[QuestData]:
        """Business logic: Generate a quest for an NPC"""
        if not self.generation_service:
            return None
        
        return self.generation_service.generate_quest_for_npc(npc_data, context)

    def calculate_quest_difficulty_score(self, quest: QuestData) -> float:
        """Business logic: Calculate difficulty score for a quest"""
        base_score = {
            QuestDifficulty.EASY: 1.0,
            QuestDifficulty.MEDIUM: 2.0,
            QuestDifficulty.HARD: 3.0,
            QuestDifficulty.EPIC: 5.0
        }.get(quest.difficulty, 2.0)
        
        # Adjust for level
        level_multiplier = 1.0 + (quest.level - 1) * 0.1
        
        # Adjust for number of steps
        step_multiplier = 1.0 + (len(quest.steps) - 1) * 0.2
        
        return base_score * level_multiplier * step_multiplier

    def _is_valid_status_transition(self, current_status: QuestStatus, new_status: QuestStatus) -> bool:
        """Business rule: Validate status transitions"""
        valid_transitions = {
            QuestStatus.PENDING: [QuestStatus.ACTIVE, QuestStatus.EXPIRED],
            QuestStatus.ACTIVE: [QuestStatus.COMPLETED, QuestStatus.FAILED, QuestStatus.ABANDONED],
            QuestStatus.COMPLETED: [],  # Terminal state
            QuestStatus.FAILED: [QuestStatus.PENDING],  # Can be retried
            QuestStatus.ABANDONED: [QuestStatus.PENDING],  # Can be retried
            QuestStatus.EXPIRED: [QuestStatus.PENDING]  # Can be renewed
        }
        
        return new_status in valid_transitions.get(current_status, [])
