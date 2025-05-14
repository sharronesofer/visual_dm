from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.models.quest import Quest, QuestStage, QuestDependency, QuestReward, QuestWorldImpact
from app.core.database import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class QuestService:
    """Service for managing quests and quest stages."""
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or db.session

    def create_quest(self, quest_data: Dict[str, Any], stages: Optional[List[Dict[str, Any]]] = None) -> Quest:
        """Create a new quest with optional stages."""
        try:
            quest = Quest(**quest_data)
            self.db_session.add(quest)
            self.db_session.flush()  # Get quest.id
            if stages:
                for idx, stage_data in enumerate(stages):
                    stage = QuestStage(quest_id=quest.id, order=idx, **stage_data)
                    self.db_session.add(stage)
            self.db_session.commit()
            return quest
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise RuntimeError(f"Failed to create quest: {e}")

    def get_quest(self, quest_id: int) -> Optional[Quest]:
        """Retrieve a quest by ID."""
        return self.db_session.query(Quest).get(quest_id)

    def get_all_quests(self) -> List[Quest]:
        """Retrieve all quests."""
        return self.db_session.query(Quest).all()

    def update_quest_stage(self, quest_id: int, stage_id: int, update_data: Dict[str, Any]) -> Optional[QuestStage]:
        """Update a quest stage's data."""
        stage = self.db_session.query(QuestStage).filter_by(quest_id=quest_id, id=stage_id).first()
        if not stage:
            return None
        for key, value in update_data.items():
            setattr(stage, key, value)
        try:
            self.db_session.commit()
            return stage
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise RuntimeError(f"Failed to update quest stage: {e}")

    def complete_quest_stage(self, quest_id: int, stage_id: int) -> bool:
        """Mark a quest stage as completed and check if quest is complete."""
        stage = self.db_session.query(QuestStage).filter_by(quest_id=quest_id, id=stage_id).first()
        if not stage:
            return False
        stage.completion_criteria['completed'] = True
        try:
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise RuntimeError(f"Failed to complete quest stage: {e}")
        # Check if all stages are complete
        stages = self.db_session.query(QuestStage).filter_by(quest_id=quest_id).all()
        if all(s.completion_criteria.get('completed') for s in stages):
            quest = self.db_session.query(Quest).get(quest_id)
            if quest:
                quest.status = quest.QuestStatus.COMPLETED
                self.db_session.commit()
        return True

    def abandon_quest(self, quest_id: int) -> bool:
        """Abandon a quest (mark as failed)."""
        quest = self.db_session.query(Quest).get(quest_id)
        if not quest:
            return False
        quest.status = quest.QuestStatus.FAILED
        try:
            self.db_session.commit()
            return True
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise RuntimeError(f"Failed to abandon quest: {e}")

    def check_prerequisites(self, quest_id: int, player_completed_quests: List[int]) -> bool:
        """Check if all prerequisites for a quest are met by the player."""
        quest = self.db_session.query(Quest).get(quest_id)
        if not quest:
            return False
        for prereq_id in quest.prerequisites:
            if prereq_id not in player_completed_quests:
                return False
        return True

    def get_available_quests_for_player(self, player_completed_quests: List[int]) -> List[Quest]:
        """Return all quests for which the player meets prerequisites."""
        all_quests = self.db_session.query(Quest).all()
        return [q for q in all_quests if self.check_prerequisites(q.id, player_completed_quests)]

    def progress_quest_stage(self, quest_id: int, character_id: int, branch_id: Any) -> bool:
        """Progress the quest to the next stage based on chosen branch."""
        quest = self.get_quest(quest_id)
        if not quest or not quest.stages:
            return False
        # Find current stage
        current_stage = None
        for stage in quest.stages:
            if not stage.completed_at:
                current_stage = stage
                break
        if not current_stage:
            return False
        # Find the branch in current stage's completion_criteria (assume branches are stored there)
        branches = current_stage.completion_criteria.get('branches', [])
        next_stage_id = None
        for branch in branches:
            if branch.get('id') == branch_id:
                next_stage_id = branch.get('next_stage_id')
                break
        if next_stage_id is None:
            return False
        # Mark current stage as completed
        current_stage.completed_at = datetime.utcnow()
        # Set quest's current_stage_id to next_stage_id, or mark quest as completed if no next stage
        next_stage = self.db_session.query(QuestStage).filter_by(id=next_stage_id).first() if next_stage_id else None
        if next_stage:
            quest.current_stage_id = next_stage_id
        else:
            quest.status = quest.QuestStatus.COMPLETED
            quest.completed_at = datetime.utcnow()
        try:
            self.db_session.commit()
            return True
        except SQLAlchemyError as e:
            self.db_session.rollback()
            return False

    def add_branching_path(self, quest_id: int, branch_data: Dict[str, Any]) -> None:
        """Add a branching path to a quest (stores in QuestWorldImpact for now). If branch_id is present, progress quest stage."""
        branch_id = branch_data.get('branch_id')
        if branch_id is not None:
            # Progress quest stage if branch_id is provided
            character_id = branch_data.get('character_id')
            if character_id is not None:
                self.progress_quest_stage(quest_id, character_id, branch_id)
        impact = QuestWorldImpact(quest_id=quest_id, impact_type='branch', details=branch_data)
        self.db_session.add(impact)
        try:
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise RuntimeError(f"Failed to add branching path: {e}")

    def get_quest_branches(self, quest_id: int) -> List[Dict[str, Any]]:
        """Return all branching paths for a quest."""
        impacts = self.db_session.query(QuestWorldImpact).filter_by(quest_id=quest_id, impact_type='branch').all()
        return [impact.details for impact in impacts]

    def unlock_dependent_quests(self, completed_quest_id: int) -> List[Quest]:
        """Unlock quests that depend on the completed quest (quest chains)."""
        dependent_quests = self.db_session.query(QuestDependency).filter_by(prerequisite_quest_id=completed_quest_id).all()
        unlocked_quests = []
        for dep in dependent_quests:
            quest = self.db_session.query(Quest).get(dep.quest_id)
            if quest and quest.status == Quest.QuestStatus.AVAILABLE:
                unlocked_quests.append(quest)
        return unlocked_quests 