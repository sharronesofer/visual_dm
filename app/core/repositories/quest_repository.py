"""
Repository layer for quest-related database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from app.core.models.quest_system import (
    Quest, QuestStage, QuestReward, QuestWorldImpact,
    QuestType, QuestStatus
)

class QuestRepository:
    """Repository for managing quest-related database operations."""
    
    def __init__(self, session: Session):
        self.session = session
        
    def create_quest(self, quest_data: Dict[str, Any]) -> Quest:
        """
        Create a new quest in the database.
        
        Args:
            quest_data: Dictionary containing quest data
            
        Returns:
            Created Quest instance
        """
        quest = Quest(**quest_data)
        self.session.add(quest)
        self.session.commit()
        return quest
        
    def get_quest(self, quest_id: int) -> Optional[Quest]:
        """
        Get a quest by ID.
        
        Args:
            quest_id: ID of the quest to retrieve
            
        Returns:
            Quest if found, None otherwise
        """
        return self.session.query(Quest).get(quest_id)
        
    def get_quests_by_status(self, status: QuestStatus) -> List[Quest]:
        """
        Get all quests with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of quests with the specified status
        """
        return self.session.query(Quest).filter(Quest.status == status).all()
        
    def get_quests_by_type(self, quest_type: QuestType) -> List[Quest]:
        """
        Get all quests of a specific type.
        
        Args:
            quest_type: Type to filter by
            
        Returns:
            List of quests of the specified type
        """
        return self.session.query(Quest).filter(Quest.type == quest_type).all()
        
    def get_available_quests(
        self,
        level: int,
        faction_id: Optional[int] = None,
        location_id: Optional[int] = None
    ) -> List[Quest]:
        """
        Get quests that are potentially available based on basic criteria.
        
        Args:
            level: Character level to check against
            faction_id: Optional faction ID to filter by
            location_id: Optional location ID to filter by
            
        Returns:
            List of potentially available quests
        """
        filters = [
            Quest.status.in_([QuestStatus.HIDDEN, QuestStatus.LOCKED]),
            Quest.level_requirement <= level
        ]
        
        if faction_id is not None:
            filters.append(Quest.faction_id == faction_id)
            
        if location_id is not None:
            filters.append(Quest.location_id == location_id)
            
        return self.session.query(Quest).filter(and_(*filters)).all()
        
    def get_active_quests_for_character(self, character_id: int) -> List[Quest]:
        """
        Get all active quests for a specific character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            List of active quests
        """
        # Note: This assumes a character_quests association table exists
        # Implementation will be updated when character system is implemented
        return self.session.query(Quest).filter(
            Quest.status == QuestStatus.ACTIVE
        ).all()
        
    def get_completed_quests_for_character(self, character_id: int) -> List[Quest]:
        """
        Get all completed quests for a specific character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            List of completed quests
        """
        # Note: This assumes a character_quests association table exists
        # Implementation will be updated when character system is implemented
        return self.session.query(Quest).filter(
            Quest.status == QuestStatus.COMPLETED
        ).all()
        
    def get_quest_stages(self, quest_id: int) -> List[QuestStage]:
        """
        Get all stages for a specific quest.
        
        Args:
            quest_id: ID of the quest
            
        Returns:
            List of quest stages in order
        """
        return self.session.query(QuestStage).filter(
            QuestStage.quest_id == quest_id
        ).order_by(QuestStage.order).all()
        
    def get_quest_rewards(self, quest_id: int) -> List[QuestReward]:
        """
        Get all rewards for a specific quest.
        
        Args:
            quest_id: ID of the quest
            
        Returns:
            List of quest rewards
        """
        return self.session.query(QuestReward).filter(
            QuestReward.quest_id == quest_id
        ).all()
        
    def get_quest_impacts(self, quest_id: int) -> List[QuestWorldImpact]:
        """
        Get all world impacts for a specific quest.
        
        Args:
            quest_id: ID of the quest
            
        Returns:
            List of quest world impacts
        """
        return self.session.query(QuestWorldImpact).filter(
            QuestWorldImpact.quest_id == quest_id
        ).all()
        
    def update_quest(self, quest_id: int, update_data: Dict[str, Any]) -> Optional[Quest]:
        """
        Update a quest's data.
        
        Args:
            quest_id: ID of the quest to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated Quest if found, None otherwise
        """
        quest = self.get_quest(quest_id)
        if not quest:
            return None
            
        for key, value in update_data.items():
            setattr(quest, key, value)
            
        self.session.commit()
        return quest
        
    def delete_quest(self, quest_id: int) -> bool:
        """
        Delete a quest and all related data.
        
        Args:
            quest_id: ID of the quest to delete
            
        Returns:
            True if quest was deleted, False if not found
        """
        quest = self.get_quest(quest_id)
        if not quest:
            return False
            
        # Delete related entities
        self.session.query(QuestStage).filter(
            QuestStage.quest_id == quest_id
        ).delete()
        
        self.session.query(QuestReward).filter(
            QuestReward.quest_id == quest_id
        ).delete()
        
        self.session.query(QuestWorldImpact).filter(
            QuestWorldImpact.quest_id == quest_id
        ).delete()
        
        self.session.delete(quest)
        self.session.commit()
        return True
        
    def create_quest_stage(self, stage_data: Dict[str, Any]) -> QuestStage:
        """
        Create a new quest stage.
        
        Args:
            stage_data: Dictionary containing stage data
            
        Returns:
            Created QuestStage instance
        """
        stage = QuestStage(**stage_data)
        self.session.add(stage)
        self.session.commit()
        return stage
        
    def create_quest_reward(self, reward_data: Dict[str, Any]) -> QuestReward:
        """
        Create a new quest reward.
        
        Args:
            reward_data: Dictionary containing reward data
            
        Returns:
            Created QuestReward instance
        """
        reward = QuestReward(**reward_data)
        self.session.add(reward)
        self.session.commit()
        return reward
        
    def create_quest_impact(self, impact_data: Dict[str, Any]) -> QuestWorldImpact:
        """
        Create a new quest world impact.
        
        Args:
            impact_data: Dictionary containing impact data
            
        Returns:
            Created QuestWorldImpact instance
        """
        impact = QuestWorldImpact(**impact_data)
        self.session.add(impact)
        self.session.commit()
        return impact
        
    def get_expired_quests(self) -> List[Quest]:
        """
        Get all quests that have expired based on their end date.
        
        Returns:
            List of expired quests
        """
        now = datetime.utcnow()
        return self.session.query(Quest).filter(
            and_(
                Quest.end_date.isnot(None),
                Quest.end_date < now,
                Quest.status.in_([
                    QuestStatus.AVAILABLE,
                    QuestStatus.ACTIVE,
                    QuestStatus.HIDDEN,
                    QuestStatus.LOCKED
                ])
            )
        ).all()
        
    def get_repeatable_quests_ready(self) -> List[Quest]:
        """
        Get all repeatable quests that are ready to be reset.
        
        Returns:
            List of repeatable quests ready for reset
        """
        now = datetime.utcnow()
        return self.session.query(Quest).filter(
            and_(
                Quest.is_repeatable == True,
                Quest.status == QuestStatus.COMPLETED,
                Quest.completed_at + Quest.cooldown_time < now
            )
        ).all()
        
    def get_quests_by_location(self, location_id: int) -> List[Quest]:
        """
        Get all quests available at a specific location.
        
        Args:
            location_id: ID of the location
            
        Returns:
            List of quests at the location
        """
        return self.session.query(Quest).filter(
            Quest.location_id == location_id
        ).all()
        
    def get_quests_by_npc(self, npc_id: int) -> List[Quest]:
        """
        Get all quests given by a specific NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            List of quests given by the NPC
        """
        return self.session.query(Quest).filter(
            Quest.giver_npc_id == npc_id
        ).all()
        
    def get_quests_by_faction(self, faction_id: int) -> List[Quest]:
        """
        Get all quests associated with a specific faction.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            List of faction quests
        """
        return self.session.query(Quest).filter(
            Quest.faction_id == faction_id
        ).all() 