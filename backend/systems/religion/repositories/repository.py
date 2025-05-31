"""
Religion Repository Module

This module provides SQLAlchemy-based repository classes for religion system data persistence.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import IntegrityError, NoResultFound

from backend.systems.religion.models import (
    ReligionEntity,
    CreateReligionRequest,
    UpdateReligionRequest,
    ReligionResponse
)
from backend.infrastructure.shared.exceptions import (
    ReligionNotFoundError,
    ReligionValidationError,
    ReligionConflictError
)


class ReligionRepository:
    """Repository for religion data operations using SQLAlchemy"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    async def create(self, request: CreateReligionRequest, user_id: Optional[UUID] = None) -> ReligionEntity:
        """
        Create a new religion entity
        
        Args:
            request: Religion creation request
            user_id: Optional user ID for audit trail
            
        Returns:
            Created religion entity
            
        Raises:
            ReligionConflictError: If religion with same name already exists
            ReligionValidationError: If request data is invalid
        """
        try:
            # Check for duplicate name
            existing = self.db.query(ReligionEntity).filter(
                ReligionEntity.name == request.name,
                ReligionEntity.is_active == True
            ).first()
            
            if existing:
                raise ReligionConflictError(f"Religion with name '{request.name}' already exists")
            
            # Create new entity
            entity = ReligionEntity(
                name=request.name,
                description=request.description,
                properties=request.properties or {}
            )
            
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            return entity
            
        except IntegrityError as e:
            self.db.rollback()
            raise ReligionConflictError(f"Failed to create religion: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ReligionValidationError(f"Invalid religion data: {str(e)}")

    async def get_by_id(self, religion_id: UUID) -> Optional[ReligionEntity]:
        """
        Get religion by ID
        
        Args:
            religion_id: Religion ID
            
        Returns:
            Religion entity or None if not found
        """
        return self.db.query(ReligionEntity).filter(
            ReligionEntity.id == religion_id,
            ReligionEntity.is_active == True
        ).first()

    async def get_by_name(self, name: str) -> Optional[ReligionEntity]:
        """
        Get religion by name
        
        Args:
            name: Religion name
            
        Returns:
            Religion entity or None if not found
        """
        return self.db.query(ReligionEntity).filter(
            ReligionEntity.name == name,
            ReligionEntity.is_active == True
        ).first()

    async def update(self, religion_id: UUID, request: UpdateReligionRequest) -> ReligionEntity:
        """
        Update religion entity
        
        Args:
            religion_id: Religion ID
            request: Update request
            
        Returns:
            Updated religion entity
            
        Raises:
            ReligionNotFoundError: If religion not found
            ReligionConflictError: If update conflicts with existing data
        """
        try:
            entity = await self.get_by_id(religion_id)
            if not entity:
                raise ReligionNotFoundError(f"Religion with ID {religion_id} not found")
            
            # Check for name conflicts if name is being updated
            if request.name and request.name != entity.name:
                existing = await self.get_by_name(request.name)
                if existing:
                    raise ReligionConflictError(f"Religion with name '{request.name}' already exists")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(entity, field, value)
            
            self.db.commit()
            self.db.refresh(entity)
            
            return entity
            
        except (ReligionNotFoundError, ReligionConflictError):
            raise
        except Exception as e:
            self.db.rollback()
            raise ReligionValidationError(f"Failed to update religion: {str(e)}")

    async def delete(self, religion_id: UUID) -> bool:
        """
        Soft delete religion entity
        
        Args:
            religion_id: Religion ID
            
        Returns:
            True if deleted, False if not found
        """
        entity = await self.get_by_id(religion_id)
        if not entity:
            return False
        
        entity.is_active = False
        self.db.commit()
        return True

    async def list_all(
        self, 
        page: int = 1, 
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> Tuple[List[ReligionEntity], int]:
        """
        List religions with pagination and filtering
        
        Args:
            page: Page number (1-based)
            size: Page size
            status: Optional status filter
            search: Optional search term
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            
        Returns:
            Tuple of (entities, total_count)
        """
        query = self.db.query(ReligionEntity).filter(ReligionEntity.is_active == True)
        
        # Apply filters
        if status:
            query = query.filter(ReligionEntity.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    ReligionEntity.name.ilike(search_term),
                    ReligionEntity.description.ilike(search_term)
                )
            )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(ReligionEntity, sort_by, ReligionEntity.name)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * size
        entities = query.offset(offset).limit(size).all()
        
        return entities, total

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get religion system statistics
        
        Returns:
            Dictionary with various statistics
        """
        total_count = self.db.query(ReligionEntity).filter(
            ReligionEntity.is_active == True
        ).count()
        
        status_counts = self.db.query(
            ReligionEntity.status,
            func.count(ReligionEntity.id).label('count')
        ).filter(
            ReligionEntity.is_active == True
        ).group_by(ReligionEntity.status).all()
        
        return {
            "total_religions": total_count,
            "status_breakdown": {status: count for status, count in status_counts},
            "active_religions": total_count
        }

    async def bulk_create(self, requests: List[CreateReligionRequest]) -> List[ReligionEntity]:
        """
        Create multiple religions in a transaction
        
        Args:
            requests: List of creation requests
            
        Returns:
            List of created entities
        """
        try:
            entities = []
            for request in requests:
                entity = ReligionEntity(
                    name=request.name,
                    description=request.description,
                    properties=request.properties or {}
                )
                entities.append(entity)
                self.db.add(entity)
            
            self.db.commit()
            
            # Refresh all entities
            for entity in entities:
                self.db.refresh(entity)
            
            return entities
            
        except Exception as e:
            self.db.rollback()
            raise ReligionValidationError(f"Failed to bulk create religions: {str(e)}")

    async def search(
        self, 
        query: str, 
        limit: int = 20
    ) -> List[ReligionEntity]:
        """
        Search religions by name and description
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching entities
        """
        search_term = f"%{query}%"
        return self.db.query(ReligionEntity).filter(
            and_(
                ReligionEntity.is_active == True,
                or_(
                    ReligionEntity.name.ilike(search_term),
                    ReligionEntity.description.ilike(search_term)
                )
            )
        ).limit(limit).all()


def create_religion_repository(db_session: Session) -> ReligionRepository:
    """Factory function for creating religion repository"""
    return ReligionRepository(db_session)


def get_religion_repository(db_session: Session) -> ReligionRepository:
    """Get religion repository instance (alias for create_religion_repository)"""
    return create_religion_repository(db_session) 