"""
Character System Services

This module provides business logic services for the character system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.character.models import (
    CharacterEntity,
    CharacterModel,
    CreateCharacterRequest,
    UpdateCharacterRequest,
    CharacterResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    CharacterNotFoundError,
    CharacterValidationError,
    CharacterConflictError
)

logger = logging.getLogger(__name__)


class CharacterService(BaseService[CharacterEntity]):
    """Service class for character business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, CharacterEntity)
        self.db = db_session

    async def create_character(
        self, 
        request: CreateCharacterRequest,
        user_id: Optional[UUID] = None
    ) -> CharacterResponse:
        """Create a new character"""
        try:
            logger.info(f"Creating character: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise CharacterConflictError(f"Character with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = CharacterEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created character {entity.id} successfully")
            return CharacterResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating character: {str(e)}")
            self.db.rollback()
            raise

    async def get_character_by_id(self, character_id: UUID) -> Optional[CharacterResponse]:
        """Get character by ID"""
        try:
            entity = self.db.query(CharacterEntity).filter(
                CharacterEntity.id == character_id,
                CharacterEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return CharacterResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting character {_character_id}: {str(e)}")
            raise

    async def update_character(
        self, 
        character_id: UUID, 
        request: UpdateCharacterRequest
    ) -> CharacterResponse:
        """Update existing character"""
        try:
            entity = await self._get_entity_by_id(character_id)
            if not entity:
                raise CharacterNotFoundError(f"Character {_character_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated character {entity.id} successfully")
            return CharacterResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating character {_character_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete character"""
        try:
            entity = await self._get_entity_by_id(character_id)
            if not entity:
                raise CharacterNotFoundError(f"Character {_character_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted character {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting character {_character_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_characters(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[CharacterResponse], int]:
        """List characters with pagination and filters"""
        try:
            query = self.db.query(CharacterEntity).filter(
                CharacterEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(CharacterEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        CharacterEntity.name.ilike(f"%{search}%"),
                        CharacterEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(CharacterEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [CharacterResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing characters: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[CharacterEntity]:
        """Get entity by name"""
        return self.db.query(CharacterEntity).filter(
            CharacterEntity.name == name,
            CharacterEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[CharacterEntity]:
        """Get entity by ID"""
        return self.db.query(CharacterEntity).filter(
            CharacterEntity.id == entity_id,
            CharacterEntity.is_active == True
        ).first()

    async def get_character_statistics(self) -> Dict[str, Any]:
        """Get character system statistics"""
        try:
            total_count = self.db.query(func.count(CharacterEntity.id)).filter(
                CharacterEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(CharacterEntity.id)).filter(
                CharacterEntity.is_active == True,
                CharacterEntity.status == "active"
            ).scalar()
            
            return {
                "total_characters": total_count,
                "active_characters": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting character statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_character_service(db_session: Session) -> CharacterService:
    """Create character service instance"""
    return CharacterService(db_session)
