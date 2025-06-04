"""
Arc Progression Repository

Database operations for ArcProgression entities.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.systems.arc.models.arc_progression import ArcProgression, ProgressionMethod
from backend.infrastructure.repositories import BaseRepository

logger = logging.getLogger(__name__)

class ArcProgressionRepository(BaseRepository[ArcProgression]):
    """Repository for ArcProgression entity operations."""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, ArcProgression)
    
    async def get_by_arc(self, arc_id: UUID) -> Optional[ArcProgression]:
        """Get progression record for a specific arc."""
        try:
            query = select(ArcProgression).where(ArcProgression.arc_id == arc_id)
            result = await self.db_session.execute(query)
            return result.scalars().first()
            
        except Exception as e:
            logger.error(f"Error getting progression for arc {arc_id}: {e}")
            return None
    
    async def get_active_progressions(self) -> List[ArcProgression]:
        """Get all active arc progressions."""
        try:
            query = select(ArcProgression).where(
                ArcProgression.is_active == True
            ).order_by(ArcProgression.updated_at.desc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting active progressions: {e}")
            return []
    
    async def get_completed_progressions(self) -> List[ArcProgression]:
        """Get all completed arc progressions."""
        try:
            query = select(ArcProgression).where(
                and_(
                    ArcProgression.is_active == False,
                    ArcProgression.completed_at.isnot(None)
                )
            ).order_by(ArcProgression.completed_at.desc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting completed progressions: {e}")
            return []
    
    async def get_by_method(self, method: ProgressionMethod) -> List[ArcProgression]:
        """Get progressions by progression method."""
        try:
            query = select(ArcProgression).where(
                ArcProgression.progression_method == method
            ).order_by(ArcProgression.updated_at.desc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting progressions by method {method}: {e}")
            return []
    
    async def create_progression(self, arc_id: UUID) -> Optional[ArcProgression]:
        """Create a new progression record for an arc."""
        try:
            progression_data = {
                "arc_id": arc_id,
                "current_step_index": 0,
                "completion_percentage": 0.0,
                "is_active": True,
                "completed_steps": [],
                "failed_steps": [],
                "skipped_steps": [],
                "total_events": 0,
                "progression_method": ProgressionMethod.LINEAR,
                "events": [],
                "average_step_duration": 0.0,
                "total_duration": 0.0,
                "started_at": datetime.utcnow()
            }
            
            return await self.create(progression_data)
            
        except Exception as e:
            logger.error(f"Error creating progression for arc {arc_id}: {e}")
            return None
    
    async def add_event(
        self,
        progression_id: UUID,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """Add an event to a progression record."""
        try:
            progression = await self.get(progression_id)
            if not progression:
                return False
            
            event = {
                "type": event_type,
                "data": event_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add event to the list
            events = progression.events or []
            events.append(event)
            progression.events = events
            
            # Increment event counter
            progression.total_events += 1
            
            await self.db_session.commit()
            logger.info(f"Added event {event_type} to progression {progression_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding event to progression {progression_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def complete_step(self, progression_id: UUID, step_index: int) -> bool:
        """Mark a step as completed in the progression."""
        try:
            progression = await self.get(progression_id)
            if not progression:
                return False
            
            # Add to completed steps if not already there
            completed_steps = progression.completed_steps or []
            if step_index not in completed_steps:
                completed_steps.append(step_index)
                progression.completed_steps = completed_steps
            
            # Update current step index
            progression.current_step_index = max(progression.current_step_index, step_index + 1)
            
            # Add completion event
            await self.add_event(progression_id, "step_completed", {
                "step_index": step_index,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await self.db_session.commit()
            logger.info(f"Completed step {step_index} for progression {progression_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing step {step_index} for progression {progression_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def fail_step(self, progression_id: UUID, step_index: int) -> bool:
        """Mark a step as failed in the progression."""
        try:
            progression = await self.get(progression_id)
            if not progression:
                return False
            
            # Add to failed steps if not already there
            failed_steps = progression.failed_steps or []
            if step_index not in failed_steps:
                failed_steps.append(step_index)
                progression.failed_steps = failed_steps
            
            # Add failure event
            await self.add_event(progression_id, "step_failed", {
                "step_index": step_index,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await self.db_session.commit()
            logger.info(f"Failed step {step_index} for progression {progression_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error failing step {step_index} for progression {progression_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def skip_step(self, progression_id: UUID, step_index: int) -> bool:
        """Mark a step as skipped in the progression."""
        try:
            progression = await self.get(progression_id)
            if not progression:
                return False
            
            # Add to skipped steps if not already there
            skipped_steps = progression.skipped_steps or []
            if step_index not in skipped_steps:
                skipped_steps.append(step_index)
                progression.skipped_steps = skipped_steps
            
            # Update current step index
            progression.current_step_index = max(progression.current_step_index, step_index + 1)
            
            # Add skip event
            await self.add_event(progression_id, "step_skipped", {
                "step_index": step_index,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await self.db_session.commit()
            logger.info(f"Skipped step {step_index} for progression {progression_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error skipping step {step_index} for progression {progression_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def start_progression(self, progression_id: UUID) -> bool:
        """Mark a progression as started."""
        try:
            progression = await self.get(progression_id)
            if not progression:
                return False
            
            progression.is_active = True
            progression.started_at = datetime.utcnow()
            
            # Add start event
            await self.add_event(progression_id, "progression_started", {
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await self.db_session.commit()
            logger.info(f"Started progression {progression_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting progression {progression_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def complete_progression(self, progression_id: UUID) -> bool:
        """Mark a progression as completed."""
        try:
            progression = await self.get(progression_id)
            if not progression:
                return False
            
            progression.is_active = False
            progression.completed_at = datetime.utcnow()
            
            # Calculate total duration
            if progression.started_at:
                duration = progression.completed_at - progression.started_at
                progression.total_duration = duration.total_seconds() / 3600  # Convert to hours
            
            # Add completion event
            await self.add_event(progression_id, "progression_completed", {
                "timestamp": datetime.utcnow().isoformat(),
                "total_duration_hours": progression.total_duration
            })
            
            await self.db_session.commit()
            logger.info(f"Completed progression {progression_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing progression {progression_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def update_completion_percentage(
        self,
        progression_id: UUID,
        total_steps: int
    ) -> bool:
        """Update the completion percentage based on completed steps."""
        try:
            progression = await self.get(progression_id)
            if not progression:
                return False
            
            if total_steps > 0:
                completed_count = len(progression.completed_steps or [])
                progression.completion_percentage = completed_count / total_steps
            else:
                progression.completion_percentage = 0.0
            
            await self.db_session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating completion percentage for progression {progression_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def get_progression_statistics(self) -> Dict[str, Any]:
        """Get comprehensive progression statistics."""
        try:
            query = select(ArcProgression)
            result = await self.db_session.execute(query)
            all_progressions = result.scalars().all()
            
            stats = {
                "total_progressions": len(all_progressions),
                "active_progressions": 0,
                "completed_progressions": 0,
                "average_completion_percentage": 0.0,
                "average_duration_hours": 0.0,
                "by_method": {},
                "total_events": 0
            }
            
            if not all_progressions:
                return stats
            
            active_count = 0
            completed_count = 0
            total_completion = 0.0
            total_duration = 0.0
            completed_progressions = []
            total_events = 0
            
            # Count by method
            for method in ProgressionMethod:
                stats["by_method"][method.value] = 0
            
            for progression in all_progressions:
                if progression.is_active:
                    active_count += 1
                else:
                    completed_count += 1
                    completed_progressions.append(progression)
                
                total_completion += progression.completion_percentage or 0.0
                total_duration += progression.total_duration or 0.0
                total_events += progression.total_events or 0
                
                method_key = progression.progression_method.value
                stats["by_method"][method_key] += 1
            
            stats["active_progressions"] = active_count
            stats["completed_progressions"] = completed_count
            stats["total_events"] = total_events
            
            # Calculate averages
            if len(all_progressions) > 0:
                stats["average_completion_percentage"] = total_completion / len(all_progressions)
            
            if completed_progressions:
                stats["average_duration_hours"] = total_duration / len(completed_progressions)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting progression statistics: {e}")
            return {
                "total_progressions": 0,
                "active_progressions": 0,
                "completed_progressions": 0,
                "average_completion_percentage": 0.0,
                "average_duration_hours": 0.0,
                "by_method": {},
                "total_events": 0
            }
    
    async def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Get all events of a specific type across all progressions."""
        try:
            query = select(ArcProgression)
            result = await self.db_session.execute(query)
            progressions = result.scalars().all()
            
            events = []
            for progression in progressions:
                progression_events = progression.events or []
                for event in progression_events:
                    if event.get("type") == event_type:
                        event["progression_id"] = str(progression.id)
                        event["arc_id"] = str(progression.arc_id)
                        events.append(event)
            
            # Sort by timestamp
            events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return events
            
        except Exception as e:
            logger.error(f"Error getting events by type {event_type}: {e}")
            return [] 