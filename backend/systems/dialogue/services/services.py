"""
Dialogue System Services

This module provides business logic services for the dialogue system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.dialogue.models import (
    DialogueEntity,
    DialogueModel,
    CreateDialogueRequest,
    UpdateDialogueRequest,
    DialogueResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    DialogueNotFoundError,
    DialogueValidationError,
    DialogueConflictError
)

logger = logging.getLogger(__name__)


class DialogueService(BaseService[DialogueEntity]):
    """Service class for dialogue business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, DialogueEntity)
        self.db = db_session

    async def create_dialogue(
        self, 
        request: CreateDialogueRequest,
        user_id: Optional[UUID] = None
    ) -> DialogueResponse:
        """Create a new dialogue"""
        try:
            logger.info(f"Creating dialogue: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise DialogueConflictError(f"Dialogue with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = DialogueEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created dialogue {entity.id} successfully")
            return DialogueResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating dialogue: {str(e)}")
            self.db.rollback()
            raise

    async def get_dialogue_by_id(self, dialogue_id: UUID) -> Optional[DialogueResponse]:
        """Get dialogue by ID"""
        try:
            entity = self.db.query(DialogueEntity).filter(
                DialogueEntity.id == dialogue_id,
                DialogueEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return DialogueResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting dialogue {_dialogue_id}: {str(e)}")
            raise

    async def update_dialogue(
        self, 
        dialogue_id: UUID, 
        request: UpdateDialogueRequest
    ) -> DialogueResponse:
        """Update existing dialogue"""
        try:
            entity = await self._get_entity_by_id(dialogue_id)
            if not entity:
                raise DialogueNotFoundError(f"Dialogue {_dialogue_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated dialogue {entity.id} successfully")
            return DialogueResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating dialogue {_dialogue_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_dialogue(self, dialogue_id: UUID) -> bool:
        """Soft delete dialogue"""
        try:
            entity = await self._get_entity_by_id(dialogue_id)
            if not entity:
                raise DialogueNotFoundError(f"Dialogue {_dialogue_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted dialogue {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting dialogue {_dialogue_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_dialogues(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[DialogueResponse], int]:
        """List dialogues with pagination and filters"""
        try:
            query = self.db.query(DialogueEntity).filter(
                DialogueEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(DialogueEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        DialogueEntity.name.ilike(f"%{search}%"),
                        DialogueEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(DialogueEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [DialogueResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing dialogues: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[DialogueEntity]:
        """Get entity by name"""
        return self.db.query(DialogueEntity).filter(
            DialogueEntity.name == name,
            DialogueEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[DialogueEntity]:
        """Get entity by ID"""
        return self.db.query(DialogueEntity).filter(
            DialogueEntity.id == entity_id,
            DialogueEntity.is_active == True
        ).first()

    async def get_dialogue_statistics(self) -> Dict[str, Any]:
        """Get dialogue system statistics"""
        try:
            total_count = self.db.query(func.count(DialogueEntity.id)).filter(
                DialogueEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(DialogueEntity.id)).filter(
                DialogueEntity.is_active == True,
                DialogueEntity.status == "active"
            ).scalar()
            
            return {
                "total_dialogues": total_count,
                "active_dialogues": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dialogue statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_dialogue_service(db_session: Session) -> DialogueService:
    """Create dialogue service instance"""
    return DialogueService(db_session)
