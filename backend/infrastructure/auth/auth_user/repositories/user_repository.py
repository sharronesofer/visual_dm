"""
User repository for database operations.

This module provides database access layer for User entities.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.infrastructure.auth.auth_user.models.user_models import User, Role
from backend.infrastructure.shared.exceptions import Auth_UserNotFoundError


class UserRepository:
    """Repository for User database operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        try:
            result = await self.db_session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            result = await self.db_session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user."""
        user = User(**user_data)
        self.db_session.add(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user
    
    async def update_user(self, user_id: UUID, update_data: dict) -> Optional[User]:
        """Update user by ID."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        for key, value in update_data.items():
            setattr(user, key, value)
        
        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Soft delete user by setting is_active to False."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        await self.db_session.commit()
        return True
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        result = await self.db_session.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_user_with_roles(self, user_id: UUID) -> Optional[User]:
        """Get user with roles loaded."""
        try:
            result = await self.db_session.execute(
                select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None 