"""
Role repository for database operations.

This module provides database access layer for Role entities.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.infrastructure.auth.auth_user.models.user_models import Role, Permission


class RoleRepository:
    """Repository for Role database operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_role_by_id(self, role_id: UUID) -> Optional[Role]:
        """Get role by ID."""
        try:
            result = await self.db_session.execute(
                select(Role).where(Role.id == role_id)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        try:
            result = await self.db_session.execute(
                select(Role).where(Role.name == name)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    async def create_role(self, role_data: dict) -> Role:
        """Create a new role."""
        role = Role(**role_data)
        self.db_session.add(role)
        await self.db_session.commit()
        await self.db_session.refresh(role)
        return role
    
    async def update_role(self, role_id: UUID, update_data: dict) -> Optional[Role]:
        """Update role by ID."""
        role = await self.get_role_by_id(role_id)
        if not role:
            return None
        
        for key, value in update_data.items():
            setattr(role, key, value)
        
        await self.db_session.commit()
        await self.db_session.refresh(role)
        return role
    
    async def delete_role(self, role_id: UUID) -> bool:
        """Delete role by ID."""
        role = await self.get_role_by_id(role_id)
        if not role:
            return False
        
        await self.db_session.delete(role)
        await self.db_session.commit()
        return True
    
    async def list_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """List roles with pagination."""
        result = await self.db_session.execute(
            select(Role)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_role_with_permissions(self, role_id: UUID) -> Optional[Role]:
        """Get role with permissions loaded."""
        try:
            result = await self.db_session.execute(
                select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.id == role_id)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None 