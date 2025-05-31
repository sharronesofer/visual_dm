"""
Arc Completion Record Repository

Database operations for ArcCompletionRecord entities.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.orm import selectinload, Session
from sqlalchemy.future import select

from backend.systems.arc.models.arc_completion_record import ArcCompletionRecord, ArcCompletionResult
from backend.infrastructure.repositories import BaseRepository

logger = logging.getLogger(__name__)

class ArcCompletionRecordRepository(BaseRepository[ArcCompletionRecord]):
    """Repository for ArcCompletionRecord entity operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, ArcCompletionRecord)
    
    async def get_by_arc(self, arc_id: UUID) -> Optional[ArcCompletionRecord]:
        """Get completion record for a specific arc."""
        try:
            query = select(ArcCompletionRecord).where(ArcCompletionRecord.arc_id == arc_id)
            result = await self.db_session.execute(query)
            return result.scalars().first()
            
        except Exception as e:
            logger.error(f"Error getting completion record for arc {arc_id}: {e}")
            return None
    
    async def get_by_result(self, result: ArcCompletionResult) -> List[ArcCompletionRecord]:
        """Get completion records by result type."""
        try:
            query = select(ArcCompletionRecord).where(
                ArcCompletionRecord.result == result
            ).order_by(ArcCompletionRecord.created_at.desc())
            
            result_data = await self.db_session.execute(query)
            return result_data.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting completion records by result {result}: {e}")
            return []
    
    async def get_successful_completions(self) -> List[ArcCompletionRecord]:
        """Get all successful arc completions."""
        return await self.get_by_result(ArcCompletionResult.SUCCESS)
    
    async def get_failed_completions(self) -> List[ArcCompletionRecord]:
        """Get all failed arc completions."""
        return await self.get_by_result(ArcCompletionResult.FAILURE)
    
    async def get_recent_completions(self, days: int = 7) -> List[ArcCompletionRecord]:
        """Get completion records from the last N days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = select(ArcCompletionRecord).where(
                ArcCompletionRecord.created_at >= cutoff_date
            ).order_by(ArcCompletionRecord.created_at.desc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting recent completions: {e}")
            return []
    
    async def create_completion_record(
        self,
        arc_id: UUID,
        result: ArcCompletionResult,
        final_narrative: Optional[str] = None,
        completion_notes: Optional[str] = None,
        total_steps_completed: int = 0,
        total_steps_failed: int = 0,
        total_steps_skipped: int = 0,
        final_completion_percentage: float = 0.0,
        total_duration_hours: float = 0.0,
        average_step_duration_hours: float = 0.0,
        outcomes: Optional[Dict[str, Any]] = None,
        rewards_granted: Optional[List[Dict[str, Any]]] = None,
        consequences: Optional[List[Dict[str, Any]]] = None,
        world_state_changes: Optional[Dict[str, Any]] = None,
        character_changes: Optional[Dict[str, Any]] = None,
        faction_changes: Optional[Dict[str, Any]] = None,
        step_history: Optional[List[Dict[str, Any]]] = None,
        decision_history: Optional[List[Dict[str, Any]]] = None,
        arc_started_at: Optional[datetime] = None,
        arc_completed_at: Optional[datetime] = None
    ) -> Optional[ArcCompletionRecord]:
        """Create a new completion record for an arc."""
        try:
            record_data = {
                "arc_id": arc_id,
                "result": result,
                "final_narrative": final_narrative,
                "completion_notes": completion_notes,
                "total_steps_completed": total_steps_completed,
                "total_steps_failed": total_steps_failed,
                "total_steps_skipped": total_steps_skipped,
                "final_completion_percentage": final_completion_percentage,
                "total_duration_hours": total_duration_hours,
                "average_step_duration_hours": average_step_duration_hours,
                "outcomes": outcomes or {},
                "rewards_granted": rewards_granted or [],
                "consequences": consequences or [],
                "world_state_changes": world_state_changes or {},
                "character_changes": character_changes or {},
                "faction_changes": faction_changes or {},
                "step_history": step_history or [],
                "decision_history": decision_history or [],
                "arc_started_at": arc_started_at,
                "arc_completed_at": arc_completed_at
            }
            
            return await self.create(record_data)
            
        except Exception as e:
            logger.error(f"Error creating completion record for arc {arc_id}: {e}")
            return None
    
    async def add_outcome(
        self,
        record_id: UUID,
        outcome_type: str,
        outcome_data: Any
    ) -> bool:
        """Add an outcome to a completion record."""
        try:
            record = await self.get(record_id)
            if not record:
                return False
            
            outcomes = record.outcomes or {}
            outcomes[outcome_type] = outcome_data
            record.outcomes = outcomes
            
            await self.db_session.commit()
            logger.info(f"Added outcome {outcome_type} to completion record {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding outcome to completion record {record_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def add_reward(
        self,
        record_id: UUID,
        reward: Dict[str, Any]
    ) -> bool:
        """Add a reward to a completion record."""
        try:
            record = await self.get(record_id)
            if not record:
                return False
            
            rewards = record.rewards_granted or []
            rewards.append(reward)
            record.rewards_granted = rewards
            
            await self.db_session.commit()
            logger.info(f"Added reward to completion record {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding reward to completion record {record_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def add_consequence(
        self,
        record_id: UUID,
        consequence: Dict[str, Any]
    ) -> bool:
        """Add a consequence to a completion record."""
        try:
            record = await self.get(record_id)
            if not record:
                return False
            
            consequences = record.consequences or []
            consequences.append(consequence)
            record.consequences = consequences
            
            await self.db_session.commit()
            logger.info(f"Added consequence to completion record {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding consequence to completion record {record_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def record_world_state_change(
        self,
        record_id: UUID,
        change_type: str,
        change_data: Any
    ) -> bool:
        """Record a world state change in a completion record."""
        try:
            record = await self.get(record_id)
            if not record:
                return False
            
            changes = record.world_state_changes or {}
            changes[change_type] = change_data
            record.world_state_changes = changes
            
            await self.db_session.commit()
            logger.info(f"Recorded world state change {change_type} in completion record {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording world state change in completion record {record_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def record_character_change(
        self,
        record_id: UUID,
        character_id: str,
        change_data: Any
    ) -> bool:
        """Record a character change in a completion record."""
        try:
            record = await self.get(record_id)
            if not record:
                return False
            
            changes = record.character_changes or {}
            changes[character_id] = change_data
            record.character_changes = changes
            
            await self.db_session.commit()
            logger.info(f"Recorded character change for {character_id} in completion record {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording character change in completion record {record_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def record_faction_change(
        self,
        record_id: UUID,
        faction_id: str,
        change_data: Any
    ) -> bool:
        """Record a faction change in a completion record."""
        try:
            record = await self.get(record_id)
            if not record:
                return False
            
            changes = record.faction_changes or {}
            changes[faction_id] = change_data
            record.faction_changes = changes
            
            await self.db_session.commit()
            logger.info(f"Recorded faction change for {faction_id} in completion record {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording faction change in completion record {record_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def add_step_to_history(
        self,
        record_id: UUID,
        step_data: Dict[str, Any]
    ) -> bool:
        """Add a step to the history of a completion record."""
        try:
            record = await self.get(record_id)
            if not record:
                return False
            
            history = record.step_history or []
            history.append(step_data)
            record.step_history = history
            
            await self.db_session.commit()
            logger.info(f"Added step to history in completion record {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding step to history in completion record {record_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def add_decision_to_history(
        self,
        record_id: UUID,
        decision_data: Dict[str, Any]
    ) -> bool:
        """Add a decision to the history of a completion record."""
        try:
            record = await self.get(record_id)
            if not record:
                return False
            
            history = record.decision_history or []
            history.append(decision_data)
            record.decision_history = history
            
            await self.db_session.commit()
            logger.info(f"Added decision to history in completion record {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding decision to history in completion record {record_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def get_completion_statistics(self) -> Dict[str, Any]:
        """Get comprehensive completion statistics."""
        try:
            query = select(ArcCompletionRecord)
            result = await self.db_session.execute(query)
            all_records = result.scalars().all()
            
            stats = {
                "total_completions": len(all_records),
                "by_result": {},
                "success_rate": 0.0,
                "average_completion_percentage": 0.0,
                "average_duration_hours": 0.0,
                "average_steps_completed": 0.0,
                "average_steps_failed": 0.0,
                "total_rewards": 0,
                "total_consequences": 0
            }
            
            if not all_records:
                return stats
            
            # Count by result
            for result_type in ArcCompletionResult:
                stats["by_result"][result_type.value] = len([
                    record for record in all_records if record.result == result_type
                ])
            
            # Calculate success rate
            successful_count = stats["by_result"].get("success", 0)
            if len(all_records) > 0:
                stats["success_rate"] = successful_count / len(all_records)
            
            # Calculate averages
            total_completion = sum(record.final_completion_percentage or 0.0 for record in all_records)
            total_duration = sum(record.total_duration_hours or 0.0 for record in all_records)
            total_steps_completed = sum(record.total_steps_completed or 0 for record in all_records)
            total_steps_failed = sum(record.total_steps_failed or 0 for record in all_records)
            
            stats["average_completion_percentage"] = total_completion / len(all_records)
            stats["average_duration_hours"] = total_duration / len(all_records)
            stats["average_steps_completed"] = total_steps_completed / len(all_records)
            stats["average_steps_failed"] = total_steps_failed / len(all_records)
            
            # Count rewards and consequences
            total_rewards = sum(len(record.rewards_granted or []) for record in all_records)
            total_consequences = sum(len(record.consequences or []) for record in all_records)
            
            stats["total_rewards"] = total_rewards
            stats["total_consequences"] = total_consequences
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting completion statistics: {e}")
            return {
                "total_completions": 0,
                "by_result": {},
                "success_rate": 0.0,
                "average_completion_percentage": 0.0,
                "average_duration_hours": 0.0,
                "average_steps_completed": 0.0,
                "average_steps_failed": 0.0,
                "total_rewards": 0,
                "total_consequences": 0
            }
    
    async def get_completion_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get completion trends over the last N days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = select(ArcCompletionRecord).where(
                ArcCompletionRecord.created_at >= cutoff_date
            ).order_by(ArcCompletionRecord.created_at.asc())
            
            result = await self.db_session.execute(query)
            records = result.scalars().all()
            
            # Group by day
            daily_stats = {}
            for record in records:
                day_key = record.created_at.date().isoformat()
                
                if day_key not in daily_stats:
                    daily_stats[day_key] = {
                        "total": 0,
                        "successful": 0,
                        "failed": 0,
                        "partial": 0,
                        "abandoned": 0,
                        "timeout": 0
                    }
                
                daily_stats[day_key]["total"] += 1
                daily_stats[day_key][record.result.value] += 1
            
            return {
                "period_days": days,
                "daily_stats": daily_stats,
                "total_period_completions": len(records)
            }
            
        except Exception as e:
            logger.error(f"Error getting completion trends: {e}")
            return {
                "period_days": days,
                "daily_stats": {},
                "total_period_completions": 0
            }
    
    async def search_completion_records(
        self,
        search_term: str,
        result: Optional[ArcCompletionResult] = None
    ) -> List[ArcCompletionRecord]:
        """Search completion records by text in narrative or notes."""
        try:
            # Base search on final narrative and completion notes
            query = select(ArcCompletionRecord).where(
                or_(
                    ArcCompletionRecord.final_narrative.ilike(f"%{search_term}%"),
                    ArcCompletionRecord.completion_notes.ilike(f"%{search_term}%")
                )
            )
            
            # Apply optional filters
            if result:
                query = query.where(ArcCompletionRecord.result == result)
            
            query = query.order_by(ArcCompletionRecord.created_at.desc())
            
            result_data = await self.db_session.execute(query)
            return result_data.scalars().all()
            
        except Exception as e:
            logger.error(f"Error searching completion records with term '{search_term}': {e}")
            return [] 