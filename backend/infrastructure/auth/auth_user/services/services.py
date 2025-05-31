"""
Auth_User System Services

This module provides business logic services for the auth_user system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.auth.auth_user.models import (
    Auth_UserEntity,
    Auth_UserModel,
    CreateAuth_UserRequest,
    UpdateAuth_UserRequest,
    Auth_UserResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    Auth_UserNotFoundError,
    Auth_UserValidationError,
    Auth_UserConflictError
)

logger = logging.getLogger(__name__)


class Auth_UserService(BaseService[Auth_UserEntity]):
    """Service class for auth_user business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Auth_UserEntity)
        self.db = db_session

    async def create_auth_user(
        self, 
        request: CreateAuth_UserRequest,
        user_id: Optional[UUID] = None
    ) -> Auth_UserResponse:
        """Create a new auth_user"""
        try:
            logger.info(f"Creating auth_user: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise Auth_UserConflictError(f"Auth_User with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = Auth_UserEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created auth_user {entity.id} successfully")
            return Auth_UserResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating auth_user: {str(e)}")
            self.db.rollback()
            raise

    async def get_auth_user_by_id(self, auth_user_id: UUID) -> Optional[Auth_UserResponse]:
        """Get auth_user by ID"""
        try:
            entity = self.db.query(Auth_UserEntity).filter(
                Auth_UserEntity.id == auth_user_id,
                Auth_UserEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return Auth_UserResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting auth_user {_auth_user_id}: {str(e)}")
            raise

    async def update_auth_user(
        self, 
        auth_user_id: UUID, 
        request: UpdateAuth_UserRequest
    ) -> Auth_UserResponse:
        """Update existing auth_user"""
        try:
            entity = await self._get_entity_by_id(auth_user_id)
            if not entity:
                raise Auth_UserNotFoundError(f"Auth_User {_auth_user_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated auth_user {entity.id} successfully")
            return Auth_UserResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating auth_user {_auth_user_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_auth_user(self, auth_user_id: UUID) -> bool:
        """Soft delete auth_user"""
        try:
            entity = await self._get_entity_by_id(auth_user_id)
            if not entity:
                raise Auth_UserNotFoundError(f"Auth_User {_auth_user_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted auth_user {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting auth_user {_auth_user_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_auth_users(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Auth_UserResponse], int]:
        """List auth_users with pagination and filters"""
        try:
            query = self.db.query(Auth_UserEntity).filter(
                Auth_UserEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(Auth_UserEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        Auth_UserEntity.name.ilike(f"%{search}%"),
                        Auth_UserEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(Auth_UserEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [Auth_UserResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing auth_users: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[Auth_UserEntity]:
        """Get entity by name"""
        return self.db.query(Auth_UserEntity).filter(
            Auth_UserEntity.name == name,
            Auth_UserEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[Auth_UserEntity]:
        """Get entity by ID"""
        return self.db.query(Auth_UserEntity).filter(
            Auth_UserEntity.id == entity_id,
            Auth_UserEntity.is_active == True
        ).first()

    async def get_auth_user_statistics(self) -> Dict[str, Any]:
        """Get auth_user system statistics"""
        try:
            total_count = self.db.query(func.count(Auth_UserEntity.id)).filter(
                Auth_UserEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(Auth_UserEntity.id)).filter(
                Auth_UserEntity.is_active == True,
                Auth_UserEntity.status == "active"
            ).scalar()
            
            return {
                "total_auth_users": total_count,
                "active_auth_users": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting auth_user statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_auth_user_service(db_session: Session) -> Auth_UserService:
    """Create auth_user service instance"""
    return Auth_UserService(db_session)
