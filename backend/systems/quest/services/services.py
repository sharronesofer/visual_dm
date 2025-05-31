"""
Quest System Services

This module provides business logic services for the quest system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.quest.models import (
    QuestEntity,
    QuestModel,
    CreateQuestRequest,
    UpdateQuestRequest,
    QuestResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    QuestNotFoundError,
    QuestValidationError,
    QuestConflictError
)

logger = logging.getLogger(__name__)


class QuestService(BaseService[QuestEntity]):
    """Service class for quest business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, QuestEntity)
        self.db = db_session

    async def create_quest(
        self, 
        request: CreateQuestRequest,
        user_id: Optional[UUID] = None
    ) -> QuestResponse:
        """Create a new quest"""
        try:
            logger.info(f"Creating quest: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise QuestConflictError(f"Quest with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = QuestEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created quest {entity.id} successfully")
            return QuestResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating quest: {str(e)}")
            self.db.rollback()
            raise

    async def get_quest_by_id(self, quest_id: UUID) -> Optional[QuestResponse]:
        """Get quest by ID"""
        try:
            entity = self.db.query(QuestEntity).filter(
                QuestEntity.id == quest_id,
                QuestEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return QuestResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting quest {_quest_id}: {str(e)}")
            raise

    async def update_quest(
        self, 
        quest_id: UUID, 
        request: UpdateQuestRequest
    ) -> QuestResponse:
        """Update existing quest"""
        try:
            entity = await self._get_entity_by_id(quest_id)
            if not entity:
                raise QuestNotFoundError(f"Quest {_quest_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated quest {entity.id} successfully")
            return QuestResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating quest {_quest_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_quest(self, quest_id: UUID) -> bool:
        """Soft delete quest"""
        try:
            entity = await self._get_entity_by_id(quest_id)
            if not entity:
                raise QuestNotFoundError(f"Quest {_quest_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted quest {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting quest {_quest_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_quests(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[QuestResponse], int]:
        """List quests with pagination and filters"""
        try:
            query = self.db.query(QuestEntity).filter(
                QuestEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(QuestEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        QuestEntity.name.ilike(f"%{search}%"),
                        QuestEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(QuestEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [QuestResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing quests: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[QuestEntity]:
        """Get entity by name"""
        return self.db.query(QuestEntity).filter(
            QuestEntity.name == name,
            QuestEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[QuestEntity]:
        """Get entity by ID"""
        return self.db.query(QuestEntity).filter(
            QuestEntity.id == entity_id,
            QuestEntity.is_active == True
        ).first()

    async def get_quest_statistics(self) -> Dict[str, Any]:
        """Get quest system statistics"""
        try:
            total_count = self.db.query(func.count(QuestEntity.id)).filter(
                QuestEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(QuestEntity.id)).filter(
                QuestEntity.is_active == True,
                QuestEntity.status == "active"
            ).scalar()
            
            return {
                "total_quests": total_count,
                "active_quests": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting quest statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_quest_service(db_session: Session) -> QuestService:
    """Create quest service instance"""
    return QuestService(db_session)
