"""
Arc Repository

Database operations for Arc entities.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.systems.arc.models.arc import Arc, ArcType, ArcStatus, ArcPriority
from backend.infrastructure.repositories import BaseRepository

logger = logging.getLogger(__name__)

class ArcRepository(BaseRepository[Arc]):
    """Repository for Arc entity operations."""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, Arc)
    
    async def get_by_type(
        self,
        arc_type: ArcType,
        status: Optional[ArcStatus] = None
    ) -> List[Arc]:
        """Get arcs by type, optionally filtered by status."""
        try:
            query = select(Arc).where(Arc.arc_type == arc_type)
            
            if status:
                query = query.where(Arc.status == status)
            
            query = query.order_by(Arc.priority.desc(), Arc.created_at.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting arcs by type {arc_type}: {e}")
            return []
    
    async def get_by_status(self, status: ArcStatus) -> List[Arc]:
        """Get all arcs with a specific status."""
        try:
            query = select(Arc).where(Arc.status == status).order_by(
                Arc.priority.desc(),
                Arc.created_at.asc()
            )
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting arcs by status {status}: {e}")
            return []
    
    async def get_active_arcs(self) -> List[Arc]:
        """Get all active arcs."""
        return await self.get_by_status(ArcStatus.ACTIVE)
    
    async def get_by_region(self, region_id: str) -> List[Arc]:
        """Get arcs associated with a specific region."""
        try:
            query = select(Arc).where(
                Arc.region_id == region_id
            ).order_by(Arc.priority.desc(), Arc.created_at.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting arcs by region {region_id}: {e}")
            return []
    
    async def get_by_character(self, character_id: str) -> List[Arc]:
        """Get arcs associated with a specific character."""
        try:
            query = select(Arc).where(
                Arc.character_id == character_id
            ).order_by(Arc.priority.desc(), Arc.created_at.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting arcs by character {character_id}: {e}")
            return []
    
    async def get_by_npc(self, npc_id: str) -> List[Arc]:
        """Get arcs associated with a specific NPC."""
        try:
            query = select(Arc).where(
                Arc.npc_id == npc_id
            ).order_by(Arc.priority.desc(), Arc.created_at.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting arcs by NPC {npc_id}: {e}")
            return []
    
    async def get_by_faction(self, faction_id: str) -> List[Arc]:
        """Get arcs associated with a specific faction."""
        try:
            query = select(Arc).where(
                Arc.faction_ids.contains([faction_id])
            ).order_by(Arc.priority.desc(), Arc.created_at.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting arcs by faction {faction_id}: {e}")
            return []
    
    async def get_stalled_arcs(self, hours_threshold: int = 24) -> List[Arc]:
        """Get arcs that haven't had activity within the threshold."""
        try:
            threshold_time = datetime.utcnow() - timedelta(hours=hours_threshold)
            
            query = select(Arc).where(
                and_(
                    Arc.status == ArcStatus.ACTIVE,
                    or_(
                        Arc.last_activity < threshold_time,
                        Arc.last_activity.is_(None)
                    )
                )
            ).order_by(Arc.priority.desc(), Arc.created_at.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting stalled arcs: {e}")
            return []
    
    async def count_by_type(self, arc_type: ArcType) -> int:
        """Count arcs of a specific type."""
        try:
            query = select(Arc).where(Arc.arc_type == arc_type)
            result = await self.db_session.execute(query)
            return len(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error counting arcs by type {arc_type}: {e}")
            return 0
    
    async def count_by_status(self, status: ArcStatus) -> int:
        """Count arcs with a specific status."""
        try:
            query = select(Arc).where(Arc.status == status)
            result = await self.db_session.execute(query)
            return len(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error counting arcs by status {status}: {e}")
            return 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive arc statistics."""
        try:
            stats = {
                "total_arcs": 0,
                "by_type": {},
                "by_status": {},
                "by_priority": {},
                "completion_rate": 0.0
            }
            
            # Get all arcs for statistics
            query = select(Arc)
            result = await self.db_session.execute(query)
            all_arcs = result.scalars().all()
            
            stats["total_arcs"] = len(all_arcs)
            
            if not all_arcs:
                return stats
            
            # Count by type
            for arc_type in ArcType:
                stats["by_type"][arc_type.value] = len([
                    arc for arc in all_arcs if arc.arc_type == arc_type
                ])
            
            # Count by status
            for status in ArcStatus:
                stats["by_status"][status.value] = len([
                    arc for arc in all_arcs if arc.status == status
                ])
            
            # Count by priority
            for priority in ArcPriority:
                stats["by_priority"][priority.value] = len([
                    arc for arc in all_arcs if arc.priority == priority
                ])
            
            # Calculate completion rate
            completed_count = stats["by_status"].get("completed", 0)
            if stats["total_arcs"] > 0:
                stats["completion_rate"] = completed_count / stats["total_arcs"]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting arc statistics: {e}")
            return {
                "total_arcs": 0,
                "by_type": {},
                "by_status": {},
                "by_priority": {},
                "completion_rate": 0.0
            }
    
    async def search_arcs(
        self,
        search_term: str,
        arc_type: Optional[ArcType] = None,
        status: Optional[ArcStatus] = None,
        priority: Optional[ArcPriority] = None
    ) -> List[Arc]:
        """Search arcs by text in title or description."""
        try:
            # Base search on title and description
            query = select(Arc).where(
                or_(
                    Arc.title.ilike(f"%{search_term}%"),
                    Arc.description.ilike(f"%{search_term}%"),
                    Arc.starting_point.ilike(f"%{search_term}%"),
                    Arc.preferred_ending.ilike(f"%{search_term}%"),
                    Arc.current_narrative.ilike(f"%{search_term}%")
                )
            )
            
            # Apply optional filters
            if arc_type:
                query = query.where(Arc.arc_type == arc_type)
            
            if status:
                query = query.where(Arc.status == status)
            
            if priority:
                query = query.where(Arc.priority == priority)
            
            query = query.order_by(Arc.priority.desc(), Arc.created_at.asc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error searching arcs with term '{search_term}': {e}")
            return []
    
    async def update_last_activity(self, arc_id: UUID) -> bool:
        """Update the last activity timestamp for an arc."""
        try:
            arc = await self.get(arc_id)
            if not arc:
                return False
            
            arc.last_activity = datetime.utcnow()
            await self.db_session.commit()
            
            logger.info(f"Updated last activity for arc {arc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating last activity for arc {arc_id}: {e}")
            await self.db_session.rollback()
            return False 