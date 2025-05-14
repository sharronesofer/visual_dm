"""
Service layer for managing quests and related operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from app.core.models.quest_system import (
    Quest, QuestStage, QuestReward, QuestWorldImpact,
    QuestType, QuestStatus, QuestCondition
)
from app.core.database import db
from app.core.services.time_service import TimeService
from app.core.services.character_service import CharacterService
from app.core.services.inventory_service import InventoryService
from app.core.services.faction_service import FactionService
from app.core.services.world_state_service import WorldStateService

class QuestService:
    """Service for managing quest-related operations."""
    
    def __init__(
        self,
        session: Session,
        time_service: TimeService,
        character_service: CharacterService,
        inventory_service: InventoryService,
        faction_service: FactionService,
        world_state_service: WorldStateService
    ):
        self.session = session
        self.time_service = time_service
        self.character_service = character_service
        self.inventory_service = inventory_service
        self.faction_service = faction_service
        self.world_state_service = world_state_service
        
    def get_available_quests(self, character_id: int) -> List[Quest]:
        """
        Get all quests currently available to a character.
        
        Args:
            character_id: ID of the character to check quests for
            
        Returns:
            List of available quests
        """
        # Get current game state for availability checks
        game_state = self._get_game_state(character_id)
        
        # Query all non-completed quests
        quests = self.session.query(Quest).filter(
            Quest.status.in_([QuestStatus.HIDDEN, QuestStatus.LOCKED])
        ).all()
        
        # Filter to only those that should be available
        available_quests = []
        for quest in quests:
            if quest.check_availability(game_state):
                quest.status = QuestStatus.AVAILABLE
                available_quests.append(quest)
                
        self.session.commit()
        return available_quests
        
    def get_active_quests(self, character_id: int) -> List[Quest]:
        """
        Get all currently active quests for a character.
        
        Args:
            character_id: ID of the character to get quests for
            
        Returns:
            List of active quests
        """
        return self.session.query(Quest).filter(
            Quest.status == QuestStatus.ACTIVE
        ).all()
        
    def start_quest(self, quest_id: int, character_id: int) -> Tuple[bool, str]:
        """
        Attempt to start a quest for a character.
        
        Args:
            quest_id: ID of the quest to start
            character_id: ID of the character starting the quest
            
        Returns:
            Tuple of (success, message)
        """
        quest = self.session.query(Quest).get(quest_id)
        if not quest:
            return False, "Quest not found"
            
        # Verify character meets requirements
        game_state = self._get_game_state(character_id)
        if not quest.check_availability(game_state):
            return False, "Requirements not met"
            
        # Start the quest
        if not quest.start(character_id):
            return False, "Failed to start quest"
            
        self.session.commit()
        return True, "Quest started successfully"
        
    def update_quest_progress(
        self,
        character_id: int,
        quest_id: int,
        progress_data: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Update progress on a quest based on character actions.
        
        Args:
            character_id: ID of the character
            quest_id: ID of the quest to update
            progress_data: Data about the progress made
            
        Returns:
            Tuple of (success, message)
        """
        quest = self.session.query(Quest).get(quest_id)
        if not quest or quest.status != QuestStatus.ACTIVE:
            return False, "Quest not found or not active"
            
        # Get current game state
        game_state = self._get_game_state(character_id)
        game_state.update(progress_data)
        
        # Try to advance the quest
        if quest.advance_stage(game_state):
            # Apply any world impacts from the completed stage
            self._apply_stage_impacts(quest.current_stage)
            
            # Award any stage-specific rewards
            self._award_stage_rewards(quest.current_stage, character_id)
            
            self.session.commit()
            return True, "Quest progress updated"
            
        return False, "Failed to update quest progress"
        
    def complete_quest(self, quest_id: int, character_id: int) -> Tuple[bool, str]:
        """
        Mark a quest as completed and handle completion effects.
        
        Args:
            quest_id: ID of the quest to complete
            character_id: ID of the character completing the quest
            
        Returns:
            Tuple of (success, message)
        """
        quest = self.session.query(Quest).get(quest_id)
        if not quest or quest.status != QuestStatus.ACTIVE:
            return False, "Quest not found or not active"
            
        # Verify all stages are complete
        if any(not stage.completed_at for stage in quest.stages if not stage.is_optional):
            return False, "Not all required stages are complete"
            
        # Complete the quest
        quest.complete()
        
        # Award quest rewards
        self._award_quest_rewards(quest, character_id)
        
        # Apply final world impacts
        self._apply_quest_impacts(quest)
        
        # Handle repeatable quests
        if quest.is_repeatable:
            quest.reset()
            
        self.session.commit()
        return True, "Quest completed successfully"
        
    def fail_quest(self, quest_id: int, character_id: int) -> Tuple[bool, str]:
        """
        Mark a quest as failed.
        
        Args:
            quest_id: ID of the quest to fail
            character_id: ID of the character failing the quest
            
        Returns:
            Tuple of (success, message)
        """
        quest = self.session.query(Quest).get(quest_id)
        if not quest or quest.status != QuestStatus.ACTIVE:
            return False, "Quest not found or not active"
            
        quest.fail()
        
        # Handle repeatable quests
        if quest.is_repeatable:
            quest.reset()
            
        self.session.commit()
        return True, "Quest failed"
        
    def abandon_quest(self, quest_id: int, character_id: int) -> Tuple[bool, str]:
        """
        Allow a character to abandon an active quest.
        
        Args:
            quest_id: ID of the quest to abandon
            character_id: ID of the character abandoning the quest
            
        Returns:
            Tuple of (success, message)
        """
        quest = self.session.query(Quest).get(quest_id)
        if not quest or quest.status != QuestStatus.ACTIVE:
            return False, "Quest not found or not active"
            
        quest.fail()  # Use fail to track attempt
        
        # Handle repeatable quests
        if quest.is_repeatable:
            quest.reset()
            
        self.session.commit()
        return True, "Quest abandoned"
        
    def _get_game_state(self, character_id: int) -> Dict[str, Any]:
        """
        Get the current game state relevant for quest operations.
        
        Args:
            character_id: ID of the character to get state for
            
        Returns:
            Dictionary containing current game state
        """
        character = self.character_service.get_character(character_id)
        return {
            'character': character,
            'inventory': self.inventory_service.get_inventory(character_id),
            'time': self.time_service.get_current_time(),
            'world_state': self.world_state_service.get_current_state(),
            'faction_standings': self.faction_service.get_standings(character_id)
        }
        
    def _award_stage_rewards(self, stage: QuestStage, character_id: int) -> None:
        """
        Award any rewards associated with completing a quest stage.
        
        Args:
            stage: The completed quest stage
            character_id: ID of the character to reward
        """
        if not stage.rewards:
            return
            
        game_state = self._get_game_state(character_id)
        
        for reward in stage.rewards:
            if all(QuestCondition(**c).evaluate(game_state) for c in reward.conditions):
                self._apply_reward(reward, character_id)
                
    def _award_quest_rewards(self, quest: Quest, character_id: int) -> None:
        """
        Award all rewards associated with completing a quest.
        
        Args:
            quest: The completed quest
            character_id: ID of the character to reward
        """
        game_state = self._get_game_state(character_id)
        
        for reward in quest.rewards:
            if all(QuestCondition(**c).evaluate(game_state) for c in reward.conditions):
                self._apply_reward(reward, character_id)
                
    def _apply_reward(self, reward: QuestReward, character_id: int) -> None:
        """
        Apply a specific reward to a character.
        
        Args:
            reward: The reward to apply
            character_id: ID of the character to reward
        """
        if reward.reward_type == 'item':
            self.inventory_service.add_item(
                character_id,
                reward.value['item_id'],
                reward.value.get('quantity', 1)
            )
        elif reward.reward_type == 'experience':
            self.character_service.add_experience(
                character_id,
                reward.value['amount']
            )
        elif reward.reward_type == 'faction_standing':
            self.faction_service.modify_standing(
                character_id,
                reward.value['faction_id'],
                reward.value['amount']
            )
        # Add other reward types as needed
                
    def _apply_stage_impacts(self, stage: QuestStage) -> None:
        """
        Apply any world impacts associated with completing a quest stage.
        
        Args:
            stage: The completed quest stage
        """
        for impact in stage.world_impacts:
            self._apply_impact(impact)
            
    def _apply_quest_impacts(self, quest: Quest) -> None:
        """
        Apply any world impacts associated with completing a quest.
        
        Args:
            quest: The completed quest
        """
        for impact in quest.world_impacts:
            self._apply_impact(impact)
            
    def _apply_impact(self, impact: QuestWorldImpact) -> None:
        """
        Apply a specific world impact.
        
        Args:
            impact: The impact to apply
        """
        # Schedule the impact if it has a trigger time
        if impact.trigger_time and impact.trigger_time > datetime.utcnow():
            self.time_service.schedule_event(
                impact.trigger_time,
                lambda: self.world_state_service.apply_impact(
                    impact.impact_type,
                    impact.details
                )
            )
        else:
            # Apply immediately
            self.world_state_service.apply_impact(
                impact.impact_type,
                impact.details
            ) 