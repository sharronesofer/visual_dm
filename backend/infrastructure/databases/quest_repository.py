"""
Quest Repository
Handles data access operations for the quest system.
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

# Import from infrastructure models
from backend.infrastructure.databases.quest_models import QuestEntity

# Import business logic for conversion
from backend.systems.quest.models import QuestData, QuestStatus
from backend.infrastructure.shared.repositories import BaseRepository

logger = logging.getLogger(__name__)


class QuestRepository(BaseRepository[QuestEntity]):
    """Repository for quest data operations"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, QuestEntity)
        
    def get_by_player_id(self, player_id: str, status: Optional[str] = None) -> List[QuestEntity]:
        """Get all quests for a specific player"""
        try:
            query = self.db_session.query(QuestEntity).filter(
                QuestEntity.properties.contains({"player_id": player_id}),
                QuestEntity.is_active == True
            )
            
            if status:
                query = query.filter(QuestEntity.status == status)
                
            return query.all()
        except Exception as e:
            logger.error(f"Error getting quests for player {player_id}: {str(e)}")
            return []
    
    def get_by_npc_id(self, npc_id: str, status: Optional[str] = None) -> List[QuestEntity]:
        """Get all quests associated with a specific NPC"""
        try:
            query = self.db_session.query(QuestEntity).filter(
                QuestEntity.properties.contains({"npc_id": npc_id}),
                QuestEntity.is_active == True
            )
            
            if status:
                query = query.filter(QuestEntity.status == status)
                
            return query.all()
        except Exception as e:
            logger.error(f"Error getting quests for NPC {npc_id}: {str(e)}")
            return []
    
    def get_by_location(self, location_id: str, status: Optional[str] = None) -> List[QuestEntity]:
        """Get all quests in a specific location"""
        try:
            query = self.db_session.query(QuestEntity).filter(
                QuestEntity.properties.contains({"location_id": location_id}),
                QuestEntity.is_active == True
            )
            
            if status:
                query = query.filter(QuestEntity.status == status)
                
            return query.all()
        except Exception as e:
            logger.error(f"Error getting quests for location {location_id}: {str(e)}")
            return []
    
    def update_quest_status(self, quest_id: UUID, new_status: str) -> bool:
        """Update quest status"""
        try:
            quest = self.get_by_id(quest_id)
            if quest:
                quest.status = new_status
                quest.updated_at = datetime.utcnow()
                self.db_session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating quest status: {str(e)}")
            self.db_session.rollback()
            return False
    
    def get_quest_statistics(self) -> Dict[str, Any]:
        """Get quest system statistics"""
        try:
            total_quests = self.db_session.query(func.count(QuestEntity.id)).filter(
                QuestEntity.is_active == True
            ).scalar()
            
            status_counts = self.db_session.query(
                QuestEntity.status,
                func.count(QuestEntity.id)
            ).filter(
                QuestEntity.is_active == True
            ).group_by(QuestEntity.status).all()
            
            return {
                "total_quests": total_quests,
                "status_breakdown": dict(status_counts),
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting quest statistics: {str(e)}")
            return {"total_quests": 0, "status_breakdown": {}, "last_updated": datetime.utcnow().isoformat()} 