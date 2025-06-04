"""
Arc Step Repository

Database operations for ArcStep entities.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.systems.arc.models.arc_step import ArcStep, ArcStepStatus, ArcStepType
from backend.infrastructure.repositories import BaseRepository

logger = logging.getLogger(__name__)

class ArcStepRepository(BaseRepository[ArcStep]):
    """Repository for ArcStep entity operations."""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, ArcStep)
    
    async def get_by_arc(self, arc_id: UUID, order_by_index: bool = True) -> List[ArcStep]:
        """Get all steps for a specific arc."""
        try:
            query = select(ArcStep).where(ArcStep.arc_id == arc_id)
            
            if order_by_index:
                query = query.order_by(ArcStep.step_index.asc())
            else:
                query = query.order_by(ArcStep.created_at.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting steps for arc {arc_id}: {e}")
            return []
    
    async def get_by_arc_and_index(self, arc_id: UUID, step_index: int) -> Optional[ArcStep]:
        """Get a specific step by arc ID and step index."""
        try:
            query = select(ArcStep).where(
                and_(
                    ArcStep.arc_id == arc_id,
                    ArcStep.step_index == step_index
                )
            )
            
            result = await self.db_session.execute(query)
            return result.scalars().first()
            
        except Exception as e:
            logger.error(f"Error getting step {step_index} for arc {arc_id}: {e}")
            return None
    
    async def get_by_status(self, status: ArcStepStatus, arc_id: Optional[UUID] = None) -> List[ArcStep]:
        """Get steps by status, optionally filtered by arc."""
        try:
            query = select(ArcStep).where(ArcStep.status == status)
            
            if arc_id:
                query = query.where(ArcStep.arc_id == arc_id)
            
            query = query.order_by(ArcStep.step_index.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting steps by status {status}: {e}")
            return []
    
    async def get_by_type(self, step_type: ArcStepType, arc_id: Optional[UUID] = None) -> List[ArcStep]:
        """Get steps by type, optionally filtered by arc."""
        try:
            query = select(ArcStep).where(ArcStep.step_type == step_type)
            
            if arc_id:
                query = query.where(ArcStep.arc_id == arc_id)
            
            query = query.order_by(ArcStep.step_index.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting steps by type {step_type}: {e}")
            return []
    
    async def get_completed_steps(self, arc_id: UUID) -> List[ArcStep]:
        """Get all completed steps for an arc."""
        return await self.get_by_status(ArcStepStatus.COMPLETED, arc_id)
    
    async def get_failed_steps(self, arc_id: UUID) -> List[ArcStep]:
        """Get all failed steps for an arc."""
        return await self.get_by_status(ArcStepStatus.FAILED, arc_id)
    
    async def get_pending_steps(self, arc_id: UUID) -> List[ArcStep]:
        """Get all pending steps for an arc."""
        return await self.get_by_status(ArcStepStatus.PENDING, arc_id)
    
    async def get_active_steps(self, arc_id: Optional[UUID] = None) -> List[ArcStep]:
        """Get all active steps, optionally filtered by arc."""
        return await self.get_by_status(ArcStepStatus.ACTIVE, arc_id)
    
    async def get_next_step(self, arc_id: UUID, current_step_index: int) -> Optional[ArcStep]:
        """Get the next step after the current step index."""
        try:
            query = select(ArcStep).where(
                and_(
                    ArcStep.arc_id == arc_id,
                    ArcStep.step_index > current_step_index,
                    ArcStep.status == ArcStepStatus.PENDING
                )
            ).order_by(ArcStep.step_index.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().first()
            
        except Exception as e:
            logger.error(f"Error getting next step after {current_step_index} for arc {arc_id}: {e}")
            return None
    
    async def get_current_step(self, arc_id: UUID) -> Optional[ArcStep]:
        """Get the currently active step for an arc."""
        try:
            query = select(ArcStep).where(
                and_(
                    ArcStep.arc_id == arc_id,
                    ArcStep.status == ArcStepStatus.ACTIVE
                )
            ).order_by(ArcStep.step_index.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().first()
            
        except Exception as e:
            logger.error(f"Error getting current step for arc {arc_id}: {e}")
            return None
    
    async def count_steps_by_arc(self, arc_id: UUID) -> int:
        """Count total steps for an arc."""
        try:
            query = select(ArcStep).where(ArcStep.arc_id == arc_id)
            result = await self.db_session.execute(query)
            return len(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error counting steps for arc {arc_id}: {e}")
            return 0
    
    async def count_steps_by_status(self, arc_id: UUID, status: ArcStepStatus) -> int:
        """Count steps with a specific status for an arc."""
        try:
            query = select(ArcStep).where(
                and_(
                    ArcStep.arc_id == arc_id,
                    ArcStep.status == status
                )
            )
            result = await self.db_session.execute(query)
            return len(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error counting steps by status {status} for arc {arc_id}: {e}")
            return 0
    
    async def get_step_statistics(self, arc_id: UUID) -> Dict[str, Any]:
        """Get comprehensive step statistics for an arc."""
        try:
            steps = await self.get_by_arc(arc_id)
            
            stats = {
                "total_steps": len(steps),
                "by_status": {},
                "by_type": {},
                "completion_percentage": 0.0,
                "average_attempts": 0.0
            }
            
            if not steps:
                return stats
            
            # Count by status
            for status in ArcStepStatus:
                stats["by_status"][status.value] = len([
                    step for step in steps if step.status == status
                ])
            
            # Count by type
            for step_type in ArcStepType:
                stats["by_type"][step_type.value] = len([
                    step for step in steps if step.step_type == step_type
                ])
            
            # Calculate completion percentage
            completed_count = stats["by_status"].get("completed", 0)
            if stats["total_steps"] > 0:
                stats["completion_percentage"] = completed_count / stats["total_steps"]
            
            # Calculate average attempts
            total_attempts = sum(step.attempts for step in steps)
            if stats["total_steps"] > 0:
                stats["average_attempts"] = total_attempts / stats["total_steps"]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting step statistics for arc {arc_id}: {e}")
            return {
                "total_steps": 0,
                "by_status": {},
                "by_type": {},
                "completion_percentage": 0.0,
                "average_attempts": 0.0
            }
    
    async def create_step(
        self,
        arc_id: UUID,
        step_index: int,
        title: str,
        description: str,
        narrative_text: str,
        step_type: ArcStepType,
        completion_criteria: Optional[Dict[str, Any]] = None,
        quest_probability: float = 0.0,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ArcStep]:
        """Create a new arc step."""
        try:
            step_data = {
                "arc_id": arc_id,
                "step_index": step_index,
                "title": title,
                "description": description,
                "narrative_text": narrative_text,
                "step_type": step_type,
                "completion_criteria": completion_criteria or {},
                "quest_probability": quest_probability,
                "tags": tags or [],
                "metadata": metadata or {}
            }
            
            return await self.create(step_data)
            
        except Exception as e:
            logger.error(f"Error creating step {step_index} for arc {arc_id}: {e}")
            return None
    
    async def mark_step_completed(self, step_id: UUID) -> bool:
        """Mark a step as completed."""
        try:
            step = await self.get(step_id)
            if not step:
                return False
            
            step.status = ArcStepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            await self.db_session.commit()
            
            logger.info(f"Marked step {step_id} as completed")
            return True
            
        except Exception as e:
            logger.error(f"Error marking step {step_id} as completed: {e}")
            await self.db_session.rollback()
            return False
    
    async def mark_step_failed(self, step_id: UUID) -> bool:
        """Mark a step as failed."""
        try:
            step = await self.get(step_id)
            if not step:
                return False
            
            step.status = ArcStepStatus.FAILED
            await self.db_session.commit()
            
            logger.info(f"Marked step {step_id} as failed")
            return True
            
        except Exception as e:
            logger.error(f"Error marking step {step_id} as failed: {e}")
            await self.db_session.rollback()
            return False
    
    async def increment_step_attempts(self, step_id: UUID) -> bool:
        """Increment the attempts counter for a step."""
        try:
            step = await self.get(step_id)
            if not step:
                return False
            
            step.attempts += 1
            await self.db_session.commit()
            
            logger.info(f"Incremented attempts for step {step_id} to {step.attempts}")
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing attempts for step {step_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def set_step_active(self, step_id: UUID) -> bool:
        """Mark a step as active."""
        try:
            step = await self.get(step_id)
            if not step:
                return False
            
            step.status = ArcStepStatus.ACTIVE
            await self.db_session.commit()
            
            logger.info(f"Set step {step_id} as active")
            return True
            
        except Exception as e:
            logger.error(f"Error setting step {step_id} as active: {e}")
            await self.db_session.rollback()
            return False
    
    async def search_steps(
        self,
        search_term: str,
        arc_id: Optional[UUID] = None,
        step_type: Optional[ArcStepType] = None,
        status: Optional[ArcStepStatus] = None
    ) -> List[ArcStep]:
        """Search steps by text in title, description, or narrative."""
        try:
            # Base search on title, description, and narrative
            query = select(ArcStep).where(
                or_(
                    ArcStep.title.ilike(f"%{search_term}%"),
                    ArcStep.description.ilike(f"%{search_term}%"),
                    ArcStep.narrative_text.ilike(f"%{search_term}%")
                )
            )
            
            # Apply optional filters
            if arc_id:
                query = query.where(ArcStep.arc_id == arc_id)
            
            if step_type:
                query = query.where(ArcStep.step_type == step_type)
            
            if status:
                query = query.where(ArcStep.status == status)
            
            query = query.order_by(ArcStep.step_index.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error searching steps with term '{search_term}': {e}")
            return [] 